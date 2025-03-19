from .common import doc_generator
from ..schemas.bill_payment import (
    BILL_PAYMENT_RESPONSE, BILL_PAYMENT_LIST_RESPONSE, BILL_PAYMENT_CREATE_PARAMS, 
    BILL_PAYMENT_GET_PARAMS, BILL_PAYMENT_DELETE_PARAMS, BILL_PAYMENT_LIST_PARAMS) 

bill_payments_docs = {
    'list_bill_payments': doc_generator.create_endpoint_doc(
        'list',
        'bill_payment',
        param_schema=BILL_PAYMENT_LIST_PARAMS,
        response_schema=BILL_PAYMENT_LIST_RESPONSE
    ),
    'get_bill_payment': doc_generator.create_endpoint_doc(
        'get',
        'bill_payment',
        param_schema=BILL_PAYMENT_GET_PARAMS,
        response_schema=BILL_PAYMENT_RESPONSE
    ),
    'create_bill_payment': doc_generator.create_endpoint_doc(
        'create',
        'bill_payment',
        param_schema=BILL_PAYMENT_CREATE_PARAMS,
        response_schema=BILL_PAYMENT_RESPONSE
    ),
    'delete_bill_payment': doc_generator.create_endpoint_doc(
        'delete',
        'bill_payment',
        param_schema=BILL_PAYMENT_DELETE_PARAMS
    )
}
