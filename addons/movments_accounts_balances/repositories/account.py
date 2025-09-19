from odoo import models
from .base import BaseOdooService
from ..constants import CONSTANTS
from .currency import CurrencyService
from .journal import JournalService
from ..schemas.accounts import AccountCreateRequestModel
    

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
    
    def create_default_accounts(self, company_id):
        """Create default accounts for the company"""
        currency_id = CurrencyService(self.env).get_default_currency_id()
        for account_data in CONSTANTS['DEFAULT_ACCOUNTS']:
            account_vals = account_data.copy()
            account_vals['company_id'] = company_id
            account_vals['currency_id'] = currency_id
            account_vals['code'] = AccountCreateRequestModel.get_unique_account_code(account_vals['account_type'])
            account = self.create(account_vals)
            journal_vals = {
                'name': account.name,
                'code': account.code,
                'company_id': account.company_id.id,
                'default_account_id': account.id,
                'account_type': account.account_type,
                'payment_method': None,
            }
            journal_service = JournalService(self.env)
            journal_service.create(journal_vals)

    
