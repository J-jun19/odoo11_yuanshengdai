# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _
from odoo.exceptions import AccessError, ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_ids = fields.One2many('account.payment', compute='_compute_payment', string='Collections')
    payment_amount = fields.Float(compute='_compute_payment', string='Collection Amount')
    payment_percentage = fields.Float(compute='_compute_payment', digits=(5, 2), string='Collection Percentage')
    note_attachment = fields.Text('Notes for attachment')

    @api.multi
    def _compute_payment(self):
        for order in self:
            payment_total = 0
            order.payment_ids = self.env['account.payment'].search([('origin', '=', order.name)])
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
        journal_id = self.env['account.journal'].search(
            [('code', '=', 'BNK1'), ('company_id', '=', self.company_id.id)])

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
                # 'default_sale_order_id': self.id,
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
            result = super(SaleOrder, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(SaleOrder, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_cost')
        if group_hide_product_cost:
            for field in vals.keys():
                if group_hide_product_cost and field in ['amount_total', 'amount_tax', 'amount_untaxed']:
                    raise AccessError(_("Sorry, you are not allowed to write %s field.") % field)
        result = super(SaleOrder, self).write(vals)
        return result

    purchase_picking_count = fields.Integer(compute='_compute_purchase_picking', string='Purchase Receptions',
                                            default=0)
    purchase_picking_ids = fields.Many2many('stock.picking', compute='_compute_purchase_picking',
                                            string='Purchase Receptions', copy=False)

    def _compute_purchase_picking(self):
        for r in self:
            purchase_ids = self.env['purchase.order'].search([('origin', '=', r.name)])
            pickings = purchase_ids.mapped('picking_ids')
            r.picking_ids = pickings
            r.picking_count = len(pickings)

    @api.multi
    def action_view_purchase_picking(self):
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]
        result['context'] = {}
        pick_ids = self.mapped('purchase_picking_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    to_approve = fields.Integer(string='To Approve', copy=False, readonly=True)

    @api.multi
    def _get_to_approve(self):
        if self.company_id.so_multiple_validation == 'three_step' and self.amount_total >= self.env.user.company_id.currency_id.compute(
                self.company_id.so_multiple_validation_two_step_amount, self.currency_id):
            return 2
        elif self.company_id.so_multiple_validation == 'two_step' and self.amount_total >= self.env.user.company_id.currency_id.compute(
                self.company_id.so_multiple_validation_one_step_amount, self.currency_id):
            return 1
        else:
            return 0

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        order.write({'to_approve': order._get_to_approve()})
        return order

    @api.multi
    def action_approve(self):
        for order in self:
            group_xmlid = self.env['ir.model.data'].object_to_xmlid(self.company_id.so_multiple_validation_two_step_group)
            if order.to_approve == 2 and order.state in ['draft', 'sent'] and order.user_has_groups(group_xmlid):
                order.write({'to_approve': 1})
                return
            group_xmlid = self.env['ir.model.data'].object_to_xmlid(self.company_id.so_multiple_validation_one_step_group)
            if order.to_approve == 1 and order.state in ['draft', 'sent'] and order.user_has_groups(group_xmlid):
                order.write({'to_approve': 0})
                return
            raise ValidationError(_('No need to approve'))

    @api.multi
    def action_confirm(self):
        for order in self:
            if order.to_approve:
                raise ValidationError(_('Managers must approve orders'))
            else:
                return super(SaleOrder, order).action_confirm()

    @api.multi
    def action_cancel(self):
        self.write({'to_approve': 0})
        return super(SaleOrder, self).action_cancel()

    @api.multi
    def action_draft(self):
        self.write({'to_approve': self._get_to_approve()})
        return super(SaleOrder, self).action_draft()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    notes = fields.Char('Notes')

    @api.multi
    def action_view_product_sales(self):
        self.ensure_one()
        action = self.env.ref('sale.action_product_sale_list')
        product_ids = self.with_context(active_test=False).product_id.ids
        partner_id = self.env.context.get('partner_id') or self.order_id.partner_id.id

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': 'new',
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']), ('product_id', 'in', product_ids),
                       ('order_id.partner_id', '=', partner_id)],
        }

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost:
            bypass_fields = []
            read_fields = []
            for field in fields:
                if group_hide_product_cost and field in ['price_unit', 'price_subtotal']:
                    bypass_fields.append(field)
                else:
                    read_fields.append(field)
            result = super(SaleOrderLine, self).read(read_fields, load=load)
            for row in result:
                for bypass_field in bypass_fields:
                    row[bypass_field] = False
        else:
            result = super(SaleOrderLine, self).read(fields, load=load)
        return result

    @api.multi
    def write(self, vals):
        group_hide_product_cost = self.env.user.has_group('mk_base.group_hide_product_price')
        if group_hide_product_cost:
            for field in vals.keys():
                if group_hide_product_cost and field in ['price_unit', 'price_subtotal']:
                    raise AccessError(_("Sorry, you are not allowed to write %s field.") % field)
        result = super(SaleOrderLine, self).write(vals)
        return result
