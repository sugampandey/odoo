from odoo import http
from odoo.http import Response, Controller, request
import json
import os
from ..swagger.common import doc_generator

class SwaggerController(http.Controller):
    
    def _get_swagger_spec(self):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Odoo API Documentation',
                'version': '1.0.0',
                'description': 'This is the API documentation for Odoo REST endpoints.'
            },
            'servers': [{'url': request.httprequest.url_root[:-1]}],
            'tags': doc_generator.tags,  # Add tags for grouping
            'paths': {},
            'components': {
                'schemas': doc_generator.schemas,
                'securitySchemes': {
                    'ApiKeyAuth': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key'
                    }
                }
            }
        }

        # Get the current database name
        db = http.request.db

        if db:
            try:
                # Get the router for the current database
                router = http.root.get_db_router(db)

                # Collect and sort routes
                routes = []
                
                # Get all routes
                for rule in router.bind('').map._rules:
                    if rule.rule.startswith('/api/'):
                        if hasattr(rule.endpoint, 'routing'):
                            path = rule.rule.replace('<int:', '{').replace('>', '}')
                            # Get methods from the rule
                            endpoint_func = rule.endpoint
                            if hasattr(endpoint_func, '_swagger_doc'):
                                routes.append((path, endpoint_func))
                                
                # Sort routes by tag and operation order
                sorted_routes = sorted(routes, key=lambda r: (
                    r[1]._swagger_doc.get('tags', [''])[0],
                    r[1]._swagger_doc.get('x-order', 99),
                    r[0]
                ))
                # Add sorted routes to spec
                for path, endpoint_func in sorted_routes:
                    if path not in spec['paths']:
                        spec['paths'][path] = {}

                    methods = endpoint_func.routing.get('methods', [])
                    for method in methods:
                        if method == 'OPTIONS':
                            continue
                        method = method.lower()
                        method_spec = endpoint_func._swagger_doc.copy()
                        
                        # Don't add parameters if they're already defined
                        if 'parameters' not in method_spec:
                            method_spec['parameters'] = []

                        # Add path parameters from URL if not already present
                        for converter, variable in rule._trace:
                            if converter and variable:
                                # Skip session_code parameter
                                if variable in ['session_code', 'create_token']:
                                    continue
                                if not any(p for p in method_spec['parameters'] 
                                         if p.get('in') == 'path' and p.get('name') == variable):
                                    param_type = 'integer' if converter == 'int' else 'string'
                                    method_spec['parameters'].append({
                                        'name': variable,
                                        'in': 'path',
                                        'required': True,
                                        'schema': {'type': param_type}
                                    })

                        # Filter out session_code from existing parameters
                        if 'parameters' in method_spec:
                            method_spec['parameters'] = [
                                param for param in method_spec['parameters']
                                if param.get('name') != 'session_code'
                            ]
                        # Handle request body for POST/PUT/PATCH methods
                        if method.upper() in ['POST', 'PUT', 'PATCH']:
                            # Check if there's a request body definition in the swagger doc
                            if hasattr(endpoint_func, '_swagger_doc') and 'requestBody' in endpoint_func._swagger_doc:
                                method_spec['requestBody'] = endpoint_func._swagger_doc['requestBody']
                            # If there's a body parameter in parameters, convert it to requestBody
                            elif 'parameters' in method_spec:
                                body_params = [p for p in method_spec['parameters'] if p.get('in') == 'body']
                                if body_params:
                                    body_param = body_params[0]
                                    # Remove body parameter from parameters list
                                    method_spec['parameters'] = [
                                        p for p in method_spec['parameters'] if p.get('in') != 'body'
                                    ]
                                    # Add as requestBody
                                    method_spec['requestBody'] = {
                                        'required': body_param.get('required', True),
                                        'content': {
                                            'application/json': {
                                                'schema': body_param.get('schema', {
                                                    'type': 'object'
                                                })
                                            }
                                        }
                                    }
                            # Add default request body if none specified
                            else:
                                method_spec['requestBody'] = {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object'
                                            }
                                        }
                                    }
                                }
                        spec['paths'][path][method] = method_spec

            except Exception as e:
                # _logger.error(f"Error generating swagger spec: {str(e)}")
                return spec

        return spec

    @http.route('/api/swagger.json', type='http', auth='public')
    def get_swagger_spec(self):
        return request.make_response(
            json.dumps(self._get_swagger_spec()),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/docs', type='http', auth='public')
    def swagger_ui(self):
        return request.render('movments_accounts_balances.swagger_ui_template', {
            'spec_url': '/api/swagger.json'
        })

