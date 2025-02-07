# from odoo import http
# from odoo.http import request
# import json
# from .common import validate_and_convert_data, APIResponse, get_request_data
# from .validation_schema import journal_expected_fields
# from .utils import validate_company

# from ..swagger.common import swagger_doc
# from ..swagger.journal import journals_docs
# from .schemas.journal import JOURNAL_SCHEMA

# class JournalController(http.Controller):

#     def validate_and_prepare_journal_data(self, data, invoice_expected_fields):
#         success, converted_data = validate_and_convert_data(data, invoice_expected_fields)
#         if success is not True:
#             return False, converted_data
        
#         # Validate company 
#         company_id = converted_data['company_id']
#         is_valid, error_message = validate_company(request, company_id)
#         if not is_valid:
#             return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
        
#         if len(converted_data.get('code')) > 5: 
#             return False, APIResponse.error_response(message='Journal code must be at most 5 characters long', errors='Journal code must be at most 5 characters long')

#         existing_journal = request.env['account.journal'].sudo().search([
#             ('name', '=', converted_data['name']),
#             ('company_id', '=', converted_data['company_id'])
#         ])
#         if existing_journal:
#             return False, APIResponse.error_response(message='Journal already exists', errors='Journal name should be unique for a company')
        
#         journal_data = {
#             'name': converted_data.get('name'),
#             'code': converted_data.get('code'),
#             'type': converted_data.get('type'),
#             'company_id': int(converted_data.get('company_id')),
#             'default_account_id': int(converted_data.get('default_account_id')) if converted_data.get('default_account_id') else None,
#             'profit_account_id': int(converted_data.get('profit_account_id')) if converted_data.get('profit_account_id') else None,
#             'loss_account_id': int(converted_data.get('loss_account_id')) if converted_data.get('loss_account_id') else None,
#             'bank_account_id': int(converted_data.get('bank_account_id')) if converted_data.get('bank_account_id') else None
#         }
#         # TODO Add 'bank_account_id': data.get('bank_account_id')
#         return True, journal_data
        

#     @http.route('/api/journals', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
#     @swagger_doc(journals_docs['create_journal'])
#     def create_journal(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)

#                 success, journal_data = self.validate_and_prepare_journal_data(data, JOURNAL_SCHEMA)
#                 if success is not True:
#                     return journal_data
                
#                 journal = request.env['account.journal'].sudo().create(journal_data)
#                 # prepare response data
#                 response_data = {
#                     'id': journal.id,
#                     'name': journal.name,
#                     'code': journal.code,
#                     'type': journal.type,
#                     'company': {
#                         'id': journal.company_id.id,
#                         'name': journal.company_id.name
#                     } if journal.company_id else None,
#                     'active': journal.active,
#                     'default_account': {
#                         'id': journal.default_account_id.id,
#                         'name': journal.default_account_id.name
#                     } if journal.default_account_id else None,
#                     'profit_account': {
#                         'id': journal.profit_account_id.id,
#                         'name': journal.profit_account_id.name
#                     } if journal.profit_account_id else None,
#                     'loss_account': {
#                         'id': journal.loss_account_id.id,
#                         'name': journal.loss_account_id.name
#                     } if journal.loss_account_id else None,
#                     'bank_account': {
#                         'id': journal.bank_account_id.id,
#                         'name': journal.bank_account_id.bank_id.name
#                     } if journal.bank_account_id else None
#                 }
#                 return APIResponse.success_response(message='Journal created successfully', data=response_data)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='An error occurred while creating journal', errors=str(e), status=500)
        

#     @http.route('/api/journals', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(journals_docs['list_journals'])
#     def get_journals(self, company_id, journal_type=None, active=None, limit=20, offset=0, **kwargs):
#         try:
#             domain = []
#             # Add filters to domain if provided
#             if active is not None:
#                 active = active.lower() == 'true'
#                 domain.append(('active', '=', active))
#             domain.append(('company_id', '=', int(company_id)))
#             if journal_type:
#                 domain.append(('type', '=', journal_type))

#             limit = int(limit)
#             offset = int(offset)
            
#             # Get total count for pagination
#             total_count = request.env['account.journal'].sudo().search_count(domain)
            
#             # Get journals with pagination
#             journals = request.env['account.journal'].sudo().search(
#                 domain, 
#                 limit=limit,
#                 offset=offset,
#                 order='name asc'
#             )

#             # Prepare response data
#             journals_list = [{
#                 'id': journal.id,
#                 'name': journal.name,
#                 'code': journal.code,
#                 'type': journal.type,
#                 'type_name': dict(journal._fields['type'].selection).get(journal.type),
#                 'company': {
#                     'id': journal.company_id.id,
#                     'name': journal.company_id.name
#                 } if journal.company_id else None,
#                 'active': journal.active,
#                 'default_account': {
#                     'id': journal.default_account_id.id,
#                     'name': journal.default_account_id.name,
#                     'code': journal.default_account_id.code
#                 } if journal.default_account_id else None,
#                 'profit_account': {
#                     'id': journal.profit_account_id.id,
#                     'name': journal.profit_account_id.name,
#                     'code': journal.profit_account_id.code
#                 } if journal.profit_account_id else None,
#                 'loss_account': {
#                     'id': journal.loss_account_id.id,
#                     'name': journal.loss_account_id.name,
#                     'code': journal.loss_account_id.code
#                 } if journal.loss_account_id else None,
#                 'bank_account': {
#                     'id': journal.bank_account_id.id,
#                     'acc_number': journal.bank_account_id.acc_number,
#                     'bank_name': journal.bank_account_id.bank_id.name
#                 } if journal.bank_account_id else None,
#                 'create_date': journal.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'write_date': journal.write_date.strftime('%Y-%m-%d %H:%M:%S')
#             } for journal in journals]

#             response_data = {
#                 'journals': journals_list,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }

#             return APIResponse.success_response(message='Journals retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message='An error occurred while retrieving journals', errors=str(e), status=500)

#     @http.route('/api/journals/<int:journal_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(journals_docs['get_journal'])
#     def get_journal_detail(self, journal_id, **kwargs):
#         try:
#             journal = request.env['account.journal'].sudo().browse(int(journal_id))
            
#             if not journal.exists():
#                 return APIResponse.error_response(message='Journal not found', errors='Journal not found', status=404)

#             # Prepare detailed journal information
#             journal_data = {
#                 'id': journal.id,
#                 'name': journal.name,
#                 'code': journal.code,
#                 'type': journal.type,
#                 'type_name': dict(journal._fields['type'].selection).get(journal.type),
#                 'company': {
#                     'id': journal.company_id.id,
#                     'name': journal.company_id.name
#                 } if journal.company_id else None,
#                 'active': journal.active,
#                 'bank_account': {
#                     'id': journal.bank_account_id.id,
#                     'acc_number': journal.bank_account_id.acc_number,
#                     'bank_name': journal.bank_account_id.bank_id.name
#                 } if journal.bank_account_id else None,
#                 'default_account': {
#                     'id': journal.default_account_id.id,
#                     'name': journal.default_account_id.name
#                 } if journal.default_account_id else None,
#                 'profit_account': {
#                     'id': journal.profit_account_id.id,
#                     'name': journal.profit_account_id.name
#                 } if journal.profit_account_id else None,
#                 'loss_account': {
#                     'id': journal.loss_account_id.id,
#                     'name': journal.loss_account_id.name
#                 } if journal.loss_account_id else None,
#                 'create_date': journal.create_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'write_date': journal.write_date.strftime('%Y-%m-%d %H:%M:%S')
#             }
#             return APIResponse.success_response(message='Journal retrieved successfully', data=journal_data)
#         except Exception as e:
#             return APIResponse.error_response(message='An error occurred while retrieving journal details', errors=str(e), status=500)
        
#     @http.route('/api/journals/<int:journal_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(journals_docs['delete_journal'])
#     def delete_journal(self, journal_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():

#                 journal = request.env['account.journal'].sudo().browse(journal_id)

#                 if not journal.exists():
#                     return APIResponse.error_response(message='Journal not found', errors='Journal not found', status=404)

#                 # journal.unlink()
#                 journal.write({'active': False}) 

#                 return APIResponse.success_response(message='Journal deactivated successfully')
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='An error occurred while deleting journal', errors=str(e), status=500)
        

#     @http.route('/api/journal_types', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
#     @swagger_doc(journals_docs['get_journal_types'])
#     def get_journal_types(self, **kwargs):
#         journal_types = [
#             {"code": "sale", "name": "Sales"},
#             {"code": "purchase", "name": "Purchase"},
#             {"code": "cash", "name": "Cash"},
#             {"code": "bank", "name": "Bank"},
#             {"code": "general", "name": "Miscellaneous"},
#         ]
#         return APIResponse.success_response(message='Journal types retrieved successfully', data=journal_types)
        
