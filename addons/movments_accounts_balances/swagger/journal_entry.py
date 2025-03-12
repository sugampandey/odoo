from .common import doc_generator
from ..controllers.schemas.journal_entry import (
    JOURNAL_ENTRY_LIST_PARAMS, JOURNAL_ENTRY_LIST_RESPONSE, JOURNAL_ENTRY_GET_PARAMS,
    JOURNAL_ENTRY_CREATE_RESPONSE, JOURNAL_ENTRY_GET_RESPONSE, JOURNAL_ENTRY_CREATE_PARAMS, JOURNAL_ENTRY_DELETE_PARAMS,
)

journal_entries_docs = {
    'list_journal_entries': doc_generator.create_endpoint_doc(
        'list',
        'journal_entry',
        param_schema=JOURNAL_ENTRY_LIST_PARAMS,
        response_schema=JOURNAL_ENTRY_LIST_RESPONSE
    ),
    'get_journal_entry': doc_generator.create_endpoint_doc(
        'get',
        'journal_entry',
        param_schema=JOURNAL_ENTRY_GET_PARAMS,
        response_schema=JOURNAL_ENTRY_GET_RESPONSE
    ),
    'create_journal_entry': doc_generator.create_endpoint_doc(
        'create',
        'journal_entry',
        param_schema=JOURNAL_ENTRY_CREATE_PARAMS,
        response_schema=JOURNAL_ENTRY_CREATE_RESPONSE
    ),
    'delete_journal_entry': doc_generator.create_endpoint_doc(
        'delete',
        'journal_entry',
        param_schema=JOURNAL_ENTRY_DELETE_PARAMS
    ),
}
