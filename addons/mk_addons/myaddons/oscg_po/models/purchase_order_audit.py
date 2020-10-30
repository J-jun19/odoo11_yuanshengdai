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


class IacPurchaseOrderAudit(models.Model):
    """PO 的操作日志报表用途"""
    _name = "iac.purchase.order.audit"
    _description = u"PO Audit Log"
    _order = 'name asc'

    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_change_id = fields.Many2one('iac.purchase.order.change', string="Purchase Order Change", index=True)
    order_code = fields.Char(string="Purchase Order",  index=True)
    user_login_code = fields.Char(string="User Login Code", index=True)
    user_id = fields.Many2one('res.users', string="User Info", index=True)
    op_date=fields.Datetime(string='Op Date Time',default=fields.Datetime.now())
    action_type=fields.Selection([("new_po_imported","New PO Imported"),
                                  ("po_change","PO Change"),
                                  ("webflow_error","Webflow Error"),
                                  ("send_to_webflow","Send To Webflow"),
                                  ("approved_by_webflow","Approved By Webflow"),
                                  ("denied_by_webflow","Denied By Webflow"),
                                  ("webflow_call_back","Webflow Call Back"),  #200512 ning add
                                  ("send_to_sap","Send To SAP"),
                                  ("send_sap_error","Send SAP Error"),
                                  ("vendor_exception","Vendor Exception"),
                                  ("vendor_confirmed","Vendor Confirmed"),
                                  ('wait_vendor_confirm', 'Wait Vendor Confirm'),
                                 ],string="Action Type")
    rel_data=fields.Char(string="Rel Data")
    comment=fields.Char(string="Comments")
    order_change_id=fields.Many2one('iac.purchase.order.change',string="Po Change")
    ori_payment_term = fields.Many2one('payment.term',  string='Original Payment Term')
    ori_incoterm_id = fields.Many2one('incoterm',  string='Original Incoterm')
    ori_incoterm1 = fields.Char( string="Original Incoterm Destination")

    new_payment_term = fields.Many2one('payment.term', string='New Payment Term')
    new_incoterm = fields.Many2one('incoterm', string='New Incoterm')
    new_incoterm1 = fields.Char(string="New Incoterm Destination")
    state_msg = fields.Char(string="Status Message")
    audit_source=fields.Selection([('po_new','PO New'),('po_change','PO Change')],string="Audit Source")


class IacPurchaseOrderLineAudit(models.Model):
    """PO 的操作日志报表用途"""
    _name = "iac.purchase.order.line.audit"
    _description = u"PO Line Audit Log"
    _order = 'name asc'

    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Purchase Order Line", index=True)
    order_line_change_id = fields.Many2one('iac.purchase.order.line.change', string="Purchase Order Line Change", index=True)
    currency_id = fields.Many2one('res.currency', string="Currency Info", index=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant Id", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Plant Id", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    part_id = fields.Many2one('material.master.po.line', 'Part No', index=True)#物料
    division_id = fields.Many2one('division.code', string="Division Info", index=True)
    source_code =fields.Char(string="Source Code")
    currency_id = fields.Many2one('res.currency', string="Currency Info", index=True)

    order_code = fields.Char(string="Purchase Order Code",  index=True)
    order_line_code = fields.Char(string="Purchase Order Line Code",  index=True)
    user_login_code = fields.Char(string="User Login Code", index=True)
    user_id = fields.Many2one('res.users', string="User Info", index=True)
    op_date=fields.Datetime(string='Op Date Time',default=fields.Datetime.now())
    action_type=fields.Selection([("new_po_imported","New PO Imported"),
                                  ("po_change","PO Change"),
                                  ("webflow_error","Webflow Error"),
                                  ("send_to_webflow","Send To Webflow"),
                                  ("approved_by_webflow","Approved By Webflow"),
                                  ("denied_by_webflow","Denied By Webflow"),
                                  ("send_to_sap","Send To SAP"),
                                  ("send_sap_error","Send SAP Error"),
                                  ("vendor_exception","Vendor Exception"),
                                  ("vendor_confirmed","Vendor Confirmed"),
                                  ('wait_vendor_confirm', 'Wait Vendor Confirm'),
                                 ],string="Action Type")
    vendor_code=fields.Char(string="Vendor Code")
    part_no=fields.Char(string="Part No")
    plant_code=fields.Char(string="Plant")
    buyer_code=fields.Char(string="Buyer Code")
    division_code=fields.Char(string="Division Code")
    ori_qty=fields.Float(string="Ori Quantity",digits=(18,4))
    new_qty=fields.Float(string="New Quantity",digits=(18,4))
    ori_price =fields.Float(string="Ori Price",digits=(18,4))
    new_price =fields.Float(string="New Price",digits=(18,4))
    ori_price_unit=fields.Integer(string="Ori Price Unit")
    new_price_unit=fields.Integer(string="New Price Unit")
    currency =fields.Char(string="Currency Name")
    vendor_exception_reason=fields.Text(string="Vendor Exception Reason")
    ori_delivery_date = fields.Date(string="Ori Delivery Date")#交期
    new_delivery_date = fields.Date(string="New Delivery Date")#交期
    vendor_delivery_date = fields.Date(string="Vendor Delivery Date")  # Vendor确认的交期
    ori_deletion_flag = fields.Boolean(string='Ori Deletion Flag')#初始删除标记
    new_deletion_flag = fields.Boolean(string='New Deletion Flag' )#变更后删除标记
    audit_source=fields.Selection([('po_new','PO New'),('po_change','PO Change')],string="Audit Source")
    state_msg=fields.Text(string="State Message")

