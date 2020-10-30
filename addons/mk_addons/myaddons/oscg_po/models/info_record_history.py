# -*- coding: utf-8 -*-
import threading
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from rule_parser import RuleParser
import odoo.addons.decimal_precision as dp
import traceback, logging, types,json

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval as eval
from odoo.modules.registry import RegistryManager
import odoo
_logger = logging.getLogger(__name__)


class InforecordHistory(models.Model):
    _inherit = "inforecord.history"
    currency_id = fields.Many2one('res.currency', string="Currency Info")
    @api.model
    def get_last_price_rec(self,vendor_id,part_id):
        """
        指定vendor_id和part_id获取info_record_history的定价记录
        :param vendor_id:
        :param part_id:
        :return:
        """

        op_date=fields.date.today()
        domain=[('vendor_id','=',vendor_id)]
        domain+=[('part_id','=',part_id)]
        domain+=[('valid_from','<=',op_date)]
        domain+=[('valid_to','>=',op_date)]
        result=self.env["inforecord.history"].search(domain,limit=1,order="valid_from desc")
        return result