from typing import Any, List
from datetime import datetime, timedelta
from ...enums import ClassificationType
from ...schemas.reports import (RowsModel, ReportResponseModel, ColumnsModel, ColumnModel, 
                               ColDataModel, MetaDataModel, DataRowModel, SectionRowModel,
                               SectionHeaderModel, NestedRowsModel, SummaryModel)
from ...repositories.account import AccountService
from ...repositories.account_move import AccountMoveLineService
from .common import create_header, create_column_definition, create_data_row, create_section, get_summarized_data, create_multi_col_data_row, format_period, create_section_multi_col, prepare_report_with_summarization


def prepare_account_balance_response(
        request: Any, 
        start_date: Any, 
        end_date: Any,
        company_id: int,
        domain: List[Any],
        currency: str = None,
        summarize_column_by: str = "Total"
        ):
    ASSET = ClassificationType.ASSET
    LIABILITY = ClassificationType.LIABILITY
    EQUITY = ClassificationType.EQUITY

    account_service = AccountService(request.env)
    account_move_line_service = AccountMoveLineService(request.env)

    # Get accounts grouped by type
    accounts = account_service.search([
        ('company_id', '=', company_id),
        ('internal_group', 'in', [ASSET, LIABILITY, EQUITY])
    ])
    domain.append(('account_id', 'in', accounts.ids))

    # Get columns and balance data
    if summarize_column_by in ["Month", "Week"]:
        columns, balance_data = get_summarized_data(account_move_line_service, domain, start_date, end_date, summarize_column_by)
    else:
        account_balances = account_move_line_service.read_group(domain=domain, fields=['account_id', 'balance'], groupby=['account_id'])
        balance_dict = {group['account_id'][0]: group['balance'] for group in account_balances}
        columns = create_column_definition()
        balance_data = [balance_dict]

    # Initialize categories and totals
    account_types = {ASSET: {}, LIABILITY: {}, EQUITY: {}}
    totals = {
        ASSET: {'total': [0] * len(balance_data), 'types': {}},
        LIABILITY: {'total': [0] * len(balance_data), 'types': {}},
        EQUITY: {'total': [0] * len(balance_data), 'types': {}}
    }

    # Process accounts and their balances
    for account in accounts:
        account_type = account.account_type  
        internal_group = account.internal_group 
        amounts, col_data = create_multi_col_data_row(account.id, account.name, balance_data)
        
        # amounts = [str(round(balance_data[i].get(account.id, 0.0), 2)) for i in range(len(balance_data))]
        
        # Update totals
        if account_type not in totals[internal_group]['types']:
            totals[internal_group]['types'][account_type] = [0] * len(balance_data)
        
        for i, amount in enumerate(amounts):
            val = float(amount)
            totals[internal_group]['types'][account_type][i] += val
            totals[internal_group]['total'][i] += val

        # Create data row
        # col_data = [ColDataModel(id=str(account.id), value=account.name)]
        # col_data.extend([ColDataModel(value=amt) for amt in amounts])
        
        data_row = DataRowModel(ColData=col_data, type="Data")

        if account_type not in account_types[internal_group]:
            account_types[internal_group][account_type] = []
        account_types[internal_group][account_type].append(data_row)

    # Create header
    header = create_header(start_date, end_date, "BalanceSheet", currency)
    header.SummarizeColumnsBy = summarize_column_by

    response = ReportResponseModel(Header=header, Columns=columns, Rows=RowsModel(Row=[]))

    # Create main sections
    main_sections = []
    for group_name, group_data in [
        ("ASSETS", (ASSET, account_types[ASSET])),
        ("LIABILITIES", (LIABILITY, account_types[LIABILITY])),
        ("EQUITY", (EQUITY, account_types[EQUITY]))
    ]:
        internal_group, type_data = group_data
        type_sections = []

        for acc_type, accounts_list in type_data.items():
            if accounts_list:
                total_amounts = [str(round(amt, 2)) for amt in totals[internal_group]['types'][acc_type]]
                type_section = create_section_multi_col(acc_type.upper(), accounts_list, total_amounts)
                type_sections.append(type_section)

        total_amounts = [str(round(amt, 2)) for amt in totals[internal_group]['total']]
        main_section = create_section_multi_col(group_name, type_sections, total_amounts)
        main_sections.append(main_section)

    response.Rows.Row = main_sections
    return response


