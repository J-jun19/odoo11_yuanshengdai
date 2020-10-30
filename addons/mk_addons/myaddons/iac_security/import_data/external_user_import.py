# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
import xlrd
import erppeek
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)
"""
导入外部user
"""

class IacUserExternalImport(models.TransientModel):
    _name = 'iac.user.external.import'
    _description = 'User External Import'

    @api.model
    def import_xls(self,xls_path):
        try:
            workbook = xlrd.open_workbook(xls_path)
            sheet = workbook.sheet_by_index(0)
            self.import_xls_sheet(sheet,1,sheet.nrows-1)
        except:
            traceback.print_exc()


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        while index <=end and index <= sheet.nrows - 1:
            exists_user_id=self.env["res.users"].search([('login', '=', sheet.cell_value(index, 1))])
            if not exists_user_id.exists():
                group_id=self.env.ref('oscg_vendor.IAC_vendor_groups')
                groups_ids=[]
                groups_ids.append((4,group_id.id))
                user_vals = {
                    'name': sheet.cell_value(index, 0),
                    'login': sheet.cell_value(index, 1),
                    'password': sheet.cell_value(index, 2),
                    'share': True,
                    'groups_id': groups_ids
                }
                try:
                    exists_user_id = self.env["res.users"].create(user_vals)
                    self.env.cr.commit()
                    partner_vals = {
                        'email': sheet.cell_value(index, 3),
                        'supplier': True
                    }
                    exists_user_id.partner_id.write(partner_vals)
                    self.env.cr.commit()
                    logging.warn(u'第 %s 个user，处理 %s 成功.user_id=%s' % (index, exists_user_id.name, exists_user_id.id))
                except:
                    traceback.print_exc()
                    logging.error(u'第 %s 个user出现异常' % (index,))
                    logging.error(traceback.format_exc())
                    raise u'第 %s 个user出现异常' % (index,)

            else:
                user_vals = {
                    'password': sheet.cell_value(index, 2)
                }
                exists_user_id.write(user_vals)
                self.env.cr.commit()
                logging.warn(u'第 %s 个user %s %s 已经存在，跳过不再创建。user_id=%s' % (index, exists_user_id.login, exists_user_id.name, exists_user_id.id))
            index += 1
        logging.warn(u'需处理 %s 个user' % (index - 1))

if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.user.external.import')
    #model.import_xls('d:/lwt/vendor_data/external_user.xls')
    model.import_xls('C:/iac/data/data_import/external_user.xls')