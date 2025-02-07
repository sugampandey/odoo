from .common import doc_generator
from ..controllers.schemas.journal import (
    JOURNAL_RESPONSE, JOURNAL_LIST_RESPONSE, JOURNAL_CREATE_PARAMS, JOURNAL_GET_PARAMS,
    JOURNAL_DELETE_PARAMS, JOURNAL_LIST_PARAMS, JOURNAL_TYPES_RESPONSE)

journals_docs = {
    'list_journals': doc_generator.create_endpoint_doc(
        'list',
        'journal',
        param_schema=JOURNAL_LIST_PARAMS,
        response_schema=JOURNAL_LIST_RESPONSE
    ),
    'get_journal': doc_generator.create_endpoint_doc(
        'get',
        'journal',
        param_schema=JOURNAL_GET_PARAMS,
        response_schema=JOURNAL_RESPONSE
    ),
    'create_journal': doc_generator.create_endpoint_doc(
        'create',
        'journal',
        param_schema=JOURNAL_CREATE_PARAMS,
        response_schema=JOURNAL_RESPONSE
    ),
    'delete_journal': doc_generator.create_endpoint_doc(
        'delete',
        'journal',
        param_schema=JOURNAL_DELETE_PARAMS
    ),
    'get_journal_types': doc_generator.create_endpoint_doc(
        'list',
        'journal_types',
        response_schema=JOURNAL_TYPES_RESPONSE
    )
}
