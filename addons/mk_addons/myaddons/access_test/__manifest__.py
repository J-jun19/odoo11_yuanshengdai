# -*- coding: utf-8 -*-
{
    'name': "ACCESS TEST",

    'summary': """

        """,

    'description': """

    """,

    'author': "Ning",
    'website': "www.oscg.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_import'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'view/congtrol_table_report.xml',
        'view/access_test.xml',
        'view/menu.xml',

    ],
    'installable': True,
    'application': True
}