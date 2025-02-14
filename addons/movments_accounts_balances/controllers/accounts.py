import datetime
from odoo import http, fields
from odoo.http import request
from .common import APIResponse, validate_and_convert_data, get_request_data
from .utils import validate_company, validate_account
from .logger import logger
from ..swagger.common import swagger_doc
from ..swagger.accounts import accounts_docs
from .schemas.accounts import ACCOUNT_SCHEMA, AccountCreateRequestModel , AccountResponseModel, AccountModel, MetaDataModel, CurrencyRefModel

class AccountAPI(http.Controller):
    asset_method_types = ['asset_cash', 'asset_current']
    liability_method_types = ['liability_current', 'liability_credit_card']
    
    def get_journal_code(self, company_id):
        journals = request.env['account.journal'].sudo().search([('company_id', '=', company_id)])
        journal_count = len(journals)
        return f"J{journal_count + 1}"
    
    def create_payment_method_and_line(self, payment_method_data, payment_type):
        method = request.env['account.payment.method'].sudo().create({
            'name': f"{payment_method_data['name']} ({payment_type.capitalize()})",
            'code': f"{payment_method_data['code']}_{payment_type[:2]}",
            'payment_type': payment_type
        })
        
        line = request.env['account.payment.method.line'].sudo().create({
            'name': method.name,
            'payment_method_id': method.id,
            'journal_id': payment_method_data['journal_id'],
            'payment_account_id': payment_method_data['payment_account_id']
        })
        
        return method, line
    
    def create_payment_method(self, journal, account):
        payment_method_data = {
            'name': account['name'],
            'code': account['code'],
            'journal_id': journal.id,
            'payment_account_id': account.id
        }
        # Create inbound and outbound payment methods and their lines
        inbound_method, inbound_line = self.create_payment_method_and_line(payment_method_data, 'inbound')
        outbound_method, outbound_line = self.create_payment_method_and_line(payment_method_data, 'outbound')

    def create_journal(self, account, account_request_data):
        payment_method = account_request_data.get('PaymentMethod') if account_request_data.get('PaymentMethod') else 'none'
        if payment_method.lower() == 'none':
            if account_request_data['AccountType'].lower() == 'income':
                journal_type = 'sale'
            elif account_request_data['AccountType'].lower() == 'expense':
                journal_type = 'purchase'
            else:
                journal_type = 'general'
        elif account_request_data['AccountType'].lower() in self.liability_method_types:
            if payment_method.lower() == 'credit_card':
                journal_type = 'bank'
            else:
                raise ValueError('Invalid payment method for liability account')
        elif account_request_data['AccountType'].lower() in self.asset_method_types:
            if payment_method.lower() == 'cash':
                journal_type = 'cash'
            if payment_method.lower() == 'bank':
                journal_type = 'bank'
        else:
            raise ValueError('Invalid payment method')
        journal = request.env['account.journal'].sudo().create({
            'name': account.name,
            'code': self.get_journal_code(account.company_id.id),
            'type': journal_type,
            'company_id': account.company_id.id,
            'default_account_id': account.id,
        })
        if journal_type in ['cash', 'bank']:
            self.create_payment_method(journal, account)
        # return journal

    def create_account_vals(self, account_request_data, company_id, currency_id):
        return {
            'name': account_request_data['Name'],
            'code': account_request_data['AcctNum'],
            'account_type': account_request_data['AccountType'],
            'company_id': company_id,
            'currency_id': currency_id
        }
    
    def create_account_response(self, account):
        meta_data = MetaDataModel(
            CreateTime = account.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            LastUpdatedTime = account.write_date.strftime('%Y-%m-%d %H:%M:%S'),
        )
        if account.currency_id:
            currency_ref = CurrencyRefModel(
                name=account.currency_id.full_name,
                value=account.currency_id.name
            )
        else:
            currency_ref = None
        account = AccountModel(
            Id=account.id,
            Name=account.name,
            FullyQualifiedName=account.name,
            AccountType=account.account_type,
            Classification=account.internal_group,
            MetaData=meta_data,
            CurrencyRef=currency_ref,
            Active= not account.deprecated,
            AcctNum=account.code
        )
        return AccountResponseModel(
            Account=account,
            time=datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        ).to_dict()
    
    def validate_and_prepare_account_data(self, data, company_id, ACCOUNT_SCHEMA):
        # Validate company
        company = request.env['res.company'].sudo().browse(company_id)
        if not company.exists():
            return False, APIResponse.error_response(message='Company not found', errors='Invalid company_id', status=404)
                    
        success, converted_data = validate_and_convert_data(data, ACCOUNT_SCHEMA)
        if not success:
            logger.warning(f"Data validation failed: {converted_data}")
            return False, converted_data, converted_data
        
        # Convert request data 
        account_request_data = AccountCreateRequestModel(
            Name=converted_data['Name'],
            AcctNum=converted_data['AcctNum'],
            AccountType=converted_data['AccountType'],
            CurrencyRef=converted_data.get('CurrencyRef'),
            PaymentMethod=converted_data.get('PaymentMethod'),
        ).to_dict()

        currency_ref = account_request_data.get('CurrencyRef')
        currency_id = None
        if currency_ref:
            currency_value = currency_ref.get('value')
            currency = request.env['res.currency'].sudo().search([('name', '=', currency_value)], limit=1)
            if not currency:
                return False, APIResponse.error_response(message='Invalid currency', errors='Invalid currency_ref'), account_request_data
            currency_id = currency.id
            
        account_vals = self.create_account_vals(account_request_data, company_id, currency_id)
        return True, account_vals, account_request_data
        
    
    @http.route('/api/accounts', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(accounts_docs['create_account'])
    def create_account(self, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                logger.info("Processing create account request")
                data = get_request_data(request)
                logger.debug(f"Received data: {data}")
                
                company_id = int(request.httprequest.headers.get('CompanyId')) if request.httprequest.headers.get('CompanyId') else None
                if not company_id:
                    return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)

                success, account_vals, account_request_data = self.validate_and_prepare_account_data(data, company_id, ACCOUNT_SCHEMA)
                if success is not True:
                    return account_vals
                
                # Create the account
                account = request.env['account.account'].sudo().create(account_vals)
                self.create_journal(account, account_request_data)

                # # Handle opening balances if provided
                # opening_debit = float(converted_data.get('opening_debit')) if converted_data.get('opening_debit') else 0
                # opening_credit = float(converted_data.get('opening_credit')) if converted_data.get('opening_credit') else 0
                # if opening_debit or opening_credit:
                #     self.create_opening_balance(account, opening_debit, opening_credit, company_id)

                # Prepare response data
                response_data = self.create_account_response(account)
                return APIResponse.success_response(
                    message='Account created successfully',
                    data=response_data,
                    status=201
                )
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)

    
    def create_opening_balance(self, account, opening_debit, opening_credit, company_id):
        """
        Creates an opening balance journal entry for the given account.

        :param account: The account.account record for which the opening balance is being created.
        :param opening_debit: The opening debit value.
        :param opening_credit: The opening credit value.
        :param company_id: The ID of the company for the opening balance.
        """
        # Validate that only one of opening_debit or opening_credit is non-zero
        logger.info(f"Creating opening balance for account {account.code} - {account.name}")
        logger.debug(f"Opening balance details: debit={opening_debit}, credit={opening_credit}, company_id={company_id}")
        if opening_debit and opening_credit:
            logger.error("Both opening_debit and opening_credit provided")
            raise ValueError("Both opening_debit and opening_credit cannot be non-zero simultaneously.")
        
        if opening_debit < 0 or opening_credit < 0:
            logger.error(f"Invalid negative values: debit={opening_debit}, credit={opening_credit}")
            raise ValueError("Opening debit and credit values must be non-negative.")

        # Find the general journal for the company
        opening_journal = request.env['account.journal'].sudo().search([
            ('type', '=', 'general'),
            ('company_id', '=', company_id)
        ], limit=1)

        if not opening_journal:
            logger.error(f"No general journal found for company_id: {company_id}")
            raise ValueError("No general journal found for the specified company.")

        # Create the journal entry
        opening_move_vals = {
            'journal_id': opening_journal.id,
            'date': fields.Date.today(),
            'ref': f'Opening Balance for {account.code} - {account.name}',
            'move_type': 'entry',
            'line_ids': [
                (0, 0, {
                    'account_id': account.id,
                    'debit': opening_debit,
                    'credit': opening_credit,
                    'name': 'Opening Balance',
                    'move_name': f'OPEN/{account.code}',
                    'journal_id': opening_journal.id,
                    'balance': opening_debit - opening_credit,
                })
            ]
        }
        # If there's a difference, balance it with retained earnings account
        difference = opening_debit - opening_credit
        if difference != 0:
            retained_earnings_account = request.env['account.account'].sudo().search([
                ('company_id', '=', company_id),
                ('account_type', '=', 'equity_unaffected')
            ], limit=1)
            if not retained_earnings_account:
                raise ValueError("No retained earnings account found for the specified company.")
            opening_move_vals['line_ids'].append(
                (0, 0, {
                    'account_id': retained_earnings_account.id,
                    'debit': abs(difference),
                    'credit': abs(difference),
                    'name': 'Opening Balance - Retained Earnings',
                    'move_name': f'OPEN/{account.code}',
                    'journal_id': opening_journal.id,
                    'balance': abs(difference),
                })
            )
        opening_balance_entry = request.env['account.move'].sudo().create(opening_move_vals)
        opening_balance_entry.with_context(send_webhook=True).action_post()
    

    @http.route('/api/accounts', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(accounts_docs['list_accounts'])
    def list_accounts(self, account_type=None, company_id=None, deprecated=None, limit=20, offset=0, **kwargs):
        try:
            logger.info(f"Fetching accounts with parameters: account_type={account_type}, company_id={company_id}, deprecated={deprecated}")
            domain = []
            if account_type:
                # account_type = eval(account_type)
                domain.append(('account_type', '=', account_type))
                # domain.append(('internal_group', '=', account_type))
                logger.debug(f"Added account_type filter: {account_type}")
            if company_id:
                domain.append(('company_id', '=', int(company_id)))
                logger.debug(f"Added company_id filter: {company_id}")
            if deprecated is not None:
                deprecated = deprecated.lower() == 'true'
                domain.append(('deprecated', '=', deprecated))
                logger.debug(f"Added deprecated filter: {deprecated}")

            logger.debug(f"Final search domain: {domain}")
            limit = int(limit)
            offset = int(offset)

            # Get total count
            total_count = request.env['account.account'].sudo().search_count(domain)
            logger.info(f"Total matching accounts: {total_count}")

            # Search for accounts based on the domain with pagination
            accounts = request.env['account.account'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset
            )
            logger.info(f"Retrieved {len(accounts)} accounts")

            # Prepare the response data
            account_data = []
            for account in accounts:
                account_data.append({
                    'id': account.id,
                    'name': account.name,
                    'code': account.code,
                    'account_type': account.account_type,
                    'company': {
                        'id': account.company_id.id,
                        'name': account.company_id.name
                    } if account.company_id else None,
                    'create_date': account.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'deprecated': account.deprecated
                })
            response_data = {
                'accounts': account_data,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }

            return APIResponse.success_response(message='Accounts data retrieved successfully', data=response_data)
        except Exception as e:
            logger.error(f"Error in list_accounts: {str(e)}", exc_info=True)
            return APIResponse.error_response(message=f'An error occurred: {str(e)}', errors=f'{str(e)}', status=500)
        
    @http.route('/api/account-types', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_account_types(self, **kwargs):
        # Define the account types
        account_types = [
            {"code": "asset_receivable", "name": "Receivable"},
            {"code": "asset_cash", "name": "Bank and Cash"},
            {"code": "asset_current", "name": "Current Assets"},
            {"code": "asset_non_current", "name": "Non-current Assets"},
            {"code": "asset_prepayments", "name": "Prepayments"},
            {"code": "asset_fixed", "name": "Fixed Assets"},
            {"code": "liability_payable", "name": "Payable"},
            {"code": "liability_credit_card", "name": "Credit Card"},
            {"code": "liability_current", "name": "Current Liabilities"},
            {"code": "liability_non_current", "name": "Non-current Liabilities"},
            {"code": "equity", "name": "Equity"},
            {"code": "equity_unaffected", "name": "Current Year Earnings"},
            {"code": "income", "name": "Income"},
            {"code": "income_other", "name": "Other Income"},
            {"code": "expense", "name": "Expenses"},
            {"code": "expense_depreciation", "name": "Depreciation"},
            {"code": "expense_direct_cost", "name": "Cost of Revenue"},
            {"code": "off_balance", "name": "Off-Balance Sheet"},
        ]
        return APIResponse.success_response(message='Account types retrieved successfully', data=account_types)
    
    @http.route('/api/accounts/<int:account_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(accounts_docs['get_account'])
    def get_account(self, account_id):
        try:
            # Retrieve the account
            account = request.env['account.account'].sudo().browse(account_id)
            if not account.exists():
                return APIResponse.error_response(message='Account not found', errors='Invalid account_id', status=404)

            response_data = self.create_account_response(account)
            return APIResponse.success_response(message='Account retrieved successfully', data=response_data)
        except Exception as e:
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
    

    @http.route('/api/accounts/<int:account_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(accounts_docs['delete_account'])
    def delete_account(self, account_id, **kwargs):
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                company_id = int(kwargs.get('company_id')) if kwargs.get('company_id') else kwargs.get('company_id')
                if not company_id:
                    return APIResponse.error_response(message='Company ID not provided', errors='company_id is required')
                
                # Validate company
                is_valid, error_message = validate_company(request, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
                
                # Validate account
                is_valid, error_message = validate_account(request, account_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
                
                # Retrieve the account
                account = request.env['account.account'].sudo().browse(account_id)

                # Delete the account
                account.write({'deprecated': True})
                return APIResponse.success_response(message="Account deprecated successfully")
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)


# class ResponseCOA:
#     def __init__(self, account_id, account_number, parent_id, parent_number, level):
#         self.account_id = account_id
#         self.account_number = account_number
#         self.parent_id = parent_id
#         self.parent_number = parent_number
#         self.level = level