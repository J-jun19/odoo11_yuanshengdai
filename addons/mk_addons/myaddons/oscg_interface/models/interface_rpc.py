# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
from odoo import tools

class InterfaceRpc(models.AbstractModel):
    _name = 'iac.interface.rpc'
    _description = "Interface rpc"


    @api.multi
    def invoke_web_call_with_log(self,interface_code,biz_object):
        """
        传入2个参数
        1   接口代码 F01_B
        2   接口调用json参数
                biz_object={
            "id":1,
            "biz_object_id":1
        }

        返回值有4个
        1   布尔型处理结果
        2   json数据对象
        3   日志id
        4   异常信息列表

        :return:
        """
        #传入2个参数

        #是否是假的接口调用,直接返回4个参数不进行实际的接口调用
        #运用在本机接口调试上是使用
        conf_obj=tools.config
        if conf_obj.get('dummy_interface',False):
            return True,{},0,[]

        #获取接口配置,每个接口都有一个代码，通过代码获取接口配置信息
        interface_cfg_rs=self.env["iac.interface.cfg"].sudo().search([('code','=',interface_code)])

        #批量替换无效的False值
        for key in biz_object:
            if biz_object[key]==False:
                biz_object[key]=""

        exception_log=[]
        context={
            "interface_id":interface_cfg_rs.id,
            "interface_code":interface_cfg_rs.code,
            "web_call_url":interface_cfg_rs.outer_sys_call_url,
            }
        context.update(biz_object)
        context["user_code"]=self.env.user.login
        context["call_param_str"]=json.dumps(biz_object)

        inf_model_name=interface_cfg_rs.model_name
        rpc_result=False
        rpc_json_data={}
        log_line_id=0
        exception_list=[]
        rpc_result,rpc_json_data,log_line_id,exception_log=self.env[inf_model_name].sudo().invoke_web_call_with_log(context)
        return rpc_result,rpc_json_data,log_line_id,exception_log
