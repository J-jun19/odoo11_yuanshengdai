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

    workbook = xlrd.open_workbook('d:\\lwt\\vendor_data\\vendor_factory.xls')
    sheet = workbook.sheet_by_index(0)

    logging.warn(u'需处理 %s 个vendor.factory' % (sheet.nrows - 1))

    # 执行导入数据
    index = 1
    while index <= sheet.nrows - 1:
        int_vendor_id = False
        int_vendor_reg_id = False

        try:
            if sheet.cell_value(index, 0):
                object_id = api.model('iac.vendor').get([('vendor_code', '=', sheet.cell_value(index, 0))])
                int_vendor_id = object_id.id
                int_vendor_reg_id = object_id.vendor_reg_id

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
                api.model('iac.vendor.factory').create(vendor_factory_vals)
            else:
                logging.warn(u'No.%s 行vendor未找到，跳过，vendor_code=%s' % (index, sheet.cell_value(index, 0)))
        except:
            traceback.print_exc()
            logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 0)))

        index += 1

    logging.warn(u'成功处理 %s 个vendor.factory' % (index - 1))