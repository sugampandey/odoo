from odoo import http, fields
from odoo.http import request
from .common import APIResponse
from .utils import validate_analytic_account, validate_journal, validate_partner, validate_account, validate_company

from ..swagger.common import swagger_doc
from ..swagger.reports import reports_docs

class ReportsAPI(http.Controller):

    def generate_move_line_response(self, line):
        return {
            'date': line.date.strftime('%Y-%m-%d'),
            'move': {
                'id': line.move_id.id,
                'name': line.move_id.name,
                'ref': line.move_id.ref,
                'state': line.move_id.state
            },
            'journal': {
                'id': line.journal_id.id,
                'name': line.journal_id.name,
                'type': line.journal_id.type
            },
            'account': {
                'id': line.account_id.id,
                'code': line.account_id.code,
                'name': line.account_id.name,
                'type': line.account_id.account_type
            },
            'partner': {
                'id': line.partner_id.id,
                'name': line.partner_id.name
            } if line.partner_id else None,
            'ref': line.ref or '',
            'name': line.name or '',
            'debit': line.debit,
            'credit': line.credit,
            'balance': line.balance,
            'analytic_distribution': line.analytic_distribution,
            'amount_currency': line.amount_currency,
            'reconciled': line.reconciled,
            'full_reconcile_id': line.full_reconcile_id.id if line.full_reconcile_id else None,
            'matching_number': line.matching_number or '',
        }
    
    def get_move_line_data(self, domain):
        # Get move lines
        move_lines = request.env['account.move.line'].sudo().search(
            domain,
            order='date desc, move_id desc, id desc'
        )
        # Prepare the general ledger data
        ledger_entries = []
        running_balance = 0
        for line in move_lines:
            running_balance += line.balance
            entry = self.generate_move_line_response(line)
            entry['running_balance'] = running_balance
            ledger_entries.append(entry)

        # Prepare summary
        summary = {
            'total_debit': sum(line['debit'] for line in ledger_entries),
            'total_credit': sum(line['credit'] for line in ledger_entries),
            'net_balance': sum(line['balance'] for line in ledger_entries),
            'entry_count': len(ledger_entries),
        }
        return {
            'summary': summary,
            'ledger_entries': ledger_entries,
        }

    @http.route('/api/general_ledger', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(reports_docs['general_ledger'])
    def get_general_ledger(self, company_id, end_date=None, partner_id=None, 
                           account_id=None, analytic_class_id=None, 
                           include_unposted=False, **kwargs):
        try:
            # Validate company
            if not company_id:
                return APIResponse.error_response(message='Company ID is required')
            company = request.env['res.company'].sudo().browse(int(company_id))
            if not company.exists():
                return APIResponse.error_response(message=f'Invalid company_id: {company_id}')

            # Build domain
            domain = [('company_id', '=', int(company_id))]

            if end_date:
                try:
                    end_date = fields.Date.from_string(end_date)
                    domain.extend([('date', '<=', end_date)])
                except ValueError:
                    return APIResponse.error_response(message='Invalid date format. Use YYYY-MM-DD')

            # Partner validation and domain
            if partner_id:
                partner_id = int(partner_id)
                is_valid, error_message = validate_partner(request, partner_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid partner: {error_message}')
                domain.append(('partner_id', '=', partner_id))

            # Account validation and domain
            if account_id:
                account_id = int(account_id)
                is_valid, error_message = validate_account(request, account_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid account: {error_message}')
                domain.append(('account_id', '=', account_id))

            # Analytic account validation and domain
            if analytic_class_id:
                analytic_account_id = int(analytic_class_id)
                is_valid, error_message = validate_analytic_account(request, analytic_account_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid analytic class: {error_message}')
                # First get move_line_ids from analytic lines
                analytic_lines = request.env['account.analytic.line'].sudo().search([('account_id', '=', analytic_account_id)])
                if analytic_lines:
                    move_line_ids = analytic_lines.mapped('move_line_id').ids
                    if move_line_ids:
                        domain.append(('id', 'in', move_line_ids))

            # Posted entries filter
            if not include_unposted:
                domain.append(('move_id.state', '=', 'posted'))

            response_data = self.get_move_line_data(domain)

            return APIResponse.success_response(message='General ledger retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message=f'Error retrieving general ledger: {str(e)}', status=500)
        
    
    @http.route('/api/account_balance', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(reports_docs['account_balance'])
    def get_account_balance(self, company_id, end_date=None, account_id=None, **kwargs):
        try:
            # Validate company
            if not company_id:
                return APIResponse.error_response(message='Company ID is required')
            company = request.env['res.company'].sudo().browse(int(company_id))
            if not company.exists():
                return APIResponse.error_response(message=f'Invalid company_id: {company_id}')

            # Build domain
            domain = [('company_id', '=', int(company_id))]

            if end_date:
                try:
                    end_date = fields.Date.from_string(end_date)
                    domain.extend([('date', '<=', end_date)])
                except ValueError:
                    return APIResponse.error_response(message='Invalid date format. Use YYYY-MM-DD')

            # Account validation and domain
            if account_id:
                account_id = int(account_id)
                is_valid, error_message = validate_account(request, account_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid account: {error_message}')
                domain.append(('account_id', '=', account_id))
            
            response_data = self.get_move_line_data(domain)
            
            return APIResponse.success_response(message='Account balance retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message=f'Error retrieving account balance: {str(e)}', status=500)

    # @http.route('/api/get_general_ledger', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # def get_general_ledger(self, company_id, date_from=None, date_to=None, account_ids=None, partner_id=None, **kwargs):
    #     try:
    #         domain = [('move_id.state', '=', 'posted')]
    #         # Validate company
    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #         domain.append(('company_id', '=', int(company_id)))

    #         if (date_from and not date_to) or (date_to and not date_from):
    #             return APIResponse.error_response(message='Both date_from and date_to must be provided')
    #         elif date_from and date_to:
    #             domain.append(('date', '>=', date_from))
    #             domain.append(('date', '<=', date_to))
    #         if account_ids:
    #             account_ids = eval(account_ids)
    #             if type(account_ids) != list:
    #                 return APIResponse.error_response(message='account_ids must be a list')
    #             for account_id in account_ids:
    #                 is_valid, error_message = validate_account(request, account_id, company_id)
    #                 if not is_valid:
    #                     return APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
    #             domain.append(('account_id', 'in', account_ids))
    #         if partner_id:
    #             is_valid, error_message = validate_partner(request, partner_id, company_id)
    #             if not is_valid:
    #                 return APIResponse.error_response(message=f'Invalid partner: {error_message}', errors=f'Invalid partner_id: {partner_id}')
    #             domain.append(('partner_id', '=', int(partner_id)))

    #         move_lines = request.env['account.move.line'].sudo().search(
    #             domain, order='date, move_id, id'
    #         )

    #         ledger_data = []
    #         running_balance = 0.0
    #         for line in move_lines:
    #             running_balance += line.debit - line.credit
    #             ledger_data.append({
    #                 'date': line.date.isoformat() if line.date else None,
    #                 'move_id': line.move_id.name,
    #                 'journal': line.journal_id.name,
    #                 # 'account_code': line.account_id.code,
    #                 'account_name': line.account_id.name,
    #                 'partner': line.partner_id.name,
    #                 'label': line.name,
    #                 'debit': round(line.debit, 2),
    #                 'credit': round(line.credit, 2),
    #                 'running_balance': round(running_balance, 2),
    #                 'ref': line.ref,
    #                 'tax': line.tax_line_id.name,
    #                 'analytic_account': line.analytic_distribution,
    #             })
    #         return APIResponse.success_response(message='General Ledger retrieved successfully', data=ledger_data)
    #     except Exception as e:
    #         return APIResponse.error_response(message='Error retrieving General Ledger', errors=str(e), status=500)
    
    # @http.route('/api/get_journal_entries', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(reports_docs['journal_entries'])
    # def get_journal_entries(self, company_id, journal_ids=None, date_from=None, date_to=None, limit=20, offset=0, **kwargs):
    #     try:
    #         domain = [('state', '=', 'posted')]
    #         # Validate company
    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #         domain.append(('company_id', '=', int(company_id)))
    #         if (date_from and not date_to) or (date_to and not date_from):
    #             return APIResponse.error_response(message='Both date_from and date_to must be provided')
    #         elif date_from and date_to:
    #             domain.append(('date', '>=', date_from))
    #             domain.append(('date', '<=', date_to))
    #         if journal_ids:
    #             journal_list =  eval(journal_ids)
    #             if type(journal_list) != list:
    #                 return APIResponse.error_response(message='journal_ids must be a list')
    #             for journal_id in journal_list:
    #                 is_valid, error_message = validate_journal(request, journal_id, company_id)
    #                 if not is_valid:
    #                     return APIResponse.error_response(f'Invalid journal: {error_message}', f'Invalid journal_id: {journal_id}')
    #             domain.append(('journal_id', 'in', journal_list))

    #         limit = int(limit)
    #         offset = int(offset)
    #         # Get total count for pagination
    #         total_count = request.env['account.move'].sudo().search_count(domain)

    #         # Get journal entries with pagination
    #         moves = request.env['account.move'].sudo().search(
    #             domain,
    #             limit=limit,
    #             offset=offset,
    #             order='date desc, name desc'
    #         )
    #         entries_data = []

    #         for move in moves:
    #             move_data = {
    #                 'date': move.date.isoformat() if move.date else None,
    #                 'journal': {
    #                     'id': move.journal_id.id,
    #                     'name': move.journal_id.name,
    #                     'type': move.journal_id.type
    #                 },
    #                 'move_number': move.name,
    #                 'ref': move.ref,
    #                 'lines': []
    #             }

    #             for line in move.line_ids:
    #                 move_data['lines'].append({
    #                     'account': {
    #                         'id': line.account_id.id,
    #                         'code': line.account_id.code,
    #                         'name': line.account_id.name
    #                     },
    #                     'partner': {
    #                         'id': line.partner_id.id,
    #                         'name': line.partner_id.name
    #                     } if line.partner_id else None,
    #                     'label': line.name,
    #                     'debit': line.debit,
    #                     'credit': line.credit,
    #                 })
    #             entries_data.append(move_data)
    #         response_data = {
    #             'journal_entries': entries_data,
    #             'pagination': {
    #                 'total_count': total_count,
    #                 'limit': limit,
    #                 'offset': offset
    #             }
    #         }
    #         return APIResponse.success_response(message='Journal Entries retrieved successfully', data=response_data)
    #     except Exception as e:
    #         return APIResponse.error_response(message='Error retrieving Journal Entries', errors=str(e), status=500)
        

    # @http.route('/api/analytic_balances', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(reports_docs['analytic_balance'])
    # def get_analytic_balances(self, company_id, date_from=None, date_to=None, account_ids=None, limit=20, offset=0, **kwargs):
    #     try:
    #         # Validate company
    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
    #         domain = [('company_id', '=', int(company_id))]

    #         if (date_from and not date_to) or (date_to and not date_from):
    #             return APIResponse.error_response(message='Both date_from and date_to must be provided')
    #         elif date_from and date_to:
    #             domain.append(('date', '>=', date_from))
    #             domain.append(('date', '<=', date_to))
    #         if account_ids:
    #             account_ids = eval(account_ids)
    #             if type(account_ids) != list:
    #                 return APIResponse.error_response(message='account_ids must be a list')
    #             for account_id in account_ids:
    #                 is_valid, error_message = validate_account(request, account_id, company_id)
    #                 if not is_valid:
    #                     return APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
    #             domain.append(('account_id', 'in', account_ids))

    #         limit = int(limit)
    #         offset = int(offset)
    #         # Get total count for pagination
    #         total_count = request.env['account.analytic.line'].sudo().search_count(domain)

    #         # Get analytic lines
    #         analytic_lines = request.env['account.analytic.line'].sudo().search(
    #             domain,
    #             limit=limit,
    #             offset=offset,
    #             order='date desc, id desc'
    #         )
            
    #         balances = {}
    #         for line in analytic_lines:
    #             key = line.account_id.id
    #             if key not in balances:
    #                 balances[key] = {
    #                     'account_name': line.account_id.name,
    #                     'code': line.account_id.code,
    #                     'balance': 0.0,
    #                     'debit': 0.0,
    #                     'credit': 0.0,
    #                     'details': []
    #                 }
                
    #             amount = line.amount
    #             balances[key]['balance'] += amount
    #             if amount > 0:
    #                 balances[key]['debit'] += amount
    #             else:
    #                 balances[key]['credit'] += abs(amount)
                    
    #             balances[key]['details'].append({
    #                 'date': line.date.isoformat(),
    #                 'name': line.name,
    #                 'amount': amount,
    #                 'reference': line.ref,
    #                 'partner': {
    #                     'id': line.partner_id.id,
    #                     'name': line.partner_id.name
    #                 } if line.partner_id else None,
    #                 'type': line.move_line_id.move_id.name,
    #                 'product': {
    #                     'id': line.product_id.id,
    #                     'name': line.product_id.name
    #                 } if line.product_id else None
    #             })
    #         response_data = {
    #             'analytic_balances': balances,
    #             'pagination': {
    #                 'total_count': total_count,
    #                 'limit': limit,
    #                 'offset': offset
    #             }
    #         }
    #         return APIResponse.success_response(message='Analytic Balances retrieved successfully', data=response_data)
    #     except Exception as e:
    #         return APIResponse.error_response(message='Error retrieving Analytic Balances', errors=str(e), status=500)
    

    # @http.route('/api/balance_enquiry', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # def get_balance_enquiry(self, **kwargs):
    #     """Get balance enquiry for vendors and customers"""
    #     try:
    #         # Get parameters from request
    #         partner_id = kwargs.get('partner_id')
    #         partner_type = kwargs.get('partner_type')  # 'customer' or 'vendor'
    #         date_from = kwargs.get('date_from')
    #         date_to = kwargs.get('date_to')
    #         include_reconciled = kwargs.get('include_reconciled', 'false').lower() == 'true'

    #         domain = []
            
    #         # Validate and convert partner_id
    #         if partner_id:
    #             try:
    #                 partner_id = int(partner_id)
    #                 partner = request.env['res.partner'].sudo().browse(partner_id)
    #                 if not partner.exists():
    #                     return APIResponse.error_response(
    #                         message='Partner not found',
    #                         errors=f'No partner found with ID {partner_id}',
    #                         status=404
    #                     )
    #                 domain.append(('partner_id', '=', partner_id))
    #             except ValueError:
    #                 return APIResponse.error_response(
    #                     message='Invalid partner_id',
    #                     errors='partner_id must be an integer',
    #                     status=400
    #                 )

    #         # Add partner type filter
    #         if partner_type:
    #             if partner_type not in ['customer', 'vendor']:
    #                 return APIResponse.error_response(
    #                     message='Invalid partner_type',
    #                     errors="partner_type must be either 'customer' or 'vendor'",
    #                     status=400
    #                 )
                
    #             if partner_type == 'customer':
    #                 domain.append(('account_id.account_type', '=', 'asset_receivable'))
    #             else:  # vendor
    #                 domain.append(('account_id.account_type', '=', 'liability_payable'))

    #         # Add date filters
    #         if date_from:
    #             try:
    #                 date_from = fields.Date.from_string(date_from)
    #                 domain.append(('date', '>=', date_from))
    #             except ValueError:
    #                 return APIResponse.error_response(
    #                     message='Invalid date_from',
    #                     errors='date_from must be in YYYY-MM-DD format',
    #                     status=400
    #                 )

    #         if date_to:
    #             try:
    #                 date_to = fields.Date.from_string(date_to)
    #                 domain.append(('date', '<=', date_to))
    #             except ValueError:
    #                 return APIResponse.error_response(
    #                     message='Invalid date_to',
    #                     errors='date_to must be in YYYY-MM-DD format',
    #                     status=400
    #                 )

    #         # Add reconciliation filter
    #         if not include_reconciled:
    #             domain.append(('reconciled', '=', False))

    #         # Get move lines
    #         move_lines = request.env['account.move.line'].sudo().search(domain)

    #         # Group by partner
    #         partner_balances = {}
    #         for line in move_lines:
    #             if not line.partner_id:
    #                 continue

    #             partner_key = line.partner_id.id
    #             if partner_key not in partner_balances:
    #                 partner_balances[partner_key] = {
    #                     'partner': {
    #                         'id': line.partner_id.id,
    #                         'name': line.partner_id.name,
    #                         'ref': line.partner_id.ref,
    #                         'type': 'customer' if line.account_id.account_type == 'asset_receivable' else 'vendor',
    #                     },
    #                     'total_debit': 0.0,
    #                     'total_credit': 0.0,
    #                     'balance': 0.0,
    #                     'currency_id': line.company_currency_id.id,
    #                     'currency_name': line.company_currency_id.name,
    #                     'transactions': []
    #                 }

    #             partner_balances[partner_key]['total_debit'] += line.debit
    #             partner_balances[partner_key]['total_credit'] += line.credit
    #             partner_balances[partner_key]['balance'] = partner_balances[partner_key]['total_debit'] - partner_balances[partner_key]['total_credit']

    #             # Add transaction details
    #             partner_balances[partner_key]['transactions'].append({
    #                 'move_id': line.move_id.id,
    #                 'move_name': line.move_id.name,
    #                 'date': line.date.strftime('%Y-%m-%d'),
    #                 'journal_id': line.journal_id.id,
    #                 'journal_name': line.journal_id.name,
    #                 'account_id': line.account_id.id,
    #                 'account_code': line.account_id.code,
    #                 'account_name': line.account_id.name,
    #                 'debit': line.debit,
    #                 'credit': line.credit,
    #                 'amount_currency': line.amount_currency,
    #                 'currency_id': line.currency_id.id,
    #                 'currency_name': line.currency_id.name,
    #                 'ref': line.ref or '',
    #                 'name': line.name or '',
    #                 'reconciled': line.reconciled,
    #                 'matched_debit_ids': [r.id for r in line.matched_debit_ids],
    #                 'matched_credit_ids': [r.id for r in line.matched_credit_ids],
    #             })

    #         # Convert to list and sort by partner name
    #         result = list(partner_balances.values())
    #         result.sort(key=lambda x: x['partner']['name'])

    #         # Add summary
    #         summary = {
    #             'total_receivables': sum(p['balance'] for p in result if p['partner']['type'] == 'customer'),
    #             'total_payables': sum(p['balance'] for p in result if p['partner']['type'] == 'vendor'),
    #             'count_customers': len([p for p in result if p['partner']['type'] == 'customer']),
    #             'count_vendors': len([p for p in result if p['partner']['type'] == 'vendor']),
    #         }

    #         response_data = {
    #             'summary': summary,
    #             'balances': result,
    #             'filters': {
    #                 'partner_id': partner_id,
    #                 'partner_type': partner_type,
    #                 'date_from': date_from.strftime('%Y-%m-%d') if date_from else None,
    #                 'date_to': date_to.strftime('%Y-%m-%d') if date_to else None,
    #                 'include_reconciled': include_reconciled,
    #             }
    #         }

    #         return APIResponse.success_response(
    #             message='Balance enquiry retrieved successfully',
    #             data=response_data
    #         )

    #     except Exception as e:
    #         # _logger.error(f"Failed to get balance enquiry: {str(e)}")
    #         return APIResponse.error_response(
    #             message='Failed to get balance enquiry',
    #             errors=str(e),
    #             status=500
    #         )
        

    # @http.route('/api/partner_balance/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(reports_docs['partner_balance'])
    # def get_partner_balance(self,  company_id, partner_id, date_from=None, date_to=None, **kwargs):
    #     try:
    #         # Validate company
    #         is_valid, error_message = validate_company(request, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')

    #         # Validate partner
    #         partner_id = int(partner_id)
    #         is_valid, error_message = validate_partner(request, partner_id, company_id)
    #         if not is_valid:
    #             return APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')
    #         partner = request.env['res.partner'].sudo().browse(partner_id)

    #         # Validate date filters
    #         if (date_from and not date_to) or (date_to and not date_from):
    #             return APIResponse.error_response(message='Both date_from and date_to must be provided')

    #         # Base domain for both receivable and payable
    #         domain = [
    #             ('partner_id', '=', partner_id),
    #             ('move_id.state', '=', 'posted')
    #             ]
    #         # Add date filters if provided
    #         if date_from and date_to:
    #             try:
    #                 date_from = fields.Date.from_string(date_from)
    #                 date_to = fields.Date.from_string(date_to)
    #                 domain.extend([
    #                     ('date', '>=', date_from),
    #                     ('date', '<=', date_to)
    #                 ])
    #             except ValueError:
    #                 return APIResponse.error_response(message='Invalid date format', errors='Dates must be in YYYY-MM-DD format')

    #         # Get receivable and payable accounts with domain
    #         receivable_domain = domain + [('account_id.account_type', '=', 'asset_receivable')]
    #         payable_domain = domain + [('account_id.account_type', '=', 'liability_payable')]

    #         receivable_lines = request.env['account.move.line'].sudo().search(receivable_domain)
    #         payable_lines = request.env['account.move.line'].sudo().search(payable_domain)

    #         # Calculate balances
    #         receivable_balance = sum(receivable_lines.mapped('balance'))  # Debit - Credit
    #         payable_balance = sum(payable_lines.mapped('balance'))      # Debit - Credit

    #         # Group transactions by type
    #         receivable_transactions = []
    #         for line in receivable_lines:
    #             receivable_transactions.append({
    #                 'move_id': line.move_id.id,
    #                 'move_name': line.move_id.name,
    #                 'date': line.date.strftime('%Y-%m-%d'),
    #                 'journal': {
    #                     'id': line.journal_id.id,
    #                     'name': line.journal_id.name,
    #                     'type': line.journal_id.type,
    #                 },
    #                 'debit': line.debit,
    #                 'credit': line.credit,
    #                 'balance': line.balance,  # Positive means customer owes us
    #                 'reconciled': line.reconciled,
    #                 'amount_currency': line.amount_currency,
    #                 'ref': line.ref or '',
    #                 'move_type': line.move_id.move_type,  # To identify invoices, payments, etc.
    #             })

    #         payable_transactions = []
    #         for line in payable_lines:
    #             payable_transactions.append({
    #                 'move_id': line.move_id.id,
    #                 'move_name': line.move_id.name,
    #                 'date': line.date.strftime('%Y-%m-%d'),
    #                 'journal': {
    #                     'id': line.journal_id.id,
    #                     'name': line.journal_id.name,
    #                     'type': line.journal_id.type,
    #                 },
    #                 'debit': line.debit,
    #                 'credit': line.credit,
    #                 'balance': line.balance,  # Negative means we owe vendor
    #                 'reconciled': line.reconciled,
    #                 'amount_currency': line.amount_currency,
    #                 'ref': line.ref or '',
    #                 'move_type': line.move_id.move_type,
    #             })

    #         response_data = {
    #             'partner': {
    #                 'id': partner.id,
    #                 'name': partner.name,
    #                 'ref': partner.ref,
    #                 'customer_rank': partner.customer_rank,
    #                 'supplier_rank': partner.supplier_rank,
    #             },
    #             'balances': {
    #                 'receivable': {
    #                     'balance': receivable_balance,
    #                     'total_debit': sum(receivable_lines.mapped('debit')),
    #                     'total_credit': sum(receivable_lines.mapped('credit')),
    #                     'transaction_count': len(receivable_lines),
    #                 },
    #                 'payable': {
    #                     'balance': payable_balance,
    #                     'total_debit': sum(payable_lines.mapped('debit')),
    #                     'total_credit': sum(payable_lines.mapped('credit')),
    #                     'transaction_count': len(payable_lines),
    #                 },
    #                 'net_position': receivable_balance - payable_balance
    #             },
    #             'transactions': {
    #                 'receivable': receivable_transactions,
    #                 'payable': payable_transactions
    #             },
    #             'summary': {
    #                 'total_invoiced': sum(line.balance for line in receivable_lines.filtered(
    #                     lambda l: l.move_id.move_type == 'out_invoice'
    #                 )),
    #                 'total_bills': sum(line.balance for line in payable_lines.filtered(
    #                     lambda l: l.move_id.move_type == 'in_invoice'
    #                 )),
    #                 'total_payments_received': sum(line.balance for line in receivable_lines.filtered(
    #                     lambda l: l.payment_id
    #                 )),
    #                 'total_payments_made': sum(line.balance for line in payable_lines.filtered(
    #                     lambda l: l.payment_id
    #                 )),
    #             }
    #         }

    #         return APIResponse.success_response(
    #             message='Partner balance retrieved successfully',
    #             data=response_data
    #         )

    #     except Exception as e:
    #         # _logger.error(f"Failed to get partner balance: {str(e)}")
    #         return APIResponse.error_response(
    #             message='Failed to get partner balance',
    #             errors=str(e),
    #             status=500
    #         )




