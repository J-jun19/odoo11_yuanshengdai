# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json

class interface_temp_table_group(models.Model):
    """
        存储中间表分组信息
    """
    _name = "iac.interface.temp.table.group"
    _description = u"Interface Temp Table Group"
    code=fields.Char(string="Group Code")
    name=fields.Char(string="Group Name")
    first_start_time=fields.Datetime(string="First Datetime Start")
    interval_seconds=fields.Integer(string="Interval In Seconds")
    seq_id=fields.Integer(string="Seq Id")

    exe_line_ids=fields.One2many('iac.interface.temp.table.group.line','group_id',string="Group Lines Info")

    @api.model
    def trans_group_data(self,group_name=None):
        print 'interface_temp_table_group, group_name is ( %s ) has invoked' %( group_name,)
        pass
class interface_temp_table_group_line(models.Model):
    """
        存储中间表分组条目信息
    """
    _name = "iac.interface.temp.table.group.line"
    _description = u"Interface Temp Table Group Line"
    group_line_code=fields.Char(string="Group Line Code")
    group_line_name=fields.Char(string="Group Line Name")
    sap_group_line_name=fields.Char(string="SAP Group Line Name")
    src_table_name=fields.Char(string="Source Table Name")
    dst_table_name=fields.Char(string="Destination Table Name")
    db_func_name_1=fields.Char(string="Database Func Name 1")
    db_func_name_2=fields.Char(string="Database Func Name 2")
    db_func_name_3=fields.Char(string="Database Func Name 3")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    miss_record_counts=fields.Integer(string="Miss Record Counts")
    last_id=fields.Integer("Last Process Id")
    update_miss_flag=fields.Selection([('Y','Y'),('N','N')],string="Need Update Miss Use db_func_name_3",default='N')
    sequence=fields.Integer("Sequence Of Group Line")

class interface_temp_table_group_exe(models.Model):
    """
        存储中间表分组执行情况
    """
    _order='id desc'
    _name = "iac.interface.temp.table.group.exe"
    _description = u"Interface Temp Table Group Execute"
    group_code=fields.Char(string="Group Code")
    group_name=fields.Char(string="Group Name")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    start_time=fields.Datetime(string="First Datetime Start")
    end_time=fields.Datetime(string="Last Finished Datetime")
    seq_id=fields.Integer(string="Seq Id")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail Has Some Errors")],string="Group Execute State")
    memo_str=fields.Text(string="Memo String")

    success_group_line_count=fields.Integer(string="Success Group Line Count")
    fail_group_line_count=fields.Integer(string="Fail Group Line Count")
    manual_call_id=fields.Many2one("iac.interface.temp.table.group.manual.call",string="Group Manual Call Info")
    #exe_line_ids=fields.One2many('iac.interface.temp.table.group.exe.line','group_exe_id',string="Group Execute Lines Info")
    exe_line_ids=fields.One2many('sp.job.time.log','group_exe_id',string="Group Execute Lines Info")
    sap_log_id=fields.Char(string="SAP Log Id")

    #数据转移,从中间表的正式表转移过程中的记录,插入记录数量,更新记录数量，失败的数量等
    insert_record_counts=fields.Integer(string="Insert Total  Record Counts")
    update_record_counts=fields.Integer(string="Update Total  Record Counts")
    fail_record_counts=fields.Integer(string="Fail Record Counts")
    miss_record_counts=fields.Integer(string="Miss Record Counts")


class interface_temp_table_group_exe_line(models.Model):
    """
        存储中间表分组条目执行情况
    """
    _name = "iac.interface.temp.table.group.exe.line"
    _description = u"Interface Temp Table Group Execute"
    group_code=fields.Char(string="Group Code")
    group_name=fields.Char(string="Group Name")
    group_line_code=fields.Char(string="Group Line Code")
    group_line_name=fields.Char(string="Group Line Name")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    group_line_id=fields.Many2one("iac.interface.temp.table.group.line",string="Temp Table Group Line Info")
    group_exe_id=fields.Many2one("iac.interface.temp.table.group.exe",string="Temp Table Group Execute Info")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Finished Datetime")
    store_proc_name=fields.Char(string="Database Store Proc Name")

    #数据转移,从中间表的正式表转移过程中的记录,插入记录数量,更新记录数量，失败的数量等
    insert_record_counts=fields.Integer(string="Insert Total  Record Counts")
    update_record_counts=fields.Integer(string="Update Total  Record Counts")
    fail_record_counts=fields.Integer(string="Fail Record Counts")
    miss_record_counts=fields.Integer(string="Miss Record Counts")


    seq_id=fields.Integer(string="Seq Id")
    memo_str=fields.Text(string="Memo String")
    state=fields.Selection([("success","Success"),("processing","Processing"),("fail","Fail Has Some Errors")],string="Group Execute State")

    manual_call_id=fields.Many2one("iac.interface.temp.table.group.manual.call",string="Group Manual Call Info")
    sap_log_id = fields.Char(string="Sap log Info")

    #废弃字段 时间都用start_time 和end_time
    last_id=fields.Integer("Last Process Id")
    insert_start_time=fields.Datetime(string="Insert Record Datetime Start")
    insert_end_time=fields.Datetime(string="Insert Record Finished Datetime")
    update_start_time=fields.Datetime(string="Update Record Ref Datetime Start")
    update_end_time=fields.Datetime(string="Update Record Ref Finished Datetime")
    total_record_counts=fields.Integer(string="Total Record Counts")
    insert_fail_record_counts=fields.Integer(string="Insert Fail Record Counts")
    update_ref_record_counts=fields.Integer(string="Update Ref Total Record Counts")
    update_ref_fail_record_counts=fields.Integer(string="Update Ref Fail Record Counts")


class interface_temp_table_group_exe_log(models.Model):
    """
        存储中间表分组条目执行异常情况
    """
    _name = "iac.interface.temp.table.group.exe.log"
    _description = u"Interface Temp Table Group Execute Exception Log"
    _order=" id desc"
    group_code=fields.Char(string="Group Code")
    group_name=fields.Char(string="Group Name")
    group_line_code=fields.Char(string="Group Line Code")
    group_line_name=fields.Char(string="Group Line Name")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    group_line_id=fields.Many2one("iac.interface.temp.table.group.line",string="Temp Table Group Line Info")
    group_exe_id=fields.Many2one("iac.interface.temp.table.group.exe",string="Temp Table Group Execute Info")
    group_exe_line_id=fields.Many2one("iac.interface.temp.table.group.exe.line",string="Temp Table Group Execute Info Line")
    start_time=fields.Datetime(string="Datetime Start")
    exception_str=fields.Text(string="Exception  String")
    table_name=fields.Char(string="Table Name")
    column_name=fields.Char(string="Column Name")
    message_text=fields.Text(string="Exception Message Main  String")
    exception_detail=fields.Text(string="Exception  Detail String")
    sap_log_id = fields.Char(string="Sap log Info")
    src_id = fields.Integer(string="Source Table Record ID")


class interface_temp_table_group_manual_call(models.Model):
    """
        存储中间表分组条目执行异常情况
    """
    _name = "iac.interface.temp.table.group.manual.call"
    _description = u"Interface Temp Table Group Manual Call"
    code=fields.Char(string="Manual Call Code")
    name=fields.Char(string="Manual Call Name")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    start_time=fields.Datetime(string="Datetime Start")
    end_time=fields.Datetime(string="Datetime Start")
    memo_str=fields.Text(string="Memo  String")
    exception_str=fields.Text(string="Exception  String")