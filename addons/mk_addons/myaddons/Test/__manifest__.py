# -*- coding: utf-8 -*-
{
    'name': "IAC TEST",

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
    'depends': ['base'],

    # always loaded
    'data': [
        # 'views/tree_button.xml',
        #'security/ir.model.access.csv',
        #'view/congtrol_table_report.xml',
        # 'data/common_data.xml',
        'view/test.xml',
        # 'views/add_button.xml',
        # 'view/workflow_demo.xml',
        'view/menu.xml',

    ],

    # 'qweb':[
    #     'static/src/xml/tree_button.xml'
    # ],
    'application':True

}