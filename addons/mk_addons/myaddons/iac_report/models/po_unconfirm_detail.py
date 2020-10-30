# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request

class PoUnconfirmDetail(models.Model):
    """    報表 檔
        """
    _name = 'v.po.unconfirm.detail'
    _description = "PoUnconfirmDetail Report"
    _auto = False
    _order = 'document_no'

    document_no = fields.Char(string=" document no")
    document_line_no = fields.Char(string="document line no")
    buyer_erp_id = fields.Char(string="buyer code")
    vendor_erp_id = fields.Char(string="vendor code")
    vendor_name = fields.Char(string="vendor name")
    division_code = fields.Char(string="division code")
    part_no = fields.Char(string="part no")
    description = fields.Char(string="description")
    original_qty = fields.Char(string="original qty")
    last_qty = fields.Char(string='last qty')
    new_qty = fields.Char(string="new qty")
    difference = fields.Char(string="difference")
    price = fields.Char(string="price")
    price_unit = fields.Char(string="price unit")
    currency = fields.Char(string="currency")
    change_date = fields.Char(string="change date")
    plant = fields.Char(string="plant")
    ori_deletion_flag = fields.Boolean(string="old deletion flag")
    new_deletion_flag = fields.Boolean(string="new deletion flag")
    actions = fields.Char(string="actions")
    po_creation_date = fields.Char(string="po creation date")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_unconfirm_detail')
        self._cr.execute("""        
             CREATE OR REPLACE VIEW v_po_unconfirm_detail AS
             SELECT pud.id,
                    pud.document_no,
                    pud.document_line_no,
                    po.buyer_erp_id,
                    pud.vendor_erp_id,
                    pud.vendor_name,
                    mm.division AS division_code,
                    pud.part_no,
                    mm.part_description AS description,
                    coalesce(polh.quantity,0) AS original_qty,
                    pud.orig_total_qty AS last_qty,
                    pud.total_qty AS new_qty,
                    pud.diff AS difference,
                    pud.price,
                    pud.priceunit AS price_unit,
                    pud.currency,
                    pud.change_date,
                    pud.plant_id AS plant,
                    pud.ori_deletion_flag,
                    pud.new_deletion_flag,
                    pud.flag AS actions,
                    po.order_date AS po_creation_date

                   FROM iac_purchase_order_unconfirm_detail pud inner
                   JOIN iac_purchase_order_line pol on pol.id = pud.order_line_id  
        left outer JOIN iac_purchase_order_line_history polh on polh.id = pol.line_history_id
                   JOIN material_master mm on mm.id = pud.part_id
                   JOIN iac_purchase_order po ON po.id = pud.order_id
                   where data_type = 'current'
                   ;   """)

class PoUnconfirmDetailWizard(models.TransientModel):
    _name = 'iac.po.unconfirm.detail.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *:", index=True,domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    document_no = fields.Char(string="PO Number:")
    material_id = fields.Many2one('material.master', string="Part:", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer Code:", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Code:", index=True)

    @api.multi
    def search_po_unconfirm_detail(self):
        #print ' *00: ', self.env.user.id,',', self.env.user.name,',',request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

            #print '*19: start buye_code'
            ##多選 buyer_code 處理______s
            buyer_codes_list = []
            for buyer_id in wizard.buyer_ids:
                buyer_codes_list.append(buyer_id.buyer_erp_id)
            wizard.buyer_codes_list = ','.join(buyer_codes_list)
            #print '*20:',buyer_codes_list

            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.document_no:
                domain += [('document_no', '=', wizard.document_no)]
            if wizard.material_id:
                domain += [('part_no', '=', wizard.material_id.part_no)]
            if wizard.buyer_codes_list:
                domain += [('buyer_erp_id', 'in', buyer_codes_list)]
            if wizard.vendor_id:
                domain += [('vendor_erp_id', '=', wizard.vendor_id.vendor_code)]
            #print '--debug --: domain:', domain

            result = self.env['v.po.unconfirm.detail'].search(domain)
            #print '--debug -- :result', result

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Po Unconfirm Detail'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.unconfirm.detail'
        }
        return action