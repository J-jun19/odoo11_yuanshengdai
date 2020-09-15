# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Sale',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'MK Sale',
    'description': "",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'sale',
        'sale_stock',
        'mk_base',
        'mk_account',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'views/sale_views.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
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
