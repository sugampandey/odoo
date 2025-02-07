INVOICE_RESPONSE = {
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
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

INVOICE_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'invoices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'ref': {'type': 'string'},
                            'date': {'type': 'string', 'format': 'date'},
                            'state': {'type': 'string'},
                            'partner': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                }
                            },
                            'amount': {'type': 'number'},
                            'company': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                }
                            }
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
            },
        }
    },
}



INVOICE_SCHEMA = {
    'required': {
        'invoice_date': {
            'type': str,
            'display_name': 'Invoice Date',
            'format': 'date',
            'swagger_type': 'string'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'invoice_date_due': {
            'type': str,
            'display_name': 'Invoice Due Date',
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
                        'display_name': 'Income Account',
                        'swagger_type': 'integer'
                    }
                }
            }
        },
        'customer_id': {
            'type': int,
            'display_name': 'Customer',
            'swagger_type': 'integer'
        },
    },
    'optional': {
        'ref': {
            'type': str,
            'display_name': 'Reference',
            'swagger_type': 'string'
        },
        'receivable_account_id': {
            'type': int,
            'display_name': 'Receivable Account',
            'swagger_type': 'integer'
        },
    }
}

INVOICE_LIST_PARAMS = {
    'query': [
        {
            'name': 'state',
            'type': 'string',
            'description': 'Filter by invoice state',
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
            'description': 'Start date for filtering invoices (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date for filtering invoices (YYYY-MM-DD)',
            'required': False
        }
    ]
}


INVOICE_GET_PARAMS = {
    'path': [
        {
            'name': 'invoice_id',
            'type': 'integer',
            'description': 'ID of the invoice to retrieve',
            'required': True
        }
    ],
}
INVOICE_CREATE_PARAMS = {
    'body': {
        'schema': INVOICE_SCHEMA,
        'required': True
    }
}

INVOICE_DELETE_PARAMS = {
    'path': [
        {
            'name': 'invoice_id',
            'type': 'integer',
            'description': 'ID of the invoice to delete',
            'required': True
        }
    ]
}



