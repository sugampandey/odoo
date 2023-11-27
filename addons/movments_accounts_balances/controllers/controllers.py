from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountBalance(models.Model):
    _inherit = 'account.account'

    @api.model
    def get_all_accounts(self):
        accounts = self.env['account.account'].search([])

        account_data = [{'id': account.id, 'name': account.name} for account in accounts]

        return account_data

    @api.model
    def get_analytic_accounts(self):
        accounts = self.env['account.analytic.account'].search([])

        account_data = [{'id': account.id, 'name': account.name} for account in accounts]

        return account_data

    @api.model
    def get_all_partners(self):
        partners = self.env['res.partner'].search([])

        partner_data = [{'id': partner.id, 'name': partner.name} for partner in partners]

        return partner_data

    @api.model
    def get_balance(self, account_id, end_date):
        # Define search criteria to filter account move lines
        domain = [('account_id', '=', account_id),
                  ('date', '<=', end_date)]

        # Retrieve the most recent account move line based on the criteria
        move_line = self.env['account.move.line'].search(domain, order='date DESC', limit=1)

        # Prepare ledger data or return an empty list if no move lines are found
        balance_info = [{
            'name': move_line.name,
            'date': move_line.date,
            'balance': move_line.balance,
        }] if move_line else []

        # Return the general ledger data
        return {'balance_info': balance_info}

    @api.model
    def general_ledger_report(self, account_id, start_date, end_date):
        domain = [
            ('account_id', '=', account_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ]
        move_lines = self.env['account.move.line'].search(domain)

        ledger_data = []

        for line in move_lines:
            analytic_info = self.env['account.analytic.line'].search([('move_line_id', '=', line.id)], limit=1)
            analytic_partner_id = analytic_info.partner_id if analytic_info else False
            partner_name = analytic_partner_id.name if analytic_info else False
            analytic_account_id = analytic_info.account_id if analytic_info else ""
            analytic_account_name = analytic_account_id.name if analytic_info else ""
            analytic_account_amount = analytic_info.amount if analytic_info else "",
            partner_id = line.partner_id.id if line.partner_id else ""
            partner_type = None
            if line.partner_id:
                partner = line.partner_id
                if partner.customer_rank > 0 and partner.supplier_rank > 0:
                    partner_type = 'Customer/Vendor'
                elif partner.customer_rank > 0:
                    partner_type = 'Customer'
                elif partner.supplier_rank > 0:
                    partner_type = 'Vendor'

            else:
                partner_type = ""

            ledger_data.append({
                'date': line.date,
                'debit': line.debit,
                'credit': line.credit,
                'account_root_id': line.account_root_id.id,
                'analytic_move_id': analytic_info.id,
                'analytic_account_amount': analytic_account_amount,
                'analytic_account_name': analytic_account_name,
                'partner_id': line.partner_id.name,
                'partner_type': partner_type,

            })

        return {
            'ledger_data': ledger_data,
        }

    @api.model
    def get_bill(self, bill_id):
        # Define search criteria to filter bills
        domain = [
            ('id', '=', bill_id),
            ('move_type', '=', 'in_invoice'),
        ]

        # Retrieve bills based on the criteria
        bill = self.env['account.move'].search(domain, order='invoice_date', limit=1)

        if not bill:
            return {'error': 'Bill not found'}
    
        # Prepare a list to store bill data
        bill_data = []

        # Prepare a list to store invoice line data
        invoice_line_data = []
        for line in bill.invoice_line_ids:
            invoice_line_data.append({
                'line_id': line.id,
                'account_id': line.account_id.id,
                'account_name': line.account_id.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
                'analytic_account_name': line.analytic_account_id.name if line.analytic_account_id else '',
            })

        # Assemble bill data
        bill_data = {
            'id': bill.id,
            'bill_number': bill.ref,
            'bill_date': bill.invoice_date,
            'supplier_id': bill.partner_id.name,
            'amount': bill.amount_total,
            'state': bill.payment_state,
            'invoice_lines': invoice_line_data,
        }

        # Create a dictionary with a "bill_info" key
        response = {'bill_info': bill_data}

        return response

    @api.model
    # def create_bill(self, partner_id, invoice_date, due_date, reference, line_data, global_narration):
    def create_bill(self, bill_vals, partner_id, invoice_date, invoice_date_due, ref, narration):
        """
        Create a bill based on the provided data.

        :param partner_id: Partner ID for the bill.
        :param invoice_date: Invoice date for the bill.
        :param due_date: Due date for the bill.
        :param reference: Reference for the bill.
        :param line_data: List of dictionaries containing line data for the bill.
        :param global_narration: Global narration for the entire bill.
        :return: The created bill record.
        """
        # Prepare the invoice lines
        invoice_lines = []
        for line in bill_vals:
            invoice_line_vals = {
                'name': line.get('description', ''),
                'price_unit': line.get('amount', 0.0),
                'account_id': line.get('account_id'),
                'analytic_account_id': line.get('analytic_account_id', False),
            }
            invoice_lines.append((0, 0, invoice_line_vals))

        # Create a new bill record
        bill = self.env['account.move'].create({

            'move_type': 'in_invoice',
            'partner_id': partner_id,
            'invoice_date': invoice_date,
            'invoice_date_due': invoice_date_due,
            'ref': ref,
            'narration': narration,
            'invoice_line_ids': invoice_lines,
        })

        return bill

    @api.model
    def delete_bill(self, bill_id):
        Bill = self.env['account.move']
        bill = Bill.search([('id', '=', bill_id), ('move_type', '=', 'in_invoice')])

        if not bill:
            return "Bill not found."

        # Check if the bill is posted (validated)
        if bill.state == 'posted':
            # Add logic to cancel related journal entries (if any)
            # Example: bill.button_draft() or bill.button_cancel()
            try:
                bill.button_draft()  # Reset to draft
            except Exception as e:
                return "Failed to reset bill to draft: {}".format(e)

        # Additional logic to unreconcile payments if the bill is reconciled

        try:
            bill.unlink()  # Delete the bill
            return "Bill deleted successfully."
        except Exception as e:
            return "Failed to delete bill: {}".format(e)
        
    #Example usage: 
    # bills_ids = [1, 2, 3]  # Replace with the actual IDs of the bills
    # journal_id = 5  # Replace with the ID of the payment journal
    # payment_date = fields.Date.today()
    # payment_method_id = 1  # Replace with the actual payment method ID
    # payment_id = self.env['custom.model'].create_bill_payment(bills_ids, journal_id, payment_date, payment_method_id)
    @api.model
    def create_bill_payment(self, bills_ids, journal_id, payment_date, payment_method_id):
        Payment = self.env['account.payment']
        Bill = self.env['account.move']
        bills = Bill.browse(bills_ids)

        total_amount = sum(bill.amount_residual for bill in bills)
        payment_vals = {
            'amount': total_amount,
            'payment_date': payment_date,
            'communication': 'Payment for multiple bills',
            'partner_id': bills[0].partner_id.id,  # Assuming all bills are for the same partner
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'payment_method_id': payment_method_id,
            'journal_id': journal_id
        }

        payment = Payment.create(payment_vals)
        payment.post()

        # Reconcile each bill with the payment
        for bill in bills:
            payment.register_payment(bill.invoice_payments_widget)

        return payment.id
    
    @api.model
    def get_bill_payment_by_journal_entry_id(self, journal_entry_id):
        Payment = self.env['account.payment']
        # Search for payment associated with the given journal entry
        payment = Payment.search([('move_id', '=', journal_entry_id)], limit=1)
        if payment:
            return payment
        else:
            return "No payment found for the provided journal entry ID."
        
    #Used to create payment_method and payment_journal for a bank or a credit card - to be used for bill payment
    # Example usage: 
    # journal_name = "Vendor Payments Journal"
    # account_id = 1000  # Replace with the actual ID of your Chart of Account
    # journal_type = "bank"  # or "cash" depending on your requirements
    # payment_method_name = "Manual Outbound Payment"
    # journal_id, payment_method_id = self.env['custom.model'].setup_payment_journal(journal_name, account_id, journal_type, payment_method_name)
    
    @api.model
    def setup_payment_journal(self, journal_name, account_id, journal_type, payment_method_name):
        AccountJournal = self.env['account.journal']
        AccountPaymentMethod = self.env['account.payment.method']

        # Create or find the journal
        journal = AccountJournal.search([('name', '=', journal_name)], limit=1)
        if not journal:
            journal = AccountJournal.create({
                'name': journal_name,
                'type': journal_type,  # 'bank' or 'cash'
                'code': journal_name[:5].upper(),
                'default_debit_account_id': account_id,
                'default_credit_account_id': account_id,
            })

        # Create or find the payment method
        payment_method = AccountPaymentMethod.search([('name', '=', payment_method_name)], limit=1)
        if not payment_method:
            payment_method = AccountPaymentMethod.create({
                'name': payment_method_name,
                'payment_type': 'outbound',  # 'inbound' for customer payments, 'outbound' for supplier payments
                'code': payment_method_name[:10].upper(),
            })

        # Link the payment method to the journal
        journal.write({'outbound_payment_method_ids': [(4, payment_method.id)]})

        return journal.id, payment_method.id
    
    @api.model
    def cancel_and_delete_bill_payment(self, payment_id):
        Payment = self.env['account.payment']
        payment = Payment.browse(payment_id)

        if not payment:
            return "Payment not found."

        # Attempt to cancel the payment if it's not already in a cancellable state
        if payment.state not in ['draft', 'cancelled']:
            try:
                # Attempt to cancel the payment
                payment.action_cancel()
            except exceptions.UserError as e:
                return "Failed to cancel payment: {}".format(e)
            except Exception as e:
                return "Unexpected error occurred: {}".format(e)

        # Check again if the payment is in a cancellable state after attempting cancellation
        if payment.state in ['draft', 'cancelled']:
            try:
                payment.unlink()
                return "Payment deleted successfully."
            except Exception as e:
                return "Failed to delete payment: {}".format(e)
        else:
            return "Payment cannot be deleted as it is not in draft or cancelled state."


















