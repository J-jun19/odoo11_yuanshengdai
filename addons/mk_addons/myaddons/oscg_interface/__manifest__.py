# -*- coding: utf-8 -*-
{
    'name': "IAC Interface",

    'summary': """

        """,

    'description': """
        英华达EP项目接口模块。
        定时任务触发类型为cron的时候
        year (int|str) – 4-digit year
        month (int|str) – month (1-12)
        day (int|str) – day of the (1-31)
        week (int|str) – ISO week (1-53)
        day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour (int|str) – hour (0-23)
        minute (int|str) – minute (0-59)
        second (int|str) – second (0-59)
        start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    """,

    'author': "www.oscg.cn",
    'website': "www.oscg.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','oscg_vendor','oscg_rfq','iac_forecast_release_to_vendor'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'view/interface_view.xml',
        'view/temp_table_log_view.xml',
        'data/temp_table_group_data.xml',
        #'data/timer_job_data.xml',
        'view/interface_timer_view.xml',
        #'view/test_report_view.xml',
    ],
}