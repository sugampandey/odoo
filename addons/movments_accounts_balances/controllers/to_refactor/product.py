# from odoo import http
# from odoo.http import request
# import json
# from odoo.exceptions import ValidationError
# from .common import APIResponse, validate_and_convert_data, get_request_data
# from .utils import validate_company, validate_tax, validate_account

# from ..swagger.common import swagger_doc
# from ..swagger.product import product_categories_docs, products_docs
# from .schemas.product import PRODUCT_CATEGORY_SCHEMA, PRODUCT_SCHEMA

# class ProductCategoryAPI(http.Controller):

#     @http.route('/api/product_categories', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
#     @swagger_doc(product_categories_docs['create_product_category'])
#     def create_product_category(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)
                
#                 success, converted_data = validate_and_convert_data(data, PRODUCT_CATEGORY_SCHEMA)
#                 if not success:
#                     return converted_data

#                 # Prepare category values
#                 category_values = {
#                     'name': converted_data['name'],
#                     'parent_id': converted_data.get('parent_id', False),
#                 }

#                 # Create category
#                 category = request.env['product.category'].sudo().create(category_values)

#                 response_data = {
#                     'id': category.id,
#                     'name': category.name,
#                     'complete_name': category.complete_name,  # This gives full path (e.g., "All/Electronics/Laptops")
#                     'parent_id': {
#                         'id': category.parent_id.id,
#                         'name': category.parent_id.name
#                     } if category.parent_id else None,
#                 }
                
#                 return APIResponse.success_response(message='Category created successfully', data=response_data)
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='Failed to create category', errors=str(e), status=500)

#     @http.route('/api/product_categories', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
#     @swagger_doc(product_categories_docs['list_product_categories'])
#     def get_product_categories(self, parent_id=None, limit=20, offset=0, **kwargs):
#         try:
#             domain = []
            
#             # Handle parent category filter
#             if parent_id:
#                 domain.append(('parent_id', '=', int(parent_id)))

#             # Handle name search
#             limit = int(limit)
#             offset = int(offset)
            
#             # Get total count for pagination
#             total_count = request.env['product.category'].sudo().search_count(domain)

#             # Get product categories with pagination
#             categories = request.env['product.category'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='complete_name asc'  # Sort by complete name for hierarchical view
#             )
            
#             categories_data = [{
#                 'id': category.id,
#                 'name': category.name,
#                 'complete_name': category.complete_name,
#                 'parent': {
#                     'id': category.parent_id.id,
#                     'name': category.parent_id.name
#                 } if category.parent_id else None,
#                 'child_categories': [{
#                     'id': child.id,
#                     'name': child.name,
#                     'complete_name': child.complete_name
#                 } for child in category.child_id]
#             } for category in categories]

#             response_data = {
#                 'categories': categories_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }

#             return APIResponse.success_response(message='Categories retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message='Failed to retrieve categories', errors=str(e), status=500)

#     @http.route('/api/product_categories/<int:category_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
#     @swagger_doc(product_categories_docs['get_product_category'])
#     def get_product_category(self, category_id, **kwargs):
#         try:
#             category = request.env['product.category'].sudo().browse(category_id)
            
#             if not category.exists():
#                 return APIResponse.error_response(message='Category not found', status=404)

#             response_data = {
#                 'id': category.id,
#                 'name': category.name,
#                 'complete_name': category.complete_name,
#                 'parent': {
#                     'id': category.parent_id.id,
#                     'name': category.parent_id.name
#                 } if category.parent_id else None,
#                 'child_categories': [{
#                     'id': child.id,
#                     'name': child.name,
#                     'complete_name': child.complete_name
#                 } for child in category.child_id],
#             }

#             return APIResponse.success_response(message='Category retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message='Failed to retrieve category', errors=str(e), status=500)

#     @http.route('/api/product_categories/<int:category_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
#     @swagger_doc(product_categories_docs['delete_product_category'])
#     def delete_product_category(self, category_id, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 category = request.env['product.category'].sudo().browse(category_id)
                
#                 if not category.exists():
#                     return APIResponse.error_response(message='Category not found', errors="", status=404)

#                 # Check if category has child categories
#                 if category.child_id:
#                     return APIResponse.error_response(message='Cannot delete category with child categories', errors="Cannot delete category with child categories")

#                 # Delete the category
#                 category.unlink()

#                 return APIResponse.success_response(message='Category deleted successfully')
#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='Failed to delete category', errors=str(e), status=500)



# class ProductAPI(http.Controller):

#     def _get_product_accounts(self, product):
#         """Get the accounts associated with the product"""
#         return product.get_product_accounts()
    
#     def get_product_accounts_data(self, product):
#         """Helper method to get product accounts including fallback to category accounts"""
#         return {
#             'income': {
#                 'id': product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id,
#                 'code': product.property_account_income_id.code or product.categ_id.property_account_income_categ_id.code,
#                 'name': product.property_account_income_id.name or product.categ_id.property_account_income_categ_id.name,
#                 'is_category_account': not bool(product.property_account_income_id)
#             },
#             'expense': {
#                 'id': product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id,
#                 'code': product.property_account_expense_id.code or product.categ_id.property_account_expense_categ_id.code,
#                 'name': product.property_account_expense_id.name or product.categ_id.property_account_expense_categ_id.name,
#                 'is_category_account': not bool(product.property_account_expense_id)
#             }
#         }
    
#     def set_property_account(self, product, account_id, property_name, company_id):
#         """
#         Set property account for product
        
#         Args:
#             product: product.template record
#             account_id: account.account ID
#             property_name: name of the property (property_account_income_id/property_account_expense_id)
#             company_id: company ID
#         """
#         try:
#             IrProperty = request.env['ir.property'].sudo()

#             # validate account
#             is_valid, error_message = validate_account(request, account_id, company_id)
#             if not is_valid:
#                 raise ValidationError(f"Invalid account: {error_message}")
            
#             # Check if property already exists
#             existing_property = IrProperty.search([
#                 ('name', '=', property_name),
#                 ('res_id', '=', f'product.template,{product.id}'),
#                 ('company_id', '=', company_id)
#             ], limit=1)

#             property_value = f'account.account,{account_id}'
            
#             if existing_property:
#                 # Update existing property
#                 existing_property.write({
#                     'value_reference': property_value
#                 })
#             else:
#                 # Create new property
#                 property_account = IrProperty.create({
#                     'name': property_name,
#                     'company_id': company_id,
#                     'res_id': f'product.template,{product.id}',
#                     'type': 'many2one',
#                     'value_reference': property_value,
#                     'fields_id': request.env['ir.model.fields'].sudo().search([
#                         ('model', '=', 'product.template'),
#                         ('name', '=', property_name)
#                     ], limit=1).id
#                 })
#         except Exception as e:
#             raise ValidationError(f"Error setting property account: {str(e)}")
    
#     def validate_and_prepare_invoice_data(self, data, product_expected_fields):
#         success, converted_data = validate_and_convert_data(data, product_expected_fields)
#         if success is not True:
#             return False, converted_data, converted_data
        
#         # Validate company 
#         company_id = converted_data['company_id']
#         is_valid, error_message = validate_company(request, company_id)
#         if not is_valid:
#             return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}'), converted_data

#         # Prepare product values
#         product_values = {
#             'name': converted_data.get('name'),
#             'type': converted_data.get('type') if converted_data.get('type') else converted_data.get('detailed_type'),
#             'default_code': converted_data.get('default_code'),
#             'barcode': converted_data.get('barcode'),
#             'list_price': float(converted_data.get('list_price', 0.0)),
#             'standard_price': float(converted_data.get('standard_price', 0.0)),
#             'sale_ok': converted_data.get('can_be_sold', True),
#             'purchase_ok': converted_data.get('can_be_purchased', True),
#             'detailed_type': converted_data.get('detailed_type'),
#             'categ_id': converted_data.get('category_id'),
#             'description': converted_data.get('description'),
#             'description_sale': converted_data.get('description_sale'),
#             'weight': converted_data.get('weight', 0.0),
#             'volume': converted_data.get('volume', 0.0),
#             'active': converted_data.get('active', True),
#             'company_id': converted_data.get('company_id'),
#         }

#         # Handle taxes
#         if converted_data.get('taxes_id'):
#             for tax_id in converted_data['taxes_id']:
#                 is_valid, error_message = validate_tax(request, tax_id, company_id)
#                 if not is_valid:
#                     return False, APIResponse.error_response(f'Invalid tax: {error_message}', f'Invalid tax_id: {tax_id}'), converted_data
#             product_values['taxes_id'] = [(6, 0, converted_data['taxes_id'])]
                
#         if converted_data.get('supplier_taxes_id'):
#             for tax_id in converted_data['supplier_taxes_id']:
#                 is_valid, error_message = validate_tax(request, tax_id, company_id)
#                 if not is_valid:
#                     return False, APIResponse.error_response(f'Invalid supplier tax: {error_message}', f'Invalid supplier_tax_id: {tax_id}'), converted_data
#             product_values['supplier_taxes_id'] = [(6, 0, converted_data['supplier_taxes_id'])]
#         return True, product_values, converted_data

#     @http.route('/api/products', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
#     @swagger_doc(products_docs['create_product'])
#     def create_product(self, **kwargs):
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 data = get_request_data(request)

#                 success, product_values, converted_data = self.validate_and_prepare_invoice_data(data, PRODUCT_SCHEMA)
#                 if not success:
#                     return product_values

#                 # Create product
#                 product = request.env['product.template'].sudo().create(product_values)

#                 # Handle product variants if attributes are provided
#                 if 'attributes' in converted_data:
#                     for attribute in converted_data['attributes']:
#                         # Create or get attribute
#                         attr = request.env['product.attribute'].sudo().create({
#                             'name': attribute['name'],
#                             'display_type': attribute.get('display_type', 'radio'),
#                         })

#                         # Create attribute values
#                         attr_value_ids = []
#                         for value in attribute['values']:
#                             attr_value = request.env['product.attribute.value'].sudo().create({
#                                 'name': value,
#                                 'attribute_id': attr.id
#                             })
#                             attr_value_ids.append(attr_value.id)

#                         # Link attributes to product template
#                         request.env['product.template.attribute.line'].sudo().create({
#                             'product_tmpl_id': product.id,
#                             'attribute_id': attr.id,
#                             'value_ids': [(6, 0, attr_value_ids)]
#                         })

#                 if converted_data.get('property_account_income_id'):
#                     self.set_property_account(
#                         product,
#                         converted_data['property_account_income_id'],
#                         'property_account_income_id',
#                         converted_data['company_id']
#                     )

#                 if converted_data.get('property_account_expense_id'):
#                     self.set_property_account(
#                         product,
#                         converted_data['property_account_expense_id'],
#                         'property_account_expense_id',
#                         converted_data['company_id']
#                     )

#                 # Get product accounts
#                 product_accounts = self._get_product_accounts(product)

#                 # Prepare response
#                 response_data = {
#                     'id': product.id,
#                     'name': product.name,
#                     'default_code': product.default_code,
#                     'barcode': product.barcode,
#                     'list_price': product.list_price,
#                     'standard_price': product.standard_price,
#                     'type': product.type,
#                     'categ_id': {
#                         'id': product.categ_id.id,
#                         'name': product.categ_id.name,
#                     },
#                     'accounts': {
#                         'income': {
#                             'id': product_accounts.get('income').id,
#                             'code': product_accounts.get('income').code,
#                             'name': product_accounts.get('income').name,
#                         } if product_accounts.get('income') else None,
#                         'expense': {
#                             'id': product_accounts.get('expense').id,
#                             'code': product_accounts.get('expense').code,
#                             'name': product_accounts.get('expense').name,
#                         } if product_accounts.get('expense') else None,
#                     },
#                     'taxes': [{
#                         'id': tax.id,
#                         'name': tax.name,
#                         'amount': tax.amount
#                     } for tax in product.taxes_id],
#                     'supplier_taxes': [{
#                         'id': tax.id,
#                         'name': tax.name,
#                         'amount': tax.amount
#                     } for tax in product.supplier_taxes_id],
#                     'variants': [{
#                         'id': variant.id,
#                         'name': variant.name,
#                         'default_code': variant.default_code,
#                         'barcode': variant.barcode,
#                         'attribute_values': [
#                             {
#                                 'attribute': value.attribute_id.name,
#                                 'value': value.name
#                             }
#                             for value in variant.product_template_attribute_value_ids
#                         ]
#                     } for variant in product.product_variant_ids]
#                 }
#                 return APIResponse.success_response(message='Product created successfully', data=response_data)

#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='Failed to process request', errors=str(e), status=500)
        

#     @http.route('/api/products', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
#     @swagger_doc(products_docs['list_products'])
#     def get_products(self, company_id=None, category_id=None, active=None, limit=20, offset=0, **kwargs):
#         """Get all products or filter by parameters"""
#         try:
#             domain = []
            
#             # Build domain filters
#             if active:
#                 active = active.lower() == 'true'
#                 domain.append(('active', '=', active))
#             if category_id:
#                 domain.append(('categ_id', '=', int(category_id)))
#             if company_id:
#                 domain.append(('company_id', '=', int(company_id)))
#             limit = int(limit)
#             offset = int(offset)

#             # Get total count for pagination
#             total_count = request.env['product.template'].sudo().search_count(domain)

#             # Get products with pagination
#             products = request.env['product.template'].sudo().search(
#                 domain,
#                 limit=limit,
#                 offset=offset,
#                 order='name asc'
#             )

#             products_data = []
#             for product in products:
#                 product_data = {
#                     'id': product.id,
#                     'name': product.name,
#                     'default_code': product.default_code,
#                     'barcode': product.barcode,
#                     'type': product.type,
#                     'detailed_type': product.detailed_type,
#                     'list_price': product.list_price,
#                     'standard_price': product.standard_price,
#                     'category': {
#                         'id': product.categ_id.id,
#                         'name': product.categ_id.name,
#                         'complete_name': product.categ_id.complete_name,
#                     },
#                     'can_be_sold': product.sale_ok,
#                     'can_be_purchased': product.purchase_ok,
#                     'active': product.active,
#                     'weight': product.weight,
#                     'volume': product.volume,
#                     'accounts': self.get_product_accounts_data(product),
#                     'taxes': [{
#                         'id': tax.id,
#                         'name': tax.name,
#                         'amount': tax.amount,
#                         'type': tax.type_tax_use
#                     } for tax in product.taxes_id],
#                     'supplier_taxes': [{
#                         'id': tax.id,
#                         'name': tax.name,
#                         'amount': tax.amount,
#                         'type': tax.type_tax_use
#                     } for tax in product.supplier_taxes_id],
#                     'variants': [{
#                         'id': variant.id,
#                         'name': variant.name,
#                         'default_code': variant.default_code,
#                         'barcode': variant.barcode,
#                         'attribute_values': [{
#                             'attribute': value.attribute_id.name,
#                             'value': value.name
#                         } for value in variant.product_template_attribute_value_ids]
#                     } for variant in product.product_variant_ids]
#                 }
#                 products_data.append(product_data)
#             response_data = {
#                 'products': products_data,
#                 'pagination': {
#                     'total_count': total_count,
#                     'limit': limit,
#                     'offset': offset
#                 }
#             }

#             return APIResponse.success_response(message='Products retrieved successfully', data=response_data)

#         except Exception as e:
#             return APIResponse.error_response(message='Failed to retrieve products', errors=str(e), status=500)

#     @http.route('/api/products/<int:product_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
#     @swagger_doc(products_docs['get_product'])
#     def get_product(self, product_id, **kwargs):
#         """Get single product by ID"""
#         try:
#             product = request.env['product.template'].sudo().browse(product_id)
            
#             if not product.exists():
#                 return APIResponse.error_response(message='Product not found', errors="Product not found")

#             response_data = {
#                 'id': product.id,
#                 'name': product.name,
#                 'default_code': product.default_code,
#                 'barcode': product.barcode,
#                 'type': product.type,
#                 'detailed_type': product.detailed_type,
#                 'list_price': product.list_price,
#                 'standard_price': product.standard_price,
#                 'category': {
#                     'id': product.categ_id.id,
#                     'name': product.categ_id.name,
#                     'complete_name': product.categ_id.complete_name,
#                 },
#                 'can_be_sold': product.sale_ok,
#                 'can_be_purchased': product.purchase_ok,
#                 'active': product.active,
#                 'weight': product.weight,
#                 'volume': product.volume,
#                 'accounts': self.get_product_accounts_data(product),
#                 'taxes': [{
#                     'id': tax.id,
#                     'name': tax.name,
#                     'amount': tax.amount,
#                     'type': tax.type_tax_use
#                 } for tax in product.taxes_id],
#                 'supplier_taxes': [{
#                     'id': tax.id,
#                     'name': tax.name,
#                     'amount': tax.amount,
#                     'type': tax.type_tax_use
#                 } for tax in product.supplier_taxes_id],
#                 'variants': [{
#                     'id': variant.id,
#                     'name': variant.name,
#                     'default_code': variant.default_code,
#                     'barcode': variant.barcode,
#                     'attribute_values': [{
#                         'attribute': value.attribute_id.name,
#                         'value': value.name
#                     } for value in variant.product_template_attribute_value_ids]
#                 } for variant in product.product_variant_ids]
#             }
#             return APIResponse.success_response(message='Product retrieved successfully', data=response_data)
#         except Exception as e:
#             return APIResponse.error_response(message='Failed to retrieve product', errors=str(e), status=500)

#     @http.route('/api/products/<int:product_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
#     @swagger_doc(products_docs['delete_product'])
#     def delete_product(self, product_id, **kwargs):
#         """Delete product by ID"""
#         cursor = request.env.cr
#         try:
#             with cursor.savepoint():
#                 product = request.env['product.template'].sudo().browse(product_id)
                
#                 if not product.exists():
#                     return APIResponse.error_response(message='Product not found', errors="Product not found", status=404)

#                 # Delete the product
#                 # product.unlink()
#                 product.write({'active': False})

#                 return APIResponse.success_response(message='Product deleted successfully')

#         except Exception as e:
#             cursor.rollback()
#             return APIResponse.error_response(message='Failed to delete product', errors=str(e), status=500)



