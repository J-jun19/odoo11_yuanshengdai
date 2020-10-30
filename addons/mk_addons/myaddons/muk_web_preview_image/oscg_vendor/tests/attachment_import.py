# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging
import base64
from odoo import fields
from datetime import datetime, timedelta
import traceback

"""
导入attachment
"""

if __name__=="__main__":
    api = erppeek.Client('http://10.158.6.102:8069', 'IAC_DB', 'admin', 'iacadmin')
    # api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

    workbook = xlrd.open_workbook('/var/lib/odoo/files/Vendor_files_1.1.xls')
    # workbook = xlrd.open_workbook('d:/temp/Vendor_files_1.1.xls')
    sheet = workbook.sheet_by_name('Sheet 1')

    # 执行导入数据
    index = 1
    while index <= sheet.nrows - 1:
        logging.warn('do index=%s' % (index))

        int_vendor_id = False
        int_vendor_reg_id = False
        int_attachment_type_id = False
        time_sensitive = False
        group = 'basic'

        if sheet.cell_value(index, 0):
            object_id = api.model('iac.vendor').get([('vendor_code', '=', sheet.cell_value(index, 0))])
            if object_id:
                int_vendor_id = object_id.id
                if object_id.vendor_reg_id:
                    int_vendor_reg_id = object_id.vendor_reg_id.id

        if int_vendor_id:
            if sheet.cell_value(index, 4):
                object_id = api.model('iac.attachment.type').get([('name', '=', sheet.cell_value(index, 4))])
                if object_id:
                    int_attachment_type_id = object_id.id
                    time_sensitive = object_id.time_sensitive
                    if object_id.name in ['A24','A15','A16']:
                        group = 'bank'

            # 处理文件
            directory = 1# basic
            if group == 'bank':
                directory = 2# bank

            try:
                open_file = open(r'/var/lib/odoo/files/EP_FILE/%s' % (sheet.cell_value(index, 1)), 'rb')  # 二进制方式打开文件
                # open_file = open(r'd:/temp/EP_FILE/%s' % (sheet.cell_value(index, 1)), 'rb')  # 二进制方式打开文件
                base64_file_content = base64.b64encode(open_file.read())  # 读取文件内容，转换为base64编码
                open_file.close()

                file_vals = {
                    'filename': sheet.cell_value(index, 1),
                    'file': base64_file_content,
                    'directory': directory
                }
                file_id = api.model('muk_dms.file').create(file_vals)

                # 如果文档类型需要过期日期管理，但上传文件中没有过期日期，则使用upload_date + 2年
                str_upload_date = False
                str_expiration_date = False
                if sheet.cell_value(index, 5):
                    upload_date = fields.Date.from_string(sheet.cell_value(index, 5))
                else:
                    upload_date = fields.Date.from_string(fields.Date.today())
                str_upload_date = fields.Date.to_string(upload_date)
                if time_sensitive:
                    if not sheet.cell_value(index, 6):
                        str_expiration_date = fields.Date.to_string(upload_date + timedelta(days=int(365 * 2)))
                    else:
                        str_expiration_date = sheet.cell_value(index, 6)
                attachment_vals = {
                    'type': int_attachment_type_id,
                    'file_id': file_id.id,
                    'description': sheet.cell_value(index, 2),
                    'group': group,
                    'expiration_date': str_expiration_date,
                    'state': sheet.cell_value(index, 7)
                }
                if group == 'basic':
                    if int_vendor_reg_id:
                        attachment_vals['vendor_reg_id'] = int_vendor_reg_id
                        api.model('iac.vendor.register.attachment').create(attachment_vals)
                    else:
                        logging('row:%s no vendor register,vendor code %s' % (index, sheet.cell_value(index, 0)))
                if group == 'bank':
                    if int_vendor_id:
                        attachment_vals['vendor_id'] = int_vendor_id
                        api.model('iac.vendor.attachment').create(attachment_vals)
                    else:
                        logging('row:%s no vendor,vendor code %s' % (index, sheet.cell_value(index, 0)))
            except:
                traceback.print_exc()
                logging.warn(u'row %s error,vendor_code=%s' % (index, sheet.cell_value(index, 0)))
        else:
            logging.warn('no vendor %s' % (sheet.cell_value(index, 0)))

        index += 1

    logging.warn(u'成功处理 %s 个attachment' % (index - 1))