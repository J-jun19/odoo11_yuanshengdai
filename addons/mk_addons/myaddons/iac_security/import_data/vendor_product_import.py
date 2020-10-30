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

class IacVendorProductImport(models.TransientModel):
    _name = 'iac.vendor.product.import'
    _description = 'Vendor Product Import'

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
            int_material_group_id = False
            int_subclass_id = False

            try:
                if sheet.cell_value(index, 0):
                    domain=[('vendor_code', '=', sheet.cell_value(index, 0))]
                    object_id=self.env["iac.vendor"].search(domain,limit=1)
                    if object_id.exists():
                        int_vendor_id = object_id.id
                        int_vendor_reg_id = object_id.vendor_reg_id.id


                if int_vendor_id:
                    if sheet.cell_value(index, 2):
                        domain=[('material_group', '=', sheet.cell_value(index, 2))]
                        object_id=self.env["material.group"].search(domain,limit=1)
                        if object_id.exists():
                            int_material_group_id = object_id.id

                    if sheet.cell_value(index, 3):
                        domain=[('material_group', '=', sheet.cell_value(index, 2)),
                                                                   ('subclass', '=', sheet.cell_value(index, 3))]
                        object_id=self.env["plm.subclass"].search(domain,limit=1)
                        if object_id.exists():
                            int_subclass_id = object_id.id


                    vendor_product_vals = {
                        'vendor_reg_id': int_vendor_reg_id,
                        'vendor_id': int_vendor_id,
                        'product_name': sheet.cell_value(index, 1),
                        'product_type': int_material_group_id,
                        'product_class': int_subclass_id,
                        'brand_name': sheet.cell_value(index, 4),
                        'capacity_month': sheet.cell_value(index, 5),
                        'major_customer': sheet.cell_value(index, 6)
                    }

                    domain=[('vendor_id','=',int_vendor_id),('product_name', '=',sheet.cell_value(index, 1))]
                    object_id=self.env["iac.vendor.product"].search(domain,limit=1)
                    if not object_id.exists():
                        self.env["iac.vendor.product"].create(vendor_product_vals)
                    else:
                        object_id.write(vendor_product_vals)
                else:
                    logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
            except:
                traceback.print_exc()
                logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
            index += 1
        logging.warn(u'成功处理 %s 个vendor.product' % (index - 1))


if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.product.import')
    #model.import_xls('d:\\lwt\\vendor_data\\vendor_product.xlsx')
    ex_list=model.import_xls('C://iac//data//data_import//vendor_product.xls')