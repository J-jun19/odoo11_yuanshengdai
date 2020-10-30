# -*- coding: utf-8 -*-
{
    'name': "IAC SECURITY",

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
    'depends': ['base', 'oscg_vendor', 'oscg_po', 'oscg_rfq', 'iac_vendor_evaluation', 'iac_forecast_release_to_vendor',
                'oscg_control_table','iac_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/res.groups.csv',
        'security/ir_rule.xml',
    ],
}