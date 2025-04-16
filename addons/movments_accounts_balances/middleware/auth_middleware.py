from functools import wraps
from odoo.http import request
import os
from dotenv import load_dotenv
from ..utils import APIResponse

# Load the environment variables from .env file
load_dotenv()

def validate_token_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the token from the Authorization header
        auth_header = request.httprequest.headers.get('X-Access-Token')
        if not auth_header or not auth_header.startswith('Bearer '):
            return APIResponse.error_response(message='No valid authorization token provided', status=401)

        token = auth_header.split(' ')[1]
        
        # Get the expected token from environment variable
        stored_token = os.environ.get('API_AUTH_TOKEN')

        if not stored_token:
            return APIResponse.error_response(message='API token not configured in environment variables', status=500)

        if token != stored_token:
            return APIResponse.error_response(message='Invalid token', status=401)

        # If token is valid, proceed with the original function
        return func(*args, **kwargs)

    return wrapper

