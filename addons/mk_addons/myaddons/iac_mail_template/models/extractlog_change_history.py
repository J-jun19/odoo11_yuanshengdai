# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
import datetime
from odoo.odoo_env import odoo_env


class ExtractlogChangeHistory(models.Model):

    _name = 'extractlog.change.history'

    extractwmid = fields.Char()
    extractname = fields.Char()
    sourcetable = fields.Char()
    desttable = fields.Char()
    extractdate = fields.Char()
    extractcount = fields.Char()
    extractstatus = fields.Char()
    extractenddate = fields.Char()
    update_on = fields.Char()


    @odoo_env
    @api.model
    def change_extractlog(self):
        self._cr.execute("  select distinct(extractgroup)  from ep_temp_master.extractgroup ")
        for group in self.env.cr.dictfetchall():
            # print group['extractgroup']
            extractgroup = group['extractgroup']
            self._cr.execute("select extractdate from ep_temp_master.extractlog" 
     " where extractname in ( select extractname from ep_temp_master.extractgroup where extractgroup = %s )" 
       "  order by extractdate desc limit 1",(extractgroup,))
            for date in self.env.cr.dictfetchall():
                # print date['extractdate']
                extractdate = date['extractdate']
                self._cr.execute("select * from ep_temp_master.extractlog"
                                 " where extractname in ( select extractname from ep_temp_master.extractgroup where extractgroup = %s )"
                                 "  and extractdate=%s and (extractstatus='PROCESS' or extractstatus='ODOO_PROCESS')",(extractgroup,extractdate))
                for name in self.env.cr.dictfetchall():
                    extractname = name['extractname']
                    self._cr.execute("  select intervaltime  from ep_temp_master.extractgroup where extractname=%s and extractgroup=%s",(extractname,extractgroup))
                    for item in self.env.cr.dictfetchall():
                        intervaltime = int(item['intervaltime'])
                        if (datetime.datetime.now()-datetime.timedelta(minutes=intervaltime)).strftime('%Y-%m-%d %H:%M:%S') > extractdate:
                            self._cr.execute("select * from ep_temp_master.extractlog"
                                             " where extractname =%s"
                                             "  and extractdate=%s",
                                             (extractname, extractdate))
                            for info in self.env.cr.dictfetchall():
                                vals = {
                                    'extractwmid':info['extractwmid'],
                                    'extractname':info['extractname'],
                                    'sourcetable':info['sourcetable'],
                                    'desttable':info['desttable'],
                                    'extractdate':info['extractdate'],
                                    'extractcount':info['extractcount'],
                                    'extractstatus':info['extractstatus'],
                                    'extractenddate':info['extractenddate'],
                                    'update_on':datetime.datetime.now()
                                }
                                self.env['extractlog.change.history'].create(vals)
                                self.env.cr.commit()
                                self._cr.execute("delete from  extractlog_change_history where extractwmid is null")
                                self.env.cr.commit()
                                self._cr.execute("update ep_temp_master.extractlog set extractstatus=%s where extractwmid=%s",('CLEAN',info['extractwmid']))
                                self.env.cr.commit()

