from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union
from odoo import http
from odoo.http import request
from .auth_middleware import validate_token_middleware
from ..logger.logger import logger
from ..utils import APIResponse, get_company_from_headers, validate_request_data
from ..schemas.common import ACCESS_TOKEN_HEADER, COMPANY_HEADERS
from ..schemas.partner import (CustomerModel, CustomerCreateRequestModel, CustomerResponseModel, CustomerListResponseModel,
                                VendorModel, VendorCreateRequestModel, VendorResponseModel, VendorListResponseModel)
from ..repository.partner import PartnerService
from ..repository.company import CompanyService
from ..swagger.swagger_generator import swagger_gen



class PartnerAPI(http.Controller):
    
    @http.route('/api/v1/customers', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='customer',
        request_model=CustomerCreateRequestModel,
        response_model=CustomerResponseModel,
        tags=['Customers'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def create_customer(self, **kwargs):
        # """
        # Create a new customer in Odoo.
        # """
        try:
            # Get and validate request data
            data = validate_request_data(request, CustomerCreateRequestModel)
            if not isinstance(data, CustomerCreateRequestModel):  # If error response
                return data

            return self._create_partner_record(request, data, False)
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
    @http.route('/api/v1/vendors', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='create',
        resource_name='vendor',
        request_model=VendorCreateRequestModel,
        response_model=VendorResponseModel,
        tags=['Vendors'],
        additional_headers=ACCESS_TOKEN_HEADER + COMPANY_HEADERS
    )
    def create_vendor(self, **kwargs):
        # """
        # Create a new vendor in Odoo.
        # """
        try:
            # Get and validate request data
            data = validate_request_data(request, VendorCreateRequestModel)
            if not isinstance(data, VendorCreateRequestModel):  # If error response
                return data

            return self._create_partner_record(request, data, True)
        except Exception as e:
            logger.error(f"Failed to create vendor: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

    
    @http.route('/api/v1/customers/<int:customer_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='customer',
        response_model=CustomerResponseModel,
        tags=['Customers'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_customer(self, customer_id: int, company_id: int):
        try:
            company_service = CompanyService(request.env)
            partner_service = PartnerService(request.env)
            domain = [('id', '=', customer_id)]
            category_id = partner_service.get_default_customer_category()
            domain.append(('category_id', 'child_of', int(category_id)))
            
            
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))

            return self._fetch_single_partner(domain, False)

        except Exception as e:
            logger.error(f"Error in get_customer: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    @http.route('/api/v1/vendors/<int:vendor_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='vendor',
        response_model=VendorResponseModel,
        tags=['Vendors'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_vendor(self, vendor_id: int, company_id: int):
        try:
            partner_service = PartnerService(request.env)
            company_service = CompanyService(request.env)
            domain = [('id', '=', vendor_id)]
            category_id = partner_service.get_default_vendor_category()
            domain.append(('category_id', 'child_of', int(category_id)))
            
            # Validate and add company filter
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return [], APIResponse.error_response(message=f'Invalid company: {error_message}',
                    errors=f'Invalid company_id: {company_id}', status=HTTPStatus.UNPROCESSABLE_ENTITY
                )
            domain.append(('company_id', '=', int(company_id)))

            return self._fetch_single_partner(domain, True)

        except Exception as e:
            logger.error(f"Error in get_customer: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    
    @http.route('/api/v1/vendors/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='vendor',
        response_model=VendorListResponseModel,
        tags=['Vendors'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_vendors(self, company_id: int, DisplayName: Optional[str] = None, active: Optional[str] = None, 
                     maxresults: int = 100, startposition: int = 0, **kwargs
                     ) -> Dict[str, Any]:
        try:
            domain, error_response = self._build_search_domain(
                DisplayName, company_id, active, True
            )
            if error_response:
                return error_response

            return self._fetch_partners(
                domain, int(startposition), int(maxresults), True
            )
        except Exception as e:
            logger.error(f"Error in list_vendors: {str(e)}")
            return APIResponse.error_response(message=f'An error occurred: {str(e)}',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    @http.route('/api/v1/customers/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='customer',
        response_model=CustomerListResponseModel,
        tags=['Customers'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def list_customers(self, company_id: int, DisplayName: Optional[str] = None, active: Optional[str] = None, 
                       maxresults: int = 100, startposition: int = 0, **kwargs
                     ) -> Dict[str, Any]:
        try:
            domain, error_response = self._build_search_domain(
                DisplayName, company_id, active, False
            )
            if error_response:
                return error_response

            return self._fetch_partners(
                domain, int(startposition), int(maxresults), False
            )
        except Exception as e:
            logger.error(f"Error in list_customers: {str(e)}")
            return APIResponse.error_response(message=f'An error occurred: {str(e)}',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        

    @http.route('/api/v1/vendors/<int:vendor_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='vendor',
        tags=['Vendors'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_vendor(self, vendor_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                self.delete_partner(vendor_id)
                return APIResponse.success_response({'message':'Venodr deleted successfully'})
        except Exception as e:
            cursor.rollback()  
            return APIResponse.error_response(message='An error occurred while deleting the vendor', errors=str(e), status=500)
        
    @http.route('/api/v1/customers/<int:customer_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='customer',
        tags=['Customers'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_customer(self, customer_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                self.delete_partner(customer_id)
                return APIResponse.success_response({'message':'Customer deleted successfully'})
        except Exception as e:
            cursor.rollback()  
            return APIResponse.error_response(message='An error occurred while deleting the customer', errors=str(e), status=500)
        
        

    def _create_partner_record(self, request, partner_model: Union[CustomerCreateRequestModel, VendorCreateRequestModel], is_vendor: bool) -> Dict[str, Any]:
        company_id = get_company_from_headers(request)
        if not isinstance(company_id, int):  # If error response
                return company_id
        
        if is_vendor:
            partner_vals = partner_model.create_vendor_vals(company_id)
        else:
            partner_vals = partner_model.create_customer_vals(company_id)
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                partner = self._save_partner(request, partner_vals)
                return self._prepare_success_response(partner, is_vendor)
        except Exception as e:
            cursor.rollback()
            logger.error(f"Failed to create partner: {str(e)}")
            return APIResponse.error_response(message='Failed to process request',
                errors=str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def _save_partner(self, request, partner_vals: Dict[str, Any]) -> Any:
        partner_service = PartnerService(request.env)
        partner = partner_service.create(partner_vals)
        return partner
    
    def _prepare_success_response(self, partner: Any, is_vendor:bool) -> Dict[str, Any]:
        if is_vendor:
            response_data = VendorResponseModel.create_vendor_response(partner)
        else:
            response_data = CustomerResponseModel.create_customer_response(partner)
        return APIResponse.success_response(response_data.model_dump(mode='json'),
            status=HTTPStatus.CREATED
        )

    def _build_search_domain(self, DisplayName: Optional[str], company_id: int, active: Optional[str], is_vendor: bool
                             ) -> Tuple[List[Tuple], Optional[Dict[str, Any]]]:
        domain = []
        company_service = CompanyService(request.env)
        partner_service = PartnerService(request.env)

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
            active = active.lower() == 'true'
            domain.append(('active', '=', active))
            logger.debug(f"Added active filter: {active}")

        # Add name filter
        if DisplayName:
            domain.append(('name', 'ilike', DisplayName))
            logger.debug(f"Added name filter: {DisplayName}")
        
        category_id = partner_service.get_default_vendor_category() if is_vendor else partner_service.get_default_customer_category()
        domain.append(('category_id', 'child_of', int(category_id)))

        logger.debug(f"Final search domain: {domain}")
        return domain, None
    
    def _fetch_partners(self, domain: List[Tuple], start_position: int, max_results: int, is_vendor: bool) -> Dict[str, Any]:
        # Get total count
        partner_service = PartnerService(request.env)
        total_count = partner_service.search_count(domain)
        logger.info(f"Total matching partners: {total_count}")

        # Search for partners
        partners = partner_service.search(
            domain,
            limit=max_results,
            offset=start_position,
            order='id DESC'
        )
        logger.info(f"Retrieved {len(partners)} partners")

        return self._prepare_list_response(
            partners, total_count, start_position, is_vendor
        )

    def _prepare_list_response(self, partners: Any, total_count: int, start_position: int, is_vendor: bool) -> Dict[str, Any]:
        if is_vendor:
            vendor_data = [VendorModel.vendor_object(partner) for partner in partners]
            response_data = VendorListResponseModel.list_vendor_response(
                vendor_data, total_count, start_position, len(partners)
            )
        else:
            customer_data = [CustomerModel.customer_object(partner) for partner in partners]
            response_data = CustomerListResponseModel.list_customer_response(
                customer_data, total_count, start_position, len(partners)
            )
        
        return APIResponse.success_response(response_data.model_dump(mode='json'))
    

    def _fetch_single_partner(self, domain: List[Tuple], is_vendor: bool) -> Dict[str, Any]:
        partner_service = PartnerService(request.env)
        partner = partner_service.search(domain, limit=1)
        
        if is_vendor:
            if not partner.exists():
                return APIResponse.error_response(message='Vendor not found',
                    errors='Invalid vendor_id', status=HTTPStatus.NOT_FOUND
                )
            response_data = VendorResponseModel.create_vendor_response(partner)
        else:
            if not partner.exists():
                return APIResponse.error_response(message='Customer not found',
                    errors='Invalid customer_id', status=HTTPStatus.NOT_FOUND
                )
            response_data = CustomerResponseModel.create_customer_response(partner)
        return APIResponse.success_response(response_data.model_dump(mode='json'))
    

    def delete_partner(self, partner_id):
        partner_service = PartnerService(request.env)
        partner = partner_service.browse(partner_id)
        if not partner.exists():
            return APIResponse.error_response(message='Partner not found', errors='Invalid partner_id', status=404)
            
        # partner.unlink()  # Delete the partner
        partner.write({'active': False})