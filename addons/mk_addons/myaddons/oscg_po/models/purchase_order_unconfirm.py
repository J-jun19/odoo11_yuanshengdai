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

def odoo_thread_env(func,**kwargs):
    def __decorator(self,**kwargs):    #add parameter receive the user information
        db_name = self.env.registry.db_name
        db = odoo.sql_db.db_connect(db_name)
        threading.current_thread().dbname = db_name
        cr = db.cursor()
        print threading.current_thread().getName()+" open db connection"
        with api.Environment.manage():
            try:
                env=api.Environment(cr, self.env.uid, {})
                self.env=env
                func(self,**kwargs)

            except:
                traceback.print_exc()
        cr.commit()
        cr.close()
        print threading.current_thread().getName()+" close db connection"

    return __decorator
class IacPurchaseOrderUnconfirmSummary(models.Model):
    """PO 的操作日志报表用途"""
    _name = "iac.purchase.order.unconfirm.summary"
    _description = u"PO Unconfrim Summary"
    _order = 'id desc'

    #中间表字段
    document_no=fields.Char(string="Purchase Order Code")
    document_line_no=fields.Char(string="Purchase Order LIne Code")
    part_no=fields.Char(string="Part No")
    plant_id=fields.Char(string="Plant")
    buyer_erp_id=fields.Char(string="Buyer Code")
    description=fields.Char(string="Description")
    division_code=fields.Char(string="Division Code")
    vendor_erp_id=fields.Char(string="Vendor Code")
    vendor_name=fields.Char(string="Vendor Name")
    unconqtyd=fields.Float(string="Unconfirm Qty Decrease",digits=(18,4))
    unconqtyr=fields.Float(string="Unconfirm Qty Increase",digits=(18,4))
    price =fields.Float(string="Price",digits=(18,4))
    price_unit=fields.Float(string="Price Unit",digits=(18,4))
    currency =fields.Char(string="Currency Name")
    last_update_date=fields.Datetime(string="Last Update Date")
    data_type=fields.Selection([('history','History'),('current','Current')],string="Data Type",default="history")
    #附加关联字段
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Order Line Id", index=True)
    part_id = fields.Many2one('material.master', string="Part Info", index=True)
    odoo_plant_id = fields.Many2one('pur.org.data', string="Plant Id", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    division_id = fields.Many2one('division.code', string="Division Info", index=True)
    source_code =fields.Char(string="Source Code")
    currency_id = fields.Many2one('res.currency', string="Currency Info", index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")



class IacPurchaseOrderUnconfirmDetail(models.Model):
    """PO 的操作日志报表用途"""
    _name = "iac.purchase.order.unconfirm.detail"
    _description = u"PO Audit Log"
    _order = 'document_no asc'

    #中间表字段
    document_no=fields.Char(string="Purchase Order Code")
    document_line_no=fields.Char(string="Purchase Order Line Code")
    part_no=fields.Char(string="Part No")
    plant_id=fields.Char(string="Plant")
    vendor_erp_id=fields.Char(string="Vendor Code")
    vendor_name=fields.Char(string="Vendor Name")
    description=fields.Char(string="Description")
    buyer_erp_id=fields.Char(string="Buyer Code")
    orig_total_qty=fields.Float(string="Buyer Code",digits=(18,4))
    total_qty=fields.Float(string="Buyer Code",digits=(18,4))
    deletion_flag=fields.Char(string="Deletion Flag")
    diff =fields.Float(string="Diff",digits=(18,4))
    currency=fields.Char(string="Currency Name")
    price=fields.Float(string="Price",digits=(18,4))
    priceunit=fields.Float(string="Price Unit",digits=(18,4))
    change_date=fields.Datetime(string="Change Date")
    division_code=fields.Char(string="Division Code")
    flag=fields.Char(string="Flag")
    last_update_date=fields.Datetime(string="Last Update Date")
    data_type=fields.Selection([('history','History'),('current','Current')],string="Data Type",default="history")
    ori_deletion_flag = fields.Boolean(string='Ori Deletion Flag')#初始删除标记
    new_deletion_flag = fields.Boolean(string='New Deletion Flag' )#变更后删除标记
    #附加关联字段
    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Order Line Id", index=True)
    order_line_change_id = fields.Many2one('iac.purchase.order.line.change', string="Order Line Change Id", index=True)
    odoo_plant_id = fields.Many2one('pur.org.data', string="Plant Id", index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Info", index=True)
    division_id = fields.Many2one('division.code', string="Division Info", index=True)
    source_code =fields.Char(string="Source Code")
    currency_id = fields.Many2one('res.currency', string="Currency Info", index=True)
    part_id = fields.Many2one('material.master', string="Part Info", index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")

    @api.model
    def update_unconfirm_data_exception(self,order_id):
        """
        处理po 状态为vendor_exception时候的unconfirm记录情况
        po状态vendor_exception
            存在po_change,并且po的version_no<=1  --OK
                不做任何处理
            存在po_change,并且po的version_no>1  --OK
                对vendor_exception的po_line生成confirm数据(如果存在就unconfirm的，先更新为history,然后创建新的unconfirm)
                对vendor_confirmed的po_line,更新unconfirm表中的数据从current更新为history
            不存在po_change
                不做任何处理--
                針對vendor_confirmed的PO_line, 如果PO version_no >=2,按PO line 找unconfirmed detail and summary,如果存在current記錄，都更新為history
                針對vendor_exception的PO_line, 如果PO version_no >=2,按PO line 找unconfirmed detail and summary,如果存在current記錄，先更新为history,然后创建新的unconfirm
        :param order_id:
        :return:
        """
        order_rec=self.env["iac.purchase.order"].browse(order_id)

        #判断版本号是否大于1,初始po version_no 为null,送签一次为1，生产change后为2
        self.env.cr.execute("""
         select cast(COALESCE(version_no,'0') as int4) from iac_purchase_order where id=%s
        """,(order_id,))
        pg_result=self.env.cr.fetchall()
        version_no=pg_result[0][0]

        #version_no<=1,那么不做任何处理
        if  version_no<=1:
            return

        #对po中已经confirmed的po_line更新状态为history
        self.env.cr.execute("""
        UPDATE iac_purchase_order_unconfirm_detail po_line_unconfirm
            SET data_type = 'history'
            WHERE
                po_line_unconfirm.data_type = 'current'
            and po_line_unconfirm.order_id = %s
            AND EXISTS (
                SELECT
                    1
                FROM
                    iac_purchase_order_line po_line
                WHERE
                    po_line.order_id = %s
                AND po_line. ID = po_line_unconfirm.order_line_id
                AND po_line. STATE = 'vendor_confirmed'
            )
        """,(order_id,order_id))

        #po_change存在的情况下,要生成相应的unconfirm数据
        if order_rec.last_change_id.exists():
            for order_line_change in order_rec.last_change_id.line_ids:
                if order_line_change.change_state=='no_change':
                    continue
                #对已经confrim的order_line不写入unconfirm数据
                if order_line_change.order_line_id.state=='vendor_confirmed':
                    continue

                #对于vendor_exception的数据写入unconfirm detail
                if order_line_change.order_line_id.state=='vendor_exception':
                    #对已经存在的vendor_exception设置为history
                    self.env.cr.execute("""
                    UPDATE iac_purchase_order_unconfirm_detail po_line_unconfirm
                        SET data_type = 'history'
                        WHERE po_line_unconfirm.order_id=%s and po_line_unconfirm.order_line_id=%s
                            and po_line_unconfirm.order_line_change_id = %s and po_line_unconfirm.data_type = 'current'
                    """,(order_id,order_line_change.order_line_id.id,order_line_change.id))

                unconfirm_vals={
                        "buyer_erp_id":order_line_change.part_id.buyer_erp_id,
                        "buyer_id":order_line_change.part_id.buyer_code_id.id,
                        "change_date":order_line_change.create_date,
                        "currency":order_line_change.currency_id.name,
                        "currency_id":order_line_change.currency_id.id,
                        "diff":0,
                        "division":order_line_change.part_id.division,
                        "division_id":order_line_change.part_id.division_id.id,
                        "document_no":order_line_change.order_id.document_erp_id,
                        "document_line_no":order_line_change.order_line_code_2,
                        "last_update_date":order_line_change.write_date,
                        "odoo_plant_id":order_line_change.order_id.plant_id.id,
                        "flag":"vendor_exception",
                        "order_id":order_line_change.order_id.id,
                        "order_line_id":order_line_change.order_line_id.id,
                        "order_line_change_id":order_line_change.id,
                        "part_id":order_line_change.part_id.id,
                        "part_no":order_line_change.part_id.part_no,
                        "plant_id":order_line_change.order_id.plant_id.plant_code,
                        "price":order_line_change.new_price,
                        "priceunit":order_line_change.last_price_unit,
                        "total_qty":order_line_change.new_qty,
                        "vendor_erp_id":order_line_change.order_id.vendor_id.vendor_code,
                        "vendor_name":order_line_change.order_id.vendor_id.name,
                        "source_code":order_line_change.part_id.sourcer,
                        "ori_deletion_flag":order_line_change.ori_deletion_flag,
                        "new_deletion_flag":order_line_change.odoo_deletion_flag,
                        "orig_total_qty":order_line_change.ori_qty,
                        "data_type":"current"
                        }
                if order_line_change.odoo_deletion_flag==True:
                    unconfirm_vals["total_qty"]=0
                if order_line_change.ori_deletion_flag==False and  order_line_change.odoo_deletion_flag==True:
                    unconfirm_vals["orig_total_qty"]=order_line_change.new_qty
                    unconfirm_vals["total_qty"]=0
                if order_line_change.ori_deletion_flag==True and  order_line_change.odoo_deletion_flag==False:
                    unconfirm_vals["orig_total_qty"]=0
                    unconfirm_vals["total_qty"]=order_line_change.new_qty
                unconfirm_vals["diff"]=unconfirm_vals["total_qty"]-unconfirm_vals["orig_total_qty"]
                self.env["iac.purchase.order.unconfirm.detail"].create(unconfirm_vals)

        #summary必定进行重算
        self.env.cr.execute("""
        update iac_purchase_order_unconfirm_summary
          set data_type='history' where order_id=%s and data_type='current'
        """,(order_id,))

        self.env.cr.execute("""
            select order_id,order_line_id,part_id
                ,sum((case when diff >=00 then diff else 0 end)) unconfirm_inc,
                sum((case when diff <00 then diff else 0 end)) unconfirm_dec
            from iac_purchase_order_unconfirm_detail
            where order_id=%s and data_type='current' group by order_id,order_line_id,part_id
        """,(order_id,))
        pg_result=self.env.cr.fetchall()

        #遍历汇总结果写入summary表
        for order_id,order_line_id,part_id,unconfirm_inc,unconfirm_dec in pg_result:
            po_line=self.env["iac.purchase.order.line"].browse(order_line_id)
            unconfirm_vals={
                "buyer_erp_id":po_line.part_id.buyer_erp_id,
                "buyer_id":po_line.part_id.buyer_code_id.id,
                "currency":po_line.order_id.currency_id.name,
                "currency_id":po_line.order_id.currency_id.id,
                "description":po_line.part_id.part_description,
                "division_code":po_line.part_id.division,
                "division_id":po_line.part_id.division_id.id,
                "document_no":po_line.order_id.document_erp_id,
                "document_line_no":po_line.order_line_code,
                "last_update_date":po_line.write_date,
                "odoo_plant_id":po_line.order_id.plant_id.id,
                "order_id":po_line.order_id.id,
                "order_line_id":po_line.id,
                "part_id":po_line.part_id.id,
                "part_no":po_line.part_id.part_no,
                "plant_id":po_line.order_id.plant_id.plant_code,
                "price":po_line.price,
                "price_unit":po_line.price_unit,
                "vendor_erp_id":po_line.order_id.vendor_id.vendor_code,
                "vendor_name":po_line.order_id.vendor_id.name,
                "source_code":po_line.part_id.sourcer,
                "unconqtyd":unconfirm_dec,
                "unconqtyr":unconfirm_inc,
                "data_type":"current"
                }
            order_line_confirmed_rec=self.env["iac.purchase.order.unconfirm.summary"].create(unconfirm_vals)

    @api.model
    def update_unconfirm_data_confirmed(self,order_id):
        """
        po状态vendor_confirmed
            存在po_change,并且po 的version_no>1  --OK
                更新当前存在unconfirm表中的记录,把unconfirm current 更新成为history
            不存在po_change,po 直接送签的情况
                不做任何处理 -- 如果PO version_no >=2,找unconfirmed detail and summary,如果存在current記錄，都更新為history

        :param order_id:
        :return:
        """
        order_rec=self.env["iac.purchase.order"].browse(order_id)

        #判断版本号是否大于1,初始po version_no 为null,送签一次为1，生产change后为2
        self.env.cr.execute("""
         select cast(COALESCE(version_no,'0') as int4) from iac_purchase_order where id=%s
        """,(order_id,))
        pg_result=self.env.cr.fetchall()
        version_no=pg_result[0][0]
        #version_no<=1,那么不做任何处理
        if  version_no<=1:
            return

        #更新detail中的unconfirm记录状态
        self.env.cr.execute("""
        update iac_purchase_order_unconfirm_detail
          set data_type='history' where order_id=%s and data_type='current'
        """,(order_id,))

        #更新summary中的unconfirm记录状态
        self.env.cr.execute("""
        update iac_purchase_order_unconfirm_summary
          set data_type='history' where order_id=%s and data_type='current'
        """,(order_id,))


    @api.model
    def generate_unconfirm_data(self,order_change_id):
        """
        在完成po_change的时候需要生成相应的unconfrim数据
        只能被po_change对象调用
        :param action_type:
        :param order_id:
        :return:
        """
        po_change_rec=self.env["iac.purchase.order.change"].browse(order_change_id)
        order_id=po_change_rec.order_id.id

        #判断版本号是否大于1,初始po version_no 为null,送签一次为1，生产change后为2
        self.env.cr.execute("""
         select cast(COALESCE(version_no,'0') as int4) from iac_purchase_order where id=%s
        """,(order_id,))
        pg_result=self.env.cr.fetchall()
        version_no=pg_result[0][0]
        #version_no<=1,那么不做任何处理
        if  version_no<=1:
            return

        #po_change存在的情况下,要生成相应的unconfirm数据
        for order_line_change in po_change_rec.line_ids:
            if order_line_change.change_state=='no_change':
                continue
            #对已经confrim的order_line不写入unconfirm数据
            if order_line_change.order_line_id.state=='vendor_confirmed':
                continue

            #对于vendor_exception的数据写入unconfirm detail
            if order_line_change.order_line_id.state=='vendor_exception':
                continue

            unconfirm_vals={
                    "buyer_erp_id":order_line_change.part_id.buyer_erp_id,
                    "buyer_id":order_line_change.part_id.buyer_code_id.id,
                    "change_date":order_line_change.create_date,
                    "currency":order_line_change.currency_id.name,
                    "currency_id":order_line_change.currency_id.id,
                    "diff":0,
                    "division":order_line_change.part_id.division,
                    "division_id":order_line_change.part_id.division_id.id,
                    "document_no":order_line_change.order_id.document_erp_id,
                    "document_line_no":order_line_change.order_line_code_2,
                    "last_update_date":order_line_change.write_date,
                    "odoo_plant_id":order_line_change.order_id.plant_id.id,
                    "flag":"vendor_exception",
                    "order_id":order_line_change.order_id.id,
                    "order_line_id":order_line_change.order_line_id.id,
                    "order_line_change_id":order_line_change.id,
                    "part_id":order_line_change.part_id.id,
                    "part_no":order_line_change.part_id.part_no,
                    "plant_id":order_line_change.order_id.plant_id.plant_code,
                    "price":order_line_change.new_price,
                    "priceunit":order_line_change.last_price_unit,
                    "total_qty":order_line_change.new_qty,
                    "vendor_erp_id":order_line_change.order_id.vendor_id.vendor_code,
                    "vendor_name":order_line_change.order_id.vendor_id.name,
                    "source_code":order_line_change.part_id.sourcer,
                    "ori_deletion_flag":order_line_change.ori_deletion_flag,
                    "new_deletion_flag":order_line_change.odoo_deletion_flag,
                    "orig_total_qty":order_line_change.ori_qty,
                    "data_type":"current"
                    }
            if order_line_change.odoo_deletion_flag==True:
                unconfirm_vals["total_qty"]=0
            if order_line_change.ori_deletion_flag==False and  order_line_change.odoo_deletion_flag==True:
                unconfirm_vals["orig_total_qty"]=order_line_change.new_qty
                unconfirm_vals["total_qty"]=0
            if order_line_change.ori_deletion_flag==True and  order_line_change.odoo_deletion_flag==False:
                unconfirm_vals["orig_total_qty"]=0
                unconfirm_vals["total_qty"]=order_line_change.new_qty
            unconfirm_vals["diff"]=unconfirm_vals["total_qty"]-unconfirm_vals["orig_total_qty"]
            self.env["iac.purchase.order.unconfirm.detail"].create(unconfirm_vals)

        #summary必定进行重算
        self.env.cr.execute("""
        update iac_purchase_order_unconfirm_summary
          set data_type='history' where order_id=%s and data_type='current'
        """,(order_id,))

        self.env.cr.execute("""
            select order_id,order_line_id,part_id
                ,sum((case when diff >=00 then diff else 0 end)) unconfirm_inc,
                sum((case when diff <00 then diff else 0 end)) unconfirm_dec
            from iac_purchase_order_unconfirm_detail
            where order_id=%s and data_type='current' group by order_id,order_line_id,part_id
        """,(order_id,))
        pg_result=self.env.cr.fetchall()

        #遍历汇总结果写入summary表
        for order_id,order_line_id,part_id,unconfirm_inc,unconfirm_dec in pg_result:
            po_line=self.env["iac.purchase.order.line"].browse(order_line_id)
            unconfirm_vals={
                "buyer_erp_id":po_line.part_id.buyer_erp_id,
                "buyer_id":po_line.part_id.buyer_code_id.id,
                "currency":po_line.order_id.currency_id.name,
                "currency_id":po_line.order_id.currency_id.id,
                "description":po_line.part_id.part_description,
                "division_code":po_line.part_id.division,
                "division_id":po_line.part_id.division_id.id,
                "document_no":po_line.order_id.document_erp_id,
                "document_line_no":po_line.order_line_code,
                "last_update_date":po_line.write_date,
                "odoo_plant_id":po_line.order_id.plant_id.id,
                "order_id":po_line.order_id.id,
                "order_line_id":po_line.id,
                "part_id":po_line.part_id.id,
                "part_no":po_line.part_id.part_no,
                "plant_id":po_line.order_id.plant_id.plant_code,
                "price":po_line.price,
                "price_unit":po_line.price_unit,
                "vendor_erp_id":po_line.order_id.vendor_id.vendor_code,
                "vendor_name":po_line.order_id.vendor_id.name,
                "source_code":po_line.part_id.sourcer,
                "unconqtyd":unconfirm_dec,
                "unconqtyr":unconfirm_inc,
                "data_type":"current"
                }
            order_line_confirmed_rec=self.env["iac.purchase.order.unconfirm.summary"].create(unconfirm_vals)
