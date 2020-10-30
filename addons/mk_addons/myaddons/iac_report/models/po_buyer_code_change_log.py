# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class PoBuyercodeChangeLog(models.Model):
    _name = "v.po.buyer.code.change.log"
    _description = "po buyer code change log"
    _auto = False
    #    _order = 'gv_code'

    plant = fields.Char(string="plant", readonly=True)
    document_erp_id = fields.Char(string="document_erp_id", readonly=True)
    ori_buyer_code = fields.Char(string="ori_buyer_code", readonly=True)
    new_buyer_code = fields.Char(string="new_buyer_code", readonly=True)
    change_on = fields.Date(string="change_on", readonly=True)
    login = fields.Char(string="login", readonly=True)
    change_by = fields.Char(string="change_by", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_po_buyer_code_change_log')
        self._cr.execute("""

            CREATE OR REPLACE VIEW public.v_po_buyer_code_change_log AS
             select  row_number() OVER () AS id,
               pod.plant_code as plant, po.document_erp_id,pclg.ori_buyer_code,pclg.new_buyer_code,pclg.change_on,ru.login,rp."name" as change_by
                from iac_purchase_order_buyer_code_change_log pclg
               inner join res_users ru on ru.id = pclg.change_by
               inner join iac_purchase_order po on po.id = pclg.order_id
               inner join res_partner rp on rp.id = ru.partner_id
               inner join pur_org_data pod on pod.id = po.plant_id
               where pclg.flag = 'SUCCESS';
                                       """)


class PoBuyercodeChangeLogWizard(models.TransientModel):
    _name = 'v.po.buyer.code.change.log.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
                                                     )], index=True)
    document_erp_id = fields.Char(string="PO number", index=True)
    ori_buyer_code = fields.Char(string="Ori buyer code", index=True)
    new_buyer_code = fields.Char(string="New buyer code", index=True)
    change_on = fields.Date(string="Change date", index=True)

    @api.multi
    def search_po_buyer_code_change_log(self):
        self.ensure_one()
        result = []

        for wizard in self:
            domain = []
            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.document_erp_id:
                domain += [('document_erp_id', '=', wizard.document_erp_id)]
            if wizard.ori_buyer_code:
                domain += [('ori_buyer_code', '=', wizard.ori_buyer_code)]
            if wizard.new_buyer_code:
                domain += [('new_buyer_code', '=', wizard.new_buyer_code)]
            if wizard.change_on:
                domain += [('change_on', '=', wizard.change_on)]

            result = self.env['v.po.buyer.code.change.log'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            # 'domain': domain,
            'name': _('po buyer code change log'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.po.buyer.code.change.log'
        }
        return action
