# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    so_multiple_validation = fields.Selection([
        ('one_step', 'Confirm sale orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a sale order'),
        ('three_step', 'Get 3 levels of approvals to confirm a sale order')
    ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for sales")

    so_multiple_validation_one_step_amount = fields.Monetary(string='Single validation amount', default=5000,
                                                  help="Minimum amount for which a single validation is required")
    so_multiple_validation_one_step_group = fields.Many2one('res.groups', string='Single validation group', default=lambda self: self.env.ref('sales_team.group_sale_manager'))

    so_multiple_validation_two_step_amount = fields.Monetary(string='Double validation amount', default=25000,
                                                  help="Minimum amount for which a double validation is required")
    so_multiple_validation_two_step_group = fields.Many2one('res.groups', string='Double validation group', default=lambda self: self.env.ref('sales_team.group_sale_manager'))