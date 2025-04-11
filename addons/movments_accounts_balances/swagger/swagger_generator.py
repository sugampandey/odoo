from typing import Type, Optional, Dict, Any, List, Callable, get_type_hints
from pydantic import BaseModel
from functools import wraps
import inspect
import re
from ..schemas.error import ErrorResponseModel, ResponseHeaderModel, ResponseModel, ErrorDetail, FaultModel

class SwaggerGenerator:
    def __init__(self):
        self.schemas = {}
        self._registered_models = set()
        # Register error models during initialization
        self.register_model(ErrorResponseModel)
        self.register_model(ResponseHeaderModel)
        self.register_model(ResponseModel)
        # Register base error models during initialization
        self.register_model(ErrorDetail)
        self.register_model(FaultModel)

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
        processed_schema = self._process_schema(schema)
        self.schemas[model.__name__] = processed_schema

    @staticmethod
    def generate_endpoint_doc(
        operation: str,
        resource_name: str,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        query_params: Optional[List[Dict[str, Any]]] = None,
        path_params: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[List[Dict[str, Any]]] = None,
        custom_responses: Optional[Dict[int, Dict[str, Any]]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate Swagger documentation for an API endpoint.
        
        Args:
            operation: The HTTP operation (create, read, update, delete, list)
            resource_name: Name of the resource
            request_model: Pydantic model for request body
            response_model: Pydantic model for response
            query_params: List of query parameters
            path_params: List of path parameters
            headers: List of header parameters
            custom_responses: Custom response schemas for different status codes
            description: Custom description for the endpoint
            tags: List of tags for grouping endpoints
            
        Returns:
            Dict containing the Swagger documentation
        """
        doc = {
            'summary': f'{operation.capitalize()} {resource_name}',
            'description': description or f'Endpoint to {operation} {resource_name}',
            'tags': tags or [resource_name],
            'responses': {
                '200': {
                    'description': 'Success',
                    'content': {
                        'application/json': {
                            'schema': response_model.model_json_schema() if response_model else {}
                        }
                    }
                }
            }
        }

        # Add request body schema if provided
        if request_model:
            doc['requestBody'] = {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': request_model.model_json_schema()
                    }
                }
            }

        # Initialize parameters list
        parameters = []

        # Add query parameters if provided
        if query_params:
            parameters.extend([
                {
                    'name': param['name'],
                    'in': 'query',
                    'description': param.get('description', ''),
                    'required': param.get('required', False),
                    'schema': {
                        'type': param['type'],
                        'default': param.get('default')
                    }
                }
                for param in query_params
            ])

        # Add path parameters if provided
        if path_params:
            parameters.extend([
                {
                    'name': param['name'],
                    'in': 'path',
                    'description': param.get('description', ''),
                    'required': param.get('required', True),
                    'schema': {
                        'type': param['type']
                    }
                }
                for param in path_params
            ])

        # Add header parameters if provided
        if headers:
            parameters.extend([
                {
                    'name': header['name'],
                    'in': 'header',
                    'description': header.get('description', ''),
                    'required': header.get('required', False),
                    'schema': {
                        'type': header['type']
                    }
                }
                for header in headers
            ])

        if parameters:
            doc['parameters'] = parameters

        # Add custom responses
        if custom_responses:
            doc['responses'].update(custom_responses)

        return doc

    @staticmethod
    def _get_parameter_type(param_type: Type) -> str:
        """Convert Python type to Swagger type"""
        type_mapping = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            list: 'array',
            dict: 'object',
            'date': 'string',
            'datetime': 'string'
        }
        return type_mapping.get(param_type, 'string')

    @staticmethod
    def _extract_parameters_from_function(func: Callable) -> Dict[str, List[Dict[str, Any]]]:
        """Extract parameters from function signature and route"""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        parameters = {
            'query': [],
            'path': [],
            'header': []
        }

        # Extract path parameters from route pattern
        path_param_names = set()
        if hasattr(func, 'original_routing'):
            routes = func.original_routing.get('routes', [])
            for route in routes:
                # Find all path parameters in the route pattern
                path_params = re.findall(r'<(?:int|str|float):(\w+)>', route)
                for param_name in path_params:
                    param_type = 'integer'
                    if f'<str:{param_name}>' in route:
                        param_type = 'string'
                    elif f'<float:{param_name}>' in route:
                        param_type = 'number'
                    
                    parameters['path'].append({
                        'name': param_name,
                        'type': param_type,
                        'description': f'{param_name.replace("_", " ").title()}',
                        'required': True
                    })
                    path_param_names.add(param_name)
        
        # Process remaining parameters as query parameters
        for name, param in sig.parameters.items():
            # Skip if parameter is already handled as path parameter
            if name in path_param_names or name in ['self', 'kwargs']:
                continue
                
            param_type = type_hints.get(name, str)
            swagger_type = SwaggerGenerator._get_parameter_type(param_type)
            
            # Get parameter description from docstring
            docstring = inspect.getdoc(func)
            param_doc = ''
            if docstring:
                for line in docstring.split('\n'):
                    if line.strip().startswith(f'{name}:'):
                        param_doc = line.split(':', 1)[1].strip()
                        break
            
            param_info = {
                'name': name,
                'type': swagger_type,
                'description': param_doc or f'{name.replace("_", " ").title()}',
                'required': param.default == inspect.Parameter.empty
            }
            
            # Determine parameter location based on name or type
            if name.startswith('x_') or name in ['authorization', 'content_type']:
                parameters['header'].append(param_info)
            elif name in ['start_date', 'end_date', 'date_from', 'date_to']:
                param_info['format'] = 'date'
                parameters['query'].append(param_info)
            else:
                parameters['query'].append(param_info)
                
        return parameters

    def create_error_model(self, model_name: str) -> Type[ErrorResponseModel]:
        """Create a dynamic error response model for a specific resource"""
        class DynamicErrorResponseModel(ErrorResponseModel):
            class Config:
                title = f"{model_name}ErrorResponse"
        
        DynamicErrorResponseModel.__name__ = f"{model_name}ErrorResponse"
        self.register_model(DynamicErrorResponseModel)
        return DynamicErrorResponseModel

    def swagger_doc(
        self,
        operation: str,
        resource_name: str,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        custom_responses: Optional[Dict[int, Dict[str, Any]]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        additional_headers: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Decorator to add Swagger documentation to an endpoint.
        """
        def decorator(func):
            # Extract parameters from function
            parameters = self._extract_parameters_from_function(func)
            
            # Register models if provided
            if request_model:
                self.register_model(request_model)
            if response_model:
                self.register_model(response_model)

            # Create dynamic error model for this resource
            model_name = resource_name.replace('-', '_').title().replace('_', '')
            error_model = self.create_error_model(model_name)

            # Add additional headers if provided
            if additional_headers:
                parameters['header'].extend(additional_headers)

            # Process parameters
            processed_parameters = []
            
            # Add query parameters
            for param in parameters['query']:
                param_schema = {'type': param['type']}
                if 'format' in param:
                    param_schema['format'] = param['format']
                processed_parameters.append({
                    'name': param['name'],
                    'in': 'query',
                    'required': param['required'],
                    'description': param['description'],
                    'schema': param_schema
                })

            # Add header parameters
            for param in parameters['header']:
                processed_parameters.append({
                    'name': param['name'],
                    'in': 'header',
                    'required': param.get('required', False),
                    'description': param['description'],
                    'schema': {'type': param['type']}
                })

            doc = {
                'summary': f'{operation.capitalize()} {resource_name}',
                'description': description or f'Endpoint to {operation} {resource_name}',
                'tags': tags or [resource_name],
                'parameters': processed_parameters,
                'responses': {
                    '200': {
                        'description': 'Success',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{response_model.__name__}'} if response_model else {}
                            }
                        }
                    },
                    '400': {
                        'description': f'Bad Request - Invalid {resource_name}',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{error_model.__name__}'}
                            }
                        }
                    },
                    '404': {
                        'description': f'{resource_name.title()} not found',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{error_model.__name__}'}
                            }
                        }
                    },
                    '500': {
                        'description': 'Internal Server Error',
                        'content': {
                            'application/json': {
                                'schema': {'$ref': f'#/components/schemas/{error_model.__name__}'}
                            }
                        }
                    }
                }
            }

            # Add custom responses
            if custom_responses:
                doc['responses'].update(custom_responses)

            # Add request body if model provided
            if request_model:
                doc['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {'$ref': f'#/components/schemas/{request_model.__name__}'}
                        }
                    }
                }

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            wrapper._swagger_doc = doc
            return wrapper
        return decorator

    def generate_swagger_spec(self, controllers: List[Any]) -> Dict[str, Any]:
        """Generate complete OpenAPI specification from controllers"""
        paths = {}
        
        for controller in controllers:
            for name, method in inspect.getmembers(controller, inspect.isfunction):
                if not hasattr(method, '_swagger_doc'):
                    continue
                    
                doc = method._swagger_doc.copy()  # Make a copy to avoid modifying the original
                routes = method.original_routing.get('routes', [])
                http_method = method.original_routing.get('methods', ['GET'])[0].lower()
                
                if not routes or not http_method:
                    continue

                for route in routes:
                    # Transform route parameters from Odoo-style to OpenAPI style
                    transformed_route = re.sub(r'<(?:int|str|float):(\w+)>', r'{\1}', route)
                    
                    # Extract path parameters
                    path_params = []
                    path_param_names = set()
                    for match in re.finditer(r'<(int|str|float):(\w+)>', route):
                        param_type = match.group(1)
                        param_name = match.group(2)
                        path_param_names.add(param_name)
                        swagger_type = 'integer' if param_type == 'int' else 'string' if param_type == 'str' else 'number'
                        
                        path_params.append({
                            'name': param_name,
                            'in': 'path',
                            'required': True,
                            'description': f'{param_name.replace("_", " ").title()}',
                            'schema': {'type': swagger_type}
                        })
                    
                    # Filter out path parameters from query parameters
                    if 'parameters' in doc:
                        doc['parameters'] = [
                            p for p in doc['parameters']
                            if p.get('in') != 'path' and p.get('name') not in path_param_names
                        ]
                    else:
                        doc['parameters'] = []
                    
                    # Add path parameters
                    doc['parameters'].extend(path_params)
                    
                    if transformed_route not in paths:
                        paths[transformed_route] = {}
                    
                    paths[transformed_route][http_method] = doc
        
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Odoo API Documentation',
                'version': '1.0.0',
                'description': 'API documentation for Odoo controllers'
            },
            'paths': paths,
            'components': {
                'schemas': self.schemas,
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT'
                    }
                }
            },
            'security': [{'bearerAuth': []}]
        }
        
        return spec

    def generate_api_docs(
        self,
        controllers: List[Any],
        title: str = 'API Documentation',
        version: str = '1.0.0',
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate complete OpenAPI/Swagger documentation."""
        spec = self.generate_swagger_spec(controllers)
        
        # Update info section with provided values
        spec['info'].update({
            'title': title,
            'version': version,
        })
        if description:
            spec['info']['description'] = description
        if tags:
            spec['tags'] = tags
            
        return spec

# Initialize a single instance to be used across the application
swagger_gen = SwaggerGenerator()
