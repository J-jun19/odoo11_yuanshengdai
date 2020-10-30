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

class IacSupplierCompanyImport(models.TransientModel):
    _name = 'iac.supplier.company.import'
    _description = 'Supplier Company Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        ex_list=[]
        while index <= sheet.nrows - 1:
            logging.warn(u'处理第%s个' % (index))
            int_vendor_ids = []
            if sheet.cell_value(index, 5):
                for item in sheet.cell_value(index, 5).split('|'):
                    domain=[('vendor_code', '=', item)]
                    object_id=self.env['iac.vendor'].search(domain,limit=1)
                    if object_id.exists():
                        int_vendor_ids.append(object_id.id)
                    else:
                        logging.error(u'vendor code %s 不存在' % (item,))
                        ex_list.append(u'vendor code %s 不存在' % (item))

            if int_vendor_ids:
                try:
                    supplier_company_vals = {
                        'company_no': sheet.cell_value(index, 0),
                        'name': sheet.cell_value(index, 1),
                        'company_name2': sheet.cell_value(index, 2),
                        'vat_no': sheet.cell_value(index, 3),
                        'supplier_type': sheet.cell_value(index, 4).strip()
                    }

                    domain=[('company_no', '=',  sheet.cell_value(index, 0))]
                    supplier_company_id=self.env['iac.supplier.company'].search(domain,limit=1)
                    if not supplier_company_id.exists():
                        supplier_company_id = self.env['iac.supplier.company'].create(supplier_company_vals)

                    for int_vendor_id in int_vendor_ids:
                        supplier_company_line_vals = {
                            'supplier_company_id': supplier_company_id.id,
                            'vendor_id':int_vendor_id
                        }
                        self.env['iac.supplier.company.line'].create(supplier_company_line_vals)
                        vendor_rec=self.env['iac.vendor'].browse(int_vendor_id)
                        vendor_rec.write({"is_bind":True})
                        self.env.cr.commit()
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，company_no=%s' % (index, sheet.cell_value(index, 0)))
                    ex_list.append(u'No.%s 行异常，company_no=%s' % (index, sheet.cell_value(index, 0)))
            else:
                logging.warn(u'No.%s 行异常，vendor code都不存在，跳过，company_no=%s' % (index, sheet.cell_value(index, 0)))
            index += 1
        logging.warn(u'成功创建 %s 个supplier.company' % (index - 1))
        logging.error(ex_list)
        return ex_list



if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.supplier.company.import')
    #model.import_xls('d:\\lwt\\vendor_data\\supplier_company.xls')
    ex_list=model.import_xls('C://iac//data//data_import//supplier_company.xls')
    print ex_list