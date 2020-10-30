# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types, json

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


class IacPurchaseOrderMassWizard(models.TransientModel):
    """多笔变更查询po向导
    日期选择条件：
    	Delivery date base
    	PO date base（RFQ生效后的PO）
    	PO date base（all open PO）
    	Delivery date base + PO date base（RFQ生效后的PO）
    	Delivery date base + PO date base（all open PO）
    """
    _name = 'iac.purchase.order.mass.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    part_id = fields.Many2one('material.master.po.line', 'Part No')
    division_id = fields.Many2one('division.code', string='Division Info')
    order_code = fields.Char(string="Purchase Order")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    date_base = fields.Selection([('po_date_base_all_open_po', u'PO date base（all open PO）'),
                                  ('delivery_date_base', 'Delivery date base'),
                                  ('po_date_base', u'PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base',
                                   u'Delivery date base + PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base_all_open_po',
                                   u'Delivery date base + PO date base（all open PO）')
                                 ], default='po_date_base_all_open_po', string="Price Date Base")

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        self.part_id = False
        self.vendor_id = False

    @api.multi
    def search_purchase_orders(self):
        """
        这里用存储过程实现,原有的代码废除
        :return:
        """
        result = []
        ##根据界面中选择的条件,生成参数sql
        param_sql = ''
        for wizard in self:
            if wizard.part_id.id != False:
                param_sql += ' and po_line.part_id=%s' % (wizard.part_id.id,)
            if wizard.plant_id.id != False:
                param_sql += ' and po.plant_id=%s' % (wizard.plant_id.id,)
            if wizard.vendor_id.id != False:
                param_sql += ' and po.vendor_id=%s' % (wizard.vendor_id.id,)
            if wizard.order_code:
                param_sql += ' and po.document_erp_id=\'%s\'' % (wizard.order_code,)
            if wizard.date_from:
                param_sql += ' and po.order_date>=to_date(\'%s\',\'yyyy-mm-dd hh24:mi:ss\')' % (wizard.date_from,)
            if wizard.date_to:
                param_sql += ' and po.order_date<=to_date(\'%s\',\'yyyy-mm-dd hh24:mi:ss\')' % (wizard.date_to,)

        #增加buyer_id_list 筛选条件
        if len(self.env.user.buyer_id_list)>0:
            buyer_id_list_str=[str(x) for x in self.env.user.buyer_id_list]
            buyer_id_sql_txt=' and po.buyer_id in ('+  ','.join(buyer_id_list_str) + ')'
            param_sql +=buyer_id_sql_txt

        #查询数据库中符合条件的po_line信息,并附加上变价的信息
        self.env.cr.execute("select id from public.proc_get_order_mass(%s, %s)",
                            (param_sql, wizard.date_base))

        result_po_line_id = self.env.cr.fetchall()
        result_ids = []
        for po_line_id in result_po_line_id:
            result_ids.append(po_line_id)
        #action_view_iac_purchase_order_line_mass_change_list
        action = self.env.ref('oscg_po.action_view_iac_purchase_order_line_mass_change_list')
        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'domain': [('id', 'in', result_ids)],
            'view_type': "form",
            'view_mode': "tree",
            'res_model': action.res_model,
            'view_id':  self.env.ref('oscg_po.view_iac_purchase_order_line_mass_change_list').id,
            'search_view_id': self.env.ref("oscg_po.view_search_iac_purchase_order_line_mass_change").id,
            }

        return action_window



class IacPurchaseOrderLineMassChange(models.Model):
    """当前模型用做处理多条po line 变更价格进行拆单的工作
    """
    _name = "iac.purchase.order.line.mass.change"
    _inherit = "iac.purchase.order.line"
    _table = "iac_purchase_order_line"
    _description = "PO Line Mass Change"
    _order = 'id desc'

    @api.multi
    def button_to_update_price(self):
        """通过菜单进行单笔或者多笔批量变更价格"""
        order_id_list = []
        order_line_id_list = []
        for order_line in self:
            if order_line.order_id.state in ['pending','unapproved','vendor_confirmed','vendor_exception','wait_vendor_confirm']:
                order_id_list.append(order_line.order_id.id)
                order_line_id_list.append(order_line.id)

        #删除重复的order_id
        order_change_ids = []
        order_id_list = list(set(order_id_list))

        # 181210暂时注释，先上线授权下单
        #批量获取锁
        # self.env["iac.purchase.order"].try_batch_lock(order_id_list)

        order_change_ids=[]
        for order_id in order_id_list:

            order = self.env["iac.purchase.order"].browse(order_id)
            if not order.history_order_id.exists():
                history_order = order._copy_history_order()
                order.write({'history_order_id': history_order.id})

            #生成order_change,order_change会复制变价相关的4个字段
            order_change = order.generate_order_change()

            order_change.with_context({'po_change_type':'price_change'}).write({"change_type":"po_change_mass",'po_change_type':'price_change'})
            order_change_ids.append(order_change.id)
            #遍历所有order_change中的明细条目处理变价
            for order_line_change in order_change.line_ids:
                #判断是否是需要变更价格的order_line
                if order_line_change.order_line_id.id in order_line_id_list:
                    #获取当前的订单条目的入料信息
                    self.env.cr.execute("SELECT                                     " \
                                        "	o_gr_count,o_asn_count,o_open_count      " \
                                        "FROM                                       " \
                                        "	public.proc_po_part_info (              " \
                                        "		%s,                      " \
                                        "		%s,                      " \
                                        "		%s                       " \
                                        "	)                             ",
                                        (order_line_change.order_id.id, order_line_change.order_line_id.id,
                                         order_line_change.part_id.id,))
                    gr_count=0
                    asn_count=0
                    open_count=0
                    l_gr_asn_count=0
                    part_result=self.env.cr.fetchall()

                    gr_count=part_result[0][0]
                    asn_count=part_result[0][1]
                    open_count=part_result[0][2]

                    #处理特殊情况,没有入料,直接修改价格
                    #培武修改-20180917-begin
                    #1.當ASN和入料都是0時，直接修改價格
                    #2.如果有ASN或者GR時
                    #2.1 ASN+GR >= Original PO line qty，不拆不動
                    #2.2 ASN+GR <  Original PO line qty，拆分item，原Item數量保留ASN+GR數，剩餘數量作為新item數
                    # if gr_count==0:
                    if gr_count==0 and asn_count==0:
                        order_line_change.write({
                            "ori_price":order_line_change.new_price,
                            "new_price":order_line_change.order_line_id.last_price,
                            "last_price_unit":order_line_change.order_line_id.last_price_unit,
                            "item_type":"ori_item",
                            "price_date":fields.date.today(),
                        })
                        continue

                    #入料数量或者ASN數量大于0,并且入料数量+在途ASN數小于订单行中的数量,进行拆单处理
                    l_gr_asn_count = gr_count + asn_count
                    # if gr_count>0 and gr_count<order_line_change.new_qty:
                    #     ori_item_qty=gr_count+asn_count
                    #     new_item_qty=order_line_change.new_qty-ori_item_qty
                    #     new_item_price=order_line_change.last_price

                    if l_gr_asn_count > 0 and l_gr_asn_count < order_line_change.new_qty:
                        ori_item_qty = l_gr_asn_count
                        new_item_qty = order_line_change.new_qty - ori_item_qty
                        new_item_price = order_line_change.last_price

                    # 培武修改-20180917-end
                        #构建新建item的数据信息
                        new_item_vals={
                            "ori_price":order_line_change.new_price,
                            "new_price":order_line_change.order_line_id.last_price,
                            "last_price_unit":order_line_change.order_line_id.last_price_unit,
                            "ori_qty":0,
                            "new_qty":new_item_qty,
                            "item_type":"split_item",
                            "parent_item_id":order_line_change.id,
                            "change_id":order_line_change.change_id.id,
                            "price_date":fields.date.today(),
                            }

                        vals = order_line_change.copy_data(new_item_vals)[0]
                        order_line_change_new = self.env["iac.purchase.order.line.change"].create(vals)
                        #order_line_change_new=order_line_change.copy(new_item_vals)

                        #改写现存项目的数量信息,维持价格不变
                        order_line_change.write({
                            "price_date":fields.date.today(),
                            "new_qty":ori_item_qty,
                            "next_item_id":order_line_change_new.id
                        })

        # 181210暂时注释，先上线授权下单
        #操作处理完成释放po的锁
        # self.env["iac.purchase.order"].release_batch_lock(order_id_list)

        #数据处理完成后应该跳转页面到po change
        action = {
            'domain': [('id', 'in', order_change_ids)],
            'name': _('Purchase Order Change'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iac.purchase.order.change'
        }

        return action