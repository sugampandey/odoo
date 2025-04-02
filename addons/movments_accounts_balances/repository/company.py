from typing import Any, Dict, List, Optional, Union
from odoo import models
from .base import BaseOdooService
    

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
    
    