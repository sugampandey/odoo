from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any

class OptionModel(BaseModel):
    Name: Optional[str] = None
    Value: Optional[str] = None


class HeaderModel(BaseModel):
    Time: str
    ReportName: str 
    ReportBasis: str 
    StartPeriod: Optional[str] = None
    EndPeriod: Optional[str] = None
    Currency: str 
    Option: Optional[List[OptionModel]] = None
    DateMacro: Optional[str] = None
    SummarizeColumnsBy: Optional[str] = None


class MetaDataModel(BaseModel):
    Name: str
    Value: str

class ColumnModel(BaseModel):
    ColTitle: str
    ColType: str 
    MetaData: List[MetaDataModel] = Field(default_factory=list)

class ColumnsModel(BaseModel):
    Column: List[ColumnModel]

class ColDataModel(BaseModel):
    value: Any
    id: Optional[int] = None

class DataRowModel(BaseModel):
    ColData: List[ColDataModel]
    type: str 

class SummaryModel(BaseModel):
    ColData: List[ColDataModel]

class SectionHeaderModel(BaseModel):
    ColData: List[ColDataModel]

class NestedRowsModel(BaseModel):
    Row: List[Union['SectionRowModel', DataRowModel]]

class SectionRowModel(BaseModel):
    Header: SectionHeaderModel
    Rows: NestedRowsModel
    type: str 
    Summary: SummaryModel
    group: Optional[str] = None

class RowsModel(BaseModel):
    Row: List[SectionRowModel]

class ReportResponseModel(BaseModel):
    Header: HeaderModel
    Columns: ColumnsModel
    Rows: RowsModel

# Handle forward references
SectionRowModel.model_rebuild()



# General Ledger Report Schema
GENERAL_LEDGER_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'summary': {
                    'type': 'object',
                    'properties': {
                        'total_debit': {'type': 'number'},
                        'total_credit': {'type': 'number'},
                        'net_balance': {'type': 'number'},
                        'entry_count': {'type': 'integer'}
                    }
                },
                'ledger_entries': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'date': {'type': 'string', 'format': 'date'},
                            'move': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'ref': {'type': 'string'},
                                    'state': {'type': 'string'}
                                }
                            },
                            'journal': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'type': {'type': 'string'}
                                }
                            },
                            'account': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'code': {'type': 'string'},
                                    'name': {'type': 'string'},
                                    'type': {'type': 'string'}
                                }
                            },
                            'partner': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                },
                            },
                            'ref': {'type': 'string'},
                            'name': {'type': 'string'},
                            'debit': {'type': 'number'},
                            'credit': {'type': 'number'},
                            'balance': {'type': 'number'},
                            'running_balance': {'type': 'number'},
                            'analytic_distribution': {'type': 'object'},
                            'amount_currency': {'type': 'number'},
                            'reconciled': {'type': 'boolean'},
                            'full_reconcile_id': {'type': 'integer'},
                            'matching_number': {'type': 'string'}
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


# Partner Balance Report Schema
PARTNER_BALANCE_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'partner': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'ref': {'type': 'string'},
                        'customer_rank': {'type': 'integer'},
                        'supplier_rank': {'type': 'integer'}
                    }
                },
                'balances': {
                    'type': 'object',
                    'properties': {
                        'receivable': {
                            'type': 'object',
                            'properties': {
                                'balance': {'type': 'number'},
                                'total_debit': {'type': 'number'},
                                'total_credit': {'type': 'number'},
                                'transaction_count': {'type': 'integer'}
                            }
                        },
                        'payable': {
                            'type': 'object',
                            'properties': {
                                'balance': {'type': 'number'},
                                'total_debit': {'type': 'number'},
                                'total_credit': {'type': 'number'},
                                'transaction_count': {'type': 'integer'}
                            }
                        },
                        'net_position': {'type': 'number'}
                    }
                },
                'transactions': {
                    'type': 'object',
                    'properties': {
                        'receivable': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'date': {'type': 'string', 'format': 'date'},
                                    'name': {'type': 'string'},
                                    'journal': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer'},
                                            'name': {'type': 'string'},
                                            'type': {'type': 'string'}
                                        }
                                    },
                                    'debit': {'type': 'number'},
                                    'credit': {'type': 'number'},
                                    'balance': {'type': 'number'},
                                    'reconciled': {'type': 'boolean'},
                                    'amount_currency': {'type': 'number'},
                                    'ref': {'type': 'string'},
                                    'move_type': {'type': 'string'}
                                }
                            }
                        },
                        'payable': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'date': {'type': 'string', 'format': 'date'},
                                    'name': {'type': 'string'},
                                    'journal': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer'},
                                            'name': {'type': 'string'},
                                            'type': {'type': 'string'}
                                        }
                                    },
                                    'debit': {'type': 'number'},
                                    'credit': {'type': 'number'},
                                    'balance': {'type': 'number'},
                                    'reconciled': {'type': 'boolean'},
                                    'amount_currency': {'type': 'number'},
                                    'ref': {'type': 'string'},
                                    'move_type': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                'summary': {
                    'type': 'object',
                    'properties': {
                        'total_invoiced': {'type': 'number'},
                        'total_bills': {'type': 'number'},
                        'total_payments_received': {'type': 'number'},
                        'total_payments_made': {'type': 'number'}
                    }
                }
            }
        }
    }
}



# Journal Entries Report Schema
JOURNAL_ENTRIES_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'journal_entries': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'date': {'type': 'string', 'format': 'date'},
                            'journal': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'type': {'type': 'string'}
                                }
                            },
                            'move_number': {'type': 'string'},
                            'ref': {'type': 'string'},
                            'lines': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'account': {
                                            'type': 'object',
                                            'properties': {
                                                'id': {'type': 'integer'},
                                                'code': {'type': 'string'},
                                                'name': {'type': 'string'}
                                            }
                                        },
                                        'partner': {
                                            'type': 'object',
                                            'properties': {
                                                'id': {'type': 'integer'},
                                                'name': {'type': 'string'}
                                            },
                                        },
                                        'label': {'type': 'string'},
                                        'debit': {'type': 'number'},
                                        'credit': {'type': 'number'}
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

# Analytic Balance Report Schema
ANALYTIC_BALANCE_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'analytic_balances': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'account_name': {'type': 'string'},
                            'code': {'type': 'string'},
                            'balance': {'type': 'number'},
                            'debit': {'type': 'number'},
                            'credit': {'type': 'number'},
                            'details': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'date': {'type': 'string', 'format': 'date'},
                                        'name': {'type': 'string'},
                                        'amount': {'type': 'number'},
                                        'reference': {'type': 'string'},
                                        'partner': {
                                            'type': 'object',
                                            'properties': {
                                                'id': {'type': 'integer'},
                                                'name': {'type': 'string'}
                                            },
                                        },
                                        'type': {'type': 'string'},
                                        'product': {
                                            'type': 'object',
                                            'properties': {
                                                'id': {'type': 'integer'},
                                                'name': {'type': 'string'}
                                            },
                                        }
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


# Report Parameters
GENERAL_LEDGER_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID',
            'required': True
        },
        {
            'name': 'columns',
            'type': 'string',
            'description': 'Columns Name (Separated by commas)',
            'required': True
        },
        {
            'name': 'start_date',
            'type': 'string',
            'format': 'date',
            'description': 'Start date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'end_date',
            'type': 'string',
            'format': 'date',
            'description': 'End date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'Filter by partner ID',
            'required': False
        },
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'Filter by account ID',
            'required': False
        },
        {
            'name': 'sort_by',
            'type': 'string',
            'description': 'Sort by',
            'required': False
        },
        {
            'name': 'sort_order',
            'type': 'string',
            'description': 'Sort order (asc or desc)',
            'required': False
        },
        {
            'name': 'analytic_class_id',
            'type': 'integer',
            'description': 'Filter by analytic class ID',
            'required': False
        },
        {
            'name': 'include_unposted',
            'type': 'boolean',
            'description': 'Include unposted entries',
            'required': False,
            'default': False
        },

    ]
}

ACCOUNT_BALANCE_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID',
            'required': True
        },
        {
            'name': 'end_date',
            'type': 'string',
            'format': 'date',
            'description': 'End date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'Filter by account ID',
            'required': False
        }
    ]
}

PARTNER_BALANCE_PARAMS = {
    'query': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'Partner ID',
            'required': True
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID',
            'required': True
        }
    ]
}


# Parameters for Journal Entries Report
JOURNAL_ENTRIES_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID',
            'required': True
        },
        {
            'name': 'journal_ids',
            'type': 'string',
            'description': 'List of journal IDs (e.g., [1,2,3])',
            'required': False
        },
        {
            'name': 'date_from',
            'type': 'string',
            'format': 'date',
            'description': 'Start date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date (YYYY-MM-DD)',
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

# Parameters for Analytic Balance Report
ANALYTIC_BALANCE_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID',
            'required': True
        },
        {
            'name': 'date_from',
            'type': 'string',
            'format': 'date',
            'description': 'Start date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date (YYYY-MM-DD)',
            'required': False
        },
        {
            'name': 'account_ids',
            'type': 'string',
            'description': 'List of account IDs (e.g., [1,2,3])',
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
