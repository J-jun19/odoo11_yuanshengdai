# -*- coding: utf-8 -*-
{
    'name': "IAC PO",

    'summary': """

        """,

    'description': """
        英华达EP项目PO模块。
    """,

    'author': "www.oscg.cn",
    'website': "www.oscg.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','oscg_vendor'],

    # always loaded
    'data': [
        #'security/ir_security.xml',
        'data/common_data.xml',
        'view/vendor_base_view.xml',
        'view/purchase_order_view.xml',
        'view/purchase_order_file_view.xml',
        'view/purchase_order_change_view.xml',
        'view/purchase_order_mass_change_view.xml',
        'view/purchase_order_approve_view.xml',
        'view/purchase_order_vendor_confirm_view.xml',
        'view/purchase_order_vendor_confirm_history_view.xml',
        'view/purchase_order_vendor_unconfirm_stat_view.xml',
        'view/currency_exchange_view.xml',
        'view/change_po_buyer_code.xml',
        'view/mm_create.xml',
        'view/im_upload.xml',
        'view/im_upload_list.xml',
        'view/smart_po_recover.xml',
        'view/smart_po_cancel.xml',
        'view/menu_item_view.xml'
    ],
}



