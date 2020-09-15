# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    #sale_order_id = fields.Many2one('sale.order', string='销售订单')
