# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

import json
import logging

from odoo import http
from odoo.addons.web.controllers.main import ReportController
from odoo.http import request, serialize_exception as _serialize_exception
from odoo.tools import html_escape

_logger = logging.getLogger(__name__)


class DocxReportController(ReportController):

    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'pdf':
            context = dict(request.env.context)
            report = request.env['ir.actions.report']._get_report_from_name(reportname)
            if report.docx_engine and not report.docx_convert:
                docids = [int(i) for i in docids.split(',')]
                docx = report.with_context(context).render_qweb_pdf(docids, data=data)[0]
                docxhttpheaders = [('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'), ('Content-Length', len(docx))]
                return request.make_response(docx, headers=docxhttpheaders)
            else:
                return super(DocxReportController, self).report_routes(reportname, docids, converter, **data)
        else:
            return super(DocxReportController, self).report_routes(reportname,docids,converter, **data)

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        try:
            response = super(DocxReportController, self).report_download(data, token)
            if response.headers.get('Content-type') == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                response.headers.set('Content-Disposition', response.headers.get('Content-Disposition')[:-3] + 'docx')
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
