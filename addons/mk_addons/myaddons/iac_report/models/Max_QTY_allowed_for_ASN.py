# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class MaxQtyReport(models.Model):
    _name = "v.max.qty.report"
    _description = "Max Qty"
    _auto = False
    #_order = 'vendor_code'

    vendor_code = fields.Char()
    vendor_name = fields.Char()
    plant = fields.Char()
    material = fields.Char()
    material_description = fields.Char()
    maxqty = fields.Char(string='max qty')
    weekly_qty = fields.Char()
    adjust_qty = fields.Char()
    allowqty = fields.Char(string='allow qty')
    lastupdatedate = fields.Char(string='lastupdate date')
    status = fields.Char()


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_max_qty_report')
        self._cr.execute("""
CREATE OR REPLACE VIEW "public"."v_max_qty_report" AS 
 SELECT amq.id,
    amq.vendorcode AS vendor_code,
    v.name AS vendor_name,
    amq.plant,
    amq.material,
    mm.part_description AS material_description,
    amq.maxqty,
    amq.shipped_qty AS weekly_qty,
    COALESCE(sum(amqcl.increase_qty), (0)::bigint) AS adjust_qty,
    ((amq.maxqty - amq.shipped_qty) + COALESCE(sum(amqcl.increase_qty), (0)::bigint)) AS allowqty,
    amq.write_date AS lastupdatedate,
    amq.state AS status,
    amq.create_date
   FROM (((asn_maxqty amq
     JOIN iac_vendor v ON ((v.id = amq.vendor_id)))
     JOIN material_master mm ON ((amq.part_id = mm.id)))
     LEFT JOIN iac_asn_max_qty_create_line_update amqcl ON (((amqcl.asn_max_qty_id = amq.id) AND (amqcl.asn_line_id IS NULL))))
  WHERE (1 = 1)
  GROUP BY amq.id, amq.vendorcode, v.name, amq.plant, amq.material, mm.part_description, amq.maxqty, amq.shipped_qty, amq.write_date, amq.state, amq.create_date;
                            """)


class MaxQtyReportWizard(models.Model):
    _name = "iac.max.qty.report.wizard"
    #_description = "Max Qty"
    #_auto = False
    #_order = 'vendor_code'

    part_no = fields.Text()
    status = fields.Selection([('done','Done'),
                              ('cancel','Cancel')])



    @api.multi
    def search_max_qty_report(self):
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []
            if wizard.part_no:
                part_no_list = wizard.part_no.split('\n')
                domain += [('material', 'in',part_no_list)]
            if wizard.status:
                domain+=[('status','=',wizard.status)]

            result = self.env['v.max.qty.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Max Qty Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.max.qty.report'
        }
        return action



