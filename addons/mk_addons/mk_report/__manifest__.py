# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Report',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'MK Report',
    'description': """
MK Report
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'web'
    ],
    'external_dependencies': {
        'python': ['docxtpl'],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/ir_actions.xml',
        'views/assets_backend.xml'
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
