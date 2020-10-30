# -*- coding: utf-8 -*-
{
    'name': "IAC CONTROL TABLE",

    'summary': """

        """,

    'description': """

    """,

    'author': "www.oscg.cn",
    'website': "www.oscg.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_import','oscg_vendor','mail'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'view/congtrol_table_report.xml',
        'view/iacControlTableView.xml',
        'view/country_origin.xml',
        'view/country_origin_upload.xml',
        'view/menu.xml',

    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True
}