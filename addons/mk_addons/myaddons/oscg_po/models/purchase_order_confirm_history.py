# -*- coding: utf-8 -*-
import threading
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval
from odoo.modules.registry import RegistryManager
import odoo
_logger = logging.getLogger(__name__)

class IacPurchaseOrderConfirmHistory(models.Model):
    """PO 的操作日志报表用途"""
    _name = "iac.purchase.order.confirm.history"
    _description = u"PO Confirm History"
    _order = 'id desc'

    #中间表字段
    order_code=fields.Char(string="Purchase Order Code")
    order_line_code=fields.Char(string="Purchase Order LIne Code")
    vendor_code=fields.Char(string="Vendor Code")
    part_no=fields.Char(string="Part No")
    plant_code=fields.Char(string="Plant")
    buyer_code=fields.Char(string="Buyer Code")
    division_code=fields.Char(string="Division Code")
    ori_qty=fields.Float(string="Ori Quantity",digits=(18,4))
    new_qty=fields.Float(string="New Quantity",digits=(18,4))
    ori_price =fields.Float(string="Price",digits=(18,4))
    new_price =fields.Float(string="Price",digits=(18,4))
    ori_price_unit=fields.Integer(string="Ori Price Unit")
    new_price_unit=fields.Integer(string="New Price Unit")
    currency =fields.Char(string="Currency Name")
    last_update_date=fields.Datetime(string="Last Update Date")
    vendor_confirm_flag=fields.Boolean(string="Vendor Confirm Flag")#标识Vendor 是否确认订单变更信息
    vendor_exception_reason=fields.Text(string="Vendor Exception Reason")
    delivery_date = fields.Date(string="Delivery Date")#交期
    vendor_delivery_date = fields.Date(string="Vendor Delivery Date")  # Vendor确认的交期
    ori_deletion_flag = fields.Boolean(string='Ori Deletetion Flag')#初始删除标记
    new_deletion_flag = fields.Boolean(string='New Deletetion Flag' )#变更后删除标记

    #附加关联字段
    vendor_id = fields.Many2one('iac.vendor', string="Plant Id", index=True)
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Order Line Id", index=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant Id", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    division_id = fields.Many2one('division.code', string="Division Info", index=True)
    source_code =fields.Char(string="Source Code")
    currency_id = fields.Many2one('res.currency', string="Currency Info", index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")


