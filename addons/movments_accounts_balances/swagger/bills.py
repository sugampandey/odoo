from .common import doc_generator
from ..controllers.schemas.bills import (
    BILL_RESPONSE, BILL_LIST_RESPONSE, BILL_CREATE_PARAMS, BILL_LIST_PARAMS, 
    BILL_GET_PARAMS, BILL_DELETE_PARAMS)


bills_docs = {
    'list_bills': doc_generator.create_endpoint_doc(
        'list',
        'bill',
        param_schema=BILL_LIST_PARAMS,
        response_schema=BILL_LIST_RESPONSE
    ),
    'get_bill': doc_generator.create_endpoint_doc(
        'get',
        'bill',
        param_schema=BILL_GET_PARAMS,
        response_schema=BILL_RESPONSE
    ),
    'create_bill': doc_generator.create_endpoint_doc(
        'create',
        'bill',
        param_schema=BILL_CREATE_PARAMS,
        response_schema=BILL_RESPONSE
    ),
    'delete_bill': doc_generator.create_endpoint_doc(
        'delete',
        'bill',
        param_schema=BILL_DELETE_PARAMS
    ),
    # 'cancel_bill': doc_generator.create_endpoint_doc(
    #     'cancel',
    #     'bill',
    #     param_schema=BILL_CANCEL_PARAMS
    # )
}
