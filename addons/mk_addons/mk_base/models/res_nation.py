# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResNation(models.Model):
    _name = 'res.nation'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')

