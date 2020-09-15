# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_count = fields.Integer(compute="_compute_sale", string='# of Sale Order', copy=False, default=0)
    sale_ids = fields.One2many('sale.order', compute="_compute_sale", string='Sales', copy=False)

    @api.multi
    def action_view_sale(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        res = self.sale_ids
        action['domain'] = [('id', 'in', res.ids)]
        return action

    @api.depends('origin')
    def _compute_sale(self):
        for r in self:
            res_ids = self.env['sale.order'].search([('name', '=', r.origin), ('state', '!=', 'cancel')])
            r.sale_ids = res_ids
            r.sale_count = len(res_ids)
