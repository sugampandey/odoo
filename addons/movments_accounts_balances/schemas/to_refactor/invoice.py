from typing import Optional, List
from ..common import MetaDataModel, RefModel
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator


class SalesItemLineDetailModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        TaxInclusiveAmt: Optional[float] = None,
        DiscountAmt: Optional[float] = None,
        ItemRef: Optional[RefModel] = None,
        ClassRef : Optional[RefModel] = None,
        TaxCodeRef : Optional[RefModel] = None,
        ItemAccountRef: Optional[RefModel] = None,
        ServiceDate: Optional[str] = None,
        DiscountRate: Optional[float] = None,
        Qty: Optional[float] = None,
        UnitPrice: Optional[float] = None,
    ):
        self.TaxInclusiveAmt = TaxInclusiveAmt
        self.DiscountAmt = DiscountAmt
        self.ItemRef = ItemRef
        self.ClassRef = ClassRef
        self.TaxCodeRef = TaxCodeRef
        self.ItemAccountRef = ItemAccountRef
        self.ServiceDate = ServiceDate
        self.DiscountRate = DiscountRate
        self.Qty = Qty
        self.UnitPrice = UnitPrice

    def to_dict(self) -> dict:
        return {
            'TaxInclusiveAmt': self.TaxInclusiveAmt,
            'DiscountAmt': self.DiscountAmt,
            'ItemRef': self.ItemRef.to_dict() if self.ItemRef else None,
            'ClassRef': self.ClassRef.to_dict() if self.ClassRef else None,
            'TaxCodeRef': self.TaxCodeRef.to_dict() if self.TaxCodeRef else None,
            'ItemAccountRef': self.ItemAccountRef.to_dict() if self.ItemAccountRef else None,
            'ServiceDate': self.ServiceDate,
            'DiscountRate': self.DiscountRate,
            'Qty': self.Qty,
            'UnitPrice': self.UnitPrice
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            TaxInclusiveAmt=data.get('TaxInclusiveAmt', 0.0),
            DiscountAmt=data.get('DiscountAmt', 0.0),
            ItemRef=RefModel.from_dict(data.get('ItemRef', {})) if data.get('ItemRef') else None,
            ClassRef=RefModel.from_dict(data.get('ClassRef', {})) if data.get('ClassRef') else None,
            TaxCodeRef=RefModel.from_dict(data.get('TaxCodeRef', {})) if data.get('TaxCodeRef') else None,
            ItemAccountRef=RefModel.from_dict(data.get('ItemAccountRef', {})) if data.get('ItemAccountRef') else None,
            ServiceDate=data.get('ServiceDate', ''),
            DiscountRate=data.get('DiscountRate', 0.0),
            Qty=data.get('Qty', 0.0),
            UnitPrice=data.get('UnitPrice', 0.0)
        )
        

class InvoiceLineRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        SalesItemLineDetail: SalesItemLineDetailModel,
        DetailType: Optional[str] = None,
        Amount: Optional[float] = None,
        Description: Optional[str] = None,
        Id: Optional[str] = None,
    ):
        self.SalesItemLineDetail = SalesItemLineDetail
        self.DetailType = DetailType
        self.Amount = Amount
        self.Description = Description
        self.Id = Id

    def to_dict(self) -> dict:
        return {
            'SalesItemLineDetail': self.SalesItemLineDetail.to_dict(),
            'DetailType': self.DetailType,
            'Amount': self.Amount,
            'Description': self.Description,
            'Id': self.Id,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            SalesItemLineDetail=SalesItemLineDetailModel.from_dict(data.get('SalesItemLineDetail', {})),
            DetailType=data.get('DetailType', ''),
            Amount=data.get('Amount', 0.0),
            Description=data.get('Description', ''),
            Id=data.get('Id', '')
        )
    

class InvoiceRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        Line: List[InvoiceLineRequestModel],
        CurrencyRef: Optional[RefModel] = None,
        CustomerRef: Optional[RefModel] = None,
        ProjectRef: Optional[RefModel] = None,
    ):
        self.Line = Line
        self.CurrencyRef = CurrencyRef
        self.CustomerRef = CustomerRef
        self.ProjectRef = ProjectRef

    def to_dict(self) -> dict:
        return {
            'Line': [line.to_dict() for line in self.Line],
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
            'CustomerRef': self.CustomerRef.to_dict() if self.CustomerRef else None,
            'ProjectRef': self.ProjectRef.to_dict() if self.ProjectRef else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Line=[InvoiceLineRequestModel.from_dict(line_data) for line_data in data.get('Line', [])],
            CurrencyRef=RefModel.from_dict(data.get('CurrencyRef', {})),
            CustomerRef=RefModel.from_dict(data.get('CustomerRef', {})),
            ProjectRef=RefModel.from_dict(data.get('ProjectRef', {}))
        )

class InvoiceLineResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        DetailType: Optional[str] = None,
        Amount: Optional[float] = None,
        Description: Optional[str] = None,
        Id: Optional[str] = None,
        SalesItemLineDetail: Optional[SalesItemLineDetailModel] = None,
    ):
        if DetailType == 'SalesItemLineDetail' and SalesItemLineDetail is None:
            raise ValueError("SalesItemLineDetail is required when DetailType is 'SalesItemLineDetail'")
        
        self.SalesItemLineDetail = SalesItemLineDetail
        self.DetailType = DetailType
        self.Amount = Amount
        self.Description = Description
        self.Id = Id

    def to_dict(self) -> dict:
        result = {
            'DetailType': self.DetailType,
            'Amount': self.Amount,
            'Description': self.Description,
            'Id': self.Id
        }

        if self.DetailType == 'SalesItemLineDetail' and self.SalesItemLineDetail:
            result['SalesItemLineDetail'] = self.SalesItemLineDetail.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict):
        detail_type = data.get('DetailType', '')
        
        journal_entry_detail = None
        description_detail = None
        
        if detail_type == 'SalesItemLineDetail':
            journal_entry_detail = SalesItemLineDetailModel.from_dict(
                data.get('SalesItemLineDetail', {})
            )

        return cls(
            DetailType=detail_type,
            Amount=data.get('Amount', 0.0),
            Description=data.get('Description', ''),
            SalesItemLineDetail=journal_entry_detail,
            DescriptionLineDetail=description_detail,
            Id=data.get('Id')
        )

class InvoiceModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Line: List[InvoiceLineResponseModel],
        Id: Optional[str] = None,
        

        CustomerRef: Optional[RefModel] = None,
        SyncToken: Optional[str] = None,
        # ShipFromAddr : Optional[ShipFromAddr] = None,
        CurrencyRef: Optional[RefModel] = None,
        ProjectRef: Optional[RefModel] = None,
        BillEmail: Optional[str] = None,
        TxnDate: Optional[str] = None,
        ShipDate: Optional[str] = None,
        TrackingNum: Optional[str] = None,
        ClassRef: Optional[RefModel] = None,
        TxnSource: Optional[str] = None,
        # LinkedTxn: Optional[str] = None, will be List no use 
        DepositToAccountRef: Optional[RefModel] = None,
        AllowOnlineACHPayment: Optional[bool] = False,
        DueDate: Optional[str] = None,
        MetaData: Optional[MetaDataModel] = None,
        PrivateNote: Optional[str] = None,


    ):
        pass
    


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
                'items':{
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



