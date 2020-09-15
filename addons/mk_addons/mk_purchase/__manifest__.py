# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Purchase',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'MK Purchase',
    'description': "",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'purchase',
        'mk_base',
        'mk_account',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/mk_purchase_security.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_team_views.xml',
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
