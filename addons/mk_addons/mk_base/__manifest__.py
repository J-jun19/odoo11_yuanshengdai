# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

{
    'name': 'MK Base',
    'version': '1.0',
    'category': 'Mokuai',
    'summary': 'MK Base',
    'description': '',
    'author': 'Jarvis (www.odoomod.com)',
    'website': 'http://www.odoomod.com',
    'license': 'Other proprietary',
    'depends': [
        'product',
        'l10n_cn',  # country, state
        'base_address_city',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/mk_base_security.xml',
        'data/mk_base_data.xml',
        'data/city_data.xml',
        'data/nation_data.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/product_template_views.xml',
        'views/product_brand_views.xml',
        'views/product_attribute_views.xml',
        'views/res_country_views.xml',
        'views/res_nation_views.xml',
        'views/assets_backend.xml',
        'views/webclient_templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
