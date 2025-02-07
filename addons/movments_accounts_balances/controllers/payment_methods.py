# from odoo import http
# from odoo.http import request
# from .common import APIResponse, validate_and_convert_data, get_request_data
# from ..swagger.common import swagger_doc
# from ..swagger.payment_methods import payment_methods_docs
# from .schemas.payment_methods import PAYMENT_METHOD_SCHEMA

# class PaymentMethodController(http.Controller):

#     def validate_and_prepare_payment_method_data(self, data, payment_method_expected_fields):
#         success, converted_data = validate_and_convert_data(data, payment_method_expected_fields)
#         if success is not True:
#             return False, converted_data
        
#         journal_id = int(converted_data.get('journal_id'))
#         payment_account_id = int(converted_data.get('payment_account_id')) if converted_data.get('payment_account_id') else converted_data.get('payment_account_id')

#         # check account and journal is of same company
#         journal = request.env['account.journal'].sudo().browse(journal_id)
#         if not journal.exists():
#             return False, APIResponse.error_response(message="Bad Request for invalid data", errors="Journal does not exist")
        
#         if payment_account_id:
#             account = request.env['account.account'].sudo().browse(payment_account_id)
#             if account.exists():
#                 if journal.company_id != account.company_id:
#                     return False, APIResponse.error_response(message="Bad Request for invalid data", errors="Account and Journal are not of same company")
#             else:
#                 return False, APIResponse.error_response(message="Bad Request for invalid data", errors="Account does not exist")
        
#         method_line_data = {
#             'name': converted_data['name'],
#             'code' : converted_data.get('code') or converted_data['name'].lower().replace(' ', '_'),
#             'journal_id': journal_id,
#             'payment_account_id': payment_account_id
#         }
#         return True, method_line_data

        
#     @http.route('/api/payment-methods', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(payment_methods_docs['list_payment_methods'])
#     def get_payment_method(self, journal_id=None, payment_type=None, limit=20, offset=0, **kwargs):
#         try:
#             domain = []
#             if journal_id:
#                 domain.append(('journal_id', '=', int(journal_id)))
#             if payment_type:
#                 domain.append(('payment_method_id.payment_type', '=', payment_type))

#             limit = int(limit)
#             offset = int(offset)

#             # Get total count for pagination
#             total_count = request.env['account.payment.method.line'].sudo().search_count(domain)

#             # Get payment method lines with pagination
#             payment_method_lines = request.env['account.payment.method.line'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='id desc'
#             )
            
#             # Format the payment method lines data
#             payment_method_lines_data = []
#             for line in payment_method_lines:
#                 payment_method_lines_data.append({
#                     'id': line.id,
#                     'journal': {
#                     'id': line.journal_id.id,
#                     'name': line.journal_id.name,
#                     'type': line.journal_id.type,
#                     },
#                     'payment_method': {
#                         'id': line.payment_method_id.id,
#                         'name': line.payment_method_id.name,
#                         'code': line.payment_method_id.code,
#                         'type': line.payment_method_id.payment_type,
#                     },
#                     'payment_account': {
#                         'id': line.payment_account_id.id,
#                         'name': line.payment_account_id.name,
#                     } if line.payment_account_id else None,
#                 })
#             response_data = {
#                 'payment_methods': payment_method_lines_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }
#             return APIResponse.success_response(message='Payment method lines retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message="An error occurred while retrieving payment method lines", errors=str(e), status=500)
        
        
#     # Function to create payment method and its line
#     def create_payment_method_and_line(self, payment_method_data, payment_type):
#         method = request.env['account.payment.method'].sudo().create({
#             'name': f"{payment_method_data['name']} ({payment_type.capitalize()})",
#             'code': f"{payment_method_data['code']}_{payment_type[:2]}",
#             'payment_type': payment_type
#         })
        
#         line = request.env['account.payment.method.line'].sudo().create({
#             'name': method.name,
#             'payment_method_id': method.id,
#             'journal_id': payment_method_data['journal_id']
#         })
        
#         return method, line
        
#     @http.route('/api/payment-methods/', type='http', auth='public', methods=['POST'], csrf=False)
#     @swagger_doc(payment_methods_docs['create_payment_method'])
#     def add_payment_method(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)
#                 success, payment_method_data = self.validate_and_prepare_payment_method_data(data, PAYMENT_METHOD_SCHEMA)
#                 if success is not True:
#                     return payment_method_data
                
#                 # Create inbound and outbound payment methods and their lines
#                 inbound_method, inbound_line = self.create_payment_method_and_line(payment_method_data, 'inbound')
#                 outbound_method, outbound_line = self.create_payment_method_and_line(payment_method_data, 'outbound')
#                 response_data = {
#                     'inbound': {
#                         'method': {
#                             'id': inbound_method.id,
#                             'name': inbound_method.name,
#                             'code': inbound_method.code,
#                             'payment_type': inbound_method.payment_type,
#                         },
#                         'method_line': {
#                             'id': inbound_line.id,
#                             'name': inbound_line.name,
#                             'journal_id': inbound_line.journal_id.id,
#                         }
#                     },
#                     'outbound': {
#                         'method': {
#                             'id': outbound_method.id,
#                             'name': outbound_method.name,
#                             'code': outbound_method.code,
#                             'payment_type': outbound_method.payment_type,
#                         },
#                         'method_line': {
#                             'id': outbound_line.id,
#                             'name': outbound_line.name,
#                             'journal_id': outbound_line.journal_id.id,
#                         }
#                     }
#                 }
#                 return APIResponse.success_response(message='Payment method added successfully', data=response_data, status=201)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)

        
#     @http.route('/api/payment-methods/<int:payment_method_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(payment_methods_docs['delete_payment_method'])
#     def delete_payment_method(self, payment_method_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 payment_method = request.env['account.payment.method'].sudo().browse(payment_method_id)
#                 # Check if the payment method exists
#                 if not payment_method.exists():
#                     return APIResponse.error_response(message='Payment method not found', errors='Payment method not found', status=404)

#                 # Check if the payment method is being used in payment method lines
#                 payment_method_lines = request.env['account.payment.method.line'].sudo().search([
#                     ('payment_method_id', '=', payment_method_id)
#                 ])
                
#                 # Delete method lines first to avoid constraint errors
#                 if payment_method_lines:
#                     payment_method_lines.unlink()

#                 # Delete the payment method
#                 payment_method.unlink()

#                 return APIResponse.success_response(message='Payment method deleted successfully')
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        

# class BankPaymentMethodController(http.Controller):

#     @http.route('/api/banks', type='http', auth='public', methods=['POST'], csrf=False)
#     @swagger_doc(banks_docs['create_bank'])
#     def add_bank_details(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)
#                 success, converted_data = validate_and_convert_data(data, BANK_SCHEMA)
#                 if not success:
#                     return converted_data
#                 bank_data = {
#                     'name': converted_data.get('name'),
#                     'bic': converted_data.get('bic'),
#                 }
#                 bank = request.env['res.bank'].sudo().create(bank_data)
#                 bank_response = {
#                     'id': bank.id,
#                     'name': bank.name,
#                     'bic': bank.bic,
#                 }
#                 return APIResponse.success_response(message='Bank details added successfully', data=bank_response, status=201)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
#     @http.route('/api/banks', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(banks_docs['list_banks'])
#     def get_banks(self, active=None, limit=20, offset=0, **kwargs):
#         try:
#             domain = []
#             limit = int(limit)
#             offset = int(offset)
#             if active is not None:
#                 active = active.lower() == 'true'
#                 domain.append(('active', '=', active))

#             # Get total count for pagination
#             total_count = request.env['res.bank'].sudo().search_count(domain)

#             # Get banks with pagination
#             banks = request.env['res.bank'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='name asc'
#             )

#             # Format the banks data
#             banks_data = []
#             for bank in banks:
#                 banks_data.append({
#                     'id': bank.id,
#                     'name': bank.name,
#                     'bic': bank.bic,
#                     'active': bank.active,
#                     'email': bank.email,
#                     'phone': bank.phone,
#                 })
#             response_data = {
#                 'banks': banks_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }
#             return APIResponse.success_response(message='Banks retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
#     @http.route('/api/banks/<int:bank_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(banks_docs['get_bank'])
#     def get_bank_details(self, bank_id, **kwargs):
#         try:
#             bank = request.env['res.bank'].sudo().browse(bank_id)
#             if not bank.exists():
#                 return APIResponse.error_response(message='Bank not found', errors='Bank not found', status=404)

#             # Format the bank details data
#             bank_data = {
#                 'id': bank.id,
#                 'name': bank.name,
#                 'bic': bank.bic,
#                 'active': bank.active,
#                 'email': bank.email,
#                 'phone': bank.phone,
#             }
#             return APIResponse.success_response(message='Bank details retrieved successfully', data=bank_data)
#         except Exception as e:
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
#     @http.route('/api/banks/<int:bank_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(banks_docs['delete_bank'])
#     def delete_bank(self, bank_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 bank = request.env['res.bank'].sudo().browse(bank_id)
#                 # Check if the bank exists
#                 if not bank.exists():
#                     return APIResponse.error_response(message='Bank not found', errors='Bank not found', status=404)

#                 # Check if the bank is being used in bank accounts
#                 bank_accounts = request.env['res.partner.bank'].sudo().search([
#                     ('bank_id', '=', bank_id)
#                 ])
#                 if bank_accounts:
#                     return APIResponse.error_response(message='Cannot delete bank as it is being used in bank accounts', errors='Cannot delete bank as it is being used in bank accounts')

#                 # Delete the bank
#                 # bank.unlink()
#                 bank.write({'active': False})
#                 return APIResponse.success_response(message='Bank deactivated successfully')
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        

#     def validate_and_prepare_bank_account_data(self, data, bank_account_expected_fields):

#         success, converted_data = validate_and_convert_data(data, bank_account_expected_fields)
#         if success is not True:
#             return converted_data

#         # Prepare bank account data
#         bank_account_data = {
#             'acc_number': data.get('acc_number'),
#             'partner_id': int(data.get('partner_id')),
#             'bank_id': int(data.get('bank_id')),
#             'acc_holder_name': data.get('acc_holder_name'),
#             'company_id': int(data.get('company_id')),
#         }
#         return True, bank_account_data


#     @http.route('/api/bank-accounts', type='http', auth='public', methods=['POST'], csrf=False)
#     @swagger_doc(bank_accounts_docs['create_bank_account'])
#     def add_bank_accounts(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)

#                 success, account_data = self.validate_and_prepare_bank_account_data(data, BANK_ACCOUNT_SCHEMA)
#                 if success is not True:
#                     return account_data

#                 account = request.env['res.partner.bank'].sudo().create(account_data)
#                 account_response = {
#                     'id': account.id,
#                     'acc_number': account.acc_number,
#                     'acc_holder_name': account.acc_holder_name,
#                 }
#                 return APIResponse.success_response(message='Bank account added successfully', data=account_response, status=201) 
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        

#     @http.route('/api/bank-accounts/<int:account_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(bank_accounts_docs['get_bank_account'])
#     def get_bank_account_details(self, account_id, **kwargs):
#         try:
#             account = request.env['res.partner.bank'].sudo().browse(account_id)
#             if not account.exists():
#                 return APIResponse.error_response(message='Account not found', errors='Account not found', status=404)
            
#             # Format the bank account details data
#             account_data = {
#                 'id': account.id,
#                 'acc_number': account.acc_number,
#                 'acc_holder_name': account.acc_holder_name,
#                 'bank':{
#                     'id': account.bank_id.id,
#                     'name': account.bank_id.name,
#                     'bic': account.bank_id.bic
#                 } if account.bank_id else None,
#                 'partner': {
#                     'id': account.partner_id.id,
#                     'name': account.partner_id.name,
#                 } if account.partner_id else None,
#                 'company': {
#                     'id': account.company_id.id,
#                     'name': account.company_id.name,
#                 } if account.company_id else None,
#                 'active': account.active,
#                 'create_date': account.create_date.strftime('%Y-%m-%d %H:%M:%S')
#             }
#             return APIResponse.success_response(message='Bank account details retrieved successfully', data=account_data)
#         except Exception as e:
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
#     @http.route('/api/bank-accounts/<int:account_id>', type='http', auth='public', methods=['POST'], csrf=False)
#     def update_bank_accounts(self, account_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 # First check if account exists
#                 account = request.env['res.partner.bank'].sudo().browse(account_id)
#                 if not account.exists():
#                     return APIResponse.error_response(message='Account not found', errors='Account not found', status=404)
                
#                 data = request.params
#                 field_mapping = {
#                     'account_number': ('acc_number', str),
#                     'partner_id': ('partner_id', int),
#                     'bank_id': ('bank_id', int),
#                     'account_holder_name': ('acc_holder_name', str),
#                     'company_id': ('company_id', int),
#                     'active': ('active', bool)
#                 }

#                 account_data = {}
#                 # Build update data only for provided fields
#                 for param_field, (db_field, field_type) in field_mapping.items():
#                     if param_field in data:
#                             account_data[db_field] = field_type(data[param_field])
                
#                 # If no valid fields to update
#                 if not account_data:
#                     return APIResponse.format(
#                         success=False,
#                         message='No valid fields to update',
#                         errors='Request must contain at least one valid field to update',
#                         status=400
#                     )
                
#                 account = request.env['res.partner.bank'].sudo().browse(account_id)
#                 # Update the account
#                 account.write(account_data)

#                 # Prepare response data
#                 response_data = {
#                     'id': account.id,
#                     'acc_number': account.acc_number,
#                     'acc_holder_name': account.acc_holder_name,
#                     'partner': {
#                         'id': account.partner_id.id,
#                         'name': account.partner_id.name
#                     } if account.partner_id else None,
#                     'bank': {
#                         'id': account.bank_id.id,
#                         'name': account.bank_id.name,
#                         'bic': account.bank_id.bic
#                     } if account.bank_id else None,
#                     'company': {
#                         'id': account.company_id.id,
#                         'name': account.company_id.name
#                     } if account.company_id else None,
#                     'active': account.active,
#                     'write_date': account.write_date.strftime('%Y-%m-%d %H:%M:%S')
#                 }
#                 return APIResponse.format(
#                     success=True,
#                     message='Bank account updated successfully',
#                     data=response_data,
#                     status=200
#                 )
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.format(
#                 success=False,
#                 message=str(e),
#                 errors=str(e),
#                 status=500
#             )
        
#     @http.route('/api/bank-accounts', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(bank_accounts_docs['list_bank_accounts'])
#     def get_bank_accounts(self, partner_id=None, company_id=None, bank_id=None, active=None, limit=20, offset=0, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 domain = []
                
#                 # Add filters to domain if provided
#                 if company_id:
#                     is_valid, error_message = validate_company(request, company_id)
#                     if not is_valid:
#                         return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
#                     domain.append(('company_id', '=', int(company_id)))
#                 if partner_id:
#                     is_valid, error_message = validate_partner(request, partner_id)
#                     if not is_valid:
#                         return APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')
#                     domain.append(('partner_id', '=', int(partner_id)))
#                 if bank_id:
#                     is_valid, error_message = validate_bank(request, bank_id)
#                     if not is_valid:
#                         return APIResponse.error_response(f'Invalid bank: {error_message}', f'Invalid bank_id: {bank_id}')
#                     domain.append(('bank_id', '=', int(bank_id)))
#                 if active is not None:
#                     active = active.lower() == 'true'
#                     domain.append(('active', '=', active))

#                 limit = int(limit)
#                 offset = int(offset)

#                 # Get total count for pagination
#                 total_count = request.env['res.partner.bank'].sudo().search_count(domain)

#                 # Get bank accounts with pagination
#                 bank_accounts = request.env['res.partner.bank'].sudo().search(
#                     domain,
#                     limit=limit,
#                     offset=offset,
#                     order='id desc'
#                 )

#                 # Prepare response data
#                 accounts_data = [{
#                     'id': account.id,
#                     'acc_number': account.acc_number,
#                     'acc_holder_name': account.acc_holder_name,
#                     'active': account.active,
#                     'partner': {
#                         'id': account.partner_id.id,
#                         'name': account.partner_id.name
#                     } if account.partner_id else None,
#                     'bank': {
#                         'id': account.bank_id.id,
#                         'name': account.bank_id.name,
#                         'bic': account.bank_id.bic
#                     } if account.bank_id else None,
#                     'company': {
#                         'id': account.company_id.id,
#                         'name': account.company_id.name
#                     } if account.company_id else None,
#                     'create_date': account.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 } for account in bank_accounts]

#                 response_data = {
#                     'bank_accounts': accounts_data,
#                     'pagination': {
#                         'total_count': total_count,
#                         'limit': limit,
#                         'offset': offset
#                     }
#                 }
#                 return APIResponse.success_response(message='Bank accounts retrieved successfully', data=response_data)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        
#     @http.route('/api/bank-accounts/<int:account_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(bank_accounts_docs['delete_bank_account'])
#     def delete_bank_accounts(self, account_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 account = request.env['res.partner.bank'].sudo().browse(account_id)
#                 # Check if the account exists
#                 if not account.exists():
#                     return APIResponse.error_response(message='Account not found', errors='Account not found', status=404)

#                 # Store some info for the response before deletion
#                 response_data = {
#                     'id': account.id,
#                     'acc_number': account.acc_number,
#                     'acc_holder_name': account.acc_holder_name,
#                 }

#                 # Delete the account
#                 account.write({'active': False})

#                 return APIResponse.success_response(message='Bank account deactivated successfully', data=response_data)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message=str(e), errors=str(e), status=500)
        

    