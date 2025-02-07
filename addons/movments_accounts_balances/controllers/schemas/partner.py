PARTNER_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'email': {'type': 'string'},
        'phone': {'type': 'string'},
        'is_company': {'type': 'boolean'},
        'mobile': {'type': 'string'},
        'active': {'type': 'boolean'},
        'parent': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'street': {'type': 'string'},
        'street2': {'type': 'string'},
        'zip': {'type': 'string'},
        'city': {'type': 'string'},
        'state': {'type': 'string'},
        'country': {'type': 'string'}
    }
}

PARTNER_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': PARTNER_OBJECT
    }
}


PARTNER_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'partners': {
                    'type': 'array',
                    'items': PARTNER_OBJECT
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


PARTNER_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Name',
            'swagger_type': 'string'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'is_company': {
            'type': bool,
            'display_name': 'Is Company',
            'swagger_type': 'boolean'
        },
        'email': {
            'type': str,
            'display_name': 'Email',
            'swagger_type': 'string'
        },
        'phone': {
            'type': str,
            'display_name': 'Phone',
            'swagger_type': 'string'
        },
        # 'category_id': {
        #     'type': int,
        #     'display_name': 'Category',
        #     'swagger_type': 'integer'
        # }
    },
    'optional': {
        'parent_id': {
            'type': int,
            'display_name': 'Parent',
            'swagger_type': 'integer'
        },
        'street': {
            'type': str,
            'display_name': 'Street',
            'swagger_type': 'string'
        },
        'street2': {
            'type': str,
            'display_name': 'Street 2',
            'swagger_type': 'string'
        },
        'zip': {
            'type': str,
            'display_name': 'Zip',
            'swagger_type': 'string'
        },
        'city': {
            'type': str,
            'display_name': 'City',
            'swagger_type': 'string'
        },
        'state_id': {
            'type': int,
            'display_name': 'State',
            'swagger_type': 'integer'
        },
        'country_id': {
            'type': int,
            'display_name': 'Country',
            'swagger_type': 'integer'
        }
    }
}


# Parameters for different endpoints
PARTNER_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
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

PARTNER_GET_PARAMS = {
    'path': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'ID of the partner to retrieve',
            'required': True
        }
    ]
}

PARTNER_DELETE_PARAMS = {
    'path': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'ID of the partner to delete',
            'required': True
        }
    ]
}

VENDOR_GET_PARAMS = {
    'path': [
        {
            'name': 'vendor_id',
            'type': 'integer',
            'description': 'ID of the vendor to retrieve',
            'required': True
        }
    ]
}

CUSTOMER_GET_PARAMS = {
    'path': [
        {
            'name': 'customer_id',
            'type': 'integer',
            'description': 'ID of the customer to retrieve',
            'required': True
        }
    ]
}

VENDOR_DELETE_PARAMS = {
    'path': [
        {
            'name': 'vendor_id',
            'type': 'integer',
            'description': 'ID of the vendor to delete',
            'required': True
        }
    ]
}

CUSTOMER_DELETE_PARAMS = {
    'path': [
        {
            'name': 'customer_id',
            'type': 'integer',
            'description': 'ID of the customer to delete',
            'required': True
        }
    ]
}

PARTNER_CREATE_PARAMS = {
    'body': {
        'schema': PARTNER_SCHEMA,
        'required': True
    }
}

PARTNER_CATEGORY_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'active': {'type': 'boolean'}
                }
            }
        }
    }
}
