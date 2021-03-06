# -*- coding: utf-8 -*-
from odoo import models, fields, api
import traceback
class WebCallOutWebflowF07(models.AbstractModel):
    _name = 'web.call.in.webflow.f07_e_2'
    _inherit="webflow.call.in.base"
    _description = "Web Call In Webflow F07 po change Interface"


    @api.model
    def invoke_biz_mothod(self,context=None):
        """
        调用业务模型的方法,做业务处理
        返回值为2个,第一个为布尔型,表示业务处理是否成功
        第二个为异常信息列表
        :param context:
        :return:
        """
        odoo_model_name="iac.purchase.order.change"
        proc_context={
            "approve_status": False,
            "data": {
                "id": int(context.get("id",0)),
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
            proc_result,proc_ex=self.env[odoo_model_name].po_change_callback(proc_context)
        except:
            ex_string=traceback.format_exc()
            proc_result=False
            proc_ex.append(ex_string)
            traceback.print_exc()
        return proc_result,proc_ex
