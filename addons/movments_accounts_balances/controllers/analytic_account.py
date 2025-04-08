from typing import Any, Dict, List, Optional, Tuple
from odoo import http
from http import HTTPStatus
from odoo.http import request
from pydantic import ValidationError
from ..utils import APIResponse, get_company_from_headers, validate_request_data

# from ..swagger.common import swagger_doc
# from ..swagger.analytic_account import analytic_accounts_docs
from ..schemas.analytic_account import AnalyticClassModel, AnalyticClassListResponseModel, AnalyticClassResponseModel, AnalyticClassCreateRequestModel
from ..logger.logger import logger
from ..repository.analytic_account import AnalyticAccountService, AnalyticPlanService
from ..repository.company import CompanyService

class AnalyticAccountAPI(http.Controller):

    @http.route('/api/analytic-class', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(analytic_accounts_docs['create_analytic_account'])
    def create_analytic_account(self, **kwargs):
        logger.info("Processing create Analytic Account request")
        try:
            data = validate_request_data(request, AnalyticClassCreateRequestModel)
            if not isinstance(data, AnalyticClassCreateRequestModel):  # If error response
                return data
            
            return self._create_analytic_account_record(request, data)
        except Exception as e:
            logger.error(f"Failed to create Analytic Class: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    @http.route('/api/analytic-class', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(analytic_accounts_docs['list_analytic_accounts'])
    def list_analytic_accounts(self, company_id: int, active: Optional[str] = None, maxresults: int = 100, startposition: int = 0, **kwargs):
        """
        Retrieves analytic accounts from Odoo's accounting module.

        Returns:
        list: List of dictionaries, each containing details of an analytic account.

        Raises:
        ValidationError: If no analytic accounts are found.
        """
        try:
            # Build search domain and validate company
            domain, error_response = self._build_search_domain(
                company_id, active
            )
            if error_response:
                return error_response

            return self._fetch_analytic_accounts(
                domain, int(startposition), int(maxresults)
            )
            
        except Exception as e:
            logger.error(f"Error in list_analytic_accounts: {str(e)}")
            return APIResponse.error_response(message=f'An error occurred: {str(e)}',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    @http.route('/api/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(analytic_accounts_docs['get_analytic_account'])
    def get_analytic_account(self, analytic_class_id: int, company_id: int, **kwargs):
        """
        Retrieves an analytic account by ID within Odoo's accounting module.

        Args:
        - analytic_class_id (int): The ID of the analytic account to retrieve.

        Returns:
        dict: Dictionary containing a key 'account_info' with details of the retrieved analytic account.

        Raises:
        ValidationError: If the analytic account does not exist.
        """
        company_service = CompanyService(request.env)
        analytic_account_id = analytic_class_id
        try:
            domain = [('id', '=', int(analytic_account_id))]
            
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))
            return self._fetch_single_analytic_account(domain)
        except Exception as e:
            logger.error(f"Error in get_analytic_account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    @http.route('/api/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(analytic_accounts_docs['delete_analytic_account'])
    def delete_analytic_account(self, analytic_class_id, **kwargs):
        try:
            company_service = CompanyService(request.env)
            analytic_account_service = AnalyticAccountService(request.env)

            analytic_account_id = analytic_class_id
            company_id = int(kwargs.get('company_id')) if kwargs.get('company_id') else kwargs.get('company_id')
            if not company_id:
                return APIResponse.error_response(message='Company ID not provided', errors='company_id is required')
            
            # Validate company
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
        
            # Attempt to retrieve the analytic account using the provided ID
            account = analytic_account_service.browse(analytic_account_id)

            # Check if the analytic account actually exists
            if not account.exists():
                raise ValidationError(f"Analytic class with ID {analytic_account_id} does not exist.")
            
            if account.company_id.id != company_id:
                return APIResponse.error_response(message='Analytic class does not belong to the specified company', errors=f'Analytic account {analytic_account_id} does not belong to company {company_id}')

            # Delete the analytic account
            account.write({'active': False})

            return APIResponse.success_response({'message':'Analytic class deactivated successfully'})
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while deactivating the analytic class', errors=str(e), status=500)
    
    def _create_analytic_account_record(self, request, analytic_account_model: AnalyticClassCreateRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):  # If error response
                return company_id
        
        analytic_account_vals = analytic_account_model.create_analytic_class_vals(company_id)

        cursor = request.env.cr
        try:
            with cursor.savepoint():
                analytic_account = self._save_analytic_account(request, analytic_account_vals)
                return self._prepare_success_response(analytic_account)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create Analytic Class: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def _save_analytic_account(self, request, analytic_account_vals: Dict[str, Any]) -> Any:
        analytic_plan_service = AnalyticPlanService(request.env)
        analytic_account_service = AnalyticAccountService(request.env)

        analytic_account_plan = analytic_plan_service.create({
                    'name':analytic_account_vals['name'],
                    'company_id': analytic_account_vals['company_id']
                })
        
        analytic_account_vals['plan_id'] = analytic_account_plan.id
        analytic_account = analytic_account_service.create(analytic_account_vals)
        return analytic_account
    
    def _prepare_success_response(self, analytic_account: Any) -> Dict[str, Any]:
        response_data = AnalyticClassResponseModel.create_analytic_class_response(analytic_account)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )
        
    def _build_search_domain(self, company_id: int, active: Optional[str]
        ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        domain = []
        company_service = CompanyService(request.env)

        # Validate and add company filter
        if company_id:
            is_valid, error_message = company_service.validate_company(company_id)
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


        logger.debug(f"Final search domain: {domain}")
        return domain, None
    
    def _fetch_analytic_accounts(self, domain: List[Tuple], start_position: int, max_results: int) -> Dict[str, Any]:
        # Get total count
        analytic_account_service = AnalyticAccountService(request.env)
        total_count = analytic_account_service.search_count(domain)
        logger.info(f"Total matching accounts: {total_count}")

        # Search for accounts
        analytic_accounts = analytic_account_service.search(
            domain,
            limit=max_results,
            offset=start_position,
            order='id DESC'
        )
        logger.info(f"Retrieved {len(analytic_accounts)} analytic accounts")

        return self._prepare_list_response(
            analytic_accounts, total_count, start_position
        )
    
    def _prepare_list_response(self, analytic_accounts: Any, total_count: int, start_position: int) -> Dict[str, Any]:
        analytic_accounts_data = [AnalyticClassModel.analytic_class_object(analytic_account) for analytic_account in analytic_accounts]
        
        response_data = AnalyticClassListResponseModel.list_analytic_class_response(
            analytic_accounts_data, total_count, start_position, len(analytic_accounts)
        )
        
        return APIResponse.success_response(response_data.model_dump(mode='json'))
        
    def _fetch_single_analytic_account(self, domain: List[Tuple]) -> Dict[str, Any]:
        analytic_account_service = AnalyticAccountService(request.env)
        analytic_account = analytic_account_service.search(domain, limit=1)
        
        if not analytic_account.exists():
            return APIResponse.error_response(message='Analytic Class not found',
                errors='Invalid analytic_class_id', status=HTTPStatus.NOT_FOUND
            )

        response_data = AnalyticClassResponseModel.create_analytic_class_response(analytic_account)
        return APIResponse.success_response(response_data.model_dump(mode='json'))
    
