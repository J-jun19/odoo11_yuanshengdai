# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _

class DeletedPOReport(models.Model):
    _name = "v.po.line.info"
    _description = "PO line info"
    # _auto = False

    plant_code = fields.Char(string='Plant')
    division = fields.Char(string='Division')
    part_no = fields.Char(string='Part No')
    part_description = fields.Char(string='Part description')
    po_date = fields.Datetime(string='PO date')
    quantity = fields.Float(string='PO quantity')
    open_qty = fields.Float(string='Open PO quantity')
    price = fields.Float(string='Price')
    price_unit = fields.Integer(string='Price unit')
    document_erp_id = fields.Char(string='PO number')
    document_line_erp_id = fields.Char(string='PO line number')
    delivery_date = fields.Date(string='Delivery date')
    vendor_code = fields.Char(string='Vendor code')
    buyer_erp_id = fields.Char(string='Buyer erp ID')
    buyer_name = fields.Char(string='Buyer Name')
    deletion_flag = fields.Char(string='Deletion flag')

    # @api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'v_po_line_info')
    #     self._cr.execute("""
    #                         create
    #                             or replace view public.v_po_line_info as select
    #                                 row_number() OVER () AS id,
    #                                 pol.plant_code,
    #                                 mm.division,
    #                                 mm.part_no,
    #                                 mm.part_description,
    #                                 pol.create_date as po_date,
    #                                 pol.quantity,
    #                                 0 as open_qty,
    #                                 pol.price,
    #                                 pol.price_unit,
    #                                 pol.document_erp_id,
    #                                 pol.document_line_erp_id,
    #                                 pol.delivery_date,
    #                                 pol.vendor_code,
    #                                 bc.buyer_erp_id,
    #                                 bc.buyer_name,
    #                                 pol.deletion_flag
    #                             from
    #                                 iac_purchase_order_line pol
    #                             inner join material_master mm on
    #                                 pol.part_id = mm.id
    #                             inner join buyer_code bc on
    #                                 bc.id = pol.buyer_id
    #                     """)


class IacPODeleteStateWizard(models.TransientModel):
    _name = 'v.po.delete.state.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *", required='1',domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    part_id = fields.Many2one('material.master', string='Part no')
    buyer_code_id = fields.Many2one('buyer.code', string='Buyer code')
    division_id = fields.Many2one('division.code', string='Division no')
    vendor_id = fields.Many2one('iac.vendor', string='Vendor no')
    po_date_begin = fields.Date(string='PO date from *',required='1')
    po_date_end = fields.Date(string='PO date to *',required='1')

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return{'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}


    @api.multi
    def search_po_line_report(self):
        self.ensure_one()
        result = []
        domain = []
        domain += [('deletion_flag', '=', 'L')]  # 固定抓被刪掉的item

        lt_part = ''
        lt_buyer = ''
        lt_division = ''
        lt_vendor = ''
        lt_delete = 'L'

        for wizard in self:
            # if wizard.plant_id:
            #     domain += [('plant_code', '=', wizard.plant_id.plant_code)]
            if wizard.part_id:
                # domain += [('part_no', '=', wizard.part_id.part_no)]
                lt_part = wizard.part_id.part_no
            if wizard.buyer_code_id:
                # domain += [('buyer_erp_id', 'in', [x.buyer_erp_id for x in wizard.buyer_code_id])]
                lt_buyer = wizard.buyer_code_id.buyer_erp_id
            if wizard.division_id:
                # domain += [('division', 'in', [x.division for x in wizard.division_id])]
                lt_division = wizard.division_id.division
            if wizard.vendor_id:
                # domain += [('vendor_code', 'in', [x.vendor_code for x in wizard.vendor_id])]
                lt_vendor = wizard.vendor_id.vendor_code
            # if wizard.po_date_begin:
            #     domain += [('po_date', '>=', wizard.po_date_begin)]
            #
            # if wizard.po_date_end:
            #     domain += [('po_date', '<=', wizard.po_date_end)]


            # result = self.env['v.po.line.info'].search(domain)
            self.env.cr.execute('select v_id from public.proc_po_delete_state'
                                ' (%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                                (wizard.plant_id.plant_code, lt_part, lt_buyer, lt_division,
                                 lt_vendor, wizard.po_date_begin, wizard.po_date_end,lt_delete))

            result_po_delete = self.env.cr.fetchall()
            result_ids = []
            for result_po_delete_item in result_po_delete:
                result_ids.append(result_po_delete_item)


        action = {
            'domain': [('id', 'in', result_ids)],
            #'domain': domain,
            'name': _('PO line info'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.po.line.info'
        }
        return action