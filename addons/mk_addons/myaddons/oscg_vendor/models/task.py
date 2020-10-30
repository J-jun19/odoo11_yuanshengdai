# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
import utility
import logging
from odoo.odoo_env import odoo_env

_logger = logging.getLogger(__name__)

# 定时任务，密码过期提醒
class TaskVendorPassword(models.Model):
    _name = 'task.vendor.password'

    name = fields.Char(string="Name")

    def cron_vendor_password_expiration_date(self):
        _logger.debug(u'定时任务启动，开始判断密码失效日期...')

        # 计算密码过期日期
        expiration_days = self.env['ir.config_parameter'].get_param('password_expiration_days', False)
        before_days = self.env['ir.config_parameter'].get_param('password_before_days', False)
        deadline = datetime.now() - timedelta(days=int(before_days))
        for user in self.env['res.users'].search([('active', '=', True)]):
            expiration_date = fields.Datetime.from_string(user.password_date) + timedelta(days=int(expiration_days))
            if expiration_date <= deadline:
                utility.send_to_email(self, user.id, 'oscg_vendor.password_expired_email')

# 定时任务，代理日期过期处理
class TaskAgentUsers(models.Model):
    _name = 'task.agent.users'

    name = fields.Char(string="Name")

    @odoo_env
    def cron_agent_expiration_date(self):
        _logger.debug(u'定时任务启动，开始判断代理失效日期...')

        for agent in self.env['iac.agent.users'].search([('expired_date', '<=', fields.Datetime.to_string(datetime.now()))]):
            agent.unlink()
        
# 定时任务，判断文档是否过期
class TaskDocument(models.Model):
    _name = 'task.document'

    name = fields.Char(string="Name")

    def cron_document_expiration_date(self):
        _logger.debug(u'定时任务启动，开始判断文档失效日期...')

        # 判断文档是否过期，如果过期则发邮件
        before_days = self.env['ir.config_parameter'].get_param('attachment_before_days', False)
        deadline = datetime.now() - timedelta(days=int(before_days))
        for attachment in self.env['iac.vendor.register.attachment'].search([('active', '=', True),
                                                                             ('time_sensitive', '=', True),
                                                                             ('expiration_date', '<=', fields.Datetime.to_string(deadline))]):
            utility.send_to_email(self, attachment.id, 'oscg_vendor.vendor_register_attachment_email')
        for attachment in self.env['iac.vendor.attachment'].search([('active', '=', True),
                                                                    ('time_sensitive', '=', True),
                                                                    ('expiration_date', '<=', fields.Datetime.to_string(deadline))]):
            utility.send_to_email(self, attachment.id, 'oscg_vendor.vendor_attachment_email')