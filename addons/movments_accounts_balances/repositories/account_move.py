from odoo import models
from .base import BaseOdooService
    

class AccountMoveService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.move'].sudo()

    def validate_journal_entry(self, jounral_entry_id, company_id):
        model = self._get_model()
        journal_entry = model.browse(jounral_entry_id)
        if not journal_entry:
            return False, "Journal entry not found"
        
        if journal_entry.company_id.id != int(company_id):
            return False, "Journal entry belongs to different company"

        return True, ""
        

class AccountMoveLineService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.move.line'].sudo()
    