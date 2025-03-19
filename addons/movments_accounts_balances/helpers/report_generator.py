import datetime
from typing import Any, Dict, List, Iterator
from decimal import Decimal

from ..mapping.reports import MOVE_TYPE_MAPPING
from ..constants import CONSTANTS
from contextlib import contextmanager

@contextmanager
def log_queries():
    from odoo.sql_db import Cursor  # Import Cursor directly
    query_count = 0
    original_execute = Cursor.execute
    
    def counting_execute(self, query, params=None, log_exceptions=None):
        nonlocal query_count
        query_count += 1
        return original_execute(self, query, params, log_exceptions)
    
    Cursor.execute = counting_execute
    try:
        yield
    finally:
        Cursor.execute = original_execute
        print("----------------------------------------------------------------")
        print(f"Executed {query_count} queries")
        print("----------------------------------------------------------------")


GL_REPORT_COLUMNS = [
    "tx_date",
    "txn_type",
    "doc_num",
    "name",
    "memo",
    "split_acc",
    "subt_nat_amount",
    "rbal_nat_amount",
    "account_name",
    "vend_name",
    "klass_name",
]


# def get_split_acc(request: Any, entry: Any, move_lines: Iterator[Any]):
#     """
#     Get the split account information for a given entry and its move lines.
    
#     Args:
#         entry: The account entry record
#         move_lines: The related account move lines
        
#     Returns:
#         tuple: (account_name, account_id) of the split account
#     """
#     def filter_move_lines(lines, field):
#         return [line for line in lines if getattr(line, field) != 0]
    
#     # move_lines = request.env['account.move.line'].sudo().search([('move_id', '=', entry.move_id.id)])
#     entity_lines = [line for line in move_lines if line.move_id.id == entry.move_id.id]
#     debit_entity_lines = filter_move_lines(entity_lines, 'debit')
#     credit_entity_lines = filter_move_lines(entity_lines, 'credit')
#     DEFAULT_SPLIT = ("-Split-", "")

#     if entry.debit != 0 and len(credit_entity_lines) == 1:
#         return (credit_entity_lines[0].account_id.name, credit_entity_lines[0].account_id.id)
#     elif entry.credit != 0 and len(debit_entity_lines) == 1:
#         return (debit_entity_lines[0].account_id.name, debit_entity_lines[0].account_id.id)
        
#     return DEFAULT_SPLIT

def get_opposite_accounts(request, move_lines):
    """
    Get opposite accounts for move lines using SQL self-join with SQL injection prevention.
    Returns a dictionary mapping move_line_id to its opposite account(s).
    """
    if not move_lines:
        return {}

    # Safely create tuple of move line IDs
    move_line_ids = tuple(int(line.id) for line in move_lines)  # Convert to int for safety
    if not move_line_ids:
        return {}

    # Use a parameterized query with proper parameter binding
    query = """
        WITH move_counts AS (
            SELECT move_id, COUNT(*) as line_count
            FROM account_move_line
            WHERE move_id IN (
                SELECT DISTINCT move_id 
                FROM account_move_line 
                WHERE id = ANY(%s)
            )
            GROUP BY move_id
        )
        SELECT 
            aml1.id as line_id,
            CASE 
                WHEN mc.line_count > 2 THEN '-Split-'
                ELSE aml2.account_id::text
            END as opposite_account_id,
            CASE 
                WHEN mc.line_count > 2 THEN '-Split-'
                ELSE acc.name
            END as opposite_account_name,
            mc.line_count
        FROM account_move_line aml1
        JOIN move_counts mc ON aml1.move_id = mc.move_id
        LEFT JOIN account_move_line aml2 ON 
            aml1.move_id = aml2.move_id 
            AND aml1.id != aml2.id
            AND (
                (aml1.debit > 0 AND aml2.credit > 0) OR 
                (aml1.credit > 0 AND aml2.debit > 0)
            )
        LEFT JOIN account_account acc ON aml2.account_id = acc.id
        WHERE aml1.id = ANY(%s)
    """
    
    try:
        # Use parameter binding with a list
        params = [list(move_line_ids), list(move_line_ids)]
        request.cr.execute(query, params)
        results = request.cr.dictfetchall()
        
    except Exception as e:
        # Log the error and return empty dict
        print(f"Error executing opposite accounts query: {str(e)}")
        return {}
    
    # Convert results to dictionary with safe type conversion
    opposite_accounts = {}
    for row in results:
        try:
            line_id = int(row['line_id'])
            line_count = int(row['line_count'])
            
            if line_count > 2:
                opposite_accounts[line_id] = ('-Split-', '')
            else:
                # Safely handle potentially NULL values
                account_name = str(row['opposite_account_name'] or '-Split-')
                account_id = str(row['opposite_account_id'] or '')
                opposite_accounts[line_id] = (account_name, account_id)
                
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error processing row {row}: {str(e)}")
            continue
    
    return opposite_accounts


def get_split_acc(request: Any, entry: Any, opposite_accounts: Dict):
    """
    Get the split account information for a given entry using pre-fetched opposite accounts.
    
    Args:
        request: The Odoo request object
        entry: The account entry record
        opposite_accounts: Dictionary mapping move_line_id to opposite account info
        
    Returns:
        tuple: (account_name, account_id) of the split account
    """
    return opposite_accounts.get(entry.id, ("-Split-", ""))

def get_klass_name(entry):
    with log_queries():
        analytic_class = entry.analytic_line_ids.account_id
        if not analytic_class:
            return "", ""
        return analytic_class.name, analytic_class.id


def create_header(start_date, end_date, currency: str = "USD") -> Dict[str, Any]:
    """Create the header section of the response."""
    return {
        "Time": datetime.datetime.now().strftime(CONSTANTS['DATE_FORMAT']),
        "ReportName": "GeneralLedger",
        "ReportBasis": "Accrual",
        "StartPeriod": start_date.strftime(CONSTANTS['DATE_FORMAT']),
        "EndPeriod": end_date.strftime(CONSTANTS['DATE_FORMAT']),
        "Currency": currency or "USD",
        "Option": [{"Name": "NoReportData", "Value": "false"}]
    }

def create_column_definition(columns_list: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Create the column definitions section."""
    return {
        "Column": [
            {
                "ColTitle": col,
                "ColType": "String",
                "MetaData": [{"Name": "ColKey", "Value": col}]
            }
            for col in columns_list if col in GL_REPORT_COLUMNS
        ]
    }

def get_column_value(entry: Any, col: str, split_acc: str, split_id: str, 
                    klass_name: str, klass_id: str) -> Dict[str, Any]:
    """Get the value for a specific column."""
    match col:
        case "tx_date":
            return {"value": entry.date.strftime(CONSTANTS['DATE_FORMAT'])}
        case "txn_type":
            return {"value": MOVE_TYPE_MAPPING.get(entry.move_type)}
        case "doc_num":
            return {"value": entry.move_name}
        case "name":
            return {"value": entry.partner_id.name, "id": entry.partner_id.id}
        case "memo":
            return {"value": entry.ref}
        case "split_acc":
            return {"value": split_acc, "id": split_id}
        case "subt_nat_amount":
            return {"value": float(entry.debit if entry.debit != 0 else entry.credit)}
        case "rbal_nat_amount":
            return {"value": float(entry.balance)}
        case "account_name":
            return {"value": entry.account_id.name, "id": entry.account_id.id}
        case "vend_name":
            return {"value": entry.partner_id.name, "id": entry.partner_id.id}
        case "klass_name":
            return {"value": klass_name, "id": klass_id}
        case _:
            return {"value": ""}

def create_account_section(account: Dict[str, Any], columns_list: List[str]) -> Dict[str, Any]:
    """Create an account section template."""
    return {
        "Header": {
            "ColData": [{"value": account["name"], "id": account["id"]}] + 
                      [{"value": ""} for _ in range(len(columns_list) - 1)]
        },
        "Rows": {"Row": []},
        "Summary": {
            "ColData": [{"value": f"Total for {account['name']}", "id": account.get("id", "")}] + 
                      [{"value": ""} for _ in range(len(columns_list) - 2)] +
                      [{"value": 0}]
        },
        "type": "Section"
    }


def get_accounts(move_lines: List[Any]) -> List[Dict[str, Any]]:
    """Extract account information from move lines."""
    return [{
        "name": account.name, 
        "id": str(account.id)
    } for account in move_lines.mapped('account_id')]



# def process_move_line(request: Any, entry: Any, move_lines: Iterator[Any], columns_list: List[str]) -> Dict[str, Any]:
#     """Process a single move line and return row data."""
#     split_acc, split_id = get_split_acc(request, entry, move_lines)
#     klass_name, klass_id = get_klass_name(entry)
    
#     return {
#         "ColData": [
#             get_column_value(entry, col, split_acc, split_id, klass_name, klass_id)
#             for col in columns_list
#         ],
#         "type": "Data"
#     }

def process_move_line(request: Any, entry: Any, opposite_accounts: Dict, columns_list: List[str]) -> Dict[str, Any]:
    """Process a single move line and return row data."""
    split_acc, split_id = get_split_acc(request, entry, opposite_accounts)
    klass_name, klass_id = get_klass_name(entry)
    
    return {
        "ColData": [
            get_column_value(entry, col, split_acc, split_id, klass_name, klass_id)
            for col in columns_list
        ],
        "type": "Data"
    }

def process_account_move_lines(
    request: Any, 
    account_move_lines: Iterator[Any], 
    move_lines: Iterator[Any], 
    opposite_accounts: Dict, 
    columns_list: List[str]
) -> tuple[List[Dict[str, Any]], Decimal]:
    """Process all move lines for an account and return rows and total."""
    rows = []
    account_total = Decimal('0')
    
    for entry in account_move_lines:
        row_data = process_move_line(request, entry, opposite_accounts, columns_list)
        rows.append(row_data)
        account_total += Decimal(str(entry.debit - entry.credit))
    
    return rows, account_total

def process_account(
    request: Any, 
    account: Dict[str, Any], 
    move_lines: List[Any], 
    opposite_accounts: Dict,
    columns_list: List[str]
) -> Dict[str, Any]:
    """Process a single account and return its section."""
    account_section = create_account_section(account, columns_list)
    
    # Filter move lines for this account (using generator for efficiency)
    account_move_lines = [
        x for x in move_lines 
        if x.account_id.id == int(account["id"])
    ]
    
    # Process move lines and get total
    rows, account_total = process_account_move_lines(
        request, 
        account_move_lines, 
        move_lines,
        opposite_accounts,
        columns_list
    )
    
    # Update account section
    account_section["Rows"]["Row"].extend(rows)
    account_section["Summary"]["ColData"][-1]["value"] = float(account_total)
    
    return account_section

def prepare_response(
    request: Any, 
    start_date: Any, 
    end_date: Any,
    move_lines: List[Any], 
    columns_list: List[str], 
    currency: str = None
) -> Dict[str, Any]:
    """Prepare the response with account movements and balances."""
    # Initialize response structure
    response = {
        "Header": create_header(start_date, end_date, currency),
        "Columns": create_column_definition(columns_list),
        "Rows": {"Row": []}
    }
    # Get opposite accounts for all move lines in one query
    opposite_accounts = get_opposite_accounts(request, move_lines)
    
    # Get accounts and process each one
    accounts = get_accounts(move_lines)
    for account in accounts:
        account_section = process_account(
            request, 
            account, 
            move_lines, 
            opposite_accounts,
            columns_list
        )
        response["Rows"]["Row"].append(account_section)
    
    return response


# def prepare_response(
#     request: Any, 
#     start_date: Any, 
#     end_date: Any,
#     columns_list: List[str], 
#     currency: str = None
# ) -> Dict[str, Any]:
#     """Prepare the response with account movements and balances."""
#     # Fetch all move lines at once
#     domain = [
#         ('date', '>=', start_date),
#         ('date', '<=', end_date),
#         # Add any other necessary filters
#     ]
    
#     # Fetch all move lines in one query
#     move_lines = request.env['account.move.line'].sudo().search(domain)
    
#     # Get opposite accounts for all move lines in one query
#     opposite_accounts = get_opposite_accounts(request, move_lines)
    
#     # Initialize response structure
#     response = {
#         "Header": create_header(start_date, end_date, currency),
#         "Columns": create_column_definition(columns_list),
#         "Rows": {"Row": []}
#     }
    
#     # Get accounts and process each one
#     accounts = get_accounts(move_lines)
#     for account in accounts:
#         account_section = process_account(
#             request, 
#             account, 
#             move_lines,
#             opposite_accounts,  # Pass the pre-fetched opposite accounts
#             columns_list
#         )
#         response["Rows"]["Row"].append(account_section)
    
#     return response
