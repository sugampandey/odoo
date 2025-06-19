from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime, timezone

ACCESS_TOKEN_HEADER = [
    {
        'name': 'X-Access-Token',
        'type': 'string',
        'description': 'Access token',
        'required': True
    }
]

COMPANY_HEADERS = [
    {
        'name': 'X-Company-Id',
        'type': 'string',
        'description': 'Company identifier',
        'required': True
    }
]


class PaginationModel(BaseModel):
    """Base class for pagination parameters"""
    startPosition: int = Field(
        1, 
        ge=1,
        description="Starting position of the result set"
    )
    maxResults: int = Field(
        20, 
        ge=0, 
        le=100,
        description="Maximum number of results to return"
    )


class PaginationResponseModel(PaginationModel):
    totalCount: int = Field(..., ge=0, description="Total count of records")


class RefModel(BaseModel):
    name: Optional[str] = None
    value: str 

    @field_validator('value')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v


class MetaDataModel(BaseModel):
    CreateTime: datetime
    LastUpdatedTime: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True


class BillAddrModel(BaseModel):
    City: Optional[str] = Field(None, description="City name")
    Country: Optional[str] = Field(None, description="Country name")
    Line1: Optional[str] = Field(None, description="Address line 1")
    Line2: Optional[str] = Field(None, description="Address line 2")
    Line3: Optional[str] = Field(None, description="Address line 3")
    PostalCode: Optional[str] = Field(None, description="Postal/ZIP code")
    CountrySubDivisionCode: Optional[str] = Field(None, description="State/Province/Region code")

    class Config:
        from_attributes = True

class PhoneNumberModel(BaseModel):
    FreeFormNumber: str = Field(..., description="Phone number in free form format")

    class Config:
        from_attributes = True


class EmailAddressModel(BaseModel):
    Address: EmailStr = Field(..., description="Email address")

    class Config:
        from_attributes = True


class WebAddrModel(BaseModel):
    URI: Optional[str] = Field(None, description="Web address URI")
    
    
    