# -*- coding: utf-8 -*-

from odoo import models, fields, api

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