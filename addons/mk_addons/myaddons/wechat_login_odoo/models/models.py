# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# class wechat_login_odoo(models.Model):
#     _name = 'wechat_login_odoo.wechat_login_odoo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class wechat_corp_config(models.Model):
    _name = 'wechat.corp.config'
    _rec_name = 'corp_agent'
    _description = u'企业微信配置'

    corp_id = fields.Char('企业 CorpID')
    corp_agent = fields.Char('应用 AgentId', default='0')
    corp_agent_secret = fields.Char('应用 Secret')
    corp_secret = fields.Char('通讯录 Secret')
    first = fields.Boolean(u'占位字段')

    @api.onchange('corp_id', 'corp_agent', 'corp_agent_secret', 'corp_secret')
    def _onchange_filter_spaces(self):
        """过滤首尾空格"""
        self.corp_id = self.corp_id.strip() if self.corp_id else ''
        self.corp_agent = self.corp_agent.strip() if self.corp_agent else ''
        self.corp_agent_secret = self.corp_agent_secret.strip() if self.corp_agent_secret else ''
        self.corp_secret = self.corp_secret.strip() if self.corp_secret else ''


class wechat_corp_users(models.Model):
    _name = 'wechat.corp.users'
    _description = u'企业微信用户'

    name = fields.Char('姓名', required=True)
    userid = fields.Char('账号', required=True)
    gender = fields.Selection([("1", "男"), ("2", "女")])
    mobile = fields.Char('手机号')
    email = fields.Char('邮箱')
    position = fields.Char('职位')
    status = fields.Selection([("1", "已关注"), ("2", "已禁用"), ("4", "未关注")], string='状态', default="4")
    avatar = fields.Char('头像')
    department = fields.Integer('部门')

    _sql_constraints = [
        ('userid_key', 'UNIQUE (userid)', '账号已存在 !'),
        ('mobile_key', 'UNIQUE (mobile)', '手机号已存在 !'),
        ('email_key', 'UNIQUE (email)', '邮箱已存在 !'),
    ]

    def sync_users(self):
        """ 一键同步企业微信用户
        先从企业微信把用户同步下来，再从系统用户以增量的方式同步到企业微信
         """
        pass

