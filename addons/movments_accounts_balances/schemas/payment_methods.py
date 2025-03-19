# Bank Account Schemas
BANK_ACCOUNT_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'acc_number': {'type': 'string'},
        'acc_holder_name': {'type': 'string'},
        'active': {'type': 'boolean'},
        'partner': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'bank': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'bic': {'type': 'string'}
            },
        },
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'create_date': {'type': 'string', 'format': 'date-time'}
    }
}
BANK_ACCOUNT_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': BANK_ACCOUNT_OBJECT
    }
}

BANK_ACCOUNT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'bank_accounts': {
                    'type': 'array',
                    'items': BANK_ACCOUNT_OBJECT
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


BANK_ACCOUNT_SCHEMA = {
    'required': {
        'acc_number': {
            'type': str,
            'display_name': 'Account Number',
            'swagger_type': 'string'
        },
        'partner_id': {
            'type': int,
            'display_name': 'Partner ID',
            'swagger_type': 'integer'
        },
        'bank_id': {
            'type': int,
            'display_name': 'Bank ID',
            'swagger_type': 'integer'
        },
        'acc_holder_name': {
            'type': str,
            'display_name': 'Account Holder Name',
            'swagger_type': 'string'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company ID',
            'swagger_type': 'integer'
        }
    },
    'optional': {
        'active': {
            'type': bool,
            'display_name': 'Active',
            'swagger_type': 'boolean'
        }
    }
}


# Payment Method Schemas
PAYMENT_METHOD_RESPONSE = {
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
                'payment_type': {'type': 'string'},
                'active': {'type': 'boolean'}
            }
        }
    }
}

PAYMENT_METHOD_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'payment_methods': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'journal': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'type': {'type': 'string'}
                                }
                            },
                            'payment_method': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'code': {'type': 'string'},
                                    'type': {'type': 'string'}
                                }
                            },
                            'payment_account': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'code': {'type': 'string'}
                                }
                            },
                            'active': {'type': 'boolean'}
                        }
                    }
                },
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'total_count': {'type': 'integer'},
                        'limit': {'type': 'integer'},
                        'offset': {'type': 'integer'}
                    },
                }
            },
        }
    },
}


PAYMENT_METHOD_SCHEMA = {
    'required': {
        'journal_id': {
            'type': int,
            'display_name': 'Journal',
            'swagger_type': 'integer'
        },
        'name': {
            'type': str,
            'display_name': 'Description',
            'swagger_type': 'string'
        }
    },
    'optional': {
        'code': {
            'type': str,
            'display_name': 'Code',
            'swagger_type': 'string'
        },
        'payment_account_id': {
            'type': int,
            'display_name': 'Payment Account',
            'swagger_type': 'integer'
        }
    }
}


# Bank Schemas
BANK_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'bic': {'type': 'string'},
        'active': {'type': 'boolean'},
        'email': {'type': 'string'},
        'phone': {'type': 'string'}
    }
}
BANK_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': BANK_OBJECT
    }
}

BANK_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'banks': {
                    'type': 'array',
                    'items': BANK_OBJECT
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


BANK_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Bank Name',
            'swagger_type': 'string'
        },
        'bic': {
            'type': str,
            'display_name': 'BIC/SWIFT Code',
            'swagger_type': 'string'
        }
    },
    'optional': {}
}

# Parameters for different endpoints
BANK_ACCOUNT_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': False
        },
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'Filter by partner ID',
            'required': False
        },
        {
            'name': 'bank_id',
            'type': 'integer',
            'description': 'Filter by bank ID',
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

BANK_ACCOUNT_GET_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the bank account to retrieve',
            'required': True
        }
    ]
}

BANK_ACCOUNT_CREATE_PARAMS = {
    'body': {
        'schema': BANK_ACCOUNT_SCHEMA,
        'required': True
    }
}

BANK_ACCOUNT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the bank account to delete',
            'required': True
        }
    ]
}

PAYMENT_METHOD_LIST_PARAMS = {
    'query': [
        {
            'name': 'payment_type',
            'type': 'string',
            'description': 'Filter by payment type',
            'required': False,
            'enum': ['inbound', 'outbound']
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
        }
    ]
}

PAYMENT_METHOD_GET_PARAMS = {
    'path': [
        {
            'name': 'payment_method_id',
            'type': 'integer',
            'description': 'ID of the payment method to retrieve',
            'required': True
        }
    ]
}


PAYMENT_METHOD_CREATE_PARAMS = {
    'body': {
        'schema': PAYMENT_METHOD_SCHEMA,
        'required': True
    }
}

PAYMENT_METHOD_DELETE_PARAMS = {
    'path': [
        {
            'name': 'payment_method_id',
            'type': 'integer',
            'description': 'ID of the payment method to delete',
            'required': True
        }
    ]
}

BANK_LIST_PARAMS = {
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
        }
    ]
}

BANK_GET_PARAMS = {
    'path': [
        {
            'name': 'bank_id',
            'type': 'integer',
            'description': 'ID of the bank to retrieve',
            'required': True
        }
    ]
}


BANK_DELETE_PARAMS = {
    'path': [
        {
            'name': 'bank_id',
            'type': 'integer',
            'description': 'ID of the bank to delete',
            'required': True
        }
    ]
}


BANK_CREATE_PARAMS = {
    'body': {
        'schema': BANK_SCHEMA,
        'required': True
    }
}
