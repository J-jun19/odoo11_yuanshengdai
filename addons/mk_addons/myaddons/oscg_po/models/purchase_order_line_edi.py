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
from odoo.odoo_env import odoo_env
_logger = logging.getLogger(__name__)


class IacPurchaseOrderLineEdi(models.Model):
    """EDI Auto Confirm"""
    _name = "iac.purchase.order.line.edi"
    _description = u"PO Line Edit Auto Confirm"
    _order = 'po_no desc'

    name = fields.Char(string="Purchase Order Code",  index=True)
    po_no = fields.Char(string="Purchase Order Code",  index=True)
    po_line_no = fields.Char(string="Purchase Order Line Code",  index=True)
    part_no = fields.Char(string="Part No",  index=True)
    qty=fields.Float(string="Quantity")
    edi_type=fields.Char(string="EDI Type",default="I855")
    ep_status=fields.Selection([('EP2','success'),('EP3','fail')],string="EP Status For SAP")
    ep_comment=fields.Text(string="EP Comments")
    sap_fail_msg=fields.Text(string="EP Comments")
    state=fields.Selection([('draft','Draft'),
                            ('valid_fail','Valid Data fail'),
                            ('valid_success','Valid Data Success'),
                            ('sap_fail','SAP Fail'),
                            ('done','Done')],string="Status For ODOO",default="draft")
    sap_flag=fields.Selection([('Y','Y'),('N','N')],string="Has Processed For SAP",default="N")

    order_id = fields.Many2one('iac.purchase.order', string="Purchase Order", index=True)
    order_line_id = fields.Many2one('iac.purchase.order.line', string="Purchase Order Change", index=True)

    @api.model
    def sap_odoo_po_005(self):
        """
        调用SAP接口获取edi PO Line 数据信息
        :return:
        """
        #获取唯一的序列值
        self.env.cr.execute("select nextval('public.odoo_po_005_id_seq')")
        pg_result=self.env.cr.fetchall()
        seq_id=pg_result[0][0]
        # 调用SAP接口
        biz_object = {
            "id": seq_id,
            "biz_object_id": seq_id,
            "odoo_key": str(seq_id)
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_PO_005", biz_object)
        return rpc_result, rpc_json_data, log_line_id, exception_log


    def sap_odoo_po_006(self):
        """
        调用SAP接口发送edi PO Line 数据处理结果信息
        :return:
        """
        #获取唯一的序列值

        self.env.cr.execute("select nextval('public.odoo_po_006_id_seq')")
        pg_result=self.env.cr.fetchall()
        odoo_key=pg_result[0][0]
        # 调用SAP接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id,
            "odoo_key": str(odoo_key),
        }

        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_PO_006", biz_object)
        #不管处理成功或者失败一律标识为处理过
        self.write({"sap_flag":"Y"})
        return rpc_result, rpc_json_data, log_line_id, exception_log

    @api.model
    def load_po_line_edi_data(self):
        """
        从SAP系统接口获取edi PO Line数据,并且存储到本地表中
        :return:
        """
        #调用SAP接口获取数据
        rpc_result, rpc_json_data, log_line_id, exception_log=self.env["iac.purchase.order.line.edi"].sap_odoo_po_005()
        if rpc_result==False:
            return
        #没有数据直接返回
        if rpc_json_data.get("rpc_callback_data").get('Document',False)==False:
            return

        po_line_item_list = rpc_json_data.get("rpc_callback_data").get('Document').get('ITEM')
        #遍历po_line_item进行处理
        for po_line_item in po_line_item_list:
            po_line_edi_vals={
                "po_no":po_line_item.get("PO_NO",False),
                "po_line_no":str(int(po_line_item.get("PO_LINE_NO",False))),
                "qty":int(float(po_line_item.get("QTY",False))),
                "sap_flag":"N",
            }
            #对order_line_code补0操作
            if po_line_edi_vals.get("po_line_no",False)!=False:
                po_line_no=po_line_edi_vals.get("po_line_no",False)
                po_line_edi_vals["po_line_no"]=po_line_no.zfill(5)

            #判定现有表中是否存在条目
            domain=[('po_no','=',po_line_edi_vals.get("po_no",False)),('po_line_no','=',po_line_edi_vals.get("po_line_no",False))]
            po_line_edi=self.env["iac.purchase.order.line.edi"].search(domain,limit=1)
            if not po_line_edi.exists():
                po_line_edi=self.env["iac.purchase.order.line.edi"].create(po_line_edi_vals)
            else:
                #记录应存在的情况下标识为已经处理
                if po_line_edi.state not in ['done']:
                    po_line_edi.write({"sap_flag":"N"})
        self.env.cr.commit()
        return True

    @api.model
    def valid_po_line_edi_data(self):
        """
        验证数据是否合法,关键字段是否匹配
        :return:
        """
        domain=[('sap_flag','=','N'),('state','in',['draft','valid_fail'])]
        po_line_list=self.env["iac.purchase.order.line.edi"].search(domain)
        for po_line_edi in po_line_list:
            po_rec=self.env["iac.purchase.order"].search([('document_erp_id','=',po_line_edi.po_no)],limit=1)
            if not po_rec.exists():
                update_vals={
                    "state":"valid_fail",
                    "ep_status":"EP3",
                    "ep_comment":"PO NO not exists %s in odoo"%(po_line_edi.po_no,)
                }
                po_line_edi.write(update_vals)
                continue
            po_line_rec=self.env["iac.purchase.order.line"].search([('document_erp_id','=',po_line_edi.po_no),
                                                                       ('order_line_code','=',po_line_edi.po_line_no)
                                                                   ],limit=1)
            if not po_line_rec.exists():
                update_vals={
                    "state":"valid_fail",
                    "ep_status":"EP3",
                    "ep_comment":"PO Line NO not exists,PO No is  %s ,PO Line NO is %s"%(po_line_edi.po_no,po_line_edi.po_line_no)
                }
                po_line_edi.write(update_vals)
                continue

            #验证po的状态是否正常
            if po_rec.state not in ['wait_vendor_confirm','vendor_exception']:
                update_vals={
                    "state":"valid_fail",
                    "ep_status":"EP3",
                    "ep_comment":"PO No is  %s is not in state ['wait_vendor_confirm','vendor_exception']"%(po_line_edi.po_no,)
                }
                po_line_edi.write(update_vals)
                continue
            #验证po是否被签核过一次
            if po_rec.approve_flag==False:
                update_vals={
                    "state":"valid_fail",
                    "ep_status":"EP3",
                    "ep_comment":"PO No is  %s has not approved once"%(po_line_edi.po_no,)
                }
                po_line_edi.write(update_vals)
                continue

            #判定是否存在po_change,如果存在po_change则不能进行po_edi_confirm操作
            domain=[('order_id','=',po_rec.id)]
            po_change_rec=self.env["iac.purchase.order.change"].search(domain,limit=1)
            if po_change_rec.exists():
                update_vals={
                    "state":"valid_fail",
                    "ep_status":"EP3",
                    "ep_comment":"PO No is  %s has PO Change data,can not auto confirm"%(po_line_edi.po_no,)
                }
                po_line_edi.write(update_vals)
                continue

            #验证全部通过的情况下,标记状态
            update_vals={
                "order_id":po_rec.id,
                "order_line_id":po_line_rec.id,
                "state":"valid_success",
                "ep_status":"EP2",
                "ep_comment":False
            }
            po_line_edi.write(update_vals)
            self.env.cr.commit()
        self.env.cr.commit()


    @api.model
    def proc_po_line_edi_data(self):
        """
        对验证通过的po_line_edi进行处理
        :return:
        """
        domain=[('sap_flag','=','N'),('state','in',['sap_fail','valid_success'])]
        po_line_list=self.env["iac.purchase.order.line.edi"].search(domain)
        #循环调用sap告知confirm成功,sap调用成功后修改odoo这边的po_line 状态
        order_id_list=[]
        for po_line_edi in po_line_list:
            rpc_result, rpc_json_data, log_line_id, exception_log=po_line_edi.sap_odoo_po_006()
            #调用SAP失败的情况下
            if rpc_result==False:
                update_vals={
                    "sap_fail_msg":rpc_json_data,
                    "state":"sap_fail",
                    "sap_flag":"Y"
                }
                po_line_edi.write(update_vals)
                self.env.cr.commit()
            else:
                #调用SAP成功的情况下
                update_vals={
                    "sap_fail_msg":False,
                    "state":"done",
                    "sap_flag":"Y"
                }
                po_line_edi.write(update_vals)
                po_line_edi.order_line_id.write({"state":"vendor_confirmed"})
                po_line_edi.order_line_id.apply_po_line_audit()
                if po_line_edi.order_id.id not in order_id_list:
                    order_id_list.append(po_line_edi.order_id.id)
                self.env.cr.commit()

        #判定当前order是否所有的条目都是vendor_confirmed状态
        for order_id in order_id_list:
            self.env.cr.execute("""
            SELECT
                SUM (
                    po_line_state.confirm_count
                ) confirm_count,
                SUM (po_line_state.all_count) all_count
            FROM
                (
                    SELECT
                        COUNT (*) confirm_count,
                        0 all_count
                    FROM
                        iac_purchase_order_line
                    WHERE
                        order_id = %s
                    AND STATE = 'vendor_confirmed'
                    UNION ALL
                        SELECT
                            0,
                            COUNT (*)
                        FROM
                            iac_purchase_order_line
                        WHERE
                            order_id = %s
                ) po_line_state
            """,(order_id,order_id))
            pg_result=self.env.cr.fetchone()
            #所有po line 都confirmed的情况下,设置po header状态为confirm
            if pg_result[0]==pg_result[1]:
                order_rec=self.env["iac.purchase.order"].browse(order_id)
                order_rec.write({"state":"vendor_confirmed"})
                self.env.cr.commit()

        #处理失败的记录,回调SAP通知SAP状态
        domain=[('sap_flag','=','N'),('state','in',['valid_fail'])]
        po_line_list=self.env["iac.purchase.order.line.edi"].search(domain)
        for po_line_edi in po_line_list:
            rpc_result, rpc_json_data, log_line_id, exception_log=po_line_edi.sap_odoo_po_006()
            #调用SAP失败的情况下
            if rpc_result==False:
                update_vals={
                    "sap_fail_msg":rpc_json_data,
                }
                po_line_edi.write(update_vals)
                self.env.cr.commit()
            else:
                #调用SAP成功的情况下
                update_vals={
                    "sap_fail_msg":False,
                    "sap_flag":"Y"
                }
                po_line_edi.write(update_vals)
                self.env.cr.commit()

    @odoo_env
    @api.model
    def job_po_line_edi_confirm(self):
        #从SAP 系统加载load po line edi
        logging.info("job_po_line_edi_confirm start,thread name is %s" %(threading.currentThread().getName()))
        self.load_po_line_edi_data()

        #数据有效性校验
        self.valid_po_line_edi_data()

        #进行相关作业处理
        self.proc_po_line_edi_data()

        logging.info("job_po_line_edi_confirm run success,thread name is %s" %(threading.currentThread().getName()))