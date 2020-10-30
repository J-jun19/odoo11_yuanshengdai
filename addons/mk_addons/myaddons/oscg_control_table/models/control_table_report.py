# -*- coding: utf-8 -*-

import json
import xlwt
import time, base64
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

_logger = logging.getLogger(__name__)


class IacControlTableReportWizard(models.TransientModel):
    """mm下载rfq,选择查询条件进行下载：
    """
    _name = 'iac.control.table.report.wizard'

    message = fields.Char(string=u'是否下載模版？' ,readonly=True)
    @api.multi
    def action_confirm_download(self):
        """
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """
        header_field_list = []
        header_field_list = ['plant_code', 'vendor_code', 'pulling_type', 'trans_lt','eta_trans','reason']

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)

        for i in range(0, 6):
            sheet1.write(0, i, header_field_list[i])  # 灰底,黑字


        wb2.save(output)

        # 文件输出成功之后,跳转链接，浏览器下载文件
        vals = {
            'name': 'control_table_report',
            'datas_fname': 'control_table_report.xls',
            'description': 'Control Table Report',
            'type': 'binary',
            'db_datas': base64.encodestring(output.getvalue()),
        }
        file = self.env['ir.attachment'].create(vals)
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s.xls' % (file.id, file.id,),
            'target': 'new',
        }

        return action