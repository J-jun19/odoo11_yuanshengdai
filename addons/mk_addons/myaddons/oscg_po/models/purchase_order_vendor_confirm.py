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


class IacPurchaseOrderVendorConfirm(models.Model):
    """PO 主表"""
    _name = "iac.purchase.order.vendor.confirm"
    _inherit = "iac.purchase.order"
    _table="iac_purchase_order"
    _description = "Purchase Order"
    _order = 'document_erp_id desc'

    order_line = fields.One2many("iac.purchase.order.line.vendor.confirm", "order_id", string="PO Line Number")

    @api.one
    def button_set_all_exception(self):
        """
        遍历当前订单的条目，对所有的条目设置成为 Vendor Exception
        :return:
        """
        for order_line in self.order_line:
            order_line.with_context(state_change=True).write({"state":"vendor_exception"})

    @api.one
    def button_set_all_confirm(self):
        """
        遍历当前订单的条目，对所有的条目设置成为Vendor Confirm
        :return:
        """
        for order_line in self.order_line:
            order_line.with_context(state_change=True).write({"state":"vendor_confirmed"})

    @api.one
    def button_set_to_confirm(self):
        """
        遍历当前订单的条目，判断选中状态,对所有选中的条目设置成为Vendor Confirm
        :return:
        """
        for order_line in self.order_line:
            if order_line.selection_flag==True:
                order_line.with_context(state_change=True).write({"state":"vendor_confirmed"})

    @api.one
    def button_set_to_exception(self):
        """
        遍历当前订单的条目，判断选中状态,对所有选中的条目设置成为Vendor Exception
        :return:
        """
        for order_line in self.order_line:
            if order_line.selection_flag==True:
                order_line.with_context(state_change=True).write({"state":"vendor_exception"})

    @api.multi
    def button_to_submit(self):
        #进行数据检查,检查交期和exception 信息
        for order in self:
            for order_line in order.order_line:
                if order_line.state=='wait_vendor_confirm':
                    raise UserError("order code is %s ,order line code is %s need to be confirmed" %(order.document_erp_id,order_line.document_line_erp_id,))
                if order_line.state=='vendor_exception' and order_line.vendor_exception_reason==False:
                    raise UserError("order code is %s ,order line code is %s need to set exception reason" %(order.document_erp_id,order_line.document_line_erp_id,))
                if order_line.state=='vendor_exception' and order_line.vendor_delivery_date==False:
                    raise UserError("order code is %s ,order line code is %s need to set vendor delivery date" %(order.document_erp_id,order_line.document_line_erp_id,))

        #更改订单状态,并且导航到相关页面
        #情况1,存在 vendor_exception
        for order in self:

            #判断所有订单项目的状态
            self.env.cr.execute("""
             select state,count(*) state_count from iac_purchase_order_line t where order_id=%s group by state
            """,(order.id,))
            state_result=self.env.cr.dictfetchall()
            dict_state={}
            #组装一个dict,以状态名称为key ,状态对应的记录条目数量为值
            for state_line in state_result:
                state_name=state_line.get("state")
                state_count=state_line.get("state_count")
                dict_state[state_name]=state_count

            #如果一个条目被确认，那么比较这个订单条目曾经被确认过,为报表提供数据支持
            po_line_list=self.env["iac.purchase.order.line"].search([('order_id','=',self.id),('state','=','vendor_confirmed')])
            if po_line_list.exists():
                po_line_list.with_context(state_change=True).write({"ever_confirmed":True})

            #情况1,存在 vendor_exception
            #情况2,存在 wait_vendor_confirm
            #情况3,全部状态为vendor_confirmed
            po_line_list=self.env["iac.purchase.order.line"].search([('order_id','=',self.id),('state','=','vendor_exception')],limit=1)


            #根据订单条目的状态来写订单头状态
            #只要存在未确认的条目,那么订单头的状态就是 wait_vendor_confirm
            #if "wait_vendor_confirm" in dict_state:
            #    order.write({"state":"wait_vendor_confirm"})
            #else:
            #    #不存在wait_vendor_confirm 的状态情况下,判断是否存在vendor_exception
            #    if "vendor_exception" in dict_state:
            #        order.write({"state":"vendor_exception"})
            #    else:
            #        #不存在wait_vendor_confirm和vendor_exception,那么可以确定所有条目都被confirm
            #        order.write({"state":"vendor_confirmed"})

            po_state=''
            if "vendor_exception" in dict_state:
                order.write({"state":"vendor_exception"})
                po_state="vendor_exception"
            else:
                po_state="vendor_confirmed"
                order.write({"state":"vendor_confirmed"})

            if order.state=="vendor_confirmed":
                # 200505 ning add begin
                if order.need_unconfirm == True:
                # end
                    self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data_confirmed(order.id)
            else:#vendor_exception
                # 200505 ning add begin
                if order.need_unconfirm == True:
                # end
                    self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data_exception(order.id)

				
            #生成po稽核信息
            order_audit_vals={
                "order_id":order.id,
                "order_code":order.document_erp_id,
                "action_type":order.state,
                "user_id":self.env.user.id,
                "user_login_code":self.env.user.login,
                }
            self.env["iac.purchase.order.audit"].sudo().create(order_audit_vals)

            #记录order_line日志,记录vendor_confirm状态
            for order_line in order.order_line:
                order_line.apply_po_line_audit()

        vals = {
            'action_type': 'Vendor Confirm PO',
            'vendor_id':self.vendor_id.id
        }
        self.env['iac.supplier.key.action.log'].create(vals)
        self.env.cr.commit()
        #跳转页面到当前视图的Tree 视图
        action = self.env.ref('oscg_po.action_view_po_vendor_confirm_list')

        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': "form",
            'view_mode': "tree,form",
            'target': action.target,
            'domain':action.domain,
            'res_model': action.res_model,
            'search_view_id': self.env.ref("oscg_po.view_iac_purchase_order_vendor_confirm_search").id,
        }

        view_id_list=[]
        form_view=self.env.ref("oscg_po.view_po_vendor_confirm_form")
        tree_view=self.env.ref("oscg_po.view_po_vendor_confirm_list")
        form_view_item={
            "view_mode":"form",
            "view_id":form_view.id,
            }

        tree_view_item={
            "view_mode":"tree",
            "view_id":tree_view.id,
            }

        view_id_list.append((0,0,form_view_item))
        view_id_list.append((0,0,tree_view_item))
        action_window["view_ids"]=view_id_list

        return action_window


class IacPurchaseOrderLineVendorConfirm(models.Model):
    """PO Line从表"""
    _name = "iac.purchase.order.line.vendor.confirm"
    _inherit = "iac.purchase.order.line"
    _table="iac_purchase_order_line"
    _description = u"PO Line订单"
    _order = 'id desc, name'

    order_id = fields.Many2one('iac.purchase.order.vendor.confirm', string="Purchase Order", index=True)
    selection_flag = fields.Boolean(string='Select', default=False)#选中标记
    state = fields.Selection([
                                 ('wait_vendor_confirm', 'Wait Vendor Confirm'),
                                 ('vendor_confirmed', 'Vendor Confirmed'),  # vendor confirmed
                                 ('vendor_exception', 'Vendor Exception'),  # vendor exception
                             ], default='pending', string="Vendor Confirmed State")

    @api.one
    def button_to_toggle(self):
        if self.state == 'wait_vendor_confirm':
            self.with_context(state_change=True).write({'state': 'vendor_confirmed'})
        elif self.state=='vendor_confirmed':
            self.with_context(state_change=True).write({'state': 'vendor_exception'})
        elif self.state=='vendor_exception':
            self.with_context(state_change=True).write({'state': 'wait_vendor_confirm'})

    @api.one
    def button_to_confirm(self):
        if self.state == 'wait_vendor_confirm' or self.state == 'vendor_exception':
            self.with_context(state_change=True).write({'state': 'vendor_confirmed'})

    @api.one
    def button_to_exception(self):
        if self.state == 'wait_vendor_confirm' or self.state=='vendor_confirmed':
            self.with_context(state_change=True).write({'state': 'vendor_exception'})



class IacPurchaseOrderBuyerConfirm(models.Model):
    """PO 主表"""
    _name = "iac.purchase.order.buyer.confirm"
    _inherit = "iac.purchase.order"
    _table="iac_purchase_order"
    _description = "Purchase Order"
    _order = 'id desc, name'
    order_line = fields.One2many("iac.purchase.order.line.buyer.confirm", "order_id", string="PO Line Number")

    @api.multi
    def button_submit_to_sap(self):
        if self.state == 'vendor_exception':
            self.write({'state': 'vendor_confirmed'})
            order_change=self.generate_order_change()
            #为exception 的订单条目设置交期
            for order_line_change in order_change.line_ids:
                if order_line_change.order_line_id.state=="vendor_exception":
                    order_line_change.write({"new_delivery_date":order_line_change.order_line_id.vendor_delivery_date,
                                             "state":"vendor_exception",
                    })
            #调用SAP接口更新数据
            # 调用SAP接口
            biz_object = {
                "id": order_change.id,
                "biz_object_id": order_change.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_PO_002", biz_object)
            try:
                if rpc_result:
                    # 根据order change更新order
                    self.apply_po_change_data(order_change)

                    #操作成功的情况下,修改记录状态
                    proc_result=True
                    order_change.write({"state":"vendor_confirmed"})
                    self.write({"state":"vendor_confirmed"})
                else:
                    order_change.write({'state_msg': u'通知SAP失败'})

            except:
                order_change.unlink()
                traceback.print_exc()
        return True

    @api.multi
    def button_send_back_to_vendor(self):
        if self.state == 'vendor_exception':
            self.write({'state': 'wait_vendor_confirm'})
        return True


class IacPurchaseOrderLineBuyerConfirm(models.Model):
    """PO Line从表"""
    _name = "iac.purchase.order.line.buyer.confirm"
    _inherit = "iac.purchase.order.line"
    _description = u"PO Line订单"
    _order = 'id desc, name'
    _table="iac_purchase_order_line"
    order_id = fields.Many2one('iac.purchase.order.buyer.confirm', string="Purchase Order", index=True)
