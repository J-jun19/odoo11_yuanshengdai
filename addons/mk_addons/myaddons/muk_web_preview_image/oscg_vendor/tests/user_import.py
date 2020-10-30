# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging

"""
导入user
"""

if __name__=="__main__":
    api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

    import_data = 1
    if import_data == 1:# 导入IAC内部user
        workbook = xlrd.open_workbook('d:\\temp\\internal_user.xls')
        sheet = workbook.sheet_by_name('Sheet1')

        # 导入数据校验
        check_flag = True
        index = 1
        while index <= sheet.nrows - 1:
            logging.warn(u'检查第 %s 行' % index)
            exists_user_id = api.model('res.users').get([('login', '=', sheet.cell_value(index, 1))])
            if not exists_user_id:
                if sheet.cell_value(index, 4):
                    for item in sheet.cell_value(index, 4).split('|'):
                        object_id = api.model('buyer.code').get([('buyer_erp_id', '=', item)])
                        if not object_id:
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到buyer_code=%s' % (index, item))

                if sheet.cell_value(index, 5):
                    for item in sheet.cell_value(index, 5).split('|'):
                        object_id = api.model('pur.org.data').get([('plant_code', '=', item)])
                        if not object_id:
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到plant_code=%s' % (index, item))

                if sheet.cell_value(index, 6):
                    for item in sheet.cell_value(index, 6).split('|'):
                        object_id = api.model('division.code').get([('division', '=', item)])
                        if not object_id:
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到division_code=%s' % (index, item))

                if sheet.cell_value(index, 7):
                    for item in sheet.cell_value(index, 7).split('|'):
                        object_id = api.model('source.code').get([('source_code', '=', item)])
                        if not object_id:
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到source_code=%s' % (index, item))

                if sheet.cell_value(index, 8):
                    for item in sheet.cell_value(index, 8).split('|'):
                        object_id = api.model('res.groups').get('oscg_vendor.' + item)
                        if not object_id:
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到group_id=%s' % (index, item))
            else:
                logging.info(u'第 %s 个user %s 已经存在，跳过检查。user_id=%s' % (index, exists_user_id.name, exists_user_id.id))
                
            index += 1
        logging.warn(u'需处理 %s 个user' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= sheet.nrows - 1:
                exists_user_id = api.model('res.users').get([('login', '=', sheet.cell_value(index, 1))])
                if not exists_user_id:
                    int_buyer_code_ids = []
                    int_plant_ids = []
                    int_division_code_ids = []
                    int_source_code_ids = []
                    int_groups_ids = []
                    buyer_code_ids = False
                    plant_ids = False
                    division_code_ids = False
                    source_code_ids = False
                    groups_ids = False

                    if sheet.cell_value(index, 4):
                        for item in sheet.cell_value(index, 4).split('|'):
                            object_id = api.model('buyer.code').get([('buyer_erp_id', '=', item)])
                            if object_id:
                                int_buyer_code_ids.append(object_id.id)
                        buyer_code_ids = erppeek.RecordList(api.model('buyer.code'), int_buyer_code_ids)

                    if sheet.cell_value(index, 5):
                        for item in sheet.cell_value(index, 5).split('|'):
                            object_id = api.model('pur.org.data').get([('plant_code', '=', item)])
                            if object_id:
                                int_plant_ids.append(object_id.id)
                        plant_ids = erppeek.RecordList(api.model('pur.org.data'), int_plant_ids)

                    if sheet.cell_value(index, 6):
                        for item in sheet.cell_value(index, 6).split('|'):
                            object_id = api.model('division.code').get([('division', '=', item)])
                            if object_id:
                                int_division_code_ids.append(object_id.id)
                        division_code_ids = erppeek.RecordList(api.model('division.code'), int_division_code_ids)

                    if sheet.cell_value(index, 7):
                        for item in sheet.cell_value(index, 7).split('|'):
                            object_id = api.model('source.code').get([('source_code', '=', item)])
                            if object_id:
                                int_source_code_ids.append(object_id.id)
                        source_code_ids = erppeek.RecordList(api.model('source.code'), int_source_code_ids)

                    if sheet.cell_value(index, 8):
                        for item in sheet.cell_value(index, 8).split('|'):
                            object_id = api.model('res.groups').get('oscg_vendor.' + item)
                            if object_id:
                                int_groups_ids.append(object_id.id)
                        groups_ids = erppeek.RecordList(api.model('res.groups'), int_groups_ids)

                    user_vals = {
                        'name': sheet.cell_value(index, 0),
                        'login': sheet.cell_value(index, 1),
                        'password': sheet.cell_value(index, 2),
                        'share': False,
                        'groups_id': groups_ids
                    }
                    user_id = api.model('res.users').create(user_vals)

                    partner_vals = {
                        'email': sheet.cell_value(index, 3),
                        'plant_ids': plant_ids,
                        'buyer_code_ids': buyer_code_ids,
                        'source_code_ids': source_code_ids,
                        'division_code_ids': division_code_ids,
                        'supplier': False
                    }
                    user_id.partner_id.write(partner_vals)
                    logging.warn(u'第 %s 个user 处理 %s 成功。user_id=%s' % (index, user_id.name, user_id.id))
                else:
                    logging.warn(u'第 %s 个user %s %s 已经存在，跳过不再创建。user_id=%s' % (index, exists_user_id.login, exists_user_id.name, exists_user_id.id))

                index += 1

            logging.warn(u'成功处理 %s 个user' % (index - 1))
    elif import_data == 2:  # 导入IAC外部user
        workbook = xlrd.open_workbook('d:\\temp\\external_user.xls')
        sheet = workbook.sheet_by_name('Sheet1')

        # 导入数据校验
        check_flag = True
        index = 1
        while index <= sheet.nrows - 1:
            index += 1
        logging.warn(u'需处理 %s 个user' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= sheet.nrows - 1:
                exists_user_id = api.model('res.users').get([('login', '=', sheet.cell_value(index, 1))])
                if not exists_user_id:
                    group_id = api.model('res.groups').get('oscg_vendor.IAC_vendor_groups')
                    groups_ids = erppeek.RecordList(api.model('res.groups'), [group_id.id])
                    user_vals = {
                        'name': sheet.cell_value(index, 0),
                        'login': sheet.cell_value(index, 1),
                        'password': sheet.cell_value(index, 2),
                        'share': True,
                        'groups_id': groups_ids
                    }
                    user_id = api.model('res.users').create(user_vals)

                    partner_vals = {
                        'email': sheet.cell_value(index, 3),
                        'supplier': True
                    }
                    user_id.partner_id.write(partner_vals)
                    logging.warn(u'第 %s 个user，处理 %s 成功.user_id=%s' % (index, user_id.name, user_id.id))
                else:
                    logging.warn(u'第 %s 个user %s %s 已经存在，跳过不再创建。user_id=%s' % (index, exists_user_id.login, exists_user_id.name, exists_user_id.id))

                index += 1

            logging.warn(u'成功处理 %s 个user' % (index - 1))