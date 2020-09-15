# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _


class PurchaseTransport(models.Model):
    _name = 'purchase.transport.status'

    name = fields.Char('Name')


class PurchaseTransport(models.Model):
    _name = 'purchase.transport'
    _description = 'Purchase Transport'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')

    status_lines = fields.One2many('purchase.transport.line', 'transport_id')

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

    origin = fields.Char('Source Document', copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    self._name) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(self._name) or _('New')
        result = super(PurchaseTransport, self).create(vals)
        return result

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})


class PurchaseTransportLine(models.Model):
    _name = 'purchase.transport.line'

    transport_id = fields.Many2one('purchase.transport', string='Transport')
    date = fields.Date(string='Date')
    status_id = fields.Many2one('purchase.transport.status', string='Status', required=True)
    note = fields.Text(string='Notes')

