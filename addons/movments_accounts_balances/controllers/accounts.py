import datetime
from typing import Dict, Any, List, Optional, Tuple
from http import HTTPStatus
from pydantic import ValidationError
from odoo import http, fields
from odoo.http import request
from ..common import APIResponse, get_company_from_headers, get_payment_method_from_headers, validate_and_convert_data, get_request_data
from ..utils import validate_company, validate_account
from ..logger.logger import logger
from ..swagger.common import swagger_doc, swagger_document
# from ..swagger.accounts import accounts_docs
from ..schemas.accounts import AccountCreateRequestModel , AccountResponseModel, AccountModel, AccountQueryResponseModel, AccountListResponseModel
from ..schemas.common import MetaDataModel, CurrencyRefModel
from ..mapping.accounts import ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING, ACCOUNT_TYPE_MAPPING, TYPE_PREFIX_MAPPING
from ..constants import CONSTANTS
from ..repository.journal import Journal

class AccountAPI(http.Controller):

    def _get_validated_request_data(self, request) -> Dict[str, Any]:
        try:
            data = get_request_data(request)
            logger.debug(f"Received data: {data}")
            
            account_model = AccountCreateRequestModel(**data)
            return account_model
        except ValidationError as e:
            return APIResponse.error_response(message='Invalid request data', 
                errors=e.errors(), status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

    def _validate_company(self, request) -> Optional[Dict[str, Any]]:
        company_id = get_company_from_headers(request)
        if not company_id:
            return APIResponse.error_response(message='Company ID is required',
                errors='Missing CompanyId', status=HTTPStatus.BAD_REQUEST
            )

        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return APIResponse.error_response(message=f'Invalid company: {error_message}',
                errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        return None

    def _create_account_record(self, request, account_model: AccountCreateRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        payment_method = get_payment_method_from_headers(request)
        account_vals = account_model.create_account_vals(request, company_id)

        cursor = request.env.cr
        try:
            with cursor.savepoint():
                account = self._save_account(request, account_vals, payment_method)
                return self._prepare_success_response(account)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def _save_account(self, request, account_vals: Dict[str, Any], payment_method: str) -> Any:
        account = request.env['account.account'].sudo().create(account_vals)
        Journal.create(request, account.name, account.code, account.company_id.id, 
                       account.id, account.account_type, payment_method)
        return account

    def _prepare_success_response(self, account: Any) -> Dict[str, Any]:
        response_data = AccountResponseModel.create_account_response(account)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )
    
    @http.route('/api/accounts', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_account(self, **kwargs) -> Dict[str, Any]:
        logger.info("Processing create account request")
        
        try:
            # Get and validate request data
            data = self._get_validated_request_data(request)
            if isinstance(data, dict):  # If error response
                return data

            # Validate company
            company_validation = self._validate_company(request)
            if company_validation:
                return company_validation

            # Create account
            return self._create_account_record(request, data)
        except Exception as e:
            logger.error(f"Failed to create account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
            

    def _build_search_domain(self, name: Optional[str], account_type: Optional[str],
        company_id: Optional[str], active: Optional[str]
        ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        domain = []
        
        # Add account type filter
        if account_type:
            mapped_type = ACCOUNT_TYPE_MAPPING.get(account_type)
            domain.append(('account_type', '=', mapped_type))
            logger.debug(f"Added account_type filter: {mapped_type}")

        # Validate and add company filter
        if company_id:
            is_valid, error_message = validate_company(request, company_id)
            if not is_valid:
                return [], APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))
            logger.debug(f"Added company_id filter: {company_id}")

        # Add active status filter
        if active is not None:
            deprecated = not (active.lower() == 'true')
            domain.append(('deprecated', '=', deprecated))
            logger.debug(f"Added deprecated filter: {deprecated}")

        # Add name filter
        if name:
            domain.append(('name', 'ilike', name))
            logger.debug(f"Added name filter: {name}")

        logger.debug(f"Final search domain: {domain}")
        return domain, None


    def _fetch_accounts(self, domain: List[Tuple], start_position: int, max_results: int) -> Dict[str, Any]:
        # Get total count
        total_count = request.env['account.account'].sudo().search_count(domain)
        logger.info(f"Total matching accounts: {total_count}")

        # Search for accounts
        accounts = request.env['account.account'].sudo().search(
            domain,
            limit=max_results,
            offset=start_position,
            order='id DESC'
        )
        logger.info(f"Retrieved {len(accounts)} accounts")

        return self._prepare_list_response(
            accounts, total_count, start_position
        )

    def _prepare_list_response(self, accounts: Any, total_count: int, start_position: int) -> Dict[str, Any]:
        accounts_data = [AccountModel.account_object(account) for account in accounts]
        
        response_data = AccountListResponseModel.list_account_response(
            accounts_data, total_count, start_position, len(accounts)
        )
        
        return APIResponse.success_response(response_data.model_dump(mode='json'))

    
    @http.route('/api/accounts', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def list_accounts(self, name: Optional[str] = None, account_type: Optional[str] = None, company_id: Optional[str] = None,
        active: Optional[str] = None, maxresults: int = 100, startposition: int = 0, **kwargs
    ) -> Dict[str, Any]:
        try:
            logger.info(
                f"Fetching accounts with parameters: "
                f"account_type={account_type}, "
                f"company_id={company_id}, "
                f"active={active}"
            )
            
            # Build search domain and validate company
            domain, error_response = self._build_search_domain(
                name, account_type, company_id, active
            )
            if error_response:
                return error_response

            return self._fetch_accounts(
                domain, int(startposition), int(maxresults)
            )

        except Exception as e:
            logger.error(f"Error in list_accounts: {str(e)}")
            return APIResponse.error_response(message=f'An error occurred: {str(e)}',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    

    
    
    @http.route('/api/accounts/<int:account_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_account(self, account_id: int, company_id: int) -> Dict[str, Any]:
        try:
            domain = [('id', '=', account_id)]
            
            # Validate and add company filter
            is_valid, error_message = validate_company(request, company_id)
            if not is_valid:
                return [], APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))

            return self._fetch_single_account(domain)

        except Exception as e:
            logger.error(f"Error in get_account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def _fetch_single_account(self, domain: List[Tuple]) -> Dict[str, Any]:
        account = request.env['account.account'].sudo().search(domain, limit=1)
        
        if not account.exists():
            return APIResponse.error_response(message='Account not found',
                errors='Invalid account_id', status=HTTPStatus.NOT_FOUND
            )

        response_data = AccountResponseModel.create_account_response(account)
        return APIResponse.success_response(response_data.model_dump(mode='json'))


    @http.route('/api/accounts/<int:account_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(accounts_docs['delete_account'])
    def delete_account(self, account_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                company_id = int(kwargs.get('company_id')) if kwargs.get('company_id') else kwargs.get('company_id')
                if not company_id:
                    return APIResponse.error_response(message='Company ID not provided', errors='company_id is required')
                
                # Validate company
                is_valid, error_message = validate_company(request, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
                
                # Validate account
                is_valid, error_message = validate_account(request, account_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
                
                # Retrieve the account
                account = request.env['account.account'].sudo().browse(account_id)

                # Delete the account
                account.write({'deprecated': True})
                return APIResponse.success_response()
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
        
      
    @http.route('/api/account-types', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_account_types(self, **kwargs):
        account_types = [{"code": ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING[key], "name": key} for key in ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING.keys()]
        return APIResponse.success_response(account_types)
    
    def create_opening_balance(self, account, opening_debit, opening_credit, company_id):
        """
        Creates an opening balance journal entry for the given account.

        :param account: The account.account record for which the opening balance is being created.
        :param opening_debit: The opening debit value.
        :param opening_credit: The opening credit value.
        :param company_id: The ID of the company for the opening balance.
        """
        # Validate that only one of opening_debit or opening_credit is non-zero
        logger.info(f"Creating opening balance for account {account.code} - {account.name}")
        logger.debug(f"Opening balance details: debit={opening_debit}, credit={opening_credit}, company_id={company_id}")
        if opening_debit and opening_credit:
            logger.error("Both opening_debit and opening_credit provided")
            raise ValueError("Both opening_debit and opening_credit cannot be non-zero simultaneously.")
        
        if opening_debit < 0 or opening_credit < 0:
            logger.error(f"Invalid negative values: debit={opening_debit}, credit={opening_credit}")
            raise ValueError("Opening debit and credit values must be non-negative.")

        # Find the general journal for the company
        opening_journal = request.env['account.journal'].sudo().search([
            ('type', '=', 'general'),
            ('company_id', '=', company_id)
        ], limit=1)

        if not opening_journal:
            logger.error(f"No general journal found for company_id: {company_id}")
            raise ValueError("No general journal found for the specified company.")

        # Create the journal entry
        opening_move_vals = {
            'journal_id': opening_journal.id,
            'date': fields.Date.today(),
            'ref': f'Opening Balance for {account.code} - {account.name}',
            'move_type': 'entry',
            'line_ids': [
                (0, 0, {
                    'account_id': account.id,
                    'debit': opening_debit,
                    'credit': opening_credit,
                    'name': 'Opening Balance',
                    'move_name': f'OPEN/{account.code}',
                    'journal_id': opening_journal.id,
                    'balance': opening_debit - opening_credit,
                })
            ]
        }
        # If there's a difference, balance it with retained earnings account
        difference = opening_debit - opening_credit
        if difference != 0:
            retained_earnings_account = request.env['account.account'].sudo().search([
                ('company_id', '=', company_id),
                ('account_type', '=', 'equity_unaffected')
            ], limit=1)
            if not retained_earnings_account:
                raise ValueError("No retained earnings account found for the specified company.")
            opening_move_vals['line_ids'].append(
                (0, 0, {
                    'account_id': retained_earnings_account.id,
                    'debit': abs(difference),
                    'credit': abs(difference),
                    'name': 'Opening Balance - Retained Earnings',
                    'move_name': f'OPEN/{account.code}',
                    'journal_id': opening_journal.id,
                    'balance': abs(difference),
                })
            )
        opening_balance_entry = request.env['account.move'].sudo().create(opening_move_vals)
        opening_balance_entry.with_context(send_webhook=True).action_post()
    
    
    
    # @http.route('/api/accounts', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # def create_account(self, **kwargs):
    #     logger.info("Processing create account request")
    #     data = get_request_data(request)
    #     logger.debug(f"Received data: {data}")
        
    #     company_id = get_company_from_headers(request)
    #     payment_method = get_payment_method_from_headers(request)

    #     if company_id:
    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #     else:
    #         return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)
        
    #     try:
    #         account_model = AccountCreateRequestModel(**data)
    #     except ValidationError as e:
    #         return APIResponse.error_response(message='Invalid request data', errors=e.errors())
        
    #     account_vals = account_model.create_account_vals(request, company_id)

    #     cursor = request.env.cr
    #     try:
    #         with cursor.savepoint():
    #             # Create the account
    #             account = request.env['account.account'].sudo().create(account_vals)
    #             Journal.create(account.name, account.code, account.company_id.id, account.id, account.account_type, payment_method)
    #     except Exception as e:
    #         cursor.rollback()
    #         return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
    #     try:
    #         # Prepare response data
    #         response_data = AccountResponseModel.create_account_response(account)
    #         return APIResponse.success_response(response_data.model_dump(), status=201)
    #     except Exception as e:
    #         return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)

    
    # @http.route('/api/accounts', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # # @swagger_doc(accounts_docs['list_accounts'])
    # def list_accounts(self, name=None, account_type=None, company_id=None, active=None, maxresults=100, startposition=0, **kwargs):
    #     try:
    #         logger.info(f"Fetching accounts with parameters: account_type={account_type}, company_id={company_id}, active={active}")
    #         domain = []
    #         if account_type:
    #             domain.append(('account_type', '=', ACCOUNT_TYPE_MAPPING.get(account_type)))
    #             logger.debug(f"Added account_type filter: {ACCOUNT_TYPE_MAPPING.get(account_type)}")
    #         if company_id:
    #             is_valid, error_message = validate_company(request, company_id)
    #             if not is_valid:
    #                 return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #             domain.append(('company_id', '=', int(company_id)))
    #             logger.debug(f"Added company_id filter: {company_id}")
    #         if active is not None:
    #             deprecated = not (active.lower() == 'true')
    #             domain.append(('deprecated', '=', deprecated))
    #             logger.debug(f"Added deprecated filter: {deprecated}")
    #         if name:
    #             domain.append(('name', 'ilike', name))
    #             logger.debug(f"Added name filter: {name}")

    #         logger.debug(f"Final search domain: {domain}")

    #         # Get total count
    #         total_count = request.env['account.account'].sudo().search_count(domain)
    #         logger.info(f"Total matching accounts: {total_count}")

    #         # Search for accounts based on the domain with pagination
    #         startposition = int(startposition)
    #         maxresults = int(maxresults)
    #         accounts = request.env['account.account'].sudo().search(
    #             domain, 
    #             limit=maxresults, 
    #             offset=startposition,
    #             order='id DESC'
    #         )
    #         logger.info(f"Retrieved {len(accounts)} accounts")

    #         # Prepare the response data
    #         accounts_data = []
    #         for account in accounts:
    #             accounts_data.append(AccountModel.account_object(account))
    #         response_data = AccountListResponseModel.list_account_response(accounts_data, total_count, startposition, len(accounts))

    #         return APIResponse.success_response(response_data)
    #     except Exception as e:
    #         logger.error(f"Error in list_accounts: {str(e)}")
    #         return APIResponse.error_response(message=f'An error occurred: {str(e)}', errors=f'{str(e)}', status=500)
    
    
    # @http.route('/api/accounts/<int:account_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # # @swagger_doc(accounts_docs['get_account'])
    # def get_account(self, account_id, company_id):
    #     try:
    #         domain = [('id', '=', int(account_id))]

    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #         domain.append(('company_id', '=', int(company_id)))
    #         # Retrieve the account
    #         account = request.env['account.account'].sudo().search(domain, limit=1)
    #         if not account.exists():
    #             return APIResponse.error_response(message='Account not found', errors='Invalid account_id', status=404)

    #         response_data = AccountResponseModel.create_account_response(account)
    #         return APIResponse.success_response(response_data)
    #     except Exception as e:
    #         return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
    
    
    # def validate_and_prepare_account_data(self, data, company_id, ACCOUNT_SCHEMA):
    #     # Validate company
    #     is_valid, error_message = validate_company(request, company_id)
    #     if not is_valid:
    #         return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    
    #     account_request_data = AccountCreateRequestModel(data).to_dict()

            
    #     account_vals = AccountCreateRequestModel.create_account_vals(request, account_request_data, company_id)
    #     return True, account_vals, account_request_data
        
    

    # @swagger_doc(accounts_docs['create_account'])
    # @swagger_document(
    #     summary="Create a new account",
    #     request_model=AccountCreateRequestModel,
    #     response_model=AccountResponse,
    #     tags=['Accounts']
    # )
