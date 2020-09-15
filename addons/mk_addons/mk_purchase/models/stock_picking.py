# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields, _
from odoo.tools import safe_eval


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_count = fields.Integer(compute="_compute_purchase", string='# of Purchase Order', copy=False, default=0)
    purchase_ids = fields.Many2many('purchase.order', compute="_compute_purchase", string='Purchases', copy=False)

    @api.multi
    def action_view_purchase(self):
        self.ensure_one()
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        res = self.purchase_ids
        action['domain'] = [('id', 'in', res.ids)]
        return action

    @api.depends('origin')
    def _compute_purchase(self):
        for r in self:
            res_ids = self.env['purchase.order'].search([('name', '=', r.origin), ('state', '!=', 'cancel')])
            r.purchase_ids = res_ids
            r.purchase_count = len(res_ids)
