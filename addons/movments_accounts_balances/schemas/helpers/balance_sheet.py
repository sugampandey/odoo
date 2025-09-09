from typing import Any, List
from datetime import datetime, timedelta
from ...enums import ClassificationType
from ...schemas.reports import DataRowModel
from ...repositories.account import AccountService
from ...repositories.account_move import AccountMoveLineService
from .common import create_multi_col_data_row, create_multi_col_data_row_bs, create_section_multi_col, prepare_report_with_summarization, get_summarized_data





def group_balance_sheet_accounts(accounts, balance_data):
    """Group accounts by internal_group and account_type for balance sheet."""
    account_types = {ClassificationType.ASSET: {}, ClassificationType.LIABILITY: {}, ClassificationType.EQUITY: {}}
    totals = {
        ClassificationType.ASSET: {'total': [0] * len(balance_data), 'types': {}},
        ClassificationType.LIABILITY: {'total': [0] * len(balance_data), 'types': {}},
        ClassificationType.EQUITY: {'total': [0] * len(balance_data), 'types': {}}
    }

    for account in accounts:
        # Use balance sheet specific function that handles empty strings
        amounts, col_data = create_multi_col_data_row_bs(account.id, account.name, balance_data)
        
        if account.account_type not in totals[account.internal_group]['types']:
            totals[account.internal_group]['types'][account.account_type] = [0] * len(balance_data)
        
        for i, amount in enumerate(amounts):
            if amount != "":  # Only add non-empty values to totals
                val = float(amount)
                totals[account.internal_group]['types'][account.account_type][i] += val
                totals[account.internal_group]['total'][i] += val

        data_row = DataRowModel(ColData=col_data, type="Data")
        
        if account.account_type not in account_types[account.internal_group]:
            account_types[account.internal_group][account.account_type] = []
        account_types[account.internal_group][account.account_type].append(data_row)

    return account_types, totals

def build_balance_sheet_sections(account_groups, totals, balance_data):
    """Build balance sheet sections."""
    main_sections = []
    for group_name, group_data in [
        ("ASSETS", (ClassificationType.ASSET, account_groups[ClassificationType.ASSET])),
        ("LIABILITIES", (ClassificationType.LIABILITY, account_groups[ClassificationType.LIABILITY])),
        ("EQUITY", (ClassificationType.EQUITY, account_groups[ClassificationType.EQUITY]))
    ]:
        internal_group, type_data = group_data
        type_sections = []

        for acc_type, accounts_list in type_data.items():
            if accounts_list:
                # Handle empty strings in totals
                total_amounts = []
                for amt in totals[internal_group]['types'][acc_type]:
                    if amt == 0.0:
                        total_amounts.append("")
                    else:
                        total_amounts.append(str(round(amt, 2)))
                type_section = create_section_multi_col(acc_type.upper(), accounts_list, total_amounts)
                type_sections.append(type_section)

        # Handle empty strings in main totals
        total_amounts = []
        for amt in totals[internal_group]['total']:
            if amt == 0.0:
                total_amounts.append("")
            else:
                total_amounts.append(str(round(amt, 2)))
        main_section = create_section_multi_col(group_name, type_sections, total_amounts)
        main_sections.append(main_section)

    return main_sections

def prepare_account_balance_response(
        request: Any, 
        start_date: Any, 
        end_date: Any,
        company_id: int,
        domain: List[Any],
        currency: str = None,
        summarize_column_by: str = "Total"
        ):    
    account_service = AccountService(request.env)
    account_move_line_service = AccountMoveLineService(request.env)

    accounts = account_service.search([
        ('company_id', '=', company_id),
        ('internal_group', 'in', [ClassificationType.ASSET, ClassificationType.LIABILITY, ClassificationType.EQUITY])
    ])
    domain.append(('account_id', 'in', accounts.ids))

    # Get Balance Sheet specific data (running balances, no total column)
    columns, balance_data = get_summarized_data(account_move_line_service, domain, start_date, end_date, summarize_column_by, "BS")

    return prepare_report_with_summarization(
        account_move_line_service, accounts, domain, start_date, end_date,
        "BalanceSheet", currency, summarize_column_by,
        group_balance_sheet_accounts, build_balance_sheet_sections,
        columns, balance_data  # Pass pre-fetched data
    )