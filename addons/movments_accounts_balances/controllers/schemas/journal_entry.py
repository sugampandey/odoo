from typing import Optional, List
from enum import Enum
from .common import (CurrencyRefModel, MetaDataModel, TaxCodeRefModel, ClassRefModel, AccountRefModel, HEADERS)
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator


class PostingType(str, Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"
    
class EntityRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: Optional[str] = None,
        value: Optional[str] = None
    ):
        self.name = name
        self.value = value
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get('name', ''),
            value=data.get('value', '')
        )
    

class EntityModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        Type: Optional[str] = None,
        EntityRef: Optional[EntityRefModel] = None,
    ):
        self.Type = Type
        self.EntityRef = EntityRef

    def to_dict(self) -> dict:
        return {
            'Type': self.Type,
            'EntityRef': self.EntityRef.to_dict() if self.EntityRef else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Type=data.get('Type', ''),
            EntityRef=EntityRefModel.from_dict(data.get('EntityRef', {})) if data.get('EntityRef') else None
        )
    

class JournalEntryLineDetailModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        PostingType: Optional[str] = None,
        AccountRef: Optional[AccountRefModel] = None,
        TaxApplicableOn : Optional[str] = None,
        ClassRef : Optional[ClassRefModel] = None,
        TaxCodeRef : Optional[TaxCodeRefModel] = None,
        Entity: Optional[EntityModel] = None
    ):
        self.PostingType = PostingType
        self.AccountRef = AccountRef
        self.TaxApplicableOn = TaxApplicableOn
        self.ClassRef = ClassRef
        self.TaxCodeRef = TaxCodeRef
        self.Entity = Entity

    def to_dict(self) -> dict:
        return {
            'PostingType': self.PostingType,
            'AccountRef': self.AccountRef.to_dict(),
            'TaxApplicableOn': self.TaxApplicableOn,
            'ClassRef': self.ClassRef.to_dict() if self.ClassRef else None,
            'TaxCodeRef': self.TaxCodeRef.to_dict() if self.TaxCodeRef else None,
            'Entity': self.Entity.to_dict() if self.Entity else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            PostingType=data.get('PostingType', ''),
            AccountRef=AccountRefModel.from_dict(data.get('AccountRef', {})),
            TaxApplicableOn=data.get('TaxApplicableOn', ''),
            ClassRef=ClassRefModel.from_dict(data.get('ClassRef', {})) if data.get('ClassRef') else None,
            TaxCodeRef=TaxCodeRefModel.from_dict(data.get('TaxCodeRef', {})) if data.get('TaxCodeRef') else None,
            Entity=EntityModel.from_dict(data.get('Entity', {})) if data.get('Entity') else None,
        )


class LineRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        JournalEntryLineDetail: JournalEntryLineDetailModel,
        DetailType: Optional[str] = None,
        Amount: Optional[float] = None,
        Description: Optional[str] = None,
        Id: Optional[str] = None,
    ):
        self.JournalEntryLineDetail = JournalEntryLineDetail
        self.DetailType = DetailType
        self.Amount = Amount
        self.Description = Description
        self.Id = Id

    def to_dict(self) -> dict:
        return {
            'JournalEntryLineDetail': self.JournalEntryLineDetail.to_dict(),
            'DetailType': self.DetailType,
            'Amount': self.Amount,
            'Description': self.Description,
            'Id': self.Id,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            JournalEntryLineDetail=JournalEntryLineDetailModel.from_dict(data.get('JournalEntryLineDetail', {})),
            DetailType=data.get('DetailType', ''),
            Amount=data.get('Amount', 0.0),
            Description=data.get('Description', ''),
            Id=data.get('Id', '')
        )

class JournalEntryRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        Line: List[LineRequestModel],
        CurrencyRef: Optional[CurrencyRefModel] = None,
    ):
        self.Line = Line
        self.CurrencyRef = CurrencyRef

    def to_dict(self) -> dict:
        return {
            'Line': [line.to_dict() for line in self.Line],
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Line=[LineRequestModel.from_dict(line_data) for line_data in data.get('Line', [])],
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {}))
        )

class DescriptionLineDetailModel(ResponseSchemaGenerator):
    def __init__(
            self,
            TaxCodeRef : Optional[TaxCodeRefModel] = None,
            ServiceDate : Optional[str] = None
            ):
        self.TaxCodeRef = TaxCodeRef
        self.ServiceDate = ServiceDate
    
    def to_dict(self):
        return {
            'TaxCodeRef': self.TaxCodeRef.to_dict() if self.TaxCodeRef else None,
            'ServiceDate': self.ServiceDate
        }
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            TaxCodeRef=TaxCodeRefModel.from_dict(data.get('TaxCodeRef', {})) if data.get('TaxCodeRef') else None,
            ServiceDate=data.get('ServiceDate', '')
        )

class LineResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        DetailType: Optional[str] = None,
        Amount: Optional[float] = None,
        Description: Optional[str] = None,
        Id: Optional[str] = None,
        JournalEntryLineDetail: Optional[JournalEntryLineDetailModel] = None,
        DescriptionLineDetail: Optional[DescriptionLineDetailModel] = None,
    ):
        if DetailType == 'JournalEntryLineDetail' and JournalEntryLineDetail is None:
            raise ValueError("JournalEntryLineDetail is required when DetailType is 'JournalEntryLineDetail'")
        if DetailType == 'DescriptionLineDetail' and DescriptionLineDetail is None:
            raise ValueError("DescriptionLineDetail is required when DetailType is 'DescriptionLineDetail'")
        
        self.JournalEntryLineDetail = JournalEntryLineDetail
        self.DescriptionLineDetail = DescriptionLineDetail
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

        if self.DetailType == 'JournalEntryLineDetail' and self.JournalEntryLineDetail:
            result['JournalEntryLineDetail'] = self.JournalEntryLineDetail.to_dict()
        elif self.DetailType == 'DescriptionLineDetail' and self.DescriptionLineDetail:
            result['DescriptionLineDetail'] = self.DescriptionLineDetail.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict):
        detail_type = data.get('DetailType', '')
        
        journal_entry_detail = None
        description_detail = None
        
        if detail_type == 'JournalEntryLineDetail':
            journal_entry_detail = JournalEntryLineDetailModel.from_dict(
                data.get('JournalEntryLineDetail', {})
            )
        elif detail_type == 'DescriptionLineDetail':
            description_detail = DescriptionLineDetailModel.from_dict(
                data.get('DescriptionLineDetail', {})
            )

        return cls(
            DetailType=detail_type,
            Amount=data.get('Amount', 0.0),
            Description=data.get('Description', ''),
            JournalEntryLineDetail=journal_entry_detail,
            DescriptionLineDetail=description_detail,
            Id=data.get('Id')
        )


class JournalEntryModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Line: List[LineResponseModel],
        SyncToken: Optional[str] = None,
        domain: Optional[str] = None,
        TxnDate: Optional[str] = None,
        sparse: Optional[bool] = None,
        Adjustment: Optional[bool] = None,
        Id: Optional[str] = None,
        TxnTaxDetail: Optional[dict] = None,
        MetaData: Optional[MetaDataModel] = None
    ):
        self.Line = Line
        self.SyncToken = SyncToken
        self.domain = domain
        self.TxnDate = TxnDate
        self.sparse = sparse
        self.Adjustment = Adjustment
        self.Id = Id
        self.TxnTaxDetail = TxnTaxDetail
        self.MetaData = MetaData

    def to_dict(self) -> dict:
        return {
            'Line': [line.to_dict() for line in self.Line],
            'SyncToken': self.SyncToken,
            'domain': self.domain,
            'TxnDate': self.TxnDate,
            'sparse': self.sparse,
            'Adjustment': self.Adjustment,
            'Id': self.Id,
            'TxnTaxDetail': self.TxnTaxDetail,
            'MetaData': self.MetaData.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Line=[LineResponseModel.from_dict(line_data) for line_data in data.get('Line', [])],
            SyncToken=data.get('SyncToken', ''),
            domain=data.get('domain', ''),
            TxnDate=data.get('TxnDate', ''),
            sparse=data.get('sparse', False),
            Adjustment=data.get('Adjustment', False),
            Id=data.get('Id', ''),
            TxnTaxDetail=data.get('TxnTaxDetail', {}),
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {}))
        )

class JournalEntryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        time: str,
        JournalEntry: JournalEntryModel
    ):
        self.time = time
        self.JournalEntry = JournalEntry

    def to_dict(self) -> dict:
        return {
            'time': self.time,
            'JournalEntry': self.JournalEntry.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            time=data.get('time', ''),
            JournalEntry=JournalEntryModel.from_dict(data.get('JournalEntry', {}))
        )
    
class JournalEntryQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        JournalEntry: list[JournalEntryModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.JournalEntry = JournalEntry
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'JournalEntry': [journalEntry.to_dict() for journalEntry in self.JournalEntry],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }
    
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            JournalEntry=[JournalEntryModel.from_dict(journalEntry_data) for journalEntry_data in data.get('JournalEntry', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )
           
class JournalEntryListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: JournalEntryQueryResponseModel,
        time: str
    ):
        self.QueryResponse = QueryResponse
        self.time = time

    def to_dict(self) -> dict:
        return {
            'QueryResponse': self.QueryResponse.to_dict(),
            'time': self.time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            QueryResponse=JournalEntryQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )


JOURNAL_ENTRY_CREATE_RESPONSE = JOURNAL_ENTRY_GET_RESPONSE = JournalEntryResponseModel.get_response_schema()
JOURNAL_ENTRY_LIST_RESPONSE = JournalEntryListResponseModel.get_response_schema()

JOURNAL_ENTRY_SCHEMA = JournalEntryRequestModel.get_request_schema()

# JOURNAL_ENTRY_RESPONSE = {
#     'type': 'object',
#     'properties': {
#         'success': {'type': 'boolean'},
#         'message': {'type': 'string'},
#         'data': {
#             'type': 'object',
#             'properties': {
#                 'id': {'type': 'integer'},
#                 'name': {'type': 'string'},
#                 'ref': {'type': 'string'},
#                 'date': {'type': 'string', 'format': 'date'},
#                 'state': {'type': 'string'},
#                 'journal': {
#                     'type': 'object',
#                     'properties': {
#                         'id': {'type': 'integer'},
#                         'name': {'type': 'string'}
#                     }
#                 },
#                 'company': {
#                     'type': 'object',
#                     'properties': {
#                         'id': {'type': 'integer'},
#                         'name': {'type': 'string'}
#                     }
#                 },
#                 'lines': {
#                     'type': 'array',
#                     'items': {
#                         'type': 'object',
#                         'properties': {
#                             'id': {'type': 'integer'},
#                             'account': {
#                                 'type': 'object',
#                                 'properties': {
#                                     'id': {'type': 'integer'},
#                                     'code': {'type': 'string'},
#                                     'name': {'type': 'string'}
#                                 }
#                             },
#                             'name': {'type': 'string'},
#                             'debit': {'type': 'number'},
#                             'credit': {'type': 'number'},
#                             'partner': {
#                                 'type': 'object',
#                                 'properties': {
#                                     'id': {'type': 'integer'},
#                                     'name': {'type': 'string'}
#                                 },
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }

# JOURNAL_ENTRY_LIST_RESPONSE = {
#     'type': 'object',
#     'properties': {
#         'success': {'type': 'boolean'},
#         'message': {'type': 'string'},
#         'data': {
#             'type': 'object',
#             'properties': {
#                 'journal_entries': {
#                     'type': 'array',
#                     'items': {
#                         'type': 'object',
#                         'properties': {
#                             'id': {'type': 'integer'},
#                             'name': {'type': 'string'},
#                             'ref': {'type': 'string'},
#                             'date': {'type': 'string', 'format': 'date'},
#                             'journal_id': {
#                                 'type': 'object',
#                                 'properties': {
#                                     'id': {'type': 'integer'},
#                                     'name': {'type': 'string'}
#                                 }
#                             },
#                             'state': {'type': 'string'},
#                             'company': {
#                                 'type': 'object',
#                                 'properties': {
#                                     'id': {'type': 'integer'},
#                                     'name': {'type': 'string'}
#                                 }
#                             },
#                         }
#                     }
#                 },
#                 'pagination': {
#                     'type': 'object',
#                     'properties': {
#                         'total_count': {'type': 'integer'},
#                         'limit': {'type': 'integer'},
#                         'offset': {'type': 'integer'}
#                     }
#                 }
#             }
#         }
#     }
# }

# JOURNAL_ENTRY_SCHEMA = {
#     'required': {
#         'date': {
#             'type': str,
#             'display_name': 'Date',
#             'format': 'date',
#             'swagger_type': 'string'
#         },
#         'line_ids': {
#             'type': list,
#             'display_name': 'Line Items',
#             'swagger_type': 'array',
#             'items': {
#                 'type': dict,
#                 'required': {
#                     'partner_id': {
#                         'type': int,
#                         'display_name': 'Partner',
#                         'swagger_type': 'integer'
#                     },
#                     'amount': {
#                         'type': float,
#                         'display_name': 'Amount',
#                         'swagger_type': 'number'
#                     },
#                     'amount_type': {
#                         'type': str,
#                         'display_name': 'Amount Type',
#                         'swagger_type': 'string',
#                         'enum': ['debit', 'credit']
#                     },
#                     'account_id': {
#                         'type': int,
#                         'display_name': 'Account',
#                         'swagger_type': 'integer'
#                     }
#                 },
#                 'optional': {
#                     'ref' : {
#                         'type': str,
#                         'display_name': 'Reference',
#                         'swagger_type': 'string'
#                     },
#                     'analytic_distribution': {
#                         'type': str,
#                         'display_name': 'Analytic Distribution',
#                         'swagger_type': 'string'
#                     }
#                 }
#             }
#         },
#         'company_id': {
#             'type': int,
#             'display_name': 'Company',
#             'swagger_type': 'integer'
#         }
#     },
#     'optional': {
#         'partner_id': {
#             'type': int,
#             'display_name': 'Partner',
#             'swagger_type': 'integer'
#         },
#         'name': {
#             'type': str,
#             'display_name': 'Name',
#             'swagger_type': 'string'
#         },
#         'ref': {
#             'type': str,
#             'display_name': 'Reference',
#             'swagger_type': 'string'
#         },
#     }
# }


# Parameters for different endpoints
JOURNAL_ENTRY_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'journal_id',
            'type': 'integer',
            'description': 'Filter by journal ID',
            'required': False
        },
        {
            'name': 'maxresults',
            'type': 'integer',
            'description': 'Number of records to return (default: 100)',
            'required': False,
            'default': 100
        },
        {
            'name': 'startposition',
            'type': 'integer',
            'description': 'Number of records to skip (default: 0)',
            'required': False,
            'default': 0
        },
        {
            'name': 'date_from',
            'type': 'string',
            'format': 'date',
            'description': 'Start date for filtering journal entries (YYYY-MM-DD). Must be used together with date_to',
            'required': False
        },
        {
            'name': 'date_to',
            'type': 'string',
            'format': 'date',
            'description': 'End date for filtering journal entries (YYYY-MM-DD). Must be used together with date_from',
            'required': False
        }
    ]
}


JOURNAL_ENTRY_GET_PARAMS = {
    'path': [
        {
            'name': 'journal_entry_id',
            'type': 'integer',
            'description': 'ID of the journal entry to retrieve',
            'required': True
        }
    ]
}

JOURNAL_ENTRY_DELETE_PARAMS = {
    'path': [
        {
            'name': 'journal_entry_id',
            'type': 'integer',
            'description': 'ID of the journal entry to delete',
            'required': True
        }
    ]
}

JOURNAL_ENTRY_CREATE_PARAMS = {
    'headers': HEADERS,
    'body': {
        'schema': JOURNAL_ENTRY_SCHEMA,
        'required': True
    }
}
