# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request

class PoPriceChangeHistory(models.Model):
    """    報表 檔
        """
    _name = 'v.po.price.change.history'
    _description = "Po Price Change History Report"
    _auto = False
    #_order = 'vendor_name'

    plant = fields.Char(string="Plant")
    division = fields.Char(string="Division")
    order_code = fields.Char(string="Order Code")
    order_line_code = fields.Char(string="Order Line Code")
    buyer_code = fields.Char(string="Buyer Code")
    buyer_name = fields.Char(string="Buyer Name")
    vendor_code = fields.Char(string="Vendor Code")
    vendor_name = fields.Char(string="Vendor Name")
    part_no = fields.Char(string="Part No")
    part_description = fields.Char(string="Part description")
    old_price = fields.Char(string="Last Price")
    new_price = fields.Char(string="New Price")
    delta = fields.Char(string="Delta")
    price_unit = fields.Char(string="Price Unit")
    currency = fields.Char(string="Currency")
    rfq_price = fields.Char(string="RFQ Price")
    rfq_price_unit = fields.Char(string="RFQ Price Unit")
    valid_from = fields.Char(string="Valid From")
    valid_to = fields.Char(string="Valid To")
    change_state = fields.Char(string="Change State")
    original_quantity = fields.Char(string="Original Quantity")
    last_quantity = fields.Char(string="Last Quantity")
    new_quantity = fields.Char(string="New Quantity")
    gr_qty = fields.Char(string="GR Quantity")
    open_qty = fields.Char(string="Open Quantity")
    current_amt = fields.Char(string="Current Amount")
    tax_code = fields.Char(string="Tax Code")
    change_date = fields.Char(string="Change Date")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_price_change_history')
        self._cr.execute("""
                 CREATE OR REPLACE VIEW public.v_po_price_change_history AS
                 SELECT dic.id,
                        pl.plant_code AS plant,
                        dc.division,
                        dic.order_code,
                        dic.order_line_code,
                        dm.buyer_erp_id AS buyer_code,
                        bc.buyer_name,
                        v.vendor_code,
                        v.name AS vendor_name,
                        p.part_no,
                        p.part_description,
                        dic.ori_price AS old_price,
                        dic.new_price,
                        dic.ori_price - dic.new_price AS delta,
                        dic.price_unit,
                        dm.currency,
                        rfq.price AS rfq_price,
                        rfq.price_unit AS rfq_price_unit,
                        rfq.valid_from,
                        rfq.valid_to,
                        dic.change_state,
                        coalesce(polh.quantity,0) AS original_quantity,
                        dic.ori_qty AS last_quantity,
                        dic.new_qty AS new_quantity,
                        fm_get_pol_gr_qty(dic.order_line_id::character varying) AS gr_qty,
                        dic.new_qty - fm_get_pol_gr_qty(dic.order_line_id::character varying) AS open_qty,
                            CASE dic.price_unit
                                WHEN 0 THEN 0::double precision
                                ELSE dic.new_qty * dic.new_price / dic.price_unit::double precision
                            END AS current_amt,
                        dic.tax_code,
                        dic.create_date AS change_date
                       FROM iac_purchase_order_line_change dic
                         JOIN iac_purchase_order_line pol on pol.id = dic.order_line_id 
              left outer JOIN iac_purchase_order_line_history polh on polh.id = pol.line_history_id
                         JOIN iac_vendor v ON v.id = dic.vendor_id
                         JOIN material_master p ON p.id = dic.part_id
                         JOIN division_code dc ON dc.id = p.division_id
                         JOIN iac_purchase_order dm ON dm.id = dic.order_id
                         JOIN pur_org_data pl ON pl.id = dm.plant_id
                         JOIN buyer_code bc ON bc.id = dm.buyer_id
                         LEFT JOIN v_valid_rfq rfq ON rfq.part_no::text = p.part_no::text AND rfq.vendor_code::text = v.vendor_code::text
                      WHERE dic.change_state::text = ANY (ARRAY['cost_up'::character varying::text, 'cost_down'::character varying::text])
                      ORDER BY dic.order_code, dic.order_line_code """)


class PoPriceChangeHistoryWizard(models.TransientModel):
    _name = 'iac.po.price.change.history.wizard'

    #plant_id = fields.Many2one('pur.org.data',string="Plant **",index=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)],
                               index=True)
    order_code = fields.Char(string="PO")
    part_no = fields.Many2one('material.master', string="Part No", index=True)
    division_ids = fields.Many2many('division.code', string="Division", index=True)
    buyer_ids = fields.Many2many('buyer.code', string="Buyer code", index=True)
    starttime = fields.Date(string="Change Date From *")
    endtime = fields.Date(string="Change Date To")

    #change_state = fields.Selection(related='last_order_line_change_id.change_state', string="Change State")
    #change_ids = fields.Many2many('change.state', string="Change State")
    change_ids = fields.Selection([
        ('ALL', 'ALL'),
        ('cost_up', 'Cost Up'),
        ('cost_down', 'Cost Down')
    ], string='Change State', index=True, copy=False)

    @api.multi
    def search_po_price_change_history_report(self):

        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

        if wizard.plant_id:
            domain += [('plant', '=', wizard.plant_id.plant_code)]
        if wizard.order_code:
            domain += [('order_code', '=', wizard.order_code)]
        if wizard.part_no:
            domain += [('part_no', '=', wizard.part_no.part_no)]

        # 處理 多選Division code
        division_codes_list = []
        for division_code in wizard.division_ids:
            division_codes_list.append(division_code.division)
        wizard.division_codes_list = ','.join(division_codes_list)
        #
        if wizard.division_ids:
            domain += [('division', 'in',  division_codes_list)]

        # 處理 多選Buyer code
        buyer_codes_list = []
        for buyer_code in wizard.buyer_ids:
            buyer_codes_list.append(buyer_code.buyer_erp_id)
        wizard.buyer_codes_list = ','.join(buyer_codes_list)
        #
        if wizard.buyer_ids:
            domain += [('buyer_code', "in", buyer_codes_list)]

        # 處理 多選change_state
         #   change_states_list = []
         #   for change_state in wizard.change_ids:
         #   change_states_list.append('cost_up')
         #   change_states_list.append('cost_down')
         #   wizard.change_states_list = ','.join(change_states_list)

        if wizard.change_ids and wizard.change_ids != 'ALL':
            domain += [('change_state', '=', wizard.change_ids)]
        print '*155:', domain

        #if wizard.change_state:
        #    domain += [('change_state', 'in', wizard.last_order_line_change_id.change_state)]
        if wizard.starttime:
            domain += [('change_date', '>=', wizard.starttime)]
        if wizard.endtime:
            domain += [('change_date', '<=', wizard.endtime)]


        print '*51:', domain

        result = self.env['v.po.price.change.history'].search(domain)
        # print '*54:', result
        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('PO Price Change History'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.price.change.history'
        }
        return action