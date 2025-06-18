from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from ...schemas.reports import (HeaderModel, ColumnModel, ColumnsModel, ColDataModel, 
                               MetaDataModel, OptionModel, DataRowModel, SummaryModel, 
                               SectionHeaderModel, NestedRowsModel, SectionRowModel)



def create_header(start_date, end_date, report_name, currency: str = "USD") -> HeaderModel:
    """Create the header section of the response."""
    return HeaderModel(
        Time=datetime.now(timezone.utc),
        ReportName=report_name,
        ReportBasis="Accrual",
        StartPeriod=start_date if start_date else None,
        EndPeriod=end_date if end_date else None,
        Currency=currency or "USD",
        Option=[
            OptionModel(Name="AccountingStandard", Value="GAAP"),
            OptionModel(Name="NoReportData", Value="false")
            ],
        SummarizeColumnsBy="Total"       
    )

def create_column_definition() -> ColumnsModel:
    """Create the default ColumnsModel structure."""
    return ColumnsModel(
        Column=[
            ColumnModel(
                ColType="Account",
                ColTitle="",
                MetaData=[MetaDataModel(Name="ColKey", Value="account")]
            ),
            ColumnModel(
                ColType="Money",
                ColTitle="Total",
                MetaData=[MetaDataModel(Name="ColKey", Value="total")]
            )
        ]
    )


def create_data_row(id: Optional[str], value: str, amount: str) -> DataRowModel:
    """Create a data row."""
    return DataRowModel(
        ColData=[
            ColDataModel(id=id, value=value),
            ColDataModel(value=amount)
        ],
        type="Data"
    )

def create_section(title: str, data_rows: List[Union[SectionRowModel, DataRowModel]], group: Optional[str], total_value: str) -> SectionRowModel:
    """Create a section with header, rows, and summary."""
    return SectionRowModel(
        Header=SectionHeaderModel(
            ColData=[
                ColDataModel(value=title),
                ColDataModel(value="")
            ]
        ),
        Rows=NestedRowsModel(Row=data_rows),
        type="Section",
        group=group,
        Summary=SummaryModel(
            ColData=[
                ColDataModel(value=f"TOTAL {title}"),
                ColDataModel(value=total_value)
            ]
        )
    )

def create_summary_section(title: str, amount: str, group: str) -> SectionRowModel:
    """Create a summary section with only header and summary."""
    return SectionRowModel(
        type="Section",
        group=group,
        Summary=SummaryModel(
            ColData=[
                ColDataModel(value=title),
                ColDataModel(value=amount)
            ]
        )
    )