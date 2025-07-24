from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from .common import (MetaDataModel, RefModel, BillAddrModel,
                     PhoneNumberModel, EmailAddressModel, WebAddrModel, PaginationResponseModel)



class BasePartnerCreateRequestModel(BaseModel):
    """Base model for shared contact fields between vendors and customers"""
    DisplayName: str = Field(..., description="Display name")
    GivenName: Optional[str] = Field(None, description="Given name")
    FamilyName: Optional[str] = Field(None, description="Family name")
    CompanyName: Optional[str] = Field(None, description="Company name")
    MiddleName: Optional[str] = Field(None, description="Middle name")
    PrimaryEmailAddr: Optional[EmailAddressModel] = Field(None, description="Primary email address")
    PrimaryPhone: Optional[PhoneNumberModel] = Field(None, description="Primary phone number")
    BillAddr: Optional[BillAddrModel] = Field(None, description="Billing address")
    Suffix: Optional[str] = Field(None, description="Name suffix")
    Title: Optional[str] = Field(None, description="Title")

    class Config:
        from_attributes = True

    @field_validator('DisplayName')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v

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
            'company_name': self.CompanyName if self.CompanyName else self.DisplayName,
            'phone': self.PrimaryPhone.FreeFormNumber if self.PrimaryPhone else None,
            'email': self.PrimaryEmailAddr.Address if self.PrimaryEmailAddr else None,
            'title': self.Title,
            'name': self.GivenName if self.GivenName else self.DisplayName,
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
    Notes: Optional[str] = Field(None, description="Additional notes")

    def create_customer_vals(self, company_id: int) -> Dict[str, Any]:
        """Create customer values dictionary"""
        customer_vals = self._create_base_vals(company_id)
        return customer_vals


class BasePartnerUpdateRequestModel(BaseModel):
    """Base model for shared contact fields for updating vendors and customers"""
    DisplayName: Optional[str] = Field(None, description="Display name")
    GivenName: Optional[str] = Field(None, description="Given name")
    FamilyName: Optional[str] = Field(None, description="Family name")
    CompanyName: Optional[str] = Field(None, description="Company name")
    MiddleName: Optional[str] = Field(None, description="Middle name")
    PrimaryEmailAddr: Optional[EmailAddressModel] = Field(None, description="Primary email address")
    PrimaryPhone: Optional[PhoneNumberModel] = Field(None, description="Primary phone number")
    BillAddr: Optional[BillAddrModel] = Field(None, description="Billing address")
    Suffix: Optional[str] = Field(None, description="Name suffix")
    Active: Optional[bool] = Field(None, description="Active status")

    class Config:
        from_attributes = True

    def _get_address_fields(self) -> Dict[str, Optional[str]]:
        """Extract address fields from BillAddr if present"""
        if not self.BillAddr:
            return {}
        
        address_vals = {}
        if hasattr(self.BillAddr, 'Line1') and self.BillAddr.Line1 is not None:
            address_vals['street'] = self.BillAddr.Line1
        if hasattr(self.BillAddr, 'Line2') and self.BillAddr.Line2 is not None:
            address_vals['street2'] = self.BillAddr.Line2
        if hasattr(self.BillAddr, 'PostalCode') and self.BillAddr.PostalCode is not None:
            address_vals['zip'] = self.BillAddr.PostalCode
        if hasattr(self.BillAddr, 'City') and self.BillAddr.City is not None:
            address_vals['city'] = self.BillAddr.City
            
        return address_vals

    def _get_contact_fields(self) -> Dict[str, Optional[str]]:
        """Extract common contact fields if present"""
        contact_vals = {}
        
        if self.DisplayName is not None:
            contact_vals['display_name'] = self.DisplayName
            
        if self.CompanyName is not None:
            contact_vals['company_name'] = self.CompanyName
            
        if self.PrimaryPhone is not None and hasattr(self.PrimaryPhone, 'FreeFormNumber'):
            contact_vals['phone'] = False if self.PrimaryPhone.FreeFormNumber == "" else self.PrimaryPhone.FreeFormNumber
            
        if self.PrimaryEmailAddr is not None and hasattr(self.PrimaryEmailAddr, 'Address'):
            contact_vals['email'] = False if self.PrimaryEmailAddr.Address == "" else self.PrimaryEmailAddr.Address
            
        if self.GivenName is not None:
            contact_vals['name'] = self.GivenName

        if self.Active is not None:
            contact_vals['active'] = self.Active
            
        return contact_vals

    def _update_base_vals(self) -> Dict[str, Any]:
        """Create base dictionary with common fields for update"""
        return {
            **self._get_contact_fields(),
            **self._get_address_fields()
        }

class VendorUpdateRequestModel(BasePartnerUpdateRequestModel):
    """Vendor-specific update model with additional fields"""
    WebAddr: Optional[WebAddrModel] = Field(None, description="Web address")
    Mobile: Optional[PhoneNumberModel] = Field(None, description="Mobile number")
    TaxIdentifier: Optional[str] = Field(None, description="Tax identifier")
    AcctNum: Optional[str] = Field(None, description="Account number")
    PrintOnCheckName: Optional[str] = Field(None, description="Name to print on checks")
    Vendor1099: Optional[bool] = Field(None, description="1099 reporting flag")

    def update_vendor_vals(self) -> Dict[str, Any]:
        """Create vendor values dictionary for update"""
        vendor_vals = self._update_base_vals()
        
        if self.Mobile is not None and hasattr(self.Mobile, 'FreeFormNumber'):
            vendor_vals['mobile'] = False if self.Mobile.FreeFormNumber == "" else self.Mobile.FreeFormNumber
            
        if self.Vendor1099 is not None:
            vendor_vals['vendor_1099'] = self.Vendor1099
            
        return vendor_vals

class CustomerUpdateRequestModel(BasePartnerUpdateRequestModel):
    """Customer-specific update model with additional fields"""
    FullyQualifiedName: Optional[str] = Field(None, description="Full name including hierarchy")
    Notes: Optional[str] = Field(None, description="Additional notes")

    def update_customer_vals(self) -> Dict[str, Any]:
        """Create customer values dictionary for update"""
        customer_vals = self._update_base_vals()
        
        if self.Notes is not None:
            customer_vals['comment'] = self.Notes
            
        return customer_vals
    

class BasePartnerModel(BaseModel):
    """Base model for shared partner fields between customers and vendors"""
    Id: Optional[int] = Field(None, description="Unique identifier")
    DisplayName: str = Field(..., description="Display name")
    GivenName: Optional[str] = Field(None, description="Given name")
    FamilyName: Optional[str] = Field(None, description="Family name")
    CompanyName: Optional[str] = Field(None, description="Company name")
    MiddleName: Optional[str] = None
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
            "PrimaryPhone": PhoneNumberModel(FreeFormNumber=partner.phone) if partner.phone else None,
            "PrimaryEmailAddr": EmailAddressModel(Address=partner.email) if partner.email else None
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

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def create_vendor_response(cls, vendor: VendorModel) -> "VendorResponseModel":
        return cls(
            Vendor=VendorModel.vendor_object(vendor),
            time=datetime.now(timezone.utc)
        )

class CustomerResponseModel(BaseModel):
    Customer: CustomerModel = Field(..., description="Customer details")
    time: datetime = Field(..., description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def create_customer_response(cls, customer: CustomerModel) -> "CustomerResponseModel":
        return cls(
            Customer=CustomerModel.customer_object(customer),
            time=datetime.now(timezone.utc)
        )

class VendorQueryResponseModel(PaginationResponseModel):
    Vendor: List[VendorModel] = Field([], description="List of vendors")


class CustomerQueryResponseModel(PaginationResponseModel):
    Customer: List[CustomerModel] = Field([], description="List of customers")


class VendorListResponseModel(BaseModel):
    QueryResponse: Union[dict, VendorQueryResponseModel] = Field({}, description="Query response containing vendor list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_vendor_response(cls, vendors: List[VendorModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "VendorListResponseModel":
        query_response = {}
        if vendors and len(vendors) > 0:
            query_response = VendorQueryResponseModel(
                startPosition=start_position,
                maxResults=max_results,
                totalCount=total_count,
                Vendor=vendors
            )
        return cls(
            QueryResponse=query_response,
            time=datetime.now(timezone.utc)
        )

class CustomerListResponseModel(BaseModel):
    QueryResponse: Union[dict, CustomerQueryResponseModel] = Field({}, description="Query response containing customer list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_customer_response(cls, customers: List[CustomerModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "CustomerListResponseModel":
        query_response = {}
        if customers and len(customers) > 0:
            query_response = CustomerQueryResponseModel(
                startPosition=start_position,
                maxResults=max_results,
                totalCount=total_count,
                Customer=customers
            )
        return cls(
            QueryResponse=query_response,
            time=datetime.now(timezone.utc)
        )
    
