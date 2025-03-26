
from odoo import http
from odoo.http import request
import datetime
from ..common import APIResponse, validate_and_convert_data, get_request_data
from ..utils import format_date
from ..swagger.common import swagger_doc
from ..swagger.company import companies_docs
from ..schemas.company import COMPANY_SCHEMA, CompanyModel, CompanyListResponseModel, CompanyCreateRequestModel, CompanyQueryResponseModel, CompanyResponseModel
from ..schemas.common import CurrencyRefModel, MetaDataModel, PhoneNumberModel, EmailAddressModel
from ..constants import CONSTANTS

class CreateCompany(http.Controller):

    def create_default_product(self, request, company_id):
        default_product = request.env['product.template'].sudo().create({
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

    def company_object(self, company):
        meta_data = MetaDataModel(
            CreateTime = company.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            LastUpdatedTime = company.write_date.strftime('%Y-%m-%d %H:%M:%S'),
        )
        if company.currency_id:
            currency_ref = CurrencyRefModel(
                name=company.currency_id.full_name,
                value=company.currency_id.name
            )
        else:
            currency_ref = None
        phone = PhoneNumberModel(FreeFormNumber=company.phone)
        email = EmailAddressModel(Address=company.email)
        return CompanyModel(
            Id=company.id,
            Name=company.name,
            Active=company.active,
            MetaData=meta_data,
            CurrencyRef=currency_ref,
            PrimaryPhone=phone,
            PrimaryEmailAddr=email,
        )
    
    def create_company_response(self, company):
        return CompanyResponseModel(
            Company=self.company_object(company),
            time=format_date(datetime.datetime.now())
        ).to_dict()
    
    def list_company_response(self, company_data, startPosition, maxResults, totalCount):
        QueryResponse=CompanyQueryResponseModel(
                startPosition=startPosition,
                Company=company_data,
                maxResults=maxResults,
                totalCount= totalCount
            )
        return CompanyListResponseModel(
            QueryResponse=QueryResponse,
            time=format_date(datetime.datetime.now())
        ).to_dict()
    
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
                
                currency_ref = converted_data.get('CurrencyRef')
                currency_id = None
                if currency_ref:
                    currency_value = currency_ref.get('value', 'USD')
                    currency = request.env['res.currency'].sudo().search([('name', '=', currency_value)], limit=1)
                    if not currency:
                        return APIResponse.error_response(message='Invalid currency', errors='Invalid currency_ref')
                    currency_id = currency.id
                
                company_vals = {
                    'name': converted_data.get('Name'),
                    'phone': converted_data['PrimaryPhone']['FreeFormNumber'] if converted_data.get('PrimaryPhone') else converted_data.get('PrimaryPhone'),
                    'email': converted_data['PrimaryEmailAddr']['Address'] if converted_data.get('PrimaryEmailAddr') else converted_data.get('PrimaryEmailAddr'),
                    'currency_id': currency_id or 2, # ID for USD, adjust as needed
                    # 'city': converted_data.get('city'),
                    # 'street': converted_data.get('street'),
                    # 'zip': converted_data.get('zip'),
                }
                
                company = request.env['res.company'].sudo().create(company_vals)
                default_product = self.create_default_product(request, company.id)
                # default_journals = self.create_default_journals(request, company.id)
                
                # prepare response data
                response_data = self.create_company_response(company)
                return APIResponse.success_response(response_data, status=201)
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
            response_data = self.create_company_response(company)
            return APIResponse.success_response(response_data)
        except Exception as e:
            return APIResponse.error_response(message="An error occurred", errors=str(e), status=500)
        
    @http.route('/api/companies/', type='http', auth='public', methods=['GET'], csrf=False)
    @swagger_doc(companies_docs['list_companies'])
    def list_companies(self, name=None, active=None, maxresults=100, startposition=0, **kwargs):
        try:
            domain = []
            if active is not None:
                active = active.lower() == 'true'
                domain.append(('active', '=', active))
            if name:
                domain.append(('name', 'ilike', name))
            startposition = int(startposition)
            maxresults = int(maxresults)
            # Get total count
            total_count = request.env['res.company'].sudo().search_count(domain)
            # Get paginated companies
            companies = request.env['res.company'].sudo().search(
                domain, 
                limit=maxresults, 
                offset=startposition,
                order='id DESC'
                )
            companies_data = []
            for company in companies:
                companies_data.append(self.company_object(company))
            response_data = self.list_company_response(companies_data, startposition, maxresults, total_count)
            return APIResponse.success_response(response_data)
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
    

