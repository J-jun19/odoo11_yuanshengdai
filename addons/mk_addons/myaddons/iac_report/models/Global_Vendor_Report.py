# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, exceptions, _
from odoo.tools.translate import _
from odoo.http import request


class GlobalVendorReport(models.Model):
    _name = "v.global.vendor.report"
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
    vendor_state = fields.Char(string="vendor_status", readonly=True)
    create_date = fields.Datetime(string="create_date", readonly=True)
    use_project = fields.Char(string="use_project", readonly=True)
    incoterm = fields.Char(string="incoterm", readonly=True)
    destination = fields.Char(string="destination", readonly=True)
    reason = fields.Char(string="reason", readonly=True)
    vendor_type = fields.Char(string="vendor_type", readonly=True)
    plm_name = fields.Char(string="plm_name", readonly=True)
    current_class = fields.Char(string="current_class", readonly=True)
    registration_type = fields.Char(string="registration_type", readonly=True)
    address_country = fields.Char(string="address_country", readonly=True)
    buyer_email = fields.Char(string="buyer_email", readonly=True)
    vendor_property = fields.Char(string="vendor_property", readonly=True)
    site_survey = fields.Char(string='site_survey', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_global_vendor_report')
        self._cr.execute("""
            
CREATE OR REPLACE VIEW "public"."v_global_vendor_report" AS 
 SELECT row_number() OVER () AS id,
    t.gv_code,
    t.global_name1,
    t.global_name2,
    t.sc_code,
    t.sc_name,
    t.vendor_code,
    t.vendor_name,
    t.currency,
    t.plant,
    t.payment_term,
    t.vendor_state,
    t.create_date,
    t.use_project,
    t.incoterm,
    t.destination,
    t.reason,
    t.vendor_type,
    t.plm_name,
    t.current_class,
    t.registration_type,
    t.address_country,
    t.buyer_email,
    t.vendor_property,
    t.site_survey
   FROM ( SELECT DISTINCT gv.global_vendor_code AS gv_code,
            gv.name AS global_name1,
            gv.global_name2,
            sc.company_no AS sc_code,
            sc.name AS sc_name,
            v.vendor_code,
            v.name AS vendor_name,
            curr.name AS currency,
            porg.plant_code AS plant,
            pay.payment_term,
            v.state AS vendor_state,
            v.create_date,
            reg.use_project,
            inco.incoterm,
            v.destination,
            reg.apply_memo AS reason,
            reg.supplier_type AS vendor_type,
            plm.name AS plm_name,
            sc.current_class,
            v.vendor_type AS registration_type,
            country.code AS address_country,
            v.buyer_email,
            v.vendor_property,
            v.site_survey
           FROM ((((((((((iac_global_vendor gv
             JOIN iac_global_vendor_line gvl ON ((gvl.global_vendor_id = gv.id)))
             JOIN iac_supplier_company sc ON ((sc.id = gvl.supplier_company_id)))
             JOIN iac_vendor v ON ((v.supplier_company_id = sc.id)))
             LEFT JOIN pur_org_data porg ON ((porg.id = v.plant)))
             LEFT JOIN res_currency curr ON ((curr.id = v.currency)))
             LEFT JOIN payment_term pay ON ((pay.id = v.payment_term)))
             LEFT JOIN incoterm inco ON ((inco.id = v.incoterm)))
             LEFT JOIN iac_vendor_register reg ON ((reg.id = v.vendor_reg_id)))
             LEFT JOIN res_country country ON ((country.id = reg.address_country)))
             LEFT JOIN iac_vendor_plm plm ON ((plm.global_vendor_id = gv.id)))
          ORDER BY gv.global_vendor_code, sc.company_no, v.vendor_code) t;
                                    """)

class IacGlobalVendorReportWizard(models.TransientModel):
    _name = 'v.global.vendor.report.wizard'

#    plant_id = fields.Many2one('v.user.info', string="Plant")
    plant_id = fields.Many2one('pur.org.data', string="Plant",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    gv_code = fields.Char(string="Global Vendor Code")
    global_name1 = fields.Char(string="Global Vendor Name")
    vendor_name = fields.Char(string="Vendor Name")
    plm_name = fields.Char(string="PLM Name")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Code")
    current_class = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')],
        string="class")

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def search_global_vendor_report(self):
        self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        domain = []
        record_global_vendor = 0
        record_buyer = 0
        for item in self.env.user.groups_id:
            if item.name == 'Global Vendor Report':
                record_global_vendor = 1
                continue
            if item.name == 'Buyer' or item.name =='AS' or item.name =='CM':
                record_buyer = 1
                continue

        # print record_global_vendor,record_buyer
        for wizard in self:
            if record_global_vendor == 1 and record_buyer == 1 and not wizard.plant_id:
                raise exceptions.ValidationError("Plant为必填项!")
            if record_global_vendor==0 and record_buyer==1 and not wizard.gv_code and not wizard.plm_name and not wizard.vendor_id:
                raise exceptions.ValidationError("Global Vendor Code、PLM Name、Vendor Code不能同时为空!")
            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.gv_code:
                domain += [('gv_code', 'ilike', wizard.gv_code)]
            if wizard.global_name1:
                domain += [('global_name1', 'ilike', wizard.global_name1)]
            if wizard.vendor_name:
                domain += [('vendor_name', 'ilike', wizard.vendor_name)]
            if wizard.plm_name:
                domain += [('plm_name', 'ilike', wizard.plm_name)]
            if wizard.vendor_id:
                domain += [('vendor_code', '=', wizard.vendor_id.vendor_code)]
            if wizard.current_class:
                domain += [('current_class', '=', wizard.current_class)]

            result = self.env['v.global.vendor.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            #'domain': domain,
            'name': _('Global Vendor Report'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.global.vendor.report'
        }
        return action
