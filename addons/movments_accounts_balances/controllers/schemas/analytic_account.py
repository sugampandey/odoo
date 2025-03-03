from typing import Optional, Literal, get_type_hints, Type, Union, Any
from datetime import datetime
from .common import ParentRef, MetaDataModel, HEADERS
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator

class AnalyticClassCreateRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        Name: str,
        ParentRef: Optional[ParentRef] = None,
    ):
        self.Name = Name
        self.ParentRef = ParentRef

    def to_dict(self):
        return {
            'Name': self.Name,
            'ParentRef': self.ParentRef.to_dict() if self.ParentRef else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Name=data.get('Name'),
            ParentRef=ParentRef.from_dict(data.get('ParentRef', {})),
        )

class AnalyticClassModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Name: str,
        FullyQualifiedName: Optional[str] = None,
        domain: Optional[str] = None,
        SubClass: Optional[bool] = None,
        sparse: Optional[bool] = None,
        Active: Optional[bool] = None,
        Id: Optional[str] = None,
        MetaData: Optional[MetaDataModel] = None,
        ParentRef: Optional[ParentRef] = None,
        SyncToken: Optional[str] = None,
    ):
        self.FullyQualifiedName = FullyQualifiedName
        self.domain = domain
        self.Name = Name
        self.SubClass = SubClass
        self.sparse = sparse
        self.Active = Active
        self.Id = Id
        self.MetaData = MetaData
        self.ParentRef = ParentRef
        self.SyncToken = SyncToken

    def to_dict(self):
        return {
            'FullyQualifiedName': self.FullyQualifiedName,
            'domain': self.domain,
            'Name': self.Name,
            'SubClass': self.SubClass,
            'sparse': self.sparse,
            'Active': self.Active,
            'Id': self.Id,
            'MetaData': self.MetaData.to_dict() if self.MetaData else None,
            'ParentRef': self.ParentRef.to_dict() if self.ParentRef else None,
            'SyncToken': self.SyncToken,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            FullyQualifiedName=data.get('FullyQualifiedName'),
            domain=data.get('domain'),
            Name=data.get('Name'),
            SubClass=data.get('SubClass'),
            sparse=data.get('sparse'),
            Active=data.get('Active'),
            Id=data.get('Id'),
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {})),
            ParentRef=ParentRef.from_dict(data.get('ParentRef', {})),
            SyncToken=data.get('SyncToken'),
        )

class AnalyticClassResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Class: AnalyticClassModel,
        time: str
    ):
        self.Class = Class
        self.time = time

    def to_dict(self) -> dict:
        return {
            'Class': self.Class.to_dict(),
            'time': self.time
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Class=AnalyticClassModel.from_dict(data.get('Class', {})),
            time=data.get('time', '')
        )
    

class AnalyticClassQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        Class: list[AnalyticClassModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.Class = Class
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'Class': [Class.to_dict() for Class in self.Class],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            Class=[AnalyticClassModel.from_dict(Class_data) for Class_data in data.get('Class', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )


class AnalyticClassListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: AnalyticClassQueryResponseModel,
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
            QueryResponse=AnalyticClassQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )
    
ANALYTIC_ACCOUNT_CREATE_RESPONSE = ANALYTIC_ACCOUNT_GET_RESPONSE = AnalyticClassResponseModel.get_schema()
ANALYTIC_ACCOUNT_LIST_RESPONSE = AnalyticClassListResponseModel.get_schema()

ANALYTIC_ACCOUNT_SCHEMA = AnalyticClassCreateRequestModel.get_schema()

ANALYTIC_ACCOUNT_CREATE_PARAMS = {
    'headers': HEADERS,
    'body': {
        'schema': ANALYTIC_ACCOUNT_SCHEMA,
        'required': True
    }
}

# Parameters for different endpoints
ANALYTIC_ACCOUNT_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': False
        },
        {
            'name': 'active',
            'type': 'boolean',
            'description': 'Filter by active status',
            'required': False
        },
        {
            'name': 'maxResults',
            'type': 'integer',
            'description': 'Number of records to return (default: 100)',
            'required': False,
            'default': 20
        },
        {
            'name': 'startPosition',
            'type': 'integer',
            'description': 'Number of records to skip (default: 0)',
            'required': False,
            'default': 0
        },
    ]
}

ANALYTIC_ACCOUNT_GET_PARAMS = {
    'path': [
        {
            'name': 'analytic_class_id',
            'type': 'integer',
            'description': 'ID of the analytic class to retrieve',
            'required': True
        }
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
    ]
}

ANALYTIC_ACCOUNT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'analytic_class_id',
            'type': 'integer',
            'description': 'ID of the analytic class to delete',
            'required': True
        }
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Company ID for validation',
            'required': True
        }
    ]
}
