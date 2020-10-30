# -*- coding: utf-8 -*-
from odoo import models, fields, api

class WebCallOutWebflowF04(models.AbstractModel):
    _name = 'web.call.out.webflow.f04'
    _inherit="webflow.call.out.base"
    _description = "Web Call Out Webflow F04 Interface"

    @api.multi
    def generate_json(self,context=None):
        exeception_log=[]
        json_data,exeception_log=super(WebCallOutWebflowF04,self).generate_json(context)
        return json_data,exeception_log


    @api.multi
    def invoke_web_call_from_json_with_log(self,context=None):
        """
        首先根据context中的条件生成远程调用json对象,如果产生构建错误则返回
        ,不存在构建错误,则继续远程调用
        进行远程调用,返回远程调用的json数据对象

        返回值有4个
        1   布尔型,远程调用是否成功
        2   远程调用返回的json数据对象
        3   日志id
        4   异常信息列表
        """
        rpc_result=False
        rpc_json_data={}
        log_line_id=0
        exception_list=[]
        rpc_result,rpc_json_data,log_line_id,exception_list=super(WebCallOutWebflowF04,self).invoke_web_call_from_json_with_log(context)

        return rpc_result,rpc_json_data,log_line_id,exception_list
