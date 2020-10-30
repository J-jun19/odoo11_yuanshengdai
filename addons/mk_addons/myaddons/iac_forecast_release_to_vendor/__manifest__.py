# -*- coding: utf-8 -*-
{
    'name': "IAC forecast release to vendor",
    'summary': """
        IAC forecast release to vendor
        """,
    'description': """
        英华达入料管理模块
    """,
    'author': "Laura",
    'website': "www.iac.com",
    "category" : "IAC",
    'version': '10.0.0.1',
    'depends': [
        'base', 'warning_box', 'oscg_vendor', 'oscg_po','oscg_rfq'
        #,'oscg_interface'  #20180720 laura mark 萬濤說拿掉依賴關係
    ],
    # always loaded
    'data': [
        'view/upload_lt_history.xml',
        'view/vendor_forecast_delivery_report.xml',
        'view/task.xml',
        'view/buyer_upload_lt.xml',
        'view/buyer_fcst_delivery_report.xml',
        'view/vendor_upload_lt.xml',
        'view/internal_psi_report.xml',
		'view/vendor_psi_report.xml',
        'view/buyer_fcst_report.xml',
        'view/column_title.xml',
        'view/raw_data_temp.xml',
        'view/fcst_upload.xml',
        'data/remind_data.xml',
        'view/confirm_data.xml',
        'view/confirm_version.xml',
        'view/vendor_code_list.xml',
        'view/raw_data_list.xml',
        'view/vendor_forecast_delivery_report_bk.xml',
        'view/buyer_fcst_delivery_report_bk.xml',
        'view/buyer_upload_lt_bk.xml',
        'view/vendor_upload_lt_bk.xml',
        'view/internal_psi_report_bk.xml',
		'view/vendor_psi_report_bk.xml',
        'view/menu.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True
}