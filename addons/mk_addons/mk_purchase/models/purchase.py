# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_default_team(self):
        return self.env['purchase.team']._get_default_team_id()

    user_id = fields.Many2one('res.users', string='Purchase Person', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    team_id = fields.Many2one('purchase.team', 'Purchases Channel', change_default=True, default=_get_default_team)

    payment_ids = fields.One2many('account.payment',compute='_compute_payment', string='Payments')
    payment_amount = fields.Float(compute='_compute_payment', string='Payment Amount')
    payment_percentage = fields.Float(compute='_compute_payment', digits=(5, 2), string='Payment Percentage')

    @api.multi
    def _compute_payment(self):
        for order in self:
            payment_total = 0
            order.payment_ids = self.env['account.payment'].search([('origin', '=', order.name)])
            for payment_id in order.payment_ids:
                if payment_id.payment_type == 'outbound':
                    payment_total += payment_id.amount
                else:
                    payment_total -= payment_id.amount
            order.payment_amount = payment_total
            if order.amount_total != 0:
                order.payment_percentage = payment_total / order.amount_total * 100

    @api.multi
    def action_view_payment(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments')
        journal_id = self.env['account.journal'].search([('code', '=', 'BNK1'),('company_id', '=', self.company_id.id)])

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'default_partner_id': self.partner_id.id,
                'default_journal_id': journal_id.id,
                'default_origin': self.name,
            },
            'res_model': action.res_model,
            'domain': [('origin', '=', self.name)],
        }

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        if group_hide_product_cost:
            bypass_fields = []
            read_fields = []
            for field in fields:
                if group_hide_product_cost and field in ['amount_total', 'amount_tax', 'amount_untaxed']:
                    bypass_fields.append(field)
                else:
                    read_fields.append(field)
            result = super(PurchaseOrder, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(PurchaseOrder, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        if group_hide_product_cost:
            for field in vals.keys():
                if group_hide_product_cost and field in ['amount_total', 'amount_tax', 'amount_untaxed']:
                    raise AccessError(_("Sorry, you are not allowed to write %s field.") % field)
        result = super(PurchaseOrder, self).write(vals)
        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    user_id = fields.Many2one(related='order_id.user_id', store=True, string='Purchase Person', readonly=True)
    team_id = fields.Many2one(related='order_id.team_id', store=True, string='Purchases Channel', readonly=True)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        if group_hide_product_cost:
            bypass_fields = []
            read_fields = []
            for field in fields:
                if group_hide_product_cost and field in ['price_unit', 'price_subtotal']:
                    bypass_fields.append(field)
                else:
                    read_fields.append(field)
            result = super(PurchaseOrderLine, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(PurchaseOrderLine, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        if group_hide_product_cost:
            for field in vals.keys():
                if group_hide_product_cost and field in ['price_unit', 'price_subtotal']:
                    raise AccessError(_("Sorry, you are not allowed to write %s field.") % field)
        result = super(PurchaseOrderLine, self).write(vals)
        return result