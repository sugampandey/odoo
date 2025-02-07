BIll_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'ref': {'type': 'string'},
        'invoice_date': {'type': 'string', 'format': 'date'},
        'invoice_date_due': {'type': 'string', 'format': 'date'},
        'state': {'type': 'string'},
        'amount_total': {'type': 'number'},
        'partner': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            }
        },
        'bill_lines': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'product': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'}
                        }
                    },
                    'name': {'type': 'string'},
                    'quantity': {'type': 'number'},
                    'price_unit': {'type': 'number'},
                    'price_subtotal': {'type': 'number'},
                    'account': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
}


BILL_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': BIll_OBJECT
    }
}


BILL_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'bills': {
                    'type': 'array',
                    'items': BIll_OBJECT
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

BILL_SCHEMA = {
    'required': {
        'partner_id': {
            'type': int,
            'display_name': 'Vendor',
            'swagger_type': 'integer'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'invoice_date': {
            'type': str,
            'display_name': 'Bill Date',
            'format': 'date',
            'swagger_type': 'string'
        },
        'invoice_date_due': {
            'type': str,
            'display_name': 'Due Date',
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
                    'amount': {
                        'type': float,
                        'display_name': 'Amount',
                        'swagger_type': 'number'
                    },
                },
                'optional': {
                    'description': {
                        'type': str,
                        'display_name': 'Description',
                        'swagger_type': 'string'
                    },
                    'class': {
                        'type': str,
                        'display_name': 'Class',
                        'swagger_type': 'string'
                    },
                    'account_id': {
                        'type': int,
                        'display_name': 'Expense Account',
                        'swagger_type': 'integer'
                    }
                }
            }
        }
    },
    'optional': {
        'ref': {
            'type': str,
            'display_name': 'Reference',
            'swagger_type': 'string'
        },
        'payable_account_id': {
            'type': int,
            'display_name': 'Payable Account',
            'swagger_type': 'integer'
        }
    }
}

# Parameters for different endpoints
BILL_LIST_PARAMS = {
    'query': [
        {
            'name': 'state',
            'type': 'string',
            'description': 'Filter by bill state',
            'required': False,
            'enum': ['draft', 'posted', 'cancel']
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'Filter by partner ID',
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
            'description': 'Start date for filtering bills (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date for filtering bills (YYYY-MM-DD)',
            'required': False
        }
    ]
}

BILL_GET_PARAMS = {
    'path': [
        {
            'name': 'bill_id',
            'type': 'integer',
            'description': 'ID of the bill to retrieve',
            'required': True
        }
    ]
}

BILL_CREATE_PARAMS = {
    'body': {
        'schema': BILL_SCHEMA,
        'required': True
    }
}

BILL_DELETE_PARAMS = {
    'path': [
        {
            'name': 'bill_id',
            'type': 'integer',
            'description': 'ID of the bill to delete',
            'required': True
        }
    ]
}

# BILL_CANCEL_PARAMS = {
#     'body': {
#         'required': {
#             'bill_id': {
#                 'type': int,
#                 'display_name': 'Bill ID',
#                 'swagger_type': 'integer'
#             }
#         }
#     }
# }
