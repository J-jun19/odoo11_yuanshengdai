# -*- coding: utf-8 -*-
import random
from odoo import models, fields, api
import json
class interface_cfg(models.Model):

    _name = "iac.interface.cfg"
    _description = u"Interface Config"
    code=fields.Char(string="Interface Code",index=True)
    name=fields.Char(string="Interface Name")
    model_name=fields.Char(string="Interface Process Odoo Model Name")
    outer_sys_name=fields.Selection([("SAP","SAP"),("WebFlow","WebFlow"),("Fp","Fp")],string="Outer System Name")
    interface_type=fields.Selection([("interval timer","Interval Timer"),("restful api","Restful Api")],string="Interface Tech Type",default="interval timer")
    first_start_time=fields.Datetime(string="First Datetime Start")
    interval_seconds=fields.Integer(string="Interval In Seconds")
    fail_retry_times=fields.Integer(string="Fail Retry Times")
    seq_id=fields.Integer(string="Seq Id")
    outer_sys_call_url=fields.Text(string="Outer System Call Url")
    descripton=fields.Text(string="Descripton")
    sql_proc_code=fields.Text(string="SQL Proc Code Text")
    state=fields.Selection([("draft","Draft"),("active","Active"),("abandon","Abandon")],string="Interface  State",default="draft")
    call_type=fields.Selection([("call_out","Call Out"),("call_in","Call In")],string="Interface Call Type")

    @api.multi
    def name_get(self):
        return [(request.id, request.code+' '+request.name) for request in self]

class interface_manual_proc(models.Model):

    _name = "iac.interface.manual.proc"
    _description = u"Interface Manual Proc"
    manual_user_id=fields.Many2one("res.users",string="Manual User ID")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Datetime End")
    proc_line_count=fields.Integer(string="Interface Call Process Count")
    success_line_count=fields.Integer(string="Interface Call Success Count")
    fail_line_count=fields.Integer(string="Interface Call Fail Count")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail"),("abandon","Abandon")],string="Interface Call Manual State")
    memo_str=fields.Text(string="Memo String")
    log_line_ids=fields.One2many("iac.interface.log.line","manual_proc_id",string="Interface Log Lines")

class interface_biz_job(models.Model):

    _name = "iac.interface.biz.job"
    _description = u"Interface Business Job"
    manual_user_id=fields.Many2one("res.users",string="Manual User ID")
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface Info")
    biz_object_id=fields.Integer(string="Business Object ID")
    due_start_time=fields.Datetime(string="Due Start Time")
    state=fields.Selection([("wait","Wait"),("success","Success"),("processing","Processing"),("fail","Fail"),("abandon","Abandon")],string="Interface Call Manual State")
    memo_str=fields.Text(string="Memo String")
    log_line_ids=fields.One2many("iac.interface.log.line","job_id",string="Interface Log Lines")

class interface_manual_call(models.Model):

    _name = "iac.interface.manual.call"
    _description = u"Interface Manual Call"
    manual_user_id=fields.Many2one("res.users",string="Manual User ID")
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface Info")
    interface_code=fields.Char(string="Interface Code")
    interface_name=fields.Char(string="Interface Name")
    model_name=fields.Char(string="Interface Process Odoo Model Name")
    biz_object_id=fields.Integer(string="Business Object ID")
    biz_object_str=fields.Text(string="Business Object Params")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Datetime End")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail"),("abandon","Abandon")],string="Interface Call Manual State")
    json_request_str=fields.Text(string="JSON Request String")
    json_builder_exception_str=fields.Text(string="JSON Build Exception String")
    json_response_str=fields.Text(string="JSON Response String")
    memo_str=fields.Text(string="Memo String")
    log_line_ids=fields.One2many("iac.interface.log.line","manual_call_id",string="Interface Log Lines")



    @api.multi
    def button_invoke_web_call(self):

        exception_log=[]
        json_context=json.loads(self.biz_object_str)
        context={"biz_object_id":self.biz_object_id,
                 "interface_id":self.interface_id.id,
                 "interface_code":self.interface_id.code,
                 "manual_call_id":self.id,
                 "web_call_url":self.interface_id.outer_sys_call_url,
                 "user_code":self.env.user.login,
        }
        context.update(json_context)
        inf_model_name=self.interface_id.model_name
        rpc_json_data={}
        rpc_call_back_data={}
        exception_list=[]
        rpc_json_data,rpc_call_back_data,exception_list=self.env[inf_model_name].invoke_web_call(context)
        rpc_json_data_str=json.dumps(rpc_json_data)
        rpc_call_back_data_str=json.dumps(rpc_call_back_data)
        exception_list_str=json.dumps(exception_list)
        self.write({"json_request_str":rpc_json_data_str,"json_response_str":rpc_call_back_data_str,"fail_msg":exception_list_str})

    @api.multi
    def button_invoke_web_call_with_log(self):

        exception_log=[]
        json_context=json.loads(self.biz_object_str)
        context={"biz_object_id":self.biz_object_id,
                 "interface_id":self.interface_id.id,
                 "interface_code":self.interface_id.code,
                 "manual_call_id":self.id,
                 "web_call_url":self.interface_id.outer_sys_call_url,

                 "user_code":self.env.user.login,
        }
        context.update(json_context)
        inf_model_name=self.interface_id.model_name
        rpc_result=False
        rpc_json_data={}
        log_line_id=0
        exception_list=[]
        rpc_result,rpc_json_data,log_line_id,exception_list=self.env[inf_model_name].invoke_web_call_with_log(context)
        json_str=json.dumps(rpc_json_data)

        log_line_rs=self.env["iac.interface.log.line"].browse(log_line_id)
        self.write({"json_request_str":log_line_rs.call_json_msg,"json_response_str":json_str,"json_builder_exception_str":exception_list})

    @api.multi
    def button_invoke_web_call_from_json(self):
        exception_log=[]
        if (self.json_request_str==False):
            print("Please generate JSON first")
            return

        json_context=json.loads(self.biz_object_str)
        context={"json_params":self.json_request_str,
                 "interface_id":self.interface_id.id,
                 "interface_code":self.interface_id.code,
                 "manual_call_id":self.id,
                 "web_call_url":self.interface_id.outer_sys_call_url,
                 "json_builder_exception_str":self.json_builder_exception_str,
                 "user_code":self.env.user.login,
        }
        context.update(json_context)
        inf_model_name=self.interface_id.model_name
        json_result,exception_log=self.env[inf_model_name].invoke_web_call_from_json(context)
        json_str=json.dumps(json_result)
        self.write({"json_response_str":json_str,"fail_msg":exception_log})



    @api.multi
    def button_generate_web_call_json(self):

        exception_log=[]
        json_context=json.loads(self.biz_object_str)
        context={"biz_object_id":self.biz_object_id,
          "interface_id":self.interface_id.id,
          "interface_code":self.interface_id.code,
          "manual_call_id":self.id,
          "web_call_url":self.interface_id.outer_sys_call_url,
          "user_code":self.env.user.login,
        }
        context.update(json_context)
        inf_model_name=self.interface_id.model_name
        exception_log=[]
        json_result,exception_log=self.env[inf_model_name].generate_json(context)
        json_str=json.dumps(json_result)
        exception_log_str=json.dumps(exception_log)
        self.write({"json_request_str":json_str,"json_builder_exception_str":exception_log_str})



    @api.multi
    def invoke_web_call_with_log_test(self):
        """
        传入2个参数
        1   接口代码 F01_B
        2   接口调用json参数
                biz_object={
            "id":1,
            "biz_object_id":1
        }
        :return:
        """
        biz_object={
            "id":1,
            "biz_object_id":1
        }
        rpc_result=False
        rpc_json_data={}
        log_line_id=0
        exception_list=[]
        rpc_result,rpc_json_data,log_line_id,exception_log=self.env["iac.interface.rpc"].invoke_web_call_with_log("F01_B",biz_object)
        return rpc_result,rpc_json_data,log_line_id,exception_log

class interface_log(models.Model):

    _name = "iac.interface.log"
    _description = u"Interface Log"
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface")
    interface_code=fields.Char(string="Interface Code")
    interface_name=fields.Char(string="Interface Name")
    outer_sys_name=fields.Char(string="Outer System Name")
    max_try_times=fields.Integer(string="Max Try Times")
    biz_object_id=fields.Integer(string="Business Object ID")
    manual_user_id=fields.Many2one("res.users",string="Manual User ID")
    remain_try_times=fields.Integer(string="Remain Try Times")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Datetime End")
    call_type=fields.Selection([("call out","Call Out"),("call in ","Call In")],string="Interface Call Type")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail"),("fail in retry","Fail In retry"),("abandon","Abandon")],string="Interface State")
    fail_msg=fields.Text(string="Fail Msg")
    memo_str=fields.Text(string="Memo String")
    manual_proc_id=fields.Many2one("iac.interface.manual.proc",string="Interface Manual Proc")
    manual_call_id=fields.Many2one("iac.interface.manual.call",string="Interface Manual Call")
    log_line_ids=fields.One2many("iac.interface.log.line","log_id",string="Interface Log Lines")

class interface_log_line(models.Model):

    _name = "iac.interface.log.line"
    _description = u"Interface Log.line"
    _order="id desc"
    log_id=fields.Many2one("iac.interface.log",string="Interface Log")
    manual_proc_id=fields.Many2one("iac.interface.manual.proc",string="Interface Manual Proc")
    manual_call_id=fields.Many2one("iac.interface.manual.call",string="Interface Manual Call")
    job_id=fields.Many2one("iac.interface.biz.job",string="Interface Business Job")
    manual_user_id=fields.Many2one("res.users",string="Manual User ID")
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface")
    interface_code=fields.Char(string="Interface Code")
    interface_name=fields.Char(string="Interface Name")
    seq_id=fields.Integer(string="Log Seq Id")
    pair_id=fields.Integer(string="Interface Call Pair Id")
    manual_proc_seq_id=fields.Integer(string="Manual Proc Seq Id")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Datetime End")
    call_type=fields.Selection([("call_out","Call Out"),("call_in","Call In")],string="Interface Call Type")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail"),("fail in retry","Fail In retry"),("abandon","Abandon")],string="Interface State")
    manual_user_id=fields.Integer(string="Manual User ID")
    biz_object_id=fields.Integer(string="Business Object ID")
    fail_msg=fields.Text(string="Fail Msg")
    call_json_msg=fields.Text(string="Call Json Msg")
    json_builder_exception_str=fields.Text(string="JSON Build Exception String")
    callback_json_msg=fields.Text(string="Callback Json Msg")
    memo_str=fields.Text(string="Memo String")
    eform_no=fields.Char(string="EForm NO From Webflow")
    call_param_str=fields.Text(string="Call JSON Param String")

class interface_json_builder(models.Model):
    _name = "iac.interface.json.builder"
    _description = u"Interface JSON Builder.line"
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface")
    builder_type=fields.Selection([('odoo model','Odoo Model'),('raw sql','Raw SQL'),('fix value','Fix Value'),('eval script','Eval Script')],string="Builder Type")
    odoo_model_name=fields.Char(string="ODOO Model Name")
    builder_var_name=fields.Char(string="Builder Var Name")
    builder_var_context=fields.Text(string="Builder Var Context")
    builder_line_ids=fields.One2many('iac.interface.json.builder.line','builder_id',string='Builder Line Items')
    memo_str=fields.Char(string="Memo Str")

class interface_json_builder_line(models.Model):

    _name = "iac.interface.json.builder.line"
    _description = u"Interface JSON Builder.line"
    _order = 'json_field_path, json_field_seq'

    builder_id=fields.Many2one('iac.interface.json.builder',string='JSON Builder')
    json_field_name=fields.Char(string='JSON Field Name')
    json_field_path=fields.Char(string='JSON Field Path')
    json_field_seq=fields.Integer(string='JSON Field Sequence')
    json_field_type=fields.Selection([('fix value','Fix Value'),('object','Object'),('array','Array'),('simple type','Simple Type'),('date','Date'),('datetime','Datetime'),('custom calculate','Custom Calculate'),('eval script','Eval Script'),('relation travel','Relation Travel'),],string="JSON Field Type")
    source_field_name=fields.Char(string='Source Field Name')
    source_field_type=fields.Char(string='Source Field Type')
    parent_field_id=fields.Many2one('iac.interface.json.builder.line',string='Parent Field')
    memo_str=fields.Char(string="Memo Str")
    interface_id=fields.Many2one("iac.interface.cfg",string="Interface")