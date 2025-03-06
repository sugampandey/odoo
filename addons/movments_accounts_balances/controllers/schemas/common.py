from typing import Optional
from .schema_generator import ResponseSchemaGenerator, RequestSchemaGenerator


HEADERS = [
    {
        'name': 'X-Company-Id',
        'type': 'string',
        'description': 'Company identifier',
        'required': True
    }
]

class ParentRef(RequestSchemaGenerator, ResponseSchemaGenerator):
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

class WebAddress(RequestSchemaGenerator, ResponseSchemaGenerator):
    def __init__(self, URI: str):
        self.URI = URI

    def to_dict(self) -> dict:
        return {'URI': self.URI}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(URI=data.get('URI', ''))
    
class TaxCodeRef(ResponseSchemaGenerator):
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
    
class ClassRef(RequestSchemaGenerator, ResponseSchemaGenerator):
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

ERROR_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'error': {'type': 'string'},
        'details': {'type': 'string'}
    }
}
