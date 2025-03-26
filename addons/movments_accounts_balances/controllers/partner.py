import datetime
from odoo import http
from odoo.http import request
import json
from ..common import APIResponse, get_company_from_headers, validate_and_convert_data, get_request_data
from ..utils import validate_company, validate_partner_category, get_default_customer_category, get_default_vendor_category, format_date
from ..swagger.common import swagger_doc
from ..swagger.partner import partners_docs
from ..schemas.partner import (CUSTOMER_SCHEMA, CustomerModel, CustomerCreateRequestModel, CustomerResponseModel, CustomerListResponseModel, CustomerQueryResponseModel,
                              VENDOR_SCHEMA, VendorModel, VendorCreateRequestModel, VendorResponseModel, VendorListResponseModel, VendorQueryResponseModel)
from ..schemas.common import MetaDataModel, CurrencyRefModel, BillAddrModel, PhoneNumberModel, EmailAddressModel
from ..constants import CONSTANTS


class PartnerAPI(http.Controller):

    def validate_and_prepare_partner_data(self, data, company_id, partner_expected_fields, is_vendor=None):
        # Validate company
        company = request.env['res.company'].sudo().browse(company_id)
        if not company.exists():
            return False, APIResponse.error_response(message='Company not found', errors='Invalid company_id', status=400)
        
        success, converted_data = validate_and_convert_data(data, partner_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Create the partner
        partner_vals = {
            'display_name': converted_data['DisplayName'],
            'company_name': converted_data.get('CompanyName'),
            
            'street': converted_data['BillAddr']['Line1'] if converted_data.get('BillAddr') else None,
            'street2': converted_data['BillAddr']['Line2'] if converted_data.get('BillAddr') else None,
            'zip': converted_data['BillAddr']['PostalCode'] if converted_data.get('BillAddr') else None,
            'city': converted_data['BillAddr']['City'] if converted_data.get('BillAddr') else None,
            # 'state_id': converted_data['BillAddr']['CountrySubDivisionCode'] if converted_data.get('BillAddr') else None,
            # 'country_id': converted_data['BillAddr']['Country'] if converted_data.get('BillAddr') else None,

            'phone': converted_data['PrimaryPhone']['FreeFormNumber'] if converted_data.get('PrimaryPhone') else converted_data.get('PrimaryPhone'),
            'mobile': converted_data['Mobile']['FreeFormNumber'] if converted_data.get('Mobile') else converted_data.get('Mobile'),
            'email': converted_data['PrimaryEmailAddr']['Address'] if converted_data.get('PrimaryEmailAddr') else converted_data.get('PrimaryEmailAddr'),
            'title': converted_data.get('Title'),
            'name': converted_data.get('GivenName'),
            'company_id': company_id,
            # 'is_company': converted_data.get('is_company'),
        }
        if is_vendor:
            partner_vals['vendor_1099'] = converted_data.get('Vendor1099')

        # category_id = converted_data.get('category_id')
        category_id = get_default_vendor_category(request) if is_vendor else get_default_customer_category(request)
        if category_id:
            is_valid, error_message = validate_partner_category(request, category_id)
            if not is_valid:
                return False, APIResponse.error_response(message=f'Invalid category_id: {category_id}', errors=f'Invalid category: {error_message}', status=400)            
        partner_vals['category_id'] = [(6, 0, [category_id])]

        return True, partner_vals

    
    def partner_object(self, partner, is_vendor):
        meta_data = MetaDataModel(
            CreateTime = partner.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            LastUpdatedTime = partner.write_date.strftime('%Y-%m-%d %H:%M:%S'),
        )
        if partner.currency_id:
            currency_ref = CurrencyRefModel(
                name=partner.currency_id.full_name,
                value=partner.currency_id.name
            )
        else:
            currency_ref = None
        BillAddr = BillAddrModel(
            Line1=partner.street,
            Line2=partner.street2,
            PostalCode=partner.zip,
            City=partner.city,
            CountrySubDivisionCode=partner.state_id.name if partner.state_id else None,
            Country=partner.country_id.name if partner.country_id else None,
        )
        phone = PhoneNumberModel(FreeFormNumber=partner.phone)
        email = EmailAddressModel(Address=partner.email)
        if is_vendor:
            return VendorModel(
            Id=partner.id,
            DisplayName=partner.display_name,
            GivenName=partner.name,
            CompanyName=partner.company_name,
            BillAddr=BillAddr,
            Active=partner.active,
            Vendor1099=partner.vendor_1099,
            MetaData=meta_data,
            CurrencyRef=currency_ref,
            PrimaryPhone=phone,
            PrimaryEmailAddr=email,
        )
        return CustomerModel(
            Id=partner.id,
            DisplayName=partner.display_name,
            GivenName=partner.name,
            CompanyName=partner.company_name,
            BillAddr=BillAddr,
            Active=partner.active,
            MetaData=meta_data,
            CurrencyRef=currency_ref,
            PrimaryPhone=phone,
            PrimaryEmailAddr=email,
        )
    
    def prepare_partner_response(self, partner, is_vendor=None):
        if is_vendor:
            return VendorResponseModel(
                Vendor=self.partner_object(partner, True),
                time=format_date(datetime.datetime.now())
            ).to_dict()
        return CustomerResponseModel(
            Customer=self.partner_object(partner, False),
            time=format_date(datetime.datetime.now())
        ).to_dict()
    
    def list_partner_response(self, partner_data, startPosition, maxResults, totalCount, is_vendor=None):
        if is_vendor:
            QueryResponse=VendorQueryResponseModel(
                    startPosition=startPosition,
                    Vendor=partner_data,
                    maxResults=maxResults,
                    totalCount= totalCount
                )
            return VendorListResponseModel(
                QueryResponse=QueryResponse,
                time=format_date(datetime.datetime.now())
            ).to_dict()
        QueryResponse=CustomerQueryResponseModel(
                startPosition=startPosition,
                Customer=partner_data,
                maxResults=maxResults,
                totalCount= totalCount
            )
        return CustomerListResponseModel(
            QueryResponse=QueryResponse,
            time=format_date(datetime.datetime.now())
        ).to_dict()
        

    def get_partners(self, request, company_id=None, DisplayName=None, active=None, is_vendor=False, maxresults=100, startposition=0):
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
        domain.append(('category_id', 'child_of', int(category_id)))
        if DisplayName:
            domain.append(('display_name', 'ilike', f'%{DisplayName}%'))

        startposition = int(startposition)
        maxresults = int(maxresults)

        # Get total count for pagination
        total_count = request.env['res.partner'].sudo().search_count(domain)

        # Get partners with pagination
        partners = request.env['res.partner'].sudo().search(
            domain,
            limit=maxresults, 
            offset=startposition,
            order='id DESC'
        )

        # Prepare response data
        partners_data = []
        for partner in partners:
            partners_data.append(self.partner_object(partner, is_vendor))
        response_data = self.list_partner_response(partners_data, startposition, len(partners), total_count, is_vendor)

        return True, response_data

        
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
                company_id = get_company_from_headers(request)
                if not company_id:
                    return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)

                success, partner_vals = self.validate_and_prepare_partner_data(data, company_id, CUSTOMER_SCHEMA, False)
                if not success:
                    return partner_vals
                
                partner = request.env['res.partner'].sudo().create(partner_vals)

                # Prepare response data
                response_data = self.prepare_partner_response(partner)
                return APIResponse.success_response(response_data, status=201)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
        
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
                company_id = get_company_from_headers(request)
                if not company_id:
                    return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)

                success, vendor_vals = self.validate_and_prepare_partner_data(data, company_id, VENDOR_SCHEMA, True)
                if not success:
                    return vendor_vals
                
                partner = request.env['res.partner'].sudo().create(vendor_vals)

                # Prepare response data
                response_data = self.prepare_partner_response(partner, True)
                return APIResponse.success_response(response_data, status=201)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
        
    @http.route('/api/customers/<int:customer_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['get_customer'])
    def get_customer(self, customer_id):
        try:
            domain = [('id', '=', int(customer_id))]
            category_id = get_default_customer_category(request)
            domain.append(('category_id', 'child_of', int(category_id)))
            customer = request.env['res.partner'].sudo().search(domain, limit=1)
            if not customer.exists():
                return APIResponse.error_response(message='Customer not found', errors='Invalid customer_id', status=404)
                
            # Prepare response data
            response_data = self.prepare_partner_response(customer)
            return APIResponse.success_response(response_data, status=200)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the customer', errors=str(e), status=500)
        
    @http.route('/api/vendors/<int:vendor_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['get_vendor'])
    def get_vendor(self, vendor_id, **kwargs):
        try:
            domain = [('id', '=', int(vendor_id))]
            category_id = get_default_vendor_category(request)
            domain.append(('category_id', 'child_of', int(category_id)))
            vendor = request.env['res.partner'].sudo().search(domain, limit=1)
            if not vendor.exists():
                return APIResponse.error_response(message='Vendor not found', errors='Invalid vendor_id', status=404)
            
            # Prepare response data
            response_data = self.prepare_partner_response(vendor, True)
            return APIResponse.success_response(response_data, status=200)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the vendor', errors=str(e), status=500)
        
        
    @http.route('/api/vendors/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['list_vendors'])
    def list_vendors(self, company_id=None, DisplayName=None, active=None, maxresults=100, startposition=0, **kwargs):
        try:
            success, response_data = self.get_partners(request, company_id, DisplayName, active, True, maxresults, startposition)
            if not success:
                return response_data
            return APIResponse.success_response(response_data, status=200)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the Vendor', errors=str(e), status=500)
        
    @http.route('/api/customers/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(partners_docs['list_customers'])
    def list_customers(self, company_id=None, DisplayName=None, active=None, maxresults=100, startposition=0, **kwargs):
        try:
            success, response_data = self.get_partners(request, company_id, DisplayName, active, False, maxresults, startposition)
            if not success:
                return response_data
            return APIResponse.success_response(response_data, status=200)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the Customers', errors=str(e), status=500)
        

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
        
        


