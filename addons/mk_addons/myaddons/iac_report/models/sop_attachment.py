# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from datetime import datetime, timedelta
from odoo import fields
from odoo import tools
from odoo.http import request
from odoo import SUPERUSER_ID
import time
import traceback
import logging
# import oscg_vendor.models.utility


_logger = logging.getLogger(__name__)

# 報表名稱：上傳SOP文件
#    model ：    iac_sop_attachment
# author : IAC.Laura  20180529



class IacSOPAttachment(models.Model):
    # SOP文件  资料附件
    #  繼承    iac.attachment   Iac附件

    _name = "iac.sop.attachment"
    _description = u"Iac SOP Attachment"

    file_id = fields.Many2one('muk_dms.file', string="Attachment File", index=True)
    description = fields.Char(string='Description')

    time_sensitive = fields.Boolean(related='type.time_sensitive', string='Time Sensitive')
    group = fields.Selection(string='Group', selection='_selection_subgroup', required=True,
                             default="sop")  # basic：基本资料的附件；bank：银行资料的附件
    upload_date = fields.Date(string="Upload Date")  # 上传日期
    expiration_date = fields.Date(string="Expiration Date")  # 失效日期
    state = fields.Selection([('upload', 'Upload'),('active', 'Active'), ('inactive', 'Inactive')
    ], string='Status', default='upload')
    active = fields.Boolean(string="Active", default=True)
    memo = fields.Text(string='Memo')
    vendor_id = fields.Many2one("iac.vendor", String="Vendor") # , readonly = True
    approver_id = fields.Many2one('res.users', string='Approve User')
    module = fields.Selection(string='Module', selection='_selection_module', required=True)    #屬於哪一個'模塊'下的資料
    user = fields.Selection([('external', 'external user'), ('internal', 'internal user')], string='user')

    type = fields.Many2one('iac.attachment.type', string="Attachment Type", required=True, index=True)


    @api.model
    def _selection_subgroup(self):
        res_group = []
        group_list = self.env['ir.config_parameter'].search(
                      [('key', 'like', 'doc_config_group_sop')])  #只能看到'sop'那組
        for item in group_list:
            res_group.append((item.key[17:], _(item.value)))

        return res_group

    # 屬於哪一個'模塊'下的資料
    @api.model
    def _selection_module(self):
        # print '*65:', self._name  #抓到該模型名稱
        res_module = []
        module_list = self.env['ir.config_parameter'].search([('key', 'like', 'doc_sop_module_')])
        for item in module_list:
            res_module.append((item.key[15:], _(item.value)))

        return res_module

# 報表： 繼承 model & data from iac.sop.attachment
class IacSOPAttachmentReport(models.Model):
    _inherit="iac.sop.attachment"
    _name='iac.sop.attachment.report'
    _table='iac_sop_attachment'
    _description = u"Sop Report"
