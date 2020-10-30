# -*- coding: utf-8 -*-
from odoo import models, fields, api
import traceback

class WebCallOutWebflowF02(models.AbstractModel):
    _name = 'web.call.in.webflow.f02'
    _inherit="webflow.call.in.base"
    _description = "Web Call In Webflow F02 Interface"

    @api.multi
    def invoke_biz_mothod(self,context=None):
        """
        context 是webflow 传入的json调入参数
        调用业务模型的方法,做业务处理
        返回值为2个,第一个为布尔型,表示业务处理是否成功
        第二个为异常信息列表

        模型为 iac.vendor.regster
        context={"approve_status": True,"data":{"id":1376,}}

        :param context:
        :return:
        """
        odoo_model_name="iac.vendor"
        proc_context={
            "approve_status": False,
            "data": {
                "id": context.get("id",0),
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
            #json对象中的id为模型iac.vendor.register中的id,调用目标模型为iac.vendor
            #所以需要转换
            vendor_reg_rs=self.env["iac.vendor.register"].browse(int(context.get("id",0)))
            if (not vendor_reg_rs.exists()):
                ex_msg="can not found id = ( %s ) in model iac.vendor.register" %(context.get("id",0),)
                proc_ex.append(ex_msg)
                return proc_result,proc_ex

            vendor_id=vendor_reg_rs.vendor_id.id
            proc_context["data"]["id"]=vendor_id
            proc_result,proc_ex=self.env[odoo_model_name].vendor_be_normal_callback(proc_context)
        except:
            ex_string=traceback.format_exc()
            proc_result=False
            proc_ex.append(ex_string)
            traceback.print_exc()
        return proc_result,proc_ex

