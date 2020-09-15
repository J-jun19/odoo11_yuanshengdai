# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _


class TransportMove(models.Model):
    _name = 'transport.move'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')

    address_id = fields.Many2one(
        'res.partner', 'Source Address',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    address_dest_id = fields.Many2one(
        'res.partner', 'Destination Address',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    #location_id = fields.Many2one(
    #    'stock.location', "Source Location", required=True,
    #    states={'draft': [('readonly', False)]})
    #location_dest_id = fields.Many2one(
    #    'stock.location', "Destination Location", required=True,
    #    states={'draft': [('readonly', False)]})

    product_lines = fields.One2many('transport.move.product', 'transport_id')
    package_lines = fields.One2many('transport.move.package', 'transport_id')

    note = fields.Text(string='Notes')

    carrier_id = fields.Many2one('res.partner', string='Carrier')
    freight = fields.Float(string='Freight')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', copy=False, readonly=True, store=True, default='draft')

    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(self._name) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(self._name) or _('New')
        result = super(TransportMove, self).create(vals)
        return result

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})


class TransportMoveProduct(models.Model):
    _name = 'transport.move.product'

    transport_id = fields.Many2one('transport.move', string='Transport')
    picking_id = fields.Many2one('stock.picking', string='Stock Picking', required=True)
    move_id = fields.Many2one('stock.move', string='Product', required=True,
                              domain='[("picking_id", "=", picking_id)]')
    quantity = fields.Float(string='Quantity')

    @api.onchange('move_id')
    @api.multi
    def onchange_move_id(self):
        for r in self:
            r.quantity = self.move_id.product_uom_qty


class TransportMovePackage(models.Model):
    _name = 'transport.move.package'

    transport_id = fields.Many2one('transport.move', string='Transport')
    picking_id = fields.Many2one('stock.picking', string='Stock Picking', required=True)
    package_id = fields.Many2one('stock.quant.package', string='Package', required=True)

