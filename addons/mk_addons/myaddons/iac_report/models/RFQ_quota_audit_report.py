# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.exceptions import UserError
from odoo.tools.translate import _


class RfqQuotaAuditReport(models.Model):
    _name = "v.iac.rfq.quota.history"
    _auto = False

    rfq_no = fields.Char(string='Rfq No', readonly=True)
    action_type = fields.Char(string='action_type', readonly=True)
    action_date = fields.Char(string='action_date', readonly=True)
    user_name = fields.Char(string='user_name', readonly=True)
    plant = fields.Char(string='plant', readonly=True)
    part_no = fields.Char(string='part_no', readonly=True)
    vendor_code = fields.Char(string='vendor_code', readonly=True)
    vendor_name = fields.Char(string='vendor_name', readonly=True)
    valid_from = fields.Char(string='valid_from', readonly=True)
    valid_to = fields.Char(string='valid_to', readonly=True)
    price_control = fields.Char(string='price_control', readonly=True)
    rfq_price = fields.Char(string='rfq_price', readonly=True)
    price_unit = fields.Char(string='price_unit', readonly=True)
    currency = fields.Char(string='Currency', readonly=True)
    moq = fields.Char(string='MOQ', readonly=True)
    mpq = fields.Char(string='MPQ', readonly=True)
    tax = fields.Char(string='TAX', readonly=True)
    cw = fields.Char(string='CW', readonly=True)
    rw = fields.Char(string='RW', readonly=True)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_iac_rfq_quota_history')
        self._cr.execute("""
                create view v_iac_rfq_quota_history as
                    select irqh.id,
                           ir."name" as rfq_no,
                           irqh.action_type,
                           irqh.create_timestamp as action_date,
                           rp."name" as user_name,
                           pod.plant_code as plant,
                           mm.part_no,
                           v.vendor_code,
                           v."name" as vendor_name,
                           ir.valid_from,
                           ir.valid_to,
                           ir.price_control,
                           ir.rfq_price,
                           ir.price_unit,
                           rc."name" as currency,
                           ir.moq,
                           ir.mpq,
                           ir.tax,
                           ir.cw,
                           ir.rw
                      from iac_rfq_quote_history irqh
                      inner join iac_rfq ir on ir.id = irqh.rfq_id
                      inner join material_master mm on mm.id = ir.part_id
                      inner join iac_vendor v on v.id = ir.vendor_id
                      inner join res_users ru on ru.id = irqh.create_by
                      inner join res_partner rp on rp.id = ru.partner_id
                      inner join pur_org_data pod on pod.id = ir.plant_id
                      inner join res_currency rc on rc.id = ir.currency_id
                      order by ir."name", irqh.id
                            """)


class RfqQuotaAuditForm(models.TransientModel):
    _name = 'rfq.quota.audit.form'

    plant = fields.Many2one('pur.org.data', string='Plant Code')
    vendor = fields.Many2one('iac.vendor', string='Vendor Code')
    part_id = fields.Many2one('material.master', string='Part No')
    rfq_no = fields.Char(string='Rfq No')
    action_date_from = fields.Date(string="Action Date From")
    action_date_to = fields.Date(string="Action Date To")

    @api.multi
    def search_rfq_quota_audit(self):
        self.ensure_one()
        result = []

        for wizard in self:
            domain = []
            if wizard.plant:
                domain += [('plant', '=', wizard.plant.plant_code)]

            if wizard.vendor:
                domain += [('vendor_code', '=', wizard.vendor.vendor_code)]

            if wizard.part_id:
                domain += [('part_no', 'like', wizard.part_id.part_no)]

            if wizard.rfq_no:
                domain += [('rfq_no', 'ilike', wizard.rfq_no)]

            if wizard.action_date_from and not wizard.action_date_to:
                domain += [('valid_from', '>=', wizard.action_date_from)]

            if wizard.action_date_to and not wizard.action_date_from:
                domain += [('valid_to', '<=', wizard.action_date_to)]

            if wizard.action_date_from and wizard.action_date_to:

                if wizard.action_date_from > wizard.action_date_to:
                    raise UserError(u'查询日期格式不符合条件')

                else:
                    domain += ['&', ('valid_from', '>=', wizard.action_date_from), ('valid_to', '<=', wizard.action_date_to)]

            result = self.env['v.iac.rfq.quota.history'].search(domain)

            if not result:
                raise UserError(u'查无资料')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Info Record quota audit report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.iac.rfq.quota.history'
        }

        return action