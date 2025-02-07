import json
import requests
from odoo import models, api

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
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('account_move.webhook_url')
        if not webhook_url:
            return

        payload = {
            'action': action,
            'model': 'account.move',
            'id': record.id,
            'data': {
                'name': record.name,
                'move_type': record.move_type,  # Invoice, Bill, etc.
                'state': record.state,
                'date': record.date.strftime('%Y-%m-%d') if record.date else False,
                'partner_id': record.partner_id.id,
                'partner_name': record.partner_id.name,
                'amount_total': record.amount_total,
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