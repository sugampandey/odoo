from odoo import models
from .base import BaseOdooService
    

class ConfigParamService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['ir.config_parameter'].sudo()
    
    
    def set_param(self, key: str, value: str) -> None:
        self._get_model().set_param(key, value)
    
    def get_param(self, key: str) -> str:
        return self._get_model().get_param(key)

