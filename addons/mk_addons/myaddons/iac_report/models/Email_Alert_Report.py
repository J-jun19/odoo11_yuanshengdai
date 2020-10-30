# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from datetime import datetime, timedelta

class IacEmailAlertReport(models.Model):
    _name = 'v.email.alert.report'
    _inherit = 'mail.mail'
    _table = 'mail_mail'

    ms_subject = fields.Char(string='Mail subject', related='mail_message_id.subject')
    ms_body = fields.Html(string='Mail body', related='mail_message_id.body')
    ms_email_from = fields.Char(string='Email from', related='mail_message_id.email_from')
    ms_record_name = fields.Char(string='Reference name', related='mail_message_id.record_name')


class IacEmailAlertReportWizard(models.TransientModel):
    _name = 'v.email.alert.report.wizard'

    def _get_today(self):
        return(datetime.now().strftime('%Y-%m-%d'))

    def _get_30days_ago(self):
        return(datetime.now() + timedelta(days=-30)).strftime('%Y-%m-%d')

    subject = fields.Char(string='Mail Subject')
    mail_to = fields.Char(string='Mail To')
    from_date = fields.Date(string='Mail Date From *', required='1', default=_get_30days_ago)
    to_date = fields.Date(string='Mail Date To *', required='1', default=_get_today)
    # from_date = fields.Datetime(string='Mail date from', required='1')
    # to_date = fields.Datetime(string='Mail date to', required='1')

    @api.multi
    def search_mail_alert_report(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.subject:
                domain += [('ms_subject', '=', wizard.subject)]
            if wizard.mail_to:
                domain += [('|', ('email_to' 'ilike', wizard.mail_to), ('email_cc' 'ilike', wizard.mail_to))]
            if wizard.from_date:
                domain += [('create_date', '>=', wizard.from_date)]
            if wizard.to_date:
                domain += [('create_date', '<=', wizard.to_date)]

            result = self.env['v.email.alert.report'].search(domain)
        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Mail alert report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.email.alert.report'
        }
        return action
