from .utils import BidirectionalMapper


CLASSIFICATION_DOCYT_TO_ODOO_MAPPING = {
    'asset': 'asset',
    'liability': 'liability',
    'equity': 'equity',
    'revenue': 'income',
    'expense': 'expense',
}
  

ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING = {
    'Accounts Receivable': 'asset_receivable',
    'Bank': 'asset_cash',
    'Other Current Asset': 'asset_current',
    'Other Asset': 'asset_non_current',
    'Accounts Payable': 'liability_payable',
    'Fixed Asset': 'asset_fixed',
    'Credit Card': 'liability_credit_card',
    'Other Current Liability': 'liability_current',
    'Long Term Liability': 'liability_non_current',
    'Equity': 'equity',
    'Income': 'income',
    'Other Income': 'income_other',
    'Expense': 'expense',
    'Cost of Goods Sold': 'expense_direct_cost',
    'Other Expense': 'expense_depreciation',
}

CLASSIFICATION_MAPPING = BidirectionalMapper(CLASSIFICATION_DOCYT_TO_ODOO_MAPPING) 
ACCOUNT_TYPE_MAPPING = BidirectionalMapper(ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING)