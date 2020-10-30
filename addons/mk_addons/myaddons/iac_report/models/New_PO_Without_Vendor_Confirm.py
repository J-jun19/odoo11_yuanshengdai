# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _



class IacPOWithoutVendorConfirm(models.Model):
    """    報表 檔
       """

    _name = 'v.po.without.vendor.confirm'
    # _description = "New PO without confirm report"
    # _auto = False
    # _order = 'plant, buyer_code, division, po_no, item'

    po_no = fields.Char(string="po_no")
    item = fields.Char(string="item")
    vendor_code = fields.Char(string="vendor_code")
    vendor_name = fields.Char(string="vendor_name")
    division = fields.Char(string="division")
    material = fields.Char(string="material")
    material_descrp = fields.Char(string="material_descrp")
    qty = fields.Float(string="QTY", precision=(18, 4))
    price = fields.Float(string="Price", precision=(18, 4))
    price_unit = fields.Integer(string="price_unit")
    currency = fields.Char(string="currency")
    po_date = fields.Date(string="po_date")
    plant = fields.Char(string="plant")
    buyer_code = fields.Char(string="buyer_code")
    supplier_action = fields.Char(string="supplier_action")
    sloc = fields.Char(string="sloc")



class IacPOWithoutVendorConfirmWizard(models.TransientModel):
    _name = 'v.po.without.vendor.confirm.wizard'
    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)],
                               index=True)
    material_id = fields.Many2one('material.master', string="Part No", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True)
    division_ids = fields.Many2many('division.code', string="Division", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)
    po_no = fields.Char(string="PO Number")
    start_date = fields.Date(string="PO date from")
    end_date = fields.Date(string="PO date to")

    @api.multi
    def search_new_po_unconfirm_report(self):
        self.ensure_one()
        result = []
        lc_material_id = ""
        lc_buyer_ids = ""
        lc_division_ids = ""
        lc_vendor_id = ""
        lc_po_no = ""
        for wizard in self:

            if wizard.material_id:
                lc_material_id = wizard.material_id.part_no
            if wizard.vendor_id:
                lc_vendor_id = wizard.vendor_id.vendor_code
            if wizard.po_no:
                lc_po_no = wizard.po_no
            if wizard.division_ids:
                division_list = []
                for item in wizard.division_ids:
                    division_list.append(str(item.division))
                if len(wizard.division_ids) == 1:
                    lc_division_ids = str(tuple(division_list))[:5]+str(tuple(division_list))[6:7]

                else:
                    lc_division_ids = str(tuple(division_list))
            if wizard.buyer_ids:
                # lc_buyer_ids="(504,533)"
                # print len(wizard.buyer_ids)
                buyer_list = []
                for item in wizard.buyer_ids:

                    buyer_list.append(str(item.buyer_erp_id))
                if len(wizard.buyer_ids) == 1:
                    lc_buyer_ids = str(tuple(buyer_list))[:6]+str(tuple(buyer_list))[7:8]
                else:
                    lc_buyer_ids = str(tuple(buyer_list))

        self.env.cr.execute('select v_id from public.proc_report_new_po_wo_vendor_confirm'
                            ' (%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                            (wizard.plant_id.plant_code, lc_material_id,lc_buyer_ids,
                             lc_division_ids, lc_vendor_id,lc_po_no,wizard.start_date,wizard.end_date))
        result_po_without_vendor = self.env.cr.fetchall()
        result_ids = []
        for result_po_without_vendor_wa in result_po_without_vendor:
            result_ids.append(result_po_without_vendor_wa)

        act = {
            'domain': [('id', 'in', result_ids)],
            'name': _('New PO without confirm report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.without.vendor.confirm'
        }
        return act
