from datetime import datetime
from odoo import http
from odoo.http import request
import json
from .common import APIResponse, validate_and_convert_data, get_request_data
from .validation_schema import partner_expected_fields
from .utils import validate_company, validate_partner_category, get_default_customer_category, get_default_vendor_category

from ..swagger.common import swagger_doc
from ..swagger.partner import partners_docs
from .schemas.partner import PARTNER_SCHEMA

class PartnerAPI(http.Controller):

    def validate_and_prepare_partner_data(self, data, analytic_account_expected_fields, is_vendor=None):
        success, converted_data = validate_and_convert_data(data, analytic_account_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
        
        # Create the partner
        partner_vals = {
            'name': converted_data['name'],
            'company_id': company_id,
            'email': converted_data.get('email'),
            'phone': converted_data.get('phone'),
            'is_company': converted_data['is_company'],
            'parent_id': converted_data.get('parent_id'),
            'street': converted_data.get('street'),
            'street2': converted_data.get('street2'),
            'zip': converted_data.get('zip'),
            'city': converted_data.get('city'),
            'state_id': converted_data.get('state_id'),
            'country_id': converted_data.get('country_id'),
        }

        # category_id = converted_data.get('category_id')
        category_id = get_default_vendor_category(request) if is_vendor else get_default_customer_category(request)
        if category_id:
            is_valid, error_message = validate_partner_category(request, category_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid category: {error_message}', f'Invalid category_id: {category_id}')            
        partner_vals['category_id'] = [(6, 0, [category_id])]

        return True, partner_vals
    
    def prepare_partner_response(self, partner):
        return {
                'id': partner.id,
                'name': partner.name,
                'company': {
                    'id': partner.company_id.id,
                    'name': partner.company_id.name
                } if partner.company_id else None,
                'email': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'active': partner.active,
                'is_company': partner.is_company,
                'parent': {
                    'id': partner.parent_id.id,
                    'name': partner.parent_id.name
                } if partner.parent_id else None,
                'street': partner.street,
                'street2': partner.street2,
                'zip': partner.zip,
                'city': partner.city,
                'state': partner.state_id.name if partner.state_id else None,
                'country': partner.country_id.name if partner.country_id else None,
            }

    def get_partners(self, request, company_id=None, active=None, is_vendor=None, limit=20, offset=0):
        domain = []
        if company_id:
            is_valid, error_message = validate_company(request, int(company_id))
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            domain.append(('company_id', '=', int(company_id)))
        if active is not None:
            active = active.lower() == 'true'
            domain.append(('active', '=', active))
        category_id = get_default_vendor_category(request) if is_vendor else get_default_customer_category(request)
        if category_id:
            is_valid, error_message = validate_partner_category(request, int(category_id))
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid category: {error_message}', f'Invalid category_id: {category_id}') 
            domain.append(('category_id', 'child_of', int(category_id)))

        limit = int(limit)
        offset = int(offset)

        # Get total count for pagination
        total_count = request.env['res.partner'].sudo().search_count(domain)

        # Get partners with pagination
        partners = request.env['res.partner'].sudo().search(
            domain,
        limit=limit,
            offset=offset,
            order='name asc'
        )
        partners = request.env['res.partner'].sudo().search(domain)

        # Prepare response data
        partners_data = []
        for partner in partners:
            partner_info = self.prepare_partner_response(partner)
            partners_data.append(partner_info)

        return True, {
            'partners': partners_data,
            'pagination': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
        }

        
    @http.route('/api/customers', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(partners_docs['create_customer'])
    def create_customer(self, **kwargs):
        # """
        # Create a new customer in Odoo.
        # """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data= get_request_data(request)

                success, partner_vals = self.validate_and_prepare_partner_data(data, PARTNER_SCHEMA, False)
                if not success:
                    return partner_vals
                
                partner = request.env['res.partner'].sudo().create(partner_vals)

                # Prepare response data
                response_data = self.prepare_partner_response(partner)
                return APIResponse.success_response(message='Customer created successfully', data=response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the customer', errors=str(e), status=500)
        
    @http.route('/api/vendors', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(partners_docs['create_vendor'])
    def create_vendor(self, **kwargs):
        # """
        # Create a new vendor in Odoo.
        # """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data= get_request_data(request)

                success, vendor_vals = self.validate_and_prepare_partner_data(data, PARTNER_SCHEMA, True)
                if not success:
                    return vendor_vals
                
                partner = request.env['res.partner'].sudo().create(vendor_vals)

                # Prepare response data
                response_data = self.prepare_partner_response(partner)
                return APIResponse.success_response(message='Vendor created successfully', data=response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the Vendor', errors=str(e), status=500)
        
    @http.route('/api/customers/<int:customer_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['get_customer'])
    def get_customer(self, customer_id):
        try:
            customer = request.env['res.partner'].sudo().browse(customer_id)
            if not customer.exists():
                return APIResponse.error_response(message='Customer not found', errors='Invalid customer_id', status=404)
                
            # Prepare response data
            response_data = self.prepare_partner_response(customer)
            return APIResponse.success_response(message='Customer retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the customer', errors=str(e), status=500)
        
    @http.route('/api/vendors/<int:vendor_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['get_vendor'])
    def get_vendor(self, vendor_id, **kwargs):
        try:
            vendor = request.env['res.partner'].sudo().browse(vendor_id)
            if not vendor.exists():
                return APIResponse.error_response(message='Vendor not found', errors='Invalid vendor_id', status=404)
            
            # Prepare response data
            response_data = self.prepare_partner_response(vendor)
            return APIResponse.success_response(message='Vendor retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the vendor', errors=str(e), status=500)
        
        
    @http.route('/api/vendors/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['list_vendors'])
    def list_vendors(self, company_id=None, active=None, limit=20, offset=0, **kwargs):
        try:
            success, response_data = self.get_partners(request, company_id, active, True, limit, offset)
            if not success:
                return response_data
            return APIResponse.success_response(message='Vendor retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the Vendor', errors=str(e), status=500)
        
    @http.route('/api/customers/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['list_customers'])
    def list_customers(self, company_id=None, active=None, limit=20, offset=0, **kwargs):
        try:
            success, response_data = self.get_partners(request, company_id, active, False, limit, offset)
            if not success:
                return response_data
            return APIResponse.success_response(message='Vendor retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the Vendor', errors=str(e), status=500)
        

    def delete_partner(self, partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            return APIResponse.error_response(message='Partner not found', errors='Invalid partner_id', status=404)
            
        # partner.unlink()  # Delete the partner
        partner.write({'active': False})
        

    @http.route('/api/vendors/<int:vendor_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(partners_docs['delete_vendor'])
    def delete_vendor(self, vendor_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                self.delete_partner(vendor_id)
                return APIResponse.success_response(message='Venodr deleted successfully')
        except Exception as e:
            cursor.rollback()  
            return APIResponse.error_response(message='An error occurred while deleting the vendor', errors=str(e), status=500)
        
    @http.route('/api/customers/<int:customer_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(partners_docs['delete_customer'])
    def delete_customer(self, customer_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                self.delete_partner(customer_id)
                return APIResponse.success_response(message='Customer deleted successfully')
        except Exception as e:
            cursor.rollback()  
            return APIResponse.error_response(message='An error occurred while deleting the customer', errors=str(e), status=500)
        

    # @http.route('/api/partner_category_list/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(partners_docs['list_partner_categories'])
    # def get_partner_category_list(self, **kwargs):
    #     try:
    #         categories = request.env['res.partner.category'].sudo().search([])
    #         if not categories:
    #             return APIResponse.success_response(message='No categories found', data=[])

    #         # Prepare response data
    #         response_data = [{'id': category.id, 'name': category.name, 'active': category.active} for category in categories]
    #         return APIResponse.success_response(message='Categories retrieved successfully', data=response_data)
    #     except Exception as e:
    #         return APIResponse.error_response(message='An error occurred while retrieving the categories', errors=str(e), status=500)
        


