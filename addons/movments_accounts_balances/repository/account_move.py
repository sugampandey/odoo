from odoo import models
from .base import BaseOdooService
    

class AccountMoveService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.move'].sudo()
    