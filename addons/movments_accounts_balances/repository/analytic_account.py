from typing import Any, Dict, List, Optional, Union
from odoo import models
from .base import BaseOdooService
    

class AnalyticAccountService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.analytic.account'].sudo()
    

class AnalyticPlanService(BaseOdooService):
    def _get_model(self) -> models.Model:
        return self.env['account.analytic.plan'].sudo()