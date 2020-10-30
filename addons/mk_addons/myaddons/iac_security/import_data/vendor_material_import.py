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

class IacVendorMaterialImport(models.TransientModel):
    _name = 'iac.vendor.material.import'
    _description = 'Vendor Material Import'

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
            int_division_id = False
            int_material_group_id = False

            try:
                if sheet.cell_value(index, 0):
                    domain=[('vendor_code', '=', sheet.cell_value(index, 0))]
                    object_id=self.env['iac.vendor'].search(domain,limit=1)
                    if object_id.exists():
                        int_vendor_id = object_id.id
                        int_vendor_reg_id = object_id.vendor_reg_id.id


                if int_vendor_id:
                    if sheet.cell_value(index, 1):
                        domain=[('division', '=', sheet.cell_value(index, 1))]
                        object_id=self.env['division.code'].search(domain,limit=1)
                        if object_id.exists():
                            int_division_id = object_id.id


                    if sheet.cell_value(index, 3):
                        domain=[('material_group', '=', sheet.cell_value(index, 3))]
                        object_id=self.env['material.group'].search(domain,limit=1)
                        if object_id.exists():
                            int_material_group_id = object_id.id                                                  

                    vendor_material_vals = {
                        'vendor_reg_id': int_vendor_reg_id,
                        'vendor_id': int_vendor_id,
                        'division_code': int_division_id,
                        'project': sheet.cell_value(index, 2),
                        'material_group': int_material_group_id
                    }
                    domain=[('material_group', '=', int_material_group_id),('vendor_id','=',int_vendor_id)]
                    vendor_material=self.env['iac.vendor.material'].search(domain,limit=1)
                    if not vendor_material.exists():
                        vendor_material=self.env["iac.vendor.material"].create(vendor_material_vals)
                    else:
                        vendor_material.write(vendor_material_vals)
                else:
                    logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
            except:
                traceback.print_exc()
                logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))

            index += 1

        logging.warn(u'成功处理 %s 个vendor.material' % (index - 1))


if __name__=="__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.material.import')
    #model.import_xls('d:\\lwt\\vendor_data\\vendor_material.xlsx')
    ex_list=model.import_xls('C://iac//data//data_import//vendor_material.xls')