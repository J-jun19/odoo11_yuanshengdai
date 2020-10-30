# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class SupplierAttachmentList(models.Model):
    _name = "v.vendor.file.info"
    _auto = False
    #    _order = 'gv_code'

    company_no = fields.Char(string="Company No", readonly=True)
    vendor_code = fields.Char(string="Vendor Code", readonly=True)
    name1_cn = fields.Char(string="Name1 CN", readonly=True)
    file_type = fields.Char(string="File Type", readonly=True)
    file_descp = fields.Char(string="File Descp", readonly=True)
    file_id = fields.Many2one('muk_dms.file',string="File Id")
    state = fields.Char(string="State", readonly=True)
    create_date = fields.Datetime(string="Create Date", readonly=True)
    approver = fields.Char(string="Approver", readonly=True)
    last_change_date = fields.Char(string="Last Change Date", readonly=True)
    memo = fields.Char(string="Memo", readonly=True)
    expiration_date = fields.Char(string="Expiration Date", readonly=True)
    sc_id = fields.Char()
    vendor_id = fields.Char()
    file_type_id = fields.Char()



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_file_info')
        self._cr.execute("""
                        CREATE OR REPLACE VIEW "public"."v_vendor_file_info" AS 
 SELECT row_number() OVER () AS id,
    t.sc_id,
    t.vendor_id,
    t.file_type_id,
    t.company_no,
    t.vendor_code,
    t.name1_cn,
    t.file_type,
    t.file_descp,
    t.file_id,
    t.state,
    t.create_date,
    t.approver,
    t.last_change_date,
    t.memo,
    t.expiration_date
   FROM ( SELECT DISTINCT sc.id AS sc_id,
            v.id AS vendor_id,
            iat.id AS file_type_id,
            sc.company_no,
            v.vendor_code,
            vr.name1_cn,
            iat.name AS file_type,
            iat.description AS file_descp,
            va.file_id,
            va.state,
            va.create_date,
            rp.display_name AS approver,
                CASE
                    WHEN ((va.state)::text = 'active'::text) THEN va.write_date
                    WHEN ((va.state)::text = 'inactive'::text) THEN va.write_date
                    ELSE NULL::timestamp without time zone
                END AS last_change_date,
            va.memo,
            va.expiration_date
           FROM (((((((iac_vendor_attachment va
             JOIN iac_vendor v ON ((v.id = va.vendor_id)))
             JOIN iac_vendor_register vr ON ((vr.id = v.vendor_reg_id)))
             JOIN iac_supplier_company_line scl ON ((scl.vendor_id = v.id)))
             JOIN iac_supplier_company sc ON ((sc.id = scl.supplier_company_id)))
             JOIN iac_attachment_type iat ON ((iat.id = va.type)))
             LEFT JOIN res_users ru ON ((ru.id = va.approver_id)))
             LEFT JOIN res_partner rp ON ((rp.id = ru.partner_id)))
          WHERE (va.file_id IS NOT NULL)
        UNION
         SELECT DISTINCT sc.id AS sc_id,
            v.id AS vendor_id,
            iat.id AS file_type_id,
            sc.company_no,
            v.vendor_code,
            vr.name1_cn,
            iat.name AS file_type,
            iat.description AS file_descp,
            vra.file_id,
            vra.state,
            vra.create_date,
            rp.display_name AS approver,
                CASE
                    WHEN ((vra.state)::text = 'active'::text) THEN vra.write_date
                    WHEN ((vra.state)::text = 'inactive'::text) THEN vra.write_date
                    ELSE NULL::timestamp without time zone
                END AS last_change_date,
            vra.memo,
            vra.expiration_date
           FROM (((((((iac_vendor_register_attachment vra
             JOIN iac_vendor v ON ((v.vendor_reg_id = vra.vendor_reg_id)))
             JOIN iac_vendor_register vr ON ((vr.id = vra.vendor_reg_id)))
             JOIN iac_supplier_company_line scl ON ((scl.vendor_id = v.id)))
             JOIN iac_supplier_company sc ON ((sc.id = scl.supplier_company_id)))
             JOIN iac_attachment_type iat ON ((iat.id = vra.type)))
             LEFT JOIN res_users ru ON ((ru.id = vra.approver_id)))
             LEFT JOIN res_partner rp ON ((rp.id = ru.partner_id)))
          WHERE (vra.file_id IS NOT NULL)) t;
                                    """)

class SupplierAttachmentListWizard(models.TransientModel):
    _name = 'v.vendor.file.info.wizard'

#    plant_id = fields.Many2one('v.user.info', string="Plant")
    supplier_company = fields.Many2one('iac.supplier.company', string="Supplier Company")
    vendor_code = fields.Many2one('iac.vendor',string="Vendor Code")
    file_description = fields.Many2one('iac.attachment.type',string="File Description")
    state = fields.Selection([
        ('upload', 'Upload'),
        ('active', 'Activate'),
        ('inactive', 'Inactivate')
    ], string='Status', default='upload', require=True)

    @api.onchange('supplier_company')
    def _onchange_supplier_company(self):

        if self.supplier_company:
            return {'domain': {'vendor_code': [('supplier_company_id', '=', self.supplier_company.id)]}}


    @api.multi
    def search_supplier_attachment_list(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.supplier_company:
                domain += [('sc_id', '=', wizard.supplier_company.id)]
            if wizard.vendor_code:
                domain += [('vendor_id', '=', wizard.vendor_code.id)]
            if wizard.file_description:
                domain += [('file_descp', '=', wizard.file_description.description)]
            if wizard.state:
                domain += [('state', '=', wizard.state)]


            result = self.env['v.vendor.file.info'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            #'domain': domain,
            'name': _('Supplier Attachment List'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'v.vendor.file.info'
        }
        return action
