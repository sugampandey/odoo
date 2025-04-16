from odoo import http
from odoo.http import request
import json
from ..controllers import company, accounts, analytic_account, reports, partner, journal_entry, webhook
from ..swagger.swagger_generator import swagger_gen


class SwaggerController(http.Controller):
    
    @http.route('/api/docs', type='http', auth='public', website=True)
    def swagger_ui(self, **kwargs):
        """Serve Swagger UI"""
        try:
            controllers = [
                company.CompanyAPI,
                accounts.AccountAPI,
                analytic_account.AnalyticAccountAPI,
                reports.ReportsAPI,
                partner.PartnerAPI,
                journal_entry.JournalEntryAPI,
                webhook.WebhookAPI
            ]
            
            tags = [
                {'name': 'Companies', 'description': 'Company management endpoints'},
                {'name': 'Accounts', 'description': 'Account management endpoints'},
                {'name': 'Analytic Accounts', 'description': 'Analytic account management endpoints'},
                {'name': 'Reports', 'description': 'Report generation endpoints'},
                {'name': 'Customers', 'description': 'Customers management endpoints'},
                {'name': 'Vendors', 'description': 'Vendors management endpoints'},
                {'name': 'Journal Entries', 'description': 'Journal entry management endpoints'},
                {'name': 'Webhooks', 'description': 'Webhook management endpoints'}
            ]
            
            spec = swagger_gen.generate_api_docs(
                controllers=controllers,
                title='Odoo API Documentation',
                version='1.0.0',
                description='API documentation for Odoo controllers',
                tags=tags
            )
            
            return request.render('movments_accounts_balances.swagger_template', {
                'spec': json.dumps(spec)
            })
        except Exception as e:
            return request.render('movments_accounts_balances.error_template', {
                'error': str(e)
            })
    
    @http.route('/api/docs.json', type='http', auth='public', methods=['GET'])
    def get_api_docs(self):
        """Get OpenAPI documentation"""
        controllers = [
            company.CompanyAPI,
            accounts.AccountAPI,
            analytic_account.AnalyticAccountAPI,
            reports.ReportsAPI,
            partner.PartnerAPI,
            journal_entry.JournalEntryAPI,
            webhook.WebhookAPI
        ]
        
        tags = [
            {'name': 'Companies', 'description': 'Company management endpoints'},
            {'name': 'Accounts', 'description': 'Account management endpoints'},
            {'name': 'Analytic Accounts', 'description': 'Analytic account management endpoints'},
            {'name': 'Reports', 'description': 'Report generation endpoints'},
            {'name': 'Customers', 'description': 'Customers management endpoints'},
            {'name': 'Vendors', 'description': 'Vendors management endpoints'},
            {'name': 'Journal Entries', 'description': 'Journal entry management endpoints'},
            {'name': 'Webhooks', 'description': 'Webhook management endpoints'}
        ]
        
        spec = swagger_gen.generate_api_docs(
            controllers=controllers,
            title='Odoo API Documentation',
            version='1.0.0',
            description='API documentation for Odoo controllers',
            tags=tags
        )
        
        return request.make_response(
            json.dumps(spec),
            headers=[('Content-Type', 'application/json')]
        )

