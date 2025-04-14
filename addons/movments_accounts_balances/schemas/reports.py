from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any

class OptionModel(BaseModel):
    Name: Optional[str] = None
    Value: Optional[str] = None


class HeaderModel(BaseModel):
    Time: str
    ReportName: str 
    ReportBasis: str 
    StartPeriod: Optional[str] = None
    EndPeriod: Optional[str] = None
    Currency: str 
    Option: Optional[List[OptionModel]] = None
    DateMacro: Optional[str] = None
    SummarizeColumnsBy: Optional[str] = None


class MetaDataModel(BaseModel):
    Name: str
    Value: str

class ColumnModel(BaseModel):
    ColTitle: str
    ColType: str 
    MetaData: List[MetaDataModel] = Field(default_factory=list)

class ColumnsModel(BaseModel):
    Column: List[ColumnModel]

class ColDataModel(BaseModel):
    value: Any
    id: Optional[int] = None

class DataRowModel(BaseModel):
    ColData: List[ColDataModel]
    type: str 

class SummaryModel(BaseModel):
    ColData: List[ColDataModel]

class SectionHeaderModel(BaseModel):
    ColData: List[ColDataModel]

class NestedRowsModel(BaseModel):
    Row: List[Union['SectionRowModel', DataRowModel]]

class SectionRowModel(BaseModel):
    Header: SectionHeaderModel
    Rows: NestedRowsModel
    type: str 
    Summary: SummaryModel
    group: Optional[str] = None

class RowsModel(BaseModel):
    Row: List[SectionRowModel]

class ReportResponseModel(BaseModel):
    Header: HeaderModel
    Columns: ColumnsModel
    Rows: RowsModel

# Handle forward references
SectionRowModel.model_rebuild()


