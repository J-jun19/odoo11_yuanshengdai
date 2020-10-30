# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request

class PoChangePayment(models.Model):
    """    報表 檔
        """
    _name = 'v.po.change.payment'
    _description = "PO Payment term & FOB Change History"
    _auto = False

    plant_code = fields.Char(string="Plant code")
    vendor_code = fields.Char(string="Vendor code")
    vendor_name = fields.Char(string="Vendor Name")
    document_erp_id = fields.Char(string="PO NO")
    document_line_erp_id = fields.Char(string="PO Item")
    old_payment = fields.Char(string="Old Payment")
    old_incoterm = fields.Char(string="Old Incoterm")
    old_destination = fields.Char(string="Old destination")
    new_payment = fields.Char(string="New Payment")
    new_incoterm = fields.Char(string="New Incoterm")
    new_destination = fields.Char(string="New destination")
    part_no = fields.Char(string="Material")
    description = fields.Char(string="Description")
    price = fields.Char(string="Price")
    price_unit = fields.Char(string="Unit")
    amount = fields.Char(string="Amount")
    buyer_erp_id = fields.Char(string="Buyer Code")
    create_by = fields.Char(string="Create by")
    create_date = fields.Char(string="Create date")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_change_payment')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW public.v_po_change_payment AS
                     SELECT dic.id + di.id as id,
                            pl.plant_code,
                            dm.vendor_code,
                            v.name AS vendor_name,
                            dm.document_erp_id,
                            di.document_line_erp_id,
                            pt.payment_term AS old_payment,
                            ic.incoterm AS old_incoterm,
                            dic.ori_incoterm1 AS old_destination,
                            pt1.payment_term AS new_payment,
                            ic1.incoterm AS new_incoterm,
                            dic.new_incoterm1 AS new_destination,
                            p.part_no,
                            p.part_description AS description,
                            di.price,
                            di.price_unit,
                            di.quantity * di.price  /
                                  CASE
                                    WHEN di.price_unit = 0 THEN 1
                                    ELSE di.price_unit
                                 END::double precision AS amount,         
                            dm.buyer_erp_id,
                            rp."name" AS create_by,
                            dic.create_date
                           FROM iac_purchase_order_change dic
                             JOIN iac_purchase_order dm ON dm.id = dic.order_id
                             JOIN iac_purchase_order_line di ON di.order_id = dm.id
                             JOIN iac_vendor v ON v.id = dm.vendor_id
                             JOIN material_master p ON p.id = di.part_id
                             join res_users u on dic.create_uid = u.id
                             join res_partner rp on rp.id = u.partner_id
                             JOIN payment_term pt ON pt.id = dic.ori_payment_term
                             JOIN payment_term pt1 ON pt1.id = dic.new_payment_term
                             JOIN incoterm ic ON ic.id = dic.ori_incoterm_id
                             JOIN incoterm ic1 ON ic1.id = dic.new_incoterm
                             join pur_org_data pl on pl.id = dm.plant_id
                           where dic.new_payment_term <> dic.ori_payment_term 
                              or dic.new_incoterm <> dic.ori_incoterm_id
                              or dic.new_incoterm1 <> dic.ori_incoterm1
                        ORDER BY 1 DESC
                    """)


class PoChangePaymentWizard(models.TransientModel):
    _name = 'iac.po.change.payment.wizard'

    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)],
                               index=True)
    order_no = fields.Char(string="PO")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)
    part_no = fields.Many2one('material.master.asn', string="Part No", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True)
    starttime = fields.Date(string="Change Date From *")
    endtime = fields.Date(string="Change Date To")

    @api.multi
    def search_po_change_payment(self):

        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

            #處理 多選Buyer code
            buyer_codes_list = []
            for buyer_code in wizard.buyer_ids:
                buyer_codes_list.append(buyer_code.buyer_erp_id)
            wizard.buyer_codes_list = ','.join(buyer_codes_list)
            #

            if wizard.plant_id:
                domain += [('plant_code', '=', wizard.plant_id.plant_code)]
            if wizard.order_no:
                domain += [('document_erp_id', '=', wizard.order_no)]
            if wizard.vendor_id:
                domain += [('vendor_code', '=', wizard.vendor_id.id)]
            if wizard.part_no:
                domain += [('part_no', '=', wizard.part_no.part_no)]
            if wizard.buyer_ids:
                domain += [('buyer_erp_id', "in", buyer_codes_list)]
            if wizard.starttime:
                domain += [('create_date', '>=', wizard.starttime)]
            if wizard.endtime:
                domain += [('create_date', '<=', wizard.endtime)]
            print '*51:', domain
            result = self.env['v.po.change.payment'].search(domain)
            print '*54:', result

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('PO Payment term & FOB Change History'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.change.payment'
        }
        return action