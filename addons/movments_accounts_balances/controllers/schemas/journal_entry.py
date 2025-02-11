JOURNAL_ENTRY_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'ref': {'type': 'string'},
                'date': {'type': 'string', 'format': 'date'},
                'state': {'type': 'string'},
                'journal': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                },
                'company': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                },
                'lines': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'account': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'code': {'type': 'string'},
                                    'name': {'type': 'string'}
                                }
                            },
                            'name': {'type': 'string'},
                            'debit': {'type': 'number'},
                            'credit': {'type': 'number'},
                            'partner': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                },
                            }
                        }
                    }
                }
            }
        }
    }
}

JOURNAL_ENTRY_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'journal_entries': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'ref': {'type': 'string'},
                            'date': {'type': 'string', 'format': 'date'},
                            'journal_id': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                }
                            },
                            'state': {'type': 'string'},
                            'company': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                }
                            },
                        }
                    }
                },
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'total_count': {'type': 'integer'},
                        'limit': {'type': 'integer'},
                        'offset': {'type': 'integer'}
                    }
                }
            }
        }
    }
}

JOURNAL_ENTRY_SCHEMA = {
    'required': {
        'date': {
            'type': str,
            'display_name': 'Date',
            'format': 'date',
            'swagger_type': 'string'
        },
        'line_ids': {
            'type': list,
            'display_name': 'Line Items',
            'swagger_type': 'array',
            'items': {
                'type': dict,
                'required': {
                    'partner_id': {
                        'type': int,
                        'display_name': 'Partner',
                        'swagger_type': 'integer'
                    },
                    'amount': {
                        'type': float,
                        'display_name': 'Amount',
                        'swagger_type': 'number'
                    },
                    'amount_type': {
                        'type': str,
                        'display_name': 'Amount Type',
                        'swagger_type': 'string',
                        'enum': ['debit', 'credit']
                    },
                    'account_id': {
                        'type': int,
                        'display_name': 'Account',
                        'swagger_type': 'integer'
                    }
                },
                'optional': {
                    'ref' : {
                        'type': str,
                        'display_name': 'Reference',
                        'swagger_type': 'string'
                    },
                    'analytic_distribution': {
                        'type': str,
                        'display_name': 'Analytic Distribution',
                        'swagger_type': 'string'
                    }
                }
            }
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        }
    },
    'optional': {
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
            'swagger_type': 'integer'
        },
        'name': {
            'type': str,
            'display_name': 'Name',
            'swagger_type': 'string'
        },
        'ref': {
            'type': str,
            'display_name': 'Reference',
            'swagger_type': 'string'
        },
    }
}


# Parameters for different endpoints
JOURNAL_ENTRY_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'journal_id',
            'type': 'integer',
            'description': 'Filter by journal ID',
            'required': False
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Number of records to return (default: 20)',
            'required': False,
            'default': 20
        },
        {
            'name': 'offset',
            'type': 'integer',
            'description': 'Number of records to skip (default: 0)',
            'required': False,
            'default': 0
        },
        {
            'name': 'date_from',
            'type': 'string',
            'format': 'date',
            'description': 'Start date for filtering journal entries (YYYY-MM-DD). Must be used together with date_to',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date for filtering journal entries (YYYY-MM-DD). Must be used together with date_from',
            'required': False
        }
    ]
}


JOURNAL_ENTRY_GET_PARAMS = {
    'path': [
        {
            'name': 'journal_entry_id',
            'type': 'integer',
            'description': 'ID of the journal entry to retrieve',
            'required': True
        }
    ]
}

JOURNAL_ENTRY_DELETE_PARAMS = {
    'path': [
        {
            'name': 'journal_entry_id',
            'type': 'integer',
            'description': 'ID of the journal entry to delete',
            'required': True
        }
    ]
}

JOURNAL_ENTRY_CREATE_PARAMS = {
    'body': {
        'schema': JOURNAL_ENTRY_SCHEMA,
        'required': True
    }
}
