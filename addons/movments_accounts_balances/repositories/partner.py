from ..constants import CONSTANTS
from odoo import models
from .base import BaseOdooService
    

class PartnerService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['res.partner'].sudo()
    
    def validate_partner(self, partner_id, company_id):
        """
        Validate partner based on company association
        Args:
            partner_id: ID of the partner to validate
            company_id: ID of the company
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        model = self._get_model()
        partner = model.browse(int(partner_id))

        # Basic validations
        if not partner.exists():
            return False, "Partner does not exist"

        if partner.company_id and partner.company_id.id != int(company_id):
            return False, "Partner is not associated with the provided company"
        
        if partner.active == False:
            return False, "Partner is not active"

        return True, ""
    
    def create_default_partners(self, company_id):
        """Create default vendor and customer for the company"""
        customer_category_id = PartnerCategoryService(self.env).get_default_customer_category()
        vendor_category_id = PartnerCategoryService(self.env).get_default_vendor_category()
        # Create vendor
        self.create({
            'name': CONSTANTS['DEFAULT_VENDOR_NAME'],
            'is_company': False,
            'supplier_rank': 1,
            'customer_rank': 0,
            'company_id': company_id,
            'category_id': [(6, 0, [vendor_category_id])]
        })
        
        # Create customer
        self.create({
            'name': CONSTANTS['DEFAULT_CUSTOMER_NAME'],
            'is_company': False,
            'supplier_rank': 0,
            'customer_rank': 1,
            'company_id': company_id,
            'category_id': [(6, 0, [customer_category_id])]
        })


class PartnerCategoryService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['res.partner.category'].sudo()
    
    def get_default_vendor_category(self):
        return self._get_model().search([
            ('name', '=', CONSTANTS['VENDOR_CATEGORY_NAME'])
        ], limit=1).id
    
    def get_default_customer_category(self):
        return self._get_model().search([
            ('name', '=', CONSTANTS['CUSTOMER_CATEGORY_NAME'])
        ], limit=1).id
    
    