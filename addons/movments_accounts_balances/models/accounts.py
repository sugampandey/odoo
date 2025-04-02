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

    _sql_constraints = [
        ('unique_account_combination', 
         'UNIQUE NULLS NOT DISTINCT (sub_type_code, account_number, name, account_type, company_id)',
         'The combination of Account Number, Name, Account Type, Company and Sub-type Code must be unique!')
         ]




