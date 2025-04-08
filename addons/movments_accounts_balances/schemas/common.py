from typing import Optional
from pydantic import BaseModel, Field
from odoo import fields, models
from .schema_generator import ResponseSchemaGenerator, RequestSchemaGenerator


HEADERS = [
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
        0, 
        ge=0,
        description="Starting position of the result set"
    )
    maxResults: int = Field(
        20, 
        ge=1, 
        le=100,
        description="Maximum number of results to return"
    )

class PaginationResponseModel(PaginationModel):
    totalCount: int = Field(..., ge=0, description="Total count of records")

class RefModel(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

class ParentRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    

class CurrencyRefDTO(models.TransientModel, RequestSchemaGenerator, ResponseSchemaGenerator):
    _name = 'currency.ref'
    _description = 'Currency Reference Model'

    name = fields.Char(string='Name')
    value = fields.Char(string='Value')

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
    
class CurrencyRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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

class MetaDataModel(ResponseSchemaGenerator):
    def __init__(
        self,
        CreateTime: str,
        LastUpdatedTime: str
    ):
        self.CreateTime = CreateTime
        self.LastUpdatedTime = LastUpdatedTime

    def to_dict(self) -> dict:
        return {
            'CreateTime': self.CreateTime,
            'LastUpdatedTime': self.LastUpdatedTime
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            CreateTime=data.get('CreateTime', ''),
            LastUpdatedTime=data.get('LastUpdatedTime', '')
        )
    
class PhoneNumberModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(self, FreeFormNumber: str):
        self.FreeFormNumber = FreeFormNumber

    def to_dict(self):
        return {'FreeFormNumber': self.FreeFormNumber}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(FreeFormNumber=data.get('FreeFormNumber'))
    
class EmailAddressModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(self, Address: str):
        self.Address = Address

    def to_dict(self) -> dict:
        return {'Address': self.Address}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(Address=data.get('Address', ''))

class WebAddrModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(self, URI: str):
        self.URI = URI

    def to_dict(self) -> dict:
        return {'URI': self.URI}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(URI=data.get('URI', ''))
    
    
class ClassRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    

class TaxCodeRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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


class BillAddrModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        City: Optional[str] = None,
        Country: Optional[str] = None,
        Line1: Optional[str] = None,
        Line2: Optional[str] = None,
        Line3: Optional[str] = None,
        PostalCode: Optional[str] = None,
        CountrySubDivisionCode: Optional[str] = None
    ):
        self.City = City
        self.Country = Country
        self.Line1 = Line1
        self.Line2 = Line2
        self.Line3 = Line3
        self.PostalCode = PostalCode
        self.CountrySubDivisionCode = CountrySubDivisionCode

    def to_dict(self) -> dict:
        return {
            'City': self.City,
            'Country': self.Country,
            'Line1': self.Line1,
            'Line2': self.Line2,
            'Line3': self.Line3,
            'PostalCode': self.PostalCode,
            'CountrySubDivisionCode': self.CountrySubDivisionCode
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            City=data.get('City', ''),
            Country=data.get('Country', ''),
            Line1=data.get('Line1', ''),
            Line2=data.get('Line2', ''),
            Line3=data.get('Line3', ''),
            PostalCode=data.get('PostalCode', ''),
            CountrySubDivisionCode=data.get('CountrySubDivisionCode', '')
        )
    

class AccountRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
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

class CustomerRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    

class ProjectRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    

class ItemRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    
class ItemAccountRefModel(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
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
    

ERROR_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'error': {'type': 'string'},
        'details': {'type': 'string'}
    }
}
