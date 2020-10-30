# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from datetime import datetime, timedelta


# class AsnListReportForSubcontractor(models.Model):
#     _name = "v.asn.list.report.for.subcontractor"
#     # _auto = False
#     #_order = 'vendor_code'
#
#     asn_no = fields.Char()
#     now_date = fields.Char('Create Date')
#     storage_location = fields.Char()
#     asn_line_no = fields.Char()
#     po_code = fields.Char()
#     po_line_code = fields.Char()
#     # vendor_code_sap = fields.Char()
#     plant_code = fields.Char()
#     buyer_erp_id = fields.Char()
#     asn_qty = fields.Float()
#     part_no = fields.Char()
#     gr_qty = fields.Float()
#     # in_transit_flag = fields.Char()
#     in_transit_qty = fields.Float()
#     vendor_code = fields.Char()
# line_ids = fields.One2many('v.asn.list.line', 'line_id')


# class AsnListLine(models.Model):
#     _name = "v.asn.list.line"
#
#
#     line_id = fields.Many2one('v.asn.list.report')
#     po_code = fields.Char()
#     part_no = fields.Char()
#     asn_qty = fields.Float()


class IacASNReportForSubcontractorWizard(models.TransientModel):
    _name = 'v.asn.report.for.subcontractor.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)], index=True)
    storage_location = fields.Many2one('iac.storage.location.address', string="Location",
                                       domain=lambda self: [('plant', '=', self.plant_id.plant_code)], index=True)
    part = fields.Char('Part No')
    asn = fields.Char('ASN No')
    asn_date_from = fields.Date('ASN Date From *')
    asn_date_to = fields.Date('ASN Date To *')
    open_asn_only = fields.Boolean('Open ASN Only')

    # @api.onchange('plant_id')
    # def _onchange_location(self):
    #     location = self.env["iac.storage.location.address"].search(
    #         [('plant', '=', self.plant_id.plant_code)])
    #     self.storage_location = location.id
    #
    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):
        # print self.env.user.partner_id.storage_location_ids
        list = []
        for location in self.env.user.partner_id.storage_location_ids:
            list.append(location.storage_location_id.id)
        if self.plant_id:
            return {'domain': {'storage_location': [('plant', '=', self.plant_id.plant_code),
                                                    ('id', 'in', list)]}}

    @api.multi
    def search_asn_report_for_subcontractor(self):
        self.ensure_one()
        # result = []
        lt_plant_code = ""
        lt_storage_location = ""
        lt_part = ""
        lt_asn = ""
        lt_open_asn = False
        lt_login = ""

        domain = []
        for wizard in self:

            if wizard.plant_id:
                lt_plant_code = wizard.plant_id.plant_code
            if wizard.storage_location:
                lt_storage_location = wizard.storage_location.storage_location
            if wizard.part:
                lt_part = wizard.part
            if wizard.asn:
                lt_asn = wizard.asn
            if wizard.open_asn_only:
                lt_open_asn = True
            real_end_date = (datetime.strptime(wizard.asn_date_to, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        self.env.cr.execute('select v_id from public.proc_asn_report_for_subcontractor'
                            ' (%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                            (lt_part, lt_asn,
                             wizard.asn_date_from, real_end_date, lt_open_asn, lt_storage_location, lt_plant_code,
                             lt_login))

        result_asn_report = self.env.cr.fetchall()
        result_ids = []
        for result_asn_report_item in result_asn_report:
            result_ids.append(result_asn_report_item)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('ASN Report For subcontractor'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.asn.list.report'
        }
        return action
