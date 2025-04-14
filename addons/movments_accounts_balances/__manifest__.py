# -*- coding: utf-8 -*-
{
    'name': "Custom Account Balance Calculation",
    'summary': "API documentation for account balance calculations",
    'description': """
        This module provides API documentation for account balance calculations
        using Swagger UI.
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Accounting',
    'version': '0.1',
    'sequence': 1,
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/swagger_template.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'LGPL-3',
}