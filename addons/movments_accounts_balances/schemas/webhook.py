from pydantic import BaseModel, HttpUrl


class WebhookConfigResponse(BaseModel):
    webhook_url: str

class WebhookDeleteResponse(BaseModel):
    message: str

class WebhookErrorResponse(BaseModel):
    errors: str
    message: str

# Input Models
class WebhookConfigInput(BaseModel):
    webhook_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "webhook_url": "https://example.com/webhook"
            },
            "description": {
                "webhook_url": "Must start with http:// or https://"
            }
        }



# Webhook Response Schemas
WEBHOOK_CONFIG_RESPONSE = WEBHOOK_CONFIG_UPDATE_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'data': {
            'type': 'object',
            'properties': {
                'webhook_url': {'type': 'string'}
            }
        }
    }
}

WEBHOOK_CONFIG_DELETE_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'}
    }
}

# Webhook Input Schema
WEBHOOK_CONFIG_SCHEMA = {
    'required': {
        'webhook_url': {
            'type': str,
            'display_name': 'Webhook URL',
            'swagger_type': 'string',
            'description': 'Must start with http:// or https://'
        }
    },
    'optional': {}
}

# Error Response Schema
WEBHOOK_ERROR_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'message': {'type': 'string'},
        'errors': {'type': 'string'},
        'status': {'type': 'integer'}
    }
}

# Parameters for different endpoints
WEBHOOK_CONFIG_GET_PARAMS = {
    'type': 'object',
    'properties': {}  # No parameters required for GET
}

WEBHOOK_CONFIG_UPDATE_PARAMS = {
    'body': {
        'schema': WEBHOOK_CONFIG_SCHEMA,
        'required': True
    }
}

WEBHOOK_CONFIG_DELETE_PARAMS = {
    'type': 'object',
    'properties': {}  # No parameters required for DELETE
}


