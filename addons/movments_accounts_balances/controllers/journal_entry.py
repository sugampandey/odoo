from datetime import datetime
from odoo import http
from odoo.http import request
import json
from .common import APIResponse, validate_and_convert_data, get_request_data
from .validation_schema import journal_entry_expected_fields
from .utils import validate_company, validate_journal, validate_partner, validate_account, validate_tax

from ..swagger.common import swagger_doc
from ..swagger.journal_entry import journal_entries_docs
from .schemas.journal_entry import JOURNAL_ENTRY_SCHEMA

class JournalEntryController(http.Controller):

    def validate_and_prepare_journal_entry_data(self, data, invoice_expected_fields):
        success, converted_data = validate_and_convert_data(data, invoice_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')

        # validate partner
        partner_id = converted_data.get('partner_id')
        if partner_id:
            is_valid, error_message = validate_partner(request, partner_id, company_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')

        # Validate and prepare journal items
        if not converted_data['line_ids']:
            return APIResponse.error_response(message='No journal items provided', errors='At least one journal item is required')
        
        move_lines = []
        total_debit = 0
        total_credit = 0
        
        for line in converted_data['line_ids']:
            # Validate account
            account_id = int(line.get('account_id')) if line.get('account_id') else False
            is_valid, error_message = validate_account(request, account_id, company_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
            
            partner_id = int(line.get('partner_id')) if line.get('partner_id') else False
            if partner_id:
                is_valid, error_message = validate_partner(request, partner_id, company_id)
                if not is_valid:
                    return False, APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')

            move_line = {
                'account_id': account_id,
                'ref': line.get('ref'),
                'debit': float(line.get('amount', 0.0)) if line.get('amount_type') == 'debit' else 0,
                'credit': float(line.get('amount', 0.0)) if line.get('amount_type') == 'credit' else 0,
                'partner_id': partner_id,
                'analytic_distribution': {k: int(v) if isinstance(v, str) and v.strip().isdigit() else v 
                for k, v in eval(line.get('analytic_distribution')).items()} if line.get('analytic_distribution') else None,
            }

            total_debit += move_line['debit']
            total_credit += move_line['credit']
            move_lines.append((0, 0, move_line))
            
        # Validate balanced entry
        if not (total_debit - total_credit) == 0:
            return False, APIResponse.error_response(message='Journal entry is not balanced', errors=f'Difference between debit ({total_debit}) and credit ({total_credit})')
        
        # Create the journal entry
        move_vals = {
            'move_type': 'entry',
            'partner_id': partner_id,
            'date': converted_data['date'],
            'ref': converted_data['ref'],
            'company_id': company_id,
            'line_ids': move_lines,
        }
        return True, move_vals
    
    @http.route('/api/journal-entries', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['create_journal_entry'])
    def create_journal_entry(self, *args, **post):
        """
        Creates a new journal entry in Odoo.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)

                success, move_vals = self.validate_and_prepare_journal_entry_data(data, JOURNAL_ENTRY_SCHEMA)
                if success is not True:
                    return move_vals
                    
                move = request.env['account.move'].sudo().create(move_vals)

                move.with_context(send_webhook=True).action_post()
                    
                # Prepare response data
                response_data = {
                    'id': move.id,
                    'name': move.name,
                    'ref': move.ref,
                    'date': move.date.strftime('%Y-%m-%d'),
                    'journal_id': {
                        'id': move.journal_id.id,
                        'name': move.journal_id.name
                    },
                }
                return APIResponse.success_response(message="Journal entry created successfully", data=response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to create journal entry', errors=str(e), status=500)
        
    @http.route('/api/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['get_journal_entry'])
    def get_journal_entry(self, journal_entry_id, **kwargs):
        """
        Retrieves a specific journal entry by its ID.
        
        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing the journal entry details or an error message.
        """
        try:
            move = request.env['account.move'].sudo().browse(journal_entry_id)
            if not move.exists():
                return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

            response_data = {
                'id': move.id,
                'name': move.name,
                'ref': move.ref,
                'date': move.date.strftime('%Y-%m-%d'),
                'journal': {
                    'id': move.journal_id.id,
                    'name': move.journal_id.name
                },
                'state': move.state,
                'company': {
                    'id': move.company_id.id,
                    'name': move.company_id.name
                },
                'lines': [{
                    'id': line.id,
                    'account': {
                        'id': line.account_id.id,
                        'code': line.account_id.code,
                        'name': line.account_id.name
                    },
                    'name': line.name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'partner': {
                        'id': line.partner_id.id,
                        'name': line.partner_id.name
                    } if line.partner_id else None,
                } for line in move.line_ids]
            }
            return APIResponse.success_response(message="Journal entry retrieved successfully", data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while processing the request', errors=str(e), status=500)
    
    @http.route('/api/journal-entries', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['list_journal_entries'])
    def list_journal_entry(self, company_id, journal_id=None, limit=20, offset=0, date_from=None, date_to=None, **kwargs):
        """
        Retrieves a list of all journal entries based on the provided filters.

        :param request: The HTTP request object containing optional filter parameters.
        :return: A dictionary containing the journal entry list or an error message.
        """
        try:
            domain = [
                ('move_type', '=', 'entry'),
                ('state', '=', 'posted'),
                ('payment_id', '=', None),
            ]
            is_valid, error_message = validate_company(request, company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            domain.append(('company_id', '=', int(company_id)))
            if (date_from and not date_to) or (date_to and not date_from):
                return APIResponse.error_response(message='Both date_from and date_to must be provided')
            elif date_from and date_to:
                domain.append(('date', '>=', date_from))
                domain.append(('date', '<=', date_to))
            if journal_id:  
                is_valid, error_message = validate_journal(request, journal_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid journal: {error_message}', f'Invalid journal_id: {journal_id}')
                domain.append(('journal_id', '=', int(journal_id)))

            limit = int(limit)
            offset = int(offset)
            # Get total count
            total_count = request.env['account.move'].sudo().search_count(domain)

            # Get journal entries with pagination
            moves = request.env['account.move'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc, id desc'  # Order by date descending, then by ID
            )

            # Format the journal entry data
            journal_entry_data = []
            for move in moves:
                journal_entry_data.append({
                    'id': move.id,
                    'name': move.name,
                    'ref': move.ref,
                    'date': move.date.strftime('%Y-%m-%d'),
                    'journal_id': {
                        'id': move.journal_id.id,
                        'name': move.journal_id.name
                    },
                    'state': move.state,
                    'company': {
                        'id': move.company_id.id,
                        'name': move.company_id.name
                    },
                })
            response_data = {
                'journal_entries': journal_entry_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message="Journal entries retrieved successfully", data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while processing the request', errors=str(e), status=500)
    
        
    @http.route('/api/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['delete_journal_entry'])
    def delete_journal_entry(self, journal_entry_id, **kwargs):
        """
        Deletes a specific journal entry by its ID.

        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing a success message or an error message.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                move = request.env['account.move'].sudo().browse(int(journal_entry_id))
                if not move.exists():
                    return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

                # Check the state of the journal entry
                if move.state == 'posted':
                    # Reset to draft first
                    move.button_draft()
                    # Then delete
                    move.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response(message="Journal entry deleted successfully", data=None)
                elif move.state == 'draft':
                    # If in draft state, can delete directly
                    move.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response(message="Journal entry deleted successfully", data=None)
                else:
                    return APIResponse.error_response(message=f'Cannot delete journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deleting journal entry', errors=str(e), status=500)

        

    @http.route('/api/cancel_journal_entry', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    def cancel_journal_entry(self, journal_entry_id, **kwargs):
        """
        Cancels a specific journal entry by its ID.

        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing a success message or an error message.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                move = request.env['account.move'].sudo().browse(int(journal_entry_id))
                if not move.exists():
                    return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

                # Check the state of the journal entry
                if move.state == 'posted':
                    # Reset to draft first
                    move.button_draft()

                    # Then cancel
                    move.with_context(send_webhook=True).button_cancel()

                    return APIResponse.success_response(message="Journal entry cancelled successfully", data=None)
                else:
                    return APIResponse.error_response(message=f'Cannot cancel journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}', status=400)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while cancelling journal entry', errors=str(e), status=500)
        