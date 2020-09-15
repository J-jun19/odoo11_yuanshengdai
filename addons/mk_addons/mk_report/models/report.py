# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

import logging
from base64 import b64decode
from contextlib import closing
from datetime import datetime
from datetime import timedelta
from io import BytesIO
import sys
import jinja2
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from ..lib import libreoffice_conversion

try:
    from docxtpl import DocxTemplate, InlineImage
except:
    pass

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
_logger = logging.getLogger(__name__)


def get_jinja_env():
    jinja_env = jinja2.Environment()

    @jinja2.contextfilter
    def picture(ctx, data, width=None, height=None, align=None):
        if data:
            data = b64decode(data)
            data = BytesIO(data)
            template = ctx['doc_template']
            return InlineImage(template, data)
        else:
            return ''

    def datetime_format(data, fmt=DEFAULT_SERVER_DATETIME_FORMAT, offset_hour=0):
        if isinstance(data, datetime):
            res = data
        else:
            res = datetime.strptime(data, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=offset_hour)
        return res.strftime(fmt)

    def date_format(data, fmt=DEFAULT_SERVER_DATE_FORMAT, offset_hour=0):
        if isinstance(data, datetime):
            res = data
        else:
            try:
                res = datetime.strptime(data, DEFAULT_SERVER_DATE_FORMAT) + timedelta(hours=offset_hour)
            except ValueError:
                res = datetime.strptime(data, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=offset_hour)
        return res.strftime(fmt)

    def chinese(value):
        rmbmap = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
        unit = ["分", "角", "元", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿",
                "拾", "佰", "仟", "万", "拾", "佰", "仟", "兆"]

        nums = list(map(int, list(str('%0.2f' % value).replace('.', ''))))
        words = []
        zflag = 0  # 标记连续0次数，以删除万字，或适时插入零字
        start = len(nums) - 3
        for i in range(start, -3, -1):  # 使i对应实际位数，负数为角分
            if 0 != nums[start - i] or len(words) == 0:
                if zflag:
                    words.append(rmbmap[0])
                    zflag = 0
                words.append(rmbmap[nums[start - i]])
                words.append(unit[i + 2])
            elif 0 == i or (0 == i % 4 and zflag < 3):  # 控制‘万/元’
                words.append(unit[i + 2])
                zflag = 0
            else:
                zflag += 1

        if words[-1] != unit[0]:  # 结尾非‘分’补整字
            words.append("整")
        res = ''.join(words)
        if sys.version_info[0] == 3:
            return res
        else:
            return res.decode('utf-8')

    jinja_env.filters['picture'] = picture
    jinja_env.filters['datetime'] = datetime_format
    jinja_env.filters['date'] = date_format
    jinja_env.filters['chinese'] = chinese
    return jinja_env


class IrActionReportDocx(models.Model):
    _inherit = 'ir.actions.report'

    # report_type = fields.Selection(selection_add=[("docx", "DOCX")], copy=False)
    docx_engine = fields.Boolean('DOCX Engine')
    docx_template = fields.Binary('DOCX Template')
    docx_convert = fields.Selection([("pdf", "PDF")], string='DOCX Convert')

    @api.multi
    def download_docx_template(self):
        self.ensure_one()
        url = None
        if self.model == 'sale.order':
            url = '/mk_report/static/sale.order.docx'
        if url:
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }

    @api.one
    @api.constrains('report_name')
    def _check_report_name(self):
        if len(self.env[self._name].search([('report_name', '=', self.report_name), ('id', '!=', self.id)])) > 0:
            raise ValidationError(_('The report name of the report must be unique !'))


class Report(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _render_docx(self, docx_template, data):
        out = BytesIO()
        with closing(out):
            template = b64decode(docx_template)
            template = BytesIO(template)
            doc = DocxTemplate(template)
            data['doc_template'] = doc
            jinja_env = get_jinja_env()
            doc.render(data, jinja_env)
            doc.save(out)
            content = out.getvalue()
        return content

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        report, docids = self, res_ids
        if report.docx_engine:
            docs = self.env[report.model].browse(docids)
            data = {
                'doc_ids': docids,
                'doc_model': report.model,
                'docs': docs,
                'doc': docs[0],
                'now': datetime.now()
            }

            content = self._render_docx(report.docx_template, data)
            if report.docx_convert:
                content = libreoffice_conversion.convert_from_content(content, 'docx', output_type=report.docx_convert)
        else:
            content, content_type = super(Report, self).render_qweb_pdf(res_ids, data)
        return content, 'pdf'
