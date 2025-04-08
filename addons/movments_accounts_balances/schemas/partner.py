from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from .common import (MetaDataModel, RefModel, BillAddrModel,
                     PhoneNumberModel, EmailAddressModel, WebAddrModel, HEADERS, PaginationResponseModel)


# Base Models
# TODO: Move these to common module
class MetaDataModel(BaseModel):
    CreateTime: datetime
    LastUpdatedTime: datetime

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
    FreeFormNumber: Optional[str] = Field(None, description="Phone number in free form format")
    class Config:
        from_attributes = True


class EmailAddressModel(BaseModel):
    Address: Optional[EmailStr] = Field(None, description="Email address")
    class Config:
        from_attributes = True

class WebAddrModel(BaseModel):
    URI: Optional[str] = Field(None, description="Web address URI")


class BasePartnerCreateRequestModel(BaseModel):
    """Base model for shared contact fields between vendors and customers"""
    DisplayName: str = Field(..., description="Display name")
    GivenName: str = Field(..., description="Given name")
    FamilyName: Optional[str] = Field(None, description="Family name")
    CompanyName: Optional[str] = Field(None, description="Company name")
    PrimaryEmailAddr: Optional[EmailAddressModel] = Field(None, description="Primary email address")
    PrimaryPhone: Optional[PhoneNumberModel] = Field(None, description="Primary phone number")
    BillAddr: Optional[BillAddrModel] = Field(None, description="Billing address")
    Suffix: Optional[str] = Field(None, description="Name suffix")
    Title: Optional[str] = Field(None, description="Title")

    class Config:
        from_attributes = True

    def _get_address_fields(self) -> Dict[str, Optional[str]]:
        """Extract address fields from BillAddr"""
        return {
            'street': self.BillAddr.Line1 if self.BillAddr else None,
            'street2': self.BillAddr.Line2 if self.BillAddr else None,
            'zip': self.BillAddr.PostalCode if self.BillAddr else None,
            'city': self.BillAddr.City if self.BillAddr else None,
        }

    def _get_contact_fields(self) -> Dict[str, Optional[str]]:
        """Extract common contact fields"""
        return {
            'display_name': self.DisplayName,
            'company_name': self.CompanyName,
            'phone': self.PrimaryPhone.FreeFormNumber if self.PrimaryPhone else None,
            'email': self.PrimaryEmailAddr.Address if self.PrimaryEmailAddr else None,
            'title': self.Title,
            'name': self.GivenName,
        }

    def _create_base_vals(self, company_id: int) -> Dict[str, Any]:
        """Create base dictionary with common fields"""
        return {
            **self._get_contact_fields(),
            **self._get_address_fields(),
            'company_id': company_id
        }

class VendorCreateRequestModel(BasePartnerCreateRequestModel):
    """Vendor-specific model with additional fields"""
    WebAddr: Optional[WebAddrModel] = Field(None, description="Web address")
    Mobile: Optional[PhoneNumberModel] = Field(None, description="Mobile number")
    TaxIdentifier: Optional[str] = Field(None, description="Tax identifier")
    AcctNum: Optional[str] = Field(None, description="Account number")
    PrintOnCheckName: Optional[str] = Field(None, description="Name to print on checks")
    Vendor1099: Optional[bool] = Field(False, description="1099 reporting flag")

    def create_vendor_vals(self, company_id: int) -> Dict[str, Any]:
        """Create vendor values dictionary"""
        vendor_vals = self._create_base_vals(company_id)
        vendor_vals.update({
            'mobile': self.Mobile.FreeFormNumber if self.Mobile else None,
            'vendor_1099': self.Vendor1099
        })
        return vendor_vals

class CustomerCreateRequestModel(BasePartnerCreateRequestModel):
    """Customer-specific model with additional fields"""
    FullyQualifiedName: Optional[str] = Field(None, description="Full name including hierarchy")
    MiddleName: Optional[str] = Field(None, description="Middle name")
    Notes: Optional[str] = Field(None, description="Additional notes")

    def create_customer_vals(self, company_id: int) -> Dict[str, Any]:
        """Create customer values dictionary"""
        customer_vals = self._create_base_vals(company_id)
        return customer_vals


class BasePartnerModel(BaseModel):
    """Base model for shared partner fields between customers and vendors"""
    Id: Optional[int] = Field(None, description="Unique identifier")
    DisplayName: str = Field(..., description="Display name")
    GivenName: Optional[str] = Field(None, description="Given name")
    FamilyName: Optional[str] = Field(None, description="Family name")
    CompanyName: Optional[str] = Field(None, description="Company name")
    PrimaryEmailAddr: Optional[EmailAddressModel] = None
    PrimaryPhone: Optional[PhoneNumberModel] = None
    BillAddr: Optional[BillAddrModel] = None
    MetaData: Optional[MetaDataModel] = None
    domain: Optional[str] = Field(None, description="Domain")
    Title: Optional[str] = None
    Suffix: Optional[str] = None
    Balance: Optional[float] = Field(0.0, description="Current balance")
    SyncToken: Optional[str] = None
    PrintOnCheckName: Optional[str] = None
    sparse: Optional[bool] = Field(False, description="Sparse response flag")
    Active: Optional[bool] = Field(True, description="Active status")

    class Config:
        from_attributes = True

    @classmethod
    def _create_metadata(cls, partner) -> MetaDataModel:
        """Create metadata model from partner data"""
        return MetaDataModel(
            CreateTime=partner.create_date,
            LastUpdatedTime=partner.write_date,
        )

    @classmethod
    def _create_address(cls, partner) -> BillAddrModel:
        """Create billing address model from partner data"""
        return BillAddrModel(
            Line1=partner.street if partner.street else None,
            Line2=partner.street2 if partner.street2 else None,
            PostalCode=partner.zip if partner.zip else None,
            City=partner.city if partner.city else None,
            CountrySubDivisionCode=partner.state_id.name if partner.state_id else None,
            Country=partner.country_id.name if partner.country_id else None,
        )

    @classmethod
    def _create_contact_info(cls, partner) -> Dict[str, Any]:
        """Create contact information from partner data"""
        return {
            "PrimaryPhone": PhoneNumberModel(FreeFormNumber=partner.phone if partner.phone else None),
            "PrimaryEmailAddr": EmailAddressModel(Address=partner.email if partner.email else None)
        }

    @classmethod
    def _create_base_partner_data(cls, partner) -> Dict[str, Any]:
        """Create base partner data dictionary"""
        return {
            "Id": partner.id,
            "DisplayName": partner.display_name,
            "GivenName": partner.name,
            "CompanyName": partner.company_name if partner.company_name else None,
            "BillAddr": cls._create_address(partner),
            "Active": partner.active,
            "MetaData": cls._create_metadata(partner),
            **cls._create_contact_info(partner)
        }

class CustomerModel(BasePartnerModel):
    """Customer-specific model"""
    FullyQualifiedName: Optional[str] = None
    PreferredDeliveryMethod: Optional[str] = None
    BillWithParent: Optional[bool] = Field(False, description="Bill with parent flag")
    MiddleName: Optional[str] = None
    Job: Optional[bool] = Field(False, description="Job flag")
    BalanceWithJobs: Optional[float] = Field(0.0, description="Balance including jobs")
    Taxable: Optional[bool] = Field(True, description="Taxable status")
    Notes: Optional[str] = None
    DefaultTaxCodeRef: Optional[RefModel] = None

    @classmethod
    def customer_object(cls, customer) -> "CustomerModel":
        """Create customer object from customer data"""
        customer_data = cls._create_base_partner_data(customer)
        return CustomerModel(**customer_data)

class VendorModel(BasePartnerModel):
    """Vendor-specific model"""
    Mobile: Optional[PhoneNumberModel] = None
    WebAddr: Optional[WebAddrModel] = None
    Vendor1099: Optional[bool] = Field(False, description="1099 eligible vendor")
    TaxIdentifier: Optional[str] = None
    AcctNum: Optional[str] = None

    @classmethod
    def vendor_object(cls, vendor) -> "VendorModel":
        """Create vendor object from vendor data"""
        vendor_data = cls._create_base_partner_data(vendor)
        vendor_data["Vendor1099"] = vendor.vendor_1099
        return VendorModel(**vendor_data)

# Response Models
class VendorResponseModel(BaseModel):
    Vendor: VendorModel = Field(..., description="Vendor details")
    time: datetime = Field(..., description="Response timestamp")

    @classmethod
    def create_vendor_response(cls, vendor: VendorModel) -> "VendorResponseModel":
        return cls(
            Vendor=VendorModel.vendor_object(vendor),
            time=datetime.now()
        )

class CustomerResponseModel(BaseModel):
    Customer: CustomerModel = Field(..., description="Customer details")
    time: datetime = Field(..., description="Response timestamp")

    @classmethod
    def create_customer_response(cls, customer: CustomerModel) -> "CustomerResponseModel":
        return cls(
            Customer=CustomerModel.customer_object(customer),
            time=datetime.now()
        )

class VendorQueryResponseModel(PaginationResponseModel):
    Vendor: List[VendorModel] = Field(..., description="List of vendors")

    @field_validator('Vendor')
    def validate_vendors(cls, vendors: List[VendorModel]) -> List[VendorModel]:
        if not vendors:
            raise ValueError("Vendor list cannot be empty")
        return vendors

class CustomerQueryResponseModel(PaginationResponseModel):
    Customer: List[CustomerModel] = Field(..., description="List of customers")

    @field_validator('Customer')
    def validate_customers(cls, customers: List[CustomerModel]) -> List[CustomerModel]:
        if not customers:
            raise ValueError("Customer list cannot be empty")
        return customers

class VendorListResponseModel(BaseModel):
    QueryResponse: VendorQueryResponseModel = Field(..., description="Query response containing vendor list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def list_vendor_response(cls, vendors: List[VendorModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "VendorListResponseModel":
        query_response = VendorQueryResponseModel(
            startPosition=start_position,
            maxResults=max_results,
            totalCount=total_count,
            Vendor=vendors
        )
        return cls(
            QueryResponse=query_response,
            time=datetime.now()
        )

class CustomerListResponseModel(BaseModel):
    QueryResponse: CustomerQueryResponseModel = Field(..., description="Query response containing customer list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def list_customer_response(cls, customers: List[CustomerModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "CustomerListResponseModel":
        query_response = CustomerQueryResponseModel(
            startPosition=start_position,
            maxResults=max_results,
            totalCount=total_count,
            Customer=customers
        )
        return cls(
            QueryResponse=query_response,
            time=datetime.now()
        )
    

VENDOR_GET_PARAMS = {
    'path': [
        {
            'name': 'vendor_id',
            'type': 'integer',
            'description': 'ID of the vendor to retrieve',
            'required': True
        }
    ]
}

CUSTOMER_GET_PARAMS = {
    'path': [
        {
            'name': 'customer_id',
            'type': 'integer',
            'description': 'ID of the customer to retrieve',
            'required': True
        }
    ]
}

VENDOR_DELETE_PARAMS = {
    'path': [
        {
            'name': 'vendor_id',
            'type': 'integer',
            'description': 'ID of the vendor to delete',
            'required': True
        }
    ]
}

CUSTOMER_DELETE_PARAMS = {
    'path': [
        {
            'name': 'customer_id',
            'type': 'integer',
            'description': 'ID of the customer to delete',
            'required': True
        }
    ]
}

VENDOR_CREATE_RESPONSE = VENDOR_GET_RESPONSE = VendorResponseModel
VENDOR_LIST_RESPONSE = VendorListResponseModel
VENDOR_SCHEMA = VendorCreateRequestModel
VENDOR_CREATE_PARAMS = {
    'headers': HEADERS,
    'body': {
        'schema': VENDOR_SCHEMA,
        'required': True
    }
}

CUSTOMER_CREATE_RESPONSE = CUSTOMER_GET_RESPONSE = CustomerResponseModel
CUSTOMER_LIST_RESPONSE = CustomerListResponseModel
CUSTOMER_SCHEMA = CustomerCreateRequestModel
CUSTOMER_CREATE_PARAMS = {
    'headers': HEADERS,
    'body': {
        'schema': CUSTOMER_SCHEMA,
        'required': True
    }
}

PARTNER_CATEGORY_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'active': {'type': 'boolean'}
                }
            }
        }
    }
}



