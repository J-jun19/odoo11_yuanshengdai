# -*- coding: utf-8 -*-

from odoo import models,fields


class AbolishedPartCategroy(models.Model):

    _name = 'abolished.part.categroy.storage'

    material_group = fields.Char(string='material_group')
    description = fields.Char(string='description')