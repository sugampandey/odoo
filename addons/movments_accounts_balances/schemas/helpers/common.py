from datetime import datetime, timezone, date, timedelta
from typing import Any, List, Optional, Union, Tuple
from ...schemas.reports import (HeaderModel, ColumnModel, ColumnsModel, ColDataModel, 
                               MetaDataModel, OptionModel, DataRowModel, SummaryModel, 
                               SectionHeaderModel, NestedRowsModel, SectionRowModel, 
                               ReportResponseModel, RowsModel)



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


def get_summarized_data(service, domain, start_date, end_date, summarize_column_by):
    """Common function to get columns and balance data based on summarize_column_by."""
    
    if summarize_column_by in ["Month", "Week"]:
        return get_time_data(service, domain, start_date, end_date, summarize_column_by)
    else:
        balances = service.read_group(domain=domain, fields=['account_id', 'balance'], groupby=['account_id'])
        balance_dict = {group['account_id'][0]: group['balance'] for group in balances}
        return create_column_definition(), [balance_dict]


def get_time_data(service, domain, start_date, end_date, period_type):
    """Get time-based data with single query and limits."""
    
    start = start_date if isinstance(start_date, date) else datetime.strptime(start_date, "%Y-%m-%d").date()
    end = end_date if isinstance(end_date, date) else datetime.strptime(end_date, "%Y-%m-%d").date()
    
    if period_type == "Month":
        months = (end.year - start.year) * 12 + end.month - start.month + 1
        if months > 24:
            raise ValueError("Month range cannot exceed 24 months")
        date_group = "date:month"
        
        # Generate expected month periods
        expected_periods = []
        current = start.replace(day=1)
        while current <= end:
            month_key = current.strftime("%b %Y")
            month_end = (current.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            expected_periods.append({
                'key': month_key,
                'start': current.strftime("%Y-%m-%d"),
                'end': min(month_end, end).strftime("%Y-%m-%d")
            })
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            
    elif period_type == "Week":
        weeks = (end - start).days // 7 + 1
        if weeks > 52:
            raise ValueError("Week range cannot exceed 52 weeks")
        date_group = "date:week"
        
        # Generate expected week periods
        expected_periods = []
        current = start - timedelta(days=start.weekday())  # Start of week
        while current <= end:
            week_end = current + timedelta(days=6)
            actual_start = max(current, start)
            actual_end = min(week_end, end)
            
            # Format: "Jan 1-4, 2025"
            if actual_start.month == actual_end.month:
                week_key = f"{actual_start.strftime('%b')} {actual_start.day}-{actual_end.day}, {actual_start.year}"
            else:
                week_key = f"{actual_start.strftime('%b %d')} - {actual_end.strftime('%b %d')}, {actual_start.year}"
            
            expected_periods.append({
                'key': week_key,
                'start': actual_start.strftime("%Y-%m-%d"),
                'end': actual_end.strftime("%Y-%m-%d")
            })
            current += timedelta(days=7)
    
    # Single DB call with date grouping
    results = service.read_group(domain=domain, fields=['account_id', 'balance', 'date'], groupby=['account_id', date_group], lazy=False)
    
    # Map results to expected periods
    account_period_balances = {}
    for result in results:
        account_id = result['account_id'][0]
        result_date = result.get('date') or result.get(date_group)
        balance = result['balance']
        
        result_dt = parse_odoo_date(result_date)
            
        if period_type == "Month":
            period_key = result_dt.strftime("%b %Y")
        else:  # Week
            for period in expected_periods:
                period_start = datetime.strptime(period['start'], "%Y-%m-%d").date()
                period_end = datetime.strptime(period['end'], "%Y-%m-%d").date()
                if period_start <= result_dt <= period_end:
                    period_key = period['key']
                    break
        
        if account_id not in account_period_balances:
            account_period_balances[account_id] = {}
        account_period_balances[account_id][period_key] = balance
    
    # Create columns and balance data
    columns = [ColumnModel(ColType="Account", ColTitle="", MetaData=[MetaDataModel(Name="ColKey", Value="account")])]
    for period in expected_periods:
        columns.append(ColumnModel(
            ColType="Money", 
            ColTitle=period['key'],
            MetaData=[
                MetaDataModel(Name="StartDate", Value=period['start']),
                MetaDataModel(Name="EndDate", Value=period['end']),
                MetaDataModel(Name="ColKey", Value=period['key'])
            ]
        ))
    
    balance_data = []
    for period in expected_periods:
        period_balances = {account_id: period_data.get(period['key'], 0.0) for account_id, period_data in account_period_balances.items()}
        balance_data.append(period_balances)
    
    return ColumnsModel(Column=columns), balance_data


def create_multi_col_data_row(account_id, account_name, balance_data):
    """Create data row with multiple columns."""
    amounts = [str(round(balance_data[i].get(account_id, 0.0), 2)) for i in range(len(balance_data))]
    col_data = [ColDataModel(id=str(account_id), value=account_name)]
    col_data.extend([ColDataModel(value=amt) for amt in amounts])
    return amounts, col_data


def format_period(period, period_type):
    """Format period for display."""
    if period_type == "Month":
        return period.replace(" ", " ")
    elif period_type == "Week":
        return f"Week {period.split('/')[1]} {period.split('/')[0]}"
    return str(period)


def create_section_multi_col(title, data_rows, total_amounts):
    """Create section with multiple columns."""
    header_cols = [ColDataModel(value=title)] + [ColDataModel(value="") for _ in total_amounts]
    summary_cols = [ColDataModel(value=f"Total {title}")] + [ColDataModel(value=amt) for amt in total_amounts]
    
    return SectionRowModel(
        Header=SectionHeaderModel(ColData=header_cols),
        Rows=NestedRowsModel(Row=data_rows),
        type="Section",
        Summary=SummaryModel(ColData=summary_cols)
    )

def parse_odoo_date(result_date):
    """Parse date from Odoo result handling multiple formats."""
    if isinstance(result_date, str):
        # Handle week format "W16 2025" 
        if result_date.startswith('W') and ' ' in result_date:
            try:
                week_part, year_part = result_date.split(' ')
                week_num = int(week_part[1:])  # Remove 'W' prefix
                year = int(year_part)
                # Convert week number to date (first day of that week)
                jan_1 = date(year, 1, 1)
                week_1_start = jan_1 - timedelta(days=jan_1.weekday())
                return week_1_start + timedelta(weeks=week_num - 1)
            except (ValueError, IndexError):
                pass
        
        formats = ["%B %Y", "%b %Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(result_date, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {result_date}")
    elif isinstance(result_date, datetime):
        return result_date.date()
    else:
        return result_date


def prepare_report_with_summarization(service, accounts, domain, start_date, end_date, 
                                    report_name, currency, summarize_column_by, 
                                    account_grouping_func, section_builder_func):
    """Generic function for reports with summarization support."""
    
    # Get columns and balance data
    if summarize_column_by in ["Month", "Week"]:
        columns, balance_data = get_summarized_data(service, domain, start_date, end_date, summarize_column_by)
    else:
        account_balances = service.read_group(domain=domain, fields=['account_id', 'balance'], groupby=['account_id'])
        balance_dict = {group['account_id'][0]: group['balance'] for group in account_balances}
        columns = create_column_definition()
        balance_data = [balance_dict]

    # Group accounts and calculate totals using provided function
    account_groups, totals = account_grouping_func(accounts, balance_data)

    # Create header
    header = create_header(start_date, end_date, report_name, currency)
    header.SummarizeColumnsBy = summarize_column_by

    # Build sections using provided function
    main_sections = section_builder_func(account_groups, totals, balance_data)

    return ReportResponseModel(Header=header, Columns=columns, Rows=RowsModel(Row=main_sections))
