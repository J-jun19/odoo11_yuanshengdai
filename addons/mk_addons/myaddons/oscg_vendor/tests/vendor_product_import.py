# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging
import traceback

"""
导入vendor数据
"""

if __name__=="__main__":
    api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'iacadmin')

    workbook = xlrd.open_workbook('d:\\lwt\\vendor_data\\vendor_product.xls')
    sheet = workbook.sheet_by_index(0)

    logging.warn(u'需处理 %s 个vendor.product' % (sheet.nrows - 1))

    # 执行导入数据
    index = 1
    while index <= sheet.nrows - 1:
        int_vendor_id = False
        int_vendor_reg_id = False
        int_material_group_id = False
        int_subclass_id = False

        try:
            if sheet.cell_value(index, 0):
                object_id = api.model('iac.vendor').get([('vendor_code', '=', sheet.cell_value(index, 0))])
                if object_id:
                    int_vendor_id = object_id.id
                    int_vendor_reg_id = object_id.vendor_reg_id.id

            if int_vendor_id:
                if sheet.cell_value(index, 2):
                    object_id = api.model('material.group').get([('material_group', '=', sheet.cell_value(index, 2))])
                    if object_id:
                        int_material_group_id = object_id.id

                if sheet.cell_value(index, 3):
                    object_id = api.model('plm.subclass').get([('material_group', '=', sheet.cell_value(index, 2)),
                                                               ('subclass', '=', sheet.cell_value(index, 3))])
                    if object_id:
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
                api.model('iac.vendor.product').create(vendor_product_vals)
            else:
                logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
        except:
            traceback.print_exc()
            logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))

        index += 1

    logging.warn(u'成功处理 %s 个vendor.product' % (index - 1))