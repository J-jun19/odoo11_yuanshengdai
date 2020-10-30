# -*- coding: utf-8 -*-
from ..json_builder.json_builder_wt import  *
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval as eval
#import urllib2
import requests
import json
import time
import datetime
import traceback
import sys
import traceback


from odoo import tools
import hashlib


class SapCallOutBase(models.AbstractModel):
    _name = 'sap.call.out.base'
    _description = "Sap Out Base Class"
    _order = 'date desc'
    #测试环境为QAS,正式环境为PRD,用来生成odoo_key
    sap_odoo_key_prefix="QAS"

    @api.multi
    def get_odoo_key(self,interface_code):
        """
        QAS和PRD 由当前类的静态成员sap_odoo_key_prefix决定
        "QAS"+"ODOO"+接口編號+年月日(yyyyMMdd)組成字串后，做MD5加密
        "PRD"+"ODOO"+接口編號+年月日(yyyyMMdd)組成字串后，做MD5加密
        返回值只有1个
        1 返回一个字符串
        :param interface_code: 接口编码
        :return:
        """
        time_str=time.strftime("%Y%m%d")
        odoo_key_str="%s%s%s%s"%(SapCallOutBase.sap_odoo_key_prefix,"ODOO",interface_code,time_str)
        m = hashlib.md5()
        m.update(odoo_key_str)
        psw = m.hexdigest()
        return psw

    @api.model
    def generate_json(self,context=None):
        """
            生成调用接口的json对象,返回值是2个,
            1 是json对象,
            2 异常信息列表
        :param context:
        :return:
        """
        exeception_log=[]
        json_obj_data={}
        if ("interface_id" not in context):
            ex_msg="When call build_biz_json function,\"interface_id\"  must specificed"
            print("When call build_biz_json function,\"interface_id\"  must specificed")
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        if ("interface_code" not in context):
            ex_msg="When call build_biz_json function,\"interface_id\"  must specificed"
            print("When call build_biz_json function,\"interface_id\"  must specificed")
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        #input={}
        #header={}
        #header["INT_NO"]=context["interface_code"]
        #header["PASSWORD"]=self.get_odoo_key(context["interface_code"])
        ##ODOO_KEY准备使用接口日志id，但此时接口日志id未获取，所以先设置为0
        #header["ODOO_KEY"]="0"
        script_env={}
        script_env["self"]=self
        script_env["env"]=self.env
        params={"id":context["biz_object_id"]}
        script_env["params"]=params


        #将传入的参数复制到director对象的参数节点中
        director_context={
            "params":{}
        }
        director_context["params"].update(context)
        context.update(script_env)
        builder_lines=self.env["iac.interface.json.builder.line"].search([('interface_id','=',context['interface_id']),('parent_field_id','=',False)])
        #我们认定根节点为JSON容器为字典类型
        field_list_builder=JSONObjectFieldListBuilder(builder_lines,context)


        config_rs = self.env['ir.config_parameter'].search([('key', '=', 'web.server.url')], limit=1)
        director_context["server_url"]=config_rs.value
        director_context["default_date_format"]="%m/%d/%Y"
        director_context["default_datetime_format"]="%Y/%m/%d %H:%M:%S"
        #%Y/%m/%d %H:%M:%S
        director=JSONBuilderDirector(director_context,field_list_builder)
        json_obj_data=director.build_json_obj()
        exeception_log=exeception_log+director.exception_log

        #input["Document"]=json_obj_data
        #input["Header"]=header
        #return input,exeception_log
        return json_obj_data,exeception_log

    @api.multi
    def invoke_web_call_from_json(self,context=None):
        """
         通过指定context中的json字符串信息,进行接口调用

         返回2值,
         1  返回调用结果对象
         2  返回异常信息列表
         :param context:
         :return:
         """
        exeception_log=[]
        json_obj_data={}
        if ("web_call_url" not in context):
            print ("web_call_url must set  in context")
            ex_msg="web_call_url must set  in context"
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        if ("json_params" not in context):
            print ("json_params must set  in context")
            ex_msg="json_params must set  in context"
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        web_call_url=context["web_call_url"]
        json_params=context["json_params"]
        headers = {'Content-Type': 'application/json'}

        try:
            json_params_str=json.dumps(json_params)

            headers = {'Content-Type': 'application/json'}
            result = requests.post(url=web_call_url,data=json_params_str,headers=headers)
            json_obj_data = json.loads(result.content)
            #print r.content

            #urlib2 调用 odoo_fp_001 产生致命的 http 500 异常,所以切换到了requests
            #request = urllib2.Request(web_call_url, json_params_str, headers)
            #response = urllib2.urlopen(request)
            #json_obj_data = json.loads(response.read())
        except:
            #处理未捕获的异常信息
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            exeception_log.append(ex_string)
            traceback.print_exc()
        return json_obj_data,exeception_log



    @api.multi
    def invoke_web_call(self,context=None):
        """
        调用Restful Api 调用generate_json函数生成json对象
        然后发送给invoke_web_call_from_json函数进行调用

        返回值有3个
        1   远程调用接口返回的json数据对象 rpc_callback_data
        2   生成的 rpc_json_data
        2   异常信息列表 exception_list
        """
        #生成调用接口相关的json参数对象
        exception_list=[]
        rpc_json_data,exception_list=self.generate_json(context)

        #调用接口,通过制定json参数调用接口
        context["json_params"]=rpc_json_data

        rpc_callback_data,exception_list_1=self.invoke_web_call_from_json(context)

        exception_list=exception_list+exception_list_1
        return rpc_json_data,rpc_callback_data,exception_list



    @api.multi
    def invoke_web_call_with_log(self,context=None):
        """
        首先根据context中的条件生成远程调用json对象,如果产生构建错误则返回
        ,不存在构建错误,则继续远程调用
        进行远程调用,返回远程调用的json数据对象

        返回值有4个
        1   布尔型,远程调用是否成功
        2   远程调用返回的json数据对象
        3   日志id
        4   异常信息列表

        :param context:
        :return:
        """
        call_result=False
        callback_json={}
        log_line_id=0
        exception_list=[]
        #生成调用接口相关的json参数对象

        json_data,exception_list=self.generate_json(context)

        #在日志表中记录，接口信息
        log_line_rec=self.create_log(context)
        self.env.cr.commit()

        #发生构建json错误的情况下,记录日志,退出方法
        if len(exception_list)>0:
            log_vals={"call_json_msg":json.dumps(json_data),
                      "json_builder_exception_str":json.dumps(exception_list),
                      "state":"fail",
                      }
            log_line_rec.write(log_vals)
            #self.write_log(log_line_id,log_vals)
            self.env.cr.commit()
            return call_result,json_data,log_line_id,exception_list

        rpc_context={}
        rpc_context.update(context)
        json_data["inf_call_id"]=log_line_id
        #json_data["Input"]["Header"]["ODOO_KEY"]=log_line_id
        rpc_context["json_params"]=json_data
        rpc_context["log_line_id"]=log_line_id

        #进行远程调用,返回相关异常信息
        callback_json,exception_list_2=self.invoke_web_call_from_json(rpc_context)
        exception_list=exception_list+exception_list_2
        if len(exception_list)>0:
            call_result=False
            #远程调用失败的情况下,应该记录日志并且返回
            log_vals={"call_json_msg":json.dumps(json_data),
                      "callback_json_msg":callback_json,
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":exception_list,
                      }
            log_line_rec.write(log_vals)
            #self.write_log(log_line_id,log_vals)
            self.env.cr.commit()
            return call_result,callback_json,log_line_id,exception_list

        #远程过程调用成功的情况下，进行业务校验
        validate_result=False
        log_vals={}
        validate_ex_list=[]
        validate_result,log_vals,exception_list_3=self.validate_callback_biz_data(callback_json)
        #业务校验失败或者远程返回失败信息,都视为业务校验失败，记录日志返回
        if validate_result==False:
            exception_list=exception_list+exception_list_3
            log_vals={"call_json_msg":json.dumps(json_data),
                      "callback_json_msg":json.dumps(callback_json),
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(exception_list),
                      }
            log_line_rec.write(log_vals)
            #self.write_log(log_line_id,log_vals)
            self.env.cr.commit()
            call_result=False
            return call_result,json_data,log_line_id,exception_list

        #所有操作都成功,没有构建错误,没有远程调用错误,没有返回值校验错误
        #记录日志,调用处理成功回调方法
        call_back_context={}
        call_back_context.update(context)
        call_back_context["callback_json_msg"]=callback_json

        #对远程回调做加工处理
        proc_result=False
        result_dict={}
        proc_result,result_dict,exception_list_4=self.process_callback_func(call_back_context)
        if proc_result==False:
            #执行本地业务操作失败,记录日志退出
            exception_list=exception_list+exception_list_4
            log_vals={"call_json_msg":json.dumps(json_data),
                      "callback_json_msg":json.dumps(callback_json),
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(exception_list),
                      }
            log_line_rec.write(log_vals)
            #self.write_log(log_line_id,log_vals)
            self.env.cr.commit()
            return proc_result,callback_json,log_line_id,exception_list

        #所有操作都成功的情况下,记录日志返回
        log_vals={"call_json_msg":json.dumps(json_data) ,
                  "callback_json_msg":json.dumps(callback_json),
                  "state":"success",
                  "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                  }
        log_line_rec.write(log_vals)
        #self.write_log(log_line_id,log_vals)
        self.env.cr.commit()
        call_result=True
        return call_result,result_dict,log_line_id,exception_list

    @api.multi
    def create_log(self,context=None):
        """
        在接口日志表中新增一条记录,存储接口相关的基础信息
        返回值有1个
        1   接口日志ID
        :param vals:
        :param context:
        :return:
        """
        interface_rs=self.env["iac.interface.cfg"].search([('id','=',context["interface_id"])])
        log_vals={
            "interface_id":interface_rs.id,
            "interface_code":interface_rs.code,
            "interface_name":interface_rs.name,
            "call_type":interface_rs.call_type,
            "start_time":time.strftime("%Y-%m-%d %H:%M:%S"),
            "call_param_str":context.get("call_param_str")
            }

        log_vals["biz_object_id"]=context["params"]["biz_object_id"]
        if "manual_call_id" in context:
            log_vals["manual_call_id"]=context["manual_call_id"]

        log_line_rec=self.env["iac.interface.log.line"].create(log_vals)
        #log_line_id=log_line.id
        return log_line_rec

    @api.multi
    def write_log(self,id,vals,context=None):
        """
        调用接口返回之后更新日志
        :param context: 写日志相关参数
        :return:
        """
        log_vals={}
        log_vals.update(vals)
        log_line_rec=self.env["iac.interface.log.line"].browse(id)
        log_line_rec.write(vals)

    @api.multi
    def validate_callback_biz_data(self,call_back_result):
        """
        校验业务数据格式是否正确
        返回参数有3个
        1   布尔型表示业务校验是否通过
        2   日志数据字典
        3   异常信息列表

        :param id:
        :param vals:
        :param context:
        :return:
        """
        validate_result=False
        log_vals={}
        exception_log=[]
        if "Message" not in call_back_result:
            log_vals["state"]="fail"
            ex_msg="Remote call returned json object has no key ( Message )"
            exception_log.append(ex_msg)
            validate_result=False
            return validate_result,log_vals,exception_log

        if "Status" not in call_back_result["Message"]:
            log_vals["state"]="fail"
            ex_msg="Remote call returned json object has no key ( Message/Status )"
            exception_log.append(ex_msg)
            validate_result=False
            return validate_result,log_vals,exception_log

        if call_back_result["Message"]["Status"]=="Y":
            log_vals["state"]="success"
        else:
            log_vals["state"]="fail"
            log_vals["fail_msg"]=call_back_result.get("Message")
            validate_result=False
            exception_log.append(log_vals["fail_msg"])
            return validate_result,log_vals,exception_log

        validate_result=False
        #通过业务校验失败或者远程返回失败信息的情况下，都视为业务校验失败
        if log_vals["state"]=="success":
            validate_result=True
        else:
            validate_result=False
        return validate_result,log_vals,exception_log

    def process_callback_func(self,context):
        """
        在远程调用服务返回成功标志之后,调用本地的回调函数进行处理

        返回值有3个
        1   布尔型,是否处理成功
        2   处理后的字典对象
        3   异常信息列表
        :param context:
        :return:
        """
        proc_result=True
        result_dict={}
        exception_list=[]
        print "base class process_callback_func has called"
        return proc_result,result_dict,exception_list

#读取配置文件中的配置信息初始化
conf_obj=tools.config
sap_odoo_key_prefix=conf_obj.get("sap_odoo_key_prefix")
if sap_odoo_key_prefix==None:
    raise "sap_odoo_key_prefix must set in openerp-server.conf file"

SapCallOutBase.sap_odoo_key_prefix=sap_odoo_key_prefix
