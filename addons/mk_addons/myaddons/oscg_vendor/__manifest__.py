# -*- coding: utf-8 -*-
{
    'name': "IAC Vendor",
    'summary': """
        IAC Vendor
        """,
    'description': """
        英华达Vendor模块
    """,
    'author': "www.oscg.cn",
    'website': "www.oscg.cn",
    "category" : "IAC",
    'version': '10.0.0.1',
    'depends': [
        'base', 'web', 'mail', 'base_action_rule', 'muk_dms', 'web_sheet_full_width', 'warning_box'
    ],
    # always loaded
    'data': [
        'security/res_groups.xml',
        'data/common_data.xml',
        'data/vendor_data.xml',
        'data/sequence.xml',
        'data/task.xml',
        'view/common.xml',
        'view/vendorRegist.xml',
        'view/vendorRegistView.xml',
        'view/vendorView.xml',
        'view/simpleVendor_view.xml',
        'wizard/vendor_wizard.xml',
        'view/menu.xml'
    ],
    'installable': True,
    'application': True
}