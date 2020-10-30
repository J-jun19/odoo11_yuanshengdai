# -*- coding: utf-8 -*-
import threading
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json
import utility

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval
from odoo.modules.registry import RegistryManager
import odoo
_logger = logging.getLogger(__name__)

#专门用来为PO提供上传文件的模型
class MukDmsFilePo(models.Model):
    _inherit="muk_dms.file"
    _name='muk_dms.file.po'
    _table='muk_dms_file'
    _description = u"Vendor Info"



class IacPurchaseOrder(models.Model):
    """PO 主表"""
    _name = "iac.purchase.order"
    _description = "Purchase Order"
    _order = 'document_erp_id desc'

    name = fields.Char(string="Purchase Order", related='document_erp_id', index=True)
    order_date = fields.Date(string="PO Date")
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
                                 ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")

    approved = fields.Boolean(string='Is Approved', default=False)
    changed = fields.Boolean(string='Is Changed', default=False)
    note = fields.Text(string="Note")
    approve_role_list = fields.Char(string="Approve Role List")
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记
    approve_flag = fields.Boolean(string="Approve Flag", default=False)#标识当前PO 是否被签核通过一次,包括po_new 和 po_change 的情况
    webflow_number=fields.Char(string="Webflow Number")
    order_reason = fields.Char(string="Order Reason")
    version_no = fields.Char(string="Version No")

    # 中间表附加的字段
    document_erp_id = fields.Char(string="Document Erp Id",index=True)
    company_code = fields.Char(string="Company Code")
    manually_po_reason_type = fields.Char(string="Manually Po Reason Type")
    deletion_flag = fields.Char(string='Delete')
    created_by = fields.Char(string="Created By")
    vendor_code = fields.Char(string="Vendor Code",index=True)
    vendor_name = fields.Char(related='vendor_id.name', string="Vendor Name")
    language_key = fields.Char(string="Language Key")
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)
    currency = fields.Char(string="Currency")
    exchange_rate = fields.Char(string="Exchange Rate")
    contact_person = fields.Char(string="Contact Person")
    incoterm1 = fields.Char(string="Incoterm Destination")
    incoterm2 = fields.Char(string="Incoterm2")  # 使用incoterm1
    order_release_status = fields.Char(string="Order Release Status")
    address_id = fields.Char(string="Address Id")
    your_reference = fields.Char(string="Your Reference")
    our_reference = fields.Char(string="Our Reference")
    buspartno=fields.Char(string="Number of a Business Partner in Vendor Master Record")
    incoterm = fields.Char(string="Incoterm From SAP")
    payment_term=fields.Char(string="Payment Term")
    purchase_org=fields.Char(string="Purchase Org",index=True)
    manually_po_reason = fields.Text(string="Manually PO Reason")
    manually_po_comment = fields.Text(string="Manually PO Comment")
    manually_po_comment2 = fields.Text(string="Manually PO Comment2")
    manually_po_type = fields.Text(string="Manually PO Type")  # 使用 manually_po_reason_type
    contact_name = fields.Char(string="Contact Name")
    contact_phone = fields.Char(string="Contact Phone")
    contact_fax = fields.Char(string="Contact Fax")
    order_type = fields.Char(string="Order Type")
    warehouse = fields.Char(string="Warehouse")
    company_code = fields.Char(string="Company Code")
    status = fields.Char(string="Status Message")




    # 关联字段
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code From SAP", index=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    payment_term_id = fields.Many2one('payment.term', string="Payment Term")
    company_id = fields.Many2one('company', string="Company Info")
    change_ids = fields.One2many('iac.purchase.order.change', 'order_id', string="Purchase Order Change")
    incoterm_id = fields.Many2one('incoterm', string="Incoterm")
    address_odoo_id = fields.Many2one('address', string="Address Id")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    last_change_id = fields.Many2one('iac.purchase.order.change', string="Last Purchase Order Change")
    order_line = fields.One2many("iac.purchase.order.line", "order_id", string="PO Line Number")
    attachment_ids = fields.One2many('iac.purchase.order.file','order_id', string='Attachment Files')
    history_order_id = fields.Many2one('iac.purchase.order.history', string="History Order Id")
    currency_id = fields.Many2one('res.currency', string="Currency")
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location', index=True)

    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)

    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)




    #price_his_id = fields.Many2one('inforecord.history', string="Price History Info")#关联到价格信息表,临时字段
    #last_price=fields.Float(string="Last Price Info",default=0)#从价格表中获取的最新价格
    #last_price_type=fields.Selection([('cost_up','Cost Up'),('cost_down','Cost Down')],string="Price Change Type")#价格变化类型
    #
    #废弃字段,不要使用
    pricecontrol = fields.Char(string="Price Control")
    changed_text = fields.Char(string="Changed Text")
    changed_terms = fields.Char(string="Changed Terms")
    ship_code = fields.Char(string="Ship Code")
    dropship_no = fields.Char(string="Drop Ship Number")
    ship_addr = fields.Char(string="Ship Address")
    purchase_org_id = fields.Many2one('vendor.plant', string="Purchase Org", index=True)
    #buyer confrim vendor_exception

    #计算字段
    order_amt = fields.Float(string='Order Amount',compute='_taken_amount')# SAP传过来的订单总额
    is_open = fields.Boolean(string="Open PO", compute='_taken_is_open')

    #为数据迁移所准备的字段
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")
    miss_flag=fields.Integer(string="Miss Flag",index=True)

    ori_payment_term = fields.Many2one('payment.term',  string='Original Payment Term')
    ori_incoterm_id = fields.Many2one('incoterm',  string='Original Incoterm')
    ori_incoterm1 = fields.Char( string="Original Incoterm Destination")

    new_payment_term = fields.Many2one('payment.term', string='New Payment Term')
    new_incoterm = fields.Many2one('incoterm', string='New Incoterm')
    new_incoterm1 = fields.Char(string="New Incoterm Destination")
    display_flag=fields.Boolean(string='Display Current Record',default=False,index=True)
    version_no_num = fields.Integer(string="Version Int Number", compute='_taken_version_no_num')
    lock_flag=fields.Integer(string='Lock Flag',default=0)#标识当前订单条目是否被锁定，在进行po_mass_change和创建asn的时候需要检查
    po_change_type = fields.Selection([('new_po','New PO'),
                                    ('price_change','Price change'),
                                    ('quantity_change','Quantity change'),
                                    ('quantity_and_price_change','Quantity and Price change'),
                                    ('no_change','No change')])#新增字段，根据po change type来分组
    need_unconfirm = fields.Boolean(default=False) #新增字段，用来判断change是否发生在approve之后，继而判断是否需要往unconfirm表中写入资料，如果是则为True,否则为False

    def try_lock(self):
        """
        尝试获取当前po的锁
            如果lock_flag值为0的情况下，更新lock_flag值为1并且返回true
            如果lock_flag值为1的情况下,返回false
        :return:
        """
        if self.lock_flag==0:
            self.lock_flag=1
            self.env.cr.commit()
            return True
        else:
            return False

    def release_lock(self):
        """
        释放当前po的锁
        :return:
        """
        if self.lock_flag==1:
            self.lock_flag=0
            self.env.cr.commit()

    def release_batch_lock(self,order_id_list=[]):
        #操作处理完成释放po的锁
        for order_id in order_id_list:
            order = self.env["iac.purchase.order"].browse(order_id)
            order.release_lock()

    def try_batch_lock(self,order_id_list=[]):
        """
        给定一个订单id 列表尝试批量获取锁
            如果存在获取订单锁失败的情况下就抛出异常
        :param order_id_list:
        :return:
        """
        #尝试获取po的锁,所有的待处理po锁都获得以后才能继续操作,否则则放弃锁
        order_id_lock_list=[]
        lock_fail_list=[]
        for order_id in order_id_list:
            order = self.env["iac.purchase.order"].browse(order_id)
            if order.try_lock()==True:
                order_id_lock_list.append(order_id)
            else:
                lock_fail_list.append(order_id)

        #当存在获取订单锁失败的情况下，释放已经获取的锁，并抛出异常
        if len(lock_fail_list)>0:
            order_code_list=[]
            for order_id in lock_fail_list:
                order = self.env["iac.purchase.order"].browse(order_id)
                order_code_list.append(order.document_erp_id)

            #释放已经获取的锁
            for order_id in order_id_lock_list:
                order = self.env["iac.purchase.order"].browse(order_id)
                order.release_lock()
            ex_msg=u"获取订单的锁定操作失败，可能其他操作人员正在操作这些订单，请稍后重试，订单列表为:%s" %order_code_list
            raise UserError(ex_msg)

    @api.one
    @api.depends('version_no')
    def _taken_version_no_num(self):
        """
        计算七位精度的单价
        :return:
        """
        if self.version_no==False:
            self.version_no_num=0
        else:
            self.version_no_num = int(self.version_no)

    def button_attach_file(self):
        """
        只能被po对象调用,弹出窗口增加PO的对应的附加文档
        :return:
        """
        #签核中的不运行变更文件内容
        if self.state in ['to_approve','to_change']:
            raise UserError("Can not upload file when order state is to_approve or to_change")

        # Ning add
        mm_exist = self.env['iac.purchase.order.mm.special.approval.create'].search(
            [('document_erp_id', '=', self.document_erp_id)])
        if mm_exist:
            raise UserError('授权下单的PO无法上传文件')

        po_dir_rec=self.env["muk_dms.directory"].search([('name','=','po_attachment')],order='id desc',limit=1)
        if not po_dir_rec.exists():
            raise UserError("Dir 'po_attachment' has not found")

        action = self.env.ref('oscg_po.action_iac_purchase_order_file')

        add_item_context={
            "default_order_id":self.id,
            "default_directory":po_dir_rec.id
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

    #200521 ning update 废除exception状态后提交sap的按钮 begin
    # @api.multi
    # def button_submit_to_sap(self):
    #     if self.state in ['pending']:
    #         raise UserError('Current state is pending ,can not perform send to sap')
    #     if self.state == 'vendor_exception':
    #         order_change=self.generate_order_change()
    #         #为exception 的订单条目设置交期
    #         for order_line_change in order_change.line_ids:
    #             if order_line_change.order_line_id.state=="vendor_exception":
    #                 order_line_change.write({"new_delivery_date":order_line_change.order_line_id.vendor_delivery_date,
    #                                          "state":"vendor_exception",
    #                                          })
    #         # 调用SAP接口
    #         biz_object = {
    #             "id": order_change.id,
    #             "biz_object_id": order_change.id
    #         }
    #         rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
    #             "iac.interface.rpc"].invoke_web_call_with_log(
    #             "ODOO_PO_002", biz_object)
    #
    #         if rpc_result:
    #             # 根据order change更新order
    #             order_change.apply_po_change_data()
    #
    #             #操作成功的情况下,修改记录状态
    #             proc_result=True
    #             order_change.write({"state":"erp_accepted"})
    #             self.write({"state":"vendor_confirmed"})
    #             for order_line in self.order_line:
    #                 order_line.with_context(state_change=True).write({"state":"vendor_confirmed"})
    #             #self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data(self.id,self.last_change_id.id,'vendor_confirmed')
    #             self.env["iac.purchase.order.unconfirm.detail"].sudo().update_unconfirm_data_confirmed(self.id)
    #         else:
    #             order_change.write({'state_msg': u'通知SAP失败'})
    #
    #
    #     return True
    #end

    @api.multi
    def button_send_back_to_vendor(self):
        if self.state == 'vendor_exception':
            self.write({'state': 'wait_vendor_confirm'})
            # new po state='wait vendor confirm'时给vendor发送邮件提醒其confirm
            self._new_po_mail_to_vendors()
            self.env["iac.purchase.order.vendor.confirm.his"].po_confirm_reset_to_vendor(self.id)
        return True

    @api.one
    def get_part_qty_map(self):
        """
        获取订单料号数量汇总数据
        :return:
        """
        if not self.history_order_id.exists():
            return {}
        self.env.cr.execute('select part_id,sum(quantity) from iac_purchase_order_line_history  t where t.order_id=%s group by part_id ',
            (self.id,))
        result_list=self.env.cr.fetchall()
        result_map={}
        for part_id,qty in result_list:
            result_map[part_id]=qty
        return result_map

    @api.depends('order_line')
    def _taken_amount(self):
        for order in self:
            for line in order.order_line:
                order.order_amt=order.order_amt+line.line_amount


    def _taken_is_open(self):
        is_open = False
        for order in self:
            for line in order.order_line:
                if line.open_qty > 0 and line.odoo_deletion_flag==False:
                    is_open = True
                    break
            order.is_open = is_open


    def button_to_change(self):
        """
        只能单个po new 来调用
        :return:
        """
        if not self.history_order_id.exists():
            history_order = self._copy_history_order()
            self.write({'history_order_id': history_order.id})
        domain=[('state','in',['pending','to_approve','webflow_error','unapproved'])]
        domain+=[('order_id','=',self.id)]
        last_order_change=self.env["iac.purchase.order.change"].search(domain,limit=1)
        if last_order_change.exists():
            raise UserError("当前订单存在签核中的订单变更!")

        if self.state not in ['pending','unapproved','vendor_confirmed','vendor_exception','wait_vendor_confirm']:
            raise UserError("只有处于pending,unapproved,vendor_confirmed,vendor_exception,wait_vendor_confirm 状态的订单才能变更!")

        order_change = self.generate_order_change()
        self.write({'last_change_id':order_change.id})

        #order_audit_vals={
        #    "order_id":self.id,
        #    "order_code":self.document_erp_id,
        #    "action_type":"po_change",
        #    "ref_data":order_change.id,
        #}
        #if self.env.user.exists():
        #    order_audit_vals["user_id"]=self.env.user.id
        #    order_audit_vals["user_login_code"]=self.env.user.login
        #else:
        #    order_audit_vals["user_id"]=self.env.user.id
        #    order_audit_vals["user_login_code"]=self.env.user.login
        #self.env["iac.purchase.order.audit"].sudo().create(order_audit_vals)

        action = self.env.ref('oscg_po.action_view_purchase_order_change_view_form')
        action_data={
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': 'form',
            'view_mode': 'form',
            'target': action.target,
            'res_model': action.res_model,
            'res_id':order_change.id,
            'view_id':self.env.ref("oscg_po.view_po_change_view_form").id
        }

        return action_data

    def _copy_history_order(self):
        history_order_lines = []
        for line in self.order_line:
            history_order_line = {
                'name': line.document_line_erp_id,
                'plant_id': line.plant_id.id,
                'order_id': self.id,
                'order_line_id': line.id,
                'part_id': line.part_id.id,
                'quantity': line.quantity,
                'price': line.price,
                'price_unit': line.price_unit,
                'delivery_date': line.delivery_date,
                'price_date': line.price_date,
                'unit': line.unit,
                'tax_code': line.tax_code,
                'storage_location': line.storage_location,
                'purchase_req_no':line.purchase_req_no,
                'purchase_req_item_no':line.purchase_req_item_no,
                'document_erp_id':line.document_erp_id,
                'document_line_erp_id':line.document_line_erp_id,
            }
            history_order_lines.append((0, 0, history_order_line))
        history_order = {
            'name': self.name,
            'plant_id': self.plant_id.id,
            'purchase_org_id': self.purchase_org_id.id,
            'vendor_id': self.vendor_id.id,
            'order_amt': self.order_amt,
            'order_date': self.order_date,
            'payment_term_id': self.payment_term_id.id,
            'incoterm_id': self.incoterm_id.id,
            'incoterm1': self.incoterm1,
            'ori_order_id': self.id,
            'manually_po_reason_type':self.manually_po_reason_type,
            'manually_po_comment':self.manually_po_comment,
            'line_ids': history_order_lines,
            'document_erp_id':line.document_erp_id,
        }

        # return self.env['iac.purchase.order.history'].create(history_order)

        po_history_obj = self.env['iac.purchase.order.history'].create(history_order)
        # 创建history后回写po_line的line_history_id字段
        for po_line_history in po_history_obj.line_ids:
            po_line_obj = self.env['iac.purchase.order.line'].browse(po_line_history.order_line_id.id)
            po_line_obj.with_context(state_change=True).write({'line_history_id': po_line_history.id})

        return po_history_obj

    @api.multi
    def generate_order_change(self):
        """生成po change"""
        # 拼po change


        #ori_payment_term = fields.Many2one('payment.term',  string='Original Payment Term')
        #ori_incoterm_id = fields.Many2one('incoterm',  string='Original Incoterm')
        #ori_incoterm1 = fields.Char( string="Original Incoterm Destination")

        new_change = {}
        new_change['order_id'] = self.id
        new_change['plant_id'] = self.plant_id.id
        new_change['ori_payment_term'] = self.payment_term_id.id
        new_change['ori_incoterm_id'] = self.incoterm_id.id
        new_change['ori_incoterm1'] = self.incoterm1

        new_change['new_payment_term'] = self.payment_term_id.id
        new_change['new_incoterm'] = self.incoterm_id.id
        new_change['new_incoterm1'] = self.incoterm1
        new_change['version_no'] = str(len(self.change_ids) + 1)
        new_change['vendor_id']=self.vendor_id.id
        new_change['manually_po_reason_type']=self.manually_po_reason_type
        new_change['manually_po_comment']=self.manually_po_comment
        new_change['buyer_erp_id']=self.buyer_erp_id
        new_change['buyer_id']=self.buyer_id.id

        new_change['order_code'] = self.document_erp_id
        new_change['order_date'] = self.order_date
        new_change['currency_id'] = self.currency_id.id
        new_change['vendor_code'] = self.vendor_id.vendor_code
        new_change['vendor_name'] = self.vendor_id.name

        # 拼po change line
        line_ids = []
        for line in self.order_line:
            line_val = {
                'order_id': self.id,
                'vendor_id': self.vendor_id.id,
                'order_line_id': line.id,
                'order_code': self.document_erp_id,
                'order_line_code': line.document_line_erp_id,
                'order_line_code_2': line.document_line_erp_id.zfill(5),
                'part_id': line.part_id.id,
                'ori_price': line.price,
                'ori_qty': line.quantity,
                'ori_delivery_date': line.delivery_date,
                'new_price': line.price,
                'new_qty': line.quantity,
                'new_delivery_date': line.delivery_date,
                'current_flag': True,#标记为不是新增的条目
                'odoo_deletion_flag': line.odoo_deletion_flag,
                'ori_deletion_flag': line.odoo_deletion_flag,
                'price_unit': line.price_unit,
                'last_price_unit': line.price_unit,
                'unit': line.unit,
                'storage_location': line.storage_location,
                'price_date': line.price_date,
                'tax_code': line.tax_code,
                'price_his_id': line.price_his_id.id,
                'last_price': line.last_price,
                'last_price_type': line.last_price_type,
                'date_base': line.date_base,
                'item_type':'ori_item',
                'purchase_req_no': line.purchase_req_no,
                'purchase_req_item_no': line.purchase_req_item_no,
                'division': line.part_id.division,
                'vendor_part_no': line.vendor_part_no,
                'currency_id': self.currency_id.id,
                'order_date': self.order_date,
                'change_factor_qty':'equal',
                'change_factor_price':'equal',
            }
            line_ids.append((0, 0, line_val))
        new_change['line_ids'] = line_ids
        self.write({'changed': True, 'state': 'to_change'})

        #遍历order_change为order_line设置关联的order_line_change
        order_change=self.env['iac.purchase.order.change'].create(new_change)
        #for order_line_change in order_change.line_ids:
        #    order_line_change.order_line_id.write({"last_order_line_change_id":order_line_change.id})
        #    #记录日志信息
        #    order_line_change.apply_po_line_audit()
        return order_change

    @api.multi
    def button_to_approve(self):
        """通过菜单进行单笔或者多笔送签"""
        for order in self:
            if order.state not in ['pending','webflow_error','unapproved']:
                raise UserError("只有 'pending','webflow_error','unapproved' 状态的才能送签!")

        # Ning add  校验送签PO是否为授权下单的PO
        for order in self:
            mm_exist = self.env['iac.purchase.order.mm.special.approval.create'].search([('document_erp_id','=',order.document_erp_id)],limit=1)
            if mm_exist:
                file_id = self.env['iac.purchase.order.im.special.approval.import'].browse(mm_exist.im_upload_id.id).evidence_file_id
                order_file_exist = self.env['iac.purchase.order.file'].search([('order_id', '=', order.id), ('file_id', '=', file_id)])
                if not order_file_exist:
                    vals = {
                        'order_id': order.id,
                        'file_id': file_id
                    }
                    order_file_create = self.env['iac.purchase.order.file'].create(vals)
                    order_file_create.env.cr.commit()

        for order in self:
            if not  order.history_order_id.exists():
                history_order = order._copy_history_order()
                order.write({'history_order_id': history_order.id})
            order._send_to_webflow()




    @api.multi
    def button_to_get_approve_list(self):
        """通过菜单进行单笔或者多笔送签"""
        for order in self:
            #获取po的审核角色列表
            proc_result,approve_role_list,approve_rule_list,proc_ex_list=order._get_po_new_approve_list()
            if len(proc_ex_list)>0:
                order.write({"state_msg":proc_ex_list,'approve_list':False})
            else:
                order.write({"state_msg":False,'approve_list':approve_role_list})

    def _get_po_new_approve_list(self):
        """
         获得po_new 的签核角色列表
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




        # 根据po判断规则引擎因子
        order_amount = self.order_amt
        material_maxprice = 0
        for line in self.order_line:
            #真正的单价需要除以price_unit
            #if line.usd_price==0:
            #    memo=_(u'解析规则报错,存在订单条目单价无法转换到USD！order_code 是 ( %s ) ,order_line_code ( %s )'%(line.document_erp_id,line.document_line_erp_id))
            #    proc_result=False
            #    proc_ex_list.append(memo)
            #if line.price_unit==0:
            #    memo=_(u'解析规则报错,price_unit不能等于0！order_code 是 ( %s ) ,order_line_code ( %s )'%(line.document_erp_id,line.document_line_erp_id))
            #    proc_result=False
            #    proc_ex_list.append(memo)
            #    continue
            #usd_price=line.usd_price/line.price_unit
            part_price=line.price/line.price_unit
            if part_price > material_maxprice:
                material_maxprice = part_price


        change_incoterm = ''
        change_payment_term = ''
        price_factor = ''
        quantity_factor = ''
        change_delivery = ''
        item_factor = ''

        # 规则引擎判断,判断整个订单的适应规则
        approve_role_json=[]
        regular_list = self.env['iac.purchase.approve.regular'].search([('plant_id', '=', self.plant_id.id),
                                                                    ('currency_id', '=', self.currency_id.id),
                                                                        ('rule_type','=','po')])
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
                        memo=_(u'解析规则报错,签核的关卡不是合法的JSON中的list格式！order_code 是 ( %s ) ,order_line_code ( %s )'%(line.document_erp_id,line.document_line_erp_id))
                        proc_result=False
                        proc_ex_list.append(memo)
                except:
                    traceback.print_exc()
                    error_flag='Y'
                    memo=_(u'解析规则报错,签核的关卡不是合法的JSON格式！ order_code 是 ( %s ) ,order_line_code ( %s )' %(line.document_erp_id,line.document_line_erp_id))
                    proc_result=False
                    proc_ex_list.append(memo)

                expression = regular.expression
                # 找到送签规则的情况下
                rule_record = {
                    'order_id': self.id,
                    'order_line_id': line.id,
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
            else:
                memo=''
                rule_record = {
                    'order_id': self.id,
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

        return proc_result,approve_role_list,approve_rule_list,proc_ex_list

    def _validate_webflow_exclude(self):
        """
        调用方为po_new 对象,只能单个po_new调用
        校验是否不能送签,对不能送签的弹出提示
        :return:
        """
        vendor_id=self.vendor_id.id
        for order_line in self.order_line:
            #校验是否存在签核中的相同材料
            part_id=order_line.part_id.id
            plant_id=order_line.plant_id.id
            #self.env.cr.execute("select ipol.document_erp_id,ipol.document_line_erp_id from public.iac_purchase_order_line ipol " \
            #                    "where ipol.part_id=%s                                                                           " \
            #                    "and ipol.vendor_id=%s                                                                           " \
            #                    "and exists (                                                                                   " \
            #                    "select 1 from public .iac_purchase_order ipo where ipo.id=ipol.order_id                        " \
            #                    "and ipo.state='to_approve' AND ipo.id <>%s                                                     " \
            #                    ") order by id limit 1                                                                                             ",
            #        (part_id,vendor_id,self.id))
            #result=self.env.cr.fetchall()
            #if len(result)>0:
            #    err_msg=u"存在未签核完成的订单,订单号( %s ),订单行编码为( %s ),Part No 是( %s ) "% \
            #            (result[0][0],result[0][1],order_line.part_id.part_no)
            #    raise UserError(err_msg)

            domain_part=[('part_id','=',order_line.part_id.id),('vendor_id','=',vendor_id)]
            domain_part+=[('state','in',['wait_vendor_confirm','vendor_exception'])]

            #排除自身
            domain_part+=[('order_id','<>',self.id)]
            po_line_result=self.env["iac.purchase.order.line"].search(domain_part,order='id desc',limit=1)
            #排除条件
            #当前vendor相同的料号,有未confirm 的
            #状态变更为删除的 或者订单条目中减少数量的
            #曾经confirm过的
            if po_line_result.exists():
                if po_line_result.ever_confirmed==False:
                    continue

                #减少数量并且没有变更删除标记
                if (po_line_result.ori_qty>po_line_result.new_qty
                    and  po_line_result.ori_del_flag==po_line_result.new_del_flag
                    and po_line_result.new_del_flag==False):
                    err_msg=u"存在未确认的订单条目,订单编码为( %s ),订单行编码为( %s ),Part No 是( %s ) "%\
                            (po_line_result.document_erp_id,po_line_result.document_line_erp_id,po_line_result.part_id.part_no)
                    raise UserError(err_msg)

                #变更删除标记,从False 变更为True
                if ( po_line_result.ori_del_flag<>po_line_result.new_del_flag
                    and po_line_result.new_del_flag==True):
                    err_msg=u"存在未确认的订单条目,订单编码为( %s ),订单行编码为( %s ),Part No 是( %s ) "%\
                            (po_line_result.document_erp_id,po_line_result.document_line_erp_id,po_line_result.part_id.part_no)
                    raise UserError(err_msg)
            #新訂單送簽卡控規則： loop新訂單的PO line,找unconfirm summary里，是否存在料號等於當前PO line的料號 and Plant=當前PO的Plant and
            # UNCONQTYD <> 0的資料，如果有則報錯提示，卡住送簽，如果所有PO line 都找不到unconfirm的資料，就可以送簽
            self.env.cr.execute("""
                                select document_no,document_line_no,unconqtyd from iac_purchase_order_unconfirm_summary
                                where odoo_plant_id=%s
                                and  unconqtyd<>0
                                and part_id=%s
                                and data_type='current'  limit 1
            """,(plant_id,part_id))
            pg_result=self.env.cr.fetchall()
            if len(pg_result)>0:
               err_msg=u"存在未确认的订单条目,订单编码为( %s ),订单行编码为( %s ),Part No 是( %s ),未确认数量为%s "%\
                       (pg_result[0][0],
                        pg_result[0][1],
                        order_line.part_id.part_no,
                        pg_result[0][2],
                       )
               raise UserError(err_msg)
    @api.one
    def _send_to_webflow(self):

        #第一次获取审核角色列表信息,检查是否有异常信息
        po_approve_list=[]

        proc_result=True
        approve_role_list=[]
        approve_rule_list=[]
        proc_ex_list=[]

        #判断是否能够进行送签，不能够进行送签弹出异常，终止操作
        self._validate_webflow_exclude()
        #获取po的审核角色列表

        proc_result,approve_role_list,approve_rule_list,proc_ex_list=self._get_po_new_approve_list()


        #如果获取审核角色列表出现异常则停止进行处理
        if proc_result==False:
            raise UserError(proc_ex_list)

        po_approve_item={"proc_result":proc_result,
                         "approve_role_list":approve_role_list,
                         "approve_rule_list":approve_rule_list,
                         "proc_ex_list":proc_ex_list,
                         "order_id":self.id
                         }
        po_approve_list.append(po_approve_item)

        #第二次获取审核角色列表信息,这次要开始送审核
        for po_approve_item in po_approve_list:
            proc_result=True
            approve_role_list=[]
            approve_rule_list=[]
            proc_ex_list=[]

            proc_result=po_approve_item["proc_result"]
            approve_role_list=po_approve_item["approve_role_list"]
            approve_rule_list=po_approve_item["approve_rule_list"]
            proc_result=po_approve_item["proc_result"]
            order_id=po_approve_item["order_id"]
            #存储 approve_role_list
            order_rec=self.env["iac.purchase.order"].browse(order_id)
            if len(approve_role_list)==0:
                order_rec.write({"approve_role_list":False})
            else:
                order_rec.write({"approve_role_list":approve_role_list})

            #如果获取审核角色列表出现异常则停止进行处理
            if proc_result==True:
               #找不到审核角色的情况下,设定至少要有 MM_Manager来审核
               if len(approve_role_list)==0:
                   approve_role_list.append("MM_Manager")
                   # 调用webflow接口
               biz_object = {
                   "id": order_id,
                   "biz_object_id":order_id,
                   "flow_id": approve_role_list
               }
               rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                   "iac.interface.rpc"].invoke_web_call_with_log(
                   "F07_B_1", biz_object)

               order=self.env["iac.purchase.order"].browse(po_approve_item["order_id"])
               if rpc_result:
                   vals={
                       'state': 'to_approve',
                       'state_msg': u'送签成功',
                       'webflow_number':rpc_json_data.get('EFormNO'),
                   }
                   order.write(vals)
                   order.apply_po_audit()
                   for order_line in order.order_line:
                       order_line.with_context(state_change=True).write({'state': 'to_approve'})
                       order_line.apply_po_line_audit()


               else:
                   order.write({'state_msg': u'送签失败','webflow_number':rpc_json_data.get('EFormNO',False),'state':"webflow_error"})
                   order.apply_po_audit()
                   #记录order_line日志
                   for order_line in order.order_line:
                       order_line.apply_po_line_audit()

               for approve_rule in approve_rule_list:
                   self.env['iac.purchase.approve.record'].create(approve_rule)



    @api.multi
    def button_cancel(self):
        if self.state == 'pending':
            self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_recover(self):
        if self.state == 'cancel':
            self.write({'state': 'pending'})
        return True

    def _new_po_mail_to_vendors(self):

        """ new_po 状态更新为wait_vendor_comfirm时
            及时发送Alert email 给vendor """
        # 调用utility里的公用方法
        utility.po_mail_to_vendor(self,self.order_line, 'new_po')

    def po_new_callback(self, context=None):
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
            if context["approve_status"]  and context["rpc_callback_data"]["FormStatus"]=="C":
                order_id=context.get("data").get("id")
                order = self.browse(order_id)
                if not order.exists():
                    proc_ex.append(u"iac.purchase.order model has no record with id ( %s )" %(order_id,))
                    return proc_result,proc_ex
                order.write({'state': 'to_sap',
                             'state_msg': u'webflow签核通过'})
                order.apply_po_audit()
                #记录order_line日志,签核通过
                for order_line in order.order_line:
                    order_line.apply_po_line_audit()


                # 调用SAP接口
                proc_result,proc_ex=order.send_to_sap()
                if proc_result==False:
                    order.write({'state': 'sap_error','version_no':2,
                                 'state_msg': u'通知SAP失败'})
                    order.apply_po_audit()
                    #记录order_line日志,调用SAP失败
                    for order_line in order.order_line:
                        order_line.apply_po_line_audit()
                else:
                    order.write({'state': 'wait_vendor_confirm',
                                 'approve_flag':True,
                                 'state_msg': u'通知SAP成功'})
                    order.apply_po_audit()

                    #创建Vendor Confirm History 记录
                    self.env["iac.purchase.order.vendor.confirm.his"].po_new_vendor_confirm_create(order.id)

                    # new po 产生时给vendor发送邮件提醒其confirm
                    order._new_po_mail_to_vendors()

                    #记录order_line日志,调用SAP成功
                    for order_line in order.order_line:
                        order_line.apply_po_line_audit()
                #当webflow成功的时候,丢弃调用SAP失败的异常,总是返回成功状态
                proc_result=True
                proc_ex=[]
                return proc_result,proc_ex
            elif context["approve_status"]  and context["rpc_callback_data"]["FormStatus"]=="D":
                order_id=context.get("data").get("id")
                order = self.browse(order_id)
                if not order.exists():
                    proc_ex.append(u"iac.purchase.order model has no record with id ( %s )" %(order_id,))
                    return proc_result,proc_ex

                order.write({'state': 'unapproved',
                             'state_msg': u'webflow签核未通过,webflow抽单拒绝'})
                order.apply_po_audit()
                #记录order_line日志,签核不通过
                for order_line in order.order_line:
                    order_line.apply_po_line_audit()


                proc_result=True
                return proc_result,proc_ex
            else:
                order_id=context.get("data").get("id")
                order = self.browse(order_id)
                if not order.exists():
                    proc_ex.append(u"iac.purchase.order model has no record with id ( %s )" %(order_id,))
                    return proc_result,proc_ex

                order.write({'state': 'unapproved',
                             'state_msg': u'webflow签核失败'})
                order.apply_po_audit()

                proc_result = False
                return proc_result, proc_ex
        except:
            ex_string = traceback.format_exc()
            proc_result = False
            proc_ex.append(ex_string)
            traceback.print_exc()
            return proc_result, proc_ex

    def send_to_sap(self):
        for order in self:
            if not (order.state=="sap_error" or order.state=="to_sap"):
            # if not (order.state in ['pending','sap_error','to_sap','unapproved']):
                raise UserError("Po No is %s ,state is %s ,can not call Send To SAP"%(order.document_erp_id,order.state))


            # 调用SAP接口
            biz_object = {
                "id": order.id,
                "biz_object_id": order.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_PO_001", biz_object)

            #存储po稽核信息
            order_audit_vals={
                "order_id":order.id,
                "order_code":order.document_erp_id,
                "action_type":"send_to_sap",
                }
            if self.env.user.exists():
                order_audit_vals["user_id"]=self.env.user.id
                order_audit_vals["user_login_code"]=self.env.user.login
            else:
                order_audit_vals["user_id"]=self.env.user.id
                order_audit_vals["user_login_code"]=self.env.user.login

            if rpc_result:
                # 更新ordor line的state状态
                for line in order.order_line:
                    line.with_context(state_change=True).write({'state': 'wait_vendor_confirm'})
                order.write({'state': 'wait_vendor_confirm',
                             'approve_flag': True,
                             'state_msg': u'通知SAP成功'})

                # new po state='wait vendor confirm'时给vendor发送邮件提醒其confirm
                order._new_po_mail_to_vendors()

                order_audit_vals["ref_data"]="success"
                self.env["iac.purchase.order.audit"].sudo().create(order_audit_vals)


                #更新版本po 版本号
                self.env.cr.execute("""
                 select cast(COALESCE(version_no,'0') as int4)+1 from iac_purchase_order where id=%s
                """,(order.id,))
                pg_result=self.env.cr.fetchall()
                order.write({"version_no":str(pg_result[0][0])})
                return rpc_result,exception_log
            else:
                order.write({'state_msg': u'通知SAP失败'})
                order_audit_vals["ref_data"]="fail"
                self.env["iac.purchase.order.audit"].sudo().create(order_audit_vals)
                return rpc_result,exception_log

    def button_to_sap(self):
        """
        从内部菜单中调用发送到SAP
        :return:
        """

        for order in self:
            if order.version_no_num<=1:
                raise UserError("Po No is %s ,state is %s ,version_no is %s,can not call Send To SAP"%(order.document_erp_id,order.state,order.version_no_num))
            order.send_to_sap()


    @api.one
    def apply_po_audit(self):
        """
        记录当前po 的audit 状态
        以上的状态变更的情况下备份记录po_line的变化情况
        :return:
        """
        #存储po稽核信息
        order_audit_vals={
            "order_id":self.id,
            "order_code":self.document_erp_id,
            "user_id":self.env.user.id,
            "user_login_code":self.env.user.login,
            "state_msg":self.state_msg,
            "audit_source":"po_new",
            "ori_payment_term":self.payment_term_id.id,
            "ori_incoterm_id":self.incoterm_id.id,
            "ori_incoterm1":self.incoterm1,
            "new_payment_term":self.payment_term_id.id,
            "new_incoterm_id":self.incoterm_id.id,
            "new_incoterm1":self.incoterm1,

            }
        if self.state=="webflow_error":
            order_audit_vals["action_type"]="webflow_error"
        elif self.state=="to_approve":
            order_audit_vals["action_type"]="send_to_webflow"
        elif self.state=="unapproved":
            order_audit_vals["action_type"]="denied_by_webflow"
        elif self.state=="to_sap":
            order_audit_vals["action_type"]="webflow_call_back"
        elif self.state=="sap_error":
            order_audit_vals["action_type"]="send_sap_error"
        elif self.state=="wait_vendor_confirm":
            order_audit_vals["action_type"]="wait_vendor_confirm"
        elif self.state=="vendor_confirmed":
            order_audit_vals["action_type"]="vendor_confirmed"
        elif self.state=="vendor_exception":
            order_audit_vals["action_type"]="vendor_exception"
        self.env["iac.purchase.order.audit"].create(order_audit_vals)


class IacPurchaseOrderLine(models.Model):
    """PO Line从表"""
    _name = "iac.purchase.order.line"
    _description = u"PO Line订单"
    _order = 'document_erp_id desc,order_line_code asc'


    name = fields.Char(string="Order Line Code",related="document_line_erp_id", index=True)
    order_code = fields.Char(string="Order Code", related="order_id.name", index=True)
    vendor_code = fields.Char(string="Vendor Code", index=True)

    order_date = fields.Date(string="PO Date",index=True)
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)

    current_flag = fields.Boolean(string="Current Flag", default=True)#是否当前（非复制）line，True:非复制；False：复制
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
                                 ('cancel', 'Cancelled'), # 表单取消
        ], default='pending', string="Vendor Confirmed State")
    state_msg = fields.Char(string="Status Message")
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记







    storage_location = fields.Char(string="Storage Location")
    delivery_date = fields.Date(string="Delivery Date")#交期
    vendor_delivery_date = fields.Date(string="Vendor Delivery Date")  # Vendor确认的交期

    # 中间表附加字段
    vendor_part_no = fields.Char(string="Vendor Part No")
    purchase_req_no = fields.Char(string="Purchase Request No")# PR#
    purchase_req_item_no = fields.Char(string="Purchase Request Item No")# PR itme#
    tax_code = fields.Char(string="Tax Code",index=True)
    quantity = fields.Float(string='Quantity')#当前行料号总数量
    deletion_flag = fields.Char(string='Delete')
    document_erp_id = fields.Char(string="Document Erp Id",index=True)
    document_line_erp_id = fields.Char(string="Order line code",index=True)
    rfq_status = fields.Char(string="Rfq Status")
    change_date = fields.Char(string="Change Date")
    short_text = fields.Char(string="Short Text")
    part_no = fields.Char(string="Part No",index=True)
    part_no1 = fields.Char(string="Part No1")
    plant_code = fields.Char(string="Plant",index=True)
    manufacturer_part_no = fields.Char(string="Manufacturer Part No")
    unit = fields.Char(string="Unit")
    tracking_number = fields.Char(string="Tracking Number")
    revision_level = fields.Char(string="Revision Level")
    rfq_no = fields.Char(string="Rfq No")

    reject_flag = fields.Char(string="Reject Flag")
    address_id = fields.Char(string="Address Id")
    vendor_to_be_supply = fields.Char(string="Vendor To Be Supply")
    delivery_complete = fields.Char(string="Delivery Complete")
    price = fields.Float(string="Price", precision=(18, 4))# 价格
    price_unit = fields.Integer(string="Price Unit")# 价格单位
    price_date = fields.Date(string="Price Date")


    #关联字段
    ref_line_id = fields.Many2one('iac.purchase.order.line', string="Ref PO Line Number", copy=False)#标明拆分po line时参考的目标条目
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    slocation_id = fields.Many2one(related='order_id.storage_location_id', string='storage location')
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    plant_id = fields.Many2one('pur.org.data', 'Plant', index=True)
    address_odoo_id = fields.Many2one('address', 'Address Id')
    part_id = fields.Many2one('material.master.po.line', 'Part No', index=True)#物料
    price_his_id = fields.Many2one('inforecord.history', string="Price History Info")#关联到价格信息表,临时字段
    last_order_line_change_id = fields.Many2one('iac.purchase.order.line.change', string="Last Order Line Change Info")#关联到最新的Order Line Change
    currency_id = fields.Many2one('res.currency', string="Currency",index=True)
    last_price_unit = fields.Integer(string="Last Price Unit")# 最新的价格单位
    line_history_id = fields.Many2one('iac.purchase.order.line.history', string='po line history', index=True)

    # lwt add relation fields



    division=fields.Char('division',related="part_id.division")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info")
    rfq_start_date = fields.Date(string="RFQ Start Date")
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)


    last_price=fields.Float(string="Last Price Info",default=0)#从价格表中获取的最新价格
    last_price_type=fields.Selection([('cost_up','Cost Up'),('cost_down','Cost Down')],string="Price Change Type")#价格变化类型
    date_base = fields.Selection([('po_date_base_all_open_po', u'PO date base（all open PO）'),
                                  ('delivery_date_base', 'Delivery date base'),
                                  ('po_date_base', u'PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base', u'Delivery date base + PO date base（RFQ生效后的PO）'),
                                  ('delivery_date_base_or_po_date_base_all_open_po', u'Delivery date base + PO date base（all open PO）')
                                 ], default='po_date_base_all_open_po', string="Price Date Base")
    vendor_exception_reason=fields.Text(string="Vendor Exception Reason")


    ##########计算字段
    usd_price = fields.Float('USD Price',compute='_take_usd_price')#转换到美金的价格
    #关联到gr表
    gr_line_ids=fields.One2many('goods.receipts','po_line_id',string="GR Line List")
    #关联到asn表
    asn_line_ids=fields.One2many('iac.asn.line','po_line_id',string="ASN Line List")

    asn_max_qty=fields.Integer('ASN MAX Qty', compute='_taken_asn_max_qty')
    line_amount = fields.Float(string="Line Amount", precision=(18, 4), compute='_taken_amount')

    open_qty = fields.Float(string="Open PO Quantity", compute='_taken_compute_qty')
    gr_qty = fields.Float(string="GR Quantity", compute='_taken_compute_qty')
    on_road_qty = fields.Float(string="In Transit ASN Quantity", compute='_taken_compute_qty')

    asn_qty = fields.Float(string="ASN Quantity", compute='_taken_asn_qty')

    #为数据迁移所准备的字段
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")
    miss_flag=fields.Integer(string="Miss Flag",index=True)
    order_line_code = fields.Char(string="Order Line Code",index=True)#5位字符串,不足的前面补足零,可以用来订单内部排序使用
    ever_confirmed=fields.Boolean(string="Ever Confirmed",default=False)#当前的条目是否曾经被确认过

    #应用到当前条目的change相关数据
    ori_price = fields.Float(string='Original Price', help="The Original price to purchase a product")# 原价格
    ori_qty = fields.Float(string='Original Quantity')# 原数量
    ori_delivery_date = fields.Date(string="Original Delivery Date")  # 原交期
    new_price = fields.Float('New Price',  help="The New price to purchase a product")# 新价格
    new_qty = fields.Float(string='New Quantity')# 新数量
    new_delivery_date = fields.Date(string="New Delivery Date")  # po line变更交期的最长交期
    ori_del_flag=fields.Boolean(string='Ori Del Flag')
    new_del_flag=fields.Boolean(string='New Del Flag')

    unit_price = fields.Float(string="Unit Price", precision=(18, 7),compute='_taken_unit_price')  # 单片价格
    new_asn_qty=fields.Integer(string='New Asn Qty',default=0)


    @api.one
    @api.depends('price', 'price_unit')
    def _taken_unit_price(self):
        """
        计算七位精度的单价
        :return:
        """
        if self.price_unit != 0:
            self.unit_price = self.price/self.price_unit
        else:
            self.unit_price = self.price
    #废弃字段
    #schedule_line = fields.One2many('iac.delivery.schedule', 'order_line_id', string='Order Line Schedule ID')


    # ning update 190402 修改最大可交量抓取方式
    @api.one
    @api.depends('vendor_id', 'part_id')
    def _taken_asn_max_qty(self):
        """
        PO Line物料数量-GR数量-ASN在途数量
        :return:
        """
        asn_max_qty_rec=self.env['iac.asn.max.qty.create.update'].search([('vendor_id', '=', self.vendor_id.id), ('part_id', '=', self.part_id.id),('state','=','done')],limit=1)
        if asn_max_qty_rec.exists():
            self.asn_max_qty=asn_max_qty_rec.available_qty
        else:
            self.asn_max_qty=0

    @api.one
    @api.depends('price')
    def _take_usd_price(self):
        if self.currency_id.exists() and self.currency_id.name=="USD":
            self.usd_price=self.price
        else:
            if not self.currency_id.exists():
                self.usd_price=0
            else:
                currency_exchange=self.env["iac.currency.exchange"].get_usd_exchange_record(self.currency_id.id)
                if currency_exchange.exists():
                    self.usd_price=(self.price/currency_exchange.from_currency_amount)*currency_exchange.to_currency_amount
                else:
                    self.usd_price=0

    @api.one
    @api.depends('quantity')
    def _taken_compute_qty(self):
        """
        PO Line物料数量-GR数量-ASN在途数量
        计算指定po_line 计算open_qty,计算在途asn_qty,计算gr_qty
        :return:
        """
        for line in self:
            self.env.cr.execute("SELECT                                     " \
                                "	o_gr_count,o_asn_count,o_open_count      " \
                                "FROM                                       " \
                                "	public.proc_po_part_info (              " \
                                "		%s,                      " \
                                "		%s,                      " \
                                "		%s                       " \
                                "	)                             ",
                                (line.order_id.id, line.id,
                                 line.part_id.id,))
            gr_count=0
            asn_count=0
            open_count=0
            part_result=self.env.cr.fetchall()

            gr_count=part_result[0][0]
            asn_count=part_result[0][1]
            open_count=part_result[0][2]
            line.gr_qty=gr_count
            line.open_qty=open_count
            line.on_road_qty=asn_count



    @api.one
    def _taken_asn_qty(self):
        """
        累计当前记录对应的asn数量
        :return:
        """
        asn_qty_sum=0
        for asn_line in self.asn_line_ids:
            asn_qty_sum=asn_qty_sum+asn_line.asn_qty
        self.asn_qty=asn_qty_sum



    @api.one
    @api.depends('quantity', 'price', 'price_unit')
    def _taken_amount(self):
        for line in self:
            if line.odoo_deletion_flag==True:
                continue
            if line.price_unit > 0:
                line.line_amount = line.quantity * (line.price / line.price_unit)
            else:
                line.line_amount = 0

    @api.multi
    def button_mass_to_confirm(self):
        """根据infocord生成的新价格info_price，批量确认新价格update_price
        步骤：1.根据po line排重查找po
              2.根据po生成po change
              3.根据po line的update_price对比 po line change的new_price
                如果是cost down直接更新po和po line，并更新po change和po line change的状态
                如果是cost up生成po change后送webflow签核
        """
        order_ids = []
        for line in self.ids:
            if line.order_id not in order_ids:
                order_ids.append(line.order_id)
        for order_id in order_ids:
            send_webflow = True
            if not order_id.changed:
                history_order = order_id._copy_history_order()
                order_id.write({'history_order_id': history_order.id})
            change_id = order_id.generate_order_change()# 生成po change
            max_order_line_code = len(order_id.line_ids)
            for order_line in order_id.order_line:
                max_order_line_code += 1
                # 更新po change
                for change_line in change_id.line_ids:
                    if change_line.order_line_id.id == order_line.id:
                        change_line.write({'new_qty': order_line.gr_qty + order_line.on_road_qty})
                        copy_change_line = change_line.copy()
                        copy_change_line['new_price'] = order_line.update_price
                        copy_change_line['new_qty'] = order_line.open_qty
                        copy_order_line['order_line_code'] = str(max_order_line_code)
                        change_line.create(copy_change_line)

                if order_line.update_price < order_line.price:# cost down
                    # 直接更新po line 和po line change的价格、数量，并新增item
                    order_line.with_context(apply_change=True).write({'quantity': order_line.gr_qty + order_line.on_road_qty})
                    copy_order_line = order_line.copy()
                    copy_order_line['ref_line_id'] = order_line.id
                    copy_order_line['price'] = order_line.update_price
                    copy_order_line['quantity'] = order_line.open_qty
                    copy_order_line['order_line_code'] = str(max_order_line_code)
                    order_line.create(copy_order_line)
                elif order_line.update_price > order_line.price:# cost up
                    send_webflow = True
            if send_webflow:
                change_id._send_to_webflow()
            else:
                change_id.write({'state': 'wait_vendor_confirm'})
                order_id.write({'state': 'wait_vendor_confirm'})

    @api.one
    def apply_po_line_audit(self):
        """
        记录当前po new 的audit 状态
                                  ("send_to_webflow","Send To Webflow"),
                                  ("approved_by_webflow","Approved By Webflow"),
                                  ("denied_by_webflow","Denied By Webflow"),
                                  ("send_to_sap","Send To SAP"),
                                  ("vendor_exception","Vendor Exception"),
                                  ("vendor_confirmed","Vendor Confirmed"),
                                  ('wait_vendor_confirm', 'Wait Vendor Confirm'),
        以上的状态变更的情况下备份记录po_line的变化情况
        :return:
        """
        po_line_audit_vals={
            "order_id":self.order_id.id,
            "order_line_id":self.id,
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
            "part_no":self.part_no,
            "plant_code":self.order_id.vendor_id.plant.plant_code,
            "buyer_code":self.order_id.buyer_id.buyer_erp_id,
            "division_code":self.part_id.division_id.division,
            "currency":self.currency_id.name,
            "vendor_delivery_date":self.vendor_delivery_date,
            "ori_qty":self.quantity,
            "new_qty":self.quantity,
            "ori_price":self.price,
            "new_price":self.price,
            "ori_price_unit":self.price_unit,
            "new_price_unit":self.price_unit,
            "ori_deletion_flag":self.odoo_deletion_flag,
            "new_deletion_flag":self.odoo_deletion_flag,
            "audit_source":"po_new",
            "ori_delivery_date":self.delivery_date,
            "new_delivery_date":self.delivery_date,
        }
        #根据po header状态补充相关字段
        if self.order_id.state=="webflow_error":
            po_line_audit_vals["action_type"]="webflow_error"
            po_line_audit_vals["state_msg"]=self.order_id.state_msg
        elif self.order_id.state=="to_approve":
            po_line_audit_vals["action_type"]="send_to_webflow"
        elif self.order_id.state=="unapproved":
            po_line_audit_vals["action_type"]="denied_by_webflow"
        elif self.order_id.state=="to_sap":
            po_line_audit_vals["action_type"]="send_to_sap"
        elif self.order_id.state=="sap_error":
            po_line_audit_vals["action_type"]="send_sap_error"
            po_line_audit_vals["state_msg"]=self.order_id.state_msg
        elif self.state=="wait_vendor_confirm":
            po_line_audit_vals["action_type"]="wait_vendor_confirm"
        elif self.state=="vendor_confirmed":
            po_line_audit_vals["action_type"]="vendor_confirmed"
        elif self.state=="vendor_exception":
            po_line_audit_vals["action_type"]="vendor_exception"
            po_line_audit_vals["vendor_exception_reason"]=self.vendor_exception_reason
        self.env["iac.purchase.order.line.audit"].create(po_line_audit_vals)

    @api.multi
    def write(self,vals):
        # if not (("apply_change" in self._context) or("state_change" in self._context)):
        #     raise UserError("Not Valid To Write PO Line")
        result=super(IacPurchaseOrderLine,self).write(vals)
        return result

class IacPurchaseOrderHistory(models.Model):
    """PO History主表"""
    _name = "iac.purchase.order.history"
    _description = "Purchase Order History"
    _order = 'id desc, name'

    ori_order_id = fields.Many2one('iac.purchase.order', string="Original Order Id")
    name = fields.Char(string="Order Code")

    order_amt = fields.Float(string='Order Amount')  # SAP传过来的订单总额
    order_date = fields.Date(string="PO Date")

    incoterm1 = fields.Char(string="Incoterm Destination")
    manually_po_reason_type = fields.Char(string="Manually Po Reason Type")
    manually_po_comment = fields.Text(string="Manually PO Comment")


    #附加关联字段
    line_ids = fields.One2many('iac.purchase.order.line.history', 'his_order_id', string="History Order Lines")
    currency_id = fields.Many2one('res.currency', string="Currency")
    payment_term_id = fields.Many2one('payment.term', string="Payment Term")
    incoterm_id = fields.Many2one('incoterm', string="Incoterm")
    plant_id = fields.Many2one('pur.org.data', string="Plant")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")

    #为数据迁移所准备的字段
    sap_key=fields.Char(string="SAP KEY")
    order_date = fields.Date(string="PO Date")
    order_type = fields.Char(string="Order Type")

    contact_name = fields.Char(string="Contact Name")
    contact_phone = fields.Char(string="Contact Phone")
    contact_fax = fields.Char(string="Contact Fax")

    company_code = fields.Char(string="Company Code")
    warehouse = fields.Char(string="Warehouse")
    version_no = fields.Char(string="Version")


    manually_po_reason = fields.Text(string="Manually PO Reason")
    manually_po_comment = fields.Text(string="Manually PO Comment")
    manually_po_comment2 = fields.Text(string="Manually PO Comment2")

    incoterm2 = fields.Char(string="Incoterm2")  # 使用incoterm1
    manually_po_type = fields.Text(string="Manually PO Type")  # 使用 manually_po_reason_type

    # 中间表附加的字段
    document_erp_id = fields.Char(string="Document Erp Id",index=True)

    manually_po_reason_type = fields.Char(string="Manually Po Reason Type")

    created_by = fields.Char(string="Created By")
    vendor_code = fields.Char(string="Vendor Code",index=True)
    vendor_name = fields.Char(related='vendor_id.name', string="Vendor Name")
    language_key = fields.Char(string="Language Key")
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)
    currency = fields.Char(string="Currency")
    exchange_rate = fields.Char(string="Exchange Rate")
    contact_person = fields.Char(string="Contact Person")

    order_release_status = fields.Char(string="Order Release Status")
    address_id = fields.Char(string="Address Id")
    your_reference = fields.Char(string="Your Reference")
    our_reference = fields.Char(string="Our Reference")

    incoterm = fields.Char(string="Incoterm From SAP")
    payment_term=fields.Char(string="Payment Term")
    purchase_org=fields.Char(string="Purchase Org",index=True)

    status = fields.Char(string="Status Message From SAP")
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记

    company_code = fields.Char(string="Company Code",index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")


class IacPurchaseOrderLineHistory(models.Model):
    """PO Line History从表"""
    _name = "iac.purchase.order.line.history"
    _description = u"PO Line History"
    _order = 'id desc, name'

    name = fields.Char(string="Order Line Code")

    division=fields.Char('division',related="part_id.division")
    quantity = fields.Float(string='Quantity')  # 当前行料号总数量
    price = fields.Float(string="Price", precision=(18, 4))  # 价格
    price_unit = fields.Integer(string="Price Unit")  # 价格单位
    delivery_date = fields.Date(string="Delivery Date")  # 交期
    storage_location = fields.Char(string="Storage Location")

    price_date = fields.Date(string="Price Date")
    purchase_req_no = fields.Char(string="Purchase Request No")# PR#
    purchase_req_item_no = fields.Char(string="Purchase Request Item No")# PR itme#

    #关联字段
    plant_id = fields.Many2one('pur.org.data', 'Plant')
    order_id = fields.Many2one('iac.purchase.order', string="Order Info")
    his_order_id = fields.Many2one('iac.purchase.order.history', string="Order History Id")
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Order Line Info")
    part_id = fields.Many2one('material.master.po.line', 'Part No')  # 物料
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    address_odoo_id = fields.Many2one('address', 'Address Id')

    #为数据迁移附加的字段
    order_code = fields.Char(string="Order Code", related="order_id.name", index=True)
    vendor_code = fields.Char(string="Vendor Code", index=True)
    order_date = fields.Date(string="PO Date",index=True)
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)


    line_text = fields.Char(string="Line Text")
    vendor_part_no = fields.Char(string="Vendor Part No")

    # 中间表附加字段
    deletion_flag = fields.Char(string='Delete Flag From SAP')
    document_erp_id = fields.Char(string="Document Erp Id",index=True)
    document_line_erp_id = fields.Char(string="Order line code",index=True)
    rfq_status = fields.Char(string="Rfq Status")
    change_date = fields.Char(string="Change Date")
    short_text = fields.Char(string="Short Text")
    part_no = fields.Char(string="Part No",index=True)
    part_no1 = fields.Char(string="Part No1")
    plant_code = fields.Char(string="Plant",index=True)
    manufacturer_part_no = fields.Char(string="Manufacturer Part No")
    unit = fields.Char(string="Unit")
    tracking_number = fields.Char(string="Tracking Number")
    revision_level = fields.Char(string="Revision Level")
    rfq_no = fields.Char(string="Rfq No")
    tax_code = fields.Char(string="Tax Code",index=True)
    reject_flag = fields.Char(string="Reject Flag")
    address_id = fields.Char(string="Address Id From SAP")
    vendor_to_be_supply = fields.Char(string="Vendor To Be Supply")
    delivery_complete = fields.Char(string="Delivery Complete")
    price = fields.Float(string="Price", precision=(18, 4))# 价格
    price_unit = fields.Integer(string="Price Unit")# 价格单位


    # lwt add relation fields
    odoo_deletion_flag = fields.Boolean(string='Delete', default=False)#删除标记
    sap_temp_id = fields.Integer(string="Sap Temp Info")

    #为数据迁移所准备的字段
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id = fields.Char(string="Sap log Info")
    line_amount = fields.Float(string="Line Amount", precision=(18, 4), compute='_taken_amount')
    currency_id = fields.Many2one('res.currency', string="Currency",index=True)

    @api.one
    @api.depends('quantity', 'price', 'price_unit')
    def _taken_amount(self):
        for line in self:
            if line.price_unit > 0:
                line.line_amount = line.quantity * (line.price / line.price_unit)
            else:
                line.line_amount = 0

class IacPurchaseOrderWizard(models.TransientModel):
    """单笔变更查询po向导"""
    _name = 'iac.purchase.order.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    part_id = fields.Many2one('material.master', 'Part No')
    division_id = fields.Many2one('division.code', string='Division Info')
    order_code = fields.Char(string="Order Code")
    only_changeable = fields.Boolean(string="Only Changeable",default=True, help="Search Only Changeable POS(Not in process of PO change)")
    only_open = fields.Boolean(string="Only Open PO")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")


    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        self.part_id=False
        self.vendor_id=False

    @api.multi
    def search_purchase_orders(self):
        result = []
        for wizard in self:
            domain = []
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.order_code:
                domain += [('document_erp_id', '=', wizard.order_code)]
            if wizard.only_changeable:
                #domain += [('state', 'in',['webflow_error','to_approve','unapproved','to_sap','sap_error','cancel','wait_vendor_confirm','vendor_confirmed','vendor_exception'])]
                domain += [('state', 'in',['webflow_error','unapproved','to_sap','sap_error','cancel','wait_vendor_confirm','vendor_confirmed','vendor_exception'])]
            if wizard.date_from:
                domain += [('order_date', '>=', wizard.date_from)]
            if wizard.date_to:
                domain += [('order_date', '<=', wizard.date_to)]
            order_ids = self.env['iac.purchase.order'].search(domain)

            #增加is_open,change_able判断
            if wizard.part_id:
                for order in order_ids:
                    #增加订单头排除条件
                    if wizard.only_open==True:
                        if order.is_open==False:
                            continue
                    if wizard.only_changeable==True:
                        if order.state in ['webflow_error','to_approve','unapproved','to_sap','sap_error','cancel','wait_vendor_confirm','vendor_confirmed','vendor_exception']:
                            continue
                    for line in order.order_line:
                        if wizard.part_id.id == line.part_id.id:
                            result.append(order)
            else:
                result = order_ids

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iac.purchase.order'
        }
        return action

class PoOrderPartner(models.Model):
    _name = "iac.purchase.order.partner"
    _order = 'id desc'

    document_erp_id = fields.Char(string="Document Erp Id",index=True)
    document_line_erp_id = fields.Char(string="Order line code",index=True)
    purchase_org = fields.Char(string="Purchase Org",index=True)
    partner_function = fields.Char(string="Partner Function")
    creation_date = fields.Date(string="Creation Date")
    reference_vendor_code = fields.Char(string="Reference Vendor Code")

    # lwt add relation fields
    po_line_id = fields.Many2one('iac.purchase.order.line', string="Ref PO Line Number")
    po_id = fields.Many2one('iac.purchase.order', string="Purchase Order")
    purchase_org_id = fields.Many2one('vendor.plant', string="Purchase Org")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)


class IacPurchaseOrderEdi855(models.Model):
    """PO 主表"""
    _name = "iac.purchase.order.edi.855"
    _description = "Purchase Order"
    _order = 'id desc, name'
    _inherit="iac.purchase.order"
    _table="iac_purchase_order"

    @api.model
    def update_edi_data(self):
        db_name = self.env.registry.db_name
        db = odoo.sql_db.db_connect(db_name)
        threading.current_thread().dbname = db_name
        cr = db.cursor()

        proc_result=True
        proc_ex=[]
        with api.Environment.manage():
            env=api.Environment(cr, self.env.uid, {})

            #获取唯一的序列值
            cr.execute("select nextval('public.odoo_po_005_id_seq')")
            result=cr.fetchall()
            seq_id=result[0][0]
            # 调用SAP接口
            biz_object = {
                "id": seq_id,
                "biz_object_id": seq_id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_PO_005", biz_object)

            # 根据order change更新order
            if rpc_json_data["rpc_callback_data"]["Message"]["Status"]!='Y':
                proc_result=True
                cr.commit()
                cr.close()
                return proc_result,proc_ex

            #当没有item数据的时候关闭连接直接退出
            if "ITEM" not in rpc_json_data["rpc_callback_data"]["Document"]:
                proc_result=True
                cr.commit()
                cr.close()
                return proc_result,proc_ex

            try:
                if rpc_result:

                    call_sap_item_list=[]
                    for json_item in rpc_json_data["rpc_callback_data"]["Document"]["ITEM"]:
                        order=env["iac.purchase.order"].search([('document_erp_id','=',json_item["PO_NO"])])

                        #这里发生异常应该处理
                        if not order.exists():
                            sap_item={
                                "PO_NO" : json_item["PO_NO"],
                                "EDI_TYPE" : "I855",
                                "EP_STATUS" : "EP3",
                                "EP_COMMENT" : "po dose not exists"
                            }
                            call_sap_item_list.append(sap_item)
                            continue

                        #判断当前po是否存在未提交po_change
                        if order.state=="to_change":
                            sap_item={
                                "PO_NO" : json_item["PO_NO"],
                                "EDI_TYPE" : "I855",
                                "EP_STATUS" : "EP3",
                                "EP_COMMENT" : "po is in change"
                            }
                            call_sap_item_list.append(sap_item)
                            continue

                        #排除所有异常后,保存数据，改写状态
                        order.write({"state":"vendor_confirmed"})
                        for order_line in order.order_line:
                            order_line.with_context(state_change=True).write({"state":"vendor_confirmed"})
                        sap_item={
                            "PO_NO" : json_item["PO_NO"],
                            "EDI_TYPE" : "I855",
                            "EP_STATUS" : "EP2",
                            "EP_COMMENT" : "SUCCESS"
                        }
                        call_sap_item_list.append(sap_item)


                    #调用SAP系统回传数据信息,遍历所有po进行接口调用
                    for sap_item in call_sap_item_list:
                        env.cr.execute("select nextval('public.odoo_po_006_id_seq')")
                        result=env.cr.fetchall()
                        seq_id=result[0][0]
                        biz_object = {
                            "id": seq_id,
                            "biz_object_id": seq_id,
                            "po_no":sap_item["PO_NO"],
                            "edi_type":sap_item["EDI_TYPE"],
                            "ep_status":sap_item["EP_STATUS"],
                            "ep_comment":sap_item["EP_COMMENT"],
                            }
                        rpc_result, rpc_json_data, log_line_id, exception_log = env[
                            "iac.interface.rpc"].invoke_web_call_with_log(
                            "ODOO_PO_006", biz_object)

                    #操作成功的情况下,修改记录状态
                    proc_result=True
                else:
                    proc_result=False
                    proc_ex.append(traceback.format_exc())
            except:
                traceback.print_exc()
                proc_result=False
                proc_ex.append(traceback.format_exc())
        cr.commit()
        cr.close()
        return proc_result,proc_ex
