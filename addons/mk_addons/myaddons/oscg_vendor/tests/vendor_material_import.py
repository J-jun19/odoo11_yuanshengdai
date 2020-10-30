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

    workbook = xlrd.open_workbook('d:\\lwt\\vendor_data\\vendor_material.xls')
    sheet = workbook.sheet_by_index(0)

    logging.warn(u'需处理 %s 个vendor.material' % (sheet.nrows - 1))

    # 执行导入数据
    index = 1
    while index <= sheet.nrows - 1:
        int_vendor_id = False
        int_vendor_reg_id = False
        int_division_id = False
        int_material_group_id = False

        try:
            if sheet.cell_value(index, 0):
                object_id = api.model('iac.vendor').get([('vendor_code', '=', sheet.cell_value(index, 0))])
                int_vendor_id = object_id.id
                int_vendor_reg_id = object_id.vendor_reg_id

            if int_vendor_id:
                if sheet.cell_value(index, 1):
                    object_id = api.model('division.code').get([('division', '=', sheet.cell_value(index, 1))])
                    if object_id:
                        int_division_id = object_id.id

                if sheet.cell_value(index, 3):
                    object_id = api.model('material.group').get([('material_group', '=', sheet.cell_value(index, 3))])
                    if object_id:
                        int_material_group_id = object_id.id

                vendor_material_vals = {
                    'vendor_reg_id': int_vendor_reg_id,
                    'vendor_id': int_vendor_id,
                    'division_code': int_division_id,
                    'project': sheet.cell_value(index, 2),
                    'material_group': int_material_group_id
                }
                api.model('iac.vendor.material').create(vendor_material_vals)
            else:
                logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
        except:
            traceback.print_exc()
            logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))

        index += 1

    logging.warn(u'成功处理 %s 个vendor.material' % (index - 1))