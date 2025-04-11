from datetime import datetime
from odoo import http
from odoo.http import request
from ...utils import APIResponse, validate_and_convert_data, get_request_data
from ...schemas.to_refactor.invoice import INVOICE_SCHEMA
from ...repository.partner import PartnerService
from ...repository.account import AccountService
from ...repository.company import CompanyService
from ...repository.product import ProductService


class InvoiceController(http.Controller):
    INCOME_ACCOUNT_TYPES = ['income', 'income_other']
    RECEIVABLE_ACCOUNT_TYPES = ['asset_receivable']

    def validate_and_prepare_invoice_data(self, data, invoice_expected_fields):
        partner_service = PartnerService(request.env)
        product_service = ProductService(request.env)
        account_service = AccountService(request.env)
        company_service = CompanyService(request.env)
        success, converted_data = validate_and_convert_data(data, invoice_expected_fields)
        if success is not True:
            return False, converted_data, converted_data
        
        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = company_service.validate_company(company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}'), converted_data
        
        # validate partner 
        partner_id = converted_data['customer_id']
        is_valid, error_message = partner_service.validate_partner(partner_id, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid Customer: {error_message}', f'Invalid customer_id: {partner_id}'), converted_data

        # Validate receivable account if provided
        receivable_account_id = converted_data.get('receivable_account_id')
        if receivable_account_id:
            is_valid, error_message = account_service.validate_account(receivable_account_id, company_id, self.RECEIVABLE_ACCOUNT_TYPES)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {receivable_account_id}'), converted_data
        
        # Validate Invoice items
        if not converted_data['line_ids']:
            return False, APIResponse.error_response('No Invoice items provided', 'At least one Invoice item is required'), converted_data
            
        # Validate and Prepare the invoice lines
        invoice_lines = []
        for line in converted_data['line_ids']:
            # Validate account
            if line.get('account_id'):
                account_id = int(line['account_id'])
                is_valid, error_message = account_service.validate_account(account_id, company_id, self.INCOME_ACCOUNT_TYPES)
                if not is_valid:
                    return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}'), converted_data
            
            default_product = product_service.get_default_product(company_id)
            
            # Prepare invoice line values
            invoice_line_vals = {
                'name': line.get('description'),
                'quantity': 1,
                'price_unit': float(line.get('amount')) if line.get('amount') else None,
                'product_id': default_product.id,
                'partner_id': int(partner_id) if partner_id else partner_id,
                'tax_ids': [(6, 0, [])], # used to exclude tax else default 10% tax will be used
                'analytic_distribution': {k: int(v) if isinstance(v, str) and v.strip().isdigit() else v 
            for k, v in eval(line.get('class')).items()} if line.get('class') else None,
            }
            if line.get('account_id'):
                invoice_line_vals['account_id'] = int(line['account_id'])
            invoice_lines.append((0, 0, invoice_line_vals))

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_date': converted_data['invoice_date'],
            'invoice_date_due': converted_data['invoice_date_due'],
            'invoice_line_ids': invoice_lines,
            'ref': converted_data.get('ref'),
            'partner_id': int(partner_id) if partner_id else partner_id,
            'company_id' : int(company_id)
        }

        return True, invoice_vals, converted_data
    

    @http.route('/api/invoices', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(invoice_docs['create_invoice'])
    def create_ar_invoice(self, **kwargs):
        """
        Create an AR invoice and corresponding analytic lines based on the provided data.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)

                success, invoice_vals, converted_data = self.validate_and_prepare_invoice_data(data, INVOICE_SCHEMA)
                if success is not True:
                    return invoice_vals

                # Create a new AR invoice record
                invoice = request.env['account.move'].sudo().create(invoice_vals)

                # If custom receivable account is specified, modify the receivable line
                if converted_data.get('receivable_account_id'):
                    # Wait for invoice to compute all lines
                    invoice.flush_recordset()
                    
                    # Find the receivable line
                    receivable_line = invoice.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'asset_receivable'
                    )
                    
                    if receivable_line:
                        # Update the account
                        receivable_line.write({
                            'account_id': converted_data['receivable_account_id']
                        })

                invoice.with_context(send_webhook=True).action_post()
                
                # Prepare response data
                response_data = {
                    'id': invoice.id,
                    'name': invoice.name,
                    'ref': invoice.ref,
                    'date': invoice.date.strftime('%Y-%m-%d'),
                }
                return APIResponse.success_response(
                    message ='AR invoice created successfully',
                    data = response_data,
                    status = 201
                )

        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response('Failed to process request', str(e), status=500)
        
    @http.route('/api/invoices', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(invoice_docs['list_invoices'])
    def list_invoices(self, company_id, partner_id=None, state=None, 
                      limit=20, offset=0, date_from=None, date_to=None, **kwargs):
        try:
            partner_service = PartnerService(request.env)
            company_service = CompanyService(request.env)
            domain = [
                ('move_type', '=', 'out_invoice')
            ]
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            domain.append(('company_id', '=', int(company_id)))
            if partner_id:
                is_valid, error_message = partner_service.validate_partner(int(partner_id), int(company_id))
                if not is_valid:
                    return APIResponse.error_response(message=f'Invalid Partner: {error_message}', errors=f'Invalid partner_id: {partner_id}', status=404)
                domain.append(('partner_id', '=', int(partner_id)))
            if (date_from and not date_to) or (date_to and not date_from):
                return APIResponse.error_response(message='Both date_from and date_to must be provided')
            elif date_from and date_to:
                domain.append(('date', '>=', date_from))
                domain.append(('date', '<=', date_to))
            if state:
                domain.append(('state', '=', state))

            limit = int(limit)
            offset = int(offset)
            # Get total count for pagination info
            total_count = request.env['account.move'].sudo().search_count(domain)
            
            # Get paginated invoices
            invoices = request.env['account.move'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset,
                order='date desc'
            )
            # Format the invoice data
            invoice_data = []
            for invoice in invoices:
                invoice_data.append({
                    'id': invoice.id,
                    'name': invoice.name,
                    'ref': invoice.ref,
                    'date': invoice.date.strftime('%Y-%m-%d'),
                    'state': invoice.state,
                    'partner': {
                        'id': invoice.partner_id.id,
                        'name': invoice.partner_id.name
                    } if invoice.partner_id else None,
                    'amount': invoice.amount_total,
                    'company': {
                        'id': invoice.company_id.id,
                        'name': invoice.company_id.name
                    },
                })
            response_data = {
                'invoices': invoice_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message='Invoices retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response('An error occurred while retrieving invoices', str(e))
        
    @http.route('/api/invoices/<int:invoice_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(invoice_docs['get_invoice'])
    def get_invoice(self, invoice_id, **kwargs):
        try:
            invoice = request.env['account.move'].sudo().browse(invoice_id)
            if not invoice.exists():
                return APIResponse.error_response('Invoice not found', f'Invalid invoice_id: {invoice_id}')
            invoice_data = {
                'id': invoice.id,
                'name': invoice.name,
                'ref': invoice.ref,
                'date': invoice.date.strftime('%Y-%m-%d'),
                'state': invoice.state,
                'company': {
                    'id': invoice.company_id.id,
                    'name': invoice.company_id.name
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
                } for line in invoice.line_ids]
            }
            return APIResponse.success_response(message='Invoice retrieved successfully', data=invoice_data)
        except Exception as e:
            return APIResponse.error_response('An error occurred while retrieving invoice', str(e), status=500)
        

    @http.route('/api/invoices/<int:invoice_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(invoice_docs['delete_invoice'])
    def delete_invoice(self, invoice_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                # invoice_id = int(kwargs.get('invoice_id'))
                invoice = request.env['account.move'].sudo().browse(invoice_id)
                
                if not invoice.exists():
                    return APIResponse.error_response('Invoice not found', f'Invalid invoice_id: {invoice_id}')
                
                # Verify it's actually an invoice
                if invoice.move_type != 'out_invoice':
                    return APIResponse.error_response('The specified record is not a customer invoice', 'Invalid move type')

                # Check invoice state and handle accordingly
                if invoice.state == 'posted':
                    # First reset to draft
                    invoice.button_draft()
                    
                    # Cancel the invoice
                    invoice.button_cancel()
                    
                    # Now try to delete
                    invoice.with_context(send_webhook=True).unlink()
                    
                    return APIResponse.success_response(message='Invoice cancelled and deleted successfully')
                elif invoice.state == 'cancel' or invoice.state == 'draft':
                    # If already cancelled or in draft state, can delete directly
                    invoice.unlink()
                    return APIResponse.success_response(message='Invoice deleted successfully')
                else:
                    return APIResponse.error_response(f'Cannot delete invoice in {invoice.state} state', f'Invalid invoice state: {invoice.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response('An error occurred while deleting invoice', str(e), status=500)
        

    @http.route('/api/cancel_invoice', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    def cancel_invoice(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                invoice_id = int(kwargs.get('invoice_id'))
                invoice = request.env['account.move'].sudo().browse(invoice_id)

                if not invoice.exists():
                    return APIResponse.error_response('Invoice not found', f'Invalid invoice_id: {invoice_id}')

                # Verify it's actually an invoice
                if invoice.move_type != 'out_invoice':
                    return APIResponse.error_response('The specified record is not a customer invoice', 'Invalid move type')

                # Check invoice state and handle accordingly
                if invoice.state == 'posted':
                    # Reset to draft first
                    invoice.button_draft()

                    # Then cancel
                    invoice.with_context(send_webhook=True).button_cancel()

                    return APIResponse.success_response(message='Invoice cancelled successfully')
                else:
                    return APIResponse.error_response(f'Cannot cancel invoice in {invoice.state} state', f'Invalid invoice state: {invoice.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response('An error occurred while cancelling invoice', str(e))
        
    @http.route('/api/valid_invoice_accounts', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_valid_invoice_accounts(self, **kwargs):
        try:
            # Get valid income accounts using account_type
            valid_accounts = request.env['account.account'].sudo().search([
                ('account_type', 'in', ['income', 'income_other']),
                ('deprecated', '=', False)
            ])
            
            accounts_data = [{
                'id': account.id,
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type
            } for account in valid_accounts]
            return APIResponse.success_response(message='Valid accounts retrieved successfully', data=accounts_data)
        except Exception as e:
            return APIResponse.error_response('Failed to retrieve accounts', str(e))


