from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import json
from ..common import APIResponse, validate_and_convert_data


class PaymentAPI(http.Controller):

    @http.route('/api/get_all_payments', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_all_payments(self, **kwargs):
        try:
            domain = [('move_type', '=', 'entry'), ('payment_id', '!=', None), ('state', '=', 'posted')]
            payments = request.env['account.move'].sudo().search(domain)
            # prepare response data
            payment_data = [{
                'id': payment.id,
                'name': payment.name,
                'ref': payment.ref,
                'date': payment.date.strftime('%Y-%m-%d'),
                'journal_id': {
                    'id': payment.journal_id.id,
                    'name': payment.journal_id.name
                },
                'state': payment.state,
                'company': {
                    'id': payment.company_id.id,
                    'name': payment.company_id.name
                },
                'partner_id': {
                    'id': payment.partner_id.id,
                    'name': payment.partner_id.name
                },
                'payment_id': {
                    'id': payment.payment_id.id,
                    'name': payment.payment_id.name
                }
            } for payment in payments]
            return APIResponse.success_response(message="Payments retrieved successfully", data=payment_data)
        except Exception as e:
            return APIResponse.error_response(message=str(e), errors=str(e), status=500)
