# Product Category Schemas
PRODUCT_CATEGORY_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'complete_name': {'type': 'string'},
                'parent': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'}
                    },
                },
                'child_categories': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'complete_name': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
}

PRODUCT_CATEGORY_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'categories': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'complete_name': {'type': 'string'},
                            'parent_id': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                },
                                'nullable': True
                            },
                            'child_categories': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'},
                                        'complete_name': {'type': 'string'}
                                    }
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
            }
        }
    }
}


PRODUCT_CATEGORY_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Category Name',
            'swagger_type': 'string'
        }
    },
    'optional': {
        'parent_id': {
            'type': int,
            'display_name': 'Parent Category',
            'swagger_type': 'integer'
        }
    }
}

# Product Schemas
PRODUCT_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'default_code': {'type': 'string', 'nullable': True},
        'barcode': {'type': 'string', 'nullable': True},
        'type': {'type': 'string'},
        'detailed_type': {'type': 'string'},
        'list_price': {'type': 'number'},
        'standard_price': {'type': 'number'},
        'category': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'complete_name': {'type': 'string'}
            }
        },
        'can_be_sold': {'type': 'boolean'},
        'can_be_purchased': {'type': 'boolean'},
        'active': {'type': 'boolean'},
        'weight': {'type': 'number'},
        'volume': {'type': 'number'},
        'description': {'type': 'string', 'nullable': True},
        'accounts': {
            'type': 'object',
            'properties': {
                'income': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'code': {'type': 'string'},
                        'name': {'type': 'string'},
                        'is_category_account': {'type': 'boolean'}
                    },
                    'nullable': True
                },
                'expense': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'code': {'type': 'string'},
                        'name': {'type': 'string'},
                        'is_category_account': {'type': 'boolean'}
                    },
                    'nullable': True
                }
            }
        },
        'taxes': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'amount': {'type': 'number'},
                    'type': {'type': 'string'}
                }
            }
        },
        'supplier_taxes': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'amount': {'type': 'number'},
                    'type': {'type': 'string'}
                }
            }
        },
        'variants': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'default_code': {'type': 'string', 'nullable': True},
                    'barcode': {'type': 'string', 'nullable': True},
                    'attribute_values': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'attribute': {'type': 'string'},
                                'value': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    }
}

PRODUCT_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': PRODUCT_OBJECT
    }
}


PRODUCT_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'products': {
                    'type': 'array',
                    'items': PRODUCT_OBJECT
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


PRODUCT_SCHEMA = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Product Name',
            'swagger_type': 'string'
        },
        'category_id': {
            'type': int,
            'display_name': 'Product Category',
            'swagger_type': 'integer'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
            'swagger_type': 'integer'
        },
        'detailed_type': {
            'type': str,
            'display_name': 'Detailed Type',
            'swagger_type': 'string'
        }
    },
    'optional': {
        'default_code': {
            'type': str,
            'display_name': 'Internal Reference',
            'swagger_type': 'string'
        },
        'barcode': {
            'type': str,
            'display_name': 'Barcode',
            'swagger_type': 'string'
        },
        'list_price': {
            'type': float,
            'display_name': 'Sales Price',
            'swagger_type': 'number'
        },
        'standard_price': {
            'type': float,
            'display_name': 'Cost Price',
            'swagger_type': 'number'
        },
        'description': {
            'type': str,
            'display_name': 'Description',
            'swagger_type': 'string'
        },
        'description_sale': {
            'type': str,
            'display_name': 'Sales Description',
            'swagger_type': 'string'
        },
        'can_be_sold': {
            'type': bool,
            'display_name': 'Can be Sold',
            'swagger_type': 'boolean',
            'default': True
        },
        'can_be_purchased': {
            'type': bool,
            'display_name': 'Can be Purchased',
            'swagger_type': 'boolean',
            'default': True
        },
        'weight': {
            'type': float,
            'display_name': 'Weight',
            'swagger_type': 'number'
        },
        'volume': {
            'type': float,
            'display_name': 'Volume',
            'swagger_type': 'number'
        },
        'attributes': {
            'type': list,
            'display_name': 'Product Attributes',
            'swagger_type': 'array',
            'items': {
                'type': dict,
                'required': {
                    'name': {
                        'type': str,
                        'display_name': 'Attribute Name',
                        'swagger_type': 'string'
                    },
                    'values': {
                        'type': list,
                        'display_name': 'Attribute Values',
                        'swagger_type': 'array',
                        'items': {
                            'type': str,
                            'swagger_type': 'string'
                        }
                    }
                },
                'optional': {
                    'display_type': {
                        'type': str,
                        'display_name': 'Display Type',
                        'swagger_type': 'string',
                        'default': 'radio'
                    }
                }
            }
        },
        'active': {
            'type': bool,
            'display_name': 'Active',
            'swagger_type': 'boolean',
            'default': True
        },
        'type': {
            'type': str,
            'display_name': 'Product Type',
            'swagger_type': 'string'
        },
        'taxes_id': {
            'type': list,
            'display_name': 'Customer Taxes',
            'swagger_type': 'array',
            'items': {
                'type': int,
                'swagger_type': 'integer'
            }
        },
        'supplier_taxes_id': {
            'type': list,
            'display_name': 'Vendor Taxes',
            'swagger_type': 'array',
            'items': {
                'type': int,
                'swagger_type': 'integer'
            }
        },
        'property_account_expense_id': {
            'type': int,
            'display_name': 'Expense Account',
            'swagger_type': 'integer'
        },
        'property_account_income_id': {
            'type': int,
            'display_name': 'Income Account',
            'swagger_type': 'integer'
        }
    }
}


# Parameters for different endpoints
PRODUCT_CATEGORY_LIST_PARAMS = {
    'query': [
        {
            'name': 'parent_id',
            'type': 'integer',
            'description': 'Filter by parent category ID',
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

PRODUCT_LIST_PARAMS = {
    'query': [
        {
            'name': 'category_id',
            'type': 'integer',
            'description': 'Filter by category ID',
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
            'name': 'active',
            'type': 'boolean',
            'description': 'Filter by active status',
            'required': False,
            'default': True
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': False
        }
    ]
}


PRODUCT_GET_PARAMS = {
    'path': [
        {
            'name': 'product_id',
            'type': 'integer',
            'description': 'ID of the product to retrieve',
            'required': True
        }
    ]
}

PRODUCT_CATEGORY_GET_PARAMS = {
    'path': [
        {
            'name': 'category_id',
            'type': 'integer',
            'description': 'ID of the category to retrieve',
            'required': True
        }
    ]
}

PRODUCT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'product_id',
            'type': 'integer',
            'description': 'ID of the product to delete',
            'required': True
        }
    ]
}

PRODUCT_CATEGORY_DELETE_PARAMS = {
    'path': [
        {
            'name': 'category_id',
            'type': 'integer',
            'description': 'ID of the category to delete',
            'required': True
        }
    ]
}

PRODUCT_CREATE_PARAMS = {
    'body': {
        'schema': PRODUCT_SCHEMA,
        'required': True
    }
}

PRODUCT_CATEGORY_CREATE_PARAMS = {
    'body': {
        'schema': PRODUCT_CATEGORY_SCHEMA,
        'required': True
    }
}
