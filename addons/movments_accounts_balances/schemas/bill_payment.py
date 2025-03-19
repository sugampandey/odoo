BILL_PAYMENT_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'amount': {'type': 'number'},
        'name': {'type': 'string'},
        'state': {'type': 'string'},
        'payment_reference': {'type': 'string'},
        'partner': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'journal': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'payment_method': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        }
    }
}


BILL_PAYMENT_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': BILL_PAYMENT_OBJECT
    }
}


BILL_PAYMENT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': BILL_PAYMENT_OBJECT
    }
}
BILL_PAYMENT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'payments': {
                    'type': 'array',
                    'items': BILL_PAYMENT_OBJECT
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


BILL_PAYMENT_SCHEMA = {
    'required': {
        'bill_ids': {
            'type': str,
            'display_name': 'Bill Ids',
            'swagger_type': 'string'
        },
        'payment_amount': {
            'type': float,
            'display_name': 'Payment Amount',
            'swagger_type': 'number'
        },
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
            'swagger_type': 'integer'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'payment_account_id': {
            'type': int,
            'display_name': 'Outstanding Account',
            'swagger_type': 'integer'
        },
    },
    'optional': {
        # 'account_id': {
        #     'type': int,
        #     'display_name': 'Account',
        #     'swagger_type': 'integer'
        # },
        'payment_reference': {
            'type': str,
            'display_name': 'Payment Reference',
            'swagger_type': 'string'
        }
    }
}

# Parameters for different endpoints
BILL_PAYMENT_LIST_PARAMS = {
    'query': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'Filter by partner ID',
            'required': True
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
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
            'description': 'Start date for filtering bill payments (YYYY-MM-DD). Must be used together with date_to',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date for filtering bill payments (YYYY-MM-DD). Must be used together with date_from',
            'required': False
        }
    ]
}

BILL_PAYMENT_GET_PARAMS = {
    'path': [
        {
            'name': 'payment_id',
            'type': 'integer',
            'description': 'ID of the payment to retrieve',
            'required': True
        }
    ]
}

BILL_PAYMENT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'payment_id',
            'type': 'integer',
            'description': 'ID of the payment to delete',
            'required': True
        }
    ]
}

BILL_PAYMENT_CREATE_PARAMS = {
    'body': {
        'schema': BILL_PAYMENT_SCHEMA,
        'required': True
    }
}
