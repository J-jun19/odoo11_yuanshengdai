# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json
import math
import utility

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

class IacDeliverySchedule(models.Model):
    """
    PO Line Delivery从表
    """
    _name = "iac.delivery.schedule"
    _description = "Delivery Schedule"

    order_id = fields.Many2one('iac.purchase.order', related='order_line_id.order_id', string="Purchase Order")
    order_line_id = fields.Many2one('iac.purchase.order.line', string="PO Line Number")
    sequence = fields.Integer(string="Schedule#", default=1)
    qty_received = fields.Float(string='Received Quantity')
    delivery_date = fields.Date(string="Delivery Date")  # 当前行料号该schedule的交期
    quantity = fields.Float(string='Quantity')  # 当前行料号该schedule的数量


class IacPurchaseOrderChange(models.Model):
    """PO Change主表
    PO可以多次change
    """
    _name = "iac.purchase.order.change"
    _description = "PO Change"
    _order = 'id desc'

    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    slocation_id = fields.Many2one(related='order_id.storage_location_id', string='storage location')

    order_code = fields.Char(string='Purchase Order', readonly=True)
    order_date = fields.Date(string='PO Date', readonly=True)
    order_amt = fields.Float(string='Order Amount', compute='_taken_order_amount')
    currency_id = fields.Many2one('res.currency',  string="Currency", readonly=True)

    vendor_id = fields.Many2one('iac.vendor',  string="Vendor Info", index=True)
    vendor_code = fields.Char( string="Vendor Code", readonly=True)
    vendor_name = fields.Char( string="Vendor Name", readonly=True)
    ori_payment_term = fields.Many2one('payment.term',  string='Original Payment Term')
    ori_incoterm_id = fields.Many2one('incoterm',  string='Original Incoterm')
    ori_incoterm1 = fields.Char( string="Original Incoterm Destination")

    new_payment_term = fields.Many2one('payment.term', string='New Payment Term')
    new_incoterm = fields.Many2one('incoterm', string='New Incoterm')
    new_incoterm1 = fields.Char(string="New Incoterm Destination")
    order_reason = fields.Char(string="Order Reason")
    version_no = fields.Char(string="Version No")
    # 从模型
    line_ids = fields.One2many('iac.purchase.order.line.change', 'change_id', string='Change Order Lines')
    state = fields.Selection([
                                 ('pending', 'Pending'),
                                 ('to_change', 'To Change'),#生成了po_change数据
                                 ('webflow_error', 'Webflow Error'),  # CALL webflow失败
                                 ('to_approve', 'To Approve'),# buyer review后提交webflow签核，送签
                                 ('unapproved', 'Unapproved'),# webflow拒绝或抽单
                                 ('to_sap', 'To SAP'), # webflow签核通过，call sap
                                 ('sap_error', 'SAP Error'),  # CALL SAP失败
                                 ('wait_vendor_confirm', 'Wait Vendor Confirm'),  # SAP更新数据完成,等待vendor confirm
                                 ('vendor_confirmed', 'Vendor Confirmed'),  # vendor confirmed
                                 ('vendor_exception', 'Vendor Exception'),  # vendor exception
                                 ('erp_accepted', 'Erp Accepted'),  # PO Change 结束
                                 ('cancel', 'Cancelled'), # 表单取消
                             ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")
    order_reason = fields.Text(string="Order Reason")
    approve_role_list = fields.Char(string="Approve Role List")
    webflow_number=fields.Char(string="Webflow Number")
    manually_po_reason_type = fields.Char(string="Manually Po Reason Type")
    manually_po_comment = fields.Text(string="Manually PO Comment")
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code Info", index=True)
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)
    change_type=fields.Selection([('po_change_single','Single Change'),('po_change_mass','Mass Change')],string="Change Type",default="po_change_single",index=True)
    #数据迁移索要使用的字段
    plant_code=fields.Char(string="Plant",index=True)
    currency_name=fields.Char(string="Currency Name",index=True)
    new_incoterm_code=fields.Char(string="New Incoterm Code",index=True)
    ori_incoterm_code=fields.Char(string="Ori Incoterm Code",index=True)
    new_payment_term_code=fields.Char(string="New Payment Term Code",index=True)
    ori_payment_term_code=fields.Char(string="Ori Payment Term Code",index=True)
    po_code=fields.Char(string="Order Code",index=True)
    po_vendor_code=fields.Char(string="Vendor Code",index=True)
    po_change_type = fields.Selection([('new_po', 'New PO'),
                                    ('price_change', 'Price change'),
                                    ('quantity_change', 'Quantity change'),
                                    ('quantity_and_price_change', 'Quantity and Price change'),
                                    ('no_change', 'No change')])#新增字段，根据po change type来分组

    @api.one
    @api.constrains('line_ids')
    def uniq_check_po_change(self):
        """
        对po_change 进行校验,遍历所有条目判断是否存在数量大于初始的数量
        校验总量是否大于初始的总量
        :return:
        """

        his_qty_map=self.order_id.get_part_qty_map()
        self.env.cr.execute('select document_line_erp_id,quantity  from iac_purchase_order_line_history  t where t.order_id=%s ',
                            (self.order_id.id,))
        result_list=self.env.cr.fetchall()
        his_qty_map={}
        for po_line_no,qty in result_list:
            his_qty_map[po_line_no]=qty

        #校验条目的数量是否超过初始订单条目的数量
        #for change_line in self.line_ids:
        #    if change_line.order_line_code not in his_qty_map or change_line.odoo_deletion_flag==True:
        #        continue
        #    if change_line.new_qty>his_qty_map[change_line.order_line_code]:
        #        raise UserError("Order Line No is %s quantity is greater than quantity in   history order list!" %(change_line.order_line_code,))

        #获取历史记录中的分料号总量
        self.env.cr.execute('select part_id,COALESCE(sum(quantity),0)  from iac_purchase_order_line_history  t where t.order_id=%s  group by part_id',
                            (self.order_id.id,))
        result_list=self.env.cr.fetchall()
        his_part_qty_map={}
        for part_id,qty in result_list:
            his_part_qty_map[part_id]=qty

        self.env.cr.execute("select part_id,sum(new_qty) from iac_purchase_order_line_change where odoo_deletion_flag=False " \
                                " and change_id=%s group by part_id",(self.id,))
        result_list=self.env.cr.fetchall()
        change_part_qty_map={}
        for part_id,qty in result_list:
            change_part_qty_map[part_id]=qty

        #校验订单条目数据,修改后的总量不能大于初始版本中的分材料总量
        for part_id in change_part_qty_map:
            if part_id not in his_part_qty_map:
                part_rec=self.env['material.master.po.line'].browse(part_id)
                raise UserError("Part No is %s not existed in history order list!"%(part_rec.part_no))

            if change_part_qty_map[part_id]>his_part_qty_map[part_id]:
                part_rec=self.env['material.master.po.line'].browse(part_id)
                raise UserError('Part No is %s quantity is greater than quantity in   history order list!'%(part_rec.part_no))


    @api.model
    def create(self, values):
        order_change = super(IacPurchaseOrderChange, self).create(values)

        for line in order_change.line_ids:

            if line.add_item_reason == 'cost down':
                line.write({'new_qty': line.gr_qty + line.on_road_qty})
                copy_line = line.copy()
                copy_line['ref_line_id'] = line.id
                copy_line['new_price'] = line.add_item_price
                copy_line['new_qty'] = line.open_qty
                copy_line['add_item_reason'] = 'cost down'

                line.create(copy_line)
            elif line.add_item_reason == 'cost up':
                line.write({'new_qty': line.gr_qty + line.on_road_qty})
                copy_line = line.copy()
                copy_line['ref_line_id'] = line.id
                copy_line['new_price'] = line.add_item_price
                copy_line['new_qty'] = line.open_qty
                copy_line['add_item_reason'] = 'cost up'

                line.create(copy_line)
            elif line.add_item_reason == 'change delivery':
                line.write({'new_qty': line.ori_qty - line.add_item_qty})
                copy_line = line.copy()
                copy_line['ref_line_id'] = line.id
                copy_line['new_qty'] = line.add_item_qty
                copy_line['new_delivery_date'] = line.add_item_delivery
                copy_line['add_item_reason'] = 'change delivery'

                line.create(copy_line)
        order_change.uniq_check_po_change()
        return order_change


    def _taken_order_amount(self):
        for change in self:
            order_amount = 0
            for line in change.line_ids:
                order_amount = order_amount + line.line_amount
            change.order_amt = order_amount

    @api.multi
    def button_to_get_approve_list(self):
        """通过菜单进行单笔或者多笔送签"""
        for order_change in self:
            #获取po的审核角色列表
            proc_result,approve_role_list,approve_rule_list,proc_ex_list=order_change._get_po_change_approve_list()
            if len(proc_ex_list)>0:
                result = super(IacPurchaseOrderChange, order_change).write({"state_msg": False, 'approve_role_list': approve_role_list})
            else:
                result = super(IacPurchaseOrderChange, order_change).write({"state_msg":False,'approve_role_list':approve_role_list})

    @api.multi
    def button_to_approve(self):
        """送签"""

        for order_change in self:
            #order_change_obj=self.env["iac.purchase.order.change"].browse(order_change_id)
            # 200505 ning add begin
            if order_change.order_id.approve_flag == True:
                order_change.order_id.write({'need_unconfirm': True})
            # end
            order_change._send_to_webflow()


    @api.one
    def button_to_approve_one(self):
        """单笔送签的情况，在找不到签核人员列表的情况下,可能直接同步数据给SAP系统
        """
        #200505 ning add begin
        if self.order_id.approve_flag == True:
            self.order_id.write({'need_unconfirm':True})
        #end
        approve_flag,sap_flag=self._send_to_webflow()
        #单笔记录同步到SAP的情况下,需要跳转到List 视图
        if sap_flag==False:
            return
        action=self.env.ref("oscg_po.action_view_purchase_order_change_view_form")
        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': "form",
            'view_mode': "tree,form",
            'target': action.target,
            'res_model': action.res_model,
            #'view_id':action.view_id.id,
            'search_view_id':action.search_view_id.id,
            }

        view_id_list=[]
        form_view=self.env.ref("oscg_po.view_po_change_view_form")
        tree_view=self.env.ref("oscg_po.view_purchase_order_change_view_list")
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


    def _validate_webflow_exclude(self):
        """
        调用方为 po_change 对象,只能单个 po_change 调用
        校验是否不能送签,对不能送签的弹出提示
        :return:
        """
        vendor_id=self.vendor_id.id
        for order_change_line in self.line_ids:
            #校验是否存在签核中的相同材料,搜索po_change
            part_id=order_change_line.part_id.id
            #self.env.cr.execute("select ipol.order_code,ipol.order_line_code from public.iac_purchase_order_line_change ipol " \
            #                    "where ipol.part_id=%s                                                                           " \
            #                    "and ipol.vendor_id=%s                                                                          " \
            #                    "and exists (                                                                                   " \
            #                    "select 1 from public .iac_purchase_order_change ipo where ipo.id=ipol.order_id                        " \
            #                    "and ipo.state='to_approve'                                                                     " \
            #                    ") order by id limit 1                        ",
            #                    (part_id,vendor_id))
            #result=self.env.cr.fetchall()
            #if len(result)>0:
            #    err_msg=u"存在未签核完成的订单,订单号( %s ),订单行编码为( %s ),Part No 是( %s ) "% \
            #            (result[0][0],result[0][1],order_change_line.part_id.part_no)
            #    raise UserError(err_msg)

            domain_part=[('part_id','=',order_change_line.part_id.id),('vendor_id','=',vendor_id)]
            domain_part+=[('state','in',['wait_vendor_confirm','vendor_exception'])]

            #排除自身
            domain_part+=[('order_id','<>',self.order_id.id)]
            po_line_result=self.env["iac.purchase.order.line"].search(domain_part,order='id desc',limit=1)
            #排除条件
            #当前vendor相同的料号,有未confirm 的
            #状态变更为删除的 或者订单条目中减少数量的
            #曾经confirm过的
            if po_line_result.exists():
                if po_line_result.ever_confirmed==False:
                    continue
                #po change 暂时不卡
                #减少数量并且没有变更删除标记
                #if (po_line_result.ori_qty>po_line_result.new_qty
                #    and  po_line_result.ori_del_flag==po_line_result.new_del_flag
                #    and po_line_result.new_del_flag==False):
                #    err_msg=u"存在未确认的订单条目,订单编码为( %s ),订单行编码为( %s ),Part No 是( %s ) "%\
                #            (po_line_result.document_erp_id,po_line_result.document_line_erp_id,po_line_result.part_id.part_no)
                #    raise UserError(err_msg)
#
                ##变更删除标记,从False 变更为True
                #if ( po_line_result.ori_del_flag<>po_line_result.new_del_flag
                #    and po_line_result.new_del_flag==True):
                #    err_msg=u"存在未确认的订单条目,订单编码为( %s ),订单行编码为( %s ),Part No 是( %s ) "%\
                #            (po_line_result.document_erp_id,po_line_result.document_line_erp_id,po_line_result.part_id.part_no)
                #    raise UserError(err_msg)

    def _get_approve_exclude(self):
        """
        只限于order_change记录对象调用
        获取po 签核例外参数信息
        只有2种情况需要进行签核,1是订单条目中存在涨价情况,2 对单个材料来说,总量增加
        首次change的情况下,必定签核
        返回值有1个
        1   布尔型,表示是否需要签核

        :return:
        """
        #从未签核过的情况下,必定需要签核
        if self.order_id.approve_flag==False:
            return True

        #涨价和增加po_item需要签核
        for order_line_change in self.line_ids:
            #判断是否存在涨价情况
            if order_line_change.odoo_deletion_flag==False and (order_line_change.new_price>order_line_change.ori_price):
                return True
            #存在新增条目的情况
            if order_line_change.odoo_deletion_flag==False and (order_line_change.change_state=='add_po_line'):
                return True

            #增加数量和回复条目都需要签核
            if order_line_change.odoo_deletion_flag==False and (order_line_change.change_state in ['restore_po_line']):
                return True

        #判断是否存在某种材料总量上涨的情况
        self.env.cr.execute("select t.part_id,sum(t.ori_qty) ori_qty,sum(t.new_qty) new_qty from iac_purchase_order_line_change t " \
                            " where t.change_id=%s and t.odoo_deletion_flag=False group by t.part_id " ,
            (self.id,))

        part_list=self.env.cr.fetchall()
        #数量上涨需要签核
        for part_id,ori_qty,new_qty in part_list:
            if ori_qty<new_qty:
                return True
        return False

    def _get_po_change_factor(self):
        """
        获取order_change对象的 规则参数
        返回值有3个,返回一个存储规则参数的字典

         获得po_new 的签核角色列表
         传入参数  order对象
         返回值有3个
         第1个返回值 布尔型表示是否成功
         第2个返回值 列表类型为签核角色列表
         第3个返回值 异常信息列表

        :param order_change:
        :return:
        """
        rule_vals={}

        price_factor = ''
        quantity_factor = ''
        change_delivery = ''
        item_factor=''

        proc_result=True
        proc_ex_list=[]

        # 根据po判断规则引擎因子

        #如果从来没有签核过,那么订单金额是整个订单金额,如果签核过一次，那么订单金额为发生过变化的订单条目汇总金额
        order_amount=0
        if self.order_id.approve_flag==True:
            for order_line_change in self.line_ids:
                if order_line_change.odoo_deletion_flag!=True:
                    order_amount+=order_line_change.line_amount
        else:
            order_amount = self.order_amt
        material_maxprice = 0
        for line in self.line_ids:
            #删除条目不在考虑范围内,所以直接跳过
            if  line.odoo_deletion_flag==True:
                continue
            #真正的价格需要除以price_unit

            if line.price_unit==0:
                memo=_(u'解析规则报错,price_unit不能等于0！order_code 是 ( %s ) ,order_line_code ( %s )'%(line.order_code,line.order_line_code))
                proc_result=False
                proc_ex_list.append(memo)
                continue
            part_price=line.new_price/line.price_unit
            if part_price > material_maxprice:
                material_maxprice = part_price

            if line.item_type=='new_add':
                item_factor='add'
            if line.new_qty>line.ori_qty:
                quantity_factor='up'
        change_incoterm = ''
        change_payment_term = ''

        change_incoterm = ''
        if self.new_incoterm.id == self.ori_incoterm_id.id:
            change_incoterm = 'no'
        else:
            change_incoterm = 'yes'
        change_payment_term = ''
        if self.new_payment_term.id == self.ori_payment_term.id:
            change_payment_term = 'no'
        else:
            change_payment_term = 'yes'


        rule_vals={
            "order_amount":order_amount,
            "material_maxprice":material_maxprice,
            "change_incoterm":change_incoterm,
            "change_payment_term":change_payment_term,
            "item_factor":item_factor,
            }
        return proc_result,rule_vals,proc_ex_list




    @api.multi
    def _get_approve_list_by_context(self,regular_list,rule_context):
        """
         获得order_line_change 的签核角色列表
         传入参数  order对象
         返回值有3个
         第1个返回值 布尔型表示是否成功
         第2个返回值 列表类型为签核角色列表
         第3个返回值 当前po的送签规则记录
         第4个返回值 异常信息列表
        :return:
        """
        proc_result=True
        approve_role_list=[]
        approve_rule_list=[]
        proc_ex_list=[]

        order_amount=rule_context["order_amount"]
        material_maxprice=rule_context["material_maxprice"]
        change_incoterm=rule_context["change_incoterm"]
        change_payment_term=rule_context["change_payment_term"]

        price_factor=rule_context.get("price_factor",'')
        quantity_factor=rule_context.get("quantity_factor",'')
        change_delivery=rule_context.get("change_delivery",'')
        item_factor=rule_context.get("item_factor",'')

        order_code=rule_context.get("order_code",False)
        order_line_code=rule_context.get("order_line_code",False)
        order_id=rule_context.get("order_id",False)
        order_line_id=rule_context.get("order_line_id",False)
        order_change_id=rule_context.get("order_change_id",False)
        order_line_change_id=rule_context.get("order_line_change_id",False)
        price_control=rule_context.get("price_control",'')
        ori_price=rule_context.get("ori_price",'0')
        new_price=rule_context.get("new_price",'0')
        ref_price=rule_context.get("ref_price",'0')

        for regular in regular_list:
            expression=regular.expression
            expression = expression.replace('{order_amount}', str(order_amount))
            expression = expression.replace('{material_maxprice}', str(material_maxprice))
            expression = expression.replace('{change_incoterm}', change_incoterm)
            expression = expression.replace('{change_payment_term}', change_payment_term)
            expression = expression.replace('{price_factor}', price_factor)
            expression = expression.replace('{quantity_factor}', quantity_factor)
            expression = expression.replace('{change_delivery}', change_delivery)
            expression = expression.replace('{item_factor}', item_factor)

            expression = expression.replace('{price_control}', price_control)
            expression = expression.replace('{ori_price}', ori_price)
            expression = expression.replace('{new_price}', new_price)
            expression = expression.replace('{ref_price}', ref_price)
            rule = RuleParser(expression)
            error_flag='N'
            if rule.evaluate():
                regular_id = regular.id
                memo=''
                try:
                    approve_role_json = json.loads(regular.approve_role)
                    if (type(approve_role_json) is types.ListType):
                        approve_role_list=approve_role_list+approve_role_json
                        approve_role_list = list(set(approve_role_list))
                    else:
                        error_flag='Y'
                        memo=_(u'解析规则报错,签核的关卡不是合法的JSON中的list格式！order_code 是 ( %s ) ,order_line_code ( %s )'%(order_code,order_line_code))
                        proc_result=False
                        proc_ex_list.append(memo)
                except:
                    traceback.print_exc()
                    error_flag='Y'
                    memo=_(u'解析规则报错,签核的关卡不是合法的JSON格式！ order_code 是 ( %s ) ,order_line_code ( %s )' %(order_code,order_line_code))
                    proc_result=False
                    proc_ex_list.append(memo)

                expression = regular.expression
                # 找到送签规则的情况下
                rule_record = {
                    'order_id': order_id,
                    'order_line_id': order_line_id,
                    'order_change_id': order_change_id,
                    'order_line_change_id': order_line_change_id,
                    'regular_id': regular_id,
                    'expression': expression,
                    'order_amount': order_amount,
                    'material_maxprice': material_maxprice,
                    'change_incoterm': change_incoterm,
                    'change_payment_term': change_payment_term,
                    'price_factor': price_factor,
                    'quantity_factor': quantity_factor,
                    'change_delivery': change_delivery,
                    'item_factor': item_factor,
                    'error_flag': error_flag,
                    'memo': memo
                }
                approve_rule_list.append(rule_record)

        return  proc_result,approve_role_list,approve_rule_list,proc_ex_list

    def _get_po_change_approve_list(self):
        """
         获得po_change 的签核角色列表
         传入参数  order对象
         返回值有3个
         第1个返回值 布尔型表示是否成功
         第2个返回值 列表类型为签核角色列表
         第3个返回值 当前po的送签规则记录
         第4个返回值 异常信息列表
        :return:
        """


        # 规则引擎判断,判断整个订单的适应规则
        approve_role_json=[]
        regular_list = self.env['iac.purchase.approve.regular'].search([('plant_id', '=', self.plant_id.id),
                                                                        ('currency_id', '=', self.currency_id.id)])

        #获取每一条po_item的审核人列表信息
        proc_result=True
        approve_role_list=[]
        approve_rule_list=[]
        proc_ex_list=[]

        #处理po级别的规则
        proc_result,po_rule_context,ex_list=self._get_po_change_factor()
        po_rule_list= regular_list.filtered(lambda r: r.rule_type == "po")
        proc_ex_list+=ex_list

        result,role_list,rule_list,ex_list=self._get_approve_list_by_context(po_rule_list,po_rule_context)
        proc_ex_list+=ex_list

        approve_role_list+=role_list
        approve_role_list = list(set(approve_role_list))
        approve_rule_list=approve_rule_list+rule_list

        #处理po_line_item级别的规则,只处理修改的情况
        #只有增加数量或者涨价才签核
        for order_line_change in self.line_ids.filtered(lambda r:  r.change_factor_qty=="up" or r.change_factor_price=="up"):
            po_line_rule_list= regular_list.filtered(lambda r: r.rule_type == "po_line" )
            if len(po_line_rule_list)==0:
                continue


            po_line_rule_context=order_line_change._get_po_line_change_factor()
            po_line_rule_context.update(po_rule_context)
            po_line_rule_context["order_id"]=self.order_id.id
            po_line_rule_context["order_line_id"]=order_line_change.order_line_id.id
            po_line_rule_context["order_change_id"]=self.id
            po_line_rule_context["order_line_change_id"]=order_line_change.id
            po_line_rule_context["order_code"]=order_line_change.order_id.document_erp_id
            po_line_rule_context["order_line_code"]=order_line_change.order_line_code

            result,role_list,rule_list,ex_list=self._get_approve_list_by_context(po_line_rule_list,po_line_rule_context)
            if result==False:
                proc_result=False
                proc_ex_list.append(ex_list)
            else:
                if len(role_list)>0:
                    approve_role_list=approve_role_list+role_list
                    approve_role_list = list(set(approve_role_list))
                    approve_rule_list=approve_rule_list+rule_list


        return proc_result,approve_role_list,approve_rule_list,proc_ex_list


    def _send_to_webflow(self):
        """
        当前order_change 送签到webflow
        返回值有2个
        1   布尔型表示是否送签成功
        2   布尔型表示是否同步数据给SAP
        :return:
        """
        proc_result=True
        approve_role_list=[]
        approve_rule_list=[]
        proc_ex_list=[]
        po_change_approve_list=[]

        #只有 pending webflow_error unapproved
        if self.state not in ['pending','webflow_error','unapproved']:
            raise UserError(u'只有 pending webflow_error unapproved 的状态才能送签')

        #遍历order_line_change 补充info_record_his
        #T00，J00，P00 开头的vendor_code 不校验inforecord
        exclude_vendor=['T00','J00','P00']
        if self.vendor_id.vendor_code[0:3] not in exclude_vendor:
            for order_line_change in self.line_ids:
                #价格没有发生变化的跳过检查
                if abs(order_line_change.ori_price-order_line_change.new_price)<0.0001:
                    continue
                if not order_line_change.price_his_id.exists():
                    vendor_id=self.order_id.vendor_id.id
                    part_id=order_line_change.part_id.id
                    last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
                    if last_price_rec.exists():
                        order_line_change.write({"price_his_id":last_price_rec.id})
                    else:
                        raise UserError('Part No is ( %s ) has no price in inforecord_history'% (order_line_change.part_id.part_no,))

        #遍历po change 条目判断是否有相同料号的没有cofirm这种情况不能进行送签
        self._validate_webflow_exclude()

        #判断是否需要进行签核
        #不需要签核的情况下,直接调用SAP 同步数据,返回False 不需要签核
        approve_exclude=self._get_approve_exclude()
        if approve_exclude==False:
            self.send_to_sap()
            #保存po_change_日志
            self.apply_po_audit()

            #保存po_line_change日志
            for order_line_change in self.line_ids:
                order_line_change.apply_po_line_audit()
            return False,True

        proc_result,approve_role_list,approve_rule_list,proc_ex_list=self._get_po_change_approve_list()
        #如果获取审核角色列表出现异常则停止进行处理
        if proc_result==False:
            raise UserError(proc_ex_list)

        #如果签核过一次,并且当前po_change 无法匹配到角色列表,直接同步数据到sap
        if len(approve_role_list)==0 and self.order_id.approve_flag==True:
            self.send_to_sap()
            #保存po_change_日志
            self.apply_po_audit()

            #保存po_line_change日志
            for order_line_change in self.line_ids:
                order_line_change.apply_po_line_audit()
            return False,True

        #从来没有签核过的情况,并且没有匹配到角色的情况下,默认MM_Manager
        if len(approve_role_list)==0 and self.order_id.approve_flag==False:
            approve_role_list.append("MM_Manager")
        po_approve_item={"proc_result":proc_result,
                         "approve_role_list":approve_role_list,
                         "approve_rule_list":approve_rule_list,
                         "proc_ex_list":proc_ex_list,
                         "order_id":self.order_id.id,
                         "order_change_id":self.id
        }
        self.write({"approve_role_list":approve_role_list})


        #校验当前批量中已经不存在错误的情况下,批量调用webflow送签
        # 调用webflow接口
        biz_object = {
            "id": po_approve_item["order_change_id"],
            "biz_object_id": po_approve_item["order_change_id"],
            "flow_id": po_approve_item["approve_role_list"],
            }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "F07_B_2", biz_object)
        order_change_result=self.env["iac.purchase.order.change"].browse(po_approve_item["order_change_id"])
        if rpc_result:
            vals={
                'state': 'to_approve',
                'state_msg': u'送签成功',
                'webflow_number':rpc_json_data.get('EFormNO'),
                }
            order_change_result.write(vals)
            #记录order change 日志
            order_change_result.apply_po_audit()
            #记录order_line_change日志
            for order_line_change in order_change_result.line_ids:
                order_line_change.apply_po_line_audit()
        else:
            order_change_result.write({'state_msg': u'送签失败',"state":"webflow_error"})
            #记录order change 日志
            order_change_result.apply_po_audit()
            #记录送签失败的日志信息
            for order_line_change in order_change_result.line_ids:
                order_line_change.apply_po_line_audit()

        #记录送签规则记录
        for approve_rule in po_approve_item["approve_rule_list"]:
            self.env['iac.purchase.approve.record'].create(approve_rule)


        return rpc_result,False



    @api.multi
    def button_cancel(self):
        if self.state == 'pending':
            self.write({'state': 'cancel'})
            if self.order_id.changed:
                self.order_id.write({'changed': False})
        return True

    @api.multi
    def button_recover(self):
        if self.state == 'cancel':
            self.write({'state': 'pending'})
            if self.order_id.changed:
                self.order_id.write({'changed': True})
        return True

    def _change_po_mail_to_vendors(self):
        """
        new_po 状态更新为wait_vendor_comfirm时
            及时发送Alert email 给vendor
        """
        # 调用utility里的公用方法
        utility.po_mail_to_vendor(self,self.line_ids,'change_po')

    def po_change_callback(self, context=None):
        """
        回调函数说明
        模型为 iac.purchase.order
        context={"approve_status": True,"data":{"id":1376,}}

        返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
        :param context:
        :return:
        """
        proc_result = False
        proc_ex = []
        try:
            ctx = dict(self._context or {})
            ctx['webflow_callback'] = "webflow_callback"
            if context["approve_status"]  and context["rpc_callback_data"]["FormStatus"]=="C":
                order_change_id=context.get("data").get("id")
                order_change = self.browse(order_change_id)
                if not order_change.exists():
                    proc_ex.append(u"iac.purchase.order.change model has no record with id ( %s )" %(order_change_id,))
                    return proc_result,proc_ex

                order_change.with_context(ctx).write({'state': 'to_sap',
                                    'state_msg': u'webflow签核通过'})
                #记录order change 日志
                order_change.apply_po_audit()
                #记录状态信息，签核通过
                for order_line_change in order_change.line_ids:
                    order_line_change.apply_po_line_audit()
                # 调用SAP接口
                proc_result,proc_ex=order_change.send_to_sap()
                if proc_result==False:
                    order_change.with_context(ctx).write({'state': 'sap_error',
                                        'state_msg': u'通知SAP失败'})
                    order_change.apply_po_audit()
                    #记录状态信息，通知sap失败
                    for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()
                else:
                    order_change.order_id.write({'approve_flag':True})
                    #当webflow成功的时候,丢弃调用SAP失败的异常,总是返回成功状态

                    order_change.apply_po_audit()
                    #记录状态信息，同步数据SAP成功
                    for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()

                proc_result=True
                proc_ex=[]
                return proc_result,proc_ex
            elif context["approve_status"]  and context["rpc_callback_data"]["FormStatus"]=="D":
                order_change_id=context.get("data").get("id")
                order_change = self.browse(order_change_id)
                if not order_change.exists():
                    proc_ex.append(u"iac.purchase.order model has no record with id ( %s )" %(order_change_id,))
                    return proc_result,proc_ex

                order_change.with_context(ctx).write({'state': 'unapproved',
                                    'state_msg': u'webflow签核未通过,webflow抽单拒绝'})
                order_change.apply_po_audit()

                #记录状态信息，签核失败
                for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()
                proc_result = True
                return proc_result, proc_ex
            else:
                order_change_id=context.get("data").get("id")
                order_change = self.browse(order_change_id)
                if not order_change.exists():
                    proc_ex.append(u"iac.purchase.order model has no record with id ( %s )" %(order_change_id,))
                    return proc_result,proc_ex

                order_change.with_context(ctx).write({'state': 'unapproved',
                                    'state_msg': u'webflow签核失败'})
                order_change.apply_po_audit()
                #记录状态信息，签核失败
                for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()
                proc_result = False
                return proc_result, proc_ex
        except:
            ex_string = traceback.format_exc()
            proc_result = False
            proc_ex.append(ex_string)
            traceback.print_exc()
            return proc_result, proc_ex

    @api.multi
    def apply_po_change_data(self):
        """
        给定change记录对象,应用change对象中的数据到order_line中
        :param change:
        :return:
        """

        #写入数据到订单头
        order_var = {}
        #incoterm = fields.Char(string="Incoterm From SAP")
        #payment_term=fields.Char(string="Payment Term")
        order_var['payment_term_id'] = self.new_payment_term.id
        order_var['incoterm_id'] = self.new_incoterm.id
        order_var['incoterm1'] = self.new_incoterm1
        order_var['order_reason'] = self.order_reason
        order_var['state'] = 'wait_vendor_confirm'
        order_var['incoterm'] = self.new_incoterm.incoterm
        order_var['payment_term'] = self.new_payment_term.payment_term


        order_var['ori_payment_term'] =self.ori_payment_term.id
        order_var['ori_incoterm_id'] = self.ori_incoterm_id.id
        order_var['ori_incoterm1'] = self.ori_incoterm1
        order_var['new_payment_term'] = self.new_payment_term.id
        order_var['new_incoterm'] = self.new_incoterm.id
        order_var['new_incoterm1'] = self.new_incoterm1
        self.order_id.write(order_var)

        #写入订单明细
        #处理新增的订单条目
        for change_line in self.line_ids.filtered(lambda r: r.item_type == 'new_add' or r.item_type == 'split_item'):
            add_line_vars = {
                'plant_id': self.order_id.plant_id.id,
                'plant_code': self.order_id.plant_id.plant_code,
                'order_id': self.order_id.id,
                'document_erp_id': self.order_code,
                'document_line_erp_id': change_line.order_line_code,
                'part_id': change_line.part_id.id,
                'part_no': change_line.part_id.part_no,
                'quantity': change_line.new_qty,
                'price': change_line.new_price,
                'price_unit': change_line.last_price_unit,
                'delivery_date': change_line.new_delivery_date,
                'unit': change_line.unit,
                'storage_location': change_line.storage_location,
                'tax_code': change_line.tax_code,
                'price_date': change_line.price_date,
                'vendor_id': self.order_id.vendor_id.id,
                "last_order_line_change_id":change_line.id,
                'order_line_code': change_line.order_line_code_2,
                'currency_id':change_line.order_id.currency_id.id,
                'order_date':change_line.order_id.order_date,
                'ori_qty':change_line.ori_qty,
                'new_qty':change_line.new_qty,
                'ori_price':change_line.ori_price,
                'new_price':change_line.new_price,
                'ori_delivery_date':change_line.ori_delivery_date,
                'new_delivery_date':change_line.new_delivery_date,
                'ori_del_flag':change_line.ori_deletion_flag,
                'new_del_flag':change_line.odoo_deletion_flag,
                'ever_confirm':True,
                "buyer_id":change_line.order_id.buyer_id.id
                }
            #新增的条目被删除的情况不进行处理,不需要vendor_confirm
            if change_line.odoo_deletion_flag==True:
                continue
            if change_line.change_state not in ['no_change']:
                add_line_vars["state"]="wait_vendor_confirm"
            #判定order_line中是否存在重复的记录
            domain=[('order_id','=',change_line.order_id.id)]
            domain+=[('order_line_code','=',change_line.order_line_code_2)]
            dst_order_line=self.env["iac.purchase.order.line"].search(domain,limit=1)
            if dst_order_line.exists():
                raise UserError("Order Code is %s ,Order Line Code is %s has exists,can not create "%
                                (change_line.order_id.document_erp_id,change_line.order_line_code_2))
            order_line=self.env["iac.purchase.order.line"].create(add_line_vars)

            #回写相关数据,建立数据关联
            change_line.write({"order_line_id":order_line.id,"state":"erp_accepted"})

        #处理删除的订单条目
        for change_line in self.line_ids.filtered(lambda r: r.odoo_deletion_flag == True):
            order_line_vals={
                'ori_qty':change_line.ori_qty,
                'new_qty':change_line.new_qty,
                'ori_price':change_line.ori_price,
                'new_price':change_line.new_price,
                'ori_delivery_date':change_line.ori_delivery_date,
                'new_delivery_date':change_line.new_delivery_date,
                "odoo_deletion_flag":True,
                'ori_del_flag':change_line.ori_deletion_flag,
                'new_del_flag':change_line.odoo_deletion_flag,
                'ever_confirm':True,
                "buyer_id":change_line.order_id.buyer_id.id
            }
            if change_line.change_state not in ['no_change']:
                order_line_vals["state"]="wait_vendor_confirm"
            change_line.order_line_id.with_context(apply_change=True).write(order_line_vals)
            change_line.write({"state":"erp_accepted"})

        #处理修改的订单条目
        for change_line in self.line_ids.filtered(lambda r: (r.odoo_deletion_flag == False and r.item_type == 'ori_item')):
            order_line_vars={
                "odoo_deletion_flag":change_line.odoo_deletion_flag,
                "price":change_line.new_price,
                'price_unit': change_line.last_price_unit,
                "quantity":change_line.new_qty,
                "delivery_date":change_line.new_delivery_date,
                "state_msg":u"通知SAP成功",
                'ori_qty':change_line.ori_qty,
                'new_qty':change_line.new_qty,
                'ori_price':change_line.ori_price,
                'new_price':change_line.new_price,
                'ori_delivery_date':change_line.ori_delivery_date,
                'new_delivery_date':change_line.new_delivery_date,
                'ori_del_flag':change_line.ori_deletion_flag,
                'new_del_flag':change_line.odoo_deletion_flag,
                'deletion_flag':change_line.sap_deletion_flag,
                'ever_confirm':True,
                "buyer_id":change_line.order_id.buyer_id.id
                }
            if change_line.change_state not in ['no_change']:
                order_line_vars["state"]="wait_vendor_confirm"
            change_line.order_line_id.with_context(apply_change=True).write(order_line_vars)
            change_line.write({"state":"erp_accepted"})
        #变更order change的状态
        self.write({"state":"erp_accepted","state_msg":u"通知SAP成功"})

        #处理特殊情况,po_line 第一次change,没有修改任何信息的情况下，需要vendor_confirm 一次
        for order_line_rec in self.order_id.order_line:
            if order_line_rec.state=="pending":
                order_line_rec.with_context(state_change=True).write({"state":"wait_vendor_confirm"})

        #更新版本po 版本号
        self.env.cr.execute("""
         select cast(COALESCE(version_no,'0') as int4)+1 from iac_purchase_order where id=%s
        """,(self.order_id.id,))
        pg_result=self.env.cr.fetchall()
        self.order_id.write({"version_no":str(pg_result[0][0])})

        #创建Vendor Confirm History 记录
        self.env["iac.purchase.order.vendor.confirm.his"].po_change_vendor_confirm_create(self.order_id.id)

        #生成unconfirm 数据
        if self.change_type=='po_change_single':
            self.order_id.write({"last_change_id":self.id})
            # 200505 ning add begin
            if self.order_id.need_unconfirm == True:
            # end
            #self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data(self.order_id.id,self.id,'po_change_single')
                self.env["iac.purchase.order.unconfirm.detail"].sudo().generate_unconfirm_data(self.id)

        if self.change_type=='po_change_mass':
            self.order_id.write({"last_change_id":self.id})
            # 200505 ning add begin
            if self.order_id.need_unconfirm == True:
            # end
            #self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data(self.order_id.id,self.id,'po_change_mass')
                self.env["iac.purchase.order.unconfirm.detail"].sudo().generate_unconfirm_data(self.id)

    def send_to_sap(self):
        """
        :return:
        """

        for order_change in self:
            if not (order_change.state in ['pending','sap_error','to_sap','unapproved']):
                raise UserError("Po No is %s ,state is %s ,can not call Send To SAP"%(order_change.order_code,order_change.state))
                continue

            # 调用SAP接口
            biz_object = {
                "id": order_change.id,
                "biz_object_id": order_change.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_PO_002", biz_object)

            if rpc_result:
                # 根据order change更新order
                order_change.apply_po_change_data()
                order_change.order_id.write({'approve_flag':True,'po_change_type':order_change.po_change_type})

                # change po state='wait vendor confirm'时给vendor发送邮件提醒其confirm
                # state='wait vendor confirm是在上面apply_po_change_data()方法里write的
                order_change._change_po_mail_to_vendors()

                #更新版本po 版本号
                self.env.cr.execute("""
                 select cast(COALESCE(version_no,'0') as int4)+1 from iac_purchase_order where id=%s
                """,(order_change.order_id.id,))
                pg_result=self.env.cr.fetchall()
                order_change.order_id.write({"version_no":str(pg_result[0][0])})
                proc_result=True
                return proc_result,[]
            else:
                update_vals={
                    "state_msg":"通知SAP失败,%s" %(str(exception_log),),
                    "state":"sap_error"
                }
                order_change.write(update_vals)
                proc_result = False
                return proc_result,exception_log



    @api.multi
    def button_to_sap(self):
        """
        通过菜单调用sap系统,支持多条order_change 批量送sap
        送完po change 应该返回到po change list 页面
        :return:
        """

        action=self.env.ref("oscg_po.action_view_purchase_order_change_view_form")
        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': "form",
            'view_mode': "tree,form",
            'target': action.target,
            'res_model': action.res_model,
            #'view_id':action.view_id.id,
            'search_view_id':action.search_view_id.id,
        }

        view_id_list=[]
        form_view=self.env.ref("oscg_po.view_po_change_view_form")
        tree_view=self.env.ref("oscg_po.view_purchase_order_change_view_list")
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


        for order_change in self:
            #if not (order_change.state in ['pending','sap_error','to_sap','unapproved']):
            if not (order_change.state in ['sap_error','to_sap']):
                raise UserError("Po No is %s ,state is %s ,can not call Send To SAP"%(order_change.order_code,order_change.state))
                continue

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
                    order_change.apply_po_change_data()
                    order_change.order_id.write({'approve_flag':True,'po_change_type':order_change.po_change_type})

                    # change po后po state='wait vendor confirm'时给vendor发送邮件提醒其confirm
                    # state='wait vendor confirm是在上面apply_po_change_data()方法里write的
                    order_change._change_po_mail_to_vendors()

                    #更新版本po 版本号
                    self.env.cr.execute("""
                     select cast(COALESCE(version_no,'0') as int4)+1 from iac_purchase_order where id=%s
                    """,(order_change.order_id.id,))
                    pg_result=self.env.cr.fetchall()
                    order_change.order_id.write({"version_no":str(pg_result[0][0])})
                    proc_result=True

                    order_change.apply_po_audit()
                    #记录状态信息，同步数据SAP成功
                    for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()
                    #return proc_result,[]
                else:
                    order_change.write({'state_msg': u'通知SAP失败','state':'sap_error'})
                    proc_result = False

                    order_change.apply_po_audit()
                    #记录状态信息，同步数据SAP成功
                    for order_line_change in order_change.line_ids:
                        order_line_change.apply_po_line_audit()
                    #return proc_result,exception_log
            except:
                proc_ex=[]
                traceback.print_exc()
                proc_ex.append(traceback.format_exc())
                proc_result = False
                #return proc_result,proc_ex


        return action_window
        #action_view_purchase_order_change_view_form

    @api.multi
    def button_to_edit_po_line(self):
        """
            当前方法只能由po_change对象来调用,实际上也就是只能处理一条记录
        """
        #action_view_purchase_order_line_change_edit_view_form
        action = self.env.ref('oscg_po.action_view_purchase_order_line_change_edit_view_form')
        order_ids = self.ids
        if self.state=='to_approve':
            raise UserError('Can not change order when it is in state to_approve')
            pass
        action_data={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_order_id': " + str(order_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('id', '=',order_ids[0])],
            'res_id':order_ids[0]
        }

        return action_data

    def get_change_type(self,change_id):
        # 200227 ning add 确认当前po的change type
        # print self.id
        # 查出当前po所有的line
        line_objs = self.env['iac.purchase.order.line.change'].search([('change_id', '=', change_id)])
        part_id_list = []
        ori_qty_list = []
        new_qty_list = []

        # 先根据料号分组
        for line in line_objs:
            if line.part_id.id not in part_id_list:
                part_id_list.append(line.part_id.id)
                if line.ori_deletion_flag == line.odoo_deletion_flag:
                    ori_qty_list.append(line.ori_qty)
                    new_qty_list.append(line.new_qty)
                else:
                    #如果是删除item，new qty为0
                    if line.ori_deletion_flag == False and line.odoo_deletion_flag == True:
                        ori_qty_list.append(line.ori_qty)
                        new_qty_list.append(0)
                    #如果是恢复订单行，ori qty为0
                    if line.ori_deletion_flag == True and line.odoo_deletion_flag == False:
                        ori_qty_list.append(0)
                        new_qty_list.append(line.new_qty)
            else:
                index = part_id_list.index(line.part_id.id)
                if line.ori_deletion_flag == line.odoo_deletion_flag:
                    ori_qty_list[index] = ori_qty_list[index] + line.ori_qty
                    new_qty_list[index] = new_qty_list[index] + line.new_qty
                else:
                    #如果是删除item，new qty为0
                    if line.ori_deletion_flag == False and line.odoo_deletion_flag == True:
                        ori_qty_list[index] = ori_qty_list[index] + line.ori_qty
                        new_qty_list[index] = new_qty_list[index]
                    #如果是恢复订单行，ori qty为0
                    if line.ori_deletion_flag == True and line.odoo_deletion_flag == False:
                        ori_qty_list[index] = ori_qty_list[index]
                        new_qty_list[index] = new_qty_list[index] + line.new_qty
        #用来标记数量变化，0表示没变化，1表示有变化
        qty_change = 0
        for i in range(len(part_id_list)):
            if ori_qty_list[i] != new_qty_list[i]:
                qty_change = 1
                break
            else:
                continue
        # 用来标记价格变化，0表示没变化，1表示有变化
        price_change = 0
        for line in line_objs:
            if line.change_factor_price != 'equal':
                price_change = 1
                break
            else:
                continue

        # 数量不变，价格改变
        if price_change == 1 and qty_change == 0:
            super(IacPurchaseOrderChange, self).write({'po_change_type': 'price_change'})
        #数量改变，价格没变
        if qty_change == 1 and price_change == 0:
            super(IacPurchaseOrderChange, self).write({'po_change_type': 'quantity_change'})
        #数量和价格同时改变
        if qty_change == 1 and price_change == 1:
            super(IacPurchaseOrderChange, self).write({'po_change_type': 'quantity_and_price_change'})
        #都不改变
        if qty_change == 0 and price_change == 0:
            super(IacPurchaseOrderChange, self).write({'po_change_type': 'no_change'})


    @api.multi
    def write(self,vals):
        if "webflow_callback" not in self._context and self.state in ['to_approve']:
            raise UserError('PO can not change when it is in state to_approve ')
        result=super(IacPurchaseOrderChange,self).write(vals)
        if "po_change_type" not in self._context:
            self.get_change_type(self.id)
        for order_change in self:
            order_change.uniq_check_po_change()
        return result
        pass


    @api.one
    def apply_po_audit(self):
        """
        记录当前po change 的audit 状态
        以上的状态变更的情况下备份记录po_line的变化情况
        :return:
        """
        #存储po稽核信息
        order_audit_vals={
            "order_id":self.order_id.id,
            "order_change_id":self.id,
            "order_code":self.order_id.document_erp_id,
            "user_id":self.env.user.id,
            "user_login_code":self.env.user.login,
            "state_msg":self.state_msg,
            "audit_source":"po_change",
            "ori_payment_term":self.ori_payment_term.id,
            "ori_incoterm_id":self.ori_incoterm_id.id,
            "ori_incoterm1":self.ori_incoterm1,
            "new_payment_term":self.new_payment_term.id,
            "new_incoterm_id":self.new_incoterm.id,
            "new_incoterm1":self.new_incoterm1,
            }
        if self.state=="webflow_error":
            order_audit_vals["action_type"]="webflow_error"
        elif self.state=="pending":
            order_audit_vals["action_type"]="po_change"
        elif self.state=="to_approve":
            order_audit_vals["action_type"]="send_to_webflow"
        elif self.state=="unapproved":
            order_audit_vals["action_type"]="denied_by_webflow"
        elif self.state=="to_sap":
            order_audit_vals["action_type"]="send_to_sap"
        elif self.state=="sap_error":
            order_audit_vals["action_type"]="send_sap_error"
        #send_sap_error
        elif self.state=="erp_accepted":
            order_audit_vals["action_type"]="wait_vendor_confirm"
        self.env["iac.purchase.order.audit"].create(order_audit_vals)

class IacPurchaseOrderLineChange(models.Model):
    """PO Change从表，同时是PO Line Delivery Change主表"""
    _name = "iac.purchase.order.line.change"
    _description = "PO Line Change"
    _order = 'id desc'

    change_id = fields.Many2one('iac.purchase.order.change', string="Change Order ID", index=True)# 主表外键
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)# 从order视图“变更”按钮事件传过来的值
    order_line_id = fields.Many2one('iac.purchase.order.line', string="PO Line Number", readonly=True, index=True)# 从order视图“变更”按钮事件传过来的值
    # 添加关联字段，目的为显示原始po的数据栏位
    original_qty = fields.Float(string='Original Quantity', related='order_line_id.line_history_id.quantity')

    order_code = fields.Char(string="Order Code", copy=False, index=True)
    order_line_code = fields.Char(string="Order Line Code", copy=False, index=True)
    purchase_req_no = fields.Char(string="Purchase Request No" )# PR#
    purchase_req_item_no = fields.Char(string="Purchase Request Item No")# PR itme#

    vendor_id = fields.Many2one('iac.vendor',  string="Vendor Info", index=True)
    part_id = fields.Many2one('material.master.po.line', string="Material")
    division=fields.Char('division')
    vendor_part_no = fields.Char( string="Vendor Part No")

    ori_price = fields.Float(string='Original Price', help="The Original price to purchase a product")# 原价格
    price_unit = fields.Integer(string="Price Unit")
    ori_qty = fields.Float(string='Original Quantity')# 原数量
    ori_delivery_date = fields.Date(string="Original Delivery Date")  # 原交期
    new_price = fields.Float('New Price', default=1.0, help="The New price to purchase a product")# 新价格
    new_qty = fields.Float(string='New Quantity', default=1.0)# 新数量

    line_amount = fields.Float(string="Line Amount", precision=(18, 4), compute='_taken_amount')
    new_delivery_date = fields.Date(string="New Delivery Date")  # po line变更交期的最长交期


    internal_comment = fields.Text(string="Internal Comment")

    rejection_indicator = fields.Boolean(string="Rejection Indicator", default=False)
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记
    line_deletion_flag = fields.Char(string="Delete Line", compute='_taken_deletion_flag', store=True)
    sap_deletion_flag = fields.Char(string="Delete Line", compute='_taken_sap_deletion_flag', store=True)
    storage_location = fields.Char(string="Storage Location")
    unit = fields.Char(string="Unit")
    tax_code = fields.Char(string="Tax Code")
    price_date = fields.Date(string="Price Date")

    parent_item_id = fields.Many2one('iac.purchase.order.line.change', string="Parent Item",index=True)
    item_type = fields.Selection([('ori_item', 'ori_item'), ('split_item', 'split_from_ori_item'), ('new_add', 'New Added')], default='new_add')
    next_item_id = fields.Many2one('iac.purchase.order.line.change', string="Next PO Line Number",index=True)

    search_change_line_id = fields.Many2one('iac.purchase.order.line.change', string="Search PO Line Number",index=True)
    ori_deletion_flag = fields.Boolean(string='Delete', default=False)#初始删除标记


    price_his_id = fields.Many2one('inforecord.history', string="Price History Info")#关联到价格信息表,临时字段
    last_price=fields.Float(string="Last Price Info",default=0)#从价格表中获取的最新价格
    last_price_unit = fields.Integer(string="New Price Unit") #从价格表中获取的最新price_unit
    last_price_type=fields.Selection([('cost_up','Cost Up'),('cost_down','Cost Down')],string="Price Change Type")#价格变化类型
    date_base = fields.Selection([('po_date_base_all_open_po', u'PO date base（all open PO）'),
                                  ('delivery_date_base', 'Delivery date base'),
                                  ('po_date_base', u'PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base', u'Delivery date base + PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base_all_open_po', u'Delivery date base + PO date base（all open PO）')
                                 ], default='po_date_base_all_open_po', string="Price Date Base")

    #异动状态,报表要使用这个数据
    change_state = fields.Selection([('cancel_po_line', 'Cancel PO Line'),
                                     ('restore_po_line', 'Restore PO Line'),
                                     ('cost_up', 'Cost Up'),
                                     ('cost_down', 'Cost Down'),
                                     ('no_change', 'No Change'),
                                     ('add_po_line', 'Add PO Line'),
                                     ('qty_down', 'Reduce PO Line Quantity'),
                                     ('qty_up', 'Increase PO Line Quantity'),
                                     ('cost_up_split', 'Cost Up And Split PO Line'),
                                     ('cost_down_split', 'Cost Down And Split PO Line'),
                                    ], default='no_change')
    #增量後的數量：
    #1. Cancel 再復活。
    #2. 在原 Line Item 增加數量。(待SCM內部確認)
    #3. 在原PO料號範圍內，新增 Line Item。
    increase_qty = fields.Float(string='Increased Quantity', help="Increase Quantity")
    #減量：
    #1. Cancel 的數量。
    #2. 單價調整拆 Item 減少的數量。
    decrease_qty = fields.Float(string='Decreased Quantity', help="Decrease Quantity")
    cancel_qty = fields.Float(string='Cancel Quantity', help="Cancel Quantity")
    ori_price = fields.Float(string='Original Price', help="The Original price to purchase a product")# 原价格
    usd_price = fields.Float('USD Price',compute='_take_usd_price')#转换到美金的价格
    purchase_req_no = fields.Char(string="Purchase Request No")# PR#
    purchase_req_item_no = fields.Char(string="Purchase Request Item No")# PR itme#

    #关联字段
    open_qty = fields.Float(string="Open PO Quantity", related='order_line_id.open_qty')
    gr_qty = fields.Float(string="GR Quantity", related='order_line_id.gr_qty')
    on_road_qty = fields.Float(string="On Road Quantity", related='order_line_id.on_road_qty')

    #数据迁移索要使用的字段
    part_no=fields.Char(string="Part NO",index=True)
    po_change_code=fields.Char(string="Po Change Code",index=True)
    currency_id = fields.Many2one('res.currency', string="Currency",index=True)
    order_date = fields.Date(string="PO Date",index=True)
    order_line_code_2 = fields.Char(string="Order Line Code", copy=False, index=True)##5位字符串,不足的前面补足零,可以用来订单内部排序使用
    change_factor_qty=fields.Selection([('up','Quantity Increase'),('down','Quantity Decrease'),('equal','Quantity Equal')],string='Quantity Equal',default="equal",index=True)
    change_factor_price=fields.Selection([('up','Price Up'),('down','Price Down'),('equal','Price Equal')],string='Price Equal',default="equal",index=True)

    #废弃字段不再使用
    deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记,废弃字段不再使用
    add_item_reason = fields.Selection([('not add', 'Not Add'), ('cost down', 'Cost Down'), ('cost up', 'Cost Up'), ('change delivery', 'Change Delivery')], default='not add')
    add_item_price = fields.Float('Add Item - Price', default=1.0)# 新增item价格
    add_item_qty = fields.Float(string='Add Item - Quantity', default=1.0)# 新增item数量
    add_item_delivery = fields.Date(string="Add Item - Delivery Date")# 新增item交期
    new_delivery_schedule_ids = fields.One2many('iac.delivery.schedule.change', 'line_change_id', string="New Delivery Schedule")# 从模型
    current_flag = fields.Boolean(string='Current Flag', default=False)# 新增的line current_flag设为False
    confirm_flag = fields.Boolean(string='Confirm Flag', default=False)
    price_control = fields.Char(string="Price Control")

    @api.one
    @api.depends('new_price')
    def _take_usd_price(self):

        if self.change_id.currency_id.exists() and self.change_id.currency_id.name=="USD":
            self.usd_price=self.new_price
        else:
            if not self.change_id.currency_id.exists():
                self.usd_price=0
            else:
                currency_exchange=self.env["iac.currency.exchange"].get_usd_exchange_record(self.change_id.currency_id.id)
                if currency_exchange.exists():
                    self.usd_price=(self.new_price/currency_exchange.from_currency_amount)*currency_exchange.to_currency_amount
                else:
                    self.usd_price=0

    @api.depends('new_qty', 'new_price', 'price_unit')
    def _taken_amount(self):
        for change in self:
            if change.price_unit > 0:
                change.line_amount = change.new_qty * (change.new_price / change.last_price_unit)
            else:
                change.line_amount = 0

    @api.depends('odoo_deletion_flag','ori_deletion_flag')
    def _taken_sap_deletion_flag(self):
        #for change_line in self:
        #    if change_line.ori_deletion_flag==False and  change_line.odoo_deletion_flag==True:
        #        change_line.sap_deletion_flag = 'L'
        #        continue
        #    if change_line.ori_deletion_flag==True and  change_line.odoo_deletion_flag==False:
        #        change_line.sap_deletion_flag = 'C'
        #        continue
        #    else:
        #        change_line.sap_deletion_flag = False
        for change_line in self:
            if  change_line.odoo_deletion_flag==True:
                change_line.sap_deletion_flag = 'L'
            else:
                change_line.sap_deletion_flag = 'C'


    @api.depends('odoo_deletion_flag')
    def _taken_deletion_flag(self):
        for change in self:
            if change.odoo_deletion_flag:
                change.line_deletion_flag = 'Y'
            else:
                change.line_deletion_flag = 'N'

    def _get_change_factor(self):
        """
        获取当前change_line 是否见谅或者降价,返回字典对象
        :return:
        """
        change_factor_vals={}
        #没有变更删除状态的情况下
        if self.ori_deletion_flag==self.odoo_deletion_flag:
            #当前记录为删除状态,应该保持原状态
            if self.odoo_deletion_flag==True:
                return change_factor_vals

            #当前记录没有删除
            if self.odoo_deletion_flag==False:
                if self.item_type=='new_add':
                    change_factor_vals["change_factor_qty"]="up"
                else:
                    if self.ori_qty>self.new_qty:
                        change_factor_vals["change_factor_qty"]="down"
                    elif self.ori_qty<self.new_qty:
                        change_factor_vals["change_factor_qty"]="up"
                    elif self.ori_qty==self.new_qty:
                        change_factor_vals["change_factor_qty"]="equal"

                if self.ori_price<self.new_price:
                    change_factor_vals["change_factor_price"]="up"
                elif self.ori_price>self.new_price:
                    change_factor_vals["change_factor_price"]="down"
                elif self.ori_price==self.new_price:
                    change_factor_vals["change_factor_price"]="equal"
                return change_factor_vals
        else:
            #变更了删除状态的情况下
            #当前记录从正常变更为删除,这种情况认定为减少数量
            if self.odoo_deletion_flag==True:
                change_factor_vals["change_factor_qty"]="down"
                return change_factor_vals

            #当前记录由删除变更为正常，认定为增加数量
            if self.odoo_deletion_flag==False:
                change_factor_vals["change_factor_qty"]="up"
                return change_factor_vals

    @api.multi
    def write(self, values):
        # 检查po line change

        for change_line in self:
            #200504 ning add begin
            #200703 ning 调整逻辑 1.判断deletion_flag是否变化  2.判断数量是否变化
            if values.get('odoo_deletion_flag',False):
                if values.get('odoo_deletion_flag',False) == True and values.get('new_qty',False):
                    raise UserError('不能在删除订单的同时修改数量！')
            else:
                if values.get('odoo_deletion_flag',-1) == False:
                    print 1
                else:
                    if change_line.odoo_deletion_flag == True and values.get('new_qty',False):
                        raise UserError('不能在删除订单的同时修改数量！')

            # end
            if ('last_price_unit' in values):
                last_price_unit=values.get("last_price_unit")
                if last_price_unit not in [1000,10000]:
                    raise UserError(_(u'Price Unit 只能是1000或者10000！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))

            #检查删除条目的情况下，是否有入料
            self.env.cr.execute("""
             select COALESCE(sum(qty_received),0) from goods_receipts where po_id=%s and po_line_id= %s and qty_received is not null
            """,(change_line.order_id.id,change_line.order_line_id.id))
            pg_result=self.env.cr.fetchall()
            gr_qty=pg_result[0][0]

            #检查删除条目的情况下，是否有开出asn
            self.env.cr.execute("select COALESCE(sum(asn_qty),0) from iac_asn_line where po_line_id = %s",(change_line.order_line_id.id,))
            pg_result1 = self.env.cr.fetchall()
            asn_qty = pg_result1[0][0]

            #internal_comment 不能输入超过200个字
            if ('internal_comment' in values)  and len(values["internal_comment"])>200:
                raise UserError(_(u'Internal Comment 太长，不能超过200个字！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))
            #判断原始条目的规则校验
            if change_line.item_type=='ori_item':
                #当前条目是否已经入料,已经入料的情况下不能修改价格
                if ('new_price' in values) and (values["new_price"]!=change_line.ori_price) and gr_qty>0:
                    raise UserError(_(u'已经入料的部分材料不能修改价格！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))
                #if ('new_qty' in values) and (values["new_qty"]>change_line.new_qty):
                #    raise UserError(_(u'不能改大订单行的数量！'))
                if ('new_qty' in values) and (values["new_qty"]<gr_qty):
                    raise UserError(_(u'条目数量不能小于已经入料的数量！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))
                if ('new_qty' in values) and (values["new_qty"]<change_line.order_line_id.asn_qty):
                    raise UserError(_(u'条目数量不能小于已经开立ASN的数量！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))

            if ('new_price' in values) and (not values.get('new_price', False) or values.get('new_price', False) < 0):
                raise UserError(_(u'价格必须大于零！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))
            if ('new_qty' in values) and (not values.get('new_qty', False) or values.get('new_qty', False) < 0):
                raise UserError(_(u'数量必须大于零！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))

            if ('new_devlivery_date' in values) and (values.get('new_devlivery_date', False)==False):
                raise UserError(_(u'交期不能为空！ORDER LINE CODE 为 %s '%(change_line.order_line_code,)))

            #校验删除条目的是否合法
            if ('odoo_deletion_flag' in values):
                odoo_deletion_flag=values.get('odoo_deletion_flag', False)
                if change_line.ori_deletion_flag<>odoo_deletion_flag and change_line.ori_deletion_flag==False:
                    #拆单的条目不能删除
                    if change_line.item_type=='split_item':
                        raise UserError("拆单的条目不能标记删除! ORDER LINE CODE 为 %s"%(change_line.order_line_code,))
                    #新增的条目不能标记删除
                    if change_line.item_type=='new_add':
                        raise UserError("新建的条目不能标记删除! ORDER LINE CODE 为 %s"%(change_line.order_line_code,))
                    if gr_qty>0:
                        raise UserError("已经入料的PO ITEM不能删除!ORDER LINE CODE 为 %s"%(change_line.order_line_code,) )
                    if asn_qty>0:
                        raise UserError("已经开出asn的PO ITEM不能删除!ORDER LINE CODE 为 %s" % (change_line.order_line_code,))
            #如果修改价格,根据币别对价格进行四舍五入
            if ('new_price' in values):
                digits_count=change_line.order_id.currency_id.decimal_setting
                new_price=values.get("new_price")
                values["new_price"]=round(new_price,digits_count)

            #检查金额是否合法
            digits_count=change_line.order_id.currency_id.decimal_setting
            min_amount=math.pow(10,-1*digits_count)
            if change_line.line_amount<min_amount:
                raise UserError("订单行的金额不能小于当前货币的最小金额单位 %s !ORDER LINE CODE 为 %s"%(min_amount,change_line.order_line_code,) )






        # index = 0
        # quantity = 0
        # if values.get('new_delivery_schedule_ids', False):
        #     for schedule in values.get('new_delivery_schedule_ids', False):
        #         index = index + 1
        #         if schedule[2]:
        #             if schedule[2]['quantity'] <= 0:
        #                 raise UserError(_(u'数量必须大于零！'))
        #             quantity = quantity + schedule[2]['quantity']
        #         else:
        #             if (type(schedule[1]) is types.IntType):
        #                 quantity = quantity + self.env['iac.delivery.schedule.change'].browse(schedule[1]).quantity
        #     if index == 0:
        #         raise UserError(_(u'至少有一个Schedule Line！'))
        #     if quantity > self.ori_qty:
        #         raise UserError(_(u'数量不可超过原始数量！'))

        return_result=super(IacPurchaseOrderLineChange, self).write(values)

        #计算change_factor
        change_factor_vals=self._get_change_factor()
        #保存change_factor
        return_result=super(IacPurchaseOrderLineChange, self).write(change_factor_vals)

        #获取异动状态
        change_vals=self.get_change_state()

        #保存修改状态
        return_result=super(IacPurchaseOrderLineChange, self).write(change_vals)

        #计算变更之后的增量或者减量的数量
        #有新增行的情况下，也会增加数量
        if self.item_type=="new_add" and self.odoo_deletion_flag!=False:
            qty_vals={
                "increase_qty":self.new_qty,
                "decrease_qty":0,
            }
            return_result=super(IacPurchaseOrderLineChange, self).write(qty_vals)

        #数量增加
        if self.change_state=="restore_po_line" or self.change_state=='add_po_line':
            qty_vals={
                "increase_qty":self.new_qty,
                "decrease_qty":0,
            }
            return_result=super(IacPurchaseOrderLineChange, self).write(qty_vals)

        #数量减少
        if self.change_state=="cancel_po_line" or self.change_state=="qty_down":
            qty_vals={
                "increase_qty":0,
                "decrease_qty":self.new_qty,
            }
            if self.change_state=="cancel_po_line":
                qty_vals["cancel_qty"]=self.new_qty

            return_result=super(IacPurchaseOrderLineChange, self).write(qty_vals)
        #拆单item数量减少的情况
        if self.item_type=='ori_item' and self.next_item_id.exists():
            qty_vals={
                "increase_qty":0,
                "decrease_qty":self.new_qty-self.ori_qty,
                }
            return_result=super(IacPurchaseOrderLineChange, self).write(qty_vals)
        return return_result

    #@api.one
    #@api.constrains('part_id','new_price','new_qty','new_delivery_date')
    #def uniq_check_po_line_change(self):
    #    if  self.change_id.exists() and self.change_id.vendor_id.exists() and self.part_id.exists():
    #        vendor_id=self.change_id.vendor_id.id
    #        part_id=self.part_id.id
    #        last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
    #        if not last_price_rec.exists():
    #            raise UserError('Part No is ( %s ) has no price in inforecord_history'% (self.part_id.part_no,))

    @api.multi
    def unlink(self):
        raise UserError(_(u'不能直接删除一行。请打开后设置删除标记！'))



    @api.onchange('new_price')
    def _onchange_new_price(self):
        if self.new_price < 0:
            raise UserError(_(u'价格必须大于零！'))

    @api.onchange('new_qty')
    def _onchange_new_qty(self):
        if self.new_qty < 0:
            raise UserError(_(u'价格必须大于零！'))

    @api.onchange('add_item_qty')
    def _onchange_add_item_qty(self):
        if len(self.ids)==0:
            return
        if self.add_item_qty < 0:
            raise UserError(_(u'数量必须大于零！'))
        elif self.add_item_qty > self.open_qty:
            raise UserError(_(u'数量不能大于Open Quantity！！'))

    @api.model
    def default_get(self, fields):
        default_result= super(IacPurchaseOrderLineChange,self).default_get(fields)
        default_result["order_id"]=self._context.get("order_id",False)
        default_result["order_id"]=self._context.get("order_line_id",False)
        return default_result



    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('vendor_part_no', '=ilike', name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        res = self.search(domain + args, limit=limit)
        return res.name_get()


    @api.model
    def get_change_state(self):
        """
        当前对象为order_line_change 获取当前对象的变化状态
        """
        #进行异动状态判断
        change_vals={
            "change_state":"no_change",
            }

        #新增一个item的情况
        if self.item_type=="new_add" and self.odoo_deletion_flag==self.ori_deletion_flag and self.odoo_deletion_flag==False:
            change_vals["change_state"]="add_po_line"
            return change_vals

        if self.odoo_deletion_flag!=self.ori_deletion_flag:
            if self.odoo_deletion_flag==True:
                change_vals["change_state"]="cancel_po_line"
            else:
                change_vals["change_state"]="restore_po_line"
            return change_vals

        if self.item_type=="split_item":
            if self.ori_price<self.new_price:
                change_vals["change_state"]="cost_up_split"
            if self.ori_price>self.new_price:
                change_vals["change_state"]="cost_down_split"
            return change_vals

        if self.item_type=="ori_item":
            if self.ori_qty>self.new_qty:
                change_vals["change_state"]="qty_down"
                return change_vals
            if self.ori_qty<self.new_qty:
                change_vals["change_state"]="qty_up"
                return change_vals
            if self.ori_price<self.new_price:
                change_vals["change_state"]="cost_up"
                return change_vals
            if self.ori_price>self.new_price:
                change_vals["change_state"]="cost_down"
                return change_vals

            return change_vals


        if self.item_type=="new_add":
            if self.ori_price<self.new_price:
                change_vals["change_state"]="cost_up"
                return change_vals
            if self.ori_price>self.new_price:
                change_vals["change_state"]="cost_down"
                return change_vals
            if self.ori_qty>self.new_qty:
                change_vals["change_state"]="qty_down"
                return change_vals
            return change_vals
        return change_vals

    @api.model
    def create(self, vals):
        result=super(IacPurchaseOrderLineChange,self).create(vals)
        if result.last_price_unit not in [1000,10000]:
            raise UserError("Last Price Unit Must Be 1000 or 10000")
        #补充vendor_id currency_id order_date
        update_vals={
            "vendor_id":result.change_id.vendor_id.id,
            "currency_id":result.change_id.currency_id.id,
            "order_date":result.change_id.order_date,
        }
        super(IacPurchaseOrderLineChange,result).write(update_vals)

        #如果新建的order_line_change 没有订单行编码,那么新建订单行编码
        if result.order_line_code==False:
            self.env.cr.execute("select cast((COALESCE(max((to_number(order_line_code,'99999'))),0)+10) as varchar),        " \
                                " lpad(cast((COALESCE(max((to_number(order_line_code,'99999'))),0)+10) as varchar),5,'0')       " \
                                " line_code from iac_purchase_order_line_change where change_id=%s"
                ,(result.change_id.id,))
            result_line_code =  self.env.cr.fetchall()


            readonly_vals={
                "order_line_code":result_line_code[0][0],
                "order_line_code_2":result_line_code[0][1],
                "order_code":result.order_id.document_erp_id,
                }

            #result.write(readonly_vals)
            write_result=super(IacPurchaseOrderLineChange,result).write(readonly_vals)

        #校验同一个料号只能有一个新增项目
        self.env.cr.execute("select count(*) from iac_purchase_order_line_change where change_id=%s and part_id=%s and item_type='new_add'"
            ,(result.change_id.id,result.part_id.id))
        count_result=self.env.cr.fetchall()
        if count_result[0][0]>1:
            raise UserError(u"同一个料号在只能存在一个新建的订单行项目")

        #处理数据来源问题,将原生的item和刚新建的item建立关联关系
        self.env.cr.execute("select id from iac_purchase_order_line_change where change_id=%s and part_id=%s and item_type='ori_item'"
            ,(result.change_id.id,result.part_id.id))

        for change_line_id in self.env.cr.fetchall():
            change_line=self.env["iac.purchase.order.line.change"].browse(change_line_id)
            change_line.write({"next_item_id":result.id})

        #新建记录的情况下，补充info_record_his关联数据信息
        if not result.price_his_id.exists():
            vendor_id=result.order_id.vendor_id.id
            part_id=result.part_id.id
            last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
            if last_price_rec.exists():
                price_vals={
                    "price_control":last_price_rec.price_control,
                    "price_his_id":last_price_rec.id,
                    "last_price":last_price_rec.price,
                }
                result.write(price_vals)

        #修改异动状态
        result.write({"change_state":"add_po_line"})
        return result


    def _get_po_line_change_factor(self):
        """
        获取order_line_change对象的 规则参数
        返回值有1个,返回一个存储规则参数的字典
        :param order_change:
        :return:
        """
        rule_vals={}

        price_factor = ''
        quantity_factor = ''
        change_delivery = ''
        item_factor=''
        ori_price=self.ori_price/self.price_unit
        new_price=self.new_price/self.last_price_unit
        ref_price=0
        price_control=''
        if not self.price_his_id.exists():
            vendor_id=self.order_id.vendor_id.id
            part_id=self.part_id.id
            last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
            if not last_price_rec.exists():
                ref_price=0
                price_control=''
            else:
                ref_price=last_price_rec.price/last_price_rec.price_unit
                price_control=last_price_rec.price_control
        else:
            ref_price=self.price_his_id.price/self.price_his_id.price_unit
            price_control=self.price_his_id.price_control
        if  not self.odoo_deletion_flag:
            if new_price>ori_price:
                price_factor='up'
            elif new_price < ori_price:
                price_factor = 'down'

            #if self.new_qty > self.ori_qty:
            #    quantity_factor = 'up'
            #
            #elif self.new_qty < self.ori_qty:
            #    quantity_factor = 'down'

            quantity_factor=self.change_factor_qty

            if self.new_delivery_date > self.ori_delivery_date:
                change_delivery = 'no'

            elif self.new_delivery_date < self.ori_delivery_date:
                change_delivery = 'yes'

        rule_vals={
            "price_factor":price_factor,
            "quantity_factor":quantity_factor,
            "change_delivery":change_delivery,
            "item_factor":item_factor,
            "price_control":price_control,
            "ori_price":str(ori_price),
            "new_price":str(new_price),
            "ref_price":str(ref_price),
            }
        return rule_vals

    @api.one
    def apply_po_line_audit(self):
        """
        记录当前po line 的audit 状态
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
        以上的状态变更的情况下备份记录po_line的变化情况
        :return:
        """
        po_line_audit_vals={
            "order_id":self.order_id.id,
            "order_line_id":self.order_line_id.id,
            "order_line_change_id":self.id,
            "currency_id":self.order_id.currency_id.id,
            "plant_id":self.order_id.plant_id.id,
            "buyer_id":self.order_id.buyer_id.id,
            "vendor_id":self.order_id.vendor_id.id,
            "part_id":self.part_id.id,
            "division_id":self.part_id.division_id.id,
            "source_code":self.part_id.sourcer,
            "order_code":self.order_id.document_erp_id,
            "order_line_code":self.order_line_code,
            "user_login_code":self.env.user.login,
            "user_id":self.env.user.id,
            "vendor_code":self.order_id.vendor_id.vendor_code,
            "part_no":self.part_id.part_no,
            "plant_code":self.order_id.vendor_id.plant.plant_code,
            "buyer_code":self.order_id.buyer_id.buyer_erp_id,
            "division_code":self.part_id.division_id.division,
            "currency":self.currency_id.name,
            "ori_delivery_date":self.ori_delivery_date,
            "new_delivery_date":self.new_delivery_date,
            "ori_qty":self.ori_qty,
            "new_qty":self.new_qty,
            "ori_price":self.ori_price,
            "new_price":self.new_price,
            "ori_price_unit":self.price_unit,
            "new_price_unit":self.last_price_unit,
            "ori_deletion_flag":self.ori_deletion_flag,
            "new_deletion_flag":self.odoo_deletion_flag,
            "audit_source":"po_change",
        }
        #根据po header状态补充相关字段
        if self.change_id.state=="pending":
            po_line_audit_vals["action_type"]="po_change"
        if self.change_id.state=="webflow_error":
            po_line_audit_vals["action_type"]="webflow_error"
            po_line_audit_vals["state_msg"]=self.change_id.state_msg
        elif self.change_id.state=="to_approve":
            po_line_audit_vals["action_type"]="send_to_webflow"
        elif self.change_id.state=="unapproved":
            po_line_audit_vals["action_type"]="denied_by_webflow"
        elif self.change_id.state=="to_sap":
            #调用send_to_workflow成功后PO header 的状态为to_sap，所以认为已经送webflow成功
            po_line_audit_vals["action_type"]="send_to_sap"
        elif self.change_id.state=="sap_error":
            po_line_audit_vals["action_type"]="send_sap_error"
            po_line_audit_vals["state_msg"]=self.order_id.state_msg
        elif self.change_id.state=="erp_accepted":
            po_line_audit_vals["action_type"]="wait_vendor_confirm"
        self.env["iac.purchase.order.line.audit"].create(po_line_audit_vals)

class IacDeliveryScheduleChange(models.Model):
    """
    PO Line Delivery Change从表
    """
    _name = "iac.delivery.schedule.change"
    _description = "Delivery Schedule Change"
    _order = 'sequence'

    change_id = fields.Many2one('iac.purchase.order.change', related='line_change_id.change_id', string="Change Order ID", readonly=True)
    line_change_id = fields.Many2one('iac.purchase.order.line.change', string="Change Order Line ID", readonly=True)# 主从结构外键
    order_id = fields.Many2one('iac.purchase.order', related='line_change_id.order_id', string="PO Number", readonly=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', related='line_change_id.order_line_id', string="PO Line Number", readonly=True)
    sequence = fields.Integer(string="Schedule#", default=1)
    qty_received = fields.Float(string='Received Quantity')
    delivery_date = fields.Date(string="Delivery Date")  # 当前行料号该schedule的交期
    quantity = fields.Float(string='Quantity')  # 当前行料号该schedule的数量

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity < 0:
            raise UserError(_(u'数量必须大于零！'))

    @api.multi
    def unlink(self):
        if len(self.line_change_id.new_delivery_schedule_ids) <= 1:
            raise UserError(_(u'至少有一个Schedule Line！'))
        else:
            return super(IacDeliverySchedule, self).unlink()






class IacPurchaseOrderLineChangeMaterialMaster(models.Model):
    """PO Change从表，同时是PO Line Delivery Change主表"""
    _name = "iac.purchase.order.line.change.material.master"
    _inherit="material.master"
    _table="material_master"
    _description = "Material Mater In Po Line Change"
    _order = 'id desc'

    @api.model
    def search(self,args, offset=0, limit=None, order=None, count=False):
        if "change_id" in self._context:
            change_id=self._context["change_id"]
            self.env.cr.execute("select distinct t.part_id from iac_purchase_order_line_change t where change_id=%s ",(change_id,))
            part_ids=[]
            part_vals_list=self.env.cr.fetchall()
            for part_vals in part_vals_list:
                part_ids.append(part_vals[0])
            result=self.browse(part_ids)
            return result

        result=super(IacPurchaseOrderLineChangeMaterialMaster, self).search(args, offset, limit, order, count=count)
        return result


class IacPurchaseOrderChangeEdit(models.Model):
    """当前模型用做指定po中筛选part信息
    """
    _name = "iac.purchase.order.change.edit"
    _inherit="iac.purchase.order.change"
    _table="iac_purchase_order_change"
    _description = "PO Change"
    _order = 'id desc'

    part_id = fields.Many2one('iac.purchase.order.line.change.material.master', string="Use This Field To Filter Part Info")


    @api.multi
    def button_to_add_po_line(self):
        """新建订单行项目"""
        #action_view_iac_purchase_order_line_change_add_view_form
        action = self.env.ref('oscg_po.action_view_iac_purchase_order_line_change_add_view_form')
        order_change_id = self.id
        part_id=0
        last_line_change=False
        if not self.part_id.exists():
            #没有指定part_id,自动选择一个条目进行匹配
            domain=[('change_id','=',self.id),('item_type','=','ori_item')]
            last_line_change=self.env["iac.purchase.order.line.change"].search(domain,limit=1,order='id desc')
        else:
            #选定part_id的情况
            domain=[('change_id','=',self.id),('item_type','=','ori_item')]
            domain+=[('part_id','=',self.part_id.id)]
            last_line_change=self.env["iac.purchase.order.line.change"].search(domain,limit=1,order='id desc')

        if not last_line_change.exists():
            raise UserError(u'无法找到订单条目信息')

        part_id=last_line_change.part_id.id

        #获取最新的价格

        vendor_id=self.order_id.vendor_id.id
        last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
        new_price=0
        price_unit=0
        if last_price_rec.exists():
            new_price=last_price_rec.price
            price_unit=last_price_rec.price_unit
        else:
            raise UserError('Part No is ( %s ) has no price in inforecord_history'% (last_line_change.part_id.part_no,))


        add_item_context={
            "order_change_id":order_change_id,
            "part_id":part_id,
            "division":last_line_change.part_id.division_id.division,
            "part_no":last_line_change.part_id.part_no,
            "vendor_id":self.order_id.vendor_id.id,
            "order_id":self.order_id.id,
            "order_line_id":last_line_change.order_line_id.id,
            "price_unit":price_unit,
            "last_price_unit":price_unit,
            "storage_location":last_line_change.storage_location,
            "tax_code":last_line_change.tax_code,
            "price_date":last_line_change.price_date,
            "unit":last_line_change.unit,
            'ori_qty':0,
            'ori_price':last_line_change.new_price,
            'ori_delivery_date':last_line_change.new_delivery_date,
            'new_delivery_date':last_line_change.new_delivery_date,
            'new_price':new_price,
            }

        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target':  "new",
            'context': add_item_context,
            'res_model': action.res_model,
            }
        return action_window




    @api.multi
    def button_to_return(self):
        """返回到po change form"""
        #action_view_iac_purchase_order_line_change_add_view_form
        action = self.env.ref('oscg_po.action_view_purchase_order_change_form_view')
        order_id = self.order_id.id

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_order_id': " + str(order_id) + "}",
            'res_model': action.res_model,
            'res_id':self.id,
            }

    @api.model
    def default_get(self, fields):
        default_result= super(IacPurchaseOrderLineChangeAdd,self).default_get(fields)
        default_result["part_id"]=self._context.get("part_id",False)
        default_result["change_id"]=self._context.get("order_change_id",False)
        return default_result

    @api.multi
    def button_cancel(self):
        pass

    @api.multi
    def button_recorver(self):
        pass

    @api.onchange('part_id')
    def onchange_part_id(self):
        #self=self.browse(self.id)
        #print "change_id is: %s" %(self._origin.id,)
        #print "part_id is: %s" %(self.part_id.id,)
        change_line_ids=self.env["iac.purchase.order.line.change"].search([('change_id','=',self._origin.id),('part_id','=',self.part_id.id)])
        self.line_ids=change_line_ids


    @api.multi
    def write(self, values):
        if "line_ids" in values:
            for change_line_vals in values["line_ids"]:
                if change_line_vals[2]!=False:
                    change_line=self.env["iac.purchase.order.line.change"].browse(change_line_vals[1])
                    change_line.write(change_line_vals[2])
            del values["line_ids"]

        order_change_vals={}
        order_change_vals.update(values)
        #if "part_id" in order_change_vals:
        #    del order_change_vals["part_id"]
        result = super(IacPurchaseOrderChangeEdit, self).write(order_change_vals)
        return result

class IacPurchaseOrderLineChangeAdd(models.Model):
    """当前模型用来增加指定po的指定part"""
    _name = "iac.purchase.order.line.change.add"
    _inherit = "iac.purchase.order.line.change"
    _table="iac_purchase_order_line_change"
    _description = "PO Line Change"
    _order = 'id desc'
    part_id = fields.Many2one('iac.purchase.order.line.change.material.master', string="Part Info")

    @api.model
    def create(self, vals):
        #数据校验 交期不能为空

        result=super(IacPurchaseOrderLineChangeAdd,self).create(vals)
        #200709 ning 调整 校验在已存在的 change po line中有没有当前料号存在删单或者恢复订单 begin
        change_line_objs = self.env['iac.purchase.order.line.change'].search(
            [('change_id','=',result.change_id.id),('part_id','=',vals.get('part_id',False)),
             ('id','!=',result.id)])
        part_no = self.env['material.master'].browse(vals.get('part_id',False)).part_no
        for change_line in change_line_objs:
            if change_line.ori_deletion_flag != change_line.odoo_deletion_flag:
                raise UserError('part no:'+part_no+'不能在删单或者恢复订单的同时拆单！')
        #end
        #校验数量是否合法,不能超过原始订单总数量,对每一个材料来说
        result.change_id.uniq_check_po_change()

        return result


    @api.multi
    def write(self, vals):
        result=super(IacPurchaseOrderLineChangeAdd,self).write(vals)
        return result

    @api.model
    def default_get(self, fields):
        default_result= super(IacPurchaseOrderLineChangeAdd,self).default_get(fields)
        default_result["part_id"]=self._context.get("part_id",False)
        default_result["division"]=self._context.get("division",False)
        default_result["change_id"]=self._context.get("order_change_id",False)
        default_result["vendor_id"]=self._context.get("vendor_id",False)

        default_result["price_unit"]=self._context.get("price_unit",False)
        default_result["last_price_unit"]=self._context.get("price_unit",False)
        default_result["storage_location"]=self._context.get("storage_location",False)
        default_result["tax_code"]=self._context.get("tax_code",False)
        default_result["unit"]=self._context.get("unit",False)
        default_result["price_date"]=self._context.get("price_date",False)
        default_result["item_type"]="new_add"

        default_result["ori_qty"]=self._context.get('ori_qty',False)
        default_result["ori_price"]=self._context.get('ori_price',False)
        default_result["ori_delivery_date"]=self._context.get('ori_delivery_date',False)
        default_result["new_delivery_date"]=self._context.get('new_delivery_date',False)
        default_result["new_price"]=self._context.get('new_price',False)
        default_result["order_id"]=self._context.get("order_id",False)
        default_result["order_line_id"]=self._context.get("order_line_id",False)
        vendor_id=self._context.get("vendor_id",False)
        part_id=default_result["part_id"]
        self.env["iac.purchase.order"].browse(self._context.get('order_id'))

        return default_result

    @api.multi
    def button_to_return(self):
        """新建订单行项目"""
        #action_view_iac_purchase_order_line_change_add_view_form
        #action = self.env.ref('oscg_po.action_view_purchase_order_change_form_view')
#
        #return {
        #    'name': action.name,
        #    'help': action.help,
        #    'type': action.type,
        #    'view_type': action.view_type,
        #    'view_mode': action.view_mode,
        #    'target': action.target,
        #    'res_model': action.res_model,
        #    'res_id':self.change_id.id
        #}


        action = self.env.ref('oscg_po.action_view_purchase_order_line_change_edit_view_form')


        action_data={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': 'form',
            'target': action.target,
            'res_model': action.res_model,
            'res_id':self.change_id.id
        }

        return action_data

    @api.onchange('part_id')
    def _onchange_part_id(self):
        """
        修改part_id时获取最新的价格信息
        :return:
        """
        vendor_id=self._context.get("vendor_id",False)
        change_id=self._context.get("change_id",False)
        part_id=self.part_id.id
        last_price_rec=self.env["inforecord.history"].get_last_price_rec(vendor_id,part_id)
        if last_price_rec.exists():
            self.new_price=last_price_rec.price
            self.last_price_unit=last_price_rec.price_unit
        else:
            self.new_price=0

        #获取历史价格
        domain=[('change_id','=',change_id),('part_id','=',part_id)]
        last_part_info=self.env["iac.purchase.order.line.change"].search(domain,order="create_date desc",limit=1)
        if last_part_info.exists():
            self.ori_price=last_part_info.new_price
            self.price_unit=last_part_info.last_price_unit
