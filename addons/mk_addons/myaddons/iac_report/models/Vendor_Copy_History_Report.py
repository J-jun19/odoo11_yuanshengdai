# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class VendorCopyHistoryReport(models.Model):
    _name = "v.vendor.copy.history.report"
    _description = "Vendor Copy History Report"
    _auto = False

    ori_plant = fields.Char('Ori Plant')
    ori_vendor = fields.Char('Ori Vendor')
    ori_name = fields.Char('Ori Name')
    ori_payment = fields.Char('Ori Payment')
    ori_incoterm = fields.Char('Ori Incoterm')
    ori_destination = fields.Char('Ori Destination')
    ori_country = fields.Char('Ori Country')
    new_plant = fields.Char('New Plant')
    new_vendor = fields.Char('New Vendor')
    new_name = fields.Char('New Name')
    new_payment = fields.Char('New Payment')
    new_incoterm = fields.Char('New Incoterm')
    new_destination = fields.Char('New Destination')
    new_country = fields.Char('New Country')
    copy_reason = fields.Char('Copy Reason')
    create_date = fields.Datetime('Create Date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_copy_history_report')
        self._cr.execute("""
        CREATE OR REPLACE VIEW public.v_vendor_copy_history_report AS
        select vc.id,
               pod.plant_code as ori_plant,
               v.vendor_code as ori_vendor,
               v."name" as ori_name,     
               pt.payment_term as ori_payment,
               ic.incoterm as ori_incoterm,
               v.destination as ori_destination,
               rc.code as ori_country,
               pod1.plant_code as new_plant,
               v1.vendor_code as new_vendor,
               v1."name" as new_name,
               pt1.payment_term as new_payment,
               ic1.incoterm as new_incoterm,
               v1.destination as new_destination,
               rc1.code as new_country,
               vc.copy_reason,
               vc.create_date
               from iac_vendor_copy vc
         inner join iac_vendor v on v.id = vc.ori_vendor_id
         inner join iac_Vendor v1 on v1.id = vc.new_vendor_id
         inner join pur_org_data pod on pod.id = v.plant
         inner join pur_org_data pod1 on pod1.id = v1.plant
         inner join iac_vendor_register vr on vr.id = v.vendor_reg_id
         inner join iac_vendor_register vr1 on vr1.id = v1.vendor_reg_id
         inner join payment_term pt on pt.id = v.payment_term
         inner join payment_term pt1 on pt1.id = v1.payment_term
         inner join incoterm ic on ic.id = v.incoterm
         inner join incoterm ic1 on ic1.id = v1.incoterm
         inner join res_country rc on rc.id = vr.address_country
         inner join res_country rc1 on rc1.id = vr1.address_country
                    order by vc.id desc""")


class VendorCopyHistoryReportWizard(models.TransientModel):
    _name = 'vendor.copy.history.report.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Ori Plant",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)], index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Ori Vendor")
    # vendor_name = fields.Many2one('iac.vendor', string="Ori Name")
    starttime = fields.Date(string="Create Date From")
    endtime = fields.Date(string="Create Date To")

    @api.multi
    def search_vendor_copy_history_report(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain += [('ori_plant', '=', wizard.plant_id.plant_code)]
            if wizard.vendor_id:
                domain += [('ori_vendor', '=', wizard.vendor_id.vendor_code)]
            # if wizard.vendor_name:
            # domain += [('ori_name', 'ilike', wizard.vendor_name)]
            if wizard.starttime:
                domain += [('create_date', '>=', wizard.starttime)]
            if wizard.endtime:
                domain += [('create_date', '<=', wizard.endtime)]

            result = self.env['v.vendor.copy.history.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor Copy History Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.vendor.copy.history.report'
        }
        return action
