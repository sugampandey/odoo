from typing import Any, Dict, List, Optional, Union
from odoo import models
from .base import BaseOdooService
from ..constants import CONSTANTS
    

class ProductTemplateService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['product.template'].sudo()

    def create_default_product(self, company_id):
        model = self._get_model()
        default_product = model.create({
            'name': 'Default Product',
            'default_code': CONSTANTS['PRODUCT_DEFAULT_CODE'],
            'company_id': company_id,
            'type': 'consu',
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': 0.0,
            'standard_price': 0.0,
        })


