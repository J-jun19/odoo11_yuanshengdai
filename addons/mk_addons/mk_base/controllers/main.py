# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.main import CSVExport, ExcelExport, serialize_exception, DataSet, Database

_logger = logging.getLogger(__name__)


class CSVExportExtend(CSVExport):

    @http.route('/web/export/csv', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        if http.request.env.user.has_group('mk_base.group_disable_export'):
            raise AccessError(_("Sorry, you are not allowed to export this document."))
        else:
            return super(CSVExportExtend, self).index(data, token)


class ExcelExportExtend(ExcelExport):

    @http.route('/web/export/xls', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        if http.request.env.user.has_group('mk_base.group_disable_export'):
            raise AccessError(_("Sorry, you are not allowed to export this document."))
        else:
            return super(ExcelExportExtend, self).index(data, token)


class DataSetExtend(DataSet):

    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        if model == 'res.partner' and method == 'get_formview_action' and http.request.env.user.has_group(
                'mk_base.group_disable_open_partner'):
            raise AccessError(_("Sorry, you are not allowed to open this document."))
        else:
            return super(DataSetExtend, self).call_kw(model, method, args, kwargs, path)


class DatabaseExtend(Database):

    @http.route('/web/database/backup', type='http', auth="none", methods=['POST'], csrf=False)
    def dep_backup(self, master_pwd, name, backup_format='zip'):
        response = super(DatabaseExtend, self).backup(master_pwd, name, backup_format)
        if backup_format != 'zip':
            response.headers.set('Content-Disposition', response.headers.get('Content-Disposition')[:-4] + 'zip')
        return response
