# -*- coding: utf-8 -*-

from odoo import fields,models

class SpJobTimeLog(models.Model):

    _name = 'sp.job.time.log'

    group_name = fields.Char("Group Name")
    group_line_name = fields.Char("Group Line Name")
    extractwmid = fields.Char("Extract Log Id")
    sp_name = fields.Char("Sp Function Name")
    start_time = fields.Datetime("Sp Function Start Time")
    end_time = fields.Datetime("Sp Function End Time")
    paramater_str = fields.Char()  #把传入sp的参数拼接起来，中间用，分隔

    sap_log_id=fields.Char(string="SAP Log Id")
    sp_func_text=fields.Text(string="Sp Func Text")
    group_exe_id=fields.Many2one("iac.interface.temp.table.group.exe",string="Temp Table Group Execute Info")
    group_id=fields.Many2one("iac.interface.temp.table.group",string="Temp Table Group Info")
    group_line_id=fields.Many2one("iac.interface.temp.table.group.line",string="Temp Table Group Line Info")
    start_id=fields.Integer("Start Process Id")
    last_id=fields.Integer("Last Process Id")
    log_memo=fields.Text("Process Memo")
    update_record_counts=fields.Integer(string="Update Total  Record Counts")
    fail_record_counts=fields.Integer(string="Fail Record Counts")
    miss_record_counts=fields.Integer(string="Miss Record Counts")
    state=fields.Selection([("draft","Draft"),("success","Success"),("processing","Processing"),("fail","Fail Has Some Errors")],string="Group Execute State")