from typing import List, Optional, Union
import uuid
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from .common import PaginationResponseModel, RefModel, MetaDataModel


class AnalyticClassCreateRequestModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    ParentRef: Optional[RefModel] = Field(None, description="Parent reference")

    class Config:
        from_attributes = True

    @field_validator('Name')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v

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
    ParentRef: Optional[RefModel] = None
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

class AnalyticClassQueryResponseModel(PaginationResponseModel):
    Class: List[AnalyticClassModel] = Field([], description="List of Classes")
    
    
class AnalyticClassResponseModel(BaseModel):
    Class: AnalyticClassModel = Field(..., description="Class details")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def create_analytic_class_response(cls, analytic_class: AnalyticClassModel) -> "AnalyticClassResponseModel":
        return cls(
            Class=AnalyticClassModel.analytic_class_object(analytic_class),
            time=datetime.now(timezone.utc)
        )
    

class AnalyticClassListResponseModel(BaseModel):
    QueryResponse: Union[dict, AnalyticClassQueryResponseModel] = Field({}, description="Query response containing analytic class list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_analytic_class_response(cls, analytic_classes: List[AnalyticClassModel], total_count : int, start_position: int = 0, max_results: int = 100) -> "AnalyticClassListResponseModel":
        query_response = {}
        if analytic_classes and len(analytic_classes) > 0:
            query_response = AnalyticClassQueryResponseModel(
                startPosition=start_position,
                maxResults=max_results,
                totalCount=total_count,
                Class=analytic_classes
            )
        return cls(
            QueryResponse=query_response,
            time=datetime.now(timezone.utc)
        )
 