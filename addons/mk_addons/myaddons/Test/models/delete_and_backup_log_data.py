# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.odoo_env import odoo_env
import datetime
import traceback
import logging


class DeleteAndBackupLogData(models.Model):
    _name = 'iac.log.clean.control'

    job_name = fields.Char()
    job_logic = fields.Char()
    active = fields.Boolean()
    last_exec_begin_dt = fields.Datetime()
    last_exec_end_dt = fields.Datetime()

    @odoo_env
    @api.model
    def job_delete_and_backup(self):
        job1 = self.env['iac.log.clean.control'].search(
            [('job_name', '=', 'delete_ir_attachment'), ('active', '=', True)])
        job1.write({'last_exec_begin_dt': datetime.datetime.now()})
        self._cr.execute("""delete from ir_attachment
                            where res_model in('asn.jitrule','asn.maxqty','iac.asn.jitrule','iac.control.table','iac.rfq.import.as','iac.rfq.import.mm','iac.rfq.import.quote')
                            or res_model is null and "name" in ('vendor_psi_report','rfq_line_mm_downloads','buyer_fsct_report_downloads','buyer_fcst_delivery_report','vendor forecast delivery report')
                            and cast(create_date as date ) < (current_date - 30)""")
        job1.write({'last_exec_end_dt': datetime.datetime.now()})

# self.pool.get('other.object').job_remove_old_data_to_bk()
