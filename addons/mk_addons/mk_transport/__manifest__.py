# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Transport',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'MK Transport',
    'description': """
MK Transport
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'mk_base',
        'purchase',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/transport_menu_views.xml',
        'views/transport_move_views.xml',
        'views/stock_picking_views.xml',
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
