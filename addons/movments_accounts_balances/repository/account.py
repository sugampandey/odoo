from typing import Any, Dict, List, Optional, Union
from odoo import models
from .base import BaseOdooService
    

class AccountService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.account'].sudo()
    
    def validate_account(self, account_id, company_id, valid_account_types=None):
        """
        Validate account based on allowed account types
        Args:
            account_id: ID of the account to validate
            company_id: ID of the company
            valid_account_types: List of allowed account types. 
                            If None, no account type validation is performed
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if valid_account_types is None:
            valid_account_types = []

        model = self._get_model()
        account = model.browse(account_id)
        
        # Basic validations
        if not account.exists():
            return False, "Account does not exist"
            
        if account.company_id.id != int(company_id):
            return False, "Account belongs to different company"
            
        if account.deprecated:
            return False, "Selected account is deprecated"
            
        # Account type validation if types are specified
        if valid_account_types and account.account_type not in valid_account_types:
            return False, f"Invalid account type. Expected one of: {', '.join(valid_account_types)}"
            
        return True, ""
    
