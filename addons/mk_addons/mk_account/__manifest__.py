# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Account',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'MK Account',
    'description': """
Sale Access
""",
    'author': "Jarvis (www.odoomod.com)",
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'account'
                ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
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
