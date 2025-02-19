from requests import Response
from odoo.http import request
import json
from typing import Any, Dict, Optional, Union
import datetime 
from .schemas.error import ErrorResponseModel, ErrorDetail, FaultModel, ResponseHeaderModel, ResponseModel

class APIResponse:
    # @staticmethod
    # def format(success, message, data=None, errors=None, status=200):
    #     """
    #     Formats a standardized API response.
        
    #     Args:
    #         success: Boolean indicating success or failure
    #         message: A short message describing the response
    #         data: The data payload (optional)
    #         errors: Details about errors (optional)
    #         status: HTTP status code (default: 200)
        
    #     Returns:
    #         A formatted Response object
    #     """
    #     response = {
    #         "success": success,
    #         "data": data if data is not None else {},
    #         "errors": errors if errors is not None else None,
    #     }
    #     return json_response(response, status)
    
    @staticmethod
    def error_response(message, errors=None, status=400, error_type=None):
        """Creates an error response."""
        # return APIResponse.format(False, message, errors=errors, status=status)
        error_detail = ErrorDetail(message=message, detail=errors)
        fault_model = FaultModel(error=[error_detail], type=error_type)
        response_header = ResponseHeaderModel(status=status, message=message)
        response_model = ResponseModel(fault=fault_model)
        error_response = ErrorResponseModel(responseHeader=response_header, response=response_model).to_dict()
        return json_response(error_response, status)

    
    @staticmethod
    def success_response(response, status=200):
        """Creates a success response."""
        return json_response(response, status)
    

def json_response(data, status=200):
        """Helper method to create JSON response with proper headers"""
        response = request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*, GET, POST, OPTIONS, DELETE, PUT'
        response.headers['Access-Control-Allow-Headers'] = '*, Content-Type, Authorization, X-CSRFToken'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response


def get_request_data(request):
    """
    Extract data from request either from body or params
    
    Returns:
        Dict: Request data
    """
    if request.httprequest.data.decode('utf-8'):
        return json.loads(request.httprequest.data.decode('utf-8'))
    else:
        return request.params
    
def get_company_from_headers(request):
    return int(request.httprequest.headers.get('X-Company-Id')) if request.httprequest.headers.get('X-Company-Id') else None

def get_payment_method_from_headers(request):
    return request.httprequest.headers.get('X-PaymentMethod') if request.httprequest.headers.get('X-PaymentMethod') else None
    

def convert_field_value(value, target_type, field_name, field_specs=None):
    """
    Converts a value to the target type.
    
    Args:
        value: The value to convert
        target_type: The type to convert to (int, str, bool, etc.)
        field_name: Name of the field (for error messages)
        field_specs: Additional field specifications (optional)
    
    Returns:
        Converted value
    
    Raises:
        ValueError: If conversion fails
    """
    try:
        if field_specs and field_specs.get('format') == 'date':
            if not isinstance(value, str):
                raise ValueError(f"{field_name} must be a string")
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"{field_name} should be in YYYY-MM-DD format")
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'y')
            return bool(value)
        if target_type == list:
            if not isinstance(value, list):
                raise ValueError(f"{field_name} must be a list")
            return value
        return target_type(value)
    except (ValueError, TypeError):
        raise ValueError(f"Could not convert {field_name} to {target_type.__name__}")
    

def convert_fields(data: Dict, fields_dict: Dict, required: bool = True, parent_name: str = None) -> tuple:
    """
    Converts fields without validation
    """
    converted_data = {}
    
    for field, field_specs in fields_dict.items():
        field_display = field_specs['display_name']
        if parent_name:
            field_display = f"{field_display} in {parent_name}"

        # Check if required field is missing
        if required and field not in data:
            return False, APIResponse.error_response(
                message=f"Missing required field: {field_display}",
                errors=f"Missing required field: {field_display}",
            )
        
        # Convert field if it exists and has value
        if field in data and data[field] is not None:
            try:
                if 'items' in field_specs:
                    if not isinstance(data[field], list):
                        return False, APIResponse.error_response(
                            message=f"{field_display} must be a list",
                            errors=f"{field_display} must be a list",
                        )
                    
                    converted_lines = []
                    for index, item in enumerate(data[field]):
                        if not isinstance(item, dict):
                            return False, APIResponse.error_response(
                                message=f"Item at index {index} in {field_display} must be a dictionary",
                                errors=f"Item at index {index} in {field_display} must be a dictionary",
                            )
                        
                        converted_item = {}
                        # Convert required fields in item
                        for item_field, item_specs in field_specs['items']['required'].items():
                            if item_field not in item:
                                return False, APIResponse.error_response(
                                    message=f"Missing required field '{item_specs['display_name']}' in {field_display} at index {index}",
                                    errors=f"Missing required field '{item_specs['display_name']}' in {field_display} at index {index}",
                                )
                            try:
                                converted_item[item_field] = convert_field_value(
                                    item[item_field],
                                    item_specs['type'],
                                    f"{item_specs['display_name']} in {field_display} at index {index}",
                                    item_specs
                                )
                            except ValueError as e:
                                return False, APIResponse.error_response(message=str(e), errors=str(e))
                        
                        # Convert optional fields in item
                        if field_specs['items'].get('optional'):
                            for item_field, item_specs in field_specs['items']['optional'].items():
                                if item_field in item and item[item_field] is not None:
                                    try:
                                        converted_item[item_field] = convert_field_value(
                                            item[item_field],
                                            item_specs['type'],
                                            f"{item_specs['display_name']} in {field_display} at index {index}",
                                            item_specs
                                        )
                                    except ValueError as e:
                                        return False, APIResponse.error_response(message=str(e), errors=str(e))
                        
                        converted_lines.append(converted_item)
                    converted_data[field] = converted_lines
                else:
                    converted_data[field] = convert_field_value(
                        data[field],
                        field_specs['type'],
                        field_display,
                        field_specs
                    )
            except ValueError as e:
                return False, APIResponse.error_response(message=str(e), errors=str(e))
    
    return True, converted_data

def validate_converted_data(converted_data: Dict, expected_fields: Dict) -> Union[bool, Response]:
    """
    Validates the already converted data
    """
    def validate_converted_value(value: Any, field_specs: Dict, field_display: str) -> Optional[Response]:
        """Helper function to validate converted values"""
        if 'items' in field_specs:
            if not isinstance(value, list):
                return APIResponse.error_response(
                    message=f"{field_display} must be a list",
                    errors=f"{field_display} must be a list",
                )
            
            for index, item in enumerate(value):
                if not isinstance(item, dict):
                    return APIResponse.error_response(
                        message=f"Item at index {index} in {field_display} must be a dictionary",
                        errors=f"Item at index {index} in {field_display} must be a dictionary",
                    )
                
                # Validate required fields in item
                for item_field, item_specs in field_specs['items']['required'].items():
                    if item_field not in item:
                        return APIResponse.error_response(
                            message=f"Missing required field '{item_specs['display_name']}' in {field_display} at index {index}",
                            errors=f"Missing required field '{item_specs['display_name']}' in {field_display} at index {index}",
                        )
                    
                    if item_specs.get('format') == 'date':
                        if not isinstance(item[item_field], (datetime.date, datetime.datetime)):
                            return APIResponse.error_response(
                                message=f"{item_specs['display_name']} in {field_display} at index {index} must be a valid date",
                                errors=f"Invalid date type for {item_specs['display_name']} in item {index}",
                            )
                    else:
                        if not isinstance(item[item_field], item_specs['type']):
                            return APIResponse.error_response(
                                message=f"Invalid type for {item_specs['display_name']} in {field_display} at index {index}. Expected {item_specs['type'].__name__}, got {type(item[item_field]).__name__}",
                                errors=f"Invalid type for {item_specs['display_name']} in {field_display} at index {index}",
                            )
                        
                # Validate optional fields in item if present
                if field_specs['items'].get('optional'):
                    for item_field, item_specs in field_specs['items']['optional'].items():
                        if item_field in item and item[item_field] is not None:
                            if item_specs.get('format') == 'date':
                                if not isinstance(item[item_field], (datetime.date, datetime.datetime)):
                                    return APIResponse.error_response(
                                        message=f"{item_specs['display_name']} in {field_display} at index {index} must be a valid date",
                                        errors=f"Invalid date type for {item_specs['display_name']} in item {index}",
                                    )
                            else:
                                if not isinstance(item[item_field], item_specs['type']):
                                    return APIResponse.error_response(
                                        message=f"Invalid type for {item_specs['display_name']} in {field_display} at index {index}",
                                        errors=f"Invalid type for {item_specs['display_name']} in {field_display} at index {index}",
                                    )
        else:
            if field_specs.get('format') == 'date':
                if not isinstance(value, (datetime.date, datetime.datetime)):
                    return APIResponse.error_response(
                        message=f"{field_display} must be a valid date",
                        errors=f"Invalid date type for {field_display}",
                    )
            else:
                if not isinstance(value, field_specs['type']):
                    return APIResponse.error_response(
                        message=f"Invalid type for {field_display}. Expected {field_specs['type'].__name__}, got {type(value).__name__}",
                        errors=f"Invalid type for {field_display}",
                    )
        return None

    # Validate required fields
    for field, field_specs in expected_fields['required'].items():
        if field not in converted_data:
            return APIResponse.error_response(
                message=f"Missing required field: {field_specs['display_name']}",
                errors=f"Missing required field: {field_specs['display_name']}",
            )
        
        error = validate_converted_value(converted_data[field], field_specs, field_specs['display_name'])
        if error:
            return error

    # Validate optional fields if present
    if expected_fields.get('optional'):
        for field, field_specs in expected_fields['optional'].items():
            if field in converted_data and converted_data[field] is not None:
                error = validate_converted_value(converted_data[field], field_specs, field_specs['display_name'])
                if error:
                    return error

    return True


def validate_and_convert_data(data: Dict, expected_fields: Dict):
    """
    Validates and converts the data before creation
    """
    success, result = convert_fields(data, expected_fields['required'], required=True)
    if not success:
        return False, result
    converted_data = result

    # Then convert optional fields
    success, result = convert_fields(data, expected_fields['optional'], required=False)
    if not success:
        return False, result
    converted_data.update(result)

    # Validate the converted data
    validation_result = validate_converted_data(converted_data, expected_fields)
    if validation_result is not True:
        return False, validation_result

    return True, converted_data