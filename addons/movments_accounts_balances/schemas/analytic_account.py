from typing import List, Optional, Literal, get_type_hints, Type, Union, Any
import uuid
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .common import ParentRefModel, MetaDataModel, HEADERS, PaginationMixin
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator


class MetaDataModel(BaseModel):
    CreateTime: datetime
    LastUpdatedTime: datetime

class ParentRefModel(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None

class AnalyticClassCreateRequestModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    ParentRef: Optional[ParentRefModel] = Field(None, description="Parent reference")

    class Config:
        from_attributes = True

    def create_analytic_class_vals(self, company_id: int) -> dict:
        return {
            "name": self.Name,
            "code": str(uuid.uuid4()).replace('-', '.'),
            "company_id": company_id
        }


class AnalyticClassModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    FullyQualifiedName: Optional[str] = None
    domain: Optional[str] = None
    SubClass: Optional[bool] = False
    sparse: Optional[bool] = False
    Active: Optional[bool] = True
    Id: Optional[int] = None
    MetaData: Optional[MetaDataModel] = None
    ParentRef: Optional[ParentRefModel] = None
    SyncToken: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def analytic_class_object(cls, analytic_class: dict) -> "AnalyticClassModel":
        meta_data = MetaDataModel(
                CreateTime=analytic_class.create_date,
                LastUpdatedTime=analytic_class.write_date
            )
        return cls(
            Name=analytic_class.name,
            Active=analytic_class.active,
            Id=analytic_class.id,
            MetaData=meta_data,
        )

class AnalyticClassQueryResponseModel(PaginationMixin):
    totalCount: int = Field(..., description="Total count of records")
    Class: List[AnalyticClassModel]

    @field_validator('Class')
    def validate_class(cls, analytic_class: list[AnalyticClassModel]) -> list[AnalyticClassModel]:
        if not analytic_class:
            raise ValueError("No analytic class found")
        return analytic_class
    
class AnalyticClassResponseModel(BaseModel):
    Class: AnalyticClassModel
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def create_analytic_class_response(cls, analytic_class: AnalyticClassModel) -> "AnalyticClassResponseModel":
        return cls(
            Class=AnalyticClassModel.analytic_class_object(analytic_class),
            time=datetime.now()
        )
    

class AnalyticClassListResponseModel(BaseModel):
    QueryResponse: AnalyticClassQueryResponseModel = Field(..., description="Query response containing analytic class list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def list_analytic_class_response(cls, analytic_classes: List[AnalyticClassModel], total_count : int, start_position: int = 0, max_results: int = 100) -> "AnalyticClassListResponseModel":
        query_response = AnalyticClassQueryResponseModel(
            startPosition=start_position,
            maxResults=max_results,
            totalCount=total_count,
            Class=analytic_classes
        )
        return cls(
            QueryResponse=query_response,
            time=datetime.now()
        )
    
# ANALYTIC_ACCOUNT_CREATE_RESPONSE = ANALYTIC_ACCOUNT_GET_RESPONSE = AnalyticClassResponseModel.get_response_schema()
# ANALYTIC_ACCOUNT_LIST_RESPONSE = AnalyticClassListResponseModel

# ANALYTIC_ACCOUNT_SCHEMA = AnalyticClassCreateRequestModel

# ANALYTIC_ACCOUNT_CREATE_PARAMS = {
#     'headers': HEADERS,
#     'body': {
#         'schema': ANALYTIC_ACCOUNT_SCHEMA,
#         'required': True
#     }
# }

# # Parameters for different endpoints
# ANALYTIC_ACCOUNT_LIST_PARAMS = {
#     'query': [
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'Filter by company ID',
#             'required': False
#         },
#         {
#             'name': 'active',
#             'type': 'boolean',
#             'description': 'Filter by active status',
#             'required': False
#         },
#         {
#             'name': 'maxresults',
#             'type': 'integer',
#             'description': 'Number of records to return (default: 100)',
#             'required': False,
#             'default': 100
#         },
#         {
#             'name': 'startposition',
#             'type': 'integer',
#             'description': 'Number of records to skip (default: 0)',
#             'required': False,
#             'default': 0
#         },
#     ]
# }

# ANALYTIC_ACCOUNT_GET_PARAMS = {
#     'path': [
#         {
#             'name': 'analytic_class_id',
#             'type': 'integer',
#             'description': 'ID of the analytic class to retrieve',
#             'required': True
#         }
#     ],
#     'query': [
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'Filter by company ID',
#             'required': True
#         },
#     ]
# }

# ANALYTIC_ACCOUNT_DELETE_PARAMS = {
#     'path': [
#         {
#             'name': 'analytic_class_id',
#             'type': 'integer',
#             'description': 'ID of the analytic class to delete',
#             'required': True
#         }
#     ],
#     'query': [
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'Company ID for validation',
#             'required': True
#         }
#     ]
# }
