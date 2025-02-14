from typing import Optional, Literal, get_type_hints, Type, Union, Any
from datetime import datetime

class RequestSchemaGenerator:
    @staticmethod
    def generate_schema(cls: Type[Any]) -> dict:
        type_hints = get_type_hints(cls.__init__)
        required_fields = {}
        optional_fields = {}
        
        # Remove 'return' and 'self' from type hints
        type_hints.pop('return', None)
        type_hints.pop('self', None)
        
        for field_name, field_type in type_hints.items():
            # Check if field is Optional
            is_optional = (
                hasattr(field_type, '__origin__') 
                and field_type.__origin__ is Union 
                and type(None) in field_type.__args__
            )
            
            # Get the actual type for Optional fields
            if is_optional:
                actual_type = next(t for t in field_type.__args__ if t != type(None))
            else:
                actual_type = field_type

            field_info = {
                'type': RequestSchemaGenerator._get_python_type(actual_type),
                'display_name': ' '.join(field_name.split('_')),
                'swagger_type': RequestSchemaGenerator._get_swagger_type(actual_type)
            }

            # Handle Literal types for enums
            if hasattr(actual_type, '__origin__') and actual_type.__origin__ is Literal:
                field_info['enum'] = list(actual_type.__args__)

            if is_optional:
                optional_fields[field_name] = field_info
            else:
                required_fields[field_name] = field_info

        return {
            'required': required_fields,
            'optional': optional_fields
        }
    
    @classmethod
    def get_schema(cls) -> dict:
        return RequestSchemaGenerator.generate_schema(cls)

    @staticmethod
    def _get_python_type(field_type: Type) -> Type:
        if hasattr(field_type, '__origin__'):
            if field_type.__origin__ is Literal:
                return str
            return field_type.__origin__
        return field_type

    @staticmethod
    def _get_swagger_type(field_type: Type) -> str:
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Literal:
            return 'string'
        
        type_mapping = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            list: 'array',
            dict: 'object'
        }
        
        return type_mapping.get(field_type, 'string')



class ResponseSchemaGenerator:
    TYPE_MAPPING = {
        str: {'type': 'string'},
        int: {'type': 'integer'},
        float: {'type': 'number'},
        bool: {'type': 'boolean'},
        dict: {'type': 'object'},
        list: {'type': 'array'},
        datetime: {'type': 'string', 'format': 'date-time'}
    }

    @classmethod
    def get_schema(cls, wrap_response=False) -> dict:
        """Generate OpenAPI schema based on class annotations"""
        annotations = cls.__init__.__annotations__
        properties = {}

        for field_name, field_type in annotations.items():
            if field_name != 'return':  # Skip return annotation
                field_schema = cls._get_field_schema(field_type)
                properties[field_name] = field_schema

        if wrap_response:
            return {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': properties
                    },
                    'errors': {'type': 'string'}
                }
            }
        else:
            return {
                'type': 'object',
                'properties': properties
            }

    @classmethod
    def _get_field_schema(cls, field_type: Type) -> dict:
        # Handle Optional types
        is_optional = False
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            # Check if this is Optional (Union with NoneType)
            if type(None) in field_type.__args__:
                is_optional = True
                # Get the actual type (excluding NoneType)
                field_type = next(t for t in field_type.__args__ if t != type(None))

        # Handle nested schemas
        if isinstance(field_type, type) and issubclass(field_type, ResponseSchemaGenerator):
            schema = field_type.get_schema()
            if is_optional:
                schema['nullable'] = True
            return schema

        # Handle basic types
        base_schema = cls.TYPE_MAPPING.get(field_type, {'type': 'string'}).copy()
        if is_optional:
            base_schema['nullable'] = True
        return base_schema