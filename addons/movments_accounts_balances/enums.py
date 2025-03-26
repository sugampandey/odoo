from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, NamedTuple


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


class ColumnMapping(NamedTuple):
    column_type: type
    display_name: str
    odoo_column_name: str

class GLReportColumns(Enum):
    TX_DATE = ('tx_date', ColumnMapping(
        column_type='Date',
        display_name='Date',
        odoo_column_name='date'
    ))
    TXN_TYPE = ('txn_type', ColumnMapping(
        column_type='String',
        display_name='Transaction Type',
        odoo_column_name='move_type'
    ))
    DOC_NUM = ('doc_num', ColumnMapping(
        column_type='String',
        display_name='Num',
        odoo_column_name='name'
    ))
    NAME = ('name', ColumnMapping(
        column_type='String',
        display_name='Name',
        odoo_column_name='partner_id'
    ))
    MEMO = ('memo', ColumnMapping(
        column_type='String',
        display_name='Memo/Description',
        odoo_column_name='ref'
    ))
    SPLIT_ACC = ('split_acc', ColumnMapping(
        column_type='String',
        display_name='Split',
        odoo_column_name='account_id'
    ))
    SUBT_NAT_AMOUNT = ('subt_nat_amount', ColumnMapping(
        column_type='Money',
        display_name='Amount',
        odoo_column_name='debit'
    ))
    RBAL_NAT_AMOUNT = ('rbal_nat_amount', ColumnMapping(
        column_type='Money',
        display_name='Balance',
        odoo_column_name='balance'
    ))
    ACCOUNT_NAME = ('account_name', ColumnMapping(
        column_type='String',
        display_name='Account',
        odoo_column_name='account_id'
    ))
    VEND_NAME = ('vend_name', ColumnMapping(
        column_type='String',
        display_name='Vendor',
        odoo_column_name='partner_id'
    ))
    KLASS_NAME = ('klass_name', ColumnMapping(
        column_type='String',
        display_name='Class',
        odoo_column_name='analytic_account_id'
    ))

    def __init__(self, column_name: str, mapping: ColumnMapping):
        self.column_name = column_name
        self.column_type = mapping.column_type
        self.display_name = mapping.display_name
        self.odoo_column_name = mapping.odoo_column_name

    @property
    def type(self) -> type:
        """Get the column type"""
        return self.column_type
    
    @classmethod
    def get_names(cls) -> list[str]:
        """Get list of all column names"""
        return [member.column_name for member in cls]

    @classmethod
    def get_type(cls, column_name: str) -> type:
        """Get type for a given column name"""
        for member in cls:
            if member.column_name == column_name:
                return member.column_type
        raise KeyError(f"Column {column_name} not found")
    
    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get mapping of column names to display names"""
        return {member.column_name: member.display_name for member in cls}
    
    @classmethod
    def get_types(cls) -> Dict[str, type]:
        """Get mapping of column names to types"""
        return {member.column_name: member.column_type for member in cls}
    
    @classmethod
    def get_display_name(cls, column_name: str) -> str:
        """Get display name for a given column name"""
        for member in cls:
            if member.column_name == column_name:
                return member.display_name
        raise KeyError(f"Column {column_name} not found")


    

