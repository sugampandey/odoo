from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional, List
from .common import MetaDataModel, PaginationResponseModel, RefModel
from ..enums import PostingType, DetailType
from ..repositories.journal import JournalService

# description = ref
# account_ref ={name-name, value-id}
# class_ref ={name-name, value-id}
# entity = {type=Vendor/Customer , Entityref = {name-name, value-id}}
# Amount = amount
# postingtype = Debit/Credit -- debit/credit columns
# Detailtype= JournalEntryLineDetail
# Id = id


class EntityModel(BaseModel):
    Type: str = Field(..., description="Entity type")
    EntityRef: RefModel = Field(..., description="Entity reference")

    class Config:
        from_attributes = True
    
    @field_validator('Type')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v
    
class JournalEntryLineDetailModel(BaseModel):
    PostingType: str = Field(..., description="Type of posting (Debit/Credit)")
    AccountRef: RefModel = Field(..., description="Account reference")
    TaxApplicableOn: Optional[str] = Field(None, description="Tax applicable on")
    ClassRef: Optional[RefModel] = Field(None, description="Class reference")
    TaxCodeRef: Optional[RefModel] = Field(None, description="Tax code reference")
    Entity: EntityModel = Field(..., description="Entity details")

    class Config:
        from_attributes = True
    
    @field_validator('PostingType')
    def validate_posting_type(cls, v):
        if v and v not in [pt.value for pt in PostingType]:
            raise ValueError(f"Invalid posting type: {v}")
        return v
    
    @classmethod
    def create_from_move_line(cls, move_line) -> 'JournalEntryLineDetailModel':
        """Creates a JournalEntryLineDetailModel instance from a move line."""
        return cls(
            PostingType=PostingType.DEBIT if move_line.debit != 0 else PostingType.CREDIT,
            AccountRef=cls._create_account_ref(move_line),
            ClassRef=cls._create_class_ref(move_line),
            Entity=cls._create_entity(move_line)
        )

    @staticmethod
    def _create_account_ref(move_line) -> RefModel:
        return RefModel(
            name=move_line.account_id.name,
            value=str(move_line.account_id.id),
        )

    @staticmethod
    def _create_class_ref(move_line) -> Optional[RefModel]:
        analytic_class = move_line.analytic_line_ids
        if not analytic_class:
            return None
        return RefModel(
            name=analytic_class.account_id.name,
            value=str(analytic_class.account_id.id),
        )

    @staticmethod
    def _create_entity(move_line) -> EntityModel:
        entity_ref = RefModel(
            name=move_line.partner_id.name,
            value=str(move_line.partner_id.id),
        )
        return EntityModel(
            Type=move_line.partner_id.category_id.name,
            EntityRef=entity_ref
        )

class LineRequestModel(BaseModel):
    JournalEntryLineDetail: JournalEntryLineDetailModel
    DetailType: str = Field(..., description="Type of detail")
    Amount: float = Field(..., description="Transaction amount")
    Description: Optional[str] = Field(None, description="Line item description")
    Id: Optional[int] = Field(None, description="Line item ID")

    class Config:
        from_attributes = True
    
    @field_validator('DetailType')
    def validate_non_empty_string(cls, v, info):
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
        return v

    def create_line_vals(self, company_id: int) -> dict:
        account_id = int(self.JournalEntryLineDetail.AccountRef.value) if self.JournalEntryLineDetail.AccountRef else None
        posting_type = self.JournalEntryLineDetail.PostingType.lower() if self.JournalEntryLineDetail.PostingType else None
        analytic_class_id = int(self.JournalEntryLineDetail.ClassRef.value) if self.JournalEntryLineDetail.ClassRef else None
        partner_id = int(self.JournalEntryLineDetail.Entity.EntityRef.value) if self.JournalEntryLineDetail.Entity and self.JournalEntryLineDetail.Entity.EntityRef else None
        return {
            'company_id': company_id,
            'account_id': account_id,
            'ref': self.Description if self.Description else None,
            'debit': self.Amount if posting_type == 'debit' else 0,
            'credit': self.Amount if posting_type == 'credit' else 0,
            'partner_id': partner_id,
            'analytic_distribution': {analytic_class_id: 100} if analytic_class_id else None,
        }


class JournalEntryRequestModel(BaseModel):
    Line: List[LineRequestModel] = Field(..., description="Journal entry lines")
    CurrencyRef: Optional[RefModel] = Field(None, description="Currency reference")

    class Config:
        from_attributes = True

    @field_validator('Line')
    def validate_balanced_entry(cls, Line):
        total_debit = sum(
            move_line.Amount 
            for move_line in Line 
            if move_line.JournalEntryLineDetail.PostingType == PostingType.DEBIT
        )
        total_credit = sum(
            move_line.Amount 
            for move_line in Line 
            if move_line.JournalEntryLineDetail.PostingType == PostingType.CREDIT
        )
        
        # Using a small tolerance for rounding differences
        tolerance = Decimal('0.01')
        if abs(total_debit - total_credit) > tolerance:
            difference = abs(total_debit - total_credit)
            raise ValueError(
                f'Journal entry is not balanced. '
                f'Difference between debit ({total_debit}) and credit ({total_credit}) '
                f'is {difference}'
            )
        return Line
    
    @field_validator('Line')
    def validate_non_zero_amounts(cls, Line):
        for move_line in Line:
            if move_line.Amount <= 0:
                raise ValueError(
                    f'Invalid amount {move_line.Amount}. Amount must be greater than 0'
                )
        return Line
    
    @field_validator('Line')
    def validate_minimum_lines(cls, Line):
        if len(Line) < 2:
            raise ValueError(
                'Journal entry must have at least 2 lines'
            )
        return Line

    def create_journal_entry_vals(self, company_id: int) -> dict:
        return {
            'move_type': 'entry',
            # 'partner_id': partner_id,
            'date': datetime.now().date(),
            'company_id': company_id,
            'invoice_line_ids': [(0,0, line.create_line_vals(company_id)) for line in self.Line]
        }
        

class DescriptionLineDetailModel(BaseModel):
    TaxCodeRef: Optional[RefModel] = Field(None, description="Tax code reference")
    ServiceDate: Optional[str] = Field(None, description="Service date")

    class Config:
        from_attributes = True

class LineResponseModel(BaseModel):
    DetailType: Optional[str] = Field(None, description="Type of detail")
    Amount: Optional[float] = Field(None, description="Transaction amount")
    Description: Optional[str] = Field(None, description="Line item description")
    Id: Optional[int] = Field(None, description="Line item ID")
    JournalEntryLineDetail: Optional[JournalEntryLineDetailModel] = None
    DescriptionLineDetail: Optional[DescriptionLineDetailModel] = None

    class Config:
        from_attributes = True
    
    @model_validator(mode='after')
    def validate_detail_type(self) -> 'LineResponseModel':
        detail_type = self.DetailType
        if detail_type == DetailType.JOURNAL_ENTRY and not self.JournalEntryLineDetail:
            raise ValueError(f"{DetailType.JOURNAL_ENTRY} detail is required when DetailType is '{DetailType.JOURNAL_ENTRY}'")
        if detail_type == DetailType.DESCRIPTION and not self.DescriptionLineDetail:
            raise ValueError(f"{DetailType.DESCRIPTION} detail is required when DetailType is '{DetailType.DESCRIPTION}'")
        return self
    
    @classmethod
    def create_journal_lines(cls, journal_entry) -> List['LineResponseModel']:
        """Creates a list of LineResponseModel instances from journal entry lines."""
        print(journal_entry)
        return [
            cls(
                DetailType=DetailType.JOURNAL_ENTRY,
                Amount=cls._get_amount(move_line),
                Id=move_line.id,
                Description=move_line.ref if move_line.ref else None,
                JournalEntryLineDetail=JournalEntryLineDetailModel.create_from_move_line(move_line)
            ) 
            for move_line in journal_entry.line_ids
        ]

    @staticmethod
    def _get_amount(move_line) -> float:
        """Determines the amount based on debit or credit value."""
        return move_line.debit if move_line.debit != 0 else move_line.credit


class JournalEntryModel(BaseModel):
    Line: List[LineResponseModel] = Field(..., description="Journal entry lines")
    SyncToken: Optional[str] = Field(None, description="Sync token")
    domain: Optional[str] = Field(None, description="Domain")
    TxnDate: Optional[datetime] = Field(None, description="Transaction date")
    sparse: Optional[bool] = Field(None, description="Sparse flag")
    Adjustment: Optional[bool] = Field(None, description="Adjustment flag")
    Id: Optional[int] = Field(None, description="Journal entry ID")
    TxnTaxDetail: Optional[dict] = Field(None, description="Transaction tax details")
    MetaData: Optional[MetaDataModel] = Field(None, description="Metadata")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def journal_entry_object(cls, journal_entry):
        # description = ref
        # account_ref ={name-name, value-id}
        # class_ref ={name-name, value-id}
        # entity = {type=Vendor/Customer , Entityref = {name-name, value-id}}
        # Amount = amount
        # postingtype = Debit/Credit -- debit/credit columns
        # Detailtype= JournalEntryLineDetail
        # Id = id
        try:
            meta_data = MetaDataModel(
                CreateTime=journal_entry.create_date,
                LastUpdatedTime=journal_entry.write_date
            )
            return cls(
                Line=LineResponseModel.create_journal_lines(journal_entry),
                MetaData=meta_data,
                Id=journal_entry.id,
                TxnDate=journal_entry.date
            )
        except Exception as e:
            raise ValueError(f"Error converting: {str(e)}")


class JournalEntryResponseModel(BaseModel):
    time: datetime = Field(..., description="Response timestamp")
    JournalEntry: JournalEntryModel = Field(..., description="Journal entry details")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def create_journal_entry_response(cls, journal_entry: JournalEntryModel) -> "JournalEntryResponseModel":
        return cls(
            JournalEntry=JournalEntryModel.journal_entry_object(journal_entry),
            time=datetime.now(timezone.utc)
        )
    
class JournalEntryQueryResponseModel(PaginationResponseModel):
    JournalEntry: List[JournalEntryModel] = Field(..., description="List of journal entries")

    class Config:
        from_attributes = True

    @field_validator('JournalEntry')
    def validate_journal_entries(cls, v):
        if not v:
            raise ValueError("Journal entry list cannot be empty")
        return v
           
class JournalEntryListResponseModel(BaseModel):
    QueryResponse: JournalEntryQueryResponseModel = Field(..., description="Query response")
    time: datetime = Field(..., description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_journal_entry_response(cls, journal_entries: List[JournalEntryModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "JournalEntryListResponseModel":
        query_response = JournalEntryQueryResponseModel(
            startPosition=start_position,
            maxResults=max_results,
            totalCount=total_count,
            JournalEntry=journal_entries
        )
        return cls(
            QueryResponse=query_response,
            time=datetime.now(timezone.utc)
        )

