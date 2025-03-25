import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, get_type_hints, Type, Union, Any, List
from datetime import datetime
from ..constants import CONSTANTS
from ..utils import get_currency_id
from .common import CurrencyRefModel, MetaDataModel, TaxCodeRefModel, ParentRefModel, HEADERS, PaginationMixin
from .schema_generator import RequestSchemaGenerator, ResponseSchemaGenerator
from ..mapping.accounts import CLASSIFICATION_MAPPING, ACCOUNT_TYPE_MAPPING, ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING, TYPE_PREFIX_MAPPING

# TODO: Move these to common module
class CurrencyRefModel(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

class MetaDataModel(BaseModel):
    CreateTime: datetime
    LastUpdatedTime: datetime

class TaxCodeRefModel(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None

class ParentRefModel(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None


class AccountCreateRequestModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    AcctNum: str = Field(..., description="Account Number")
    AccountType: str = Field(..., description="Account Type")
    AccountSubType: Optional[str] = Field(None, description="Sub-type of account")
    CurrencyRef: Optional[CurrencyRefModel] = Field(None, description="Currency reference")

    @field_validator('AccountType')
    def validate_account_type(cls, value: str) -> str:
        mapped_type = ACCOUNT_TYPE_MAPPING.get(value)
        if not mapped_type:
            raise ValueError(f"Invalid account type: {value}")
        return mapped_type

    def get_unique_account_code(self, account_type: str) -> str:
        type_prefix = TYPE_PREFIX_MAPPING.get(account_type, 'GN')  # GN as default prefix
        unique_id = str(uuid.uuid4()).replace('-', '.')
        # Format: PREFIX-UUID (e.g., AR.550e8400.e29b.41d4.a716.446655440000)
        return f"{type_prefix}.{unique_id}"

    
    def create_account_vals(self, request, company_id: int) -> dict:
        currency_value = self.CurrencyRef.value if self.CurrencyRef else 'USD'
        return {
            'name': self.Name,
            'code': self.get_unique_account_code(self.AccountType),
            'account_type': self.AccountType,
            'account_number': self.AcctNum,
            'sub_type_code': self.AccountSubType,
            'company_id': company_id,
            'currency_id': get_currency_id(request, currency_value) if currency_value else None
        }


class AccountModel(BaseModel):
    Id: Optional[str] = Field(None, description="Unique identifier for the account")
    Name: str = Field(..., min_length=1, max_length=256, description="Account name")
    AccountType: str = Field(..., description="Type of account")
    FullyQualifiedName: Optional[str] = Field(None, description="Full hierarchical name of the account")
    AccountSubType: Optional[str] = Field(None, description="Sub-type of account")
    Classification: Optional[str] = Field(None, description="Account classification")
    AcctNum: Optional[str] = Field(None, description="Account Number")
    CurrentBalance: Optional[float] = Field(0.0, description="Current balance")
    CurrentBalanceWithSubAccounts: Optional[float] = Field(0.0, description="Current balance including sub-accounts")
    CurrencyRef: Optional[CurrencyRefModel] = Field(None, description="Currency reference")
    Active: Optional[bool] = Field(True, description="Whether the account is active")
    domain: Optional[str] = None
    sparse: Optional[bool] = False
    MetaData: Optional[MetaDataModel] = None
    SyncToken: Optional[str] = None
    SubAccount: Optional[bool] = False
    Description: Optional[str] = None
    TxnLocationType: Optional[str] = None
    AccountAlias: Optional[str] = None
    TaxCodeRef: Optional[TaxCodeRefModel] = None
    ParentRef: Optional[ParentRefModel] = None

    class Config:
        from_attributes = True  # Allows conversion from ORM objects
    
    @staticmethod
    def get_classification(classification: str) -> str:
        return CLASSIFICATION_MAPPING.get(classification)
    
    @staticmethod
    def get_account_type(account_type: str) -> str:
        return ACCOUNT_TYPE_MAPPING.get(account_type)
    
    @classmethod
    def account_object(cls, account) -> "AccountModel":
        try:
            meta_data = MetaDataModel(
                CreateTime=account.create_date,
                LastUpdatedTime=account.write_date
            )

            currency_ref = None
            if account.currency_id:
                currency_ref = CurrencyRefModel(
                    name=account.currency_id.full_name,
                    value=account.currency_id.name
                )

            return cls(
                Id=str(account.id),
                Name=account.name,
                FullyQualifiedName=account.name,
                AccountType=cls.get_account_type(account.account_type),
                Classification=cls.get_classification(account.internal_group),
                MetaData=meta_data,
                CurrencyRef=currency_ref,
                Active=not account.deprecated,
                AcctNum=account.account_number if account.account_number else None,
                AccountSubType=account.sub_type_code if account.sub_type_code else None,
            )
        except Exception as e:
            raise ValueError(f"Error converting: {str(e)}")


class AccountQueryResponse(BaseModel):
    startPosition: int = Field(0, description="Starting position of the result set")
    maxResults: int = Field(20, description="Maximum number of results to return")
    totalCount: int = Field(..., description="Total count of records")
    Account: List[AccountModel] = Field(..., description="List of accounts")


class AccountQueryResponseModel(PaginationMixin):
    """
    Response model for account queries with pagination
    """
    totalCount: int = Field(..., ge=0, description="Total count of records")
    Account: List[AccountModel] = Field(..., description="List of accounts")

    @field_validator('Account')
    def validate_accounts(cls, accounts: List[AccountModel]) -> List[AccountModel]:
        if not accounts:
            raise ValueError("Account list cannot be empty")
        return accounts


class AccountResponseModel(BaseModel):
    Account: AccountModel = Field(..., description="Account details")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    @classmethod
    def create_account_response(cls, account: AccountModel) -> "AccountResponseModel":
        return cls(
            Account=AccountModel.account_object(account),
            time=datetime.now()
        )
        

class AccountListResponseModel(BaseModel):
    QueryResponse: AccountQueryResponseModel = Field(..., description="Query response containing account list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    
    @classmethod
    def list_account_response(cls, accounts: List[AccountModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "AccountListResponseModel":
        query_response = AccountQueryResponseModel(
            startPosition=start_position,
            maxResults=max_results,
            totalCount=total_count,
            Account=accounts
        )
        return cls(
            QueryResponse=query_response,
            time=datetime.now()
        )



# class AccountModel(ResponseSchemaGenerator):
#     def __init__(
#         self,
#         FullyQualifiedName: Optional[str] = None,
#         domain: Optional[str] = None,
#         Name: Optional[str] = None,
#         Classification: Optional[str] = None,
#         AccountSubType: Optional[str] = None,
#         CurrencyRef: Optional[CurrencyRefModel] = None,
#         CurrentBalanceWithSubAccounts: Optional[float] = None,
#         sparse: Optional[bool] = None,
#         MetaData: Optional[MetaDataModel] = None,
#         AccountType: Optional[str] = None,
#         CurrentBalance: Optional[float] = None,
#         Active: Optional[bool] = None,
#         SyncToken: Optional[str] = None,
#         Id: Optional[str] = None,
#         SubAccount: Optional[bool] = None,
#         AcctNum : Optional[str] = None,
#         Description: Optional[str] = None,
#         TxnLocationType : Optional[str] = None,
#         AccountAlias : Optional[str] = None,
#         TaxCodeRef : Optional[TaxCodeRefModel] = None,
#         ParentRef : Optional[ParentRefModel] = None,
#     ):
#         self.FullyQualifiedName = FullyQualifiedName
#         self.domain = domain
#         self.Name = Name
#         self.Classification = self.get_classification(Classification)
#         self.AccountSubType = AccountSubType
#         self.CurrencyRef = CurrencyRef
#         self.CurrentBalanceWithSubAccounts = CurrentBalanceWithSubAccounts
#         self.sparse = sparse
#         self.MetaData = MetaData
#         self.AccountType = self.get_account_type(AccountType)
#         self.CurrentBalance = CurrentBalance
#         self.Active = Active
#         self.SyncToken = SyncToken
#         self.Id = Id
#         self.SubAccount = SubAccount
#         self.AcctNum = AcctNum
#         self.Description = Description
#         self.TxnLocationType = TxnLocationType
#         self.AccountAlias = AccountAlias
#         self.TaxCodeRef = TaxCodeRef
#         self.ParentRef = ParentRef

#     def get_classification(self, classification):
#         return CLASSIFICATION_MAPPING.get(classification)
    
#     def get_account_type(self, account_type):
#         return ACCOUNT_TYPE_MAPPING.get(account_type)
    
#     def account_object(self, account):
#         meta_data = MetaDataModel(
#             CreateTime = account.create_date.strftime(CONSTANTS['DATE_FORMAT']),
#             LastUpdatedTime = account.write_date.strftime(CONSTANTS['DATE_FORMAT']),
#         )
#         if account.currency_id:
#             currency_ref = CurrencyRefModel(
#                 name=account.currency_id.full_name,
#                 value=account.currency_id.name
#             )
#         else:
#             currency_ref = None
#         return AccountModel(
#             Id=account.id,
#             Name=account.name,
#             FullyQualifiedName=account.name,
#             AccountType=account.account_type,
#             Classification=account.internal_group,
#             MetaData=meta_data,
#             CurrencyRef=currency_ref,
#             Active= not account.deprecated,
#             AcctNum=account.account_number,
#             AccountSubType = account.sub_type_code
#         )
    
#     def create_account_response(self, account):
#         return AccountResponseModel(
#             Account=self.account_object(account),
#             time=datetime.datetime.now().strftime(CONSTANTS['DATE_FORMAT'])
#         ).to_dict()
    
#     def list_account_response(self, accounts_data, startPosition, maxResults, totalCount):
#         QueryResponse=AccountQueryResponseModel(
#                 startPosition=startPosition,
#                 Account=accounts_data,
#                 maxResults=maxResults,
#                 totalCount= totalCount
#             )
#         return AccountListResponseModel(
#             QueryResponse=QueryResponse,
#             time=datetime.datetime.now().strftime(CONSTANTS['DATE_FORMAT'])
#         ).to_dict()


#     def to_dict(self) -> dict:
#         return {
#             'FullyQualifiedName': self.FullyQualifiedName,
#             'domain': self.domain,
#             'Name': self.Name,
#             'Classification': self.Classification,
#             'AccountSubType': self.AccountSubType,
#             'CurrencyRef': self.CurrencyRef.to_dict() if self.CurrencyRef else None,
#             'CurrentBalanceWithSubAccounts': self.CurrentBalanceWithSubAccounts,
#             'sparse': self.sparse,
#             'MetaData': self.MetaData.to_dict() if self.MetaData else None,
#             'AccountType': self.AccountType,
#             'CurrentBalance': self.CurrentBalance,
#             'Active': self.Active,
#             'SyncToken': self.SyncToken,
#             'Id': self.Id,
#             'SubAccount': self.SubAccount,
#             'AcctNum': self.AcctNum,
#             'Description': self.Description,
#             'TxnLocationType': self.TxnLocationType,
#             'AccountAlias': self.AccountAlias,
#             'TaxCodeRef': self.TaxCodeRef.to_dict() if self.TaxCodeRef else None,
#             'ParentRef': self.ParentRef.to_dict() if self.ParentRef else None,
#         }

#     @classmethod
#     def from_dict(cls, data: dict):
#         return cls(
#             FullyQualifiedName=data.get('FullyQualifiedName', ''),
#             domain=data.get('domain', ''),
#             Name=data.get('Name', ''),
#             Classification=data.get('Classification', ''),
#             AccountSubType=data.get('AccountSubType', ''),
#             CurrencyRef=CurrencyRefModel.from_dict(data.get('CurrencyRef', {})),
#             CurrentBalanceWithSubAccounts=data.get('CurrentBalanceWithSubAccounts', 0),
#             sparse=data.get('sparse', False),
#             MetaData=MetaDataModel.from_dict(data.get('MetaData', {})),
#             AccountType=data.get('AccountType', ''),
#             CurrentBalance=data.get('CurrentBalance', 0),
#             Active=data.get('Active', False),
#             SyncToken=data.get('SyncToken', ''),
#             Id=data.get('Id', ''),
#             SubAccount=data.get('SubAccount', False),
#             AcctNum=data.get('AcctNum', ''),
#             Description=data.get('Description', ''),
#             TxnLocationType=data.get('TxnLocationType', ''),
#             AccountAlias=data.get('AccountAlias', ''),
#             TaxCodeRef=TaxCodeRefModel.from_dict(data.get('TaxCodeRef', {})),
#             ParentRef=ParentRefModel.from_dict(data.get('ParentRef', {})),
#         )

# class AccountResponseModel(ResponseSchemaGenerator):
#     def __init__(
#         self,
#         Account: AccountModel,
#         time: str
#     ):
#         self.Account = Account
#         self.time = time

#     def to_dict(self) -> dict:
#         return {
#             'Account': self.Account.to_dict(),
#             'time': self.time
#         }

#     @classmethod
#     def from_dict(cls, data: dict):
#         return cls(
#             Account=AccountModel.from_dict(data.get('Account', {})),
#             time=data.get('time', '')
#         )


# class AccountQueryResponseModel(ResponseSchemaGenerator):
#     def __init__(
#         self,
#         startPosition: int,
#         Account: list[AccountModel],
#         maxResults: int,
#         totalCount: int
#     ):
#         self.startPosition = startPosition
#         self.Account = Account
#         self.maxResults = maxResults
#         self.totalCount = totalCount

#     def to_dict(self) -> dict:
#         return {
#             'startPosition': self.startPosition,
#             'Account': [account.to_dict() for account in self.Account],
#             'maxResults': self.maxResults,
#             'totalCount': self.totalCount
#         }

#     @classmethod
#     def from_dict(cls, data: dict):
#         return cls(
#             startPosition=data.get('startPosition', 0),
#             Account=[AccountModel.from_dict(account_data) for account_data in data.get('Account', [])],
#             maxResults=data.get('maxResults', 0),
#             totalCount=data.get('totalCount', 0)
#         )
    
# class AccountListResponseModel(ResponseSchemaGenerator):
#     def __init__(
#         self,
#         QueryResponse: AccountQueryResponseModel,
#         time: str
#     ):
#         self.QueryResponse = QueryResponse
#         self.time = time

#     def to_dict(self) -> dict:
#         return {
#             'QueryResponse': self.QueryResponse.to_dict(),
#             'time': self.time
#         }
    
#     @classmethod
#     def from_dict(cls, data: dict):
#         return cls(
#             QueryResponse=AccountQueryResponseModel.from_dict(data.get('QueryResponse', {})),
#             time=data.get('time', '')
#         )


# ACCOUNT_CREATE_RESPONSE = ACCOUNT_GET_RESPONSE = AccountResponseModel.get_response_schema()
# ACCOUNT_LIST_RESPONSE = AccountListResponseModel.get_response_schema()

# ACCOUNT_SCHEMA = {}


# # PARAMS
# ACCOUNT_HEADERS = [
#     {
#         'name': 'X-PaymentMethod',
#         'type': 'string',
#         'description': 'Payment Method',
#         'required': False,
#         'enum': ['none', 'cash', 'bank', 'credit_card']
#     }
# ]
# ACCOUNT_CREATE_PARAMS = {
#     'headers': ACCOUNT_HEADERS + HEADERS,
#     'body': {
#         'schema': ACCOUNT_SCHEMA,
#         'required': True
#     }
# }

# ACCOUNT_GET_PARAMS = {
#     'path': [
#         {
#             'name': 'account_id',
#             'type': 'integer',
#             'description': 'ID of the account to retrieve',
#             'required': True
#         }
#     ],
#     'query': [
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'Filter by company ID',
#             'required': True
#         },
#     ]
# }

# ACCOUNT_LIST_PARAMS = {
#     'query': [
#         {
#             'name': 'account_type',
#             'type': 'string',
#             'description': 'Filter by account type',
#             'required': False,
#             'enum': list(ACCOUNT_TYPE_DOCYT_TO_ODOO_MAPPING.keys())
#         },
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'Filter by company ID',
#             'required': True
#         },
#         {
#             'name': 'name',
#             'type': 'string',
#             'description': 'Filter by name',
#             'required': False
#         },
#         {
#             'name': 'active',
#             'type': 'boolean',
#             'description': 'Filter by active',
#             'required': False
#         },
#         {
#             'name': 'maxresults',
#             'type': 'integer',
#             'description': 'Number of records to return (default: 100)',
#             'required': False,
#             'default': 20
#         },
#         {
#             'name': 'startposition',
#             'type': 'integer',
#             'description': 'Number of records to skip (default: 0)',
#             'required': False,
#             'default': 0
#         },
#     ]
# }

# ACCOUNT_DELETE_PARAMS = {
#     'path': [
#         {
#             'name': 'account_id',
#             'type': 'integer',
#             'description': 'ID of the account to delete',
#             'required': True
#         },
#     ],
#     'query': [
#         {
#             'name': 'company_id',
#             'type': 'integer',
#             'description': 'company ID of the account to delete',
#             'required': True
#         },
#     ]
# }

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
