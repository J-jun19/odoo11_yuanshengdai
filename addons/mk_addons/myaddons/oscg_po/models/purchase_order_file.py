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


class IacPurchaseOrderFile(models.Model):
    """PO 的文件列表模型"""
    _name = "iac.purchase.order.file"
    _description = 'Purchase Order File'
    _inherits = {'muk_dms.file': 'file_id'}
    _order = 'id desc'

    file_id=fields.Many2one('muk_dms.file',string='File Info',required=True,ondelete='cascade',index=True)
    order_id=fields.Many2one('iac.purchase.order',string='Order Info',index=True)

    def button_to_unlink(self):
        if self.order_id.state in ['to_approve','to_change']:
            raise UserError("Can not delete file when order state is to_approve or to_change")

        action = self.env.ref('oscg_po.action_view_po_view_form')
        order_id = self.order_id.id
        self.unlink()
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'domain':action.domain,
            #'context': "{'default_order_id': " + str(order_id) + "}",
            'res_model': action.res_model,
            'res_id':order_id,
            }


    @api.multi
    def button_to_return(self):
        """返回到po change form"""
        action = self.env.ref('oscg_po.action_view_po_view_form')
        order_id = self.order_id.id

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'domain':action.domain,
            #'context': "{'default_order_id': " + str(order_id) + "}",
            'res_model': action.res_model,
            'res_id':order_id,
            }