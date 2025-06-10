import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from .common import COMPANY_HEADERS, ACCESS_TOKEN_HEADER, MetaDataModel, PaginationResponseModel, RefModel
from ..mapping.accounts import ACCOUNT_CLASSIFICATION_MAPPING, ACCOUNT_TYPE_MAPPING, TYPE_PREFIX_MAPPING
from ..repositories.currency import CurrencyService


class AccountCreateRequestModel(BaseModel):
    Name: str = Field(..., min_length=1, max_length=256)
    AcctNum: str = Field(..., description="Account Number")
    AccountType: str = Field(..., description="Account Type")
    AccountSubType: Optional[str] = Field(None, description="Sub-type of account")
    CurrencyRef: Optional[RefModel] = Field(None, description="Currency reference")

    @field_validator('AccountType')
    def validate_account_type(cls, value: str) -> str:
        mapped_type = ACCOUNT_TYPE_MAPPING.get(value)
        if not mapped_type:
            raise ValueError(f"Invalid account type: {value}")
        return mapped_type
    
    @field_validator('Name', 'AcctNum', 'AccountType')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v

    def get_unique_account_code(self, account_type: str) -> str:
        type_prefix = TYPE_PREFIX_MAPPING.get(account_type, 'GN')  # GN as default prefix
        unique_id = str(uuid.uuid4()).replace('-', '.')
        # Format: PREFIX-UUID (e.g., AR.550e8400.e29b.41d4.a716.446655440000)
        return f"{type_prefix}.{unique_id}"

    
    def create_account_vals(self, request, company_id: int) -> dict:
        currency_service = CurrencyService(request.env)
        currency_value = self.CurrencyRef.value if self.CurrencyRef else currency_service.get_default_currency_id()
        return {
            'name': self.Name,
            'code': self.get_unique_account_code(self.AccountType),
            'account_type': self.AccountType,
            'account_number': self.AcctNum,
            'sub_type_code': self.AccountSubType,
            'company_id': company_id,
            'currency_id': currency_service.get_currency_id(currency_value) if currency_value else None
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
    CurrencyRef: Optional[RefModel] = Field(None, description="Currency reference")
    Active: Optional[bool] = Field(True, description="Whether the account is active")
    domain: Optional[str] = None
    sparse: Optional[bool] = False
    MetaData: Optional[MetaDataModel] = None
    SyncToken: Optional[str] = None
    SubAccount: Optional[bool] = False
    Description: Optional[str] = None
    TxnLocationType: Optional[str] = None
    AccountAlias: Optional[str] = None
    TaxCodeRef: Optional[RefModel] = None
    ParentRef: Optional[RefModel] = None

    class Config:
        from_attributes = True  # Allows conversion from ORM objects
    
    @staticmethod
    def get_classification(classification: str) -> str:
        return ACCOUNT_CLASSIFICATION_MAPPING.get(classification)
    
    @staticmethod
    def get_account_type(account_type: str) -> str:
        return ACCOUNT_TYPE_MAPPING.get(account_type)
    
    @classmethod
    def account_object(cls, account) -> "AccountModel":
        try:
            meta_data = MetaDataModel(
                CreateTime=account.create_date.replace(tzinfo=timezone.utc) if account.create_date else None,
                LastUpdatedTime=account.write_date.replace(tzinfo=timezone.utc) if account.write_date else None
            )

            currency_ref = None
            if account.currency_id:
                currency_ref = RefModel(
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


class AccountQueryResponseModel(PaginationResponseModel):
    """
    Response model for account queries with pagination
    """
    Account: List[AccountModel] = Field(..., description="List of accounts")

    @field_validator('Account')
    def validate_accounts(cls, accounts: List[AccountModel]) -> List[AccountModel]:
        if not accounts:
            raise ValueError("No Account found")
        return accounts


class AccountResponseModel(BaseModel):
    Account: AccountModel = Field(..., description="Account details")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat()
        }

    @classmethod
    def create_account_response(cls, account: AccountModel) -> "AccountResponseModel":
        return cls(
            Account=AccountModel.account_object(account),
            time=datetime.now(timezone.utc)
        )
        

class AccountListResponseModel(BaseModel):
    QueryResponse: AccountQueryResponseModel = Field(..., description="Query response containing account list")
    time: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat()
        }
    
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
            time=datetime.now(timezone.utc)
        )



ACCOUNT_HEADERS = [
    {
        'name': 'X-PaymentMethod',
        'type': 'string',
        'description': 'Payment Method',
        'required': False,
        'enum': ['none', 'cash', 'bank', 'credit_card']
    }
] + COMPANY_HEADERS + ACCESS_TOKEN_HEADER


