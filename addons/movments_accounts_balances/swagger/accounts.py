from .common import doc_generator
from ..schemas.accounts import (
    ACCOUNT_CREATE_RESPONSE, ACCOUNT_GET_RESPONSE, ACCOUNT_LIST_RESPONSE, ACCOUNT_CREATE_PARAMS, ACCOUNT_GET_PARAMS,
    ACCOUNT_DELETE_PARAMS, ACCOUNT_LIST_PARAMS)

accounts_docs = {
    'list_accounts': doc_generator.create_endpoint_doc(
        'list',
        'accounts',
        param_schema=ACCOUNT_LIST_PARAMS,
        response_schema=ACCOUNT_LIST_RESPONSE
    ),
    'get_account': doc_generator.create_endpoint_doc(
        'get',
        'accounts',
        param_schema=ACCOUNT_GET_PARAMS,
        response_schema=ACCOUNT_GET_RESPONSE
    ),
    'create_account': doc_generator.create_endpoint_doc(
        'create',
        'accounts',
        param_schema=ACCOUNT_CREATE_PARAMS,
        response_schema=ACCOUNT_CREATE_RESPONSE
    ),
    # 'update_account': doc_generator.create_endpoint_doc(
    #     'update',
    #     'accounts',
    #     param_schema=ACCOUNT_UPDATE_PARAMS,
    #     response_schema=ACCOUNT_RESPONSE
    # ),
    'delete_account': doc_generator.create_endpoint_doc(
        'delete',
        'accounts',
        param_schema=ACCOUNT_DELETE_PARAMS
    )
}
