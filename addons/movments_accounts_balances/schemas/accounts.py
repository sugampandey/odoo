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
    Id: Optional[int] = Field(None, description="Unique identifier for the account")
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
