ACCOUNT_CREATE_RESPONSE = {
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
                'account_type': {'type': 'string'},
                'company': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                },
                'create_date': {'type': 'string', 'format': 'date-time'},
                'opening_debit': {'type': 'number'},
                'opening_credit': {'type': 'number'}
            }
        }
    }
}

ACCOUNT_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'code': {'type': 'string'},
        'account_type': {'type': 'string'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'create_date': {'type': 'string', 'format': 'date-time'},
        'depricated': {'type': 'boolean'},
    }
}

ACCOUNT_GET_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': ACCOUNT_OBJECT
    }
}

ACCOUNT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'accounts': {
                    'type': 'array',
                    'items': ACCOUNT_OBJECT
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


ACCOUNT_SCHEMA = {
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
        'account_type': {
            'type': str,
            'display_name': 'Account Type',
            'swagger_type': 'string'
        },
        'payment_method': {
            'type': str,
            'display_name': 'Payment Method',
            'swagger_type':'string',
            'enum': [
                'none'
                'cash',
                'bank',
                'credit_card',
            ]
        }
    },
    'optional': {
        'currency_id': {
            'type': int,
            'display_name': 'Currency',
            'swagger_type': 'integer'
        },
        # 'reconcile': {
        #     'type': bool,
        #     'display_name': 'Allow Reconciliation',
        #     'swagger_type': 'boolean'
        # },
        'opening_debit': {
            'type': float,
            'display_name': 'Opening Debit',
            'swagger_type': 'number'
        },
        'opening_credit': {
            'type': float,
            'display_name': 'Opening Credit',
            'swagger_type': 'number'
        }
    }
}


ACCOUNT_LIST_PARAMS = {
    'query': [
        {
            'name': 'account_type',
            'type': 'string',
            'description': 'Filter by account type',
            'required': False,
            'enum': [
                'asset_receivable',
                'asset_cash',
                'asset_current',
                'asset_non_current',
                'asset_prepayments',
                'asset_fixed',
                'liability_payable',
                'liability_credit_card',
                'liability_current',
                'liability_non_current',
                'equity',
                'equity_unaffected',
                'income',
                'income_other',
                'expense',
                'expense_depreciation',
                'expense_direct_cost',
                'off_balance'
            ]
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'deprecated',
            'type': 'boolean',
            'description': 'Filter by deprecated',
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

ACCOUNT_GET_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the account to retrieve',
            'required': True
        }
    ]
}

ACCOUNT_CREATE_PARAMS = {
    'body': {
        'schema': ACCOUNT_SCHEMA,
        'required': True
    }
}

ACCOUNT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the account to delete',
            'required': True
        },
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'company ID of the account to delete',
            'required': True
        },
    ]
}

# ACCOUNT_UPDATE_PARAMS = {
#     'path': [
#         {
#             'name': 'account_id',
#             'type': 'integer',
#             'description': 'ID of the account to update',
#             'required': True
#         }
#     ],
#     'body': {
#         'schema': ACCOUNT_SCHEMA,
#         'required': True
#     }
# }
