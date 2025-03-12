import datetime
from odoo import http
from odoo.http import request
import json
from .common import APIResponse, get_company_from_headers, validate_and_convert_data, get_request_data
from .validation_schema import journal_entry_expected_fields
from .utils import validate_company, validate_journal, validate_partner, validate_account, validate_tax

from ..swagger.common import swagger_doc
from ..swagger.journal_entry import journal_entries_docs
from .schemas.journal_entry import (JOURNAL_ENTRY_SCHEMA, JournalEntryModel, JournalEntryResponseModel, JournalEntryQueryResponseModel, JournalEntryListResponseModel, 
                                    LineResponseModel, JournalEntryLineDetailModel, AccountRefModel, EntityModel, EntityRefModel)
from .schemas.common import CurrencyRefModel, MetaDataModel, ClassRefModel

class JournalEntryController(http.Controller):

    # Notes 
    # Are we going to use DescriptionOnlyLine while we sync (need to add in Response ?)
    # DescriptionOnlyLine is not used while sendind Request, Is it auto generated ?

    {
    "Line": [
        {
        "JournalEntryLineDetail": {
            "PostingType": "Debit", 
            "AccountRef": {
            "name": "Opening Bal Equity", 
            "value": "39"
            }
        }, 
        "DetailType": "JournalEntryLineDetail", 
        "Amount": 100.0, 
        "Id": "0", 
        "Description": "nov portion of rider insurance"
        }, 
        {
        "JournalEntryLineDetail": {
            "PostingType": "Credit", 
            "AccountRef": {
            "name": "Notes Payable", 
            "value": "44"
            }
        }, 
        "DetailType": "JournalEntryLineDetail", 
        "Amount": 100.0, 
        "Description": "nov portion of rider insurance"
        }
    ]
    }


    def journal_entry_object(self, journal_entry):
        # description = ref
        # account_ref ={name-name, value-id}
        # class_ref ={name-name, value-id}
        # entity = {type=Vendor/Customer , Entityref = {name-name, value-id}}
        # Amount = amount
        # postingtype = Debit/Credit -- debit/credit columns
        # Detailtype= JournalEntryLineDetail
        # Id = id

        meta_data = MetaDataModel(
                CreateTime = journal_entry.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                LastUpdatedTime = journal_entry.write_date.strftime('%Y-%m-%d %H:%M:%S'),
            )

        def get_move_line(move_line):
            AccountRef = AccountRefModel(
                name=move_line.account_id.name,
                value=move_line.account_id.id,
            )
            analytic_class = request.env['account.analytic.line'].sudo().search([('move_line_id', '=', move_line.id)], limit=1)
            classRef = ClassRefModel(
                name=analytic_class.name if analytic_class else None,
                value=analytic_class.id if analytic_class else None,
            )
            EntityRef=EntityRefModel(
                name=move_line.partner_id.name,
                value=move_line.partner_id.id,
            )
            partner_type = move_line.partner_id.category_id.name
            Entity = EntityModel(
                Type=partner_type, 
                EntityRef=EntityRef
                )
            
            journal_entry_line_detail = JournalEntryLineDetailModel(
                PostingType='Debit' if move_line.debit != 0 else 'Credit',
                AccountRef=AccountRef,
                ClassRef=classRef,
                Entity=Entity,
            )
            line_item = LineResponseModel(
                Id=move_line.id,
                DetailType='JournalEntryLineDetail',
                Amount=move_line.debit if move_line.debit != 0 else move_line.credit,
                Description=move_line.ref,
                JournalEntryLineDetail=journal_entry_line_detail,
            )
            return line_item

        journal_entry = JournalEntryModel(
            Id=journal_entry.id,
            Line=[ get_move_line(line) for line in journal_entry.line_ids],
            TxnDate=journal_entry.date.strftime('%Y-%m-%d'),
            MetaData=meta_data
        )

        return journal_entry
    
    def create_journal_entry_response(self, journal_entry):
        return JournalEntryResponseModel(
            JournalEntry=self.journal_entry_object(journal_entry),
            time=datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        ).to_dict()
    
    def list_journal_entry_response(self, journal_entry_data, startPosition, maxResults, totalCount):
        QueryResponse=JournalEntryQueryResponseModel(
                startPosition=startPosition,
                JournalEntry=journal_entry_data,
                maxResults=maxResults,
                totalCount= totalCount
            )
        return JournalEntryListResponseModel(
            QueryResponse=QueryResponse,
            time=datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        ).to_dict()

        
    def validate_and_prepare_journal_entry_data(self, data, company_id, invoice_expected_fields):
        success, converted_data = validate_and_convert_data(data, invoice_expected_fields)
        if success is not True:
            return False, converted_data
        
        # Validate company 
        is_valid, error_message = validate_company(request, company_id)
        if not is_valid:
            return False, APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')

        # # validate partner
        # partner_id = converted_data.get('partner_id')
        # if partner_id:
        #     is_valid, error_message = validate_partner(request, partner_id, company_id)
        #     if not is_valid:
        #         return False, APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')

        # Validate and prepare journal items
        if not converted_data['Line']:
            return APIResponse.error_response(message='No journal items provided', errors='At least one journal item is required')
        
        move_lines = []
        total_debit = 0
        total_credit = 0
        
        for line in converted_data['Line']:
            # Docyt Values
            account_id = int(line['JournalEntryLineDetail'].get('AccountRef').get('value')) if line['JournalEntryLineDetail'].get('AccountRef') else None
            posting_type = (line['JournalEntryLineDetail'].get('PostingType')).lower() if line['JournalEntryLineDetail'].get('PostingType') else None
            amount = float(line.get('Amount', 0.0)) if line.get('Amount') else None
            description = line.get('Description') if line.get('Description') else None
            analytic_class_id =  int(line['JournalEntryLineDetail'].get('ClassRef').get('value')) if line['JournalEntryLineDetail'].get('ClassRef') else None

            # Validate account
            # account_id = int(line.get('account_id')) if line.get('account_id') else False
            is_valid, error_message = validate_account(request, account_id, company_id)
            if not is_valid:
                return False, APIResponse.error_response(f'Invalid account: {error_message}', f'Invalid account_id: {account_id}')
            
            # partner_id = int(line.get('partner_id')) if line.get('partner_id') else False
            partner_id = int(line['JournalEntryLineDetail'].get('Entity').get('EntityRef').get('value')) if line['JournalEntryLineDetail'].get('Entity') else None
            if partner_id:
                is_valid, error_message = validate_partner(request, partner_id, company_id)
                if not is_valid:
                    return False, APIResponse.error_response(f'Invalid partner: {error_message}', f'Invalid partner_id: {partner_id}')

            move_line = {
                'account_id': account_id,
                'ref': description,
                'debit': amount if posting_type == 'debit' else 0,
                'credit': amount if posting_type == 'credit' else 0,
                'partner_id': partner_id,
                # 'analytic_distribution': {k: int(v) if isinstance(v, str) and v.strip().isdigit() else v 
                # for k, v in eval(line.get('analytic_distribution')).items()} if line.get('analytic_distribution') else None,
                'analytic_distribution': {analytic_class_id: 100} if analytic_class_id else None,
            }

            total_debit += move_line['debit']
            total_credit += move_line['credit']
            move_lines.append((0, 0, move_line))
            
        # Validate balanced entry
        if not (total_debit - total_credit) == 0:
            return False, APIResponse.error_response(message='Journal entry is not balanced', errors=f'Difference between debit ({total_debit}) and credit ({total_credit})')
        
        # Create the journal entry
        move_vals = {
            'move_type': 'entry',
            'partner_id': partner_id,
            'date': datetime.date.today(),
            # 'ref': converted_data['ref'],
            'company_id': company_id,
            'line_ids': move_lines,
        }
        return True, move_vals
    
    @http.route('/api/journal-entries', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['create_journal_entry'])
    def create_journal_entry(self, *args, **post):
        """
        Creates a new journal entry in Odoo.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                company_id = get_company_from_headers(request)
                if not company_id:
                    return APIResponse.error_response(message='Company ID is required', errors='Missing CompanyId', status=400)

                success, move_vals = self.validate_and_prepare_journal_entry_data(data, company_id, JOURNAL_ENTRY_SCHEMA)
                if success is not True:
                    return move_vals
                    
                move = request.env['account.move'].sudo().create(move_vals)

                move.with_context(send_webhook=True).action_post()
                    
                # Prepare response data
                response_data = self.create_journal_entry_response(move)
                return APIResponse.success_response(response_data)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to create journal entry', errors=str(e), status=500)
        
    @http.route('/api/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['get_journal_entry'])
    def get_journal_entry(self, journal_entry_id, **kwargs):
        """
        Retrieves a specific journal entry by its ID.
        
        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing the journal entry details or an error message.
        """
        try:
            move = request.env['account.move'].sudo().browse(journal_entry_id)
            if not move.exists():
                return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)
            
            response_data = self.create_journal_entry_response(move)
            return APIResponse.success_response(response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while processing the request', errors=str(e), status=500)
    
    @http.route('/api/journal-entries', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['list_journal_entries'])
    def list_journal_entry(self, company_id, journal_id=None, maxresults=100, startposition=0, date_from=None, date_to=None, **kwargs):
        """
        Retrieves a list of all journal entries based on the provided filters.

        :param request: The HTTP request object containing optional filter parameters.
        :return: A dictionary containing the journal entry list or an error message.
        """
        try:
            domain = [
                ('move_type', '=', 'entry'),
                ('state', '=', 'posted'),
                ('payment_id', '=', None),
            ]
            is_valid, error_message = validate_company(request, company_id)
            if not is_valid:
                return APIResponse.error_response(f'Invalid company: {error_message}', f'Invalid company_id: {company_id}')
            domain.append(('company_id', '=', int(company_id)))
            if (date_from and not date_to) or (date_to and not date_from):
                return APIResponse.error_response(message='Both date_from and date_to must be provided')
            elif date_from and date_to:
                domain.append(('date', '>=', date_from))
                domain.append(('date', '<=', date_to))
            if journal_id:  
                is_valid, error_message = validate_journal(request, journal_id, company_id)
                if not is_valid:
                    return APIResponse.error_response(f'Invalid journal: {error_message}', f'Invalid journal_id: {journal_id}')
                domain.append(('journal_id', '=', int(journal_id)))

            startposition = int(startposition)
            maxresults = int(maxresults)
            # Get total count
            total_count = request.env['account.move'].sudo().search_count(domain)

            # Get journal entries with pagination
            moves = request.env['account.move'].sudo().search(
                domain,
                limit=maxresults, 
                offset=startposition,
                order='date desc, id desc'  # Order by date descending, then by ID
            )

            # Format the journal entry data
            journal_entry_data = []
            for move in moves:
                journal_entry_data.append(self.journal_entry_object(move))
            response_data = self.list_journal_entry_response(journal_entry_data, startposition, maxresults, total_count)
            return APIResponse.success_response(response_data)
        except Exception as e:
            return APIResponse.error_response(message='An error occurred while processing the request', errors=str(e), status=500)
    
        
    @http.route('/api/journal-entries/<int:journal_entry_id>', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_doc(journal_entries_docs['delete_journal_entry'])
    def delete_journal_entry(self, journal_entry_id, **kwargs):
        """
        Deletes a specific journal entry by its ID.

        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing a success message or an error message.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                move = request.env['account.move'].sudo().browse(int(journal_entry_id))
                if not move.exists():
                    return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

                # Check the state of the journal entry
                if move.state == 'posted':
                    # Reset to draft first
                    move.button_draft()
                    # Then delete
                    move.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response(message="Journal entry deleted successfully", data=None)
                elif move.state == 'draft':
                    # If in draft state, can delete directly
                    move.with_context(send_webhook=True).unlink()
                    return APIResponse.success_response(message="Journal entry deleted successfully", data=None)
                else:
                    return APIResponse.error_response(message=f'Cannot delete journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}')
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while deleting journal entry', errors=str(e), status=500)

        

    @http.route('/api/cancel_journal_entry', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    def cancel_journal_entry(self, journal_entry_id, **kwargs):
        """
        Cancels a specific journal entry by its ID.

        :param request: The HTTP request object containing the journal entry ID.
        :return: A dictionary containing a success message or an error message.
        """
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                move = request.env['account.move'].sudo().browse(int(journal_entry_id))
                if not move.exists():
                    return APIResponse.error_response(message='Journal entry not found', errors='Journal entry not found', status=404)

                # Check the state of the journal entry
                if move.state == 'posted':
                    # Reset to draft first
                    move.button_draft()

                    # Then cancel
                    move.with_context(send_webhook=True).button_cancel()

                    return APIResponse.success_response(message="Journal entry cancelled successfully", data=None)
                else:
                    return APIResponse.error_response(message=f'Cannot cancel journal entry in {move.state} state', errors=f'Invalid journal entry state: {move.state}', status=400)
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='An error occurred while cancelling journal entry', errors=str(e), status=500)
        