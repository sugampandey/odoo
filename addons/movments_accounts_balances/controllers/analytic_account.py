from typing import Any, Dict, List, Optional, Tuple
from odoo import http
from http import HTTPStatus
from odoo.http import request
from odoo.exceptions import UserError, ValidationError, MissingError
from psycopg2 import IntegrityError
from pydantic import ValidationError as PydanticValidationError
from ..middleware.auth_middleware import validate_token_middleware
from ..utils import APIResponse, get_company_from_headers, validate_request_data, validate_pagination_params
from ..logger.logger import logger
from ..swagger.swagger_generator import swagger_gen
from ..schemas.analytic_account import AnalyticClassModel, AnalyticClassListResponseModel, AnalyticClassResponseModel, AnalyticClassCreateRequestModel, AnalyticClassUpdateRequestModel
from ..schemas.common import ACCESS_TOKEN_HEADER, COMPANY_HEADERS
from ..repositories.analytic_account import AnalyticAccountService, AnalyticPlanService
from ..repositories.company import CompanyService

class AnalyticAccountAPI(http.Controller):

    @http.route('/api/v1/analytic-class', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='analytic-account',
        request_model=AnalyticClassCreateRequestModel,
        response_model=AnalyticClassResponseModel,
        tags=['Analytic Classes'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def create_analytic_account(self, **kwargs):
        """
        Creates a new analytic account record.

        Returns:
        dict: A dictionary containing the response data.

        Raises:
        ValidationError: If the request data is invalid.
        """
        logger.info("Processing create Analytic Account request")
        try:
            data = validate_request_data(request, AnalyticClassCreateRequestModel)
            if not isinstance(data, AnalyticClassCreateRequestModel):  # If error response
                return data
            
            return self._create_analytic_account_record(request, data)
        except UserError as e:
            logger.error(f"User error in create analytic account: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error in create analytic account: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.UNPROCESSABLE_ENTITY)
        except IntegrityError as e:
            logger.error(f"Database integrity error in create analytic account: {str(e)}")
            if 'unique constraint' in str(e).lower():
                return APIResponse.error_response(message="Analytic class name already exists", errors=str(e), status=HTTPStatus.CONFLICT)
            elif 'foreign key constraint' in str(e).lower():
                return APIResponse.error_response(message="Invalid reference ID", errors=str(e), status=HTTPStatus.BAD_REQUEST)
            return APIResponse.error_response(message="Database constraint violation", errors=str(e), status=HTTPStatus.CONFLICT)
        except Exception as e:
            logger.error(f"Failed to create Analytic Class: {str(e)}")
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    @http.route('/api/v1/analytic-class', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='analytic-account',
        response_model=AnalyticClassListResponseModel,
        tags=['Analytic Classes'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_analytic_accounts(self, company_id: int, active: Optional[str] = None, maxresults: int = 100, startposition: int = 1, **kwargs):
        """
        Retrieves analytic accounts from Odoo's accounting module.

        Returns:
        list: List of dictionaries, each containing details of an analytic account.

        Raises:
        ValidationError: If no analytic accounts are found.
        """
        try:
            # Validate pagination parameters
            is_valid, result = validate_pagination_params(startposition, maxresults)
            if not is_valid:
                return result
            startposition, maxresults = result
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
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    
    @http.route('/api/v1/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='analytic-account',
        response_model=AnalyticClassResponseModel,
        tags=['Analytic Classes'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
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
        try:
            domain = [('id', '=', int(analytic_class_id))]
            
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.NOT_FOUND
                )
            domain.append(('company_id', '=', int(company_id)))
            return self._fetch_single_analytic_account(domain)
        except Exception as e:
            logger.error(f"Error in get_analytic_account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    @http.route('/api/v1/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='analytic-account',
        tags=['Analytic Classes'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def delete_analytic_account(self, analytic_class_id: int) -> Dict[str, Any]:
        logger.info(f"Processing delete analutic account request for account_id: {analytic_class_id}")
        
        cursor = request.env.cr
        try:
            company_service = CompanyService(request.env)
            analytic_account_service = AnalyticAccountService(request.env)

            company_id = get_company_from_headers(request)
            if not isinstance(company_id, int):
                return company_id
            # Validate company
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.NOT_FOUND
                )

            analytic_account_id = analytic_class_id
            # Validate analytic account
            is_valid, error_message = analytic_account_service.validate_analytic_account(analytic_account_id, company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid analytic class: {error_message}',
                    errors=f'Invalid analytic_class_id: {analytic_account_id}', status=HTTPStatus.NOT_FOUND
                )
        
            # Delete the account
            analytic_account = analytic_account_service.browse(analytic_account_id)
            with cursor.savepoint():
                analytic_account.write({'active': False})
            
            return APIResponse.success_response({'message':'Analytic class deactivated successfully'})
        except UserError as e:
            cursor.rollback()
            logger.error(f"User error in delete analytic account: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.BAD_REQUEST)
        except IntegrityError as e:
            cursor.rollback()
            logger.error(f"Database integrity error in delete analytic account: {str(e)}")
            return APIResponse.error_response(message="Cannot delete: analytic class is referenced elsewhere", 
                errors=str(e), status=HTTPStatus.CONFLICT)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to delete analytic account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    @http.route('/api/v1/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['PUT'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='put',
        resource_name='analytic-account',
        request_model=AnalyticClassUpdateRequestModel,
        response_model=AnalyticClassResponseModel,
        tags=['Analytic Classes'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def update_analytic_account(self, analytic_class_id: int, **kwargs) -> Dict[str, Any]:
        logger.info(f"Processing update analytic account request for analytic_class_id: {analytic_class_id}")
        
        try:
            # Get and validate request data
            data = validate_request_data(request, AnalyticClassUpdateRequestModel)
            if not isinstance(data, AnalyticClassUpdateRequestModel):
                return data
                
            return self._update_analytic_account_record(request, analytic_class_id, data)
        except UserError as e:
            logger.error(f"User error in update analytic account: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error in update analytic account: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.UNPROCESSABLE_ENTITY)
        except IntegrityError as e:
            logger.error(f"Database integrity error in update analytic account: {str(e)}")
            if 'unique constraint' in str(e).lower():
                return APIResponse.error_response(message="Analytic class name already exists", errors=str(e), status=HTTPStatus.CONFLICT)
            elif 'foreign key constraint' in str(e).lower():
                return APIResponse.error_response(message="Invalid reference ID", errors=str(e), status=HTTPStatus.BAD_REQUEST)
            return APIResponse.error_response(message="Database constraint violation", errors=str(e), status=HTTPStatus.CONFLICT)
        except Exception as e:
            logger.error(f"Failed to update analytic account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _update_analytic_account_record(self, request, analytic_class_id: int, analytic_account_model: AnalyticClassUpdateRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):
            return company_id
        
        
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                analytic_account_service = AnalyticAccountService(request.env)
                is_valid, error_message = analytic_account_service.validate_analytic_account(analytic_class_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid analytic class: {error_message}',
                        errors=f'Invalid analytic_class_id: {analytic_class_id}', status=HTTPStatus.NOT_FOUND
                    )
                analytic_account = analytic_account_service.browse(analytic_class_id)
                analytic_account_vals = analytic_account_model.update_analytic_class_vals()
                analytic_account.write(analytic_account_vals)
                return self._prepare_success_response(analytic_account)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to update analytic account: {str(e)}")
            raise

    def _create_analytic_account_record(self, request, analytic_account_model: AnalyticClassCreateRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):  # If error response
                return company_id
        
        analytic_account_vals = analytic_account_model.create_analytic_class_vals(company_id)

        cursor = request.env.cr
        try:
            with cursor.savepoint():
                analytic_account = self._save_analytic_account(request, analytic_account_vals)
                return self._prepare_success_response(analytic_account, status=HTTPStatus.CREATED)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create Analytic Class: {str(e)}")
            raise
    
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
    
    def _prepare_success_response(self, analytic_account: Any, status: Optional[Any] = HTTPStatus.OK) -> Dict[str, Any]:
        response_data = AnalyticClassResponseModel.create_analytic_class_response(analytic_account)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=status
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
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.NOT_FOUND
                )
            domain.append(('company_id', '=', int(company_id)))
            logger.debug(f"Added company_id filter: {company_id}")

        # Add active status filter
        if active is not None:
            if active.lower() not in ['true', 'false']:
                return [], APIResponse.error_response(message='Invalid active parameter',
                    errors='active parameter must be "true" or "false"', status=HTTPStatus.BAD_REQUEST)
            active = active.lower() == 'true'
            domain.append(('active', '=', active))
            logger.debug(f"Added active filter: {active}")


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
            offset=(start_position-1),
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
                errors='Invalid analytic_class_id', status=HTTPStatus.BAD_REQUEST
            )

        response_data = AnalyticClassResponseModel.create_analytic_class_response(analytic_account)
        return APIResponse.success_response(response_data.model_dump(mode='json'))
    
