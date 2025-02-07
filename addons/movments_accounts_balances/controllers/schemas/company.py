COMPANY_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'city': {'type': 'string'},
        'street': {'type': 'string'},
        'phone': {'type': 'string'},
        'zip': {'type': 'string'},
        'email': {'type': 'string'},
        'active': {'type': 'boolean'},
        'currency': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'symbol': {'type': 'string'}
            },
        }
    }
}



COMPANY_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': COMPANY_OBJECT
    }
}

COMPANY_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'companies': {
                    'type': 'array',
                    'items': COMPANY_OBJECT
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


COMPANY_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Company Name',
            'swagger_type': 'string'
        },
        'email': {
            'type': str,
            'display_name': 'Email',
            'format': 'email',
            'swagger_type': 'string'
        },
        'phone': {
            'type': str,
            'display_name': 'Phone Number',
            'swagger_type': 'string'
        }
    },
    'optional': {
        'street': {
            'type': str,
            'display_name': 'Street Address',
            'swagger_type': 'string'
        },
        'city': {
            'type': str,
            'display_name': 'City',
            'swagger_type': 'string'
        },
        'zip': {
            'type': str,
            'display_name': 'ZIP Code',
            'swagger_type': 'string'
        },
        'currency_id': {
            'type': int,
            'display_name': 'Currency',
            'swagger_type': 'integer',
            'default': 2  # Default USD
        },
    }
}

# Parameters for different endpoints
COMPANY_LIST_PARAMS = {
    'query': [
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

COMPANY_GET_PARAMS = {
    'path': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'ID of the company to retrieve',
            'required': True
        }
    ]
}

COMPANY_DELETE_PARAMS = {
    'path': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'ID of the company to delete',
            'required': True
        }
    ]
}

COMPANY_CREATE_PARAMS = {
    'body': {
        'schema': COMPANY_SCHEMA,
        'required': True
    }
}
