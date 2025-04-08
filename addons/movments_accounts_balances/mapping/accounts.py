from .bidirectional_mapper import BidirectionalMapper

TYPE_PREFIX_MAPPING = {
    'asset_receivable': 'AR',      # Accounts Receivable
    'asset_cash': 'BK',           # Bank
    'asset_current': 'CA',        # Other Current Asset
    'asset_non_current': 'OA',    # Other Asset
    'liability_payable': 'AP',    # Accounts Payable
    'asset_fixed': 'FA',          # Fixed Asset
    'liability_credit_card': 'CC', # Credit Card
    'liability_current': 'CL',     # Other Current Liability
    'liability_non_current': 'LT', # Long Term Liability
    'equity': 'EQ',               # Equity
    'income': 'IN',               # Income
    'income_other': 'OI',         # Other Income
    'expense': 'EX',              # Expense
    'expense_direct_cost': 'CG',  # Cost of Goods Sold
    'expense_depreciation': 'OE'   # Other Expense
}

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

ACCOUNT_CLASSIFICATION_MAPPING = BidirectionalMapper(CLASSIFICATION_DOCYT_TO_ODOO_MAPPING) 
ACCOUNT_TYPE_MAPPING = BidirectionalMapper(ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING)