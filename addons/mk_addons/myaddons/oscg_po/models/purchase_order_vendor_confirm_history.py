# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval
import odoo
import threading
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)

def odoo_env(func,**kwargs):
    def __decorator(self,**kwargs):    #add parameter receive the user information
        db_name = self.env.registry.db_name
        db = odoo.sql_db.db_connect(db_name)
        threading.current_thread().dbname = db_name
        cr = db.cursor()

        try:
            with api.Environment.manage():
                try:
                    env=api.Environment(cr, SUPERUSER_ID, {})
                    self.env=env
                    func(self,**kwargs)

                except:
                    traceback.print_exc()
                    raise
            cr.commit()
            cr.close()
        except:
            cr.commit()
            cr.close()
            raise

    return __decorator

class IacPurchaseOrderVendorConfirmHis(models.Model):
    """PO Vendor Confirm History主表"""
    _name = "iac.purchase.order.vendor.confirm.his"
    _description = "Purchase Order Vendor Confirm History"
    _order = 'id desc'
    order_id=fields.Many2one("iac.purchase.order",string="Purchase Order")
    confirm_line_ids = fields.One2many("iac.purchase.order.vendor.confirm.line.his", "vendor_confirm_id", string="PO Vendor Confirm Line")
    state = fields.Selection([
                                 ('new_po_wait_confirm', 'New Po Wait Confirm'),#新po 到达需要进行第一次confirm
                                 ('chg_po_wait_confirm', 'Change Po Wait Confirm'),#发生了po Change 需要进行confirm
                                 ('chg_before_confirm', 'Change po Before Confirm'), #po change 后产生的需要confirm,在vendor confirm 之前又发生了po change,当前的单据就进入未确认的历史状态
                                 ('vendor_confirmed', 'Vendor Confirmed'),#Vendor Confirmed 客户确认订单信息
                                 ('vendor_exception', 'Vendor Exception'),#Vendor Exception 客户驳回订单信息
    ], string='Status', readonly=True, index=True, copy=False, default='new_po_wait_confirm', track_visibility='onchange')
    data_type = fields.Selection([
                                 ('current', 'Current'),
                                 ('history', 'History'),#数据记录类型，当前有效还是已经是历史数据
    ], string='Data Type', readonly=True, index=True, copy=False, default='current', track_visibility='onchange')
    name = fields.Char(string="Purchase Order",  index=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    purchase_org_id = fields.Many2one('vendor.plant', string="Purchase Org", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    changed = fields.Boolean(string='Is Changed', default=False)
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记
    ori_payment_term = fields.Many2one('payment.term',  string='Original Payment Term')
    ori_incoterm_id = fields.Many2one('incoterm',  string='Original Incoterm')
    ori_incoterm1 = fields.Char( string="Original Incoterm Destination")

    new_payment_term = fields.Many2one('payment.term', string='New Payment Term')
    new_incoterm = fields.Many2one('incoterm', string='New Incoterm')
    new_incoterm1 = fields.Char(string="New Incoterm Destination")
    payment_term_id = fields.Many2one('payment.term', string="Payment Term")
    incoterm_id = fields.Many2one('incoterm', string="Incoterm")
    incoterm1 = fields.Char(string="Incoterm Destination")
    order_type = fields.Char(string="Order Type")
    contact_person = fields.Char(string="Contact Person")
    contact_phone = fields.Char(string="Contact Phone")
    currency = fields.Char(string="Currency")
    order_reason = fields.Char(string="Order Reason")
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location', index=True)
    order_amt = fields.Float(string='Order Amount',compute='_compute_order_amt')# SAP传过来的订单总额
    source_type = fields.Selection([
                                 ('po_new', 'PO New'),
                                 ('po_change', 'PO Change'),#数据记录类型，当前有效还是已经是历史数据
    ], string='Data Type', readonly=True, index=True, copy=True, default='po_new', track_visibility='onchange')
    change_id=fields.Many2one("iac.purchase.order.change",string="PO Change")
    po_change_type = fields.Selection([('new_po','New PO'),
                                    ('price_change','Price change'),
                                    ('quantity_change','Quantity change'),
                                    ('quantity_and_price_change','Quantity and Price change'),
                                    ('no_change','No change')])#新增字段，根据po change type来分组
    order_date = fields.Date(string="PO Date")
    state_msg = fields.Char(string="Status Message")
    is_submit = fields.Boolean(string="Is Submit",default=False)
    is_vendor_submit = fields.Boolean(string="Is Submit",default=False)#vendor 点击submit按钮
    is_change_submit = fields.Boolean(string="Is Submit",default=False)#发生po_change的情况下,当前记录提交产生新的vendor_confirm

    @api.depends('confirm_line_ids')
    def _compute_order_amt(self):
        for order in self:
            for line in order.confirm_line_ids:
                order.order_amt=order.order_amt+line.line_amount

    @api.model
    def po_confirm_reset_to_vendor(self,order_id):
        """
        传入order_id,buyer 重新设置vendor confirm 要求vendor 重新confirm
        :param order_id:
        :return:
        """
        old_confirm_header=self.get_last_submit_rec(order_id)
        if not old_confirm_header:
            raise UserError("The Last Vendor Confirm History Record Not Found!")
        po_confirm_state=''
        if old_confirm_header.order_id.changed is True:
            po_confirm_state='chg_po_wait_confirm'
        else:
            po_confirm_state='new_po_wait_confirm'

        header_vals={
            "data_type":"current",
            "is_vendor_submit":False,
            "is_submit":False,
            "is_change_submit":False,
            "state":po_confirm_state
        }
        line_vals={
            "data_type":"current",
            "is_vendor_submit":False,
            "is_submit":False,
            "is_change_submit":False,
        }
        #复制header
        new_confirm_header=old_confirm_header.copy()
        new_confirm_header.write(header_vals)
        #更新旧记录的状态
        old_confirm_header.write({"data_type":"history"})
        old_confirm_header.confirm_line_ids.write({"data_type":"history"})
        for old_confirm_line in old_confirm_header.confirm_line_ids:
            new_confirm_line=old_confirm_line.copy()
            line_vals["state"]=old_confirm_line.state
            new_confirm_line.write(line_vals)


    @api.model
    def po_new_vendor_confirm_create(self,order_id):
        """
        传入order_id 创建Po Vendor Confirm 数据,包括header 和 line 信息
        :param order_id:
        :return:
        """
        header_fields_list=[
            "order_id",
            "state",
            "data_type",
            "name",
            "plant_id",
            "purchase_org_id",
            "vendor_id",
            "vendor_reg_id",
            "changed",
            "odoo_deletion_flag",
            "ori_payment_term",
            "ori_incoterm_id",
            "ori_incoterm1",
            "new_payment_term",
            "new_incoterm",
            "new_incoterm1",
            "payment_term_id",
            "incoterm_id",
            "incoterm1",
            "order_type",
            "contact_person",
            "contact_phone",
            "currency",
            "order_reason",
            "storage_location_id",
            "order_amt",
            "po_change_type",
            "order_date",
            "state_msg"
        ]

        order_rec=self.env["iac.purchase.order"].browse(order_id)
        header_vals={
            "order_id":order_id,
            "state":"new_po_wait_confirm",
            "data_type":"current",
            "source_type":"po_new",
            "name":order_rec.document_erp_id
        }

        new_item_vals={
            "order_id":order_id,
            "state":"wait_vendor_confirm",
            "data_type":"current",
            "source_type":"po_new",
        }

        all_fields_vals = order_rec.copy_data()[0]
        rec_vals={}

        #处理表头信息
        for fields_name in header_fields_list:
            if all_fields_vals.has_key(fields_name):
                rec_vals[fields_name]=all_fields_vals.get(fields_name)
        rec_vals.update(header_vals)
        #处理条目信息
        line_fields_list=[
            "order_id",
            "order_line_id",
            "vendor_confirm_id",
            "selection_flag",
            "state",
            "data_type",
            "vendor_exception_reason",
            "order_line_code",
            "part_id",
            "vendor_part_no",
            "price",
            "price_unit",
            "quantity",
            "delivery_date",
            "vendor_delivery_date",
            "ori_price",
            "ori_qty",
            "ori_delivery_date",
            "new_price",
            "new_qty",
            "new_delivery_date",
            "ori_del_flag",
            "new_del_flag",
            "purchase_req_item_no",
            "division",
            "odoo_deletion_flag",
            "purchase_req_no",
            "storage_location"
        ]

        order_line_ids=self.env["iac.purchase.order.line"].search([('order_id','=',order_id)],order='order_line_code asc')
        if order_line_ids:
            confirm_line_ids=[]
            for order_line in order_line_ids:
                confirm_line_vals={}
                order_line_vals={}
                order_line_vals=order_line.copy_data()[0]
                for fields_name in line_fields_list:
                    if order_line_vals.has_key(fields_name):
                        confirm_line_vals[fields_name]=order_line_vals.get(fields_name)
                new_item_vals["order_line_id"]=order_line.id
                confirm_line_vals.update(new_item_vals)
                confirm_line_ids.append((0,0,confirm_line_vals))
            rec_vals["confirm_line_ids"]=confirm_line_ids
            self.create(rec_vals)
        else:
            raise "PO Line Not Existed!"

    @api.model
    def po_change_vendor_confirm_create(self,order_id):
        """
        传入order_id 创建Po Vendor Confirm 数据,包括header 和 line 信息
        :param order_id:
        :return:
        """
        #查找已经存在的vendor_confirm 数据
        search_domain=[
            ('order_id','=',order_id),
            ('data_type','=','current')
            ]
        current_rec=self.search(search_domain,limit=1)
        #如果当期有效记录存在的情况下，需要根据source_type 进行一些处理
        if current_rec:
            if current_rec.source_type=='po_new':
                current_rec.write({'data_type':"history","is_submit":True,"is_change_submit":True})
                current_rec.confirm_line_ids.write({'data_type':"history","is_submit":True,"is_change_submit":True})
            elif current_rec.source_type=='po_change':
                if current_rec.state=='chg_po_wait_confirm':
                    current_rec.write({'data_type':"history","state":"chg_before_confirm","is_submit":True,"is_change_submit":True})
                    current_rec.confirm_line_ids.write({'data_type':"history","is_submit":True,"is_change_submit":True})
                else:
                    current_rec.write({'data_type':"history","is_submit":True,"is_change_submit":True})
                    current_rec.confirm_line_ids.write({'data_type':"history","is_submit":True,"is_change_submit":True})

        header_fields_list=[
            "order_id",
            "state",
            "data_type",
            "name",
            "plant_id",
            "purchase_org_id",
            "vendor_id",
            "vendor_reg_id",
            "changed",
            "odoo_deletion_flag",
            "ori_payment_term",
            "ori_incoterm_id",
            "ori_incoterm1",
            "new_payment_term",
            "new_incoterm",
            "new_incoterm1",
            "payment_term_id",
            "incoterm_id",
            "incoterm1",
            "order_type",
            "contact_person",
            "contact_phone",
            "currency",
            "order_reason",
            "storage_location_id",
            "order_amt",
            "po_change_type",
            "order_date",
            "state_msg"
        ]

        order_rec=self.env["iac.purchase.order"].browse(order_id)
        header_vals={
            "order_id":order_id,
            "state":"chg_po_wait_confirm",
            "data_type":"current",
            "source_type":"po_change",
            "change_id":order_rec.last_change_id.id,
            "name":order_rec.document_erp_id
        }
        new_item_vals={
            "order_id":order_id,
            "data_type":"current",
            "source_type":"po_change",
            "change_id":order_rec.last_change_id.id,
            "state":"wait_vendor_confirm",
        }


        all_fields_vals = order_rec.copy_data()[0]
        rec_vals={}

        #处理表头信息
        for fields_name in header_fields_list:
            if all_fields_vals.has_key(fields_name):
                rec_vals[fields_name]=all_fields_vals.get(fields_name)
        rec_vals.update(header_vals)
        #处理条目信息
        line_fields_list=[
            "order_id",
            "order_line_id",
            "vendor_confirm_id",
            "selection_flag",
            "state",
            "data_type",
            "vendor_exception_reason",
            "order_line_code",
            "part_id",
            "vendor_part_no",
            "price",
            "price_unit",
            "quantity",
            "delivery_date",
            "vendor_delivery_date",
            "ori_price",
            "ori_qty",
            "ori_delivery_date",
            "new_price",
            "new_qty",
            "new_delivery_date",
            "ori_del_flag",
            "new_del_flag",
            "purchase_req_item_no",
            "division",
            "odoo_deletion_flag",
            "purchase_req_no",
            "storage_location"
        ]

        order_line_ids=self.env["iac.purchase.order.line"].search([('order_id','=',order_id)],order='order_line_code asc')
        if order_line_ids:
            confirm_line_ids=[]
            for order_line in order_line_ids:
                confirm_line_vals={}
                order_line_vals={}
                order_line_vals=order_line.copy_data()[0]
                for fields_name in line_fields_list:
                    if order_line_vals.has_key(fields_name):
                        confirm_line_vals[fields_name]=order_line_vals.get(fields_name)

                new_item_vals["order_line_id"]=order_line.id
                if order_line_vals.has_key("last_order_line_change_id"):
                    new_item_vals["change_line_id"]=order_line_vals.get("last_order_line_change_id")
                confirm_line_vals.update(new_item_vals)
                confirm_line_ids.append((0,0,confirm_line_vals))
            rec_vals["confirm_line_ids"]=confirm_line_ids
            self.create(rec_vals)
        else:
            raise "PO Line Not Existed!"

    @api.one
    def button_set_all_exception(self):
        """
        遍历当前订单的条目，对所有的条目设置成为 Vendor Exception
        :return:
        """
        self.write({"state":"vendor_exception"})
        for po_confirm_line in self.confirm_line_ids:
            po_confirm_line.write({"state":"vendor_exception"})
        for order_line in self.order_id.order_line:
            order_line.with_context(state_change=True).write({"state":"vendor_exception"})

    @api.one
    def button_set_all_confirm(self):
        """
        遍历当前订单的条目，对所有的条目设置成为Vendor Confirm
        :return:
        """
        self.write({"state":"vendor_confirmed"})
        for po_confirm_line in self.confirm_line_ids:
            po_confirm_line.write({"state":"vendor_confirmed"})
        for order_line in self.order_id.order_line:
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
        for order_confirm in self:
            for order_line_confirm in order_confirm.confirm_line_ids:
                if order_line_confirm.state in  ['wait_vendor_confirm']:
                    raise UserError("order code is %s ,order line code is %s need to be confirmed" %(order_confirm.order_id.document_erp_id,order_line_confirm.order_line_code,))
                if order_line_confirm.state=='vendor_exception' and order_line_confirm.vendor_exception_reason==False:
                    raise UserError("order code is %s ,order line code is %s need to set exception reason" %(order_confirm.order_id.document_erp_id,order_line_confirm.order_line_code,))
                if order_line_confirm.state=='vendor_exception' and order_line_confirm.vendor_delivery_date==False:
                    raise UserError("order code is %s ,order line code is %s need to set vendor delivery date" %(order_confirm.order_id.document_erp_id,order_line_confirm.order_line_code,))

        #更改订单状态,并且导航到相关页面
        #情况1,存在 vendor_exception
        for order_confirm in self:
            #同步更新po的信息
            order_vals={
                        "new_payment_term":order_confirm.new_payment_term.id,
                        "new_incoterm":order_confirm.new_incoterm.id,
                        "new_incoterm1":order_confirm.new_incoterm1,
                        "storage_location_id":order_confirm.storage_location_id.id
                    }
            order_confirm.order_id.sudo().write(order_vals)

            #如果一个条目被确认，那么比较这个订单条目曾经被确认过,为报表提供数据支持
            po_line_confirm_list=self.env["iac.purchase.order.vendor.confirm.line.his"].search([('order_id','=',order_confirm.order_id.id),('state','=','confirmed')])
            if po_line_confirm_list.exists():
                for po_line_confirm in po_line_confirm_list:
                    po_line_confirm.order_line_id.with_context(state_change=True).write({"ever_confirmed":True})
            #更新po_line正式表中的状态信息
            for order_line_confirm in order_confirm.confirm_line_ids:
                order_line_vals={
                    "vendor_delivery_date":order_line_confirm.vendor_delivery_date,
                    "vendor_exception_reason":order_line_confirm.vendor_exception_reason,
                    "state":order_line_confirm.state
                }
                order_line_confirm.order_line_id.with_context(state_change=True).write(order_line_vals)

            #情况1,存在 vendor_exception
            #情况2,存在 wait_vendor_confirm
            #情况3,全部状态为vendor_confirmed
            po_line_confirm_list=self.env["iac.purchase.order.vendor.confirm.line.his"].search([('vendor_confirm_id','=',order_confirm.id),('state','=','vendor_exception')])
            if po_line_confirm_list.exists():
                order_confirm.write({"state":"vendor_exception","is_submit":True,"is_vendor_submit":True})
                order_confirm.confirm_line_ids.write({"is_submit":True,"is_vendor_submit":True})
                order_confirm.order_id.sudo().write({"state":"vendor_exception"})
                if order_confirm.order_id.need_unconfirm==True:
                    self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data_exception(order_confirm.order_id.id)
            else:
                #不存在exception认为全部confirmed
                order_confirm.write({"state":"vendor_confirmed","is_submit":True,"is_vendor_submit":True})
                order_confirm.confirm_line_ids.write({"is_submit":True,"is_vendor_submit":True})
                order_confirm.order_id.sudo().write({"state":"vendor_confirmed"})
                if order_confirm.order_id.need_unconfirm==True:
                    self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data_confirmed(order_confirm.order_id.id)

            #生成po稽核信息
            order_audit_vals={
                "order_id":order_confirm.order_id.id,
                "order_code":order_confirm.order_id.document_erp_id,
                "action_type":order_confirm.order_id.state,
                "user_id":self.env.user.id,
                "user_login_code":self.env.user.login,
                }
            self.env["iac.purchase.order.audit"].sudo().create(order_audit_vals)

            #记录order_line日志,记录vendor_confirm状态
            for order_line in order_confirm.order_id.order_line:
                order_line.apply_po_line_audit()

        vals = {
            'action_type': 'Vendor Confirm PO',
            'vendor_id':self.vendor_id.id
        }
        self.env['iac.supplier.key.action.log'].create(vals)
        self.env.cr.commit()
        #跳转页面到当前视图的Tree 视图
        action = self.env.ref('oscg_po.action_view_po_vendor_confirm_his_list')

        action_window={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': "form",
            'view_mode': "tree,form",
            'target': action.target,
            'domain':action.domain,
            'context':action.context,
            'res_model': action.res_model,
            'search_view_id': self.env.ref("oscg_po.view_iac_purchase_order_vendor_confirm_his_search").id,
        }

        view_id_list=[]
        form_view=self.env.ref("oscg_po.view_po_vendor_confirm_his_form")
        tree_view=self.env.ref("oscg_po.view_po_vendor_confirm_his_list")
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

    def get_last_submit_rec(self,order_id):
        """
        获取最新已经提交的vendor confirm数据
        :param order_id:
        :return:
        """
        domain=[
            ('order_id','=',order_id),
            ('data_type','=',"current"),
            ('is_submit','=',True)
        ]
        rec=self.search(domain,limit=1)
        return rec

    def create_po_confirm_from_exception(self):
        """
        当Vendor 设置po confirm 为exception 时,buyer 把po confirm 返回给vendor 时
        从当前po confirm 复制新建一个,这样可以保留vendor 的操作历史
        :return:
        """
        po_confirm_new=self.copy()
        self.write({"data_type":"history"})
        for confirm_line in self.confirm_line_ids:
            confirm_line.write({"data_type":"history"})

    @odoo_env
    @api.model
    def proc_tans_vendor_confirm(self):
        """
        处理一个组条目的函数调用操作,
        同时写入组条目的日志和多次数据函数的操作日志

        :return:
        """
        #设定默认记录分页记录数量
        def get_page_limit_list( record_count, limit_count):
            page_list = []
            if record_count <= limit_count:
                page_list.append(record_count)
                return page_list

            #计算分页偏移量
            page_limit=0
            record_count_remain=record_count
            while record_count_remain>0:
                if record_count_remain>=limit_count:
                    page_limit=limit_count
                    record_count_remain=record_count_remain-limit_count
                else:
                    page_limit=record_count_remain
                    record_count_remain=0
                page_list.append(page_limit)
            return page_list;
        dict_vals={
            "name":"wang"
        }

        #分页数组，存储sql 语句中的offset 参数
        page_list = []
        select_count="select count(*) from iac_purchase_order"
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        if record_count==0:
            log_msg="record count is zero,job will quit"
            _logger.info(log_msg)
            return

        #获取目标表的总记录数量
        limit_count=1000
        #根据要处理的记录总量,计算每个分页应该处理的记录数量
        page_list = get_page_limit_list(record_count, limit_count)
        start_id=0
        for page_limit in page_list:
            #获取执行的语句
            sql_text="""
            SELECT
                *
            FROM
                "public"."proc_trans_vendor_confirm" (
                    %s,
                    %s
                ) AS (
                    v_last_id int4,
                    v_process_count int4
                )
            """%(start_id,page_limit)
            _logger.info(sql_text)

            #正式执行sql语句
            self.env.cr.execute("""
            SELECT
                *
            FROM
                "public"."proc_trans_vendor_confirm" (
                    %s,
                    %s
                ) AS (
                    v_last_id int4,
                    v_process_count int4
                )
            """,(start_id,page_limit))
            self.env.cr.commit()
            fun_result=self.env.cr.fetchall()


            if len(fun_result)==0:
                err_msg="func name is %s has no return"%("proc_trans_vendor_confirm",)
                _logger.error(err_msg)
                raise err_msg

            for  v_last_id,v_process_count in fun_result:
                log_msg="""execute sp function text is %s ; return last_id is %s,process_count is %s"""%(sql_text,v_last_id,v_process_count)
                _logger.info(log_msg)
                start_id=v_last_id

        log_msg="proc_trans_vendor_confirm function execute successful"
        _logger.info(log_msg)


class IacPurchaseOrderVendorConfirmLineHis(models.Model):
    """PO Vendor Confirm History 明细表"""
    _name = "iac.purchase.order.vendor.confirm.line.his"
    _description = "Purchase Order Line Vendor Confirm History Line"
    _order = 'id desc'

    order_id = fields.Many2one('iac.purchase.order', string="PO", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="PO Line", index=True)
    vendor_confirm_id = fields.Many2one('iac.purchase.order.vendor.confirm.his', string="PO Vendor Confirm", index=True)
    selection_flag = fields.Boolean(string='Select', default=False)#选中标记
    state = fields.Selection([
                                 ('wait_vendor_confirm', 'New Po Wait Confirm'),#新po 到达需要进行第一次confirm
                                 ('chg_before_confirm', 'Change po Before Confirm'), #po change 后产生的需要confirm,在vendor confirm 之前又发生了po change,当前的单据就进入未确认的历史状态
                                 ('vendor_confirmed', 'Vendor Confirmed'),#Vendor Confirmed 客户确认订单信息
                                 ('vendor_exception', 'Vendor Exception'),#Vendor Exception 客户驳回订单信息
    ], string='Status', readonly=True, index=True, default='wait_vendor_confirm',copy=True, track_visibility='onchange')
    data_type = fields.Selection([
                                 ('current', 'Current'),
                                 ('history', 'History'),#数据记录类型，当前有效还是已经是历史数据
    ], string='Data Type', readonly=True, index=True, copy=False, default='current', track_visibility='onchange')
    vendor_exception_reason=fields.Text(string="Vendor Exception Reason")
    order_line_code = fields.Char(string="Order Line Code",index=True)#5位字符串,不足的前面补足零,可以用来订单内部排序使用
    part_id = fields.Many2one('material.master.po.line', 'Part No', index=True)#物料
    vendor_part_no = fields.Char(string="Vendor Part No")
    price = fields.Float(string="Price", precision=(18, 4))# 价格
    price_unit = fields.Integer(string="Price Unit")# 价格单位
    quantity = fields.Float(string='Quantity')#当前行料号总数量
    delivery_date = fields.Date(string="Delivery Date")#交期
    vendor_delivery_date = fields.Date(string="Vendor Delivery Date")  # Vendor确认的交期
    ori_price = fields.Float(string='Original Price', help="The Original price to purchase a product")# 原价格
    ori_qty = fields.Float(string='Original Quantity')# 原数量
    ori_delivery_date = fields.Date(string="Original Delivery Date")  # 原交期
    new_price = fields.Float('New Price',  help="The New price to purchase a product")# 新价格
    new_qty = fields.Float(string='New Quantity')# 新数量
    new_delivery_date = fields.Date(string="New Delivery Date")  # po line变更交期的最长交期
    ori_del_flag=fields.Boolean(string='Ori Del Flag')
    new_del_flag=fields.Boolean(string='New Del Flag')
    purchase_req_item_no = fields.Char(string="Purchase Request Item No")# PR itme#
    division=fields.Char('division',related="part_id.division")
    gr_qty = fields.Float(string="GR Quantity",related="order_line_id.gr_qty")
    gr_qty_his = fields.Float(string="GR Quantity History")
    line_amount = fields.Float(string="Line Amount", precision=(18, 4), compute='_compute_line_amount')
    open_qty = fields.Float(string="Open PO Quantity", related="order_line_id.open_qty")
    open_qty_his = fields.Float(string="Open PO Quantity")#在用户发生操作之后记录当时数据
    on_road_qty = fields.Float(string="In Transit ASN Quantity", related="order_line_id.on_road_qty")
    on_road_qty_his = fields.Float(string="In Transit ASN Quantity")#在用户发生操作之后记录当时数据
    source_type = fields.Selection([
                                 ('po_new', 'PO New'),
                                 ('po_change', 'PO Change'),#数据记录类型，当前有效还是已经是历史数据
    ], string='Data Type', readonly=True, index=True, default='po_new',copy=True, track_visibility='onchange')
    change_id=fields.Many2one('iac.purchase.order.change',string="PO Change")
    change_line_id=fields.Many2one('iac.purchase.order.line.change',string="PO Change")
    division=fields.Char('division',related="part_id.division")
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记
    purchase_req_no = fields.Char(string="Purchase Request No")# PR#
    storage_location = fields.Char(string="Storage Location")
    is_submit = fields.Boolean(string="Is Submit",default=False)#is_vendor_submit 与 is_change_submit进行或运算的结果
    is_vendor_submit = fields.Boolean(string="Is Submit",default=False)#vendor 点击submit按钮
    is_change_submit = fields.Boolean(string="Is Submit",default=False)#发生po_change的情况下,当前记录提交产生新的vendor_confirm

    @api.one
    @api.depends('quantity', 'price', 'price_unit')
    def _compute_line_amount(self):
        for line in self:
            if line.odoo_deletion_flag==True:
                continue
            if line.price_unit > 0:
                line.line_amount = line.quantity * (line.price / line.price_unit)
            else:
                line.line_amount = 0

    @api.one
    def button_to_toggle(self):
        if self.state == 'wait_vendor_confirm':
            self.write({'state': 'vendor_confirmed'})
        elif self.state=='vendor_confirmed':
            self.write({'state': 'vendor_exception'})
        elif self.state=='vendor_exception':
            self.write({'state': 'wait_vendor_confirm'})

    @api.one
    def button_to_confirm(self):
        if self.state == 'wait_vendor_confirm' or self.state == 'vendor_exception':
            self.write({'state': 'vendor_confirmed'})

    @api.one
    def button_to_exception(self):
        if self.state == 'wait_vendor_confirm' or self.state=='vendor_confirmed':
            self.write({'state': 'vendor_exception'})


"""
class IacPurchaseOrderConfirmHisBuyer(models.Model):

    _name = "iac.purchase.order.vendor.confirm.his.buyer"
    _inherit = "iac.purchase.order.vendor.confirm.his"
    _table="iac_purchase_order_vendor_confirm_his"
    _description = "Purchase Order Vendor Confirm Buyer"
    _order = 'id desc, name'
    confirm_line_ids = fields.One2many("iac.purchase.order.vendor.confirm.line.his.buyer", "vendor_confirm_id", string="PO Vendor Confirm Line")

    @api.multi
    def button_submit_to_sap(self):
        for po_confirm in self:
            if po_confirm.state == 'exception':
                #self.write({'state': 'vendor_confirmed'})
                #从当前po_confirm 中复制新建
                po_confirm_new=po_confirm.create_po_confirm_from_exception()
                order_change=po_confirm.order_id.generate_order_change()
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
                        #self.order_id.apply_po_change_data(order_change)
                        order_change.apply_po_change_data()

                        #操作成功的情况下,修改记录状态
                        proc_result=True
                        order_change.write({"state":"vendor_confirmed"})
                        po_confirm_new.button_set_all_confirm()
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


class IacPurchaseOrderConfirmLineHisBuyer(models.Model):

    _name = "iac.purchase.order.vendor.confirm.line.his.buyer"
    _inherit = "iac.purchase.order.vendor.confirm.line.his"
    _description = u"PO Line Vendor Confirm Buyer"
    _order = 'id desc, name'
    _table="iac_purchase_order_vendor_confirm_his_line"
    vendor_confirm_id = fields.Many2one('iac.purchase.order.vendor.confirm.his.buyer', string="Purchase Order Vendor Confirm", index=True)
"""