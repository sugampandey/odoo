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




