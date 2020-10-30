# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json
from datetime import datetime, timedelta
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


class IacPurchaseOrderLineVendorUnconfirm(models.Model):
    """PO Line从表"""
    _name = "iac.purchase.order.line.vendor.unconfirm.stat"
    _inherit = "iac.purchase.order.line"
    _table="iac_purchase_order_line"
    _description = u"PO Line订单"
    _order = 'id desc, name'

    @api.depends('last_change_date')
    def _taken_date_range(self):
        for change_line in self:
            time_delta=fields.Datetime.now()-fields.Datetime.from_string(change_line.last_change_date)
            change_line.date_range=time_delta.days

    increase_qty = fields.Float(related='last_order_line_change_id.increase_qty', string="Increase Quantity", readonly=True)
    decrease_qty = fields.Float(related='last_order_line_change_id.decrease_qty', string="Increase Quantity", readonly=True)
    cancel_qty = fields.Float(related='last_order_line_change_id.cancel_qty', string="Cancel Quantity", readonly=True)
    last_change_date=fields.Datetime(related='last_order_line_change_id.write_date', string="Last Change Date", readonly=True)
    date_range=fields.Integer(string="Date Range", default=_taken_date_range)
    order_date=fields.Date(related='order_id.order_date', string="PO Date", readonly=True)
    vendor_code=fields.Char(related='order_id.vendor_id.vendor_code', string="Vendor Code", readonly=True)
    vendor_name=fields.Char(related='order_id.vendor_id.name', string="Vendor Name", readonly=True)
    division_code=fields.Char(related='part_id.division', string="Division Code", readonly=True)
    part_no=fields.Char(related='part_id.part_no', string="Part No", readonly=True)
    part_description=fields.Char(related='part_id.part_description', string="Part Description", readonly=True)
    plant_code=fields.Char(related='vendor_id.plant.plant_code', string="Plant", readonly=True)

    price=fields.Float(related='last_order_line_change_id.new_price', string="Price", readonly=True)
    price_unit=fields.Integer(related='last_order_line_change_id.price_unit', string="Price Unit", readonly=True)
    currency=fields.Char(related='order_id.currency', string="Currency", readonly=True)
    buyer_erp_id=fields.Char(related='order_id.buyer_erp_id', string="Purchasing Group", readonly=True)
    change_state=fields.Selection(related='last_order_line_change_id.change_state', string="Change State", readonly=True)



