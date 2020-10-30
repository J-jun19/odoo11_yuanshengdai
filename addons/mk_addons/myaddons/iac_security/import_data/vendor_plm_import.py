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
导入supplier_company,包含supplier_company包含vendor 的信息
"""

class IacVendorPlmImport(models.TransientModel):
    _name = 'iac.vendor.plm.import'
    _description = 'Vendor Plm Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        while index <= sheet.nrows - 1:
            logging.warn(u'处理第%s个' % (index))

            int_global_vendor_id = False

            if sheet.cell_value(index, 1):
                domain=[('global_vendor_code', '=', sheet.cell_value(index, 1))]
                object_id=self.env["iac.global.vendor"].search(domain,limit=1)
                if object_id.exists():
                    int_global_vendor_id = object_id.id
                    object_id.write({"is_used":True})
                else:
                    logging.error('global_vendor_code not exists:%s' % (sheet.cell_value(index, 1)))


            if int_global_vendor_id:
                try:
                    vendor_plm_vals = {
                        'name': sheet.cell_value(index, 0),
                        'global_vendor_id': int_global_vendor_id,
                        'state': 'done'
                    }
                    domain=[('name','=',sheet.cell_value(index, 0))]
                    vendor_plm_rec=self.env["iac.vendor.plm"].search(domain)
                    if not vendor_plm_rec.exists():
                        vendor_plm_rec=self.env["iac.vendor.plm"].create(vendor_plm_vals)
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，global_vendor_code=%s' % (index, sheet.cell_value(index, 1)))
            else:
                logging.warn(u'No.%s 行异常，global vendor不存在，跳过，global_vendor_code=%s' % (index, sheet.cell_value(index, 1)))

            index += 1

        logging.warn(u'成功创建 %s 个vendor.plm' % (index - 1))


if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.plm.import')
    #model.import_xls('d:\\lwt\\vendor_data\\vendor_plm.xlsx')
    ex_list=model.import_xls('C://iac//data//data_import//vendor_plm.xls')