from typing import Optional, List, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from .common import (RefModel, MetaDataModel, BillAddrModel,
                     PhoneNumberModel, EmailAddressModel, PaginationResponseModel)
from ..repositories.currency import CurrencyService


class CompanyCreateRequestModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    PrimaryEmailAddr: Optional[EmailAddressModel] = Field(None, description="Primary email address")
    PrimaryPhone: Optional[PhoneNumberModel] = Field(None, description="Primary phone number")
    BillAddr: Optional[BillAddrModel] = Field(None, description="Billing address")
    CurrencyRef: Optional[RefModel] = Field(None, description="Currency reference")

    class Config:
        from_attributes = True

    @field_validator('Name')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v

    def create_company_vals(self, request) -> dict:
        currency_service = CurrencyService(request.env)
        return {
            'name': self.Name,
            'email': self.PrimaryEmailAddr.Address if self.PrimaryEmailAddr else None,
            'phone': self.PrimaryPhone.FreeFormNumber if self.PrimaryPhone else None,
            'currency_id': currency_service.get_currency_id(self.CurrencyRef.value) if self.CurrencyRef else currency_service.get_default_currency_id(),
        }
    

class CompanyModel(BaseModel):
    Id: Optional[int] = Field(None, description="Unique identifier for the company")
    Name: str = Field(..., min_length=1, max_length=256)
    PrimaryEmailAddr: Optional[EmailAddressModel] = None
    PrimaryPhone: Optional[PhoneNumberModel] = None
    BillAddr: Optional[BillAddrModel] = None
    CurrencyRef: Optional[RefModel] = None
    MetaData: Optional[MetaDataModel] = None
    Active: bool = Field(True, description="Whether the company is active")
    SyncToken: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def company_object(cls, company) -> "CompanyModel":
        try:
            meta_data = MetaDataModel(
                CreateTime=company.create_date,
                LastUpdatedTime=company.write_date
            )

            currency_ref = None
            if company.currency_id:
                currency_ref = RefModel(
                    name=company.currency_id.full_name,
                    value=company.currency_id.name
                )

            return cls(
                Id=str(company.id),
                Name=company.name,
                PrimaryEmailAddr=EmailAddressModel(Address=company.email) if company.email else None,
                PrimaryPhone=PhoneNumberModel(FreeFormNumber=company.phone) if company.phone else None,
                CurrencyRef=currency_ref,
                MetaData=meta_data,
                Active=company.active,
            )
        except Exception as e:
            raise ValueError(f"Error creating company object: {str(e)}")
    
class CompanyResponseModel(BaseModel):
    """
    Response model for single company operations
    """
    Company: CompanyModel = Field(..., description="Company details")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def create_company_response(cls, company: CompanyModel) -> "CompanyResponseModel":
        return cls(
            Company=CompanyModel.company_object(company),
            time=datetime.now(timezone.utc)
        )
    
class CompanyQueryResponseModel(PaginationResponseModel):
    """
    Response model for company queries with pagination
    """
    Company: List[CompanyModel] = Field([], description="List of companies")
    

class CompanyListResponseModel(BaseModel):
    """
    Response model for company list operations
    """
    QueryResponse: Union[dict, CompanyQueryResponseModel] = Field({}, description="Query response containing company list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_company_response(cls, companies: List[CompanyModel], total_count: int, start_position: int = 0, max_results: int = 100) -> "CompanyListResponseModel":
        query_response = {}
        if companies and len(companies) > 0:
            query_response = CompanyQueryResponseModel(
                startPosition=start_position,
                maxResults=max_results,
                totalCount=total_count,
                Company=companies
            )
        return cls(
            QueryResponse=query_response,
            time=datetime.now(timezone.utc)
        )
           
