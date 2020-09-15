# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _
from odoo.exceptions import AccessError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_team_id = fields.Many2one(
        'purchase.team', 'Purchases Channel',
        help='If set, this purchases channel will be used for purchases and assignations related to this partner')