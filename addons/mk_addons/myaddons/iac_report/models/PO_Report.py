# -*- coding: utf-8 -*-

from odoo import api, fields, models,exceptions, tools
from odoo.tools.translate import _
from datetime import datetime, timedelta

class IacVendorRegisterPOReport(models.Model):

    _inherit = 'iac.vendor.register'
    _name = 'iac.vendor.register.po.report'
    _table = 'iac_vendor_register'

class IacPOReport(models.Model):
    _inherit = 'iac.purchase.order'
    _name = 'iac.po.report'
    _table = 'iac_purchase_order'

    # plant = fields.Char('pur.org.date', related='plant_id.plant_code', string='Plant', readonly=True)
    # vendor_code = fields.Char('iac.vendor', related='vendor_id.vendor_code', string='Vendor Code', readonly=True)
    plant = fields.Char(string='Plant', related='plant_id.plant_code', readonly=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register.po.report')
    # vendor_code = fields.Char(string='Vendor Code', related='vendor_id.vendor_code', readonly=True)


class IacPOReportWizard(models.TransientModel):
    _name = 'v.po.report.wizard'
    plant_id = fields.Many2one('pur.org.data', string="Plant *",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    vendor_id = fields.Many2one('iac.vendor', string="Vendor *")
    document_erp_id = fields.Char(string='PO')

    def _get_today(self):
        return(datetime.now().strftime('%Y-%m-%d'))

    def _get_days_ago(self):
        return(datetime.now() + timedelta(days=-365)).strftime('%Y-%m-%d')

    document_date_from = fields.Date(string='PO date from *', default=_get_days_ago)
    document_date_to = fields.Date(string='PO date to *', default=_get_today)

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_id': [('plant', '=', self.plant_id.id)]}}
        else:
            return {'domain': {'vendor_id': []}}

    @property
    def document_erp_code_list(self):
        for item in self.env.user.groups_id:
            if item.name == 'Buyer':
                document_erp_code_list = []
                for item in self.env['iac.purchase.order'].search([('buyer_id', 'in', self.env.user.buyer_id_list)]):
                    document_erp_code_list.append(item.document_erp_id)
                return document_erp_code_list

    @api.multi
    def search_iac_po_report(self):
        for item in self.env.user.groups_id:
            if item.name == 'External vendor':

                if not self.env.user.vendor_id:
                    raise exceptions.ValidationError("please go to workspace to set vendor code")
                else:
                    domain = [('state', 'in', ('wait_vendor_confirm', 'vendor_confirmed', 'vendor_exception'))]
                    break
            else:
                domain = []
        self.ensure_one()
        result = []
        for wizard in self:

            for item in self.env.user.groups_id:
                if item.name == 'Buyer':
                    domain += [('document_erp_id', 'in', self.document_erp_code_list)]
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.document_erp_id:
                domain += [('document_erp_id', '=', wizard.document_erp_id)]

            if wizard.document_date_from:
                domain += [('order_date', '>=', wizard.document_date_from)]
            if wizard.document_date_to:
                domain += [('order_date', '<=', wizard.document_date_to)]
            result = self.env['iac.po.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('IAC PO Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'iac.po.report'
        }
        return action
