# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_multiple_validation = fields.Selection(related='company_id.so_multiple_validation',
                                              string="Levels of Approvals *")
    so_multiple_validation_one_step_amount = fields.Monetary(
        related='company_id.so_multiple_validation_one_step_amount', string="Single validation amount",
        currency_field='company_currency_id')
    so_multiple_validation_one_step_group = fields.Many2one('res.groups',
                                                              related='company_id.so_multiple_validation_one_step_group',
                                                              string='Single validation group')
    so_multiple_validation_two_step_amount = fields.Monetary(
        related='company_id.so_multiple_validation_two_step_amount', string="Double validation amount",
        currency_field='company_currency_id')
    so_multiple_validation_two_step_group = fields.Many2one('res.groups',
                                                            related='company_id.so_multiple_validation_two_step_group',
                                                            string='Double validation group')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
                                          help='Utility field to express amount currency')
