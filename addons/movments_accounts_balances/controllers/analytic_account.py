from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from .common import APIResponse, validate_and_convert_data, get_request_data
from .validation_schema import analytic_account_expected_fields
from . utils import validate_company, validate_analytic_plan, validate_analytic_account

from ..swagger.common import swagger_doc
from ..swagger.analytic_account import analytic_accounts_docs
from .schemas.analytic_account import ANALYTIC_ACCOUNT_SCHEMA

from .logger import logger

class AnalyticAccountAPI(http.Controller):

    def validate_and_prepare_analytic_account_data(self, data, analytic_account_expected_fields):
        success, converted_data = validate_and_convert_data(data, analytic_account_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
        
        # Validate plan if provided
        plan_id = converted_data['plan_id']
        is_valid, error_message = validate_analytic_plan(request, plan_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid plan: {error_message}', f'Invalid plan_id: {plan_id}')
            
        # Check if an analytic account with the same code already exists for the given company
        if request.env['account.analytic.account'].sudo().search(
            [('code', '=', converted_data['code']), ('company_id', '=', company_id)], limit=1
            ):
            return False, APIResponse.error_response('An analytic account with this code already exists', 'Duplicate code')
            
        # Create the analytic account
        analytic_account_vals = {
            'name': converted_data['name'],
            'code': converted_data['code'],
            'company_id': company_id,
            'plan_id': plan_id,
        }
        return True, analytic_account_vals
        
    @http.route('/api/analytic-class', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['create_analytic_account'])
    def create_analytic_account(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                
                success, analytic_account_vals = self.validate_and_prepare_analytic_account_data(data, ANALYTIC_ACCOUNT_SCHEMA)
                if success is not True:
                    return analytic_account_vals
                
                analytic_account = request.env['account.analytic.account'].sudo().create(analytic_account_vals)

                # Prepare response data
                response_data = {
                    'id': analytic_account.id,
                    'name': analytic_account.name,
                    'code': analytic_account.code,
                    'company': {
                        'id': analytic_account.company_id.id,
                        'name': analytic_account.company_id.name
                    } if analytic_account.company_id else None,
                    'create_date': analytic_account.create_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                return APIResponse.success_response(message='Analytic account created successfully', data=response_data) 
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the analytic account', errors=str(e), status=500)
        
    @http.route('/api/analytic-class', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['list_analytic_accounts'])
    def list_analytic_accounts(self, company_id=None, active=None, limit=20, offset=0, **kwargs):
        """
        Retrieves analytic accounts from Odoo's accounting module.

        Returns:
        list: List of dictionaries, each containing details of an analytic account.

        Raises:
        ValidationError: If no analytic accounts are found.
        """
        try:
            domain = []
            if company_id:
                # Validate company
                is_valid, error_message = validate_company(request, int(company_id))
                if not is_valid:
                    return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
                domain.append(('company_id', '=', int(company_id)))
            if active is not None:
                active = active.lower() == 'true'
                domain.append(('active', '=', active))
                
            limit = int(limit)
            offset = int(offset)

            # Get total count
            total_count = request.env['account.analytic.account'].sudo().search_count(domain)

            # Retrieve analytic accounts with pagination
            analytic_accounts = request.env['account.analytic.account'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset
            )
            if not analytic_accounts:
                return APIResponse.error_response(message='No analytic class found.', status=404)

            # Prepare response data
            accounts_data = []
            for account in analytic_accounts:
                account_info = {
                    'id': account.id,
                    'name': account.name,
                    'code': account.code,
                    'active': account.active,
                    'company': {
                        'id': account.company_id.id,
                        'name': account.company_id.name
                    } if account.company_id else None,
                    'plan': {
                        'id': account.plan_id.id,
                        'name': account.plan_id.name
                    } if account.plan_id else None,
                    'partner': {
                        'id': account.partner_id.id,
                        'name': account.partner_id.name
                    } if account.partner_id else None,
                    'create_date': account.create_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                accounts_data.append(account_info)
            response_data = {
                'analytic_class': accounts_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }

            return APIResponse.success_response(message='Analytic class retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving analytic class', errors=str(e), status=500)
        

    @http.route('/api/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['get_analytic_account'])
    def get_analytic_account(self, analytic_class_id, **kwargs):
        """
        Retrieves an analytic account by ID within Odoo's accounting module.

        Args:
        - account_id (int): The ID of the analytic account to retrieve.

        Returns:
        dict: Dictionary containing a key 'account_info' with details of the retrieved analytic account.

        Raises:
        ValidationError: If the analytic account does not exist.
        """
        analytic_account_id = analytic_class_id
        try:
            # Attempt to retrieve the analytic account using the provided ID
            account = request.env['account.analytic.account'].sudo().browse(analytic_account_id)

            # Check if the analytic account actually exists
            if not account.exists():
                raise ValidationError(f"Analytic class with ID {analytic_account_id} does not exist.")
            
            # Prepare response data
            response_data = {
                'id': account.id,
                'name': account.name,
                'code': account.code,
                'active': account.active,
                'company': {
                    'id': account.company_id.id,
                    'name': account.company_id.name
                } if account.company_id else None,
                'plan': {
                    'id': account.plan_id.id,
                    'name': account.plan_id.name
                } if account.plan_id else None,
                'partner': {
                    'id': account.partner_id.id,
                    'name': account.partner_id.name
                } if account.partner_id else None,
                'create_date': account.create_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            return APIResponse.success_response(message='Analytic class retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving analytic class', errors=str(e), status=500)
    
    @http.route('/api/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['delete_analytic_account'])
    def delete_analytic_account(self, analytic_class_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                analytic_account_id = analytic_class_id
                company_id = int(kwargs.get('company_id')) if kwargs.get('company_id') else kwargs.get('company_id')
                if not company_id:
                    return APIResponse.error_response(message='Company ID not provided', errors='company_id is required')
                
                # Validate company
                is_valid, error_message = validate_company(request, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')

                # Attempt to retrieve the analytic account using the provided ID
                account = request.env['account.analytic.account'].sudo().browse(analytic_account_id)

                # Check if the analytic account actually exists
                if not account.exists():
                    raise ValidationError(f"Analytic class with ID {analytic_account_id} does not exist.")
                
                if account.company_id.id != company_id:
                    return APIResponse.error_response(message='Analytic class does not belong to the specified company', errors=f'Analytic account {analytic_account_id} does not belong to company {company_id}')

                # Delete the analytic account
                account.write({'active': False})

                return APIResponse.success_response(message='Analytic class deactivated successfully')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deactivating the analytic class', errors=str(e), status=500)