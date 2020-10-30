# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class VendorWithoutGvcodeReport(models.Model):
    _name = "v.vendor.without.gv.code"
    _description = "vendor without gv_code"
    _auto = False
    #    _order = 'gv_code'

    vendor_code = fields.Char(string="vendor_code", readonly=True)
    name1_cn = fields.Char(string="name1_cn", readonly=True)
    short_name = fields.Char(string="short_name", readonly=True)
    vendor_type = fields.Char(string="vendor_type", readonly=True)
    supplier_type = fields.Char(string="supplier_type", readonly=True)
    buyer_email = fields.Char(string="buyer_email", readonly=True)
    create_date = fields.Datetime(string="create_date", readonly=True)
    supplier_category = fields.Char(string="supplier_category", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_without_gv_code')
        self._cr.execute("""

            CREATE OR REPLACE VIEW public.v_vendor_without_gv_code AS
             select row_number() OVER () AS id,
             v.vendor_code,
             v.buyer_email,
             sr.name1_cn,
             sr.short_name, 
             v.vendor_type,
             sr.supplier_type,
             sr.create_date,
             sr.supplier_category
        from iac_vendor v 
          inner join iac_vendor_register sr on sr.id = v.vendor_reg_id
        where not exists (select 1 from iac_supplier_company_line scl where scl.vendor_id = v.id)
          and sr.state = 'done'
          and vendor_type = 'normal'
        order by v.create_date desc;
                                       """)


class VendorWithoutGvcodeReportWizard(models.TransientModel):
    _name = 'v.vendor.without.gv.code.wizard'

    vendor_code = fields.Char(string="Vendor code")
    name1_cn = fields.Char(string="Vendor Name")
    short_name = fields.Char(string="Short Name")

    @api.multi
    def search_vendor_without_gv_code_report(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.vendor_code:
                domain += [('vendor_code', 'ilike', wizard.vendor_code)]
            if wizard.name1_cn:
                domain += [('name1_cn', 'ilike', wizard.name1_cn)]
            if wizard.short_name:
                domain += [('short_name', 'ilike', wizard.short_name)]

            result = self.env['v.vendor.without.gv.code'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            # 'domain': domain,
            'name': _('vendor without gv_code'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.vendor.without.gv.code'
        }
        return action
