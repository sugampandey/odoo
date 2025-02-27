from odoo.exceptions import UserError
from ..constants import CONSTANTS

def validate_account(request, account_id, company_id, valid_account_types=None):
    """
    Validate account based on allowed account types
    Args:
        account_id: ID of the account to validate
        company_id: ID of the company
        valid_account_types: List of allowed account types. 
                        If None, no account type validation is performed
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if valid_account_types is None:
        valid_account_types = []
        
    account = request.env['account.account'].sudo().browse(account_id)
    
    # Basic validations
    if not account.exists():
        return False, "Account does not exist"
        
    if account.company_id.id != int(company_id):
        return False, "Account belongs to different company"
        
    if account.deprecated:
        return False, "Selected account is deprecated"
        
    # Account type validation if types are specified
    if valid_account_types and account.account_type not in valid_account_types:
        return False, f"Invalid account type. Expected one of: {', '.join(valid_account_types)}"
        
    return True, ""


def validate_partner(request, partner_id, company_id):
    """
    Validate partner based on company association
    Args:
        partner_id: ID of the partner to validate
        company_id: ID of the company
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    partner = request.env['res.partner'].sudo().browse(int(partner_id))

    # Basic validations
    if not partner.exists():
        return False, "Partner does not exist"

    if partner.company_id and partner.company_id.id != int(company_id):
        return False, "Partner is not associated with the provided company"
    
    if partner.active == False:
        return False, "Partner is not active"

    return True, ""


def validate_company(request, company_id):
    """
    Validate company existence
    Args:
        company_id: ID of the company to validate
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    company = request.env['res.company'].sudo().browse(int(company_id))
    if not company.exists():
        return False, "Company does not exist"
    if company.active == False:
        return False, "Company is not active"
    return True, ""
    

def validate_product(request, product_id, company_id):
    """
    Validate product based on company association
    Args:
        product_id: ID of the product to validate
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    product = request.env['product.product'].sudo().browse(int(product_id))

    # Basic validations
    if not product.exists():
        return False, "Product does not exist"
    
    if product.product_tmpl_id.company_id:
        if product.product_tmpl_id.company_id.id != int(company_id):
            return False, "Product belongs to different company"
    
    if product.active == False:
        return False, "Product is not active"

    return True, ""
    

def validate_tax(request, tax_id, company_id):
    """
    Validate tax based on company association
    Args:
        tax_id: ID of the tax to validate
        company_id: ID of the company
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    tax = request.env['account.tax'].sudo().browse(int(tax_id))

    # Basic validations
    if not tax.exists():
        return False, "Tax does not exist"

    if tax.company_id.id != int(company_id):
        return False, "Tax belongs to different company"
    
    if tax.active == False:
        return False, "Tax is not active"

    return True, ""

def validate_journal(request, journal_id, company_id):
    journal = request.env['account.journal'].sudo().browse(int(journal_id))
    if not journal.exists():
        return False, 'Journal not found'
    if journal.company_id.id != int(company_id):
        return False, 'Journal belongs to different company'
    if journal.active == False:
        return False, 'Journal is not active'
    return True, ""

def validate_bank(request, bank_id):
    bank = request.env['res.bank'].sudo().browse(int(bank_id))
    if not bank.exists():
        return False, 'Bank not found'
    if bank.active == False:
        return False, 'Bank is not active'
    return True, ""

def validate_analytic_plan(request, plan_id):
    plan = request.env['account.analytic.plan'].sudo().browse(int(plan_id))
    if not plan.exists():
        return False, 'Plan not found'
    return True, ""

def validate_analytic_account(request, analytic_account_id, company_id):
    analytic_account = request.env['account.analytic.account'].sudo().browse(int(analytic_account_id))
    if not analytic_account.exists():
        return False, f"Analytic account with id {analytic_account_id} does not exist"
    if analytic_account.company_id.id != int(company_id):
        return False, f"Analytic account with id {analytic_account_id} does not belong to the specified company"
    return True, ""


def validate_partner_category(request, category_id):
    category = request.env['res.partner.category'].sudo().browse(category_id)
    if not category.exists():
        return False, 'Category not found'
    if category.active == False:
        return False, 'Category is not active'
    return True, ""

def validate_tax_group(request, tax_group_id):
    tax_group = request.env['account.tax.group'].sudo().browse(int(tax_group_id))
    if not tax_group.exists():
        return False, 'Tax group not found'
    return True, ""


def get_payment_method_line(request, outstanding_account_id, payment_type):
    domain = [
        ('payment_method_id.payment_type', '=', payment_type), 
        ('payment_account_id', '=', outstanding_account_id)
        ]
    payment_method_line = request.env['account.payment.method.line'].sudo().search(domain, limit=1)
    if not payment_method_line.exists():
        raise UserError("Payment method not found.")
    return payment_method_line


def get_default_product(request, company_id):
    domain = [
        ('product_tmpl_id.company_id', '=', int(company_id)),
        ('default_code', '=', CONSTANTS['PRODUCT_DEFAULT_CODE'])
    ]
    default_product = request.env['product.product'].sudo().search(domain, limit=1)
    return default_product

def get_default_vendor_category(request):
    return request.env['res.partner.category'].sudo().search([
        ('name', '=', CONSTANTS['VENDOR_CATEGORY_NAME'])
    ], limit=1).id
    
def get_default_customer_category(request):
    return request.env['res.partner.category'].sudo().search([
        ('name', '=', CONSTANTS['CUSTOMER_CATEGORY_NAME'])
    ], limit=1).id