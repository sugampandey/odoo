from odoo import models
from .base import BaseOdooService
from .account import AccountService
from .partner import PartnerService
from .product import ProductTemplateService


class CompanyService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['res.company'].sudo()
    
    def validate_company(self, company_id):
        """
        Validate company existence
        Args:
            company_id: ID of the company to validate
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        model = self._get_model()
        company = model.browse(int(company_id))
        if not company.exists():
            return False, "Company does not exist"
        if company.active == False:
            return False, "Company is not active"
        return True, ""
    
    def create_default_setup(self, company_id):
        """Orchestrate creation of all default company setup"""
        ProductTemplateService(self.env).create_default_product(company_id)
        AccountService(self.env).create_default_accounts(company_id)
        PartnerService(self.env).create_default_partners(company_id)

