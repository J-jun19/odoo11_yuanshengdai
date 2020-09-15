# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    state_id = fields.Many2one('res.country.state', 'Partner State', readonly=True)
    city_id = fields.Many2one('res.city', 'Partner City', readonly=True)

    def _select(self):
        select_str = ''.join([super(SaleReport, self)._select(), ', partner.state_id as state_id, partner.city_id as city_id '])
        return select_str

    def _group_by(self):
        group_by_str = ''.join([super(SaleReport, self)._group_by(), ', partner.state_id, partner.city_id '])
        return group_by_str

