# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacBulletinInfomationReport(models.Model):
    _name = 'iac.bulletin.publish.report'
    _inherit = ['iac.bulletin.publish']
    _table = 'iac_bulletin_publish'


class IacBulletinInformationReportWizard(models.TransientModel):
    _name = 'v.bulletin.information.report.wizard'
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    subject = fields.Char('Subject')
    start_date = fields.Date(string='Start Date *', required=True)
    end_date = fields.Date(string='End Date *', required=True)

    @api.multi
    def search_bulletin_history(self):
        self.ensure_one()  # 检验某数据集是否只包含单条数据，如果不是则报错

        domain = []
        result = []

        for wizard in self:
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]

            if not wizard.start_date:
                domain += [('start_date', '>=', '2010-01-01')]
            else:
                domain += [('start_date', '>=', wizard.start_date)]

            if not wizard.end_date:
                domain += [('end_date', '<=', '2099-12-31')]
            else:
                domain += [('end_date', '<=', wizard.end_date)]

            if wizard.subject:
                domain += [('subject', 'ilike', wizard.subject)]

        result = self.env['iac.bulletin.publish.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('IAC bulletin publish history report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'iac.bulletin.publish.report'
        }
        return action
