from datetime import datetime
from odoo import http
from odoo.http import request
from ...utils import APIResponse, validate_and_convert_data, get_request_data
from ...schemas.to_refactor.bills import BILL_SCHEMA
from ...repository.partner import PartnerService
from ...repository.account import AccountService
from ...repository.company import CompanyService
from ...repository.product import ProductService


class BillController(http.Controller):
    PAYABLE_ACCOUNT_TYPES = ['liability_payable']

    def validate_and_prepare_bill_data(self, data, bill_expected_fields):
        partner_service = PartnerService(request.env)
        product_service = ProductService(request.env)
        account_service = AccountService(request.env)
        company_service = CompanyService(request.env)

        success, converted_data = validate_and_convert_data(data, bill_expected_fields)
        if success is not True:
            return False, converted_data, converted_data
        
        # Validate company if provided
        company_id = converted_data.get('company_id')
        if company_id:
            is_valid, error_message = company_service.validate_company(company_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}'), converted_data
        
        # validate partner
        partner_id = converted_data.get('partner_id')
        if partner_id:
            is_valid, error_message = partner_service.validate_partner(partner_id, company_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}'), converted_data
        
        # Validate payable account if provided
        if converted_data.get('payable_account_id'):
            is_valid, error_message = account_service.validate_account(converted_data['payable_account_id'], company_id, self.PAYABLE_ACCOUNT_TYPES)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid payable_account_id: {converted_data["payable_account_id"]}'), converted_data

        # Validate and prepare bill items
        if not converted_data['line_ids']:
            return False, APIResponse.error_response('No bill items provided', 'At least one bill item is required'), converted_data
        
        # Prepare the bill lines
        bill_lines = []
        for line in converted_data['line_ids']:
            # Validate account
            if line.get('account_id'):
                is_valid, error_message = account_service.validate_account(line['account_id'], company_id)
                if not is_valid:
                    return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {line["account_id"]}'), converted_data
            
            default_product = product_service.get_default_product(company_id)
            
            # Prepare bill line values
            bill_line_vals = {
                'name': line.get('description'),
                'quantity': 1,
                'price_unit': float(line.get('amount')) if line.get('amount') else None,
                'product_id': default_product.id, # Fix ID of global product
                'partner_id': int(partner_id) if partner_id else partner_id,
                'tax_ids': [(6, 0, [])], # used to exclude tax else default 10% tax will be used
                'analytic_distribution': {k: int(v) if isinstance(v, str) and v.strip().isdigit() else v
            for k, v in eval(line.get('class')).items()} if line.get('class') else None,
            }
            if line.get('account_id'):
                bill_line_vals['account_id'] = int(line['account_id'])
            bill_lines.append((0, 0, bill_line_vals))

        # Prepare bill values
        bill_vals = {
            'move_type': 'in_invoice',  # This specifies it's a vendor bill
            'partner_id': converted_data['partner_id'],
            'invoice_date': converted_data['invoice_date'],
            'invoice_date_due': converted_data['invoice_date_due'],
            'ref': converted_data.get('ref'),
            'invoice_line_ids': bill_lines,
            'company_id' : int(company_id)
        }
        return True, bill_vals, converted_data


    @http.route('/api/bills', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(bills_docs['create_bill'])
    def create_bill(self, **kwargs):
        """
        Creates a vendor bill (supplier invoice) in Odoo.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)          

                success, bill_vals, converted_data = self.validate_and_prepare_bill_data(data, BILL_SCHEMA)
                if success is not True:
                    return bill_vals
                
                # Create the bill
                bill = request.env['account.move'].sudo().create(bill_vals)

                # If custom payable account is specified, modify the payable line
                if converted_data.get('payable_account_id'):
                    # Wait for bill to compute all lines
                    bill.flush_recordset()

                    payable_line = bill.line_ids.filtered(
                        lambda l: l.account_id.account_type == 'liability_payable'
                    )
                    if payable_line:
                        payable_line.write({
                            'account_id': converted_data['payable_account_id']
                        })

                bill.with_context(send_webhook=True).action_post()

                # Prepare response data
                response_data = {
                    'id': bill.id,
                    'name': bill.name,
                    'ref': bill.ref,
                    'invoice_date': bill.invoice_date.strftime('%Y-%m-%d') if bill.invoice_date else None,
                    'amount_total': bill.amount_total,
                }

                return APIResponse.success_response(
                    message='Vendor bill created successfully',
                    data=response_data,
                    status=201
                )
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the vendor bill', errors=str(e), status=500)
        
    @http.route('/api/bills', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(bills_docs['list_bills'])
    def get_bills(self, company_id, partner_id=None, state=None, 
                  limit=20, offset=0, date_from=None, date_to=None, **kwargs):
        try:
            company_service = CompanyService(request.env)
            partner_service = PartnerService(request.env)
            domain = [('move_type', '=', 'in_invoice')]
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

            bills = request.env['account.move'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc'
            )

            bill_data = []
            for bill in bills:
                bill_data.append({
                    'id': bill.id,
                    'name': bill.name,
                    'ref': bill.ref,
                    'invoice_date': bill.invoice_date.strftime('%Y-%m-%d') if bill.invoice_date else None,
                    'invoice_date_due': bill.invoice_date_due.strftime('%Y-%m-%d') if bill.invoice_date_due else None,
                    'state': bill.state,
                    'amount_total': bill.amount_total,
                    'partner': {
                        'id': bill.partner_id.id,
                        'name': bill.partner_id.name
                    },
                    'bill_lines': [{
                        'id': line.id,
                        'product': {
                            'id': line.product_id.id,
                            'name': line.product_id.name
                        } if line.product_id else None,
                        'name': line.name,
                        'quantity': line.quantity,
                        'price_unit': line.price_unit,
                        'price_subtotal': line.price_subtotal,
                        'account': {
                            'id': line.account_id.id,
                            'name': line.account_id.name
                        }
                    } for line in bill.invoice_line_ids]
                })

            response_data = {
                'bills': bill_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message='Bills retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving bills', errors=str(e), status=500)
        
    @http.route('/api/bills/<int:bill_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(bills_docs['get_bill'])
    def get_bill(self, bill_id, **kwargs):
        try:
            bill = request.env['account.move'].sudo().browse(bill_id)
            if not bill:
                return APIResponse.error_response(message='Bill not found', errors=f'Invalid bill_id: {bill_id}', status=404)
            
            bill_data = {
                'id': bill.id,
                'name': bill.name,
                'ref': bill.ref,
                'invoice_date': bill.invoice_date.strftime('%Y-%m-%d') if bill.invoice_date else None,
                'invoice_date_due': bill.invoice_date_due.strftime('%Y-%m-%d') if bill.invoice_date_due else None,
                'state': bill.state,
                'amount_total': bill.amount_total,
                'partner': {
                    'id': bill.partner_id.id,
                    'name': bill.partner_id.name
                },
                'bill_lines': [{
                    'id': line.id,
                    'product': {
                        'id': line.product_id.id,
                        'name': line.product_id.name
                    },
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'account': {
                        'id': line.account_id.id,
                        'name': line.account_id.name
                    }
                    } for line in bill.invoice_line_ids]
            }
            return APIResponse.success_response(message='Bill retrieved successfully', data=bill_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while retrieving the bill', errors=str(e), status=500)
        

    @http.route('/api/bills/<int:bill_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(bills_docs['delete_bill'])
    def delete_bill(self, bill_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():                
                bill = request.env['account.move'].sudo().browse(bill_id)
                if not bill:
                    return APIResponse.error_response(message='Bill not found', errors=f'Invalid bill_id: {bill_id}', status=404)

                # Verify it's actually a bill
                if bill.move_type != 'in_invoice':
                    return APIResponse.error_response(message='The specified record is not a vendor bill', errors=f'Invalid move type: {bill.move_type}', status=400)

                # Handle based on bill state
                if bill.state == 'posted':
                    # Reset to draft first
                    bill.button_draft()
                    
                    # Cancel the bill
                    bill.button_cancel()
                    
                    # Now delete
                    bill.with_context(send_webhook=True).unlink()
                    
                    return APIResponse.success_response(message='Bill cancelled and deleted successfully')
                elif bill.state == 'cancel' or bill.state == 'draft':
                    # If already cancelled, just delete
                    bill.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response(message='Bill deleted successfully')
                else:
                    return APIResponse.error_response(message=f'Cannot delete bill in {bill.state} state', errors=f'Invalid bill state: {bill.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deleting the bill', errors=str(e), status=500)

    @http.route('/api/cancel_bill', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(bills_docs['cancel_bill'])
    def cancel_bill(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                bill_id = int(data.get('bill_id')) if data.get('bill_id') else data.get('bill_id')
                if not bill_id:
                    return APIResponse.error_response(message=f'Missing required parameter: {bill_id}')
                
                bill = request.env['account.move'].sudo().browse(bill_id)
                if not bill:
                    return APIResponse.error_response(message='Bill not found', errors=f'Invalid bill_id: {bill_id}', status=404)

                if bill.state == 'posted':
                    # Reset to draft first
                    bill.button_draft()
                    # Then cancel
                    bill.with_context(send_webhook=True).button_cancel()
                    
                    return APIResponse.success_response(
                        message='Bill cancelled successfully',
                        data={
                            'bill_id': bill.id,
                            'state': bill.state
                        },
                    )
                else:
                    return APIResponse.error_response(message=f'Cannot cancel bill in {bill.state} state', errors=f'Invalid bill state: {bill.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while cancelling the bill', errors=str(e), status=500)


