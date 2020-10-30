# -*- coding: utf-8 -*-
import json
import xlwt
import time,base64
import datetime
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
from odoo import models, fields, api
import psycopg2
import logging
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
import pdb

logger = logging.getLogger(__name__)

class LzDianCai(models.Model):

    _name = 'lz.dian.cai.model'

    plant = fields.Char()
    holiday = fields.Date()