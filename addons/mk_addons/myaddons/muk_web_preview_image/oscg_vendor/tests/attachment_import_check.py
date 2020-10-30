# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging
import base64
from odoo import fields
from datetime import datetime, timedelta

"""
导入attachment
"""

if __name__=="__main__":
    api = erppeek.Client('http://10.158.6.102:8069', 'IAC_DB', 'admin', 'iacadmin')

    import_data = 1
    if import_data == 1:# 导入文档
        workbook = xlrd.open_workbook('/var/lib/odoo/files/Vendor_files_1.1.xls')
        sheet = workbook.sheet_by_name('Sheet 1')

        # 导入数据校验
        check_flag = True
        index = 1
        while index <= sheet.nrows - 1:
            logging.warn(u'do index %s' % (index))

            if sheet.cell_value(index, 0):
                object_id = api.model('iac.vendor').get([('vendor_code', '=', sheet.cell_value(index, 0))])
                if not object_id:
                    check_flag = check_flag & False
                    logging.error(u'No.%s 数据异常，未找到vendor_code=%s' % (index, sheet.cell_value(index, 0)))
                else:
                    logging.warn(u'vendor %s OK' % (object_id.vendor_code))

            if sheet.cell_value(index, 4):
                object_id = api.model('iac.attachment.type').get([('name', '=', sheet.cell_value(index, 4))])
                if not object_id:
                    check_flag = check_flag & False
                    logging.error(u'No.%s 数据异常，未找到attachment_type=%s' % (index, sheet.cell_value(index, 4)))
                else:
                    logging.warn(u'attachment type %s OK' % (object_id.name))

            index += 1
        logging.warn(u'需创建 %s 个Attachment' % (index - 1))
