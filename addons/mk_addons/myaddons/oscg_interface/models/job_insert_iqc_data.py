# -*- coding: utf-8 -*-

from odoo import fields,models
from odoo.odoo_env import odoo_env
from odoo.exceptions import UserError
import traceback

class IacJobInsertIQCData(models.Model):
    _name = 'iac.job.insert.iqc.data'
    _auto = False

    @odoo_env
    def job_insert_iqc_data(self):
        self.env.cr.execute("""
                SELECT extractwmid,extractstatus FROM ep_temp_master.extractlog where 
                extractname=%s ORDER BY extractdate desc LIMIT 1;
                """,('VS_WEBFLOW_IQC_DATA',))
        result = self.env.cr.dictfetchone()
        if result['extractstatus'] == 'STEP1DONE':
            self.env.cr.execute("""
                        update ep_temp_master.extractlog set extractstatus=%s
                        where extractwmid=%s;
                        """,('ODOO_PROCESS',result['extractwmid']))
            self.env.cr.commit()
            try:
                self.env.cr.execute("""select * from 
                            ep_temp_master.sp_job_iqcdata_vs_webflow_iqc_data_insert()
                            """)
            except:
                self.env.cr.rollback()
                raise UserError(traceback.format_exc())
            self.env.cr.execute("""
                                    update ep_temp_master.extractlog set extractstatus=%s
                                    where extractwmid=%s;
                                    """, ('STEP2DONE', result['extractwmid']))
            self.env.cr.commit()
