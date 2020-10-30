    # -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request

class PoUnconfirmSummaryReport(models.Model):
    """    報表 檔
        """
    _name =  'v.po.unconfirm.summary'
    _description = "PO Unconfirmed Summary Report"
    _auto = False
    # _order = 'plant_code desc,vendor_code'

    document_no = fields.Char(string="Document No")
    document_line_no = fields.Char(string="Document Line No")
    create_date = fields.Char(string="Create Date")
    buyer_erp_id = fields.Char(string="Buyer ID")
    vendor_erp_id = fields.Char(string="Vendor ID")
    vendor_name = fields.Char(string="Vendor Name")
    division_code = fields.Char(string="Division")
    part_no = fields.Char(string="Part No")
    description = fields.Char(string="Part Description")
    part_description = fields.Char(string="Part description")
    plant = fields.Char(string="Plant")
    increase_qty = fields.Char(string="Increase qty")
    decrease_qty = fields.Char(string="Decrease qty")
    price = fields.Char(string="Price")
    price_unit = fields.Char(string="Price Unit")
    currency = fields.Char(string="Currency")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_unconfirm_summary')
        self._cr.execute("""                        
            CREATE OR REPLACE VIEW public.v_po_unconfirm_summary AS
            SELECT pus.id,
                pus.document_no,
                pus.document_line_no,
                po.order_date AS create_date,
                po.buyer_erp_id,
                pus.vendor_erp_id,
                pus.vendor_name,
                mm.division AS division_code,
                pus.part_no,
                mm.part_description AS description,
                pus.plant_id AS plant,
                pus.unconqtyr AS increase_qty,
                pus.unconqtyd AS decrease_qty,
                pus.price,
                pus.price_unit,
                pus.currency
               FROM iac_purchase_order_unconfirm_summary pus
                 JOIN material_master mm ON mm.id = pus.part_id
                 JOIN iac_purchase_order po ON po.id = pus.order_id
              WHERE pus.data_type::text = 'current'::text AND (pus.unconqtyd <> 0::numeric OR pus.unconqtyr <> 0::numeric);

""")


class PoUnconfirmSummaryWizard(models.TransientModel):
    _name = 'iac.po.unconfirm.summary.wizard'
    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)],
                               index=True)
    material_id = fields.Many2one('material.master', string="Material", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)

    @api.multi
    def search_po_unconfirm_summary_report(self):
        # print ' *102: ', self.env.user.id,',', self.env.user.name,',',\
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
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.material_id:
                domain += [('part_no', '=', wizard.material_id.part_no)]
            if wizard.vendor_id:
                domain += [('vendor_erp_id', '=', wizard.vendor_id.vendor_code)]

            result = self.env['v.po.unconfirm.summary'].search(domain)
            print '*v.po.unconfirm.summary:', result

        act = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('PO Unconfirm Summary Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.unconfirm.summary'
        }
        return act