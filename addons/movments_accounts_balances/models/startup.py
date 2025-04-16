from odoo import models, api
from ..constants import CONSTANTS
from ..repositories.partner import PartnerCategoryService

class Initializer(models.Model):
    _name = 'initializer.initializer'
    _description = 'Handles Initialization'
    
    @api.model
    def _auto_init(self):
        res = super()._auto_init()
        self._create_default_partner_categories()
        return res
    
    def _create_default_partner_categories(self):
        partner_category_service = PartnerCategoryService(self.env)

        default_vendor_category = partner_category_service.search([
            ('name', '=', CONSTANTS['VENDOR_CATEGORY_NAME'])
        ], limit=1)

        if not default_vendor_category:
            partner_category_service.create({
                'name': CONSTANTS['VENDOR_CATEGORY_NAME'],
                'active': True,
            })

        default_customer_category = partner_category_service.search([
            ('name', '=', CONSTANTS['CUSTOMER_CATEGORY_NAME'])
        ], limit=1)
        
        if not default_customer_category:
            partner_category_service.create({
                'name': CONSTANTS['CUSTOMER_CATEGORY_NAME'],
                'active': True,
            })

    

