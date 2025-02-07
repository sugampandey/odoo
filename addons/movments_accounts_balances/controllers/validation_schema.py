# Validation schemas



from datetime import datetime


bank_account_expected_fields = {
    'required': {
        'acc_number': {
            'type': str,
            'display_name': 'Account Number'
        },
        'partner_id': {
            'type': int,
            'display_name': 'Partner ID'
        },
        'bank_id': {
            'type': int,
            'display_name': 'Bank ID'
        },
        'acc_holder_name': {
            'type': str,
            'display_name': 'Account Holder Name'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company ID'
        },
    },
    'optional': {
        'active': {
            'type': bool,
            'display_name': 'Active'
        }
    }
}

product_category_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Category Name'
        },
    },
    'optional': {
        'parent_id': {
            'type': int,
            'display_name': 'Parent Category ID'
        },
    }
}

product_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Product Name'
        },
        'category_id': {
            'type': int,
            'display_name': 'Product Category'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company'
        },
        'detailed_type': {
            'type': str,
            'display_name': 'Detailed Type',
        },
    },
    'optional': {
        'default_code': {
            'type': str,
            'display_name': 'Internal Reference'
        },
        'barcode': {
            'type': str,
            'display_name': 'Barcode'
        },
        'list_price': {
            'type': float,
            'display_name': 'Sales Price'
        },
        'standard_price': {
            'type': float,
            'display_name': 'Cost Price'
        },
        'description': {
            'type': str,
            'display_name': 'Description'
        },
        'description_sale': {
            'type': str,
            'display_name': 'Sales Description'
        },
        'can_be_sold': {
            'type': bool,
            'display_name': 'Can be Sold',
            'default': True
        },
        'can_be_purchased': {
            'type': bool,
            'display_name': 'Can be Purchased',
            'default': True
        },
        'weight': {
            'type': float,
            'display_name': 'Weight'
        },
        'volume': {
            'type': float,
            'display_name': 'Volume'
        },
        'attributes': {
            'type': list,
            'display_name': 'Product Attributes',
            'items': {
                'type': dict,
                'required': {
                    'name': {
                        'type': str,
                        'display_name': 'Attribute Name'
                    },
                    'values': {
                        'type': list,
                        'display_name': 'Attribute Values',
                        'items': {
                            'type': str
                        }
                    }
                },
                'optional': {
                    'display_type': {
                        'type': str,
                        'display_name': 'Display Type',
                        'default': 'radio'
                    }
                }
            }
        },
        'active': {
            'type': bool,
            'display_name': 'Active',
            'default': True
        },
        'type': {
            'type': str,
            'display_name': 'Product Type',
        },
        'taxes_id': {
            'type': list,
            'display_name': 'Customer Taxes',
            'items': {
                'type': int
            }
        },
        'supplier_taxes_id': {
            'type': list,
            'display_name': 'Vendor Taxes',
            'items': {
                'type': int
            }
        },
        'property_account_expense_id': {
            'type': int,
            'display_name': 'Expense Account'
        },
        'property_account_income_id': {
            'type': int,
            'display_name': 'Income Account'
        }
    }
}

tax_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Tax Name'
        },
        'amount': {
            'type': float,
            'display_name': 'Tax Amount'
        },
        'amount_type': {
            'type': str,
            'display_name': 'Amount Type',
        },
        'tax_group_id': {
            'type': int,
            'display_name': 'Tax Group'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company ID'
        },
    },
    'optional': {
        'description': {
            'type': str,
            'display_name': 'Description'
        },
        'active': {
            'type': bool,
            'display_name': 'Active'
        },
        'price_include': {
            'type': bool,
            'display_name': 'Included in Price'
        },
        'tax_scope': {
            'type': str,
            'display_name': 'Tax Scope',
        },
    }
}

tax_group_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Tax Group Name'
        }
    },
    'optional': {
        'country_id': {
            'type': int,
            'display_name': 'Country ID'
        }
    }
}

journal_expected_fields = {
    'required': {
        'name': {'type': str, 'display_name': 'Journal Name'},
        'code': {'type': str, 'display_name': 'Journal Code'},
        'type': {'type': str, 'display_name': 'Journal Type'},
        'company_id': {'type': int, 'display_name': 'Company'},
    },
    'optional': {
        'bank_account_id': {'type': int, 'display_name': 'Bank Account'},
        'default_account_id': {'type': int, 'display_name': 'Default Account'},
        'profit_account_id': {'type': int, 'display_name': 'Profit Account'},
        'loss_account_id': {'type': int, 'display_name': 'Loss Account'},   
    }
}

journal_entry_expected_fields = {
    'required': {
        'journal_id': {
            'type': int,
            'display_name': 'Journal',
        },
        'date': {
            'type': str,
            'display_name': 'Date',
            'format': 'date'
        },
        'line_ids': {
            'type': list,
            'display_name': 'Journal Items'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
        },
    },
    'optional': {
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
        },
        'payment_id': {
            'type': int,
            'display_name': 'Payment',
        },
        'name': {
            'type': str,
            'display_name': 'Name'
        },
        'ref': {
            'type': str,
            'display_name': 'Reference'
        },
        'state': {
            'type': str,
            'display_name': 'Status',
        },
        'move_type': {
            'type': str,
            'display_name': 'Move Type',
        },
        'payment_reference': {
            'type': str,
            'display_name': 'Payment Reference'
        },
        'payment_state': {
            'type': str,
            'display_name': 'Payment Status',
        },
        'narration': {
            'type': str,
            'display_name': 'Internal Note'
        },
        'currency_id': {
            'type': int,
            'display_name': 'Currency',
        },
    }
}

payment_method_expected_fields = {
    'required': {
        'journal_id': {
            'type': int,
            'display_name': 'Journal'
        },
        'name': {
            'type': str,
            'display_name': 'Description'
        },
    },
    'optional': {
        'code': {
            'type': str,
            'display_name': 'Code'
        },
        'payment_account_id': {
            'type': int,
            'display_name': 'Payment Account'
        }
    }
}

bank_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Name'
        },
        'bic': {
            'type': str,
            'display_name': 'BIC'
        }
    },
    'optional': {}
}

invoice_expected_fields = {
    'required': {
        'invoice_date': {
            'type': str,
            'display_name': 'Invoice Date',
            'format': 'date'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
        },
        'invoice_date_due': {
            'type': str,
            'display_name': 'Invoice Due Date',
            'format': 'date'
        },
        'line_ids': {
            'type': list,
            'display_name': 'Line Items',
            'items': {
                'type': dict,
                'required': {
                    'product_id': {
                        'type': int,
                        'display_name': 'Product'
                    },
                    'price_unit': {
                        'type': float,
                        'display_name': 'Unit Price'
                    },
                    'quantity': {
                        'type': float,
                        'display_name': 'Quantity'
                    }
                },
                'optional': {
                    'description': {
                        'type': str,
                        'display_name': 'Description'
                    },
                    'analytic_distribution': {
                        'type': str,
                        'display_name': 'Analytic Distribution'
                    },
                    'tax_id': {
                        'type': int,
                        'display_name': 'Tax'
                    },
                    'income_account_id': {
                        'type': int,
                        'display_name': 'Income Account'
                    }
                }
            }
        },
        'customer_id': {
            'type': int,
            'display_name': 'Customer',
        },
    },
    'optional': {
        'ref': {
            'type': str,
            'display_name': 'Reference'
        },
        # 'journal_id': {
        #     'type': int,
        #     'display_name': 'Journal',
        # },
        'receivable_account_id': {
            'type': int,
            'display_name': 'Receivable Account',
        },
        'currency_id': {
            'type': int,
            'display_name': 'Currency',
        },
    }
}

invoice_payment_expected_fields = {
    'required' :{ 
        'invoice_id': {
            'type': int, 
            'display_name': 'Invoice Id',
            },
        'payment_amount': {
            'type': float,
            'display_name': 'Payment Amount',
            },
        'payment_method_id': {
            'type': int,
            'display_name': 'Payment Method',
            },
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
            },
        'company_id': {
            'type': int,
            'display_name': 'Company',
        },
        },
    'optional': {
        'destination_account_id': {
            'type': int,
            'display_name': 'Account',
            },
        'payment_reference': {
            'type': str,
            'display_name': 'Payment Reference'
        },
    }
}

bill_expected_fields = {
    'required': {
        'invoice_date': {
            'type': str,
            'display_name': 'Invoice Date',
        },
        'invoice_date_due': {
            'type': str,
            'display_name': 'Invoice Due Date',
        },
        'line_ids': {
            'type': list,
            'display_name': 'Line Items'
        },
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
        },
        'company_id': {
            'type': int,
            'display_name': 'Company',
        },
    },
    'optional': {
        'ref': {
            'type': str,
            'display_name': 'Payment Reference'
        },
        'journal_id': {
            'type': int,
            'display_name': 'Journal',
        },
        'currency_id': {
            'type': int,
            'display_name': 'Currency',
        },
    }
}

bill_payment_expected_fields = {
    'required' :{ 
        'bill_id': {
            'type': int, 
            'display_name': 'Bill Id',
            },
        'payment_amount': {
            'type': float,
            'display_name': 'Payment Amount',
            },
        'payment_method_id': {
            'type': int,
            'display_name': 'Payment Method',
            },
        'partner_id': {
            'type': int,
            'display_name': 'Partner',
            },
        'company_id': {
            'type': int,
            'display_name': 'Company',
        },
        },
    'optional': {
        'account_id': {
            'type': int,
            'display_name': 'Account',
            },
        'payment_reference': {
            'type': str,
            'display_name': 'Payment Reference'
        },
    }
}

account_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Account Name'
        },
        'code': {
            'type': str,
            'display_name': 'Account Code'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company'
        },
        'account_type': {
            'type': str,
            'display_name': 'Account Type',
        }
    },
    'optional': {
        'currency_id': {
            'type': int,
            'display_name': 'Currency'
        },
        'reconcile': {
            'type': bool,
            'display_name': 'Allow Reconciliation'
        },
        'opening_debit': {
            'type': float,
            'display_name': 'Opening Debit'
        },
        'opening_credit': {
            'type': float,
            'display_name': 'Opening Credit'
        },
    }
}

analytic_account_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Analytic Account Name'
        },
        'code': {
            'type': str,
            'display_name': 'Analytic Account Code'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company'
        },
        'plan_id': {
            'type': int,
            'display_name': 'Analytic Account Plan'
        },
    },
    'optional': {}
}

partner_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Name'
        },
        'company_id': {
            'type': int,
            'display_name': 'Company'
        },
        'is_company': {
            'type': bool,
            'display_name': 'Is Company'
        },
        'email': {
            'type': str,
            'display_name': 'Email'
        },
        'phone': {
            'type': str,
            'display_name': 'Phone'
        },
        'category_id': {
            'type': int,
            'display_name': 'Category'
        }
    },
    'optional': {
        'parent_id': {
            'type': int,
            'display_name': 'Parent'
        },
        'street': {
            'type': str,
            'display_name': 'Street'
        },
        'street2': {
            'type': str,
            'display_name': 'Street 2'
        },
        'zip': {
            'type': str,
            'display_name': 'Zip'
        },
        'city': {
            'type': str,
            'display_name': 'City'
        },
        'state_id': {
            'type': int,
            'display_name': 'State'
        },
        'country_id': {
            'type': int,
            'display_name': 'Country'
        },
    },
} 

company_expected_fields = {
    'required': {
        'name': {
            'type': str,
            'display_name': 'Company Name'
        },        
        'phone': {
            'type': str,
            'display_name': 'Phone'
        },
        'email': {
            'type': str,
            'display_name': 'Email'
        },
    },
    'optional': {
        'currency_id': {
            'type': int,
            'display_name': 'Currency'
        },
        'city': {
            'type': str,
            'display_name': 'City'
        },
        'street': {
            'type': str,
            'display_name': 'Street'
        },
        'zip': {
            'type': str,
            'display_name': 'Zip'
        },
    }
}