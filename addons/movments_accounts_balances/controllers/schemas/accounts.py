from typing import Optional, Literal, get_type_hints, Type, Union, Any
from datetime import datetime
from .common import CurrencyRefModel, MetaDataModel, TaxCodeRef, HEADERS
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator
from ..mapping.accounts import CLASSIFICATION_MAPPING, ACCOUNT_TYPE_MAPPING, ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING

class ParentRef(ResponseSchemaGenerator):
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
    
class AccountCreateRequestModel(RequestSchemaGenerator):
    def __init__(
        self,
        Name: str,
        AcctNum: str,
        AccountType: str,
        AccountSubType: Optional[str] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
        # PaymentMethod: Optional[Literal['none', 'cash', 'bank', 'credit_card']] = None
    ):
        self.Name = Name
        self.AcctNum = AcctNum
        self.AccountType = self.get_account_type(AccountType)
        self.AccountSubType = AccountSubType
        self.CurrencyRef = CurrencyRef
        # self.PaymentMethod = PaymentMethod

    def get_account_type(self, account_type):
        return ACCOUNT_TYPE_MAPPING.get(account_type)
    
    def to_dict(self):
        return {
            'Name': self.Name,
            'AcctNum': self.AcctNum,
            'AccountType': self.AccountType,
            'CurrencyRef': self.CurrencyRef,
            'AccountSubType': self.AccountSubType,
            # 'PaymentMethod': self.PaymentMethod
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Name=data.get('Name'),
            AcctNum=data.get('AcctNum'),
            AccountType=data.get('AccountType'),
            CurrencyRef=data.get('CurrencyRef'),
            AccountSubType=data.get('AccountSubType'),
            # PaymentMethod=data.get('PaymentMethod')
        )


class AccountModel(ResponseSchemaGenerator):
    def __init__(
        self,
        FullyQualifiedName: Optional[str] = None,
        domain: Optional[str] = None,
        Name: Optional[str] = None,
        Classification: Optional[str] = None,
        AccountSubType: Optional[str] = None,
        CurrencyRef: Optional[CurrencyRefModel] = None,
        CurrentBalanceWithSubAccounts: Optional[float] = None,
        sparse: Optional[bool] = None,
        MetaData: Optional[MetaDataModel] = None,
        AccountType: Optional[str] = None,
        CurrentBalance: Optional[float] = None,
        Active: Optional[bool] = None,
        SyncToken: Optional[str] = None,
        Id: Optional[str] = None,
        SubAccount: Optional[bool] = None,
        AcctNum : Optional[str] = None,
        Description: Optional[str] = None,
        TxnLocationType : Optional[str] = None,
        AccountAlias : Optional[str] = None,
        TaxCodeRef : Optional[TaxCodeRef] = None,
        ParentRef : Optional[ParentRef] = None,
    ):
        self.FullyQualifiedName = FullyQualifiedName
        self.domain = domain
        self.Name = Name
        self.Classification = self.get_classification(Classification)
        self.AccountSubType = AccountSubType
        self.CurrencyRef = CurrencyRef
        self.CurrentBalanceWithSubAccounts = CurrentBalanceWithSubAccounts
        self.sparse = sparse
        self.MetaData = MetaData
        self.AccountType = self.get_account_type(AccountType)
        self.CurrentBalance = CurrentBalance
        self.Active = Active
        self.SyncToken = SyncToken
        self.Id = Id
        self.SubAccount = SubAccount
        self.AcctNum = AcctNum
        self.Description = Description
        self.TxnLocationType = TxnLocationType
        self.AccountAlias = AccountAlias
        self.TaxCodeRef = TaxCodeRef
        self.ParentRef = ParentRef

    def get_classification(self, classification):
        return CLASSIFICATION_MAPPING.get(classification)
    
    def get_account_type(self, account_type):
        return ACCOUNT_TYPE_MAPPING.get(account_type)


    def to_dict(self) -> dict:
        return {
            'FullyQualifiedName': self.FullyQualifiedName,
            'domain': self.domain,
            'Name': self.Name,
            'Classification': self.Classification,
            'AccountSubType': self.AccountSubType,
            'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
            'CurrentBalanceWithSubAccounts': self.CurrentBalanceWithSubAccounts,
            'sparse': self.sparse,
            'MetaData': self.MetaData.to_dict() if self.MetaData else None,
            'AccountType': self.AccountType,
            'CurrentBalance': self.CurrentBalance,
            'Active': self.Active,
            'SyncToken': self.SyncToken,
            'Id': self.Id,
            'SubAccount': self.SubAccount,
            'AcctNum': self.AcctNum,
            'Description': self.Description,
            'TxnLocationType': self.TxnLocationType,
            'AccountAlias': self.AccountAlias,
            'TaxCodeRef': self.TaxCodeRef.to_dict() if self.TaxCodeRef else None,
            'ParentRef': self.ParentRef.to_dict() if self.ParentRef else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            FullyQualifiedName=data.get('FullyQualifiedName', ''),
            domain=data.get('domain', ''),
            Name=data.get('Name', ''),
            Classification=data.get('Classification', ''),
            AccountSubType=data.get('AccountSubType', ''),
            CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {})),
            CurrentBalanceWithSubAccounts=data.get('CurrentBalanceWithSubAccounts', 0),
            sparse=data.get('sparse', False),
            MetaData=MetaDataModel.from_dict(data.get('MetaData', {})),
            AccountType=data.get('AccountType', ''),
            CurrentBalance=data.get('CurrentBalance', 0),
            Active=data.get('Active', False),
            SyncToken=data.get('SyncToken', ''),
            Id=data.get('Id', ''),
            SubAccount=data.get('SubAccount', False),
            AcctNum=data.get('AcctNum', ''),
            Description=data.get('Description', ''),
            TxnLocationType=data.get('TxnLocationType', ''),
            AccountAlias=data.get('AccountAlias', ''),
            TaxCodeRef=TaxCodeRef.from_dict(data.get('TaxCodeRef', {})),
            ParentRef=ParentRef.from_dict(data.get('ParentRef', {})),
        )

class AccountResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        Account: AccountModel,
        time: str
    ):
        self.Account = Account
        self.time = time

    def to_dict(self) -> dict:
        return {
            'Account': self.Account.to_dict(),
            'time': self.time
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Account=AccountModel.from_dict(data.get('Account', {})),
            time=data.get('time', '')
        )


class AccountQueryResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        startPosition: int,
        Account: list[AccountModel],
        maxResults: int,
        totalCount: int
    ):
        self.startPosition = startPosition
        self.Account = Account
        self.maxResults = maxResults
        self.totalCount = totalCount

    def to_dict(self) -> dict:
        return {
            'startPosition': self.startPosition,
            'Account': [account.to_dict() for account in self.Account],
            'maxResults': self.maxResults,
            'totalCount': self.totalCount
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            startPosition=data.get('startPosition', 0),
            Account=[AccountModel.from_dict(account_data) for account_data in data.get('Account', [])],
            maxResults=data.get('maxResults', 0),
            totalCount=data.get('totalCount', 0)
        )
    
class AccountListResponseModel(ResponseSchemaGenerator):
    def __init__(
        self,
        QueryResponse: AccountQueryResponseModel,
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
            QueryResponse=AccountQueryResponseModel.from_dict(data.get('QueryResponse', {})),
            time=data.get('time', '')
        )


ACCOUNT_CREATE_RESPONSE = ACCOUNT_GET_RESPONSE = AccountResponseModel.get_schema()
ACCOUNT_LIST_RESPONSE = AccountListResponseModel.get_schema()

ACCOUNT_SCHEMA = AccountCreateRequestModel.get_schema()


# PARAMS
ACCOUNT_HEADERS = [
    {
        'name': 'X-PaymentMethod',
        'type': 'string',
        'description': 'Payment Method',
        'required': False,
        'enum': ['none', 'cash', 'bank', 'credit_card']
    }
]
ACCOUNT_CREATE_PARAMS = {
    'headers': ACCOUNT_HEADERS + HEADERS,
    'body': {
        'schema': ACCOUNT_SCHEMA,
        'required': True
    }
}

ACCOUNT_GET_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the account to retrieve',
            'required': True
        }
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
    ]
}

ACCOUNT_LIST_PARAMS = {
    'query': [
        {
            'name': 'account_type',
            'type': 'string',
            'description': 'Filter by account type',
            'required': False,
            'enum': list(ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING.keys())
        },
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'Filter by company ID',
            'required': True
        },
        {
            'name': 'active',
            'type': 'boolean',
            'description': 'Filter by active',
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
        },
    ]
}

ACCOUNT_DELETE_PARAMS = {
    'path': [
        {
            'name': 'account_id',
            'type': 'integer',
            'description': 'ID of the account to delete',
            'required': True
        },
    ],
    'query': [
        {
            'name': 'company_id',
            'type': 'integer',
            'description': 'company ID of the account to delete',
            'required': True
        },
    ]
}

# ACCOUNT_UPDATE_PARAMS = {
#     'path': [
#         {
#             'name': 'account_id',
#             'type': 'integer',
#             'description': 'ID of the account to update',
#             'required': True
#         }
#     ],
#     'body': {
#         'schema': ACCOUNT_SCHEMA,
#         'required': True
#     }
# }
