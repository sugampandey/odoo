from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional, List, Union
from .common import MetaDataModel, PaginationResponseModel, RefModel
from ..enums import PostingType, DetailType
from ..repositories.account_move import AccountMoveService

# description = ref
# account_ref ={name-name, value-id}
# class_ref ={name-name, value-id}
# entity = {type=Vendor/Customer , Entityref = {name-name, value-id}}
# Amount = amount
# postingtype = Debit/Credit -- debit/credit columns
# Detailtype= JournalEntryLineDetail
# Id = id


class EntityModel(BaseModel):
    Type: Optional[str] = Field(None, description="Entity type")
    EntityRef: Optional[RefModel] = Field(None, description="Entity reference")

    class Config:
        from_attributes = True
    
    # @field_validator('Type')
    # def validate_non_empty_string(cls, v, info):
    #     if not v.strip():
    #         raise ValueError(f"{info.field_name} cannot be empty or contain only whitespace")
    #     return v
    
class JournalEntryLineDetailModel(BaseModel):
    PostingType: str = Field(..., description="Type of posting (Debit/Credit)")
    AccountRef: RefModel = Field(..., description="Account reference")
    TaxApplicableOn: Optional[str] = Field(None, description="Tax applicable on")
    ClassRef: Optional[RefModel] = Field(None, description="Class reference")
    TaxCodeRef: Optional[RefModel] = Field(None, description="Tax code reference")
    Entity: Optional[EntityModel] = Field(None, description="Entity details")

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
    def _create_entity(move_line) -> Optional[EntityModel]:
        if not move_line.partner_id:
            return None
        entity_ref = RefModel(
            name=move_line.partner_id.name,
            value=str(move_line.partner_id.id),
        )
        return EntityModel(
            Type=move_line.partner_id.category_id.name if move_line.partner_id else None,
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
    TxnDate: Optional[datetime] = Field(None, description="Transaction date")

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
            'date': self.TxnDate if self.TxnDate else datetime.now().date(),
            'company_id': company_id,
            'invoice_line_ids': [(0,0, line.create_line_vals(company_id)) for line in self.Line]
        }
        

class JournalEntryLineDetailUpdateModel(BaseModel):
    PostingType: Optional[str] = Field(None, description="Type of posting (Debit/Credit)")
    AccountRef: Optional[RefModel] = Field(None, description="Account reference")
    TaxApplicableOn: Optional[str] = Field(None, description="Tax applicable on")
    ClassRef: Optional[RefModel] = Field(None, description="Class reference")
    TaxCodeRef: Optional[RefModel] = Field(None, description="Tax code reference")
    Entity: Optional[EntityModel] = Field(None, description="Entity details")

    class Config:
        from_attributes = True
    
    @field_validator('PostingType')
    def validate_posting_type(cls, v):
        if v and v not in [pt.value for pt in PostingType]:
            raise ValueError(f"Invalid posting type: {v}")
        return v

class LineUpdateRequestModel(BaseModel):
    JournalEntryLineDetail: Optional[JournalEntryLineDetailUpdateModel] = Field(None)
    DetailType: Optional[str] = Field(None, description="Type of detail")
    Amount: Optional[float] = Field(None, description="Transaction amount")
    Description: Optional[str] = Field(None, description="Line item description")
    Id: int = Field(..., description="Line item ID to update")

    class Config:
        from_attributes = True

class JournalEntryUpdateRequestModel(BaseModel):
    Line: Optional[List[LineUpdateRequestModel]] = Field(None, description="Journal entry lines to update")
    CurrencyRef: Optional[RefModel] = Field(None, description="Currency reference")
    TxnDate: Optional[datetime] = Field(None, description="Transaction date")

    class Config:
        from_attributes = True

    def merge_with_original(self, original_entry) -> 'JournalEntryRequestModel':
        """Merge update data with original entry data"""
        # Start with original data
        merged_lines = []
        
        for original_line in original_entry.line_ids:
            # Find if this line has updates
            update_line = None
            if self.Line:
                update_line = next((line for line in self.Line if line.Id == original_line.id), None)
            
            # Create merged line data
            if update_line:
                # Merge updated fields with original
                merged_detail = JournalEntryLineDetailModel(
                    PostingType=update_line.JournalEntryLineDetail.PostingType if update_line.JournalEntryLineDetail and update_line.JournalEntryLineDetail.PostingType else (PostingType.DEBIT if original_line.debit != 0 else PostingType.CREDIT),
                    AccountRef=update_line.JournalEntryLineDetail.AccountRef if update_line.JournalEntryLineDetail and update_line.JournalEntryLineDetail.AccountRef else RefModel(name=original_line.account_id.name, value=str(original_line.account_id.id)),
                    ClassRef=update_line.JournalEntryLineDetail.ClassRef if update_line.JournalEntryLineDetail and update_line.JournalEntryLineDetail.ClassRef else (RefModel(name=original_line.analytic_line_ids.account_id.name, value=str(original_line.analytic_line_ids.account_id.id)) if original_line.analytic_line_ids else None),
                    Entity=update_line.JournalEntryLineDetail.Entity if update_line.JournalEntryLineDetail and update_line.JournalEntryLineDetail.Entity else (EntityModel(Type=original_line.partner_id.category_id.name if original_line.partner_id and original_line.partner_id.category_id else None, EntityRef=RefModel(name=original_line.partner_id.name, value=str(original_line.partner_id.id))) if original_line.partner_id else None)
                )
                
                merged_line = LineRequestModel(
                    JournalEntryLineDetail=merged_detail,
                    DetailType=update_line.DetailType if update_line.DetailType else DetailType.JOURNAL_ENTRY,
                    Amount=update_line.Amount if update_line.Amount is not None else (original_line.debit if original_line.debit != 0 else original_line.credit),
                    Description=update_line.Description if update_line.Description is not None else (original_line.ref if original_line.ref else None),
                    Id=original_line.id
                )
            else:
                # Keep original line data
                merged_detail = JournalEntryLineDetailModel.create_from_move_line(original_line)
                merged_line = LineRequestModel(
                    JournalEntryLineDetail=merged_detail,
                    DetailType=DetailType.JOURNAL_ENTRY,
                    Amount=original_line.debit if original_line.debit != 0 else original_line.credit,
                    Description=original_line.ref if original_line.ref else None,
                    Id=original_line.id
                )
            
            merged_lines.append(merged_line)
        
        # Create merged request model
        return JournalEntryRequestModel(
            Line=merged_lines,
            CurrencyRef=self.CurrencyRef,
            TxnDate=self.TxnDate if self.TxnDate else original_entry.date
        )


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


class ReversalInfoModel(BaseModel):
    Type: str = Field(..., description="Type: 'reversed_by' or 'reversal_of'")
    Id: Optional[int] = Field(None, description="Related entry ID")
    Name: Optional[str] = Field(None, description="Related entry name")
    
    class Config:
        from_attributes = True


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
    ReversalInfo: Optional[ReversalInfoModel] = Field(None, description="Reversal relationship info")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def journal_entry_object(cls, request, journal_entry):
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
            # Determine reversal relationship
            reversal_info = None
            
            # Check if this entry was reversed by another entry
            account_move_service = AccountMoveService(request.env)
            reversed_by_entry = account_move_service.search([
                ('reversed_entry_id', '=', journal_entry.id)
            ], limit=1)
            
            if reversed_by_entry:
                # This is an original entry that was reversed
                reversal_info = ReversalInfoModel(
                    Type="reversed_by",
                    Id=reversed_by_entry.id,
                    Name=reversed_by_entry.name
                )
            elif journal_entry.reversed_entry_id:
                # This is a reversal entry
                reversal_info = ReversalInfoModel(
                    Type="reversal_of", 
                    Id=journal_entry.reversed_entry_id.id,
                    Name=journal_entry.reversed_entry_id.name
                )
            return cls(
                Line=LineResponseModel.create_journal_lines(journal_entry),
                MetaData=meta_data,
                Id=journal_entry.id,
                TxnDate=journal_entry.date,
                ReversalInfo=reversal_info
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
    def create_journal_entry_response(cls, request, journal_entry: JournalEntryModel) -> "JournalEntryResponseModel":
        return cls(
            JournalEntry=JournalEntryModel.journal_entry_object(request, journal_entry),
            time=datetime.now(timezone.utc)
        )
    
class JournalEntryQueryResponseModel(PaginationResponseModel):
    JournalEntry: List[JournalEntryModel] = Field([], description="List of journal entries")

    class Config:
        from_attributes = True

           
class JournalEntryListResponseModel(BaseModel):
    QueryResponse: Union[dict, JournalEntryQueryResponseModel] = Field({}, description="Query response")
    time: datetime = Field(..., description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.astimezone().isoformat() if dt else None
        }
        from_attributes = True

    @classmethod
    def list_journal_entry_response(cls, journal_entries: List[JournalEntryModel], total_count : int, start_position: int = 0, max_results: int = 20) -> "JournalEntryListResponseModel":
        query_response = {}
        if journal_entries and len(journal_entries) > 0:
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

