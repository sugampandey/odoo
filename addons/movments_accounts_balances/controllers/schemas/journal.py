JOURNAL_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'code': {'type': 'string'},
        'type': {'type': 'string'},
        'type_name': {'type': 'string'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'active': {'type': 'boolean'},
        'bank_account': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'acc_number': {'type': 'string'},
                'bank_name': {'type': 'string'}
            },
        },
        'default_account': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'profit_account': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'loss_account': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'create_date': {'type': 'string'},
        'write_date': {'type': 'string'}
    }
}

JOURNAL_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': JOURNAL_OBJECT
    }
}

JOURNAL_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'journals': {
                    'type': 'array',
                    'items': JOURNAL_OBJECT
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


JOURNAL_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Journal Name',
            'swagger_type': 'string'
        },
        'code': {
            'type': str,
            'display_name': 'Journal Code',
            'swagger_type': 'string'
        },
        'type': {
            'type': str,
            'display_name': 'Journal Type',
            'swagger_type': 'string',
            'enum': ['sale', 'purchase', 'cash', 'bank', 'general']
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        }
    },
    'optional': {
        'default_account_id': {
            'type': int,
            'display_name': 'Default Account',
            'swagger_type': 'integer'
        },
        'profit_account_id': {
            'type': int,
            'display_name': 'Profit Account',
            'swagger_type': 'integer'
        },
        'loss_account_id': {
            'type': int,
            'display_name': 'Loss Account',
            'swagger_type': 'integer'
        },
        'bank_account_id': {
            'type': int,
            'display_name': 'Bank Account',
            'swagger_type': 'integer'
        }
    }
}

# Parameters for different endpoints
JOURNAL_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'journal_type',
            'type': 'string',
            'description': 'Filter by journal type',
            'required': False,
            'enum': ['sale', 'purchase', 'cash', 'bank', 'general']
        },
        {
            'name': 'active',
            'type': 'boolean',
            'description': 'Filter by active status',
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
        }
    ]
}


JOURNAL_GET_PARAMS = {
    'path': [
        {
            'name': 'journal_id',
            'type': 'integer',
            'description': 'ID of the journal to retrieve',
            'required': True
        }
    ]
}

JOURNAL_DELETE_PARAMS = {
    'path': [
        {
            'name': 'journal_id',
            'type': 'integer',
            'description': 'ID of the journal to delete',
            'required': True
        }
    ]
}

JOURNAL_CREATE_PARAMS = {
    'body': {
        'schema': JOURNAL_SCHEMA,
        'required': True
    }
}

JOURNAL_TYPES_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'name': {'type': 'string'}
                }
            }
        }
    }
}
