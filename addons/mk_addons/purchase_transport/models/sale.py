# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_transport_count = fields.Integer(compute="_compute_purchase_transport", string='# Purchase Transports', copy=False, default=0)
    purchase_transport_done_count = fields.Integer(compute="_compute_purchase_transport", string='# Purchase Done Transports', copy=False,
                                          default=0)
    purchase_transport_ids = fields.Many2many('purchase.transport', compute='_compute_purchase_transport', string='Purchase Transports', copy=False)

    @api.multi
    def action_view_purchase_transport(self):
        self.ensure_one()
        action = self.env.ref('purchase_transport.action_purchase_transport_view').read()[0]
        res = self.purchase_transport_ids
        action['domain'] = [('id', 'in', res.ids)]
        return action

    @api.multi
    @api.depends('purchase_transport_ids.state')
    def _compute_purchase_transport(self):
        for r in self:
            purchase_ids = self.env['purchase.order'].search([('origin', '=', r.name)])
            r.purchase_transport_ids = purchase_ids.mapped('purchase_transport_id')
            for purchase_transport_id in r.purchase_transport_ids:
                if purchase_transport_id.state != 'cancel':
                    r.purchase_transport_count += 1
                if purchase_transport_id.state == 'done':
                    r.purchase_transport_done_count += 1