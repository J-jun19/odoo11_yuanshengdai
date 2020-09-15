# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'Purchase Transport',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'Purchase Transport',
    'description': """
Purchase Transport
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'purchase',
        'sale',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/purchase_transport_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_views.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
