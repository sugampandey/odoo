from .common import doc_generator
from ..controllers.schemas.partner import (
    PARTNER_RESPONSE, PARTNER_LIST_RESPONSE, PARTNER_CREATE_PARAMS, PARTNER_GET_PARAMS,
    VENDOR_GET_PARAMS, CUSTOMER_GET_PARAMS, PARTNER_LIST_PARAMS, VENDOR_DELETE_PARAMS, CUSTOMER_DELETE_PARAMS)

partners_docs = {
    'list_vendors': doc_generator.create_endpoint_doc(
        'list',
        'vendor',
        param_schema=PARTNER_LIST_PARAMS,
        response_schema=PARTNER_LIST_RESPONSE
    ),
    'list_customers': doc_generator.create_endpoint_doc(
        'list',
        'customer',
        param_schema=PARTNER_LIST_PARAMS,
        response_schema=PARTNER_LIST_RESPONSE
    ),
    'get_vendor': doc_generator.create_endpoint_doc(
        'get',
        'vendor',
        param_schema=VENDOR_GET_PARAMS,
        response_schema=PARTNER_RESPONSE
    ),
    'get_customer': doc_generator.create_endpoint_doc(
        'get',
        'customer',
        param_schema=CUSTOMER_GET_PARAMS,
        response_schema=PARTNER_RESPONSE
    ),
    'create_customer': doc_generator.create_endpoint_doc(
        'create',
        'customer',
        param_schema=PARTNER_CREATE_PARAMS,
        response_schema=PARTNER_RESPONSE
    ),
    'create_vendor': doc_generator.create_endpoint_doc(
        'create',
        'vendor',
        param_schema=PARTNER_CREATE_PARAMS,
        response_schema=PARTNER_RESPONSE
    ),
    'delete_vendor': doc_generator.create_endpoint_doc(
        'delete',
        'vendor',
        param_schema=VENDOR_DELETE_PARAMS
    ),
    'delete_customer': doc_generator.create_endpoint_doc(
        'delete',
        'customer',
        param_schema=CUSTOMER_DELETE_PARAMS
    ),
    
    # 'list_partner_categories': doc_generator.create_endpoint_doc(
    #     'list',
    #     'partner_categories',
    #     response_schema=PARTNER_CATEGORY_LIST_RESPONSE
    # )
}
