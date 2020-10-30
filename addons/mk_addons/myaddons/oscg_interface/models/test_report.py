# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json

class MineTestReport(models.TransientModel):
    _name = "mine.test.report"
    _description = u"Mine Test Report"
    _inherit="mine.report.job"
    _report_code="1000"
    interface_cfg_id=fields.Many2one('iac.interface.cfg',string="Interface Config")
    interface_timer_cfg_id=fields.Many2one('iac.interface.timer',string="Interface Timer Config")
    start_time=fields.Datetime(string="Start Date Time")
    end_time=fields.Datetime(string="Start Date Time")

    @api.model
    def default_get(self, fields):
        fields_value=super(MineTestReport,self).default_get(fields)
        fields_value["report_code"]=self._report_code
        return fields_value;