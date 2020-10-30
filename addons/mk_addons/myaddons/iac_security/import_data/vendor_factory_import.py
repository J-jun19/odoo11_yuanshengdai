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

class IacVendorFactoryImport(models.TransientModel):
    _name = 'iac.vendor.factory.import'
    _description = 'Vendor Factory Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        while index <= sheet.nrows - 1:
            int_vendor_id = False
            int_vendor_reg_id = False

            try:
                if sheet.cell_value(index, 0):
                    domain=[('vendor_code', '=', sheet.cell_value(index, 0))]
                    object_id=self.env['iac.vendor'].search(domain,limit=1)
                    if object_id.exists():
                        int_vendor_id = object_id.id
                        int_vendor_reg_id = object_id.vendor_reg_id.id

                if int_vendor_id:
                    vendor_factory_vals = {
                        'vendor_reg_id': int_vendor_reg_id,
                        'vendor_id': int_vendor_id,
                        'factory_type': sheet.cell_value(index, 1),
                        'factory_name': sheet.cell_value(index, 2),
                        'factory_location': sheet.cell_value(index, 3),
                        'factory_address': sheet.cell_value(index, 4),
                        'main_flag': sheet.cell_value(index, 5),
                        'ur_flag': sheet.cell_value(index, 6),
                        'relation': sheet.cell_value(index, 7),
                        'qa_contact': sheet.cell_value(index, 8),
                        'qa_tel': sheet.cell_value(index, 9),
                        'qa_email': sheet.cell_value(index, 10)
                    }

                    domain=[('vendor_id','=',int_vendor_id),('factory_name','=',sheet.cell_value(index, 2))]
                    vendor_factory=self.env['iac.vendor.factory'].search(domain)
                    if not vendor_factory.exists():
                        vendor_factory=self.env["iac.vendor.factory"].create(vendor_factory_vals)
                    vendor_factory.write(vendor_factory_vals)
                else:
                    logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
            except:
                traceback.print_exc()
                logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))

            index += 1

        logging.warn(u'成功处理 %s 个vendor.factory' % (index - 1))


if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.factory.import')
    #model.import_xls('d:\\lwt\\vendor_data\\vendor_factory.xlsx')
    ex_list=model.import_xls('C://iac//data//data_import//vendor_factory.xlsx')