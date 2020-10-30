# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class GlobalVendorQMReport(models.Model):
    _name = "v.global.vendor.qm.report"
    _description = "Global Vendor"
    _auto = False
    #    _order = 'gv_code'

    plant = fields.Char(string="plant", readonly=True)
    gv_code = fields.Char(string="gv_code", readonly=True)
    global_name1 = fields.Char(string="global_name1", readonly=True)
    vendor_name = fields.Char(string="vendor_name", readonly=True)
    plm_name = fields.Char(string="plm_name", readonly=True)
    vendor_code = fields.Char(string="vendor_code", readonly=True)
    global_name2 = fields.Char(string="global_name2", readonly=True)
    sc_code = fields.Char(string="sc_code", readonly=True)
    sc_name = fields.Char(string="sc_name", readonly=True)
    vendor_name = fields.Char(string="vendor_name", readonly=True)
    currency = fields.Char(string="currency", readonly=True)
    plant = fields.Char(string="plant", readonly=True)
    payment_term = fields.Char(string="payment_term", readonly=True)
    vendor_sap_status = fields.Char(string="vendor_sap_status", readonly=True)
    create_date = fields.Char(string="create_date", readonly=True)
    use_project = fields.Char(string="use_project", readonly=True)
    incoterm = fields.Char(string="incoterm", readonly=True)
    destination = fields.Char(string="destination", readonly=True)
    reason = fields.Char(string="reason", readonly=True)
    vendor_type = fields.Char(string="vendor_type", readonly=True)
    plm_name = fields.Char(string="plm_name", readonly=True)
    current_class = fields.Char(string="current_class", readonly=True)
    registration_type = fields.Char(string="registration_type", readonly=True)
    address_country = fields.Char(string="address_country", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_global_vendor_qm_report')
        self._cr.execute("""
            create or replace view v_global_vendor_qm_report as (
                SELECT v.id,
                    gv.global_vendor_code AS gv_code,
                    gv.name AS global_name1,
                    gv.global_name2,
                    sc.company_no AS sc_code,
                    sc.name AS sc_name,
                    v.vendor_code,
                    v.name AS vendor_name,
                    curr.name AS currency,
                    porg.plant_code AS plant,
                    pay.payment_term,
                    v.vendor_sap_status,
                    v.create_date,
                    reg.use_project,
                    inco.incoterm,
                    v.destination,
                    reg.apply_memo AS reason,
                    reg.supplier_type AS vendor_type,
                    plm.name AS plm_name,
                    sc.current_class,
                    v.vendor_type AS registration_type,
                    country.code AS address_country
                   FROM iac_global_vendor gv
                     join iac_global_vendor_line gvl on gvl.global_vendor_id = gv.id
                     JOIN iac_supplier_company sc ON sc.id = gvl.supplier_company_id
                     JOIN iac_vendor v ON v.supplier_company_id = sc.id
                     JOIN pur_org_data porg ON porg.id = v.plant
                     JOIN res_currency curr ON curr.id = v.currency
                     JOIN payment_term pay ON pay.id = v.payment_term
                     JOIN incoterm inco ON inco.id = v.incoterm
                     JOIN iac_vendor_register reg ON reg.id = v.vendor_reg_id
                     JOIN res_country country ON country.id = reg.address_country
                     LEFT JOIN iac_vendor_plm plm ON plm.global_vendor_id = gv.id)
                                    """)

class IacGlobalVendorReportWizard(models.TransientModel):
    _name = 'v.global.vendor.qm.report.wizard'

#    plant_id = fields.Many2one('v.user.info', string="Plant")
    plant_id = fields.Many2one('pur.org.data', string="Plant *",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    gv_id = fields.Many2one('iac.global.vendor', string="Global Vendor Code")
    global_name1 = fields.Char(string="Global Vendor Name")
    vendor_name = fields.Char(string="Vendor Name")
    plm_name = fields.Char(string="PLM Name")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Code")

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def search_global_vendor_report_qm(self):
        self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.gv_id:
                domain += [('gv_code', '=', wizard.gv_id.global_vendor_code)]
            if wizard.global_name1:
                domain += [('global_name1', 'ilike', wizard.global_name1)]
            if wizard.vendor_name:
                domain += [('vendor_name', 'ilike', wizard.vendor_name)]
            if wizard.plm_name:
                domain += [('plm_name', 'ilike', wizard.plm_name)]
            if wizard.vendor_id:
                domain += [('vendor_code', '=', wizard.vendor_id.vendor_code)]
            domain += [('reason', '=', '客人指定')]
        result = self.env['v.global.vendor.qm.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            #'domain': domain,
            'name': _('Global Vendor Report - QM'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.global.vendor.qm.report'
        }
        return action
