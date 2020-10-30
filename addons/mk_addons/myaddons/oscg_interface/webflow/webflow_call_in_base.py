# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval as eval
import urllib2
import json
import time
import datetime
import traceback
import sys
import traceback
from odoo import tools



class WebflowCallInBase(models.AbstractModel):
    _name = 'webflow.call.in.base'
    _description = "Web Call In Base Class"

    @api.multi
    def validate_biz_data(self,context=None):
        """
        校验业务数据,判断是否合法
        在这里要实现，通过数据识别接口的功能,获取接口相关的数据
        可能存在异常的情况
        1   缺少特定数据
        2   找不到对应的业务数据
        3   数据格式不符

        返回值为4个
        1   布尔型，表示是否校验通过;
        2  前置log_line_id
        3  异常信息列表;

        :param context:
        :return:
        """
        validate_result=True
        validate_ex=[]
        interface_data={}
        prev_log_line_id=0
        if "id" not in context:
            validate_result=False
            validate_ex.append("id field must set")

        if "EFormNO" not in context:
            validate_result=False
            validate_ex.append("EFormNO field must set")

        if "status" not in context:
            validate_result=False
            validate_ex.append("status field must set")

        if "FormStatus" not in context:
            validate_result=False
            validate_ex.append("FormStatus field must set")

        log_line_rs=self.env["iac.interface.log.line"].search([("eform_no","=",context.get("EFormNO")),
                                                                 ("biz_object_id","=",context.get("id")),
                                                           ])
        #if (len(log_line_rs.ids)==0):
        #    validate_result=False
        #    ex_msg="EFormNO is %s ,biz_object_id is %s not found in log" %(context.get("EFormNO"),context.get("id",0))
        #    validate_ex.append(ex_msg)
        #else:
        #    #由于默认由webflow调入的操作都有前置操作,所以获取前置的日志id
        #    log_line_rec=log_line_rs.browse(log_line_rs.ids[0])
        #    prev_log_line_id=log_line_rec.id

        #业务校验位假的情况下,直接返回
        if validate_result==False:
            return validate_result,prev_log_line_id,validate_ex


        validate_result=True
        return validate_result,prev_log_line_id,validate_ex


    @api.multi
    def invoke_biz_mothod(self,context=None):
        """
        调用业务模型的方法,做业务处理
        返回值为2个,第一个为布尔型,表示业务处理是否成功
        第二个为异常信息列表
        :param context:
        :return:
        """
        proc_result=True
        exception_list=[]
        return proc_result,exception_list
        pass

    @api.multi
    def call_in_func(self,context=None):
        """
        webflow 回调的应该使用当前方法为入口方法
        首先要解析数据,验证业务逻辑是否合理
            合理则调用模型相关方法处理
            不合理,那么则组织异常信息
        记录日志信息
        组织返回数据,如果有异常那么返回数据中包含异常信息
        返回数据

        返回值有2个

        1   返回给远程接口调用的json对象,包含业务校验和业务处理的异常信息
        2   日志id

        :param context:
        :return:
        """
        validate_ex=[]

        rpc_response={
            "status": "false",
            "message": "",
            "id": str(context.get("id",0)),
            "EFormNO": context.get("EFormNO")
        }

        #记录日志信息
        log_vals={
            "call_json_msg":json.dumps(context)
        }
        log_line_rec=self.env["iac.interface.log.line"].create(log_vals)
        log_line_id=log_line_rec.id
        self.env.cr.commit()

        interface_result=False
        interface_result,interface_data=self.get_interface_data(context.get("stage"))
        if interface_result==False:
            #没有找到指定的接口
            ex_msg="Can not found interface width code %s"%(context.get("stage"),)
            rpc_response["message"]=ex_msg
            #记录日志,返回日志id
            log_vals={
                      "callback_json_msg":json.dumps(rpc_response),
                      "state":"fail",
                      "start_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(validate_ex),
                      "eform_no":context.get("EFormNO"),
                      }
            log_line_rec.write(log_vals)
            self.env.cr.commit()
            return rpc_response


        #进行业务数据校验
        validate_result,prev_log_line_id,validate_ex=self.validate_biz_data(context)

        #更新日志信息
        log_vals={}
        log_vals["start_time"]=time.strftime("%Y-%m-%d %H:%M:%S")
        log_vals.update(interface_data)
        log_line_rec.write(log_vals)
        self.env.cr.commit()


        if (validate_result==False):
            #业务校验失败,组织异常信息返回
            rpc_response["message"]=validate_ex
            rpc_response["status"]="false"

            #记录日志,返回日志id
            log_vals={"call_json_msg":json.dumps(context),
                      "callback_json_msg":json.dumps(rpc_response),
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(validate_ex),
                      "eform_no":context.get("EFormNO"),
                      }
            log_line_rec.write(log_vals)
            self.env.cr.commit()
            return rpc_response

        #业务校验通过的情况下进行业务处理
        proc_result=False
        proc_ex=[]
        proc_result,proc_ex=self.invoke_biz_mothod(context)
        self.env.cr.commit()
        #调用业务对象回调方法处理异常的情况下，把异常信息写入到返回方法中
        log_line_rec=self.env["iac.interface.log.line"].browse(log_line_id)
        if (proc_result==False):
            rpc_response["message"]=proc_ex
            rpc_response["status"]="false"
            #执行本地业务操作失败,记录日志退出

            log_vals={"call_json_msg":json.dumps(context),
                      "callback_json_msg":json.dumps(rpc_response),
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(proc_ex),
                      "eform_no":context.get("EFormNO"),
                      }
            log_line_rec.write(log_vals)
            self.env.cr.commit()
            return rpc_response

        #业务处理正常,记录日志并且返回
        rpc_response["status"]="true"
        log_vals={"call_json_msg":json.dumps(context),
                  "callback_json_msg":json.dumps(rpc_response),
                  "state":"success",
                  "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                  "eform_no":context.get("EFormNO"),
                  }
        log_line_rec.write(log_vals)
        self.env.cr.commit()
        return rpc_response

    @api.multi
    def get_interface_data(self,interface_code,context=None):
        """
        传入接口编码,根据接口编码组织接口相关的数据
        返回值有2个
        1   布尔型
        2   接口相关数据

        :param interface_code:
        :param context:
        :return:
        """
        interface_vals={}
        interface_rs=self.env["iac.interface.cfg"].search([("code","=",interface_code)])
        if len(interface_rs.ids)==0:
            return False,interface_vals
        interface_rec=self.env["iac.interface.cfg"].browse(interface_rs.ids[0])
        interface_vals["interface_code"]=interface_rec.code
        interface_vals["interface_name"]=interface_rec.name
        interface_vals["interface_id"]=interface_rec.id
        interface_vals["call_type"]=interface_rec.call_type
        return True,interface_vals
