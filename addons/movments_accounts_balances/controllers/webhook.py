from odoo import http
from odoo.http import request
from ..utils import get_request_data, APIResponse
from ..swagger.swagger_generator import swagger_gen
from ..repositories.config_parameter import ConfigParamService
from ..middleware.auth_middleware import validate_token_middleware
from ..schemas.common import ACCESS_TOKEN_HEADER



class WebhookAPI(http.Controller):
    
    @http.route('/api/webhook/config', type='http', auth='public', methods=['GET'], csrf=False, cors="*")
    @validate_token_middleware
    @swagger_gen.swagger_doc(
        operation='get',
        resource_name='webhook',
        tags=['Webhooks'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def get_webhook_url(self):
        try:
            config_param_service = ConfigParamService(request.env)
            webhook_url = config_param_service.get_param('account_move.webhook_url')
            return APIResponse.success_response({'webhook_url': webhook_url})
        except Exception as e:
            return APIResponse.error_response(message='Failed to retrieve webhook URL', errors=str(e), status=500)

    @http.route('/api/webhook/config', type='http', auth='public', methods=['POST'], csrf=False, cors="*")
    @swagger_gen.swagger_doc(
        operation='update',
        resource_name='webhook',
        tags=['Webhooks'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def update_webhook_url(self):
        config_param_service = ConfigParamService(request.env)
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                data = get_request_data(request)
                if 'webhook_url' not in data:
                    return APIResponse.error_response(message='webhook_url is required')

                webhook_url = data['webhook_url']
                
                # Basic URL validation
                if webhook_url and not webhook_url.startswith(('http://', 'https://')):
                    return APIResponse.error_response(message='Invalid URL format. Must start with http:// or https://')

                config_param_service.set_param('account_move.webhook_url', webhook_url)
                return APIResponse.success_response({'webhook_url': webhook_url})
        except Exception as e:
            cursor.rollback()
            return APIResponse.error_response(message='Failed to update webhook URL', errors=str(e), status=500)


    @http.route('/api/webhook/config', type='http', auth='public', methods=['DELETE'], csrf=False, cors="*")
    @swagger_gen.swagger_doc(
        operation='delete',
        resource_name='webhook',
        tags=['Webhooks'],
        additional_headers=ACCESS_TOKEN_HEADER
    )
    def delete_webhook_url(self):
        config_param_service = ConfigParamService(request.env)
        cursor = request.env.cr
        try:
            with cursor.savepoint():
                config_param_service.set_param('account_move.webhook_url', '')
                return APIResponse.success_response({'message':'Webhook URL removed successfully'})
        except Exception as e:
            cursor.rollback()  
            return APIResponse.error_response(message='Failed to remove webhook URL', errors=str(e), status=500)
