from odoo import models, api, fields


# Mapping 
# display_name - DisplayName
# title - title
# name - GivenName,
# company_name - CompanyName
# phone - PrimaryPhone
# mobile - Mobile
# email - PrimaryEmailAddr
# street - BillAddr-line1
# street2 - BillAddr-line2
# zip - BillAddr-PostalCode
# city - BillAddr-City
# state - BillAddr - CountrySubDivisionCode
# country_id - BillAddr - Country
# active - Active
# vendor_1099 - Vendor1099 - New column


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_1099 = fields.Char('Vendor1099', required=False, tracking=True)

    _sql_constraints = [
        ('unique_partner_combination', 
         'UNIQUE NULLS NOT DISTINCT (name, company_id, email, company_name)',
         'The combination of Name, Company, Company Name and Email must be unique!')
         ]