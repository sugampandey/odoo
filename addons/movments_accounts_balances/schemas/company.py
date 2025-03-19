from typing import Optional
from datetime import datetime
from .common import (CurrencyRefModel, MetaDataModel, BillAddrModel,
                     PhoneNumberModel, EmailAddressModel, HEADERS)
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator



class CompanyCreateRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        Name: str,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        BillAddr: Optional[BillAddrModel] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
    ):
        self.Name = Name
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.PrimaryPhone = PrimaryPhone
        self.BillAddr = BillAddr
        self.CurrencyRef = CurrencyRef

    def to_dict(self) -> dict:
        return {
            'Name': self.Name,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Name=data.get('Name', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})),
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})),
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})),
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {}))
        )

class CompanyModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Name: str,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        BillAddr: Optional[BillAddrModel] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
        MetaData: Optional[MetaDataModel] = None,
        Active: Optional[bool] = True,
        Id: Optional[str] = None
    ):
        self.Name = Name
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.PrimaryPhone = PrimaryPhone
        self.BillAddr = BillAddr
        self.CurrencyRef = CurrencyRef
        self.MetaData = MetaData
        self.Active = Active
        self.Id = Id

    def to_dict(self) -> dict:
        return {
            'Name': self.Name,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
            'MetaData': self.MetaData.to_dict() if self.MetaData else None,
            'Active': self.Active,
            'Id': self.Id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Name=data.get('Name', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})),
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})),
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})),
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {})),
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {})),
            Active=data.get('Active', True),
            Id=data.get('Id')
        )

class CompanyResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Company: CompanyModel,
        time: str
    ):
        self.Company = Company
        self.time = time

    def to_dict(self) -> dict:
        return {
            'Company': self.Company.to_dict(),
            'time': self.time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Company=CompanyModel.from_dict(data.get('Company', {})),
            time=data.get('time')
        )
    

class CompanyQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        Company: list[CompanyModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.Company = Company
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'Company': [company.to_dict() for company in self.Company],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }
    
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            Company=[CompanyModel.from_dict(company_data) for company_data in data.get('Company', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )
           
class CompanyListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: CompanyQueryResponseModel,
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
            QueryResponse=CompanyQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )

COMPANY_CREATE_RESPONSE = COMPANY_GET_RESPONSE = CompanyResponseModel.get_response_schema()
COMPANY_LIST_RESPONSE = CompanyListResponseModel.get_response_schema()

COMPANY_SCHEMA = CompanyCreateRequestModel.get_request_schema()




# COMPANY_OBJECT = {
#     'type': 'object',
#     'properties': {
#         'id': {'type': 'integer'},
#         'name': {'type': 'string'},
#         'city': {'type': 'string'},
#         'street': {'type': 'string'},
#         'phone': {'type': 'string'},
#         'zip': {'type': 'string'},
#         'email': {'type': 'string'},
#         'active': {'type': 'boolean'},
#         'currency': {
#             'type': 'object',
#             'properties': {
#                 'id': {'type': 'integer'},
#                 'name': {'type': 'string'},
#                 'symbol': {'type': 'string'}
#             },
#         }
#     }
# }



# COMPANY_RESPONSE = {
#     'type': 'object',
#     'properties': {
#         'success': {'type': 'boolean'},
#         'message': {'type': 'string'},
#         'data': COMPANY_OBJECT
#     }
# }

# COMPANY_LIST_RESPONSE = {
#     'type': 'object',
#     'properties': {
#         'success': {'type': 'boolean'},
#         'message': {'type': 'string'},
#         'data': {
#             'type': 'object',
#             'properties': {
#                 'companies': {
#                     'type': 'array',
#                     'items': COMPANY_OBJECT
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


# COMPANY_SCHEMA = {
#     'required': {
#         'name': {
#             'type': str,
#             'display_name': 'Company Name',
#             'swagger_type': 'string'
#         },
#         'email': {
#             'type': str,
#             'display_name': 'Email',
#             'format': 'email',
#             'swagger_type': 'string'
#         },
#         'phone': {
#             'type': str,
#             'display_name': 'Phone Number',
#             'swagger_type': 'string'
#         }
#     },
#     'optional': {
#         'street': {
#             'type': str,
#             'display_name': 'Street Address',
#             'swagger_type': 'string'
#         },
#         'city': {
#             'type': str,
#             'display_name': 'City',
#             'swagger_type': 'string'
#         },
#         'zip': {
#             'type': str,
#             'display_name': 'ZIP Code',
#             'swagger_type': 'string'
#         },
#         'currency_id': {
#             'type': int,
#             'display_name': 'Currency',
#             'swagger_type': 'integer',
#             'default': 2  # Default USD
#         },
#     }
# }

# Parameters for different endpoints
COMPANY_LIST_PARAMS = {
    'query': [
        {
            'name': 'name',
            'type': 'string',
            'description': 'Filter by name',
            'required': False
        },
        {
            'name': 'active',
            'type': 'boolean',
            'description': 'Filter by active status',
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
    ]
}

COMPANY_GET_PARAMS = {
    'path': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'ID of the company to retrieve',
            'required': True
        }
    ]
}

COMPANY_DELETE_PARAMS = {
    'path': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'ID of the company to delete',
            'required': True
        }
    ]
}

COMPANY_CREATE_PARAMS = {
    'body': {
        'schema': COMPANY_SCHEMA,
        'required': True
    }
}
