from ..schemas.error import ERROR_SCHEMA
from typing import Any, Dict, List, Optional, Type, get_type_hints
from pydantic import BaseModel
from datetime import datetime
import inspect
from functools import wraps
import os
import importlib
import pkgutil
from pathlib import Path

def generate_swagger_schema(schema):
    """Convert our unified schema to Swagger format"""
    swagger_properties = {}
    required_fields = []

    def process_field_spec(field_spec):
        """Helper function to process field specifications"""
        field_def = {
            'type': field_spec['swagger_type'],
            'description': field_spec['display_name']
        }
        if 'format' in field_spec:
            field_def['format'] = field_spec['format']
            
        # Handle array (list) type
        if field_spec['type'] == list:
            field_def['type'] = 'array'
            
            # Handle array of simple types
            if field_spec['items']['type'] != dict:
                field_def['items'] = {
                    'type': field_spec['items']['swagger_type']
                }
                if 'format' in field_spec['items']:
                    field_def['items']['format'] = field_spec['items']['format']
            
            # Handle array of objects (dictionaries)
            else:
                items_properties = {}
                items_required = []
                
                # Process required items fields
                if 'required' in field_spec['items']['items']:
                    for item_field, item_spec in field_spec['items']['items']['required'].items():
                        items_properties[item_field] = process_field_spec(item_spec)
                        items_required.append(item_field)
                
                # Process optional items fields
                if 'optional' in field_spec['items']['items']:
                    for item_field, item_spec in field_spec['items']['items']['optional'].items():
                        items_properties[item_field] = process_field_spec(item_spec)
                
                field_def['items'] = {
                    'type': 'object',
                    'properties': items_properties
                }
                if items_required:
                    field_def['items']['required'] = items_required
        
        # Handle object (dictionary) type
        elif field_spec['type'] == dict:
            field_def['type'] = 'object'
            properties = {}
            dict_required = []
            
            # Process required fields
            if 'required' in field_spec['items']:
                for item_field, item_spec in field_spec['items']['required'].items():
                    properties[item_field] = process_field_spec(item_spec)
                    dict_required.append(item_field)
            
            # Process optional fields
            if 'optional' in field_spec['items']:
                for item_field, item_spec in field_spec['items']['optional'].items():
                    properties[item_field] = process_field_spec(item_spec)
            
            field_def['properties'] = properties
            if dict_required:
                field_def['required'] = dict_required
                
        return field_def

    # Process required fields
    for field_name, field_spec in schema['required'].items():
        swagger_properties[field_name] = process_field_spec(field_spec)
        required_fields.append(field_name)

    # Process optional fields
    if schema.get('optional'):
        for field_name, field_spec in schema['optional'].items():
            swagger_properties[field_name] = process_field_spec(field_spec)

    return {
        'type': 'object',
        'properties': swagger_properties,
        'required': required_fields
    }


def get_pydantic_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model to OpenAPI schema"""
    if model is None:
        return {}
        
    schema = model.model_json_schema()
    processed_schema = doc_generator._process_schema(schema)
    
    # Clean up the schema
    if 'title' in processed_schema:
        del processed_schema['title']
    if 'description' in processed_schema:
        del processed_schema['description']
    
    return processed_schema

def swagger_doc(
    summary: str = None,
    request_model: Type[BaseModel] = None,
    response_model: Type[BaseModel] = None,
    tags: list = None,
    responses: Dict[int, Dict[str, Any]] = None,
    parameters: List[Dict[str, Any]] = None,
    query_params: List[Dict[str, Any]] = None,
    path_params: List[Dict[str, Any]] = None,
    headers: List[Dict[str, Any]] = None
):
    """
    Decorator to add Swagger documentation to a route
    
    Args:
        summary: A brief summary of the endpoint
        request_model: Pydantic model for request body
        response_model: Pydantic model for response
        tags: List of tags for grouping endpoints
        responses: Custom responses dictionary
        parameters: List of parameters (for backward compatibility)
        query_params: List of query parameters, each being a dict with:
            - name: Parameter name
            - required: Boolean
            - description: Parameter description
            - type: Parameter type (string, integer, etc.)
            - format: Optional format (date-time, date, etc.)
        path_params: List of path parameters, similar structure to query_params
        headers: List of required headers, similar structure to query_params
    """
    def decorator(f):
        if not hasattr(f, '_swagger_doc'):
            f._swagger_doc = {}
        
        # Register request and response models
        if request_model:
            doc_generator.register_model(request_model)
        if response_model:
            doc_generator.register_model(response_model)

        # Process parameters
        processed_parameters = []
        
        # Add path parameters
        if path_params:
            for param in path_params:
                processed_parameters.append({
                    'name': param['name'],
                    'in': 'path',
                    'required': param.get('required', True),  # Path params are typically required
                    'description': param.get('description', ''),
                    'schema': {
                        'type': param.get('type', 'string')
                    }
                })
                if 'format' in param:
                    processed_parameters[-1]['schema']['format'] = param['format']

        # Add query parameters
        if query_params:
            for param in query_params:
                processed_parameters.append({
                    'name': param['name'],
                    'in': 'query',
                    'required': param.get('required', False),
                    'description': param.get('description', ''),
                    'schema': {
                        'type': param.get('type', 'string')
                    }
                })
                if 'format' in param:
                    processed_parameters[-1]['schema']['format'] = param['format']
                if 'enum' in param:
                    processed_parameters[-1]['schema']['enum'] = param['enum']

        # Add headers
        if headers:
            for header in headers:
                processed_parameters.append({
                    'name': header['name'],
                    'in': 'header',
                    'required': header.get('required', False),
                    'description': header.get('description', ''),
                    'schema': {
                        'type': header.get('type', 'string')
                    }
                })

        # Add any additional parameters (for backward compatibility)
        if parameters:
            processed_parameters.extend(parameters)

        doc = {
            'summary': summary or f.__name__,
            'tags': tags or [],
            'parameters': processed_parameters,
            'responses': {
                '200': {
                    'description': 'Success',
                    'content': {
                        'application/json': {
                            'schema': get_pydantic_schema(response_model)
                        }
                    }
                },
                '400': {
                    'description': 'Bad Request',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'error': {'type': 'string'},
                                    'message': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                '500': {
                    'description': 'Internal Server Error'
                }
            } | (responses or {})
        }

        if request_model:
            doc['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': get_pydantic_schema(request_model)
                    }
                }
            }

        f._swagger_doc.update(doc)
        return f
    return decorator



# First, let's create a base documentation template
def create_base_doc_template(summary, description, parameters, responses):
    return {
        'summary': summary,
        'description': description,
        'parameters': parameters,
        'responses': responses
    }

# Create standard response templates
standard_responses = {
    'success_200': {
        '200': {
            'description': 'Operation successful',
            'schema': None  # Will be set dynamically
        }
    },
    'success_201': {
        '201': {
            'description': 'Created successfully',
            'schema': None  # Will be set dynamically
        }
    },
    'success_204': {
        '204': {
            'description': 'Deleted successfully'
        }
    },
    'error_400': {
        '400': {
            'description': 'Invalid input',
            # 'schema': ERROR_SCHEMA,
            'content': {'application/json': {'schema': ERROR_SCHEMA}}
        }
    },
    'error_404': {
        '404': {
            'description': 'Resource not found',
            # 'schema': ERROR_SCHEMA
            'content': {'application/json': {'schema': ERROR_SCHEMA}}
        }
    },
    'error_500': {
        '500': {
            'description': 'Internal server error',
            # 'schema': ERROR_SCHEMA
            'content': {'application/json': {'schema': ERROR_SCHEMA}}
        }
    }
}


class SwaggerDocGenerator:
    def __init__(self):
        self.docs = {}
        self.tags = []
        self.schemas = {}
        self._registered_models = set()

    def add_tag(self, name, description=None, external_docs=None):
        """Add a tag for grouping endpoints"""
        tag = {
            'name': name,
            'description': description or f'Operations about {name}',
        }
        if external_docs:
            tag['externalDocs'] = external_docs
        self.tags.append(tag)

    def _process_schema(self, schema: dict) -> dict:
        """Process a schema and its nested schemas, transforming all references"""
        processed_schema = {}
        
        for key, value in schema.items():
            if key == '$defs':
                # Register all definitions as separate schemas
                for def_name, def_schema in value.items():
                    if def_name not in self.schemas:
                        self.schemas[def_name] = self._process_schema(def_schema)
                continue
                
            elif isinstance(value, dict):
                if '$ref' in value:
                    # Transform reference
                    ref = value['$ref'].split('/')[-1]
                    processed_schema[key] = {'$ref': f'#/components/schemas/{ref}'}
                    # Preserve additional properties if they exist
                    for k, v in value.items():
                        if k != '$ref':
                            processed_schema[key][k] = v
                elif 'anyOf' in value:
                    # Check if this is a nullable reference pattern
                    refs = [item for item in value['anyOf'] if '$ref' in item]
                    null_types = [item for item in value['anyOf'] if item.get('type') == 'null']
                    
                    if len(refs) == 1 and len(null_types) == 1:
                        # Convert to nullable reference
                        ref = refs[0]['$ref'].split('/')[-1]
                        processed_schema[key] = {
                            '$ref': f'#/components/schemas/{ref}',
                            'nullable': True
                        }
                        # Preserve description and default if present
                        if 'description' in value:
                            processed_schema[key]['description'] = value['description']
                        if 'default' in value:
                            processed_schema[key]['default'] = value['default']
                    else:
                        # Process anyOf references that aren't simple nullable patterns
                        processed_anyof = []
                        for item in value['anyOf']:
                            if '$ref' in item:
                                ref = item['$ref'].split('/')[-1]
                                processed_anyof.append({'$ref': f'#/components/schemas/{ref}'})
                            else:
                                processed_anyof.append(item)
                        processed_schema[key] = {'anyOf': processed_anyof}
                        if 'default' in value:
                            processed_schema[key]['default'] = value['default']
                        if 'description' in value:
                            processed_schema[key]['description'] = value['description']
                elif 'items' in value:
                    # Process array items
                    processed_items = {}
                    items = value['items']
                    
                    if isinstance(items, dict):
                        if '$ref' in items:
                            # Transform reference in items
                            ref = items['$ref'].split('/')[-1]
                            processed_items = {'$ref': f'#/components/schemas/{ref}'}
                        else:
                            processed_items = self._process_schema(items)
                    
                    processed_schema[key] = {
                        'type': 'array',
                        'items': processed_items
                    }
                    
                    # Preserve additional array properties
                    for k, v in value.items():
                        if k != 'items':
                            processed_schema[key][k] = v
                else:
                    # Recursively process nested objects
                    processed_schema[key] = self._process_schema(value)
            elif isinstance(value, list):
                processed_schema[key] = [
                    self._process_schema(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                processed_schema[key] = value
                
        return processed_schema

    def register_model(self, model: Type[BaseModel]) -> None:
        """Register a Pydantic model and all its nested models"""
        if not model or not issubclass(model, BaseModel) or model in self._registered_models:
            return

        self._registered_models.add(model)
        schema = model.model_json_schema()
        
        # Process the schema and all its nested components
        processed_schema = self._process_schema(schema)
        
        # Register the processed schema
        self.schemas[model.__name__] = processed_schema

    def add_schema(self, name: str, schema: dict) -> None:
        """Add a schema directly"""
        self.schemas[name] = self._process_schema(schema)

    def _create_parameters(self, param_schema):
        """
        Convert parameter schema to Swagger parameters
        
        param_schema format:
        {
            'path': [
                {
                    'name': 'company_id',
                    'type': 'integer',
                    'description': 'ID of the company',
                    'required': True
                }
            ],
            'query': [
                {
                    'name': 'state',
                    'type': 'string',
                    'description': 'Status of the record',
                    'required': False,
                    'enum': ['draft', 'posted', 'cancel']
                }
            ],
            'body': {
                'schema': SOME_SCHEMA,
                'required': True
            }
        }
        """
        parameters = []
        
        # Process path and query parameters only
        for param_type in ['path', 'query', 'headers']:
            if param_type in param_schema:
                in_type = 'header' if param_type == 'headers' else param_type
                for param in param_schema[param_type]:
                    param_spec = {
                        'in': in_type,
                        'name': param['name'],
                        'schema': {
                            'type': param['type']
                        },
                        'required': param.get('required', False),
                        'description': param.get('description', '')
                    }
                    if 'enum' in param:
                        param_spec['schema']['enum'] = param['enum']
                    if 'format' in param:
                        param_spec['schema']['format'] = param['format']
                        
                    parameters.append(param_spec)

        # # Process body parameters
        # if 'body' in param_schema:
        #     parameters.append({
        #         'in': 'body',
        #         'name': 'body',
        #         'required': param_schema['body'].get('required', True),
        #         'schema': (generate_swagger_schema(param_schema['body']['schema']) 
        #                  if 'schema' in param_schema['body'] else param_schema['body'])
        #     })

        return parameters

    def create_endpoint_doc(self, 
                          operation_type,
                          resource_name,
                          param_schema=None,
                          response_schema=None,
                          custom_responses=None,
                          tag=None):
        """
        Generic endpoint documentation generator
        """
        # Add response schema to components if provided
        schema_name = f'{resource_name.capitalize()}{operation_type.capitalize()}Response'
        if response_schema:
            self.add_schema(schema_name, response_schema)
        summary_map = {
            'list': f"List {resource_name}s",
            'get': f"Get {resource_name} Details",
            'create': f"Create {resource_name}",
            'update': f"Update {resource_name}",
            'delete': f"Delete {resource_name}"
        }

        description_map = {
            'list': f"Retrieve a list of {resource_name}s",
            'get': f"Retrieve details of a specific {resource_name}",
            'create': f"Create a new {resource_name}",
            'update': f"Update an existing {resource_name}",
            'delete': f"Delete a specific {resource_name}"
        }

        # Define operation order within a tag
        operation_order = {
            'list': 1,
            'get': 2,
            'create': 3,
            'update': 4,
            'delete': 5
        }

        # Default responses based on operation type
        default_responses = {
            'list': {
                '200': {
                    'description': f'List of {resource_name}s retrieved successfully',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{schema_name}'
                            } if response_schema else {
                                'type': 'array',
                                'items': {'type': 'object'}
                            }
                        }
                    }
                },
                '400': standard_responses['error_400']['400'],
                '500': standard_responses['error_500']['500']
            },
            'get': {
                '200': {
                    'description': f'{resource_name} details retrieved successfully',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{schema_name}'
                            } if response_schema else {'type': 'object'}
                        }
                    }
                },
                '404': standard_responses['error_404']['404'],
                '500': standard_responses['error_500']['500']
            },
            'create': {
                '201': {
                    'description': f'{resource_name} created successfully',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{schema_name}'
                            } if response_schema else {'type': 'object'}
                        }
                    }
                },
                '400': standard_responses['error_400']['400'],
                '500': standard_responses['error_500']['500']
            },
            'update': {
                '200': {
                    'description': f'{resource_name} updated successfully',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{schema_name}'
                            } if response_schema else {'type': 'object'}
                        }
                    }
                },
                '400': standard_responses['error_400']['400'],
                '404': standard_responses['error_404']['404'],
                '500': standard_responses['error_500']['500']
            },
            'delete': {
                '204': {
                    'description': f'{resource_name} deleted successfully'
                },
                '404': standard_responses['error_404']['404'],
                '500': standard_responses['error_500']['500']
            }
        }

        doc = create_base_doc_template(
            summary=summary_map[operation_type],
            description=description_map[operation_type],
            parameters=[p for p in (self._create_parameters(param_schema) if param_schema else [])
                   if p['in'] != 'body'],
            responses=custom_responses if custom_responses else default_responses[operation_type]
        )
        # Add tag and operation ordering
        doc.update({
            'tags': [tag or resource_name],
            'x-order': operation_order.get(operation_type, 99)  # Default to 99 if operation type not found
        })
        # Add requestBody for POST/PUT operations
        if param_schema and 'body' in param_schema:
            doc['requestBody'] = {
                'required': param_schema['body'].get('required', True),
                'content': {
                    'application/json': {
                        'schema': (generate_swagger_schema(param_schema['body']['schema'])
                                if 'schema' in param_schema['body'] else param_schema['body'])
                    }
                }
            }

        return doc


doc_generator = SwaggerDocGenerator()

def get_route_params(func) -> Dict[str, Any]:
    """Extract route parameters from a function"""
    params = {}
    sig = inspect.signature(func)
    
    for name, param in sig.parameters.items():
        if name in ['self', 'request', 'kwargs']:
            continue
            
        param_info = {
            'name': name,
            'in': 'query',
            'required': param.default == inspect.Parameter.empty,
            'schema': {
                'type': 'string'  # Default type, can be overridden
            }
        }
        
        # Try to get type from type hints
        type_hints = get_type_hints(func)
        if name in type_hints:
            param_type = type_hints[name]
            if param_type == int:
                param_info['schema']['type'] = 'integer'
            elif param_type == bool:
                param_info['schema']['type'] = 'boolean'
            elif param_type == float:
                param_info['schema']['type'] = 'number'
            elif param_type == datetime:
                param_info['schema']['type'] = 'string'
                param_info['schema']['format'] = 'date-time'
        
        params[name] = param_info
    
    return params

def generate_swagger_spec(controllers: List[Any]) -> Dict[str, Any]:
    """Generate complete OpenAPI specification from controllers"""
    paths = {}
    
    for controller in controllers:
        for name, method in inspect.getmembers(controller, inspect.isfunction):
            if not hasattr(method, '_swagger_doc'):
                continue
                
            doc = method._swagger_doc
            route = method.original_routing.get('routes')[0] if method.original_routing.get('routes') else ''
            http_method = method.original_routing.get('methods', ['GET'])[0].lower()
            
            if not route or not http_method:
                continue
                
            if route not in paths:
                paths[route] = {}
            
            paths[route][http_method] = {
                'summary': doc.get('summary', ''),
                'tags': doc.get('tags', []),
                'requestBody': doc.get('requestBody', None),
                'responses': doc.get('responses', {})
            }
    
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Odoo API Documentation',
            'version': '1.0.0',
            'description': 'API documentation for Odoo controllers'
        },
        'paths': paths,
        'components': {
            'schemas': doc_generator.schemas
        }
    }
    
    return spec
