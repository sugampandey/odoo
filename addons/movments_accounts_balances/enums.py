from enum import Enum

class JournalType(str, Enum):
    """Enum for journal types"""
    SALE = 'sale'
    PURCHASE = 'purchase'
    GENERAL = 'general'
    BANK = 'bank'
    CASH = 'cash'

class PaymentMethodType(str, Enum):
    """Enum for payment method types"""
    NONE = 'none'
    CASH = 'cash'
    BANK = 'bank'
    CREDIT_CARD = 'credit_card'

class AccountType(str, Enum):
    """Enum for account types"""
    INCOME = 'income'
    EXPENSE = 'expense'