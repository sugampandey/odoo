from odoo import models, api
from ..constants import CONSTANTS

class Initializer(models.Model):
    _name = 'initializer.initializer'
    _description = 'Handles Initialization'
    
    @api.model
    def _auto_init(self):
        res = super()._auto_init()
        self._create_default_partner_categories()
        return res
    
    def _create_default_partner_categories(self):

        default_vendor_category = self.env['res.partner.category'].search([
            ('name', '=', CONSTANTS['VENDOR_CATEGORY_NAME'])
        ], limit=1)

        if not default_vendor_category:
            self.env['res.partner.category'].create({
                'name': CONSTANTS['VENDOR_CATEGORY_NAME'],
                'active': True,
            })

        default_customer_category = self.env['res.partner.category'].search([
            ('name', '=', CONSTANTS['CUSTOMER_CATEGORY_NAME'])
        ], limit=1)
        
        if not default_customer_category:
            self.env['res.partner.category'].create({
                'name': CONSTANTS['CUSTOMER_CATEGORY_NAME'],
                'active': True,
            })

    

