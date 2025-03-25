from .payment_method import PaymentMethod
from ..enums import PaymentMethodType, JournalType, AccountType

class Journal:
    asset_method_types = ['asset_cash', 'asset_current']
    liability_method_types = ['liability_current', 'liability_credit_card']

    @classmethod
    def get_journal_code(cls, request, company_id):
        journals = request.env['account.journal'].sudo().search([('company_id', '=', company_id)])
        journal_count = len(journals)
        return f"J{journal_count + 1}"
    
    @classmethod
    def create(cls, request, name, code, company_id, default_account_id, account_type, payment_method):
        payment_method = payment_method if payment_method else 'none'
        if payment_method.lower() == PaymentMethodType.NONE:
            if account_type.lower() == AccountType.INCOME:
                journal_type = JournalType.SALE
            elif account_type.lower() == AccountType.EXPENSE:
                journal_type = JournalType.PURCHASE
            else:
                journal_type = JournalType.GENERAL
        elif account_type.lower() in cls.liability_method_types:
            if payment_method.lower() == PaymentMethodType.CREDIT_CARD:
                journal_type = JournalType.BANK
            else:
                raise ValueError('Invalid payment method for liability account')
        elif account_type.lower() in cls.asset_method_types:
            if payment_method.lower() == PaymentMethodType.CASH:
                journal_type = JournalType.CASH
            if payment_method.lower() == PaymentMethodType.BANK:
                journal_type = JournalType.BANK
        else:
            raise ValueError('Invalid payment method')
        
        journal = request.env['account.journal'].sudo().create({
            'name': name,
            'code': cls.get_journal_code(request, company_id),
            'type': journal_type,
            'company_id': company_id,
            'default_account_id': default_account_id,
        })
        if journal_type in ['cash', 'bank']:
            PaymentMethod.create_payment_method(request, name, code, journal.id, default_account_id)
        # return journal