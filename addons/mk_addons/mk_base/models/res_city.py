# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CityDistrict(models.Model):
    _name = "res.city.district"
    _description = "District"
    _order = 'code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    zipcode = fields.Char(string='Zip')
    city_id = fields.Many2one('res.city', string="City", required=True)
