import datetime


COLUMNS = [
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

MOVE_TYPE_MAPPING = {
    "entry": "JOURNAL ENTRY",
    "out_invoice": "INVOICE",
    "in_invoice": "BILL",
    "out_refund": "CREDIT NOTE",
    "in_refund": "DEBIT NOTE",
}

def get_split_acc(request, entry):
    move_lines = request.env['account.move.line'].sudo().search([('move_id', '=', entry.move_id.id)])
    debit_move_lines = [x for x in move_lines if x.debit!= 0]
    credit_move_lines = [x for x in move_lines if x.credit!= 0]
    if entry.debit != 0:
        if len(credit_move_lines) == 1:
            split_acc = credit_move_lines[0].account_id.name
            split_id = credit_move_lines[0].account_id.id
        split_acc = "-Split-"
        split_id = ""
    else:
        if len(debit_move_lines) == 1:
            split_acc = debit_move_lines[0].account_id.name
            split_id = debit_move_lines[0].account_id.id
        split_acc = "-Split-"
        split_id = ""
    return split_acc, split_id

def get_klass_name(request, entry):
    analytic_class = request.env['account.analytic.line'].sudo().search([('move_line_id', '=', entry.id)], limit=1).account_id
    if not analytic_class:
        return "", ""
    return analytic_class.name, analytic_class.id

def prepare_response(request, start_date, end_date, move_lines, columns_list, accounts=[], currency=None):
    columns_list = [col for col in columns_list if col in COLUMNS]
    response = {
        "Header": {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
            "ReportName": "GeneralLedger",
            "ReportBasis": "Accrual",
            "StartPeriod": start_date.strftime("%Y-%m-%d, %H:%M:%S"),
            "EndPeriod": end_date.strftime("%Y-%m-%d, %H:%M:%S"),
            "Currency": currency or "USD",
            "Option": [{"Name": "NoReportData", "Value": "false"}]
        },
        # "Columns": {
        #     "Column": [
        #         {"ColTitle": col["title"], "ColType": col["type"], "MetaData": [{"Name": "ColKey", "Value": col["key"]}]}
        #         for col in columns_list
        #     ]
        # },
        "Columns": {
            "Column": [
                {"ColTitle": col, "ColType": "String", "MetaData": [{"Name": "ColKey", "Value": col}]}
                for col in columns_list
            ]
        },
        "Rows": {
            "Row": []
        }
    }
    
    for account in accounts:
        account_total = 0
        account_move_lines = [x for x in move_lines if x.account_id.id == int(account["id"])]

        account_section = {
            "Header": {
                "ColData": [{"value": account["name"], "id": account["id"]}] + [{"value": ""} for _ in range(len(columns_list) - 1)]
            },
            "Rows": {"Row": []},
            "Summary": {
                "ColData": [{"value": f"Total for {account['name']}", "id": account.get("id", "")}] + 
                            [{"value": ""} for _ in range(len(columns_list) - 2)] +
                            [{"value": account_total}]
            },
            "type": "Section"
        }

        
        for entry in account_move_lines:
            row_data = {
                "ColData": [],
                "type": "Data"
            }     
            split_acc, split_id = get_split_acc(request, entry)
            klass_name, klass_id = get_klass_name(request, entry)       
            
            for col in columns_list:
                if col == "tx_date":
                    row_data["ColData"].append({"value" : entry.date.strftime("%Y-%m-%d, %H:%M:%S")})
                elif col == "txn_type":
                    row_data["ColData"].append({"value" : MOVE_TYPE_MAPPING.get(entry.move_type)})
                if col == "doc_num":
                    row_data["ColData"].append({"value" : entry.move_name})
                elif col == "name":
                    row_data["ColData"].append({"value" : entry.partner_id.name, "id" : entry.partner_id.id})
                elif col == "memo":
                    row_data["ColData"].append({"value" : entry.ref})
                elif col == "split_acc":
                    row_data["ColData"].append({"value" : split_acc, "id" : split_id}) 
                elif col == "subt_nat_amount":
                    row_data["ColData"].append({"value" : float(entry.debit if entry.debit != 0 else entry.credit)})
                elif col == "rbal_nat_amount":
                    row_data["ColData"].append({"value" : float(entry.balance)})
                elif col == "account_name":
                    row_data["ColData"].append({"value" : entry.account_id.name, "id" : entry.account_id.id})
                elif col == "vend_name":
                    row_data["ColData"].append({"value" : entry.partner_id.name, "id" : entry.partner_id.id})
                elif col == "klass_name":
                    row_data["ColData"].append({"value" : klass_name, "id" : klass_id})

            account_section["Rows"]["Row"].append(row_data)

            # amount = float(entry.get('amount_currency', 0.0))
            account_total += 10

        account_section["Summary"]["ColData"][len(columns_list) - 1]["value"] = account_total
        
        response["Rows"]["Row"].append(account_section)
    
    return response

