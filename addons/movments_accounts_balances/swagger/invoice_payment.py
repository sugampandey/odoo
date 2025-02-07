from .common import doc_generator
from ..controllers.schemas.invoice_payment import (
    INVOICE_PAYMENT_RESPONSE, INVOICE_PAYMENT_LIST_RESPONSE, INVOICE_PAYMENT_CREATE_PARAMS,
    INVOICE_PAYMENT_GET_PARAMS, INVOICE_PAYMENT_DELETE_PARAMS, INVOICE_PAYMENT_LIST_PARAMS)


invoice_payments_docs = {
    'list_invoice_payments': doc_generator.create_endpoint_doc(
        'list',
        'invoice_payment',
        param_schema=INVOICE_PAYMENT_LIST_PARAMS,
        response_schema=INVOICE_PAYMENT_LIST_RESPONSE
    ),
    'get_invoice_payment': doc_generator.create_endpoint_doc(
        'get',
        'invoice_payment',
        param_schema=INVOICE_PAYMENT_GET_PARAMS,
        response_schema=INVOICE_PAYMENT_RESPONSE
    ),
    'create_invoice_payment': doc_generator.create_endpoint_doc(
        'create',
        'invoice_payment',
        param_schema=INVOICE_PAYMENT_CREATE_PARAMS,
        response_schema=INVOICE_PAYMENT_RESPONSE
    ),
    'delete_invoice_payment': doc_generator.create_endpoint_doc(
        'delete',
        'invoice_payment',
        param_schema=INVOICE_PAYMENT_DELETE_PARAMS
    )
}
