# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


class PurchaseApproveRegular(models.Model):
    """送签规则
    可使用变量：
    {order_amount}：订单总额
    {material_maxprice}：订单明细物料最高价格
    {change_incoterm}：变更incoterm
    {change_payment_term}：变更payment_term
    {price_factor}：价格因子
    {quantity_factor}：数量因子
    {change_delivery}：变更交期
    {item_factor}：PO Line增加或取消因子
    """
    _name = "iac.purchase.approve.regular"
    _order = "plant_id"

    plant_id = fields.Many2one('pur.org.data', string="Plant")
    currency_id = fields.Many2one('res.currency', string="Currency")

    expression = fields.Text(string="Expression")
    approve_role = fields.Text(string="Approve Role")

    #lwt add relation char key fields
    plant_code=fields.Char(string="Plant")
    currency_name=fields.Char(string="Currency Name")
    division_code=fields.Char(string="Division Code")
    rule_type = fields.Selection([
                                     ('po', 'For Order'),
                                     ('po_line', 'For Order Line Item'),

                                     ], default='po', string="Rule Type")

    @api.model
    def create(self, values):
        approve_regular = super(PurchaseApproveRegular, self).create(values)
        char_key_vals={
            "plant_code":approve_regular.plant_id.plant_code,
            "currency_name":approve_regular.currency_id.name,
            }
        super(PurchaseApproveRegular, approve_regular).write(char_key_vals)
        return approve_regular

    @api.multi
    def write(self, values):
        result = super(PurchaseApproveRegular, self).write(values)
        char_key_vals={
            "plant_code":self.plant_id.plant_code,
            "currency_name":self.currency_id.name,
            }
        super(PurchaseApproveRegular, self).write(char_key_vals)
        return result

        #action = self.env.ref('oscg_po.action_view_purchase_approve_record_view_form')
        #return {
        #    'name': action.name,
        #    'help': action.help,
        #    'type': action.type,
        #    'view_type': action.view_type,
        #    'view_mode': action.view_mode,
        #    'target': action.target,
        #    #'context': "{'default_product_id': " + str(product_ids[0]) + "}",
        #    'res_model': action.res_model,
        #    #'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],
        #    }
    #
    #return result


class PurchaseApproveRecord(models.Model):
    _name = "iac.purchase.approve.record"
    _order = 'id desc'

    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order")
    order_change_id = fields.Many2one('iac.purchase.order.change', string="Order Change Info")
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Order Line Info")
    regular_id = fields.Many2one('iac.purchase.approve.regular', string="Regular")
    expression = fields.Text(string="Expression")
    order_amount = fields.Float(string='Order Amount')
    material_maxprice = fields.Float(string='Price')
    change_incoterm = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Change Incoterm")
    change_payment_term = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Change Payment Term")
    price_factor = fields.Selection([('up', 'Up'), ('down', 'Down'),('equal','Price Equal')], string="Price Up or Down")
    quantity_factor = fields.Selection([('up', 'Up'), ('down', 'Down'),('equal','Quantity Equal')], string="quantity Up or Down")
    change_delivery = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Change Delivery")
    item_factor = fields.Selection([('add', 'Add'), ('cancel', 'Cancel')], string="Add or Cancel Item")
    error_flag = fields.Selection([('Y', 'Yes'), ('N', 'No')], string="Current rule is error",default="N")
    rule_type = fields.Selection([('order', 'Order Rule'), ('order_item', 'Order Item Rule')], string="Rule Type",default="order")
    approve_role = fields.Text(related="regular_id.approve_role", string="Approve Role")
    memo = fields.Text(string="Memo")
