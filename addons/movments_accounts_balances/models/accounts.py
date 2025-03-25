from typing import Any, Dict, Optional
import uuid

from ..common import validate_and_convert_data
from ..controllers.accounts import ACCOUNT_TYPE_MAPPING, TYPE_PREFIX_MAPPING
from odoo import models, api, fields


# column mapping 
# name - name
# acc_type - account_type
# acc_type_name - blank
# classification - internal_group	
# sub_type_code - sub_type_code
# number-account_number
# code - code

class AccountMove(models.Model):
    _inherit = "account.account"

    account_number = fields.Char(size=128, required=False, tracking=True)
    sub_type_name = fields.Char(string="Sub Type Name", required=False, tracking=True)
    sub_type_code = fields.Char(size=128, required=False, tracking=True)

    # _sql_constraints = [
    #     ('unique_account_number_company',
    #      'unique (account_number, company_id)',
    #      'Account number must be unique per company!'),
    #     ('unique_sub_type_code_company',  
    #      'unique (sub_type_code, company_id)',
    #      'Sub type code must be unique per company!')
    # ]
    _sql_constraints = [
        ('unique_account_combination', 
         'UNIQUE NULLS NOT DISTINCT (sub_type_code, account_number, name, account_type, company_id)',
         'The combination of Account Number, Name, Account Type, Company and Sub-type Code must be unique!')
         ]


# extra db calls
class AccountCreateDTO(models.TransientModel):
    _name = 'account.create.dto'
    _description = 'Account Create DTO'

    name = fields.Char(required=True)
    account_type = fields.Char(required=True)
    acct_num = fields.Char(required=True)
    currency_ref_id = fields.Many2one('currency.ref', string='Currency Reference')
    account_subtype = fields.Char()
    company_id = fields.Integer(required=True)

    def get_unique_account_code(self, account_type):
        # Create a prefix based on account type
        type_prefix = TYPE_PREFIX_MAPPING.get(account_type, 'GN')  # GN as default prefix
        
        # Generate full UUID
        unique_id = str(uuid.uuid4()).replace('-', '.')
        
        # Format: PREFIX-UUID (e.g., AR.550e8400.e29b.41d4.a716.446655440000)
        return f"{type_prefix}.{unique_id}"
    

    def validate(self, data, schema):
        success, converted_data = validate_and_convert_data(data, schema)
    
    @api.model
    def create(
        self,
        Name: str,
        AcctNum: str,
        AccountType: str,
        AccountSubType: Optional[str] = None,
        CurrencyRef: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Create a transient record for account request"""
        # Create currency reference if provided
        currency_id = None
        if CurrencyRef:
            currency_value = CurrencyRef.get('value', 'USD')
            currency = self.env['res.currency'].sudo().search([('name', '=', currency_value)], limit=1)
            if not currency:
                raise ValueError('Could not find currency')
            currency_id = currency.id

        account_type = self.get_account_type(AccountType)
        values = {
            'name': Name,
            'code': self.get_unique_account_code(account_type),
            'account_number': AcctNum,
            'account_type': account_type,
            'sub_type_code': AccountSubType,
            'company_id': company_id,
            'currency_id': currency_id
        }
        account = self.env['account.account'].sudo().create(values)
        return self.to_dict(account)
    
    def get_account_type(self, account_type: str) -> str:
        return ACCOUNT_TYPE_MAPPING.get(account_type)

    def to_dict(self, account) -> Dict[str, Any]:
        """Convert the transient record to dictionary format"""
        return {
            'Name': account.name,
            'AcctNum': account.account_number,
            'AccountType': account.account_type,
            'AccountSubType': account.sub_type_code,
            'CurrencyRef': account.currency_ref_id.to_dict() if account.currency_ref_id else None,
        }


