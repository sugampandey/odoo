from typing import Any, List
from ...enums import ClassificationType
from ...schemas.reports import (RowsModel, ReportResponseModel, SummaryModel, ColDataModel, DataRowModel, SectionRowModel)
from ...repositories.account import AccountService
from ...repositories.account_move import AccountMoveLineService
from .common import (create_header, create_column_definition, get_summarized_data, 
                    create_multi_col_data_row, create_section_multi_col, create_data_row, 
                    create_section, create_summary_section)
from ...logger.logger import logger


def prepare_profit_loss_response(
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
        ('internal_group', 'in', [ClassificationType.INCOME, ClassificationType.EXPENSE])
    ])
    domain.append(('account_id', 'in', accounts.ids))
    logger.info(('account_id', 'in', accounts.ids))

    # Get P&L specific data (period totals, with total column)
    columns, balance_data = get_summarized_data(account_move_line_service, domain, start_date, end_date, summarize_column_by, "PL")
    
    # Group accounts by type
    account_types = {t: {} for t in ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']}
    totals = {t: [0] * len(balance_data) for t in account_types}
    
    # Process accounts
    for account in accounts:
        account_type = account.account_type
        if account_type not in account_types:
            continue
            
        if summarize_column_by == "Total":
            balance = balance_data[0].get(account.id, 0.0)
            if account_type in ['income', 'income_other']:
                balance = -balance
            
            data_row = create_data_row(str(account.id), account.name, str(round(balance, 2)))
            if account.name not in account_types[account_type]:
                account_types[account_type][account.name] = []
            account_types[account_type][account.name].append(data_row)
            totals[account_type][0] += balance
        else:
            amounts, col_data = create_multi_col_data_row(account.id, account.name, balance_data)
            
            # Invert signs for income accounts
            if account_type in ['income', 'income_other']:
                amounts = [str(-float(amt)) for amt in amounts]
                col_data = [col_data[0]] + [ColDataModel(value=amt) for amt in amounts]
            
            data_row = DataRowModel(ColData=col_data, type="Data")
            
            if account.name not in account_types[account_type]:
                account_types[account_type][account.name] = []
            account_types[account_type][account.name].append(data_row)
            
            for i, amt in enumerate(amounts):
                totals[account_type][i] += float(amt)

    logger.info(f"account_types: {account_types}")
    logger.info(f"totals: {totals}")
    # Calculate metrics
    if summarize_column_by == "Total":
        total_income = totals['income'][0] + totals['income_other'][0]
        gross_profit = totals['income'][0] - totals['expense_direct_cost'][0]
        net_operating_income = gross_profit - totals['expense'][0]
        net_income = total_income - totals['expense'][0] - totals['expense_depreciation'][0] - totals['expense_direct_cost'][0]
    else:
        total_income = [totals['income'][i] + totals['income_other'][i] for i in range(len(balance_data))]
        gross_profit = [totals['income'][i] - totals['expense_direct_cost'][i] for i in range(len(balance_data))]
        net_operating_income = [gross_profit[i] - totals['expense'][i] for i in range(len(balance_data))]
        net_income = [total_income[i] - totals['expense'][i] - totals['expense_depreciation'][i] - totals['expense_direct_cost'][i] for i in range(len(balance_data))]

    # Create sections
    main_sections = []
    
    if summarize_column_by == "Total":
        # Single column sections (existing logic)
        if account_types['income']:
            income_accounts = []
            for accounts_list in account_types['income'].values():
                income_accounts.extend(accounts_list)
            main_sections.append(create_section("Income", income_accounts, "TotalIncome", str(round(totals['income'][0], 2))))
        
        if account_types['expense_direct_cost']:
            direct_cost_accounts = []
            for accounts_list in account_types['expense_direct_cost'].values():
                direct_cost_accounts.extend(accounts_list)
            main_sections.append(create_section("Cost of Goods Sold", direct_cost_accounts, "TotalCostofGoodsSold", str(round(totals['expense_direct_cost'][0], 2))))
        
        main_sections.append(create_summary_section("Gross Profit", str(round(gross_profit, 2)), "GrossProfit"))
        
        if account_types['expense']:
            expense_accounts = []
            for accounts_list in account_types['expense'].values():
                expense_accounts.extend(accounts_list)
            main_sections.append(create_section("Expenses", expense_accounts, "TotalExpenses", str(round(totals['expense'][0], 2))))
        
        if account_types['expense_depreciation']:
            depreciation_accounts = []
            for accounts_list in account_types['expense_depreciation'].values():
                depreciation_accounts.extend(accounts_list)
            main_sections.append(create_section("Other Expenses", depreciation_accounts, "TotalOtherExpense", str(round(totals['expense_depreciation'][0], 2))))
        
        main_sections.append(create_summary_section("Net Operating Income", str(round(net_operating_income, 2)), "NetOperatingIncome"))
        
        if account_types['income_other']:
            other_income_accounts = []
            for accounts_list in account_types['income_other'].values():
                other_income_accounts.extend(accounts_list)
            main_sections.append(create_section("Other Income", other_income_accounts, "TotalOtherIncome", str(round(totals['income_other'][0], 2))))
        
        main_sections.append(create_summary_section("Net Other Income", str(round(totals['income_other'][0], 2)), "NetOtherIncome"))
        main_sections.append(create_summary_section("Net Income", str(round(net_income, 2)), "NetIncome"))
    else:
        # Multi-column sections with all calculated metrics        
        if account_types['income']:
            income_accounts = []
            for accounts_list in account_types['income'].values():
                income_accounts.extend(accounts_list)
            total_amounts = [str(round(totals['income'][i], 2)) for i in range(len(balance_data))]
            main_sections.append(create_section_multi_col("Income", income_accounts, total_amounts, "TotalIncome"))
        
        if account_types['expense_direct_cost']:
            direct_cost_accounts = []
            for accounts_list in account_types['expense_direct_cost'].values():
                direct_cost_accounts.extend(accounts_list)
            total_amounts = [str(round(totals['expense_direct_cost'][i], 2)) for i in range(len(balance_data))]
            main_sections.append(create_section_multi_col("Cost of Goods Sold", direct_cost_accounts, total_amounts, "TotalCostofGoodsSold"))

        # Gross Profit summary
        gross_amounts = [str(round(gross_profit[i], 2)) for i in range(len(balance_data))]
        summary_cols = [ColDataModel(value="Gross Profit")] + [ColDataModel(value=amt) for amt in gross_amounts]
        main_sections.append(SectionRowModel(type="Section", group="GrossProfit", Summary=SummaryModel(ColData=summary_cols)))
        
        if account_types['expense']:
            expense_accounts = []
            for accounts_list in account_types['expense'].values():
                expense_accounts.extend(accounts_list)
            total_amounts = [str(round(totals['expense'][i], 2)) for i in range(len(balance_data))]
            main_sections.append(create_section_multi_col("Expenses", expense_accounts, total_amounts, "TotalExpenses"))
        
        if account_types['expense_depreciation']:
            depreciation_accounts = []
            for accounts_list in account_types['expense_depreciation'].values():
                depreciation_accounts.extend(accounts_list)
            total_amounts = [str(round(totals['expense_depreciation'][i], 2)) for i in range(len(balance_data))]
            main_sections.append(create_section_multi_col("Other Expenses", depreciation_accounts, total_amounts, "TotalOtherExpense"))
        
        # Net Operating Income summary
        net_op_amounts = [str(round(net_operating_income[i], 2)) for i in range(len(balance_data))]
        summary_cols = [ColDataModel(value="Net Operating Income")] + [ColDataModel(value=amt) for amt in net_op_amounts]
        main_sections.append(SectionRowModel(type="Section", group="NetOperatingIncome", Summary=SummaryModel(ColData=summary_cols)))
        
        if account_types['income_other']:
            other_income_accounts = []
            for accounts_list in account_types['income_other'].values():
                other_income_accounts.extend(accounts_list)
            total_amounts = [str(round(totals['income_other'][i], 2)) for i in range(len(balance_data))]
            main_sections.append(create_section_multi_col("Other Income", other_income_accounts, total_amounts, "TotalOtherIncome"))

        # Net Other Income summary
        net_other_amounts = [str(round(totals['income_other'][i], 2)) for i in range(len(balance_data))]
        summary_cols = [ColDataModel(value="Net Other Income")] + [ColDataModel(value=amt) for amt in net_other_amounts]
        main_sections.append(SectionRowModel(type="Section", group="NetOtherIncome", Summary=SummaryModel(ColData=summary_cols)))
        
        # Net Income summary
        net_income_amounts = [str(round(net_income[i], 2)) for i in range(len(balance_data))]
        summary_cols = [ColDataModel(value="Net Income")] + [ColDataModel(value=amt) for amt in net_income_amounts]
        main_sections.append(SectionRowModel(type="Section", group="NetIncome", Summary=SummaryModel(ColData=summary_cols)))

    # Create header with summarization
    header = create_header(start_date, end_date, "ProfitAndLoss", currency)
    header.SummarizeColumnsBy = summarize_column_by

    return ReportResponseModel(Header=header, Columns=columns, Rows=RowsModel(Row=main_sections))
