from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime, timezone

class ErrorDetail(BaseModel):
    message: str
    code: Optional[str] = None
    detail: Optional[Any] = None
    element: Optional[str] = None

class FaultModel(BaseModel):
    error: List[ErrorDetail]
    type: Optional[str] = None

class ResponseHeaderModel(BaseModel):
    status: int
    message: str
    intuitTid: Optional[str] = None
    realmID: Optional[str] = None

class ResponseModel(BaseModel):
    warnings: Optional[dict] = None
    intuitObject: Optional[dict] = None
    fault: Optional[FaultModel] = None
    report: Optional[dict] = None
    queryResponse: Optional[dict] = None
    batchItemResponse: Optional[List[dict]] = None
    attachableResponse: Optional[List[dict]] = None
    syncErrorResponse: Optional[dict] = None
    requestId: Optional[str] = None
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp") 
    status: Optional[str] = None
    cdcresponse: Optional[List[dict]] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

class ErrorResponseModel(BaseModel):
    responseHeader: ResponseHeaderModel
    response: ResponseModel

# If you still need the schema, you can get it using:
ERROR_SCHEMA = ErrorResponseModel.model_json_schema()





