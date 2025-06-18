from typing import Any, List
from ...enums import ClassificationType
from ...schemas.reports import (RowsModel, ReportResponseModel)
from ...repositories.account import AccountService
from ...repositories.account_move import AccountMoveLineService
from .common import create_header, create_column_definition, create_data_row, create_section


def prepare_account_balance_response(
        request: Any, 
        start_date: Any, 
        end_date: Any,
        company_id: int,
        domain: List[Any],
        currency: str = None
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

    # Read account balances using read_group
    account_balances = account_move_line_service.read_group(
        domain=domain,
        fields=['account_id', 'balance'],
        groupby=['account_id']
    )

    # Create balance lookup dictionary
    balance_dict = {
        group['account_id'][0]: group['balance'] 
        for group in account_balances
    }

    # Initialize categories and totals
    account_types = {
        ASSET: {},
        LIABILITY: {},
        EQUITY: {}
    }
    totals = {
        ASSET: {'total': 0, 'types': {}},
        LIABILITY: {'total': 0, 'types': {}},
        EQUITY: {'total': 0, 'types': {}}
    }

    # Process accounts and their balances
    for account in accounts:
        balance = balance_dict.get(account.id, 0.0)
        account_type = account.account_type  
        internal_group = account.internal_group 
        
        # Create data row for the account
        data_row = create_data_row(
            id=str(account.id),
            value=account.name,
            amount=str(round(balance, 2))
        )

        # Initialize account type if not exists
        if account_type not in account_types[internal_group]:
            account_types[internal_group][account_type] = []
        
        # Initialize total for account type if not exists
        if account_type not in totals[internal_group]['types']:
            totals[internal_group]['types'][account_type] = 0

        # Add data row to appropriate category
        account_types[internal_group][account_type].append(data_row)
        
        # Update totals
        totals[internal_group]['types'][account_type] += balance
        totals[internal_group]['total'] += balance

    response = ReportResponseModel(
        Header=create_header(start_date, end_date, "BalanceSheet", currency),
        Columns=create_column_definition(),
        Rows=RowsModel(Row=[])
    )

    # Create main sections (Assets, Liabilities, Equity)
    main_sections = []
    for group_name, group_data in [
        ("ASSETS", (ASSET, account_types[ASSET])),
        ("LIABILITIES", (LIABILITY, account_types[LIABILITY])),
        ("EQUITY", (EQUITY, account_types[EQUITY]))
    ]:
        internal_group, type_data = group_data
        type_sections = []

        # Create sections for each account type
        for acc_type, accounts_list in type_data.items():
            if accounts_list:  # Only create section if there are accounts
                type_section = create_section(
                    acc_type.upper(),
                    accounts_list,
                    f"Total{acc_type.capitalize()}",
                    str(round(totals[internal_group]['types'][acc_type], 2))
                )
                type_sections.append(type_section)

        # Create main section with account type subsections
        main_section = create_section(
            group_name,
            type_sections,
            f"Total{group_name}",
            str(round(totals[internal_group]['total'], 2))
        )
        main_sections.append(main_section)

    # Update rows with all sections
    response.Rows.Row = main_sections

    return response
