# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.odoo_env import odoo_env
import xlrd


class MailAbnormalJob(models.Model):
    _name = 'mail.abnormal.job'

    @odoo_env
    @api.model
    def job_mail_abnormal_job(self):
        self._cr.execute("""select * from ep_temp_master.extractlog 
              where cast(extractdate as date) = cast(now() as date)
               and extractstatus not in ('STEP2DONE','CLEAN')
               and extractname not in ('POPartner')
               order by extractname, extractdate """)

        search_storage = self._cr.dictfetchall()
        body_lists = []
        email = 'Zhang.Pei-Wu@iac.com.tw' + ';' + 'Wang.Ningg@iac.com.tw' + ';' + 'Jiang.Shier@iac.com.tw' + ';' + 'Li.Zhen@iac.com.tw'
        if search_storage:

            for storage_obj in search_storage:
                # print storage_obj, str(storage_obj['extractcount'])
                vm_extract_lambda = lambda r: r if r not in (False, None) else ''
                lambda r: r if r not in (False, None) else ''
                body_list = [storage_obj['extractwmid'], storage_obj['extractname'], storage_obj['sourcetable'],
                             storage_obj['desttable'],
                             storage_obj['extractdate'], vm_extract_lambda(str(storage_obj['extractcount'])),
                             storage_obj['extractstatus'], vm_extract_lambda(storage_obj['extractenddate'])]
                body_lists.append(body_list)
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', '今日job失败情况，请抓紧排查', [
                'extractwmid', 'extractname', 'sourcetable', 'desttable', 'extractdate', 'extractcount',
                'extractstatus', 'extractenddate'], body_lists, 'ABNORMAL_JOB')
        else:

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', '今日job正常跑完', [
                'extractwmid', 'extractname', 'sourcetable', 'desttable', 'extractdate', 'extractcount',
                'extractstatus', 'extractenddate'],
                                                      body_lists, 'ABNORMAL_JOB')
