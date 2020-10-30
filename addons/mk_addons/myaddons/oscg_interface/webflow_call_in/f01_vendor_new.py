# -*- coding: utf-8 -*-
from odoo import models, fields, api
import sys
import traceback
class WebCallOutWebflowF01(models.AbstractModel):
    _name = 'web.call.in.webflow.f01'
    _inherit="webflow.call.in.base"
    _description = "Web Call In Webflow F01 Interface"


    @api.multi
    def invoke_biz_mothod(self,context=None):
        """
        context 是webflow 传入的json调入参数
        调用业务模型的方法,做业务处理
        返回值为2个,第一个为布尔型,表示业务处理是否成功
        第二个为异常信息列表

        模型为 iac.vendor.regster
        context={"approve_status": True,"data":{"id":1376,"vendor_property":"Own Parts"}}

        :param context:
        :return:
        """
        odoo_model_name="iac.vendor.register"
        params=context.get("params")
        proc_context={
            "approve_status": False,
            "data": {
                "id": context.get("id",0),
                "vendor_property":params.get("vendor_property"),
                },
            "rpc_callback_data":context,
        }
        if (context["status"]=="true"):
            proc_context["approve_status"]=True
        else:
            proc_context["approve_status"]=False
        proc_result=False
        proc_ex=[]
        try:
            proc_result,proc_ex=self.env[odoo_model_name].vendor_register_callback(proc_context)
        except:
            ex_string=traceback.format_exc()
            proc_result=False
            proc_ex.append(ex_string)
            traceback.print_exc()

        return proc_result,proc_ex


