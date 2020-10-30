# -*- coding: utf-8 -*-
import traceback
from odoo import models, fields, api

class WebCallOutSapAsn001(models.AbstractModel):
    _name = 'web.call.out.sap.asn.001'
    _inherit="sap.call.out.base"
    _description = "Web Call Out Sap ODOO_ASN_001 Interface"


    @api.multi
    def invoke_web_call_with_log(self,context=None):
        """
        根据入参数进行远程调用,参数存储在context中,并且存储日志,处理回调函数等
        分为2步操作,首先生成远程调用的json数据对象
        然后将远程调用json对象作为参数传入进行远程调用
        返回值有4个
        1   布尔型,远程调用是否成功
        2   远程调用返回的json数据对象
        3   日志id
        4   异常信息列表
        :param context:
        :return:
        """
        rpc_result=True
        rpc_data={}
        exception_log=[]
        log_line_id=0
        json_data,exception_log=super(WebCallOutSapAsn001,self).generate_json(context)
        context["json_params"]=json_data
        rpc_result,rpc_data,log_line_id,exception_log=super(WebCallOutSapAsn001,self).invoke_web_call_with_log(context)
        return rpc_result,rpc_data,log_line_id,exception_log

    @api.multi
    def process_callback_func(self,context):
        """
        在远程调用服务返回成功标志之后,调用本地的回调函数进行处理

        返回值有3个
        1   布尔型,是否处理成功
        2   处理后的字典对象
        3   异常信息列表
        """
        #print "sub class process_callback_func has been called"
        proc_result=True
        result_dict={}
        exception_list=[]
        try:
            result_dict["rpc_callback_data"]=context["callback_json_msg"]
        except:
            traceback.print_exc()
            exception_list.append(traceback.format_exc())
            proc_result=False


        print "base class process_callback_func has called"
        return proc_result,result_dict,exception_list