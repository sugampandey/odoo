from odoo import models
from .base import BaseOdooService
    

class PartnerService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['res.partner'].sudo()