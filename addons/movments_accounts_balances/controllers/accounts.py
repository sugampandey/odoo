from typing import Dict, Any, List, Optional, Tuple
from http import HTTPStatus
from odoo import http
from odoo.http import request
from ..utils import APIResponse, get_company_from_headers, get_payment_method_from_headers, validate_request_data, validate_pagination_params
from ..logger.logger import logger
from ..swagger.swagger_generator import swagger_gen
from ..schemas.accounts import AccountCreateRequestModel , AccountResponseModel, AccountModel, AccountListResponseModel, ACCOUNT_HEADERS
from ..schemas.common import ACCESS_TOKEN_HEADER
from ..mapping.accounts import ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING, ACCOUNT_TYPE_MAPPING
from ..repositories.journal import JournalService
from ..repositories.account import AccountService
from ..repositories.company import CompanyService
from ..middleware.auth_middleware import validate_token_middleware

class AccountAPI(http.Controller):

    @http.route('/api/v1/accounts', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='account',
        request_model=AccountCreateRequestModel,
        response_model=AccountResponseModel,
        tags=['Accounts'],
        additional_headers=ACCOUNT_HEADERS
    )
    def create_account(self, **kwargs) -> Dict[str, Any]:
        logger.info("Processing create account request")
        
        try:
            # Get and validate request data
            data = validate_request_data(request, AccountCreateRequestModel)
            if not isinstance(data, AccountCreateRequestModel):  # If error response
                return data

            # Create account
            return self._create_account_record(request, data)
        except Exception as e:
            logger.error(f"Failed to create account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)

    
    @http.route('/api/v1/accounts', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='account',
        response_model=AccountListResponseModel,
        tags=['Accounts'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_accounts(self, company_id: int, name: Optional[str] = None, account_type: Optional[str] = None,
        active: Optional[str] = None, maxresults: int = 100, startposition: int = 1, **kwargs
    ) -> Dict[str, Any]:
        try:
            logger.info(
                f"Fetching accounts with parameters: "
                f"account_type={account_type}, "
                f"company_id={company_id}, "
                f"active={active}"
            )
            # Validate pagination parameters
            is_valid, result = validate_pagination_params(startposition, maxresults)
            if not is_valid:
                return result
            startposition, maxresults = result
            
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
    
    
    @http.route('/api/v1/accounts/<int:account_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='account',
        response_model=AccountResponseModel,
        tags=['Accounts'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_account(self, account_id: int, company_id: int) -> Dict[str, Any]:
        try:
            domain = [('id', '=', account_id)]
            company_service = CompanyService(request.env)
            
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))

            return self._fetch_single_account(domain)

        except Exception as e:
            logger.error(f"Error in get_account: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


    @http.route('/api/v1/accounts/<int:account_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='account',
        tags=['Accounts'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_account(self, account_id, **kwargs):
        try:
            company_service = CompanyService(request.env)
            account_service = AccountService(request.env)
            company_id = int(kwargs.get('company_id')) if kwargs.get('company_id') else kwargs.get('company_id')
            if not company_id:
                return APIResponse.error_response(message='Company ID not provided', errors='company_id is required')
            
            # Validate company
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            
            # Validate account
            is_valid, error_message = account_service.validate_account(account_id, company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
        
            # Retrieve the account
            account = account_service.browse(account_id)

            # Delete the account
            account.write({'deprecated': True})
            return APIResponse.success_response()
        except Exception as e:
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
        
      
    @http.route('/api/v1/account-types', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='account-type',
        tags=['Accounts'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_account_types(self, **kwargs):
        account_types = [{"code": ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING[key], "name": key} for key in ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING.keys()]
        return APIResponse.success_response(account_types)
    
    def _create_account_record(self, request, account_model: AccountCreateRequestModel) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):  # If error response
                return company_id
        
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
        account_service = AccountService(request.env)
        account = account_service.create(account_vals)
        
        journal_vals = {
            'name': account.name,
            'code': account.code,
            'company_id': account.company_id.id,
            'default_account_id': account.id,
            'account_type': account.account_type,
            'payment_method': payment_method,
        }
        journal_service = JournalService(request.env)
        journal_service.create(journal_vals)
        return account

    def _prepare_success_response(self, account: Any) -> Dict[str, Any]:
        response_data = AccountResponseModel.create_account_response(account)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )
    
    def _build_search_domain(self, name: Optional[str], account_type: Optional[str],
                             company_id: int, active: Optional[str]
                             ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        domain = []
        company_service = CompanyService(request.env)
        
        # Add account type filter
        if account_type:
            mapped_type = ACCOUNT_TYPE_MAPPING.get(account_type)
            domain.append(('account_type', '=', mapped_type))
            logger.debug(f"Added account_type filter: {mapped_type}")

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

        # Add name filter
        if name:
            domain.append(('name', 'ilike', name))
            logger.debug(f"Added name filter: {name}")

        logger.debug(f"Final search domain: {domain}")
        return domain, None


    def _fetch_accounts(self, domain: List[Tuple], start_position: int, max_results: int) -> Dict[str, Any]:
        # Get total count
        account_service = AccountService(request.env)
        total_count = account_service.search_count(domain)
        logger.info(f"Total matching accounts: {total_count}")

        # Search for accounts
        accounts = account_service.search(
            domain,
            limit=max_results,
            offset=(start_position-1),
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
    
    def _fetch_single_account(self, domain: List[Tuple]) -> Dict[str, Any]:
        account_service = AccountService(request.env)
        account = account_service.search(domain, limit=1)
        
        if not account.exists():
            return APIResponse.error_response(message='Account not found',
                errors='Invalid account_id', status=HTTPStatus.BAD_REQUEST
            )

        response_data = AccountResponseModel.create_account_response(account)
        return APIResponse.success_response(response_data.model_dump(mode='json'))

