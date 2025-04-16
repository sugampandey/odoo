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

class ProductService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['product.product'].sudo()
    
    def get_default_product(self, company_id):
        model = self._get_model()
        domain = [
            ('product_tmpl_id.company_id', '=', int(company_id)),
            ('default_code', '=', CONSTANTS['PRODUCT_DEFAULT_CODE'])
        ]
        default_product = model.search(domain, limit=1)
        return default_product

    def validate_product(self, product_id, company_id):
        """
        Validate product based on company association
        Args:
            product_id: ID of the product to validate
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        model = self._get_model()
        product = model.browse(int(product_id))

        # Basic validations
        if not product.exists():
            return False, "Product does not exist"
        
        if product.product_tmpl_id.company_id:
            if product.product_tmpl_id.company_id.id != int(company_id):
                return False, "Product belongs to different company"
        
        if product.active == False:
            return False, "Product is not active"

        return True, ""


