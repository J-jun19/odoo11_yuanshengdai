# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields
from odoo.tools import safe_eval


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char('Name')

    transport_count = fields.Integer(compute="_compute_transport", string='# Transports', copy=False, default=0)
    transport_done_count = fields.Integer(compute="_compute_transport", string='# Done Transports', copy=False, default=0)
    transport_ids = fields.Many2many('transport.move', compute='_compute_transport', string='Transports', copy=False)

    @api.multi
    def action_view_transport(self):
        self.ensure_one()
        action = self.env.ref('mk_transport.action_transport_view').read()[0]
        res = self.transport_ids
        action['domain'] = [('id', 'in', res.ids)]
        action_context = safe_eval(action['context']) if action['context'] else {}
        action_context.update({
            #'default_location_id': self.location_id.id,
            #'default_location_dest_id': self.location_dest_id.id,
            'default_picking_id': self.id,
        })
        if self.picking_type_code == 'incoming':
            action_context['default_partner_id'] = self.partner_id.id
            action_context['default_partner_dest_id'] = self.company_id.partner_id.id
        elif self.picking_type_code == 'outgoing':
            action_context['default_partner_id'] = self.company_id.partner_id.id
            action_context['default_partner_dest_id'] = self.partner_id.id
        action['context'] = action_context
        return action

    @api.multi
    @api.depends('transport_ids.state')
    def _compute_transport(self):
        for r in self:
            transport_ids = []
            data = self.env['transport.move.product'].search([('picking_id', 'in', self.ids)]).read(['transport_id'])
            transport_ids += [item['transport_id'][0] for item in data]
            data = self.env['transport.move.package'].search([('picking_id', 'in', self.ids)]).read(['transport_id'])
            transport_ids += [item['transport_id'][0] for item in data]
            transport_ids = list(set(transport_ids))
            r.transport_ids = self.env['transport.move'].browse(transport_ids)
            for transport_id in r.transport_ids:
                if transport_id.state != 'cancel':
                    r.transport_count += 1
                if transport_id.state == 'done':
                    r.transport_done_count += 1


