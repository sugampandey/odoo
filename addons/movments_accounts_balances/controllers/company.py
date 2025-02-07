from odoo import http
from odoo.http import request
import json
from .common import APIResponse, validate_and_convert_data, get_request_data
from .validation_schema import company_expected_fields

from ..swagger.common import swagger_doc
from ..swagger.company import companies_docs
from .schemas.company import COMPANY_SCHEMA
from ..constants import CONSTANTS

class CreateCompany(http.Controller):

    def create_default_product(self, request, company_id):
        default_product = request.env['product.template'].create({
            'name': 'Default Product',
            'default_code': CONSTANTS['PRODUCT_DEFAULT_CODE'],
            'company_id': company_id,
            'type': 'consu',
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': 0.0,
            'standard_price': 0.0,
        })
    
    # def create_journal(self, request, company_id, type, code, name):
    #     journal = request.env['account.journal'].create({
    #         'name': name,
    #         'code': code,
    #         'type': type,
    #         'company_id': company_id,
    #     })
    #     return journal
    # def create_default_journals(self, request, company_id):
    #     self.create_journal(request, company_id, 'sale', 'SALE', 'Sales Journal')
    #     self.create_journal(request, company_id, 'purchase', 'PURCHASE', 'Purchase Journal')
    #     self.create_journal(request, company_id, 'general', 'GENERAL', 'General Journal')

    @http.route('/api/companies', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(companies_docs['create_company'])
    def create_company(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                success, converted_data = validate_and_convert_data(data, COMPANY_SCHEMA)
                if success is not True:
                    return converted_data
                
                company_vals = {
                    'name': converted_data.get('name'),
                    'city': converted_data.get('city'),
                    'street': converted_data.get('street'),
                    'phone': converted_data.get('phone'),
                    'zip': converted_data.get('zip'),
                    'email': converted_data.get('email'),
                    'currency_id': converted_data.get('currency_id') or 2, # ID for USD, adjust as needed
                }
                company = request.env['res.company'].sudo().create(company_vals)
                default_product = self.create_default_product(request, company.id)
                # default_journals = self.create_default_journals(request, company.id)
                
                # prepare response data
                response_data = {
                    'id': company.id,
                    'name': company.name,
                    'city': company.city,
                    'street': company.street,
                    'phone': company.phone,
                    'zip': company.zip,
                    'email': company.email,
                    'currency': {
                        'id': company.currency_id.id,
                        'name': company.currency_id.name,
                        'symbol': company.currency_id.symbol
                    } if company.currency_id else None
                }
                return APIResponse.success_response(message="Company created successfully", data=response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message="An error occurred", errors=str(e), status=500)
        
    
    @http.route('/api/companies/<int:company_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @swagger_doc(companies_docs['get_company'])
    def get_company(self, company_id, **kwargs):
        """
            Get Company Details
        """
        try:
            company = request.env['res.company'].sudo().browse(company_id)
            if not company.exists():
                return APIResponse.error_response(message="Company not found", errors="Invalid company_id", status=404)
            
            # Prepare response data
            response_data = {
                'id': company.id,
                'name': company.name,
                'city': company.city,
                'street': company.street,
                'phone': company.phone,
                'zip': company.zip,
                'email': company.email,
                'active': company.active,
                'currency': {
                    'id': company.currency_id.id,
                    'name': company.currency_id.name,
                    'symbol': company.currency_id.symbol
                } if company.currency_id else None
            }
            return APIResponse.success_response(message="Company retrieved successfully", data=response_data)
        except Exception as e:
            return APIResponse.error_response(message="An error occurred", errors=str(e), status=500)
        
    @http.route('/api/companies/', type='http', auth='public', methods=['GET'], csrf=False)
    @swagger_doc(companies_docs['list_companies'])
    def list_companies(self, active=None, limit=20, offset=0, **kwargs):
        try:
            domain = []
            if active is not None:
                active = active.lower() == 'true'
                domain.append(('active', '=', active))
            limit = int(limit)
            offset = int(offset)
            # Get total count
            total_count = request.env['res.company'].sudo().search_count(domain)
            # Get paginated companies
            companies = request.env['res.company'].sudo().search(domain, limit=limit, offset=offset)
            companies_data = []
            for company in companies:
                companies_data.append({
                    'id': company.id,
                    'name': company.name,
                    'city': company.city,
                    'street': company.street,
                    'phone': company.phone,
                    'zip': company.zip,
                    'email': company.email,
                    'active': company.active,
                    'currency': {
                        'id': company.currency_id.id,
                        'name': company.currency_id.name,
                        'symbol': company.currency_id.symbol
                    } if company.currency_id else None
                })
            response_data = {
                'companies': companies_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message="Companys retrieved successfully", data=response_data)
        except Exception as e:
            return APIResponse.error_response(message="An error occurred", errors=str(e), status=500)
        

    @http.route('/api/companies/<int:company_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(companies_docs['delete_company'])
    def delete_company(self, company_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                company = request.env['res.company'].sudo().browse(company_id)
                if not company.exists():
                    return APIResponse.error_response(message='Company not found', errors='Invalid company_id', status=404)

                # Delete the company
                company.write({'active': False}) 

                return APIResponse.success_response(message='Company deactivated successfully')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deleting the company', errors=str(e), status=500)
    

