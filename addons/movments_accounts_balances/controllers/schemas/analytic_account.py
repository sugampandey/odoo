ANALYTIC_ACCOUNT_CREATE_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'code': {'type': 'string'},
                'company': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                },
                'create_date': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

ANALYTIC_ACCOUNT_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'code': {'type': 'string'},
        'active': {'type': 'boolean'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'plan': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'partner': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'create_date': {'type': 'string', 'format': 'date-time'}
    }
}

ANALYTIC_ACCOUNT_GET_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': ANALYTIC_ACCOUNT_OBJECT
    }
}


ANALYTIC_ACCOUNT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'analytic_class': {
                    'type': 'array',
                    'items': ANALYTIC_ACCOUNT_OBJECT
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


ANALYTIC_ACCOUNT_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Account Name',
            'swagger_type': 'string'
        },
        'code': {
            'type': str,
            'display_name': 'Account Code',
            'swagger_type': 'string'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'plan_id': {
            'type': int,
            'display_name': 'Analytic Plan',
            'swagger_type': 'integer'
        }
    },
    'optional': {}
}

# Parameters for different endpoints
ANALYTIC_ACCOUNT_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': False
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
        },
    ]
}

ANALYTIC_ACCOUNT_GET_PARAMS = {
    'path': [
        {
            'name': 'analytic_class_id',
            'type': 'integer',
            'description': 'ID of the analytic class to retrieve',
            'required': True
        }
    ]
}

ANALYTIC_ACCOUNT_CREATE_PARAMS = {
    'body': {
        'schema': ANALYTIC_ACCOUNT_SCHEMA,
        'required': True
    }
}

ANALYTIC_ACCOUNT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'analytic_class_id',
            'type': 'integer',
            'description': 'ID of the analytic class to delete',
            'required': True
        }
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID for validation',
            'required': True
        }
    ]
}
