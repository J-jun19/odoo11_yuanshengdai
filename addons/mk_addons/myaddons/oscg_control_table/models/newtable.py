# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class NewTable(models.Model):
    _name = 'iac.control.table.newtable'
    _rec_name = 'pulling_type'

    pulling_type = fields.Char()
    safety_lt = fields.Integer( string="Safety_IT")
    frequency = fields.Integer()
    frequency_pr = fields.Integer(string="Frequency_PR")