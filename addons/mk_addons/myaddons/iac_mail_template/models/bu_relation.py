# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request
import datetime

class TMJKBURelation(models.Model):

    _name = 'iac.tmjkburelation'

    division = fields.Char()
    division_id = fields.Many2one('division.code')
    description = fields.Char()
    budes = fields.Char()
    buid = fields.Integer()
    buname = fields.Char()
    logonid = fields.Char()
    name = fields.Char()
    validflag = fields.Char()
    cdt = fields.Datetime()
    bugroup = fields.Char()

class TGroupUserInfo(models.Model):

    _name = 'iac.tgroupuserinfo'

    levelname = fields.Char()
    plant = fields.Char()
    plant_id = fields.Many2one('pur.org.data')
    site = fields.Char()
    divisioncode = fields.Char()
    division_id = fields.Many2one('division.code')
    divisionname = fields.Char()
    ntaccount = fields.Char()
    modifyuser = fields.Char()
    cdt = fields.Datetime()

class BgDivisionInfo(models.Model):

    _name = 'iac.bg.division.info'

    plant = fields.Char()
    plant_id = fields.Many2one('pur.org.data')
    bg_id = fields.Char()
    bg = fields.Char()
    bu_id = fields.Char()
    bu = fields.Char()
    division = fields.Char()
    division_id = fields.Many2one('division.code')
    division_name = fields.Char()
    div_type = fields.Char()
    cdt = fields.Datetime()

#
# class BgDivisionInfo(models.model):
#
#     _name = 'iac.bg.division.info'
#     plant = fields.Char()
#     plant_id = fields.Many2one('pur.org.data')
#     bg_id = fields.Char()
#     bg = fields.Char()
#     bu_id = fields.Char()
#     bu = fields.Char()
#     division = fields.Char()
#     division_id = fields.Many2one('division.code')
#     division_name = fields.Char()
#     div_type = fields.Char()
#     cdt = fields.Datetime()