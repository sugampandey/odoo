# from odoo import http
# from odoo.http import request
# import json
# from .common import APIResponse, validate_and_convert_data, get_request_data
# from .validation_schema import tax_expected_fields, tax_group_expected_fields
# from .utils import validate_company, validate_tax_group, validate_tax

# from ..swagger.common import swagger_doc
# from ..swagger.tax import tax_groups_docs, tax_docs
# from .schemas.tax import TAX_GROUP_SCHEMA, TAX_SCHEMA

# class TaxController(http.Controller):

#     @http.route('/api/type_tax_use', type='http', auth='public', methods=['GET'], csrf=False)
#     def get_type_tax_use(self, **kwargs):
#         data = [
#             {"code": "sale", "name": "Sales"},
#             {"code": "purchase", "name": "Purchase"},
#             {"code": "none", "name": "None"},
#         ]
#         return APIResponse.success_response(message="Tax type retrieved successfully", data=data)
    
#     @http.route('/api/tax_scope', type='http', auth='public', methods=['GET'], csrf=False)
#     def get_tax_scope(self, **kwargs):
#         data = [
#             {"code": 'service', "name": 'Services'},
#             {"code": 'consu', "name": 'Goods'},
#         ]
#         return APIResponse.success_response(message="Tax scope retrieved successfully", data=data)
    
#     @http.route('/api/tax_exigibility', type='http', auth='public', methods=['GET'], csrf=False)
#     def get_tax_exigibility(self, **kwargs):
#         data = [
#             {'code': 'on_invoice', 'name': 'Based on Invoice'},
#             {'code': 'on_payment', 'name': 'Based on Payment'},
#         ]
#         return APIResponse.success_response(message="Tax exigibility retrieved successfully", data=data)
    
#     @http.route('/api/amount_type', type='http', auth='public', methods=['GET'], csrf=False)
#     def get_amount_type(self, **kwargs):
#         data = [
#             {'code': 'group', 'name': 'Group of Taxes'},
#             {'code': 'fixed', 'name': 'Fixed'},
#             {'code': 'percent', 'name': 'Percentage of Price'},
#             {'code': 'division', 'name': 'Percentage of Price Tax Included'}
#         ]
#         return APIResponse.success_response(message="Amount type retrieved successfully", data=data)
    
#     def validate_and_prepare_tax_data(self, data, tax_expected_fields):
#         success, converted_data = validate_and_convert_data(data, tax_expected_fields)
#         if success is not True:
#             return False, converted_data

#         # Validate company if provided
#         company_id = converted_data.get('company_id')
#         if company_id:
#             is_valid, error_message = validate_company(request, company_id)
#             if not is_valid:
#                 return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')

#         # Validate tax group existence
#         tax_group_id = converted_data.get('tax_group_id')
#         if tax_group_id:
#             is_valid, error_message = validate_tax_group(request, tax_group_id)
#             if not is_valid:
#                 return False, APIResponse.error_response(f'Invalid tax group: {error_message}', f'Invalid tax_group_id: {tax_group_id}')
        
#         # Validate tax amount range
#         if converted_data['amount_type'] == 'percent' and (converted_data['amount'] < 0 or converted_data['amount'] > 100):
#             return False, APIResponse.error_response('Tax percentage must be between 0 and 100', 'Invalid tax amount')

#         # Validate tax name uniqueness
#         existing_tax = request.env['account.tax'].sudo().search([
#             ('name', '=', converted_data['name']),
#             ('company_id', '=', converted_data.get('company_id', False))
#         ])
#         if existing_tax:
#             return False, APIResponse.error_response('Tax with this name already exists', 'Duplicate tax name')
        
#         return True, converted_data
    
#     @http.route('/api/taxes', type='http', auth='public', methods=['POST'], csrf=False)
#     @swagger_doc(tax_docs['create_tax'])
#     def add_tax(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)
#                 tax_types = ['sale', 'purchase', 'none']
#                 created_taxes = []

#                 success, converted_data = self.validate_and_prepare_tax_data(data, TAX_SCHEMA)
#                 if success is not True:
#                     return converted_data
                
#                 for tax_type in tax_types:
#                     # Create a copy of the converted data for each tax type
#                     tax_data = dict(converted_data)
                    
#                     # Modify the name and type_tax_use for each tax
#                     tax_data['name'] = f"{tax_data['name']} ({tax_type.capitalize()})"
#                     tax_data['type_tax_use'] = tax_type

#                     # Create tax record
#                     tax = request.env['account.tax'].sudo().create(tax_data)

#                     # Prepare response data with tax group information
#                     tax_info = {
#                         'id': tax.id,
#                         'name': tax.name,
#                         'amount': tax.amount,
#                         'amount_type': tax.amount_type,
#                         'type_tax_use': tax.type_tax_use,
#                         'description': tax.description,
#                     }
#                     created_taxes.append(tax_info)
#                 return APIResponse.success_response(message="Tax created successfully", data=created_taxes)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message="An error occurred while processing the request", errors=str(e), status=500)
        

#     @http.route('/api/taxes', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(tax_docs['list_taxes'])
#     def get_taxes(self, company_id, type_tax_use=None, tax_group_id=None, 
#                   active=None, limit=20, offset=0, search=None, **kwargs):
#         try:
#             domain = []
#             is_valid, error_message = validate_company(request, company_id)
#             if not is_valid:
#                 return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
#             domain.append(('company_id', '=', int(company_id)))
#             if active:
#                 active = active.lower() == 'true'
#                 domain.append(('active', '=', active))                
#             if type_tax_use:
#                 domain.append(('type_tax_use', '=', type_tax_use))
#             if tax_group_id:
#                 is_valid, error_message = validate_tax_group(request, tax_group_id)
#                 if not is_valid:
#                     return APIResponse.error_response(f'Invalid tax group: {error_message}', f'Invalid tax_group_id: {tax_group_id}')
#                 domain.append(('tax_group_id', '=', int(tax_group_id)))

#             limit = int(limit)
#             offset = int(offset)
            
#             # Get total count for pagination
#             total_count = request.env['account.tax'].sudo().search_count(domain)

#             # Get taxes
#             taxes = request.env['account.tax'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='sequence, name'
#             )
            
#             taxes_data = [{
#                 'id': tax.id,
#                 'name': tax.name,
#                 'amount': tax.amount,
#                 'amount_type': tax.amount_type,
#                 'type_tax_use': tax.type_tax_use,
#                 'description': tax.description,
#                 'active': tax.active,
#                 'company': {
#                     'id': tax.company_id.id,
#                     'name': tax.company_id.name
#                 } if tax.company_id else None,
#                 'sequence': tax.sequence,
#                 'price_include': tax.price_include,
#                 'tax_group': {
#                     'id': tax.tax_group_id.id,
#                     'name': tax.tax_group_id.name
#                 } if tax.tax_group_id else None,
#             } for tax in taxes]

#             response_data = {
#                 'taxes': taxes_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }
#             return APIResponse.success_response(message="Taxes retrieved successfully", data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message="An error occurred while processing the request", errors=str(e), status=500)

#     @http.route('/api/taxes/<int:tax_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(tax_docs['get_tax'])
#     def get_tax(self, tax_id, **kwargs):
#         try:
#             tax = request.env['account.tax'].sudo().browse(tax_id)
#             if not tax.exists():
#                 return APIResponse.error_response('Tax not found', 'Tax not found', status=404)
#             # is_valid, error_message = validate_tax(request, tax_id)
#             # if not is_valid:
#             #     return APIResponse.error_response(f'Invalid tax: {error_message}', f'Invalid tax_id: {tax_id}')
            
#             # tax = request.env['account.tax'].sudo().browse(tax_id)

#             tax_data = {
#                 'id': tax.id,
#                 'name': tax.name,
#                 'amount': tax.amount,
#                 'amount_type': tax.amount_type,
#                 'type_tax_use': tax.type_tax_use,
#                 'description': tax.description,
#                 'active': tax.active,
#                 'company': {
#                     'id': tax.company_id.id,
#                     'name': tax.company_id.name
#                 } if tax.company_id else None,
#                 'sequence': tax.sequence,
#                 'price_include': tax.price_include,
#                 'tax_group': {
#                     'id': tax.tax_group_id.id,
#                     'name': tax.tax_group_id.name,
#                 } if tax.tax_group_id else None,
#             }
#             return APIResponse.success_response(message="Tax retrieved successfully", data=tax_data)
#         except Exception as e:
#             return APIResponse.error_response(message="An error occurred while processing the request", errors=str(e), status=500)

#     @http.route('/api/taxes/<int:tax_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     def update_tax(self, tax_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 tax = request.env['account.tax'].sudo().browse(tax_id)
#                 if not tax.exists():
#                     return APIResponse.format(
#                         success=False,
#                         message='Tax not found',
#                         errors='Tax not found',
#                         status=404
#                     )

#                 data = request.params
#                 update_data = {}

#                 # Fields that can be updated
#                 allowed_fields = {
#                     'name': str,
#                     'amount': float,
#                     'amount_type': str,
#                     'type_tax_use': str,
#                     'description': str,
#                     'active': bool,
#                     'sequence': int,
#                     'price_include': bool,
#                     'tax_group_id': int
#                 }

#                 # Validate and convert data
#                 for field, field_type in allowed_fields.items():
#                     if field in data:
#                         try:
#                             if field_type == bool:
#                                 update_data[field] = data[field].lower() in ('true', '1', 'yes', 'y') if isinstance(data[field], str) else bool(data[field])
#                             else:
#                                 update_data[field] = field_type(data[field])
#                         except (ValueError, TypeError):
#                             return APIResponse.format(
#                                 success=False,
#                                 message=f'Invalid value for field {field}',
#                                 errors=f'Invalid value for field {field}',
#                                 status=400
#                             )

#                 # Validate amount_type if provided
#                 if 'amount_type' in update_data and update_data['amount_type'] not in ['percent', 'fixed']:
#                     return APIResponse.format(
#                         success=False,
#                         message='Invalid amount_type',
#                         errors='amount_type must be either "percent" or "fixed"',
#                         status=400
#                     )

#                 # Validate type_tax_use if provided
#                 if 'type_tax_use' in update_data and update_data['type_tax_use'] not in ['sale', 'purchase', 'none']:
#                     return APIResponse.format(
#                         success=False,
#                         message='Invalid type_tax_use',
#                         errors='type_tax_use must be one of: sale, purchase, none',
#                         status=400
#                     )

#                 # Validate tax_group_id if provided
#                 if 'tax_group_id' in update_data:
#                     tax_group = request.env['account.tax.group'].sudo().browse(update_data['tax_group_id'])
#                     if not tax_group.exists():
#                         return APIResponse.format(
#                             success=False,
#                             message='Tax group not found',
#                             errors='Invalid tax_group_id',
#                             status=404
#                         )

#                 # Update tax
#                 tax.write(update_data)

#                 # Prepare response data
#                 response_data = {
#                     'id': tax.id,
#                     'name': tax.name,
#                     'amount': tax.amount,
#                     'amount_type': tax.amount_type,
#                     'type_tax_use': tax.type_tax_use,
#                     'description': tax.description,
#                     'active': tax.active,
#                     'sequence': tax.sequence,
#                     'price_include': tax.price_include,
#                     'tax_group': {
#                         'id': tax.tax_group_id.id,
#                         'name': tax.tax_group_id.name
#                     } if tax.tax_group_id else None,
#                     'write_date': tax.write_date.strftime('%Y-%m-%d %H:%M:%S')
#                 }

#                 return APIResponse.format(
#                     success=True,
#                     message='Tax updated successfully',
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

#     @http.route('/api/taxes/<int:tax_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(tax_docs['delete_tax'])
#     def delete_tax(self, tax_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 tax = request.env['account.tax'].sudo().browse(tax_id)
#                 if not tax.exists():
#                     return APIResponse.error_response('Tax not found', 'Tax not found', status=404)

#                 # Perform delete 
#                 # tax.unlink()
#                 tax.write({'active': False})

#                 return APIResponse.success_response(message="Tax deleted successfully")
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(str(e), str(e), status=500)

# class TaxGroupController(http.Controller):
#     @http.route('/api/tax_groups', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(tax_groups_docs['list_tax_groups'])
#     def get_tax_groups(self, country_id=None, limit=20, offset=0, **kwargs):
#         try:
#             domain = []
#             if country_id:
#                 try:
#                     country_id = int(country_id)
#                     domain.append(('country_id', '=', country_id))
#                 except ValueError:
#                     return APIResponse.error_response('Invalid country_id format', 'country_id must be an integer', status=400)

#             limit = int(limit)
#             offset = int(offset)
            
#             # Get total count for pagination
#             total_count = request.env['account.tax.group'].sudo().search_count(domain)

#             # Get tax groups
#             tax_groups = request.env['account.tax.group'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='sequence, name'
#             )
#             tax_groups = request.env['account.tax.group'].sudo().search(domain)
            
#             tax_groups_data = [{
#                 'id': group.id,
#                 'name': group.name,
#                 'sequence': group.sequence,
#                 'country': {
#                     'country_id': group.country_id.id if group.country_id else None,
#                     'country_name': group.country_id.name if group.country_id else None,
#                 },
#                 'preceding_subtotal': group.preceding_subtotal if group.preceding_subtotal else None,
#             } for group in tax_groups]
#             response_data = {
#                 'tax_groups': tax_groups_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }

#             return APIResponse.success_response(message="Tax groups retrieved successfully", data=response_data)

#         except Exception as e:
#             return APIResponse.error_response(message="An error occurred while processing the request", errors=str(e), status=500)
        
#     @http.route('/api/tax_groups', type='http', auth='public', methods=['POST'], csrf=False)
#     @swagger_doc(tax_groups_docs['create_tax_group'])
#     def add_tax_group(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)
#                 success, converted_data = validate_and_convert_data(data, TAX_GROUP_SCHEMA)
#                 if success is not True:
#                     return converted_data
                
#                 # Create tax group
#                 tax_group = request.env['account.tax.group'].sudo().create(converted_data)
#                 response_data = {
#                     'id': tax_group.id,
#                     'name': tax_group.name,
#                     'country': {
#                         'country_id': tax_group.country_id.id if tax_group.country_id else None,
#                         'country_name': tax_group.country_id.name if tax_group.country_id else None,
#                     }
#                 }
#                 return APIResponse.success_response(message="Tax group created successfully", data=response_data)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(str(e), str(e), status=500)

#     @http.route('/api/tax_groups/<int:group_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     @swagger_doc(tax_groups_docs['get_tax_group'])
#     def get_tax_group(self, group_id, **kwargs):
#         try:
#             tax_group = request.env['account.tax.group'].sudo().browse(group_id)
#             if not tax_group.exists():
#                 return APIResponse.error_response('Tax group not found', 'Tax group not found', status=404)

#             group_data = {
#                 'id': tax_group.id,
#                 'name': tax_group.name,
#                 'sequence': tax_group.sequence,
#                 'country': {
#                     'country_id': tax_group.country_id.id if tax_group.country_id else None,
#                     'country_name': tax_group.country_id.name if tax_group.country_id else None,
#                 },
#                 'preceding_subtotal': tax_group.preceding_subtotal,
#             }
#             return APIResponse.success_response(message="Tax group retrieved successfully", data=group_data)
#         except Exception as e:
#             return APIResponse.error_response(str(e), str(e), status=500)

#     @http.route('/api/tax_groups/<int:group_id>', type='http', auth='public', methods=['GET'], csrf=False)
#     def update_tax_group(self, group_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 tax_group = request.env['account.tax.group'].sudo().browse(group_id)
#                 if not tax_group.exists():
#                     return APIResponse.error_response('Tax group not found', 'Tax group not found', status=404)

#                 data = get_request_data(request)
#                 update_data = {}

#                 # Fields that can be updated
#                 allowed_fields = {
#                     'name': str,
#                     'sequence': int,
#                     'country_id': int,
#                     'company_id': int,
#                     'preceding_subtotal': str
#                 }

#                 # Validate and convert data
#                 for field, field_type in allowed_fields.items():
#                     if field in data:
#                         try:
#                             update_data[field] = field_type(data[field])
#                         except (ValueError, TypeError):
#                             return APIResponse.format(
#                                 success=False,
#                                 message=f'Invalid value for field {field}',
#                                 errors=f'Invalid value for field {field}',
#                                 status=400
#                             )

#                 # Update tax group
#                 tax_group.write(update_data)

#                 # Prepare response data
#                 response_data = {
#                     'id': tax_group.id,
#                     'name': tax_group.name,
#                     'sequence': tax_group.sequence,
#                     'country_id': tax_group.country_id.id if tax_group.country_id else None,
#                     'country_name': tax_group.country_id.name if tax_group.country_id else None,
#                     'preceding_subtotal': tax_group.preceding_subtotal
#                 }
#                 return APIResponse.success_response(message="Tax group updated successfully", data=response_data)

#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(str(e), str(e), status=500)

#     @http.route('/api/tax_groups/<int:group_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
#     @swagger_doc(tax_groups_docs['delete_tax_group'])
#     def delete_tax_group(self, group_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 tax_group = request.env['account.tax.group'].sudo().browse(group_id)
#                 if not tax_group.exists():
#                     return APIResponse.error_response('Tax group not found', 'Tax group not found', status=404)

#                 # Check if tax group is being used by any taxes
#                 tax_group_in_use = request.env['account.tax'].sudo().search(
#                     [('tax_group_id', '=', tax_group.id)]
#                     )
#                 if tax_group_in_use:
#                     return APIResponse.error_response(
#                         message='Tax group cannot be deleted as it is being used by taxes',
#                         errors='Tax group in use',
#                     )

#                 # Delete tax group
#                 tax_group.unlink()
#                 return APIResponse.success_response(message="Tax group deleted successfully")
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(str(e), str(e), status=500)
