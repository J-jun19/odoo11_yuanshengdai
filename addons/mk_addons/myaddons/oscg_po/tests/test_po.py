# -*- coding: utf-8 -*-

import erppeek
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
from binascii import b2a_hex, a2b_hex
from datetime import datetime, timedelta
import base64
import urllib
import urllib2
import xlrd

"""
erppeek使用例子：
>>> import erppeek
>>> api = erppeek.Client('http://localhost:8069', 'todo','admin', 'admin')
>>> api.common.version()
>>> api.count('res.partner', [])
>>> api.search('res.partner', [('country_id', '=', 'be'), ('parent_id', '!=', False)])
>>> api.read('res.partner', [44], ['id', 'name', 'parent_id'])

>>> m = api.model('res.partner')
>>> m = api.ResPartner
>>> m.count([('name', 'like', 'Packt%')])
>>> 1
>>> m.search([('name', 'like', 'Packt%')])
>>> [30]

注意：调用model的自定义函数时，该函数及相关被调用函数必须有返回值
"""

if __name__=="__main__":
    test_flag = 1
    if test_flag == 1:
        context = {
            'approve_status': True,
            'data': {'id': 1}
        }
        api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

        po_confirm_his_rec = api.model('iac.purchase.order.vendor.confirm.his')
        #po_confirm_his_rec.po_new_vendor_confirm_create(850742)
        #po_confirm_his_rec.po_change_vendor_confirm_create(850742)
        po_confirm_his_rec.po_confirm_reset_to_vendor(850742)
        #po_confirm_reset_to_vendor
        #task = api.model('iac.purchase.order.line.change')
        #task.browse(282).apply_po_line_audit()

        #task = api.model('iac.purchase.order')
        #task.browse(850733).apply_po_audit()



    elif test_flag == 2:
        context = {
            'approve_status': True,
            'data': {'id': 1}
        }
        api = erppeek.Client('http://localhost:8069', 'iac_db', 'admin', 'iacadmin')

        #score_list = api.model('iac.score.list').browse(709)
        score_list_ids=[709,]
        task = api.model('task.vendor.score')
        # reg_vars = {'comment': u'', 'delivery_hours': u'', 'address_pobox': u'33014-9317', 'plant_id': 2, 'vat_number': u'', 'address_street': u'\u8857\u540d* 16115 N.W. 52ND AVENUE', 'shareholders': u'', 'user_id': 3013, 'sales_email': u' huh@agdasia.com / chenp@agdasia.com', 'is_outerbuy': u'N', 'web_site': u'www.allamerican.com', 'mother_name_cn': u'All American Semiconductor, Inc.', 'other_emails': u'', 'message_last_post': False, 'sales_telephone': u'86-0-13331877377', 'project_status': u'', 'apply_memo': u'', 'sales_mobile': u'', 'use_project': u'', 'supplier_category': u'Electronic', 'company_telephone2': u'86-021-64477019', 'short_name': u'', 'company_telephone1': u'86-021-64477015', 'buyer_email': u'li.ivy@iac.com.tw', 'company_fax': u'86-021-64477012', 'name2_cn': u'  ', 'supplier_type': u'Agent', 'address_city': u'MIAMI', 'mother_address_cn': u'  ', 'name1_en': u'AGD Electronics Asia Pacific CO. L', 'duns_number': u'', 'currency': 3, 'address_country': False, 'reject_reason': u'', 'employee_number': u'', 'license_number': u'59-2814714  ', 'factory_count': 0.0, 'address_district': u'FLORIDA', 'mother_name_en': u'All American Semiconductor, Inc.', 'state': u'done', 'capital': u'', 'name2_en': u'AGD Electronics Asia Pacific CO. L', 'vendor_code': u'0000361344', 'supplier_description': u'', 'conglomerate': u'', 'applyfile_id': False, 'reason_one': False, 'corporation_description': u'', 'address_postalcode': u'33014', 'name1_cn': u'  ', 'mother_address_en': u'  ', 'is_scene': u'N', 'contact_person': u'Henry Hu / Patty Chen', 'material_use_range': u''}
        task.browse(1).calcu_supplier_company_risk(score_list_ids,'lwt_test')
    elif test_flag == 3:
        sender = 'wangjinbin@163.com'
        receiver = 'wangjinbin@163.com'
        subject = 'python email test'
        smtpserver = 'smtp.163.com'
        username = 'wangjinbin@163.com'
        password = 'wjb820930*'

        msg = MIMEText('你好', 'text', 'utf-8')  # 中文需参数‘utf-8’，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')

        smtp = smtplib.SMTP()
        smtp.connect('smtp.163.com')
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
    elif test_flag == 4:
        api = erppeek.Client('http://localhost:8069', 'iac_test_db', 'BUYER3', '123456')

        model = api.model('iac.agent.users.wizard')
        model.selection_principal_user(api.context)

    elif test_flag == 5:
        division_vals = {
            'division_code': '0'
        }

        api = erppeek.Client('http://localhost:8069', 'iac_test_db', 'admin', '123456')

        model = api.model('iac.vendor.block')
        # self.vendor_id.vendor_reg_id.write((1, id, division_vals))
        model.browse(1).button_to_approve()
    elif test_flag == 6:
        res = ['1', '12', '13', '16']
        str = ','.join(res)
        print str

        res2 = []
        for item in str.split(','):
            res2.append(item)
        print res2

        print [g for g in str.split(',')]
    elif test_flag == 7:
        res = []
        a = ','.join(res)
        print a

        b = [g for g in ','.split(',')]
        print b

        res_str = ','.join(res)
        if res_str:
            print 'yes'
        else:
            print 'no'

        c = '1,2'.split(',')
        print c
    elif test_flag == 8:
        pc_class_ids = ['A', 'C', 'B', 'D', 'DW', 'B']

        sc_class = 'A'
        for item in pc_class_ids:
            if item > sc_class:
                sc_class = item
        print sc_class

    elif test_flag == 9:
        text = '2050-12-31'
        cryptor = AES.new('keyskeyskeyskeys', AES.MODE_CBC, 'keyskeyskeyskeys')
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        print b2a_hex(ciphertext)
    elif test_flag == 10:
        a = fields.Datetime.from_string('2018-02-09')
        b = datetime.today()
        print a, b
        if a <= b:
            print 'ok'
        else:
            print 'no'
    elif test_flag == 11:
        context = {
            'approve_status': True,
            'data': {'id': 1}
        }
        api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

        vendor_model = api.model('iac.vendor.register')
        vendor_model.browse(3051).test_send_email()
    elif test_flag == 12:
        api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

        model = api.model('res.users')
        user_id = model.get(49)
        for item in user_id.vendor_ids:
            print item.id
    elif test_flag == 13:
        file_name = 'sega123.ppt'# 28M word文件
        f = open(r'd:\temp\%s' % (file_name), 'rb')  # 二进制方式打开文件
        ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        f.close()

        url = 'http://localhost:8069/vendor/attachment/upload'
        values = {'stage': 'F01',
                  'vendor_reg_id': '3651',
                  'file_type_code': 'A01',
                  'filename': file_name,
                  'file': ls_f,
                  'description': 'test_desc',
                  'db_name': 'IAC_DB',
                  'user_name': 'admin'
                  }
        print values
        # data = urllib.urlencode(values)  # 编码工作
        # req = urllib2.Request(url, data)  # 发送请求同时传data表单
        # response = urllib2.urlopen(req)  # 接受反馈的信息
        # the_page = response.read()  # 读取反馈的内容
        # print the_page
    elif test_flag == 14:
        f = open(r'd:\temp\sega.txt', 'rb')  # 二进制方式打开文件
        file = f.read()
        print file
        print '\n\n'
        a = file.replace(' ', '+')
        print a
    elif test_flag == 15:
        workbook = xlrd.open_workbook('d:\\temp\\vendor.xls')
        sheet = workbook.sheet_by_name('Sheet1')
        index = 1
        it_levels = []
        rmas = []
        vendor_property = []
        while index <= sheet.nrows - 1:
            print 'index: %s' % index
            if sheet.cell_value(index, 43) not in it_levels:
                it_levels.append(sheet.cell_value(index, 43))
            if sheet.cell_value(index, 63) not in rmas:
                rmas.append(sheet.cell_value(index, 63))
            if sheet.cell_value(index, 65) not in vendor_property:
                vendor_property.append(sheet.cell_value(index, 65))
            index += 1
        print it_levels
        print rmas
        print vendor_property
    elif test_flag == 16:
        total = 9898
        thread_list = []
        counter = 1
        index = 1
        while (counter + 499 <= total):
            thread_list.append({'begin': counter, 'end': counter + 499})
            counter += 500
            index += 1
        if counter <= total:
            thread_list.append({'begin': counter, 'end': total})

        print 'total=%s' % index
        print thread_list