# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import datetime, timedelta
from odoo.tools.translate import _


class RFQUploadListMMReport(models.Model):
    _name = "v.iac.rfq.import.mm.report"
    _description = "RFQ Upload List MM"
    _auto = False
    #    _order = ' '

    state_as = fields.Char(string="state_as", readonly=True)
    part_no = fields.Char(string="part_no", readonly=True)
    vendor_code = fields.Char(string="vendor_code", readonly=True)
    upload_date = fields.Date(string="upload_date", readonly=True)
    valid_from = fields.Date(string="valid_from", readonly=True)
    valid_to = fields.Char(string="valid_to", readonly=True)
    input_price = fields.Float(string="input_price", digits=(18, 6), readonly=True)
    currency = fields.Char(string="currency", readonly=True)
    buyer_erp_id = fields.Char(string="buyer_erp_id", readonly=True)
    buyer_name = fields.Char(string="buyer_name", readonly=True)
    price_control = fields.Char(string="price_control", readonly=True)
    memo = fields.Char(string="memo", readonly=True)
    vendor_part_no = fields.Char(string="vendor_part_no", readonly=True)
    login_as = fields.Char(string="login_as", readonly=True)
    name_as = fields.Char(string="name_as", readonly=True)
    state_mm = fields.Char(string="state_mm", readonly=True)
    lt = fields.Integer(string="lt", readonly=True)
    moq = fields.Float(string="moq", digits=(18, 6), readonly=True)
    mpq = fields.Float(string="mpq", digits=(18, 6), readonly=True)
    rw = fields.Char(string="rw", readonly=True)
    cw = fields.Char(string="cw", readonly=True)
    tax = fields.Char(string="tax", readonly=True)
    login_mm = fields.Char(string="login_mm", readonly=True)
    name_mm = fields.Char(string="name_mm", readonly=True)
    mm_update_date = fields.Date(string="mm_update_date", readonly=True)
    rfq_no = fields.Char(string="rfq_no", readonly=True)
    state_rfq = fields.Char(string="state_rfq", readonly=True)
    webflow_number = fields.Char(string="webflow_number", readonly=True)
    rfq_update_time = fields.Char(string="rfq_update_time", readonly=True)
    plant = fields.Char(string="plant", readonly=True)
    as_upload_id = fields.Integer(string="as_upload_id", readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        result=super(RFQUploadListMMReport,self).search(args, offset, 100000, order, count)
        result_count=0
        if count==False:
            result_count=len(result.ids)
        return result


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_iac_rfq_import_as_report')
        self._cr.execute("""
        CREATE OR REPLACE VIEW public.v_iac_rfq_import_as_report AS (
            SELECT ras.id,
                  CASE
                 WHEN r.state IS NULL THEN ras.state
                  ELSE r.state
                  END AS state_as,
                    mm.part_no,
                    v.vendor_code,
                    cast(ras.create_date as date) AS upload_date,
                    ras.valid_from,
                    ras.valid_to,
                    ras.input_price,
                    rc.name AS currency,
                    bc.buyer_erp_id,
                    bc.buyer_name,
                    ras.price_control,
                    ras.note AS memo,
                    ras.vendor_part_no,
                    ru_as.login AS login_as,
                    rp_as.name AS name_as,
                    rmm.state AS state_mm,
                    rmm.lt,
                    rmm.moq,
                    rmm.mpq,
                    rmm.rw,
                    rmm.cw,
                    rmm.tax,
                    ru_mm.login AS login_mm,
                    rp_mm.name AS name_mm,
                    rmm.create_date AS mm_update_date,
                    r.name AS rfq_no,
                    r.state AS state_rfq,
                    r.webflow_number as webflow_number,
                    r.write_date AS rfq_update_time,
                    mm.plant_code as plant
                   FROM v_iac_rfq_import_as ras
                     JOIN material_master mm ON mm.id = ras.part_id
                     JOIN iac_vendor v ON v.id = ras.vendor_id
                     JOIN buyer_code bc ON bc.id = ras.buyer_code
                     JOIN res_currency rc ON rc.id = ras.currency_id
                     JOIN res_users ru_as ON ru_as.id = ras.create_uid
                     JOIN res_partner rp_as ON rp_as.id = ru_as.partner_id
                     LEFT JOIN v_iac_rfq_import_mm rmm ON rmm.as_upload_id = ras.id
                     LEFT JOIN iac_rfq r ON r.id = rmm.rfq_id
                     LEFT JOIN res_users ru_mm ON ru_mm.id = rmm.create_uid
                     LEFT JOIN res_partner rp_mm ON rp_mm.id = ru_mm.partner_id)

                                       """)

class rfq_import_mm_report(models.TransientModel):
    _name = 'v.iac.rfq.import.mm.report.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant", domain=lambda self: [('id', 'in', self.env.user.plant_id_list)])
    vendor_code = fields.Char(string="Vendor Code")
    part_no = fields.Char(string="Part No")
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True, invisible="1")
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    upload_date = fields.Date(string="AS Upload Date")

    @property
    def buyer_code_list(self):
        for item in self.env.user.groups_id:
            if item.name == 'Buyer':
                buyer_code_list = []
                for item in self.env['buyer.code'].search(
                        [('id', 'in', self.env.user.buyer_id_list)]):
                    buyer_code_list.append(item.buyer_erp_id)
                return buyer_code_list


    @api.multi
    def search_rfq_import_mm_report(self):
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.part_no:
                domain += [('part_no', 'ilike', wizard.part_no)]
            for item in self.env.user.groups_id:
                if item.name == 'Buyer':
                    domain += [('buyer_erp_id', 'in', self.buyer_code_list)]
            if wizard.valid_from:
                domain += [('valid_from', '>=', wizard.valid_from)]
            if wizard.valid_to:
                domain += [('valid_to', '<=', wizard.valid_to)]
            if wizard.vendor_code:
                domain += [('vendor_code', '=', wizard.vendor_code.zfill(10).strip())]
            if wizard.upload_date:
                domain += [('upload_date', '=', wizard.upload_date)]

            result = self.env['v.iac.rfq.import.as.report'].search(domain)

            print '*71:', domain

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Info Record Upload List MM'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.iac.rfq.import.as.report'
        }
        return action
