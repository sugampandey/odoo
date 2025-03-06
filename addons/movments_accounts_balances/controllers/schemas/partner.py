from typing import Optional
from datetime import datetime
from .common import (CurrencyRefModel, MetaDataModel, TaxCodeRefModel, BillAddrModel,
                     PhoneNumberModel, EmailAddressModel, WebAddress, HEADERS)
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator


class VendorCreateRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        DisplayName: str,
        GivenName: str,
        FamilyName: Optional[str] = None,
        CompanyName: Optional[str] = None,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        WebAddr: Optional[WebAddress] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        Mobile: Optional[PhoneNumberModel] = None,
        BillAddr: Optional[BillAddrModel] = None,
        Suffix: Optional[str] = None,
        Title: Optional[str] = None,
        TaxIdentifier: Optional[str] = None,
        AcctNum: Optional[str] = None,
        PrintOnCheckName: Optional[str] = None,
    ):
        self.DisplayName = DisplayName
        self.GivenName = GivenName
        self.FamilyName = FamilyName
        self.CompanyName = CompanyName
        self.PrintOnCheckName = PrintOnCheckName
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.WebAddr = WebAddr
        self.PrimaryPhone = PrimaryPhone
        self.Mobile = Mobile
        self.BillAddr = BillAddr
        self.Suffix = Suffix
        self.Title = Title
        self.TaxIdentifier = TaxIdentifier
        self.AcctNum = AcctNum

    def to_dict(self) -> dict:
        return {
            'DisplayName': self.DisplayName,
            'GivenName': self.GivenName,
            'FamilyName': self.FamilyName,
            'CompanyName': self.CompanyName,
            'PrintOnCheckName': self.PrintOnCheckName,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'WebAddr': self.WebAddr.to_dict() if self.WebAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'Mobile': self.Mobile.to_dict() if self.Mobile else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'Suffix': self.Suffix,
            'Title': self.Title,
            'TaxIdentifier': self.TaxIdentifier,
            'AcctNum': self.AcctNum
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            DisplayName=data.get('DisplayName', ''),
            GivenName=data.get('GivenName', ''),
            FamilyName=data.get('FamilyName', ''),
            CompanyName=data.get('CompanyName', ''),
            PrintOnCheckName=data.get('PrintOnCheckName', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})),
            WebAddr=WebAddress.from_dict(data.get('WebAddr', {})),
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})),
            Mobile=PhoneNumberModel.from_dict(data.get('Mobile', {})),
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})),
            Suffix=data.get('Suffix', ''),
            Title=data.get('Title', ''),
            TaxIdentifier=data.get('TaxIdentifier', ''),
            AcctNum=data.get('AcctNum', '')
        )


class CustomerCreateRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        DisplayName: str,
        GivenName: str,
        FamilyName: Optional[str] = None,
        CompanyName: Optional[str] = None,
        FullyQualifiedName: Optional[str] = None,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        BillAddr: Optional[BillAddrModel] = None,
        Suffix: Optional[str] = None,
        Title: Optional[str] = None,
        MiddleName: Optional[str] = None,
        Notes: Optional[str] = None,
    ):
        self.DisplayName = DisplayName
        self.GivenName = GivenName
        self.FamilyName = FamilyName
        self.CompanyName = CompanyName
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.PrimaryPhone = PrimaryPhone
        self.BillAddr = BillAddr
        self.Suffix = Suffix
        self.Title = Title
        self.FullyQualifiedName = FullyQualifiedName
        self.MiddleName = MiddleName
        self.Notes = Notes

    def to_dict(self) -> dict:
        return {
            'DisplayName': self.DisplayName,
            'GivenName': self.GivenName,
            'FamilyName': self.FamilyName,
            'CompanyName': self.CompanyName,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'Suffix': self.Suffix,
            'Title': self.Title,
            'FullyQualifiedName': self.FullyQualifiedName,
            'MiddleName': self.MiddleName,
            'Notes': self.Notes,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            DisplayName=data.get('DisplayName', ''),
            GivenName=data.get('GivenName', ''),
            FamilyName=data.get('FamilyName', ''),
            CompanyName=data.get('CompanyName', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})),
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})),
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})),
            Suffix=data.get('Suffix', ''),
            Title=data.get('Title', ''),
            FullyQualifiedName=data.get('FullyQualifiedName', ''),
            MiddleName=data.get('MiddleName', ''),
            Notes=data.get('Notes', '')
        )

class CustomerModel(ResponseSchemaGenerator):
    def __init__(
        self,
        DisplayName: str,
        CompanyName: str,
        GivenName: Optional[str] = None,
        FamilyName: Optional[str] = None,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        BillAddr: Optional[BillAddrModel] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
        DefaultTaxCodeRef: Optional[TaxCodeRefModel] = None,
        MetaData: Optional[MetaDataModel] = None,
        domain: Optional[str] = None,
        FullyQualifiedName: Optional[str] = None,
        PreferredDeliveryMethod: Optional[str] = None,
        BillWithParent: Optional[bool] = False,
        Title: Optional[str] = None,
        MiddleName: Optional[str] = None,
        Suffix: Optional[str] = None,
        Job: Optional[bool] = False,
        BalanceWithJobs: Optional[float] = 0.0,
        Taxable: Optional[bool] = True,
        Notes: Optional[str] = None,
        Active: Optional[bool] = True,
        Balance: Optional[float] = 0.0,
        SyncToken: Optional[str] = None,
        PrintOnCheckName: Optional[str] = None,
        sparse: Optional[bool] = False,
        Id: Optional[str] = None
    ):
        self.domain = domain
        self.DisplayName = DisplayName
        self.GivenName = GivenName
        self.FamilyName = FamilyName
        self.CompanyName = CompanyName
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.PrimaryPhone = PrimaryPhone
        self.BillAddr = BillAddr
        self.CurrencyRef = CurrencyRef
        self.DefaultTaxCodeRef = DefaultTaxCodeRef
        self.MetaData = MetaData
        self.FullyQualifiedName = FullyQualifiedName
        self.PreferredDeliveryMethod = PreferredDeliveryMethod
        self.BillWithParent = BillWithParent
        self.Title = Title
        self.MiddleName = MiddleName
        self.Suffix = Suffix
        self.Job = Job
        self.BalanceWithJobs = BalanceWithJobs
        self.Taxable = Taxable
        self.Notes = Notes
        self.Active = Active
        self.Balance = Balance
        self.SyncToken = SyncToken
        self.PrintOnCheckName = PrintOnCheckName
        self.sparse = sparse
        self.Id = Id

    def to_dict(self) -> dict:
        return {
            'domain': self.domain,
            'DisplayName': self.DisplayName,
            'GivenName': self.GivenName,
            'FamilyName': self.FamilyName,
            'CompanyName': self.CompanyName,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
            'DefaultTaxCodeRef': self.DefaultTaxCodeRef.to_dict() if self.DefaultTaxCodeRef else None,
            'MetaData': self.MetaData.to_dict() if self.MetaData else None,
            'FullyQualifiedName': self.FullyQualifiedName,
            'PreferredDeliveryMethod': self.PreferredDeliveryMethod,
            'BillWithParent': self.BillWithParent,
            'Title': self.Title,
            'MiddleName': self.MiddleName,
            'Suffix': self.Suffix,
            'Job': self.Job,
            'BalanceWithJobs': self.BalanceWithJobs,
            'Taxable': self.Taxable,
            'Notes': self.Notes,
            'Active': self.Active,
            'Balance': self.Balance,
            'SyncToken': self.SyncToken,
            'PrintOnCheckName': self.PrintOnCheckName,
            'sparse': self.sparse,
            'Id': self.Id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            domain=data.get('domain', ''),
            DisplayName=data.get('DisplayName', ''),
            GivenName=data.get('GivenName', ''),
            FamilyName=data.get('FamilyName', ''),
            CompanyName=data.get('CompanyName', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})),
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})),
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})),
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {})),
            DefaultTaxCodeRef=TaxCodeRefModel.from_dict(data.get('DefaultTaxCodeRef', {})),
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {})),
            FullyQualifiedName=data.get('FullyQualifiedName'),
            PreferredDeliveryMethod=data.get('PreferredDeliveryMethod'),
            BillWithParent=data.get('BillWithParent', False),
            Title=data.get('Title'),
            MiddleName=data.get('MiddleName'),
            Suffix=data.get('Suffix'),
            Job=data.get('Job', False),
            BalanceWithJobs=data.get('BalanceWithJobs', 0.0),
            Taxable=data.get('Taxable', True),
            Notes=data.get('Notes'),
            Active=data.get('Active', True),
            Balance=data.get('Balance', 0.0),
            SyncToken=data.get('SyncToken'),
            PrintOnCheckName=data.get('PrintOnCheckName'),
            sparse=data.get('sparse', False),
            Id=data.get('Id')
        )

class CustomerResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Customer: CustomerModel,
        time: str
    ):
        self.Customer = Customer
        self.time = time

    def to_dict(self) -> dict:
        return {
            'Customer': self.Customer.to_dict(),
            'time': self.time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Customer=CustomerModel.from_dict(data.get('Customer', {})),
            time=data.get('time')
        )
    

class CustomerQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        Customer: list[CustomerModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.Customer = Customer
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'Customer': [customer.to_dict() for customer in self.Customer],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }
    
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            Customer=[CustomerModel.from_dict(customer_data) for customer_data in data.get('Customer', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )
           
class CustomerListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: CustomerQueryResponseModel,
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
            QueryResponse=CustomerQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )


# VENDOR
class VendorModel(ResponseSchemaGenerator):
    def __init__(
        self,
        DisplayName: str,
        CompanyName: str,
        GivenName: Optional[str] = None,
        FamilyName: Optional[str] = None,
        PrimaryEmailAddr: Optional[EmailAddressModel] = None,
        PrimaryPhone: Optional[PhoneNumberModel] = None,
        Mobile: Optional[PhoneNumberModel] = None,
        WebAddr: Optional[WebAddress] = None,
        BillAddr: Optional[BillAddrModel] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
        MetaData: Optional[MetaDataModel] = None,
        domain: Optional[str] = None,
        Title: Optional[str] = None,
        Suffix: Optional[str] = None,
        Vendor1099: Optional[bool] = False,
        Balance: Optional[float] = 0.0,
        SyncToken: Optional[str] = None,
        PrintOnCheckName: Optional[str] = None,
        TaxIdentifier: Optional[str] = None,
        AcctNum: Optional[str] = None,
        sparse: Optional[bool] = False,
        Active: Optional[bool] = True,
        Id: Optional[str] = None
    ):
        self.domain = domain
        self.DisplayName = DisplayName
        self.GivenName = GivenName
        self.FamilyName = FamilyName
        self.CompanyName = CompanyName
        self.PrimaryEmailAddr = PrimaryEmailAddr
        self.PrimaryPhone = PrimaryPhone
        self.Mobile = Mobile
        self.WebAddr = WebAddr
        self.BillAddr = BillAddr
        self.CurrencyRef = CurrencyRef
        self.MetaData = MetaData
        self.Title = Title
        self.Suffix = Suffix
        self.Vendor1099 = Vendor1099
        self.Balance = Balance
        self.SyncToken = SyncToken
        self.PrintOnCheckName = PrintOnCheckName
        self.TaxIdentifier = TaxIdentifier
        self.AcctNum = AcctNum
        self.sparse = sparse
        self.Active = Active
        self.Id = Id

    def to_dict(self) -> dict:
        return {
            'domain': self.domain,
            'DisplayName': self.DisplayName,
            'GivenName': self.GivenName,
            'FamilyName': self.FamilyName,
            'CompanyName': self.CompanyName,
            'PrimaryEmailAddr': self.PrimaryEmailAddr.to_dict() if self.PrimaryEmailAddr else None,
            'PrimaryPhone': self.PrimaryPhone.to_dict() if self.PrimaryPhone else None,
            'Mobile': self.Mobile.to_dict() if self.Mobile else None,
            'WebAddr': self.WebAddr.to_dict() if self.WebAddr else None,
            'BillAddr': self.BillAddr.to_dict() if self.BillAddr else None,
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
            'MetaData': self.MetaData.to_dict() if self.MetaData else None,
            'Title': self.Title,
            'Suffix': self.Suffix,
            'Vendor1099': self.Vendor1099,
            'Balance': self.Balance,
            'SyncToken': self.SyncToken,
            'PrintOnCheckName': self.PrintOnCheckName,
            'TaxIdentifier': self.TaxIdentifier,
            'AcctNum': self.AcctNum,
            'sparse': self.sparse,
            'Active': self.Active,
            'Id': self.Id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            domain=data.get('domain', ''),
            DisplayName=data.get('DisplayName', ''),
            GivenName=data.get('GivenName', ''),
            FamilyName=data.get('FamilyName', ''),
            CompanyName=data.get('CompanyName', ''),
            PrimaryEmailAddr=EmailAddressModel.from_dict(data.get('PrimaryEmailAddr', {})) if data.get('PrimaryEmailAddr') else None,
            PrimaryPhone=PhoneNumberModel.from_dict(data.get('PrimaryPhone', {})) if data.get('PrimaryPhone') else None,
            Mobile=PhoneNumberModel.from_dict(data.get('Mobile', {})) if data.get('Mobile') else None,
            WebAddr=WebAddress.from_dict(data.get('WebAddr', {})) if data.get('WebAddr') else None,
            BillAddr=BillAddrModel.from_dict(data.get('BillAddr', {})) if data.get('BillAddr') else None,
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {})) if data.get('CurrencyRef') else None,
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {})) if data.get('MetaData') else None,
            Title=data.get('Title', ''),
            Suffix=data.get('Suffix', ''),
            Vendor1099=data.get('Vendor1099', False),
            Balance=data.get('Balance', 0.0),
            SyncToken=data.get('SyncToken', ''),
            PrintOnCheckName=data.get('PrintOnCheckName', ''),
            TaxIdentifier=data.get('TaxIdentifier', ''),
            AcctNum=data.get('AcctNum', ''),
            sparse=data.get('sparse', False),
            Active=data.get('Active', True),
            Id=data.get('Id', '')
        )

class VendorResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Vendor: VendorModel,
        time: str
    ):
        self.Vendor = Vendor
        self.time = time

    def to_dict(self) -> dict:
        return {
            'Vendor': self.Vendor.to_dict(),
            'time': self.time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Vendor=VendorModel.from_dict(data.get('Vendor', {})),
            time=data.get('time', '')
        )

class VendorQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        Vendor: list[VendorModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.Vendor = Vendor
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'Vendor': [vendor.to_dict() for vendor in self.Vendor],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            Vendor=[VendorModel.from_dict(vendor_data) for vendor_data in data.get('Vendor', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )
           
class VendorListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: VendorQueryResponseModel,
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
            QueryResponse=VendorQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )
    

PARTNER_OBJECT = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'company': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'email': {'type': 'string'},
        'phone': {'type': 'string'},
        'is_company': {'type': 'boolean'},
        'mobile': {'type': 'string'},
        'active': {'type': 'boolean'},
        'parent': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'}
            },
        },
        'street': {'type': 'string'},
        'street2': {'type': 'string'},
        'zip': {'type': 'string'},
        'city': {'type': 'string'},
        'state': {'type': 'string'},
        'country': {'type': 'string'}
    }
}

PARTNER_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': PARTNER_OBJECT
    }
}


PARTNER_LIST_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'partners': {
                    'type': 'array',
                    'items': PARTNER_OBJECT
                },
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'total_count': {'type': 'integer'},
                        'limit': {'type': 'integer'},
                        'offset': {'type': 'integer'}
                    }
                }
            }
        }
    }
}


# PARTNER_SCHEMA = {
#     'required': {
#         'name': {
#             'type': str,
#             'display_name': 'Name',
#             'swagger_type': 'string'
#         },
#         'company_id': {
#             'type': int,
#             'display_name': 'Company',
#             'swagger_type': 'integer'
#         },
#         'is_company': {
#             'type': bool,
#             'display_name': 'Is Company',
#             'swagger_type': 'boolean'
#         },
#         'email': {
#             'type': str,
#             'display_name': 'Email',
#             'swagger_type': 'string'
#         },
#         'phone': {
#             'type': str,
#             'display_name': 'Phone',
#             'swagger_type': 'string'
#         },
#         # 'category_id': {
#         #     'type': int,
#         #     'display_name': 'Category',
#         #     'swagger_type': 'integer'
#         # }
#     },
#     'optional': {
#         'parent_id': {
#             'type': int,
#             'display_name': 'Parent',
#             'swagger_type': 'integer'
#         },
#         'street': {
#             'type': str,
#             'display_name': 'Street',
#             'swagger_type': 'string'
#         },
#         'street2': {
#             'type': str,
#             'display_name': 'Street 2',
#             'swagger_type': 'string'
#         },
#         'zip': {
#             'type': str,
#             'display_name': 'Zip',
#             'swagger_type': 'string'
#         },
#         'city': {
#             'type': str,
#             'display_name': 'City',
#             'swagger_type': 'string'
#         },
#         'state_id': {
#             'type': int,
#             'display_name': 'State',
#             'swagger_type': 'integer'
#         },
#         'country_id': {
#             'type': int,
#             'display_name': 'Country',
#             'swagger_type': 'integer'
#         }
#     }
# }


# Parameters for different endpoints
PARTNER_LIST_PARAMS = {
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
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
        }
    ]
}

PARTNER_GET_PARAMS = {
    'path': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'ID of the partner to retrieve',
            'required': True
        }
    ]
}

PARTNER_DELETE_PARAMS = {
    'path': [
        {
            'name': 'partner_id',
            'type': 'integer',
            'description': 'ID of the partner to delete',
            'required': True
        }
    ]
}

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

# PARTNER_CREATE_PARAMS = {
#     'headers': HEADERS,
#     'body': {
#         'schema': PARTNER_SCHEMA,
#         'required': True
#     }
# }

VENDOR_CREATE_RESPONSE = VENDOR_GET_RESPONSE = VendorResponseModel.get_response_schema()
VENDOR_LIST_RESPONSE = VendorListResponseModel.get_response_schema()
VENDOR_SCHEMA = VendorCreateRequestModel.get_request_schema()
VENDOR_CREATE_PARAMS = {
    'headers': HEADERS,
    'body': {
        'schema': VENDOR_SCHEMA,
        'required': True
    }
}

CUSTOMER_CREATE_RESPONSE = CUSTOMER_GET_RESPONSE = CustomerResponseModel.get_response_schema()
CUSTOMER_LIST_RESPONSE = CustomerListResponseModel.get_response_schema()
CUSTOMER_SCHEMA = CustomerCreateRequestModel.get_request_schema()
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



