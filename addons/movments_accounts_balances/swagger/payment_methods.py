# from .common import doc_generator
# from ..controllers.schemas.payment_methods import (
#     PAYMENT_METHOD_RESPONSE, PAYMENT_METHOD_LIST_RESPONSE, PAYMENT_METHOD_CREATE_PARAMS, PAYMENT_METHOD_GET_PARAMS,
#     PAYMENT_METHOD_DELETE_PARAMS, PAYMENT_METHOD_LIST_PARAMS, BANK_ACCOUNT_RESPONSE, BANK_ACCOUNT_LIST_RESPONSE,
#     BANK_ACCOUNT_CREATE_PARAMS, BANK_ACCOUNT_GET_PARAMS, BANK_ACCOUNT_DELETE_PARAMS, BANK_ACCOUNT_LIST_PARAMS,
#     BANK_RESPONSE, BANK_LIST_RESPONSE, BANK_CREATE_PARAMS, BANK_GET_PARAMS, BANK_DELETE_PARAMS, BANK_LIST_PARAMS
# )

# payment_methods_docs = {
#     'list_payment_methods': doc_generator.create_endpoint_doc(
#         'list',
#         'payment_method',
#         param_schema=PAYMENT_METHOD_LIST_PARAMS,
#         response_schema=PAYMENT_METHOD_LIST_RESPONSE
#     ),
#     'get_payment_method': doc_generator.create_endpoint_doc(
#         'get',
#         'payment_method',
#         param_schema=PAYMENT_METHOD_GET_PARAMS,
#         response_schema=PAYMENT_METHOD_RESPONSE
#     ),
#     'create_payment_method': doc_generator.create_endpoint_doc(
#         'create',
#         'payment_method',
#         param_schema=PAYMENT_METHOD_CREATE_PARAMS,
#         response_schema=PAYMENT_METHOD_RESPONSE
#     ),
#     'delete_payment_method': doc_generator.create_endpoint_doc(
#         'delete',
#         'payment_method',
#         param_schema=PAYMENT_METHOD_DELETE_PARAMS
#     )
# }

# bank_accounts_docs = {
#     'list_bank_accounts': doc_generator.create_endpoint_doc(
#         'list',
#         'bank_account',
#         param_schema=BANK_ACCOUNT_LIST_PARAMS,
#         response_schema=BANK_ACCOUNT_LIST_RESPONSE
#     ),
#     'get_bank_account': doc_generator.create_endpoint_doc(
#         'get',
#         'bank_account',
#         param_schema=BANK_ACCOUNT_GET_PARAMS,
#         response_schema=BANK_ACCOUNT_RESPONSE
#     ),
#     'create_bank_account': doc_generator.create_endpoint_doc(
#         'create',
#         'bank_account',
#         param_schema=BANK_ACCOUNT_CREATE_PARAMS,
#         response_schema=BANK_ACCOUNT_RESPONSE
#     ),
#     'delete_bank_account': doc_generator.create_endpoint_doc(
#         'delete',
#         'bank_account',
#         param_schema=BANK_ACCOUNT_DELETE_PARAMS
#     )
# }

# banks_docs = {
#     'list_banks': doc_generator.create_endpoint_doc(
#         'list',
#         'bank',
#         param_schema=BANK_LIST_PARAMS,
#         response_schema=BANK_LIST_RESPONSE
#     ),
#     'get_bank': doc_generator.create_endpoint_doc(
#         'get',
#         'bank',
#         param_schema=BANK_GET_PARAMS,
#         response_schema=BANK_RESPONSE
#     ),
#     'create_bank': doc_generator.create_endpoint_doc(
#         'create',
#         'bank',
#         param_schema=BANK_CREATE_PARAMS,
#         response_schema=BANK_RESPONSE
#     ),
#     'delete_bank': doc_generator.create_endpoint_doc(
#         'delete',
#         'bank',
#         param_schema=BANK_DELETE_PARAMS
#     )
# }
