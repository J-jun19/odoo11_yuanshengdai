# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request

class PoCancelHistoryReport(models.Model):
    """    報表 檔
        """
    _name = 'v.po.cancel.history.report'
    _description = "PoCancelHistory Report"
    _auto = False
    # _order = 'plant_code desc,vendor_code'

    order_code = fields.Char(string="Order code")
    order_line_code = fields.Char(string="Order line code")
    buyer_code = fields.Char(string="Buyer code")
    vendor_code = fields.Char(string="Vendor code")
    vendor_id = fields.Char(string="Vendor id")
    vendor_name = fields.Char(string="Vendor name")
    division = fields.Char(string="Division")
    part_no = fields.Char(string="Part no")
    material_id = fields.Char(string="Material id")
    part_description = fields.Char(string="Part description")
    original_qty = fields.Char(string="Original qty")
    last_qty = fields.Char(string="Last qty")
    current_qty = fields.Char(string="Current qty")
    current_amt = fields.Char(string="Current amt")
    currency = fields.Char(string="Currency")
    increase_qty = fields.Char(string="Increase qty")
    decrease_qty = fields.Char(string="Decrease qty")
    deletion_flag = fields.Char(string="Deletion flag")
    ori_deletion_flag = fields.Char(string="Ori deletion flag")
    sap_deletion_flag = fields.Char(string="Sap deletion flag")
    tax_code = fields.Char(string="Tax code")
    change_state = fields.Char(string="Change state")
    change_date = fields.Char(string="Change date")
    plant = fields.Char(string="Plant")
    plant_id = fields.Char(string="Plant id")
    storage_location = fields.Char(string="storage_location")
    storage_location_id = fields.Many2one('iac.storage.location.address', string="storage_location_id")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_cancel_history_report')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW public.v_po_cancel_history_report AS
                    SELECT  row_number() OVER () AS id, 
                            dic.order_code,
                            dic.order_line_code,
                            dm.buyer_erp_id AS buyer_code,
                            v.vendor_code,                                                            
                            v.id AS vendor_id,                                                            
                            v.name AS vendor_name,                                                    
                            p.division,
                            p.part_no,
                            p.id AS material_id,
                            p.part_description,
                            coalesce(polh.quantity,0) AS original_qty,
                            dic.ori_qty AS last_qty,
                            dic.new_qty AS current_qty,
                            CASE dic.price_unit
                                 WHEN 0 THEN 0::double precision
                                 ELSE dic.new_qty * dic.new_price / dic.price_unit::double precision
                            END AS current_amt,
                            dm.currency,
                            dic.increase_qty,
                            dic.decrease_qty,
                            dic.deletion_flag,
                            dic.ori_deletion_flag,
                            dic.sap_deletion_flag,
                            dic.tax_code,
                            dic.change_state,
                            dic.create_date AS change_date,
                            pl.plant_code AS plant,
                            pl.id AS plant_id,
                            dic.storage_location,
                            sla.id AS storage_location_id
                           FROM iac_purchase_order_line_change dic
                             JOIN iac_purchase_order_line pol on pol.id = dic.order_line_id
                  left outer JOIN iac_purchase_order_line_history polh on polh.id = pol.line_history_id
                             JOIN iac_vendor v ON v.id = dic.vendor_id
                             JOIN material_master p ON p.id = dic.part_id
                             JOIN iac_purchase_order dm ON dm.id = dic.order_id
                             JOIN pur_org_data pl ON pl.id = dm.plant_id
                             JOIN iac_storage_location_address sla ON sla.plant::text = pl.plant_code::text AND sla.storage_location::text = dic.storage_location::text
                          WHERE dic.change_state::text = ANY (ARRAY['qty_down'::character varying, 'cancel_po_line'::character varying]::text[])
                          ORDER BY dic.order_code, dic.order_line_code      """)


class PoCancelHistoryWizard(models.TransientModel):
    _name = 'iac.po.cancel.history.wizard'
    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)],
                               index=True)
    # plant_id = fields.Many2one('pur.org.data',string="Plant",index=True)  # 用戶登入后選擇的plant
    starttime = fields.Date(string="Start Time *")
    material_id = fields.Many2one('material.master', string="Material", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)

    @api.multi
    def search_po_cancel_history_report(self):
        # print ' *102: ', self.env.user.id,',', self.env.user.name,',',\
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            # if wizard.plant_id:
            #     domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.material_id:
                domain += [('material_id', '=', wizard.material_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.starttime:
                domain += [('change_date', '>=', wizard.starttime)]
            print '*110:', domain

            result = self.env['v.po.cancel.history.report'].search(domain)
            print '*113:', result

        act = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Po Cancel HistoryReport'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.cancel.history.report'
        }
        return act