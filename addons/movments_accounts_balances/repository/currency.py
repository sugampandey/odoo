from odoo import models
from odoo.exceptions import UserError
from .base import BaseOdooService
    

class CurrencyService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['res.currency'].sudo()
    
    def get_currency_id(self, currency_value):
        model = self._get_model()
        currency = model.search([('name', '=', currency_value)], limit=1)
        if not currency:
            raise UserError("Invalid currency")
        return currency.id
    
    def get_default_currency_id(self):
        model = self._get_model()
        currency = model.search([('name', '=', 'USD')], limit=1)
        if not currency:
            raise UserError("Invalid currency")
        return currency.id

