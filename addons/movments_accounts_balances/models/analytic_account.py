from odoo import models, api, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    _sql_constraints = [
        ('unique_analytic_account_combination', 
         'UNIQUE NULLS NOT DISTINCT (name, company_id)',
         'The combination of Name and Company must be unique!')
         ]