from typing import Any, List
from ...enums import ClassificationType
from ...schemas.reports import (RowsModel, ReportResponseModel)
from ...repositories.account import AccountService
from ...repositories.account_move import AccountMoveLineService
from .common import create_header, create_column_definition, create_data_row, create_section, create_summary_section


def prepare_profit_loss_response(
        request: Any, 
        start_date: Any, 
        end_date: Any,
        company_id: int,
        domain: List[Any],
        currency: str = None
        ):
    account_service = AccountService(request.env)
    account_move_line_service = AccountMoveLineService(request.env)

    # Get accounts grouped by type
    accounts = account_service.search([
        ('company_id', '=', company_id),
        ('internal_group', 'in', [ClassificationType.INCOME, ClassificationType.EXPENSE])
    ])
    domain.append(('account_id', 'in', accounts.ids))

    # Read account balances using read_group
    account_balances = account_move_line_service.read_group(
        domain=domain,
        fields=['account_id', 'balance'],
        groupby=['account_id']
    )

    # Create balance lookup dictionary
    balance_dict = {group['account_id'][0]: group['balance'] for group in account_balances}
    
    # Initialize categories and totals
    account_types = {t: {} for t in ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']}
    totals = {t: 0 for t in account_types}
    
    # Process accounts and their balances
    for account in accounts:
        account_type = account.account_type
        if account_type not in account_types:
            continue
            
        balance = balance_dict.get(account.id, 0.0)
        # Invert sign for income accounts
        if account_type in ['income', 'income_other']:
            balance = -balance
        
        # Create data row for the account
        data_row = create_data_row(
            id=str(account.id),
            value=account.name,
            amount=str(round(balance, 2))
        )

        # Initialize account subtype if not exists
        if account.name not in account_types[account_type]:
            account_types[account_type][account.name] = []
        
        # Add data row and update totals
        account_types[account_type][account.name].append(data_row)
        totals[account_type] += balance

    # Calculate key metrics
    total_income = totals['income'] + totals['income_other']
    gross_profit = totals['income'] - totals['expense_direct_cost']
    net_operating_income = gross_profit - totals['expense']
    net_income = total_income - totals['expense'] - totals['expense_depreciation'] - totals['expense_direct_cost']

    # Create sections
    main_sections = []
    
    # Income section
    if account_types['income']:
        income_accounts = []
        for accounts_list in account_types['income'].values():
            income_accounts.extend(accounts_list)
        
        main_sections.append(create_section(
            "INCOME",
            income_accounts,
            "TotalIncome",
            str(round(totals['income'], 2))
        ))
    
    # Cost of Goods Sold section
    if account_types['expense_direct_cost']:
        direct_cost_accounts = []
        for accounts_list in account_types['expense_direct_cost'].values():
            direct_cost_accounts.extend(accounts_list)
        
        main_sections.append(create_section(
            "COST OF GOODS SOLD",
            direct_cost_accounts,
            "TotalCostofGoodsSold",
            str(round(totals['expense_direct_cost'], 2))
        ))
    
    # Gross Profit summary
    main_sections.append(create_summary_section(
        "Gross Profit",
        str(round(gross_profit, 2)),
        "GrossProfit"
    ))
    
    # Expenses section
    if account_types['expense']:
        expense_accounts = []
        for accounts_list in account_types['expense'].values():
            expense_accounts.extend(accounts_list)
        
        main_sections.append(create_section(
            "EXPENSES",
            expense_accounts,
            "TotalExpenses",
            str(round(totals['expense'], 2))
        ))
    
    # Depreciation/Other Expenses section
    if account_types['expense_depreciation']:
        depreciation_accounts = []
        for accounts_list in account_types['expense_depreciation'].values():
            depreciation_accounts.extend(accounts_list)
        
        main_sections.append(create_section(
            "OTHER EXPENSES",
            depreciation_accounts,
            "TotalOtherExpense",
            str(round(totals['expense_depreciation'], 2))
        ))
    
    # Net Operating Income summary
    main_sections.append(create_summary_section(
        "Net Operating Income",
        str(round(net_operating_income, 2)),
        "NetOperatingIncome"
    ))
    
    # Other Income section
    if account_types['income_other']:
        other_income_accounts = []
        for accounts_list in account_types['income_other'].values():
            other_income_accounts.extend(accounts_list)
        
        main_sections.append(create_section(
            "OTHER INCOME",
            other_income_accounts,
            "TotalOtherIncome",
            str(round(totals['income_other'], 2))
        ))
    
    # Net Other Income summary
    main_sections.append(create_summary_section(
        "Net Other Income",
        str(round(totals['income_other'], 2)),
        "NetOtherIncome"
    ))
    
    # Net Income summary
    main_sections.append(create_summary_section(
        "Net Income",
        str(round(net_income, 2)),
        "NetIncome"
    ))

    # Create response
    return ReportResponseModel(
        Header=create_header(start_date, end_date, "ProfitAndLoss", currency),
        Columns=create_column_definition(),
        Rows=RowsModel(Row=main_sections)
    )

