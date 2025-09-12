from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError, MissingError
from psycopg2 import IntegrityError
from ..middleware.auth_middleware import validate_token_middleware
from ..utils import APIResponse, validate_request_data, validate_pagination_params
from ..logger.logger import logger
from ..swagger.swagger_generator import swagger_gen
from ..schemas.company import CompanyModel, CompanyListResponseModel, CompanyCreateRequestModel, CompanyResponseModel
from ..repositories.company import CompanyService
from ..repositories.product import ProductTemplateService
from ..schemas.common import ACCESS_TOKEN_HEADER


class CompanyAPI(http.Controller):
    
    @http.route('/api/v1/companies', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='company',
        request_model=CompanyCreateRequestModel,
        response_model=CompanyResponseModel,
        tags=['Companies'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def create_company(self, **kwargs):
        cursor = request.env.cr
        try:
            # Get and validate request data
            data = validate_request_data(request, CompanyCreateRequestModel)
            if not isinstance(data, CompanyCreateRequestModel):  # If error response
                return data
            
            # Create company
            return self._create_company_record(request, data)
        except UserError as e:
            logger.error(f"User error in create company: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error in create company: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.UNPROCESSABLE_ENTITY)
        except IntegrityError as e:
            logger.error(f"Database integrity error in create company: {str(e)}")
            if 'unique constraint' in str(e).lower():
                return APIResponse.error_response(message="Company name already exists", errors=str(e), status=HTTPStatus.CONFLICT)
            elif 'foreign key constraint' in str(e).lower():
                return APIResponse.error_response(message="Invalid reference ID", errors=str(e), status=HTTPStatus.BAD_REQUEST)
            return APIResponse.error_response(message="Database constraint violation", errors=str(e), status=HTTPStatus.CONFLICT)
        except Exception as e:
            logger.error(f"Error in create_company: {str(e)}")
            return APIResponse.error_response(message="Failed to process request", errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
    
    @http.route('/api/v1/companies/<int:company_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='company',
        response_model=CompanyResponseModel,
        tags=['Companies'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_company(self, company_id: int, **kwargs):
        """Get company details by ID
        
        Args:
            company_id: The unique identifier of the company
        """
        try:
            company_service = CompanyService(request.env)
            company = company_service.browse(company_id)
            if not company.exists():
                return APIResponse.error_response(message='Company not found',
                errors='Invalid company_id', status=HTTPStatus.NOT_FOUND
                )
            
            # Prepare response data
            response_data = CompanyResponseModel.create_company_response(company)
            return APIResponse.success_response(response_data.model_dump(mode='json'))
        except Exception as e:
            logger.error(f"Error in get_company: {str(e)}")
            return APIResponse.error_response(message="Failed to process request", errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)

    
    @http.route('/api/v1/companies', type='http', auth='public', methods=['GET'], csrf=False)
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='company',
        response_model=CompanyListResponseModel,
        tags=['Companies'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_companies(self, name: Optional[str] = None, active: Optional[str] = None, 
                       maxresults: int = 100, startposition: int = 1, **kwargs):
        try:
            # Validate pagination parameters
            is_valid, result = validate_pagination_params(startposition, maxresults)
            if not is_valid:
                return result
            startposition, maxresults = result

            # Build search domain and validate company
            domain, error_response = self._build_search_domain(name, active)
            if error_response:
                return error_response

            return self._fetch_companies(
                domain, int(startposition), int(maxresults)
            )
        except Exception as e:
            logger.error(f"Error in list_companies: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )       

    @http.route('/api/v1/companies/<int:company_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='company',
        tags=['Companies'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_company(self, company_id: int, **kwargs):
        """Delete (deactivate) a company by ID
        
        Args:
            company_id: The unique identifier of the company to delete
        """
        cursor = request.env.cr
        try:
            company_service = CompanyService(request.env)
            company = company_service.browse(company_id)
            if not company.exists():
                return APIResponse.error_response(message='Company not found', errors='Invalid company_id', status=HTTPStatus.NOT_FOUND)

            # Delete the company
            company.write({'active': False}) 

            return APIResponse.success_response({'message':'Company deactivated successfully'})
        except UserError as e:
            cursor.rollback()
            logger.error(f"User error in delete company: {str(e)}")
            return APIResponse.error_response(message=str(e), errors=str(e), status=HTTPStatus.BAD_REQUEST)
        except IntegrityError as e:
            cursor.rollback()
            logger.error(f"Database integrity error in delete company: {str(e)}")
            return APIResponse.error_response(message="Cannot delete: company is referenced elsewhere", 
                errors=str(e), status=HTTPStatus.CONFLICT)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Error in delete_company: {str(e)}")
            return APIResponse.error_response(message='Failed to process request', 
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        


    def _save_company(self, request, company_vals: Dict[str, Any]) -> Any:
        company_service = CompanyService(request.env)
        company = company_service.create(company_vals)
        return company

    def _prepare_success_response(self, company: Any) -> Dict[str, Any]:
        response_data = CompanyResponseModel.create_company_response(company)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )
    
    def _create_company_record(self, request, company_model: CompanyCreateRequestModel) -> Dict[str, Any]:
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                product_service = ProductTemplateService(request.env)
                company_vals = company_model.create_company_vals(request)
                company = self._save_company(request, company_vals)
                product_service.create_default_product(company.id)
                return self._prepare_success_response(company)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create company: {str(e)}")
            raise 

    def _build_search_domain(self, name: Optional[str], active: Optional[str]
                             ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        try:
            domain = []
            # Add active status filter
            if active is not None:
                if active.lower() not in ['true', 'false']:
                    return [], APIResponse.error_response(message='Invalid active parameter',
                        errors='active parameter must be "true" or "false"', status=HTTPStatus.BAD_REQUEST)
                active = active.lower() == 'true'
                domain.append(('active', '=', active))
                logger.debug(f"Added active filter: {active}")

            # Add name filter
            if name:
                domain.append(('name', 'ilike', name))
                logger.debug(f"Added name filter: {name}")

            logger.debug(f"Final search domain: {domain}")
            return domain, None
        except Exception as e:
            logger.error(f"Error building search domain: {str(e)}")
            return [], APIResponse.error_response(message="Failed to build search criteria", 
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def _fetch_companies(self, domain: List[Tuple], start_position: int, max_results: int) -> Dict[str, Any]:
        try:
            # Get total count
            company_service = CompanyService(request.env)
            total_count = company_service.search_count(domain)
            logger.info(f"Total matching companies: {total_count}")

            # Search for companies
            companies = company_service.search(
                domain,
                limit=max_results,
                offset=(start_position-1),
                order='id DESC'
            )
            logger.info(f"Retrieved {len(companies)} companies")

            return self._prepare_list_response(companies, total_count, start_position)
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            return APIResponse.error_response(message="Failed to fetch companies", 
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    def _prepare_list_response(self, companies: Any, total_count: int, start_position: int) -> Dict[str, Any]:
        try:
            companies_data = [CompanyModel.company_object(company) for company in companies]
            
            response_data = CompanyListResponseModel.list_company_response(
                companies_data, total_count, start_position, len(companies)
            )
            
            return APIResponse.success_response(response_data.model_dump(mode='json'), status=HTTPStatus.OK)
        except Exception as e:
            logger.error(f"Error preparing list response: {str(e)}")
            return APIResponse.error_response(message="Failed to prepare response", 
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
    

