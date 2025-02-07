from ..controllers.schemas.common import ERROR_RESPONSE


def generate_swagger_schema(schema):
    """Convert our unified schema to Swagger format"""
    swagger_properties = {}
    required_fields = []

    # Process required fields
    for field_name, field_spec in schema['required'].items():
        field_def = {
            'type': field_spec['swagger_type'],
            'description': field_spec['display_name']
        }
        if 'format' in field_spec:
            field_def['format'] = field_spec['format']
            
        if field_spec['type'] == list:
            field_def['type'] = 'array'
            items_properties = {}
            items_required = []
            
            # Process required items fields
            for item_field, item_spec in field_spec['items']['required'].items():
                items_properties[item_field] = {
                    'type': item_spec['swagger_type'],
                    'description': item_spec['display_name']
                }
                items_required.append(item_field)
            
            # Process optional items fields
            for item_field, item_spec in field_spec['items']['optional'].items():
                items_properties[item_field] = {
                    'type': item_spec['swagger_type'],
                    'description': item_spec['display_name']
                }
            
            field_def['items'] = {
                'type': 'object',
                'properties': items_properties,
                'required': items_required
            }
            
        swagger_properties[field_name] = field_def
        required_fields.append(field_name)

    # Process optional fields
    if schema.get('optional'):
        for field_name, field_spec in schema['optional'].items():
            field_def = {
                'type': field_spec['swagger_type'],
                'description': field_spec['display_name']
            }
            if 'format' in field_spec:
                field_def['format'] = field_spec['format']
            swagger_properties[field_name] = field_def

    return {
        'type': 'object',
        'properties': swagger_properties,
        'required': required_fields
    }

def swagger_doc(documentation):
    """
    Decorator to add Swagger documentation to a route
    """
    def decorator(f):
        f._swagger_doc = documentation
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
            'schema': ERROR_RESPONSE
        }
    },
    'error_404': {
        '404': {
            'description': 'Resource not found',
            'schema': ERROR_RESPONSE
        }
    },
    'error_500': {
        '500': {
            'description': 'Internal server error',
            'schema': ERROR_RESPONSE
        }
    }
}


class SwaggerDocGenerator:
    def __init__(self):
        self.docs = {}
        self.tags = []
        self.schemas = {}

    def add_tag(self, name, description=None, external_docs=None):
        """Add a tag for grouping endpoints"""
        tag = {
            'name': name,
            'description': description or f'Operations about {name}',
        }
        if external_docs:
            tag['externalDocs'] = external_docs
        self.tags.append(tag)

    def add_schema(self, name, schema):
        """Add a reusable schema"""
        self.schemas[name] = schema

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
        for param_type in ['path', 'query']:
            if param_type in param_schema:
                for param in param_schema[param_type]:
                    param_spec = {
                        'in': param_type,
                        'name': param['name'],
                        'schema': {
                            'type': param['type']
                        },
                        'required': param.get('required', param_type == 'path'),
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
