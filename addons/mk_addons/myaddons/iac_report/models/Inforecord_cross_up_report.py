# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class InfoRecordCrossUpReport(models.Model):
    _name = "v.info.record.cross.up.report"
    _description = "Info Record Cross Up Report"
    _auto = False

    approve_date = fields.Date('簽核日期')
    division_code = fields.Char('Division')
    division_desc = fields.Char('Division描述')
    vendor_code = fields.Char('Vendor Code')
    vendor_name = fields.Char('Vendor Name')
    material_group = fields.Char('材料類別')
    material = fields.Char('料號')
    currency = fields.Char('幣別')
    last_price = fields.Float('原價', digits=(18, 6))
    new_price = fields.Float('現價', digits=(18, 6))
    quantity = fields.Char('數量')
    request_by = fields.Char('客人要求/廠商要求')
    reason_id = fields.Char('漲價原因')
    comment = fields.Char('漲價說明（意見欄）')
    customer_duty = fields.Char('客人是否吸收漲價')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_info_record_cross_up_report')
        self._cr.execute("""
        CREATE OR REPLACE VIEW public.v_info_record_cross_up_report AS
        select r.id,
               r.approve_date_web as approve_date,
               dc.division as division_code,
               dc.division_description as division_desc,
               v.vendor_code as vendor_code,
               v."name" as vendor_name,
               mm.material_group as material_group,
               mm.part_no as material,
               rc."name" as currency,
               r.last_price as last_price,
               r.input_price as new_price,
               r.effect_quantity_web as quantity,
               r.request_by_web as request_by,
               r.cost_up_reason_web as reason_id,
               r.comment_web as comment,
               r.customer_duty_web as customer_duty
               from iac_rfq r
         inner join division_code dc on dc.id = r.division_id
         inner join iac_vendor v on v.id = r.vendor_id  
         inner join material_master mm on mm.id = r.part_id
         inner join res_currency rc on rc.id = r.currency_id
         where r.change_factor_price = 'up' and r.approve_date_web is not null 
                     and r.last_rfq_id is not null
          """)


class InfoRecordCrossUpReportWizard(models.TransientModel):
    _name = 'info.record.cross.up.report.wizard'

    approve_date_from = fields.Date(string="签核日期 Begin *")
    approve_date_to = fields.Date(string="签核日期 End *")

    @api.multi
    def search_info_record_cross_up_report(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.approve_date_from:
                domain += [('approve_date', '>=', wizard.approve_date_from)]
            if wizard.approve_date_to:
                domain += [('approve_date', '<=', wizard.approve_date_to)]

            result = self.env['v.info.record.cross.up.report'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Info Record Cross Up Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.info.record.cross.up.report'
        }
        return action
