from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

from odoo.fields import float_compare
from ...utils import APIResponse, validate_and_convert_data, get_request_data
from ...schemas.to_refactor.invoice_payment import INVOICE_PAYMENT_SCHEMA
from ...repositories.partner import PartnerService
from ...repositories.account import AccountService
from ...repositories.company import CompanyService
from ...repositories.payment_method import PaymentMethodLineService

class InvocePaymentController(http.Controller):
    ASSET_ACCOUNT_TYPES = ['asset_cash', 'asset_current', 'asset_receivable']

    def create_unapplied_payment(self, request, data):
        """
        Helper method to create an unapplied payment (credit) for a customer.
        """
        payment_method_line_service = PaymentMethodLineService(request.env)
        # check payment method
        payment_method_line = payment_method_line_service.get_payment_method_line(int(data['payment_method_id']))
        payment_method_id = payment_method_line.payment_method_id.id
        destination_journal_id = payment_method_line.journal_id.id

        # Create the unapplied payment record
        payment_vals = {
            'payment_type': 'inbound',  # 'inbound' for customer payments
            'partner_type': 'customer',
            'partner_id': int(data['partner_id']) if data.get('partner_id') else data.get('partner_id'),
            'amount': int(data['payment_amount']) if data.get('payment_amount') else data.get('payment_amount'),
            'destination_journal_id': destination_journal_id,
            'payment_method_id': payment_method_id,
            'payment_reference': 'Unapplied Payment',
            'destination_account_id': int(data['destination_account_id']) if data.get('destination_account_id') else data.get('destination_account_id')
        }

        payment = request.env['account.payment'].sudo().create(payment_vals)

        # Post the payment, making it available as a credit
        payment.with_context(send_webhook=True).action_post()

        # prepare response data
        response_data = {
            'id': payment.id,
            'amount': payment.amount,
            'journal': {
                'id': payment.destination_journal_id.id,
                'name': payment.destination_journal_id.name,
                'type': payment.destination_journal_id.type,
            },
            'payment_method': {
                'id': payment.payment_method_id.id,
                'name': payment.payment_method_id.name,
            },
            'partner': {
                'id': payment.partner_id.id,
                'name': payment.partner_id.name,
            },
            'account': {
                'id': payment.destination_account_id.id,
                'name': payment.destination_account_id.name,
            },
            'date': payment.date.strftime('%Y-%m-%d'),
            'state': payment.move_id.state,
            'payment_reference': payment.payment_reference,
        }
        return APIResponse.success_response(message='Unapplied payment created as a credit for future use', data=response_data)

    def validate_and_prepare_invoice_payment_data(self, data, invoice_payment_expected_fields):
        payment_method_line_service = PaymentMethodLineService(request.env)
        company_service = CompanyService(request.env)
        account_service = AccountService(request.env)
        success, converted_data = validate_and_convert_data(data, invoice_payment_expected_fields)
        if success is not True:
            return False, converted_data, converted_data
        
        if converted_data['payment_amount'] <= 0:
            raise UserError("Payment amount must be greater than zero.")
        
        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = company_service.validate_company(company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}'), converted_data
        
        # invoice_id = converted_data.get('invoice_id')
        invoice_ids = eval(converted_data.get('invoice_ids'))
        # # Check if we are creating an unapplied payment (credit)
        # if not invoice_id:
        #     return False, self.create_unapplied_payment(request, converted_data), converted_data
        
        # Retrieve the invoice record
        invoices = request.env['account.move'].sudo().browse(invoice_ids)
        if not invoices:
            raise UserError("No invoice found.")
        
        # Validate all invoices exist
        if len(invoices) != len(invoice_ids):
            raise UserError("One or more invoice IDs are invalid.")
        
        # Validate all invoices are customer invoices
        non_customer_invoices = invoices.filtered(lambda b: b.move_type != 'out_invoice')
        if non_customer_invoices:
            raise UserError(f'{non_customer_invoices.mapped("name")} are not customer invoices')

        # Validate all invoices are posted
        unposted_invoices = invoices.filtered(lambda inv: inv.state != 'posted')
        if unposted_invoices:
            raise UserError(f"All invoices must be posted. Unposted invoices: {unposted_invoices.mapped('name')}")

        # Validate all invoices belong to the same partner
        if len(invoices.mapped('partner_id')) > 1:
            raise UserError("All invoices must belong to the same partner.")
        
        # Calculate total amount of invoices
        total_invoice_amount = sum(invoices.mapped('amount_residual'))
        
        # Check if payment amount matches total invoice amount
        if float_compare(converted_data['payment_amount'], total_invoice_amount, precision_digits=2) != 0:
            raise UserError(f"Payment amount ({converted_data['payment_amount']}) does not match total invoice amount ({total_invoice_amount})")
            
        # check if destination_account_id is of asset account_type
        destination_account_id = int(converted_data.get('account_id')) if converted_data.get('account_id') else None
        if destination_account_id:
            is_valid, error_message = account_service.validate_account(destination_account_id, company_id, self.ASSET_ACCOUNT_TYPES)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {destination_account_id}'), converted_data
        else:
            # Get receivable account from the first invoice (since all invoices are for same partner)
            receivable_line = invoices[0].line_ids.filtered(
                lambda l: l.account_id.account_type == 'asset_receivable'
            )
            if receivable_line:
                destination_account_id = receivable_line.account_id.id

        outstanding_account_id = int(converted_data.get('payment_account_id'))
        payment_method_line = payment_method_line_service.get_payment_method_line(outstanding_account_id, 'inbound')
        payment_method_id = payment_method_line.payment_method_id.id
        destination_journal_id = payment_method_line.journal_id.id

        # Create the payment record
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoices[0].partner_id.id,
            'amount': converted_data['payment_amount'],
            'destination_account_id': destination_account_id,
            'destination_journal_id': destination_journal_id,
            'payment_method_id': payment_method_id,
            'payment_method_line_id' : payment_method_line.id,
            'payment_reference': converted_data.get('payment_reference') if converted_data.get('payment_reference') else ', '.join(invoices.mapped('name')), 
        }
        return True, payment_vals, converted_data
    

    @http.route('/api/invoice-payments', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(invoice_payments_docs['create_invoice_payment'])
    def create_invoice_payment(self, **kwargs):
        """
        Make a payment for an AR invoice.
        - Partial payment for a single invoice
        - Full payment for a single invoice
        - Payment for multiple invoices
        - Unapplied payment as credit
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data =  get_request_data(request)
                
                success, payment_vals, converted_data = self.validate_and_prepare_invoice_payment_data(data, INVOICE_PAYMENT_SCHEMA)
                if success is not True:
                    return payment_vals
                
                company_id =int(converted_data['company_id'])

                payment = request.env['account.payment'].sudo().with_company(company_id).create(payment_vals)

                # if converted_data.get('payment_account_id'):
                #     # Wait for invoice to compute all lines
                #     payment.flush_recordset()
                    
                #     payment.write({
                #         'outstanding_account_id': converted_data['payment_account_id']
                #     })

                # Post the payment
                payment.with_context(send_webhook=True).action_post()

                # prepare response data
                response_data = {
                    'id': payment.id,
                    'amount': payment.amount,
                    'journal': {
                        'id': payment.destination_journal_id.id,
                        'name': payment.destination_journal_id.name,
                        'type': payment.destination_journal_id.type,
                    },
                    'payment_method': {
                        'id': payment.payment_method_id.id,
                        'name': payment.payment_method_id.name,
                    },
                    'partner': {
                        'id': payment.partner_id.id,
                        'name': payment.partner_id.name,
                    },
                    'account': {
                        'id': payment.destination_account_id.id,
                        'name': payment.destination_account_id.name,
                    },
                    'date': payment.date.strftime('%Y-%m-%d'),
                    'state': payment.move_id.state,
                    'payment_reference': payment.payment_reference,
                    # 'invoice_id': invoice.id
                }
                return APIResponse.success_response(message='Payment created successfully', data=response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response('An error occurred while creating payment', str(e), status=500)

    
    @http.route('/api/invoice-payments/', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(invoice_payments_docs['list_invoice_payments'])
    def list_invoice_payments(self, partner_id, company_id, limit=20, offset=0, date_from=None, date_to=None, **kwargs):
        partner_service = PartnerService(request.env)
        try:
            is_valid, error_message = partner_service.validate_partner(int(partner_id), int(company_id))
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid Partner: {error_message}', errors=f'Invalid partner_id: {partner_id}', status=404)
            domain = [
                ('partner_id', '=', int(partner_id)),
                ('partner_type', '=', 'customer')
            ]
            if (date_from and not date_to) or (date_to and not date_from):
                return APIResponse.error_response(message='Both date_from and date_to must be provided')
            elif date_from and date_to:
                domain.append(('create_date', '>=', date_from))
                domain.append(('create_date', '<=', date_to))

            limit = int(limit)
            offset = int(offset)
            # Get total count for pagination info
            total_count = request.env['account.payment'].sudo().search_count(domain)
            # Retrieve the paginated payment records
            payments = request.env['account.payment'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc'
            )

            # Prepare the response data
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'id': payment.id,
                    'amount': payment.amount,
                    'journal': {
                        'id': payment.destination_journal_id.id,
                        'name': payment.destination_journal_id.name,
                        'type': payment.destination_journal_id.type,
                    },
                    'payment_method': {
                        'id': payment.payment_method_id.id,
                        'name': payment.payment_method_id.name,
                    },
                    'partner': {
                        'id': payment.partner_id.id,
                        'name': payment.partner_id.name,
                    },
                    'account': {
                        'id': payment.destination_account_id.id,
                        'name': payment.destination_account_id.name,
                    },
                    'state': payment.move_id.state,
                    'payment_reference': payment.payment_reference,
                    # 'invoice_id': [invoice.id for invoice in payment.move_id.filtered(lambda m: m.state == 'posted')]
                })

            response_data = {
                'payments': payment_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message='Payment details retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response('An error occurred while retrieving payment details', str(e), status=500)
        
    @http.route('/api/invoice-payments/<int:payment_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(invoice_payments_docs['get_invoice_payment'])
    def get_invoice_payment(self, payment_id, **kwargs):
        try:
            # Retrieve the payment record
            payment = request.env['account.payment'].sudo().browse(int(payment_id))
            if not payment.exists():
                return APIResponse.error_response('Payment not found', 'Payment not found')
            
            # Prepare the response data
            payment_data = {
                'id': payment.id,
                'amount': payment.amount,
                'journal': {
                    'id': payment.destination_journal_id.id,
                    'name': payment.destination_journal_id.name,
                    'type': payment.destination_journal_id.type,
                },
                'payment_method': {
                    'id': payment.payment_method_id.id,
                    'name': payment.payment_method_id.name,
                },
                'partner': {
                    'id': payment.partner_id.id,
                    'name': payment.partner_id.name,
                },
                'account': {
                    'id': payment.destination_account_id.id,
                    'name': payment.destination_account_id.name,
                },
                'state': payment.move_id.state,
                'payment_reference': payment.payment_reference,
            }
            return APIResponse.success_response(message='Payment details retrieved successfully', data=payment_data)
        except Exception as e:
            return APIResponse.error_response('An error occurred while retrieving payment details', str(e), status=500)
        
    @http.route('/api/invoice-payments/<int:payment_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(invoice_payments_docs['delete_invoice_payment'])
    def delete_invoice_payment(self, payment_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                # Retrieve the payment record
                payment = request.env['account.payment'].sudo().browse(int(payment_id))
                if not payment.exists():
                    return APIResponse.error_response('Payment not found', 'Payment not found')
                
                # If payment is posted, reset to draft first
                if payment.move_id.state == 'posted':
                    payment.action_draft()
                
                # Delete the payment - Odoo will handle reconciliation automatically
                payment.with_context(send_webhook=True).unlink()
        
                return APIResponse.success_response(message='Payment deleted successfully')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response('An error occurred while deleting payment', str(e), status=500)