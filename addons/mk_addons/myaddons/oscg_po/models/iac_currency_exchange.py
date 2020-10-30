# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime
from odoo import models, fields, api,odoo_env
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from odoo.odoo_env import odoo_env
from functools import wraps
import  traceback
import threading


class IacCurrencyExchange(models.Model):
    """PO Line从表"""
    _name = "iac.currency.exchange"
    _description = u"IAC Currency Exchange"
    _order = 'id desc'

    from_currency_id=fields.Many2one('res.currency',string='From Currency',index=True)
    to_currency_id=fields.Many2one('res.currency',string='To Currency',index=True)
    op_date=fields.Date(string='Date',index=True,default=fields.date.today())
    state=fields.Selection([('active','Active'),('history','History')],string="Status")
    sap_status=fields.Selection([('Y','Y'),('N','N')],string="SAP Status")
    sap_message=fields.Text(string='SAP Message')
    from_currency_amount = fields.Float(string="From Currency Amount",digits=(16,6))
    to_currency_amount = fields.Float( string="To Currency Amount",digits=(16,6))


    @api.model
    def get_usd_exchange_record(self,from_currency_id):
        """
        获取转换到美元的汇率记录,所有to_currency_id都为美元,所以不用查询to_currency_id
        :param from_currency_id:
        :return:
        """
        #op_date=fields.date.today().strftime("%Y/%m/%d")
        op_date=fields.date.today()
        result=self.search([('from_currency_id','=',from_currency_id),('op_date','<=',op_date)],limit=1,order="op_date desc")
        return result


    @odoo_env
    @api.model
    def job_iac_currency_exchange_update(self):
        """
        更新最新的币种到美元的汇率
        :return:
        """

        usd_currency=self.env["res.currency"].search([('name','=','USD')])
        #如果美元不存在那么不转换汇率
        if not usd_currency.exists():
            return False

        currency_list=self.env["res.currency"].search([('active','=',True),('name','!=','USD')])
        for currency_rec in currency_list:

            sequence = self.env['ir.sequence'].next_by_code('iac.interface.rpc')
            vals = {
                "id": int(sequence),
                "biz_object_id": int(sequence),
                "date":fields.date.today().strftime("%Y%m%d"),
                "foreign_currency":currency_rec.name,#从这个货币转换
                "foreign_amount":"1000",
                "local_currency":"USD", #目标货币都是美元
                "foreign_amount_unit":"1"
                }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env['iac.interface.rpc'].invoke_web_call_with_log(
                "ODOO_OTHER_001", vals)
            if rpc_result==False:
                continue

            if rpc_json_data["rpc_callback_data"]["Message"]["Status"]=="Y":
                vals={
                    "from_currency_id":currency_rec.id,
                    "to_currency_id":usd_currency.id,
                    "state":"active",
                    "sap_status":"Y",
                    "from_currency_amount":1000,
                    "to_currency_amount":float(rpc_json_data["rpc_callback_data"]["Document"]["LOCAL_AMOUNT"])
                }
                #将历史数据更新状态
                domain=[('from_currency_id','=',currency_rec.id)]
                domain+=[('to_currency_id','=',usd_currency.id)]
                domain+=[('state','=',"active")]
                last_currency_rec=self.env["iac.currency.exchange"].search(domain)
                last_currency_rec.write({"state":"history"})

                #创建最新的汇率数据
                self.env["iac.currency.exchange"].create(vals)
            else:
                vals={
                    "from_currency_id":currency_rec.id,
                    "to_currency_id":usd_currency.id,
                    "state":"history",
                    "sap_status":"N",
                    "from_currency_amount":1000,
                    "sap_message":rpc_json_data["rpc_callback_data"]["Message"]["Message"],
                }
                #记录日志作用的汇率数据
                self.env["iac.currency.exchange"].create(vals)
