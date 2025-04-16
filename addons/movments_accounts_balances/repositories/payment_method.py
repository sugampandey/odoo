from typing import Any, Dict
from odoo import models
from odoo.exceptions import UserError
from .base import BaseOdooService


class PaymentMethodLineService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.payment.method.line'].sudo()
    
    def get_payment_method_line(self, outstanding_account_id, payment_type):
        model = self._get_model()
        domain = [
            ('payment_method_id.payment_type', '=', payment_type), 
            ('payment_account_id', '=', outstanding_account_id)
            ]
        payment_method_line = model.search(domain, limit=1)
        if not payment_method_line.exists():
            raise UserError("Payment method not found.")
        return payment_method_line


class PaymentMethodService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.payment.method'].sudo()

    def create(self, values: Dict[str, Any]) -> models.Model:
        results = []
        line_service = PaymentMethodLineService(self.env)

        for payment_type in ['inbound', 'outbound']:
            # Create payment method

            method = super().create({
                'name': f"{values.get('name')} ({payment_type.capitalize()})",
                'code': f"{values.get('code')}_{payment_type[:2]}",
                'payment_type': payment_type
            })
            
            # Create corresponding payment method line
            line = line_service.create({
                'name': method.name,
                'payment_method_id': method.id,
                'journal_id': values.get('journal_id'),
                'payment_account_id': values.get('account_id')
            })
            
            results.append((method, line))
        
        return results
        
