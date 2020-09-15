# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_transport_id = fields.Many2one('purchase.transport', string='Transport')


