from typing import Optional, Literal, get_type_hints, Type, Union, Any, List
from datetime import datetime

class RequestSchemaGenerator:
    @classmethod
    def generate_schema(cls) -> dict:
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
                field_info = cls._process_field_type(actual_type, field_name)
                optional_fields[field_name] = field_info
            else:
                field_info = cls._process_field_type(field_type, field_name)
                required_fields[field_name] = field_info

            # # Handle Literal types for enums
            # if hasattr(actual_type, '__origin__') and actual_type.__origin__ is Literal:
            #     field_info['enum'] = list(actual_type.__args__)

        return {
            'required': required_fields,
            'optional': optional_fields
        }
    
    @staticmethod
    def _process_field_type(field_type: Type, field_name: str) -> dict:
        display_name = ' '.join(word.capitalize() for word in field_name.split('_'))

        # Handle basic types
        if field_type in (str, int, float, bool):
            return {
                'type': field_type,
                'display_name': display_name,
                'swagger_type': RequestSchemaGenerator._get_swagger_type(field_type)
            }
        
        # Handle dictionary types
        if field_type is dict or (hasattr(field_type, '__origin__') and field_type.__origin__ is dict):
            # If it's a typed dict with __annotations__, process each field
            if hasattr(field_type, '__annotations__'):
                required_fields = {}
                optional_fields = {}
                
                for key, value_type in field_type.__annotations__.items():
                    # Check if field is Optional
                    is_optional = (
                        hasattr(value_type, '__origin__') 
                        and value_type.__origin__ is Union 
                        and type(None) in value_type.__args__
                    )
                    
                    if is_optional:
                        actual_type = next(t for t in value_type.__args__ if t != type(None))
                        field_info = RequestSchemaGenerator._process_field_type(actual_type, key)
                        optional_fields[key] = field_info
                    else:
                        field_info = RequestSchemaGenerator._process_field_type(value_type, key)
                        required_fields[key] = field_info
                
                schema = {
                    'type': dict,
                    'display_name': display_name,
                    'swagger_type': 'object',
                }
                
                if required_fields:
                    schema['required'] = required_fields
                if optional_fields:
                    schema['optional'] = optional_fields
                    
                return schema
                
            # For simple dict type
            return {
                'type': dict,
                'display_name': display_name,
                'swagger_type': 'object'
            }
        
        # Handle nested objects that inherit from RequestSchemaGenerator
        if isinstance(field_type, type) and issubclass(field_type, RequestSchemaGenerator):
            nested_schema = field_type.get_schema()
            return {
                'type': dict,
                'display_name': display_name,
                'swagger_type': 'object',
                'items': nested_schema
            }
        
        # Handle List/Array types
        if (hasattr(field_type, '__origin__') and 
            (field_type.__origin__ is list or field_type.__origin__ == List)):
            item_type = field_type.__args__[0]
            return {
                'type': list,
                'display_name': display_name,
                'swagger_type': 'array',
                'items': RequestSchemaGenerator._process_field_type(item_type, field_name)
            }

        # Handle Literal types for enums
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Literal:
            return {
                'type': str,
                'display_name': display_name,
                'swagger_type': 'string',
                'enum': list(field_type.__args__)
            }

        # Default to string if type is not recognized
        return {
            'type': str,
            'display_name': display_name,
            'swagger_type': 'string'
        }

    
    @classmethod
    def get_schema(cls) -> dict:
        return cls.generate_schema()

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
    def get_schema(cls) -> dict:
        """Generate OpenAPI schema based on class annotations"""
        annotations = cls.__init__.__annotations__
        properties = {}

        for field_name, field_type in annotations.items():
            if field_name != 'return':  # Skip return annotation
                field_schema = cls._get_field_schema(field_type)
                properties[field_name] = field_schema

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

        # Handle Lists/Arrays
        if (hasattr(field_type, '__origin__') and 
            (field_type.__origin__ is list or field_type.__origin__ == List)):
            # Get the type of items in the list
            item_type = field_type.__args__[0]
            array_schema = {
                'type': 'array',
                'items': cls._get_field_schema(item_type)  # Recursively get schema for list items
            }
            if is_optional:
                array_schema['nullable'] = True
            return array_schema
        
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
    
    