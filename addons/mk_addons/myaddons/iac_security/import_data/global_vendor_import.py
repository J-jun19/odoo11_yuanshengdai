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

class IacGlobalVendorImport(models.TransientModel):
    _name = 'iac.global.vendor.import'
    _description = 'Global Vendor Import'

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

            int_supplier_company_ids = []

            if sheet.cell_value(index, 5):
                for item in sheet.cell_value(index, 5).split('|'):
                    domain=[('company_no', '=', item)]
                    object_id= self.env['iac.supplier.company'].search(domain,order='id desc',limit=1)
                    if object_id:
                        int_supplier_company_ids.append(object_id.id)
                    else:
                        logging.error(u'company_no %s 不存在' % (item))

            if int_supplier_company_ids:
                try:
                    line_ids = []
                    for int_supplier_company_id in int_supplier_company_ids:

                        object_id= self.env['iac.supplier.company'].browse(int_supplier_company_id)
                        global_vendor_line_vals = {
                            'supplier_company_id': object_id.id
                        }
                        line_ids.append((0,0,global_vendor_line_vals))
                        object_id.write({"is_bind":True})

                    global_vendor_vals = {
                        'global_vendor_code': sheet.cell_value(index, 0),
                        'name': sheet.cell_value(index, 1),
                        'global_name2': sheet.cell_value(index, 2),
                        'global_address': sheet.cell_value(index, 3),
                        'global_address2': sheet.cell_value(index, 4),
                        'line_ids': line_ids
                    }

                    domain=['|',('global_vendor_code', '=', sheet.cell_value(index, 0)),('name','=',sheet.cell_value(index, 1))]
                    global_vendor_id= self.env['iac.global.vendor'].search(domain,limit=1)
                    if not global_vendor_id.exists():
                        global_vendor_id=self.env["iac.global.vendor"].create(global_vendor_vals)
                    else:
                        global_vendor_id.write(global_vendor_vals)
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，global_vendor_code=%s' % (index, sheet.cell_value(index, 0)))
                    raise u'No.%s 行异常，global_vendor_code=%s' % (index, sheet.cell_value(index, 0))
            else:
                logging.warn(u'No.%s 行异常，supplier company都不存在，跳过，global_vendor_code=%s' % (index, sheet.cell_value(index, 0)))

            index += 1

        logging.warn(u'成功创建 %s 个global.vendor' % (index - 1))



if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.global.vendor.import')
    #model.import_xls('d:\\lwt\\vendor_data\\global_vendor.xls')
    model.import_xls('C://iac//data//data_import//global_vendor.xls')