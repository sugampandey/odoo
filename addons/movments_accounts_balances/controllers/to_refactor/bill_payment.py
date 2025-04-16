from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

from odoo.fields import float_compare
from ...utils import APIResponse, validate_and_convert_data, get_request_data
from ...schemas.to_refactor.bill_payment import BILL_PAYMENT_SCHEMA
from ...repositories.partner import PartnerService
from ...repositories.account import AccountService
from ...repositories.company import CompanyService
from ...repositories.payment_method import PaymentMethodLineService

class BillPaymentController(http.Controller):
    LIABILITY_ACCOUNT_TYPES = ['liability_current', 'liability_payable', 'liability_receivable']

    def validate_and_prepare_bill_payment_data(self, data, bill_payment_expected_fields):
        payment_method_line_service = PaymentMethodLineService(request.env)
        company_service = CompanyService(request.env)
        account_service = AccountService(request.env)

        success, converted_data = validate_and_convert_data(data, bill_payment_expected_fields)
        if success is not True:
            return False, converted_data, converted_data
        
        if converted_data['payment_amount'] <= 0:
            raise UserError("Payment amount must be greater than zero.")

        # Validate company 
        company_id = converted_data['company_id']
        is_valid, error_message = company_service.validate_company(company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}'), converted_data

        bill_ids = eval(converted_data.get('bill_ids'))
            # Retrieve all bill records
        bills = request.env['account.move'].sudo().browse(bill_ids)
        if not bills:
            return False, APIResponse.error_response('No valid bills found'), converted_data

        # Validate all bills exist
        if len(bills) != len(bill_ids):
            return False, APIResponse.error_response('One or more bill IDs are invalid'), converted_data
        
        
        # Validate all bills are posted
        unposted_bills = bills.filtered(lambda b: b.state != 'posted')
        if unposted_bills:
            return False, APIResponse.error_response(f'All bills must be posted. Unposted bills: {unposted_bills.mapped("name")}'), converted_data
        
        # Validate all bills belong to the same partner
        if len(bills.mapped('partner_id')) > 1:
            raise UserError("All bills must belong to the same partner.")

        # Validate all bills are vendor bills
        non_vendor_bills = bills.filtered(lambda b: b.move_type != 'in_invoice')
        if non_vendor_bills:
            return False, APIResponse.error_response(
                f'{non_vendor_bills.mapped("name")} are not vendor bills'), converted_data


        # Validate all bills belong to the same partner
        if len(bills.mapped('partner_id')) > 1:
            return False, APIResponse.error_response(
                'All bills must belong to the same partner'), converted_data
        
        # Calculate total amount of bills
        total_bill_amount = sum(bills.mapped('amount_residual'))
        # Check if payment amount matches total bill amount
        if float_compare(converted_data['payment_amount'], total_bill_amount, precision_digits=2) != 0:
            return False, APIResponse.error_response(
                f"Payment amount ({converted_data['payment_amount']}) does not match total bill amount ({total_bill_amount})"), converted_data

        # check if destination_account_id is of liability account_type
        destination_account_id = int(converted_data.get('destination_account_id')) if converted_data.get('destination_account_id') else None
        if destination_account_id:
            is_valid, error_message = account_service.validate_account(destination_account_id, company_id, self.LIABILITY_ACCOUNT_TYPES)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {destination_account_id}'), converted_data
        else:
            # Get payable account from the first bill (since all bills are for same partner)
            payable_line = bills[0].line_ids.filtered(
                lambda l: l.account_id.account_type == 'liability_payable'
            )
            if payable_line:
                destination_account_id = payable_line.account_id.id        
        
        outstanding_account_id = int(converted_data.get('payment_account_id'))
        payment_method_line = payment_method_line_service.get_payment_method_line(outstanding_account_id, 'outbound')
        payment_method_id = payment_method_line.payment_method_id.id
        destination_journal_id = payment_method_line.journal_id.id

        # Create payment values
        payment_vals = {
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': converted_data.get('partner_id'),
            'payment_method_id': payment_method_id,
            'payment_method_line_id' : payment_method_line.id,
            'amount': converted_data.get('payment_amount'),
            'destination_account_id': destination_account_id,
            'destination_journal_id': destination_journal_id,
            'payment_reference': converted_data.get('payment_reference') if converted_data.get('payment_reference') else ', '.join(bills.mapped('name'))
        }
        return True, payment_vals, converted_data

    @http.route('/api/bill-payments', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    # @swagger_doc(bill_payments_docs['create_bill_payment'])
    def create_bill_payment(self, **kwargs):
        """
        Creates a payment for vendor bills.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data =  get_request_data(request)
                
                success, payment_vals, converted_data = self.validate_and_prepare_bill_payment_data(data, BILL_PAYMENT_SCHEMA)
                if success is not True:
                    return payment_vals
                
                company_id =int(converted_data['company_id'])

                # Create the payment
                payment = request.env['account.payment'].sudo().with_company(company_id).create(payment_vals)
                # if converted_data.get('outstanding_account_id'):
                #     # Wait for invoice to compute all lines
                #     payment.flush_recordset()
                    
                #     payment.write({
                #         'outstanding_account_id': converted_data['outstanding_account_id']
                #     })

                payment.with_context(send_webhook=True).action_post()


                # Prepare response data
                response_data = {
                    'id': payment.id,
                    'name': payment.name,
                    'amount': payment.amount,
                    'state': payment.move_id.state,
                    'partner': {
                        'id': payment.partner_id.id,
                        'name': payment.partner_id.name
                    },
                    'journal': {
                        'id': payment.journal_id.id,
                        'name': payment.journal_id.name
                    },
                    'payment_method': {
                        'id': payment.payment_method_id.id,
                        'name': payment.payment_method_id.name
                    },
                    'payment_reference': payment.payment_reference,
                }
                return APIResponse.success_response(message='Payment created successfully', data=response_data, status=201)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while creating the payment', errors=str(e))
        

    @http.route('/api/bill-payments', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(bill_payments_docs['list_bill_payments'])
    def list_bill_payments(self, partner_id, company_id, limit=20, offset=0, date_from=None, date_to=None, **kwargs):
        try:
            partner_service = PartnerService(request.env)
            # validate the partner record
            is_valid, error_message = partner_service.validate_partner(int(partner_id), int(company_id))
            if not is_valid:
                return APIResponse.error_response(message=f'Invalid Partner: {error_message}', errors=f'Invalid partner_id: {partner_id}', status=404)

            limit = int(limit)
            offset = int(offset)

            # Build domain with basic filters
            domain = [
                ('partner_id', '=', int(partner_id)), 
                ('partner_type', '=', 'supplier')
            ]
            if (date_from and not date_to) or (date_to and not date_from):
                return APIResponse.error_response(message='Both date_from and date_to must be provided')
            elif date_from and date_to:
                domain.append(('create_date', '>=', date_from))
                domain.append(('create_date', '<=', date_to))

            total_count = request.env['account.payment'].sudo().search_count(domain)

            # Retrieve the payment records with pagination
            payments = request.env['account.payment'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc, id desc'  # Order by date descending, then by ID
            )

            # Prepare the response data
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'id': payment.id,
                    'amount': payment.amount,
                    'name': payment.name,
                    'journal': {
                        'id': payment.journal_id.id,
                        'name': payment.journal_id.name,
                    },
                    'payment_method': {
                        'id': payment.payment_method_id.id,
                        'name': payment.payment_method_id.name,
                    },
                    'partner': {
                        'id': payment.partner_id.id,
                        'name': payment.partner_id.name,
                    },
                    'state': payment.move_id.state,
                    'payment_reference': payment.payment_reference,
                })
                
            response_data = {
                'payments': payment_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
            return APIResponse.success_response(message='Payment method lines retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        

    @http.route('/api/bill-payments/<int:payment_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    # @swagger_doc(bill_payments_docs['get_bill_payment'])
    def get_bill_payment(self, **kwargs):
        try:
            # Retrieve the payment record
            payment_id = kwargs.get('payment_id')
            payment = request.env['account.payment'].sudo().browse(int(payment_id))
            if not payment.exists():
                return APIResponse.error_response(message='Payment not found', errors='Payment not found', status=404)
            
            # Prepare the response data
            payment_data = {
                'id': payment.id,
                'amount': payment.amount,
                'name': payment.name,
                'state': payment.move_id.state,
                'payment_reference': payment.payment_reference,
                'partner': {
                    'id': payment.partner_id.id,
                    'name': payment.partner_id.name
                },
                'journal': {
                    'id': payment.journal_id.id,
                    'name': payment.journal_id.name
                },
                'payment_method': {
                    'id': payment.payment_method_id.id,
                    'name': payment.payment_method_id.name
                },
            }
            return APIResponse.success_response(message='Payment retrieved successfully', data=payment_data)
        except Exception as e:
            return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
    @http.route('/api/bill-payments/<int:payment_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    # @swagger_doc(bill_payments_docs['delete_bill_payment'])
    def delete_bill_payment(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                # Retrieve the payment record
                payment_id = kwargs.get('payment_id')
                payment = request.env['account.payment'].sudo().browse(int(payment_id))
                if not payment.exists():
                    return APIResponse.error_response(message='Payment not found', errors='Payment not found', status=404)
                
                # Verify it's a bill payment
                if payment.payment_type != 'outbound' or payment.partner_type != 'supplier':
                    return APIResponse.error_response(message='The specified record is not a bill payment', errors='Invalid payment type')

                # If payment is posted, reset to draft first
                if payment.move_id.state == 'posted':
                    payment.action_draft()
                
                # Delete the payment - Odoo will handle reconciliation automatically
                payment.with_context(send_webhook=True).action_cancel()
                return APIResponse.success_response(message='Payment deleted successfully')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message=str(e), errors=str(e), status=500)

            
