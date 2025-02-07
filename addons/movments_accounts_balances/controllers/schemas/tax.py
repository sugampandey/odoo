# Tax Group Schemas
TAX_GROUP_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'sequence': {'type': 'integer'},
        'country': {
            'type': 'object',
            'properties': {
                'country_id': {'type': 'integer'},
                'country_name': {'type': 'string'}
            }
        },
        'preceding_subtotal': {'type': 'string'}
    }
}
TAX_GROUP_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': TAX_GROUP_OBJECT
    }
}

TAX_GROUP_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'tax_groups': {
                    'type': 'array',
                    'items': TAX_GROUP_OBJECT
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


TAX_GROUP_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Tax Group Name',
            'swagger_type': 'string'
        }
    },
    'optional': {
        'country_id': {
            'type': int,
            'display_name': 'Country',
            'swagger_type': 'integer'
        },
    }
}

# Tax Schemas
TAX_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'amount': {'type': 'number'},
        'amount_type': {'type': 'string'},
        'type_tax_use': {'type': 'string'},
        'description': {'type': 'string'},
        'active': {'type': 'boolean'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'sequence': {'type': 'integer'},
        'price_include': {'type': 'boolean'},
        'tax_group': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        }
    }
}
TAX_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': TAX_OBJECT
    }
}

TAX_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'taxes': {
                    'type': 'array',
                    'items': TAX_OBJECT
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


TAX_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Tax Name',
            'swagger_type': 'string'
        },
        'amount': {
            'type': float,
            'display_name': 'Tax Amount',
            'swagger_type': 'number'
        },
        'amount_type': {
            'type': str,
            'display_name': 'Amount Type',
            'swagger_type': 'string',
            'enum': ['percent', 'fixed']
        },
        'tax_group_id': {
            'type': int,
            'display_name': 'Tax Group',
            'swagger_type': 'integer'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company ID',
            'swagger_type': 'integer'
        }
    },
    'optional': {
        'description': {
            'type': str,
            'display_name': 'Description',
            'swagger_type': 'string'
        },
        'active': {
            'type': bool,
            'display_name': 'Active',
            'swagger_type': 'boolean'
        },
        'price_include': {
            'type': bool,
            'display_name': 'Included in Price',
            'swagger_type': 'boolean'
        },
        'tax_scope': {
            'type': str,
            'display_name': 'Tax Scope',
            'swagger_type': 'string'
        }
    }
}


# Parameters for different endpoints
TAX_GROUP_LIST_PARAMS = {
    'query': [
        {
            'name': 'country_id',
            'type': 'integer',
            'description': 'Filter by country ID',
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

TAX_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'type_tax_use',
            'type': 'string',
            'description': 'Filter by tax type',
            'required': False,
            'enum': ['sale', 'purchase', 'none']
        },
        {
            'name': 'tax_group_id',
            'type': 'integer',
            'description': 'Filter by tax group ID',
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
        }
    ]
}


TAX_GET_PARAMS = {
    'path': [
        {
            'name': 'tax_id',
            'type': 'integer',
            'description': 'ID of the tax to retrieve',
            'required': True
        }
    ]
}

TAX_GROUP_GET_PARAMS = {
    'path': [
        {
            'name': 'group_id',
            'type': 'integer',
            'description': 'ID of the tax group to retrieve',
            'required': True
        }
    ]
}

TAX_DELETE_PARAMS = {
    'path': [
        {
            'name': 'tax_id',
            'type': 'integer',
            'description': 'ID of the tax to delete',
            'required': True
        }
    ]
}

TAX_GROUP_DELETE_PARAMS = {
    'path': [
        {
            'name': 'group_id',
            'type': 'integer',
            'description': 'ID of the tax group to delete',
            'required': True
        }
    ]
}

TAX_CREATE_PARAMS = {
    'body': {
        'schema': TAX_SCHEMA,
        'required': True
    }
}

TAX_GROUP_CREATE_PARAMS = {
    'body': {
        'schema': TAX_GROUP_SCHEMA,
        'required': True
    }
}
