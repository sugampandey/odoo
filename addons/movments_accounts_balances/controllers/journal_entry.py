from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from odoo import http
from odoo.http import request
from ..middleware.auth_middleware import validate_token_middleware
from ..utils import APIResponse, get_company_from_headers, validate_request_data, validate_pagination_params
from ..logger.logger import logger
from ..swagger.swagger_generator import swagger_gen
from ..schemas.journal_entry import (JournalEntryRequestModel, JournalEntryModel, JournalEntryResponseModel, JournalEntryListResponseModel)
from ..schemas.common import ACCESS_TOKEN_HEADER, COMPANY_HEADERS
from ..repositories.account_move import AccountMoveService
from ..repositories.company import CompanyService
from ..repositories.journal import JournalService

class JournalEntryAPI(http.Controller):

    
    @http.route('/api/v1/journal-entries', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='journal-entry',
        request_model=JournalEntryRequestModel,
        response_model=JournalEntryResponseModel,
        tags=['Journal Entries'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def create_journal_entry(self, **kwargs):
        """
        Creates a new journal entry in Odoo.
        """
        logger.info("Processing create journal entry request")
        try:
            # Get and validate request data
            data = validate_request_data(request, JournalEntryRequestModel)
            if not isinstance(data, JournalEntryRequestModel):  # If error response
                return data
            
            # Create account move
            return self._create_account_move_record(request, data)
        except Exception as e:
            logger.error(f"Failed to create account move record: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
    
    @http.route('/api/v1/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='journal-entry',
        response_model=JournalEntryResponseModel,
        tags=['Journal Entries'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_journal_entry(self, journal_entry_id: int, company_id: int):
        """
        Retrieves a specific journal entry by its ID.
        
        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing the journal entry details or an error message.
        """
        try:
            domain = [('id', '=', journal_entry_id)]
            company_service = CompanyService(request.env)
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))
            return self._fetch_single_journal_entry(domain)
        except Exception as e:
            logger.error(f"Error in get_account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    
    @http.route('/api/v1/journal-entries', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='journal-entry',
        response_model=JournalEntryListResponseModel,
        tags=['Journal Entries'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_journal_entry(self, company_id: int, journal_id: Optional[int]=None, 
                           maxresults: int = 100, startposition: int = 1, 
                           date_from=None, date_to=None, **kwargs) -> Dict[str, Any]:
        """
        Retrieves a list of all journal entries based on the provided filters.

        :param request: The HTTP request object containing optional filter parameters.
        :return: A dictionary containing the journal entry list or an error message.
        """
        try:
            # Validate pagination parameters
            is_valid, result = validate_pagination_params(startposition, maxresults)
            if not is_valid:
                return result
            startposition, maxresults = result

            # Build search domain and validate company
            domain, error_response = self._build_search_domain(
                company_id, journal_id, date_from, date_to
            )
            if error_response:
                return error_response
            
            return self._fetch_accounts(
                domain, int(startposition), int(maxresults)
            )
        except Exception as e:
            logger.error(f"Error in list_journal_entry: {str(e)}")
            return APIResponse.error_response(message=f'An error occurred: {str(e)}',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
        
    @http.route('/api/v1/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='journal-entry',
        tags=['Journal Entries'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_journal_entry(self, journal_entry_id: int, company_id: int):
        """
        Deletes a specific journal entry by its ID.
        """
        cursor = request.env.cr
        try:
            company_service = CompanyService(request.env)
            account_move_service = AccountMoveService(request.env)

            # Validate company
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            
            # Validate account move
            is_valid, error_message = account_move_service.validate_journal_entry(journal_entry_id, company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid Journal Entry: {error_message}',
                    errors=f'Invalid journal_entry_id: {journal_entry_id}', status=HTTPStatus.BAD_REQUEST
                )
            
            with cursor.savepoint():
                move = account_move_service.browse(int(journal_entry_id))
                if not move.exists():
                    return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

                # Check the state of the journal entry
                if move.state == 'posted':
                    # Check if this is already a reversal entry
                    if move.reversed_entry_id:
                        return APIResponse.error_response(
                            message='Cannot reverse a reversal entry', 
                            errors=f'Journal entry {journal_entry_id} is already a reversal of entry {move.reversed_entry_id.id}', 
                        )
                    # Check if already reversed (find if any entry has this as reversed_entry_id)
                    existing_reversal = account_move_service.search([('reversed_entry_id', '=', journal_entry_id)], limit=1)
                    if existing_reversal:
                        return APIResponse.error_response(
                            message='Journal entry already reversed', 
                            errors=f'Journal entry {journal_entry_id} was already reversed by entry {existing_reversal.id}', 
                        )
                    reversal = move._reverse_moves()
                    reversal.action_post()
                    return APIResponse.success_response({
                        "message": "Journal entry reversed", 
                        "original_entry_id": journal_entry_id,
                        "reversed_entry_id": reversal.id, 
                        "reversed_name": reversal.name
                    })
                elif move.state == 'draft':
                    # If in draft state, can delete directly
                    move.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response({"message":"DRAFT - Journal entry deleted successfully"})
                else:
                    return APIResponse.error_response(message=f'Cannot delete journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deleting journal entry', errors=str(e), status=500)
   

    @http.route('/api/v1/cancel_journal_entry', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    def cancel_journal_entry(self, journal_entry_id, **kwargs):
        """
        Cancels a specific journal entry by its ID.

        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing a success message or an error message.
        """
        cursor = request.env.cr
        try:
            account_move_service = AccountMoveService(request.env)
            move = account_move_service.browse(int(journal_entry_id))
            if not move.exists():
                return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

            with cursor.savepoint():
                # Check the state of the journal entry
                if move.state == 'posted':
                    # Reset to draft first
                    move.button_draft()

                    # Then cancel
                    move.with_context(send_webhook=True).button_cancel()

                    return APIResponse.success_response(message="Journal entry cancelled successfully", data=None)
                else:
                    return APIResponse.error_response(message=f'Cannot cancel journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}', status=400)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while cancelling journal entry', errors=str(e), status=500)
        

    def _create_account_move_record(self, request, journal_entry_model: JournalEntryRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):  # If error response
                return company_id
        
        journal_entry_vals = journal_entry_model.create_journal_entry_vals(company_id)

        cursor = request.env.cr
        try:
            with cursor.savepoint():
                journal_entry = self._save_journal_entry(request, journal_entry_vals)
                return self._prepare_success_response(journal_entry)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create Journal Entry: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    def _save_journal_entry(self, request, journal_entry_vals: Dict[str, Any]) -> Any:
        account_move_service = AccountMoveService(request.env)
        journal_entry = account_move_service.create(journal_entry_vals)
        journal_entry.with_context(send_webhook=True).action_post()
        return journal_entry

    def _prepare_success_response(self, journal_entry: Any) -> Dict[str, Any]:
        response_data = JournalEntryResponseModel.create_journal_entry_response(request, journal_entry)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )
        
    def _build_search_domain(self, company_id: int, journal_id: Optional[int],
                             date_from, date_to
                             ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        domain = [
                ('move_type', '=', 'entry'),
                ('state', '=', 'posted'),
                ('payment_id', '=', None),
            ]
        company_service = CompanyService(request.env)
        journal_service = JournalService(request.env)

        # Validate and add company filter
        if company_id:
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return [], APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))
            logger.debug(f"Added company_id filter: {company_id}")
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))

        if journal_id:  
            is_valid, error_message = journal_service.validate_journal(journal_id, company_id)
            if not is_valid:
                return [], APIResponse.error_response(f'Invalid journal: {error_message}', f'Invalid journal_id: {journal_id}')
            domain.append(('journal_id', '=', int(journal_id)))


        logger.debug(f"Final search domain: {domain}")
        return domain, None
    
    def _fetch_accounts(self, domain: List[Tuple], start_position: int, max_results: int) -> Dict[str, Any]:
        # Get total count
        account_move_service = AccountMoveService(request.env)
        total_count = account_move_service.search_count(domain)
        logger.info(f"Total matching accounts: {total_count}")

        # Search for journal entries
        journal_entries = account_move_service.search(
            domain,
            limit=max_results,
            offset=(start_position-1),
            order='date desc, id desc'
        )
        logger.info(f"Retrieved {len(journal_entries)} journal entries")

        return self._prepare_list_response(
            journal_entries, total_count, start_position
        )

    def _prepare_list_response(self, journal_entries: Any, total_count: int, start_position: int) -> Dict[str, Any]:
        journal_entry_data = [JournalEntryModel.journal_entry_object(request, journal_entry) for journal_entry in journal_entries]
        
        response_data = JournalEntryListResponseModel.list_journal_entry_response(
            journal_entry_data, total_count, start_position, len(journal_entries)
        )
        
        return APIResponse.success_response(response_data.model_dump(mode='json'))
    
    def _fetch_single_journal_entry(self, domain: List[Tuple]) -> Dict[str, Any]:
        account_move_service = AccountMoveService(request.env)
        journal_entry = account_move_service.search(domain, limit=1)
        
        if not journal_entry.exists():
            return APIResponse.error_response(message='Journal Entry not found',
                errors='Invalid journal_entry_id', status=HTTPStatus.BAD_REQUEST
            )

        response_data = JournalEntryResponseModel.create_journal_entry_response(journal_entry)
        return APIResponse.success_response(response_data.model_dump(mode='json'))