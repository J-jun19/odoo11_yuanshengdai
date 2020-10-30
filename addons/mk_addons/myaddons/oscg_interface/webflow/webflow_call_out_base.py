# -*- coding: utf-8 -*-
from .. json_builder.json_builder_wt import *
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval as eval
import urllib2
import json
import time
import datetime
import traceback
import sys
import traceback



class WebflowCallOutBase(models.AbstractModel):
    _name = 'webflow.call.out.base'
    _description = "Web Call Out Base Class"
    _order = 'date desc'

    @api.multi
    def get_server_file_url(self,file_url):
        """
        传入文件链接 获取文件链接后在获取服务器地址，组合之后返回
        :param file_url:
        :return:
        """
        if file_url==False:
            return ""

        config_rs = self.env['ir.config_parameter'].search([('key', '=', 'web.server.url')], limit=1)
        server_url=config_rs.value
        file_url=server_url+file_url
        return file_url
        pass

    @api.multi
    def generate_json(self,context=None):
        """
        生成调用接口的json对象
        返回值是2个
        1   是json对象
        2   另外一个是生成json时的异常信息
        :param context:
        :return:
        """
        json_obj_data={}
        exeception_log=[]
        script_env={}
        script_env["self"]=self
        script_env["env"]=self.env
        #params={"id":context["biz_object_id"]}
        #script_env["params"]=params

        if ("interface_id" not in context):
            print("When call build_biz_json function,\"interface_id\"  must specificed")
            ex_msg="When call build_biz_json function,\"interface_id\"  must specificed"
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

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
        director=JSONBuilderDirector(director_context,field_list_builder)
        json_obj_data=director.build_json_obj()
        ex_log=director.exception_log
        exeception_log=exeception_log+ex_log

        context.update(director.context)
        return json_obj_data,exeception_log

    @api.multi
    def invoke_web_call_from_json(self,context=None):
        """
         通过指定context中的json字符串信息,进行接口调用
         返回2个值
         1  返回远程调用的json数据对象
         2  异常信息列表
         :param context:
         :return:
         """
        json_obj_data={}
        exeception_log=[]
        rpc_json_data={}

        if ("web_call_url" not in context):
            print ("must set web_call_url in context")
            ex_msg="must set web_call_url in context"
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        if ("json_params" not in context):
            print ("must set json_params in context")
            ex_msg="must set json_params in context"
            exeception_log.append(ex_msg)
            return json_obj_data,exeception_log

        web_call_url=context["web_call_url"]
        json_params=context["json_params"]
        headers = {'Content-Type': 'application/json'}

        try:
            rpc_json_params=json.dumps(json_params)
            request = urllib2.Request(web_call_url, rpc_json_params, headers)
            response = urllib2.urlopen(request)
            rpc_json_data = json.loads(response.read())
        except:
            #处理未捕获的异常信息
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            exeception_log.append(ex_string)
            traceback.print_exc()
        return rpc_json_data,exeception_log


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

        #调用函数构建json对象
        json_data,exception_list=self.generate_json(context)

        #在日志表中记录，接口信息
        log_line_rec=self.create_log(context)
        self.env.cr.commit()
        log_line_id=log_line_rec.id


        #发生构建json错误的情况下,记录日志,退出方法
        if len(exception_list)>0:
            log_vals={"call_json_msg":json.dumps(json_data),
                      "json_builder_exception_str":json.dumps(exception_list),
                      "state":"fail",
                      }
            log_line_rec.write(log_vals)
            self.env.cr.commit()
            return call_result,callback_json,log_line_id,exception_list



        rpc_context={}
        rpc_context.update(context)
        json_data["inf_call_id"]=log_line_id
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
            self.env.cr.commit()
            return call_result,callback_json,log_line_id,exception_list


        #远程过程调用成功的情况下，进行业务校验
        validate_result=False
        log_vals={}
        validate_ex_list=[]
        validate_result,log_vals,exception_list_3=self.validate_callback_biz_data(callback_json)
        if validate_result==False:
            #业务校验失败的情况下,记录日志返回
            exception_list=exception_list+exception_list_3
            log_vals={"call_json_msg":json.dumps(json_data),
                      "callback_json_msg":json.dumps(callback_json),
                      "state":"fail",
                      "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                      "fail_msg":json.dumps(exception_list),
                      }
            log_line_rec.write(log_vals)
            self.env.cr.commit()
            return validate_result,callback_json,log_line_id,exception_list
        else:
            #校验未发生异常,写入单号
            log_line_rec.write({"eform_no":callback_json["EFormNO"]})
            self.env.cr.commit()

        #所有操作都成功,没有构建错误,没有远程调用错误,没有返回值校验错误
        #记录日志,调用处理成功回调方法
        call_back_context={}
        call_back_context.update(context)
        call_back_context["callback_json_msg"]=callback_json
        proc_result=False
        proc_result,exception_list_4=self.proc_callback_func(call_back_context)
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
            self.env.cr.commit()
            return proc_result,callback_json,log_line_id,exception_list

        #所有操作都成功的情况下,记录日志返回
        log_vals={"call_json_msg":json.dumps(json_data) ,
                  "callback_json_msg":json.dumps(callback_json),
                  "state":"success",
                  "end_time":time.strftime("%Y-%m-%d %H:%M:%S"),
                  }
        log_line_rec.write(log_vals)
        self.env.cr.commit()
        call_result=True
        return call_result,callback_json,log_line_id,exception_list



    @api.model
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
            "outer_sys_name":interface_rs.outer_sys_name,
            "max_try_times":interface_rs.fail_retry_times,
            "remain_try_times":interface_rs.fail_retry_times,
            "call_type":interface_rs.call_type,
            "start_time":time.strftime("%Y-%m-%d %H:%M:%S"),
            "call_param_str":context.get("call_param_str")
        }

        log_vals["biz_object_id"]=context["params"]["biz_object_id"]
        if "manual_call_id" in context:
            log_vals["manual_call_id"]=context["manual_call_id"]

        log_line=self.env["iac.interface.log.line"].create(log_vals)
        return log_line


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

        if "status" in call_back_result:
            if call_back_result["status"]=="true":
                log_vals["state"]="success"
            else:
                log_vals["state"]="fail"
                log_vals["fail_msg"]=call_back_result.get("message")
                validate_result=False
                exception_log.append(log_vals["fail_msg"])
                return validate_result,log_vals,exception_log
        else:
            exception_log.append("Biz callback data has no key named ( status )")
            log_vals["state"]="fail"
            validate_result=False
            return validate_result,log_vals,exception_log


        if "EFormNO" in call_back_result:
            log_vals["eform_no"]=call_back_result["EFormNO"]
        else:
            exception_log.append("Biz callback data has no key named ( EFormNO )")
            log_vals["state"]="fail"
            validate_result=False
            return validate_result,log_vals,exception_log

        #通过业务校验
        validate_result=True
        return validate_result,log_vals,exception_log

    @api.multi
    def proc_callback_func(self,context=None):
        """
        在rpc成功返回后，业务校验通过后,执行本地方法进行业务处理
        返回值有2个
        1   布尔类型,本地业务处理是否成功
        2   异常信息列表

        :param context:
        :return:
        """
        proc_result=True
        exception_list=[]
        return proc_result,exception_list