# from ..schemas.company import (
#     CompanyCreateRequestModel,
#     CompanyResponseModel,
#     CompanyListResponseModel
# )
# from .common import get_pydantic_schema, get_route_params

# # Common error responses
# error_responses = {
#     404: {
#         'description': 'Resource not found',
#         'content': {
#             'application/json': {
#                 'schema': {
#                     'type': 'object',
#                     'properties': {
#                         'message': {'type': 'string'},
#                         'errors': {'type': 'string'}
#                     }
#                 }
#             }
#         }
#     },
#     500: {
#         'description': 'Internal Server Error',
#         'content': {
#             'application/json': {
#                 'schema': {
#                     'type': 'object',
#                     'properties': {
#                         'message': {'type': 'string'},
#                         'errors': {'type': 'string'}
#                     }
#                 }
#             }
#         }
#     }
# }

# # Common headers for all endpoints
# common_headers = [
#     {
#         'name': 'Authorization',
#         'type': 'string',
#         'description': 'Bearer token for authentication',
#         'required': True
#     },
#     {
#         'name': 'Content-Type',
#         'type': 'string',
#         'description': 'Content type of the request',
#         'required': True,
#         'default': 'application/json'
#     }
# ]

# # Query parameters for list endpoint
# list_query_params = [
#     {
#         'name': 'name',
#         'type': 'string',
#         'description': 'Filter companies by name',
#         'required': False
#     },
#     {
#         'name': 'active',
#         'type': 'string',
#         'description': 'Filter by active status (true/false)',
#         'required': False
#     },
#     {
#         'name': 'maxresults',
#         'type': 'integer',
#         'description': 'Maximum number of records to return (default: 100)',
#         'required': False,
#         'default': 100
#     },
#     {
#         'name': 'startposition',
#         'type': 'integer',
#         'description': 'Starting position for pagination (default: 0)',
#         'required': False,
#         'default': 0
#     }
# ]

# # Path parameters for get and delete endpoints
# company_id_param = [{
#     'name': 'company_id',
#     'type': 'integer',
#     'description': 'ID of the company',
#     'required': True
# }]

# # Generate documentation for each endpoint
# companies_docs = {
#     'create_company': {
#         'route': '/api/companies',
#         'method': 'POST',
#         'summary': 'Create a new company',
#         'description': 'Creates a new company with the provided details',
#         'requestBody': {
#             'required': True,
#             'content': {
#                 'application/json': {
#                     'schema': get_pydantic_schema(CompanyCreateRequestModel)
#                 }
#             }
#         },
#         'responses': {
#             '201': {
#                 'description': 'Company created successfully',
#                 'content': {
#                     'application/json': {
#                         'schema': get_pydantic_schema(CompanyResponseModel)
#                     }
#                 }
#             },
#             '400': {
#                 'description': 'Invalid request data',
#                 'content': {
#                     'application/json': {
#                         'schema': {
#                             'type': 'object',
#                             'properties': {
#                                 'message': {'type': 'string'},
#                                 'errors': {'type': 'string'}
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     },
#     'get_company': {
#         'route': '/api/companies/{company_id}',
#         'method': 'GET',
#         'summary': 'Get company details',
#         'description': 'Retrieves details of a specific company',
#         'parameters': [
#             {
#                 'name': 'company_id',
#                 'in': 'path',
#                 'required': True,
#                 'schema': {
#                     'type': 'integer'
#                 },
#                 'description': 'ID of the company to retrieve'
#             }
#         ],
#         'responses': {
#             '200': {
#                 'description': 'Company details retrieved successfully',
#                 'content': {
#                     'application/json': {
#                         'schema': get_pydantic_schema(CompanyResponseModel)
#                     }
#                 }
#             },
#             '404': {
#                 'description': 'Company not found',
#                 'content': {
#                     'application/json': {
#                         'schema': {
#                             'type': 'object',
#                             'properties': {
#                                 'message': {'type': 'string'},
#                                 'errors': {'type': 'string'}
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     },
#     'list_companies': {
#         'route': '/api/companies',
#         'method': 'GET',
#         'summary': 'List companies',
#         'description': 'Retrieves a list of companies with optional filtering',
#         'parameters': [
#             {
#                 'name': 'name',
#                 'in': 'query',
#                 'required': False,
#                 'schema': {
#                     'type': 'string'
#                 },
#                 'description': 'Filter by company name'
#             },
#             {
#                 'name': 'active',
#                 'in': 'query',
#                 'required': False,
#                 'schema': {
#                     'type': 'boolean'
#                 },
#                 'description': 'Filter by active status'
#             },
#             {
#                 'name': 'maxresults',
#                 'in': 'query',
#                 'required': False,
#                 'schema': {
#                     'type': 'integer',
#                     'default': 100
#                 },
#                 'description': 'Maximum number of results to return'
#             },
#             {
#                 'name': 'startposition',
#                 'in': 'query',
#                 'required': False,
#                 'schema': {
#                     'type': 'integer',
#                     'default': 0
#                 },
#                 'description': 'Starting position for pagination'
#             }
#         ],
#         'responses': {
#             '200': {
#                 'description': 'List of companies retrieved successfully',
#                 'content': {
#                     'application/json': {
#                         'schema': get_pydantic_schema(CompanyListResponseModel)
#                     }
#                 }
#             }
#         }
#     },
#     'delete_company': {
#         'route': '/api/companies/{company_id}',
#         'method': 'DELETE',
#         'summary': 'Delete a company',
#         'description': 'Deactivates a company',
#         'parameters': [
#             {
#                 'name': 'company_id',
#                 'in': 'path',
#                 'required': True,
#                 'schema': {
#                     'type': 'integer'
#                 },
#                 'description': 'ID of the company to delete'
#             }
#         ],
#         'responses': {
#             '200': {
#                 'description': 'Company deactivated successfully',
#                 'content': {
#                     'application/json': {
#                         'schema': {
#                             'type': 'object',
#                             'properties': {
#                                 'message': {'type': 'string'}
#                             }
#                         }
#                     }
#                 }
#             },
#             '404': {
#                 'description': 'Company not found',
#                 'content': {
#                     'application/json': {
#                         'schema': {
#                             'type': 'object',
#                             'properties': {
#                                 'message': {'type': 'string'},
#                                 'errors': {'type': 'string'}
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }

# # Example of using the decorator with automatic parameter detection
# @SwaggerGenerator.swagger_doc(
#     operation='list',
#     resource_name='companies',
#     response_model=CompanyListResponseModel,
#     custom_responses=error_responses
# )
# def list_companies(
#     name: str = None,  # Query parameter
#     active: bool = None,  # Query parameter
#     maxresults: int = 100,  # Query parameter
#     startposition: int = 0,  # Query parameter
#     authorization: str = None,  # Header parameter
#     content_type: str = 'application/json'  # Header parameter
# ):
#     """
#     List companies with optional filtering and pagination.
    
#     Args:
#         name: Filter companies by name
#         active: Filter by active status
#         maxresults: Maximum number of records to return
#         startposition: Starting position for pagination
#         authorization: Bearer token for authentication
#         content_type: Content type of the request
#     """
#     pass

# # Generate complete API documentation
# api_docs = SwaggerGenerator.generate_api_docs(
#     endpoints={
#         'companies': {
#             'method': 'GET',
#             'doc': companies_docs['list_companies']
#         },
#         'companies/{company_id}': {
#             'method': 'GET',
#             'doc': companies_docs['get_company']
#         },
#         'companies': {
#             'method': 'POST',
#             'doc': companies_docs['create_company']
#         },
#         'companies/{company_id}': {
#             'method': 'DELETE',
#             'doc': companies_docs['delete_company']
#         }
#     },
#     title='Company API',
#     version='1.0.0'
# )
