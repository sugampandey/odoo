from odoo import http
import uuid, datetime
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from ..common import APIResponse, get_company_from_headers, validate_and_convert_data, get_request_data
from ..utils import validate_company, validate_analytic_plan, validate_analytic_account

from ..swagger.common import swagger_doc
from ..swagger.analytic_account import analytic_accounts_docs
from ..schemas.analytic_account import ANALYTIC_ACCOUNT_SCHEMA, AnalyticClassModel, AnalyticClassListResponseModel, AnalyticClassResponseModel, AnalyticClassQueryResponseModel
from ..schemas.common import MetaDataModel
from ..logger.logger import logger
from ..constants import CONSTANTS

class AnalyticAccountAPI(http.Controller):

    def validate_and_prepare_analytic_account_data(self, data, company_id, analytic_account_expected_fields):
        success, converted_data = validate_and_convert_data(data, analytic_account_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Validate company 
        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            
        # Check if an analytic account with the same code already exists for the given company
        if request.env['account.analytic.account'].sudo().search([
            ('name', '=ilike', converted_data['Name'].lower()), ('company_id', '=', company_id)
            ], limit=1):
            return False, APIResponse.error_response(message='Another Class with this Name already exists', errors='Duplicate Name')
        
        # Create the analytic account
        analytic_account_vals = {
            'name': converted_data['Name'],
            'code': str(uuid.uuid4()).replace('-', '.'), # Format: UUID (e.g., 550e8400.e29b.41d4.a716.446655440000)
            'company_id': company_id,
        }
        return True, analytic_account_vals
    
    def analytic_account_object(self, analytic_account):
        meta_data = MetaDataModel(
            CreateTime = analytic_account.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            LastUpdatedTime = analytic_account.write_date.strftime('%Y-%m-%d %H:%M:%S'),
        )
        return AnalyticClassModel(
            Id=analytic_account.id,
            Name=analytic_account.name,
            MetaData=meta_data,
            Active=analytic_account.active
        )
    
    def create_analytic_account_response(self, analytic_account):
        return AnalyticClassResponseModel(
            Class=self.analytic_account_object(analytic_account),
            time=datetime.datetime.now().strftime(CONSTANTS['DATE_FORMAT'])
        ).to_dict()
    
    def list_analytic_account_response(self, accounts_data, startPosition, maxResults, totalCount):
        QueryResponse=AnalyticClassQueryResponseModel(
                startPosition=startPosition,
                Class=accounts_data,
                maxResults=maxResults,
                totalCount= totalCount
            )
        return AnalyticClassListResponseModel(
            QueryResponse=QueryResponse,
            time=datetime.datetime.now().strftime(CONSTANTS['DATE_FORMAT'])
        ).to_dict()
        
    @http.route('/api/analytic-class', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['create_analytic_account'])
    def create_analytic_account(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                company_id = get_company_from_headers(request)
                if not company_id:
                    return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)
                
                success, analytic_account_vals = self.validate_and_prepare_analytic_account_data(data, company_id, ANALYTIC_ACCOUNT_SCHEMA)
                if success is not True:
                    return analytic_account_vals
                
                analytic_account_plan = request.env['account.analytic.plan'].sudo().create({
                    'name':analytic_account_vals['name'],
                    'company_id': analytic_account_vals['company_id']
                })

                analytic_account_vals['plan_id'] = analytic_account_plan.id
                
                analytic_account = request.env['account.analytic.account'].sudo().create(analytic_account_vals)

                # Prepare response data
                response_data = self.create_analytic_account_response(analytic_account)
                return APIResponse.success_response(response_data, status=201)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the analytic account', errors=str(e), status=500)
        
    @http.route('/api/analytic-class', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['list_analytic_accounts'])
    def list_analytic_accounts(self, company_id=None, active=None, maxresults=100, startposition=0, **kwargs):
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
                
            startposition = int(startposition)
            maxresults = int(maxresults)

            # Get total count
            total_count = request.env['account.analytic.account'].sudo().search_count(domain)

            # Retrieve analytic accounts with pagination
            analytic_accounts = request.env['account.analytic.account'].sudo().search(
                domain, 
                limit=maxresults, 
                offset=startposition,
                order='id DESC'
            )
            if not analytic_accounts:
                return APIResponse.error_response(message='No analytic class found.', status=404)

            # Prepare response data
            accounts_data = []
            for account in analytic_accounts:
                accounts_data.append(self.analytic_account_object(account))
            response_data = self.list_analytic_account_response(accounts_data, startposition, len(analytic_accounts), total_count)

            return APIResponse.success_response(response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving analytic class', errors=str(e), status=500)
        

    @http.route('/api/analytic-class/<int:analytic_class_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(analytic_accounts_docs['get_analytic_account'])
    def get_analytic_account(self, analytic_class_id, company_id, **kwargs):
        """
        Retrieves an analytic account by ID within Odoo's accounting module.

        Args:
        - analytic_class_id (int): The ID of the analytic account to retrieve.

        Returns:
        dict: Dictionary containing a key 'account_info' with details of the retrieved analytic account.

        Raises:
        ValidationError: If the analytic account does not exist.
        """
        analytic_account_id = analytic_class_id
        try:
            domain = [('id', '=', int(analytic_account_id))]
            if company_id:
                is_valid, error_message = validate_company(request, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
                domain.append(('company_id', '=', int(company_id)))

            # Attempt to retrieve the analytic account using the provided ID
            analytic_account = request.env['account.analytic.account'].sudo().search(domain, limit=1)

            # Check if the analytic account actually exists
            if not analytic_account.exists():
                return APIResponse.error_response(message=f"Analytic class with ID {analytic_account_id} does not exist.", errors='Invalid Id', status=404)
            
            # Prepare response data
            response_data = self.create_analytic_account_response(analytic_account)
            return APIResponse.success_response(response_data)
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