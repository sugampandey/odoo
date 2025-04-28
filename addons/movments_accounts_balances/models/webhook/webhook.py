import json
import requests
from odoo import models, api
from ...repositories.config_parameter import ConfigParamService

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        record = super(AccountMove, self).create(vals)
        # Only trigger webhook if explicitly requested
        if self.env.context.get('send_webhook'):
            self._trigger_webhook('create', record)
        return record

    def write(self, vals):
        result = super(AccountMove, self).write(vals)
        
        # Only trigger webhook if explicitly requested
        if self.env.context.get('send_webhook'):
            for record in self:
                if 'state' in vals and vals['state'] == 'posted':
                    self._trigger_webhook('write', record)
        
        return result
    
    def unlink(self):
        # Only trigger webhook if explicitly requested
        if self.env.context.get('send_webhook'):
            # records_to_notify = self.filtered(lambda r: r.state != 'draft')
            for record in self:
                self._trigger_webhook('delete', record)
        return super(AccountMove, self).unlink()


    def _trigger_webhook(self, action, record):
        """
        Send a webhook payload to an external endpoint
        """
        config_param_service = ConfigParamService(self.env)
        webhook_url = config_param_service.get_param('account_move.webhook_url')
        if not webhook_url:
            return

        if record.move_type == 'out_invoice':
            move_type = 'Invoice'
        elif record.move_type == 'out_refund':
            move_type = 'Credit Note'
        elif record.move_type == 'in_invoice':
            move_type = 'Bill'
        elif record.move_type == 'in_refund':
            move_type = 'Vendor Credit'
        elif record.move_type == 'out_receipt':
            move_type = 'Sales Receipt'
        elif record.move_type == 'in_receipt':
            move_type = 'Purchase Receipt'
        elif record.move_type == 'entry':
            move_type = 'Journal Entry'
        payload = {
            'action': action,
            'db_table': 'account.move',
            'id': record.id,
            'data': {
                'Name': record.name,
                'move_type': move_type,  # Invoice, Bill, etc.
                'date': record.date.strftime('%Y-%m-%d') if record.date else False,
                'Amount': record.amount_total,
            }
        }

        # Send the webhook
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # _logger.error(_("Failed to send webhook: %s"), e)
            print(e)