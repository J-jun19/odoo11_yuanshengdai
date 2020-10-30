# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
import  traceback
import threading
import types

class ChangePoBuyerCode(models.Model):
    """
    用来规避记录规则的模型,不要附加记录规则
    """
    _name = "iac.purchase.order.buyer.code.change.log"

    order_id = fields.Integer()
    ori_buyer_code = fields.Char()
    new_buyer_code = fields.Char()
    change_by = fields.Many2one('res.users',readonly=True)
    change_on = fields.Datetime()
    flag = fields.Char()
    message = fields.Char()
    po_no = fields.Char()

class IacPOBuyerCodeChangeWizard(models.TransientModel):
    _name = 'iac.po.buyer.code.change.wizard'

    original_purchase_group = fields.Many2one('buyer.code')
    new_purchase_group = fields.Many2one('buyer.code')
    list_of_po_need_to_be_changed = fields.Text()

    @api.multi
    def search_po_buyer_code_change(self):
        self.ensure_one()  # 检验某数据集是否只包含单条数据，如果不是则报错

        lt_ori_code = ''
        lt_new_code = ''
        lt_user_id = self._uid
        part_no_list = []
        lt_flag = ''
        lt_message = ''
        for wizard in self:
            if wizard.original_purchase_group:
                lt_ori_code = wizard.original_purchase_group.buyer_erp_id
            if wizard.new_purchase_group:
                lt_new_code = wizard.new_purchase_group.buyer_erp_id
            if wizard.list_of_po_need_to_be_changed:
                part_no_list = wizard.list_of_po_need_to_be_changed.split('\n')
        result_ids = []
        for num in range(len(part_no_list)):

                # 呼叫sp proc_report_vendor_terms_change_history，傳入參數，取得id
            self.env.cr.execute('select v_id from public.proc_update_po_buyer_code'
                                ' (%s,%s,%s,%s) as (v_id int8)',
                                (part_no_list[num], lt_ori_code,lt_new_code,
                                 lt_user_id))

            result_change_log = self.env.cr.fetchall()

            for result_change_log_wa in result_change_log:
                result_ids.append(result_change_log_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('buyer code change log'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.purchase.order.buyer.code.change.log'
        }
        return action

