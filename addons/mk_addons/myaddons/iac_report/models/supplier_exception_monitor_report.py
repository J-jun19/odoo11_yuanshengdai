# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class SupplierExceptionMonitorReport(models.Model):
    _name = "v.po.state.exception"
    _description = "Supplier Exception Monitor"
    _auto = False
    #    _order = ' '


    po_no = fields.Char(string="po_no", readonly=True)
    po_line_no = fields.Char(string="po_line_no", readonly=True)
    plant_code = fields.Char(string="plant_code", readonly=True)
    buyer_erp_id = fields.Char(string="buyer_erp_id", readonly=True)
    buyer_name = fields.Char(string="buyer_name", readonly=True)
    vendor_code = fields.Char(string="vendor_code", readonly=True)
    vendor_name = fields.Char(string="vendor_name", readonly=True)
    part_no = fields.Char(string="part_no", readonly=True)
    iac_price = fields.Char(string="iac_price", readonly=True)
    iac_price_unit = fields.Char(string="iac_price_unit", readonly=True)
    iac_qty = fields.Char(string="iac_qty", readonly=True)
    iac_dn_date = fields.Char(string=" iac_dn_date", readonly=True)
    supplier_dn_date = fields.Char(string="supplier_dn_date", readonly=True)
    exception_reason = fields.Char(string="exception_reason", readonly=True)
    po_date = fields.Char(string="po_date", readonly=True)
    reply_date = fields.Char(string="reply_date", readonly=True)
    open_flag = fields.Char(string="open_flag", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_state_exception')
        self._cr.execute("""
            CREATE OR REPLACE VIEW v_po_state_exception AS (
                 SELECT pol.id,
                    po.document_erp_id AS po_no,
                    pol.document_line_erp_id AS po_line_no,
                    pol.plant_code,
                    po.buyer_erp_id,
                    bc.buyer_name,
                    po.vendor_code,
                    v.name AS vendor_name,
                    pol.part_no,
                    pol.price AS iac_price,
                    pol.price_unit AS iac_price_unit,
                    pol.quantity AS iac_qty,
                    pol.delivery_date AS iac_dn_date,
                    pol.vendor_delivery_date AS supplier_dn_date,
                    pol.vendor_exception_reason AS exception_reason,
                    po.order_date AS po_date,
                    pol.write_date AS reply_date,
                    CASE
                        WHEN (pol.quantity - fm_get_pol_gr_qty(pol.id::character varying)) > 0::
                             double precision THEN 'Y'::text
                        ELSE 'N'::text
                    END AS open_flag
                   FROM iac_purchase_order po
                     JOIN iac_purchase_order_line pol ON pol.order_id = po.id
                     JOIN buyer_code bc ON bc.id = po.buyer_id
                     JOIN iac_vendor v ON v.id = po.vendor_id
                   WHERE pol.state::text = 'vendor_exception'::text)
                                       """)

class supplier_exception_monitor_report(models.TransientModel):
    _name = 'v.po.state.exception.wizard'

    # plant_id = fields.Many2one('pur.org.data', related='user_info_id.plant_id', string="Plant", index=True)
    # user_info_id = fields.Many2one('v.user.info', string="user info id", index=True, default=lambda self: self.env.user)
    plant_id = fields.Many2one('pur.org.data', string="Plant *",domain=lambda self:[('id','in',self.env.user.plant_id_list)])
    # plant_id = fields.Many2one('pur.org.data', string="Plant")
    part_no = fields.Char(string="Part No", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True)
    po_date_from = fields.Date(string=u"PO date 開始")
    po_date_to = fields.Date(string=u"PO date 結束")
    vendor_code = fields.Char(string="Vendor Code")
    open_flag = fields.Selection([('Y', 'Y'), ('N', 'N')], string="Is Open POs")

    # @api.onchange('plant_id')
    # def _onchange_plant_id(self):
    #
    #     if self.plant_id:
    #         return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
    #                                          ('state', 'in', ('done', 'block'))]}}
    #     else:
    #         return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def search_supplier_exception_monitor_report(self):
        self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

            ##多選 buyer_code 處理______s
            buyer_codes_list = []
            for buyer_id in wizard.buyer_ids:
                buyer_codes_list.append(buyer_id.buyer_erp_id)
                wizard.buyer_codes_list = ','.join(buyer_codes_list)
            # print '*62:',buyer_codes_list
            ##多選 divisions 處理______e

            if wizard.plant_id:
                domain += [('plant_code', '=', wizard.plant_id)]
            if wizard.part_no:
                domain += [('part_no', 'ilike', wizard.part_no)]
            if wizard.buyer_ids:
                domain += [('buyer_erp_id', 'in', buyer_codes_list)]
            if wizard.po_date_from:
                domain += [('po_date', '>=', wizard.po_date_from)]
            if wizard.po_date_to:
                domain += [('po_date', '<=', wizard.po_date_to)]
            if wizard.vendor_code:
                domain += [('vendor_code', '=', wizard.vendor_code.zfill(10).strip())]
            if wizard.open_flag:
                domain += [('open_flag', '=', wizard.open_flag)]
            result = self.env['v.po.state.exception'].search(domain)

            print '*71:', domain

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Supplier Exception Monitor Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.state.exception'
        }
        return action
