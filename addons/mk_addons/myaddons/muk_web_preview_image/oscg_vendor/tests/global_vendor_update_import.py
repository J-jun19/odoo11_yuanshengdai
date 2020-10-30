# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging
import traceback

"""
导入GV CODE
"""

if __name__=="__main__":
    api = erppeek.Client('http://10.158.6.102:8069', 'IAC_DB', 'admin', 'iacadmin')

    import_data = 1
    if import_data == 1:
        workbook = xlrd.open_workbook('c:\\temp\\supplier_company.xls')
        sheet = workbook.sheet_by_name('Sheet1')

        logging.warn(u'需创建 %s 个supplier.company' % (sheet.nrows - 1))

        # 执行导入数据
        index = 1
        while index <= sheet.nrows - 1:
            logging.warn(u'处理第%s个' % (index))

            int_vendor_ids = []

            object_id = api.model('iac.supplier.company').get([('company_no', '=', sheet.cell_value(index, 0))])
            if not object_id:
                if sheet.cell_value(index, 5):
                    for item in sheet.cell_value(index, 5).split('|'):
                        object_id = api.model('iac.vendor').get([('vendor_code', '=', item)])
                        if object_id:
                            int_vendor_ids.append(object_id.id)
                        else:
                            logging.error(u'vendor code %s 不存在' % (item))

                try:
                    # 判断重名
                    name = sheet.cell_value(index, 1)
                    object_id = api.model('iac.supplier.company').get([('name', '=', sheet.cell_value(index, 1))])
                    if object_id:
                        name = sheet.cell_value(index, 0) + ' ' + sheet.cell_value(index, 1)

                    supplier_company_vals = {
                        'company_no': sheet.cell_value(index, 0),
                        'name': name,
                        'company_name2': sheet.cell_value(index, 2),
                        'vat_no': sheet.cell_value(index, 3),
                        'supplier_type': sheet.cell_value(index, 4).strip()
                    }
                    supplier_company_id = api.model('iac.supplier.company').create(supplier_company_vals)

                    for int_vendor_id in int_vendor_ids:
                        object_id = api.model('iac.vendor').get(int_vendor_id)
                        supplier_company_line_vals = {
                            'supplier_company_id': supplier_company_id.id,
                            'vendor_id': object_id.id
                        }
                        api.model('iac.supplier.company.line').create(supplier_company_line_vals)
                        object_id.is_bind = True
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，company_no=%s' % (index, sheet.cell_value(index, 0)))

            index += 1

        logging.warn(u'成功创建 %s 个supplier.company' % (index - 1))
    elif import_data == 2:# 导入GV CODE
        workbook = xlrd.open_workbook('c:\\temp\\global_vendor.xls')
        sheet = workbook.sheet_by_name('Sheet1')

        logging.warn(u'需创建 %s 个global.vendor' % (sheet.nrows - 1))

        # 执行导入数据
        index = 1
        while index <= sheet.nrows - 1:
            logging.warn(u'处理第%s个' % (index))

            int_supplier_company_ids = []

            if sheet.cell_value(index, 5):
                for item in sheet.cell_value(index, 5).split('|'):
                    object_id = api.model('iac.supplier.company').get([('company_no', '=', item)])
                    if object_id:
                        int_supplier_company_ids.append(object_id.id)
                    else:
                        logging.error(u'company_no %s 不存在' % (item))

            if int_supplier_company_ids:
                try:
                    global_vendor_vals = {
                        'global_vendor_code': sheet.cell_value(index, 0),
                        'name': sheet.cell_value(index, 1),
                        'global_name2': sheet.cell_value(index, 2),
                        'global_address': sheet.cell_value(index, 3),
                        'global_address2': sheet.cell_value(index, 4)
                    }
                    global_vendor_id = api.model('iac.global.vendor').create(global_vendor_vals)

                    for int_supplier_company_id in int_supplier_company_ids:
                        object_id = api.model('iac.supplier.company').get(int_supplier_company_id)
                        global_vendor_line_vals = {
                            'global_vendor_id': global_vendor_id.id,
                            'supplier_company_id': object_id.id
                        }
                        api.model('iac.global.vendor.line').create(global_vendor_line_vals)
                        object_id.is_bind = True
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，global_vendor_code=%s' % (index, sheet.cell_value(index, 0)))
            else:
                logging.warn(u'No.%s 行异常，supplier company都不存在，跳过，global_vendor_code=%s' % (index, sheet.cell_value(index, 0)))

            index += 1

        logging.warn(u'成功创建 %s 个global.vendor' % (index - 1))
    elif import_data == 3:  # 导入vendor.plm
        workbook = xlrd.open_workbook('c:\\temp\\vendor_plm.xls')
        sheet = workbook.sheet_by_name('Sheet1')

        # 执行导入数据
        index = 1
        while index <= sheet.nrows - 1:
            logging.warn(u'处理第%s个' % (index))

            int_global_vendor_id = False

            if sheet.cell_value(index, 1):
                object_id = api.model('iac.global.vendor').get(
                    [('global_vendor_code', '=', sheet.cell_value(index, 1))])
                int_global_vendor_id = object_id.id
                object_id.is_used = True

            if int_global_vendor_id:
                try:
                    vendor_plm_vals = {
                        'name': sheet.cell_value(index, 0),
                        'global_vendor_id': int_global_vendor_id,
                        'state': 'done'
                    }
                    api.model('iac.vendor.plm').create(vendor_plm_vals)
                except:
                    traceback.print_exc()
                    logging.warn(u'No.%s 行异常，global_vendor_code=%s' % (index, sheet.cell_value(index, 1)))
            else:
                logging.warn(u'No.%s 行异常，global vendor不存在，跳过，global_vendor_code=%s' % (index, sheet.cell_value(index, 1)))

            index += 1

        logging.warn(u'成功创建 %s 个vendor.plm' % (index - 1))