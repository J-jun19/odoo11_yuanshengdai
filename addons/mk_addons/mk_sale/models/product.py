# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    notes = fields.Char('备注')

    payment_ids = fields.One2many('account.payment', compute='_compute_payment', string='收款')
    payment_amount = fields.Float(compute='_compute_payment', string='收款金额')
    payment_percentage = fields.Float(compute='_compute_payment', digits=(5, 2), string='收款百分比')

    @api.multi
    def _compute_payment(self):
        for order in self:
            payment_total = 0
            order.payment_ids = self.env['account.payment'].search([('origin','=',order.name)])
            for payment_id in order.payment_ids:
                if payment_id.payment_type == 'inbound':
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
        journal_id = self.env['account.journal'].search([('code', '=', 'BNK1'), ('company_id','=',self.company_id.id)])

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
                'default_partner_id': self.partner_id.id,
                'default_journal_id': journal_id.id,
                #'default_sale_order_id': self.id,
                'default_origin': self.name,
            },
            'res_model': action.res_model,
            'domain': [('origin', '=', self.name)],
        }

