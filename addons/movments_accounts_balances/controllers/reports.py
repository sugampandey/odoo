from odoo import http, fields
from odoo.http import request
from ..middleware.auth_middleware import validate_token_middleware
from ..utils import APIResponse, get_general_ledger_report_order
from ..swagger.swagger_generator import swagger_gen
from ..schemas.reports import ReportResponseModel
from ..schemas.helpers.general_ledger import prepare_general_ledger_response
from ..schemas.helpers.balance_sheet import prepare_account_balance_response
from ..schemas.helpers.profit_loss import prepare_profit_loss_response
from ..schemas.common import ACCESS_TOKEN_HEADER
from ..repositories.analytic_account import AnalyticAccountService
from ..repositories.partner import PartnerService
from ..repositories.account import AccountService
from ..repositories.company import CompanyService
from ..repositories.account_move import AccountMoveLineService
from ..logger.logger import logger



class ReportsAPI(http.Controller):
    
    @http.route('/api/v1/general_ledger', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='general-ledger',
        response_model=ReportResponseModel,
        tags=['Reports'],
        description='Get general ledger report with optional filters for date range, partner, account, and analytic class',
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_general_ledger(self, company_id, columns, start_date=None, end_date=None, partner_id=None, 
                           account_id=None, analytic_class_id=None, sort_by=None, sort_order=None, **kwargs):
        try:
            account_move_line_service = AccountMoveLineService(request.env)
            # Validate parameters
            is_valid, result = self.validate_report_request_params(company_id, start_date, end_date, partner_id, account_id, analytic_class_id)
            if not is_valid:
                return APIResponse.error_response(message=result)
            
            if result:  # If dates were provided and validated
                start_date, end_date = result
            
            # Build search domain
            domain = self.build_report_domain(
                company_id, start_date, end_date, partner_id, account_id)

            try:
                move_line_ids = self.get_analytic_move_line_ids(analytic_class_id)
                if move_line_ids is not None:
                    domain.append(('id', 'in', move_line_ids))
            except ValueError as e:
                return APIResponse.error_response(message=str(e))
            
            # Fetch and process move lines
            move_lines = account_move_line_service.search(
                domain,
                order=get_general_ledger_report_order(sort_by, sort_order)
            )
            
            columns_list = [col.strip() for col in columns.split(',')]

            response_data = prepare_general_ledger_response(
                request, start_date, end_date, move_lines, columns_list
            )

            return APIResponse.success_response(response_data.model_dump(mode='json'))
        except Exception as e:
            return APIResponse.error_response(message=f'Error retrieving general ledger: {str(e)}', status=500)


    @http.route('/api/v1/account_balance', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='account-balance',
        response_model=ReportResponseModel,
        tags=['Reports'],
        description='Get account balance report with optional filters for date range, partner, account, and analytic class',
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_account_balance(self, company_id, start_date=None, end_date=None, partner_id=None, 
                           account_id=None, analytic_class_id=None, summarize_column_by=None, **kwargs):
        try:
            # Validate parameters
            is_valid, result = self.validate_report_request_params(company_id, start_date, end_date, partner_id, account_id, analytic_class_id)
            if not is_valid:
                return APIResponse.error_response(message=result)
            
            if result:  # If dates were provided and validated
                start_date, end_date = result
            
            # Build search domain
            domain = self.build_report_domain(
                company_id, start_date, end_date, partner_id, account_id)
            
            logger.info(f"get_account_balance called Domain: {domain}")
            logger.info(f"get_account_balance called summarize_column_by: {summarize_column_by}")
            try:
                move_line_ids = self.get_analytic_move_line_ids(analytic_class_id)
                if move_line_ids is not None:
                    domain.append(('id', 'in', move_line_ids))
            except ValueError as e:
                return APIResponse.error_response(message=str(e))

            balance_sheet = prepare_account_balance_response(
                request, start_date, end_date, int(company_id), domain, None, summarize_column_by
            )

            return APIResponse.success_response(balance_sheet.model_dump(mode='json'))

        except Exception as e:
            return APIResponse.error_response(
                message='Error generating balance sheet',
                errors=str(e),
                status=500
            )

    @http.route('/api/v1/profit_loss', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='list',
        resource_name='profit-loss',
        response_model=ReportResponseModel,
        tags=['Reports'],
        description='Get profit and loss report with optional filters for date range, partner, account, and analytic class',
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_profit_loss(self, company_id, start_date=None, end_date=None, summarize_column_by=None, **kwargs):
        try:
            # Validate parameters
            is_valid, result = self.validate_report_request_params(company_id, start_date, end_date)
            if not is_valid:
                return APIResponse.error_response(message=result)
            
            if result:  # If dates were provided and validated
                start_date, end_date = result
            
            # Build search domain
            domain = self.build_report_domain(company_id, start_date, end_date)
            logger.info(f"get_profit_loss called Domain: {domain}")
            logger.info(f"get_profit_loss called summarize_column_by: {summarize_column_by}")

            profit_loss = prepare_profit_loss_response(
                request, start_date, end_date, int(company_id), domain, None, summarize_column_by
            )

            return APIResponse.success_response(profit_loss.model_dump(mode='json'))

        except Exception as e:
            return APIResponse.error_response(
                message='Error generating profit and loss statement',
                errors=str(e),
                status=500
            )

        
    def validate_report_request_params(self, company_id, start_date=None, end_date=None, 
                                        partner_id=None, account_id=None, analytic_class_id=None):
        company_service = CompanyService(request.env)
        analytic_account_service = AnalyticAccountService(request.env)
        partner_service = PartnerService(request.env)
        account_service = AccountService(request.env)
        
        if not company_id:
            return False, 'Company ID is required'
        
        is_valid, error_message = company_service.validate_company(company_id)
        if not is_valid:
            return False, error_message
        
        for param_id, validator in [
                (partner_id, partner_service.validate_partner),
                (account_id, account_service.validate_account),
                (analytic_class_id, analytic_account_service.validate_analytic_account)
            ]:
                if param_id:
                    is_valid, error_message = validator(int(param_id), company_id)
                    if not is_valid:
                        return False, error_message

        if start_date and end_date:
            try:
                start_date = fields.Date.from_string(start_date)
                end_date = fields.Date.from_string(end_date)
                return True, (start_date, end_date)
            except ValueError as e:
                return False, str(e)
        elif not start_date and not end_date:
            # Set year-to-date if no dates provided
            from datetime import date
            today = date.today()
            ytd_start = date(today.year, 1, 1)
            return True, (ytd_start, today)
        
        return True, None
    
    def build_report_domain(self, company_id, start_date=None, end_date=None, partner_id=None, 
                       account_id=None):
        domain = [('company_id', '=', int(company_id))]
        
        if start_date:
            domain.append(('date', '>=', start_date))
        if end_date:
            domain.append(('date', '<=', end_date))
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
        if account_id:
            domain.append(('account_id', '=', int(account_id)))
        
        return domain
    
    def get_analytic_move_line_ids(self, analytic_class_id):
        if not analytic_class_id:
            return None
            
        analytic_account_id = int(analytic_class_id)
        analytic_lines = request.env['account.analytic.line'].sudo().search([
            ('account_id', '=', analytic_account_id)
        ])
        return analytic_lines.mapped('move_line_id').ids if analytic_lines else []

