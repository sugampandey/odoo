from .common import doc_generator
from ..controllers.schemas.webhook import (
    WEBHOOK_CONFIG_RESPONSE, WEBHOOK_CONFIG_GET_PARAMS, WEBHOOK_CONFIG_UPDATE_PARAMS,
    WEBHOOK_CONFIG_UPDATE_RESPONSE, WEBHOOK_CONFIG_DELETE_PARAMS, WEBHOOK_CONFIG_DELETE_RESPONSE
)

webhooks_docs = {
    'get_webhook_config': doc_generator.create_endpoint_doc(
        'get',
        'webhook/config',
        param_schema=WEBHOOK_CONFIG_GET_PARAMS,
        response_schema=WEBHOOK_CONFIG_RESPONSE
    ),
    'update_webhook_config': doc_generator.create_endpoint_doc(
        'update',
        'webhook/config',
        param_schema=WEBHOOK_CONFIG_UPDATE_PARAMS,
        response_schema=WEBHOOK_CONFIG_UPDATE_RESPONSE
    ),
    'delete_webhook_config': doc_generator.create_endpoint_doc(
        'delete',
        'webhook/config',
        param_schema=WEBHOOK_CONFIG_DELETE_PARAMS,
        response_schema=WEBHOOK_CONFIG_DELETE_RESPONSE
    )
}
