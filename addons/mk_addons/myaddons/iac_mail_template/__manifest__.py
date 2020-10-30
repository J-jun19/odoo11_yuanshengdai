# -*- coding: utf-8 -*-
{
    'name': "IAC Mail Template",
    'summary': """
        IAC Mail Template
        """,
    'description': """
        英华达邮件模版
    """,
    'author': "Ning",
    'website': "www.iac.com",
    "category" : "IAC",
    'version': '10.0.0.1',
    'depends': [
        'base', 'warning_box', 'oscg_vendor', 'oscg_po'],
    # always loaded
    'data': [

        'data/remind_data.xml',
        # 'view/mail_template.xml',
        # 'view/menu.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
	'images': ['static/description/icon.png'],
    'installable': True,
    'application': True
}