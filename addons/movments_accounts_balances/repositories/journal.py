from typing import Any, Dict
from odoo import models
from .base import BaseOdooService
from .payment_method import PaymentMethodService
from ..enums import PaymentMethodType, JournalType, AccountType


class JournalService(BaseOdooService):
    asset_method_types = [AccountType.ASSET_CASH, AccountType.ASSET_CURRENT]
    liability_method_types = [AccountType.LIABILITY_CURRENT, AccountType.LIABILITY_CREDIT_CARD]

    def _get_model(self) -> models.Model:
        return self.env['account.journal'].sudo()
    
    def validate_journal(self, journal_id, company_id):
        model = self._get_model()
        journal = model.browse(int(journal_id))
        if not journal.exists():
            return False, 'Journal not found'
        if journal.company_id.id != int(company_id):
            return False, 'Journal belongs to different company'
        if journal.active == False:
            return False, 'Journal is not active'
        return True, ""
    
    def get_journal_code(self, company_id):
        model = self._get_model()
        journals = model.search([('company_id', '=', company_id)])
        journal_count = len(journals)
        return f"J{journal_count + 1}"
    
    def _determine_journal_type(self, account_type: str, payment_method: str) -> str:
        """Determine the journal type based on account type and payment method."""
        payment_method = payment_method.lower() if payment_method else 'none'
        account_type = account_type.lower()

        if payment_method == PaymentMethodType.NONE:
            if account_type == AccountType.INCOME:
                return JournalType.SALE
            elif account_type == AccountType.EXPENSE:
                return JournalType.PURCHASE
            return JournalType.GENERAL
        
        if account_type in self.liability_method_types:
            if payment_method == PaymentMethodType.CREDIT_CARD:
                return JournalType.BANK
            raise ValueError('Invalid payment method for liability account')
        
        if account_type in self.asset_method_types:
            if payment_method == PaymentMethodType.CASH:
                return JournalType.CASH
            if payment_method == PaymentMethodType.BANK:
                return JournalType.BANK
            
        raise ValueError('Invalid payment method')
    
    def create(self, values: Dict[str, Any]) -> models.Model:
        journal_type = self._determine_journal_type(values.get('account_type'), values.get('payment_method'))
        
        journal = super().create({  
            'name': values.get('name'),
            'code': self.get_journal_code(values.get('company_id')),
            'type': journal_type,
            'company_id': values.get('company_id'),
            'default_account_id': values.get('default_account_id'),
        })

        # Create payment methods for bank and cash journals
        if journal_type in ['cash', 'bank']:
            payment_method_service = PaymentMethodService(self.env)
            payment_method_service.create({
                'name': values.get('name'),
                'code': values.get('code'),
                'journal_id': journal.id,
                'payment_account_id': values.get('default_account_id'),
            })
