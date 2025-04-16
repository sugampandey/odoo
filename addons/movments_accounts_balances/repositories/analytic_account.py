from odoo import models
from .base import BaseOdooService
    

class AnalyticAccountService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.analytic.account'].sudo()
    
    def validate_analytic_account(self, analytic_account_id, company_id):
        model = self._get_model()
        analytic_account = model.browse(int(analytic_account_id))
        if not analytic_account.exists():
            return False, f"Analytic account with id {analytic_account_id} does not exist"
        if analytic_account.company_id.id != int(company_id):
            return False, f"Analytic account with id {analytic_account_id} does not belong to the specified company"
        return True, ""
    

class AnalyticPlanService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.analytic.plan'].sudo()
    

    def validate_analytic_plan(self, plan_id):
        model = self._get_model()
        plan = model.browse(int(plan_id))
        if not plan.exists():
            return False, 'Plan not found'
        return True, ""