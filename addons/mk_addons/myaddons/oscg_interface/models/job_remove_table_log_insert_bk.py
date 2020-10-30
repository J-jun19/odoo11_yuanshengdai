# -*- coding: utf-8 -*-

from odoo import models,api,fields
from odoo.odoo_env import odoo_env
from datetime import datetime,timedelta


class IacJobRemoveOldDataToBk(models.Model):
    _name = "iac.job.remove.old.data.to.bk"
    _auto = False

    @odoo_env
    @api.model
    def job_remove_old_data_to_bk(self):
        self._cr.execute(""" select * from iac_interface_log_line where create_date<CURRENT_DATE-15 ORDER BY id DESC """)
        res = self._cr.fetchall()
        if res:
            self.env['iac.job.remove.log.insert.bk'].storage_old_interface_log_data(res)
        # print 1
        self._cr.execute(""" select * from iac_interface_timer_line where create_date<CURRENT_DATE-15 ORDER BY id DESC """)
        res_timer = self._cr.fetchall()
        if res_timer:
            self.env['iac.job.remove.timer.data.insert.bk'].storage_old_interface_timer_data(res_timer)

        # ning 191029 调整 删除15天前iac_job_func_call_log表的资料
        self._cr.execute("""delete from iac_job_func_call_log where cdt <= %s""",
                         ((datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),))
        # ning 200327 add 删除15天前sp_job_time_log表的资料
        self._cr.execute("""delete from sp_job_time_log where create_date <= %s""",
                         ((datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),))


class IacJobRemoveLogInsertBk(models.Model):
    _name = "iac.job.remove.log.insert.bk"
    _inherit = "iac.interface.log.line"
    _order = 'id desc'

    create_date_copy = fields.Datetime()
    write_date_copy = fields.Datetime()

    @api.model
    def storage_old_interface_log_data(self,res):
        for res_one in res:
            vals = {
                    'create_date_copy': res_one[1],
                    'manual_user_id': res_one[2],
                    'write_uid': res_one[3],
                    'json_builder_exception_str': res_one[4],
                    'eform_no': res_one[5],
                    'manual_call_id': res_one[6],
                    'create_uid': res_one[7],
                    'biz_object_id': res_one[8],
                    'job_id': res_one[9],
                    'seq_id': res_one[10],
                    'memo_str': res_one[11],
                    'interface_id': res_one[12],
                    'state': res_one[13],
                    'pair_id': res_one[14],
                    'call_param_str': res_one[15],
                    'start_time': res_one[16],
                    'manual_proc_id': res_one[17],
                    'call_json_msg': res_one[18],
                    'interface_code': res_one[19],
                    'write_date_copy': res_one[20],
                    'call_type': res_one[21],
                    'interface_name': res_one[22],
                    'log_id': res_one[23],
                    'manual_proc_seq_id': res_one[24],
                    'callback_json_msg': res_one[25],
                    'end_time': res_one[26],
                    'fail_msg': res_one[27],
                    }
            try:
                self.env['iac.job.remove.log.insert.bk'].create(vals)
                self.env['iac.interface.log.line'].browse(res_one[0]).unlink()
                # self.env.cr.commit()
            except:
                self.env.cr.rollback()
        return


class IacJobRemoveTimerDataInsertBk(models.Model):
    _name = "iac.job.remove.timer.data.insert.bk"
    _inherit = "iac.interface.timer.line"
    _order = 'id desc'

    create_date_copy = fields.Datetime()
    write_date_copy = fields.Datetime()

    @api.model
    def storage_old_interface_timer_data(self,res_timer):
        for res_line in res_timer:
            # vals = {
            #         'create_uid': res_line[1],
            #         'job_err_msg': res_line[2],
            #         'job_id': res_line[3],
            #         'job_name': res_line[4],
            #         'write_uid': res_line[5],
            #         'create_date': res_line[6],
            #         'write_date': res_line[7],
            #         'executed_time': res_line[8],
            #         'state': res_line[9],
            #         }
            vals = {
                    'create_uid': res_line[1],
                    'job_err_msg': res_line[2],
                    'job_id': res_line[3],
                    'job_name': res_line[4],
                    'write_uid': res_line[5],
                    'state': res_line[6],
                    'write_date_copy': res_line[7],
                    'executed_time': res_line[8],
                    'create_date_copy': res_line[9],
                    }
            try:
                self.env['iac.job.remove.timer.data.insert.bk'].create(vals)
                self.env['iac.interface.timer.line'].browse(res_line[0]).unlink()
                # self.env.cr.commit()
            except:
                self.env.cr.rollback()
        return