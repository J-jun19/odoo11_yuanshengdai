# -*- coding: utf-8 -*-

import erppeek
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from datetime import datetime, timedelta
from odoo import fields
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
    test_flag = 2
    if test_flag == 1:
        context = {
            "rpc_callback_data": {
                "status": "true",
                "FormStatus": "D",
                "jsonrpc": "2.0",
                "id": 24,
                "tokens": ["aHR0cDovL3d3dy5vc2NnLmNuLCBJQUNfREIsIGFkbWluLCAxLCAxNTI4NDQ3NjM5"],
                "params": {
                    "FlowList": [{
                        "Timestamp": "2018/06/08 19:25:02",
                        "Approver": "劉紅霞",
                        "Comments": "申請.",
                        "Stage": "開始"
                    }, {
                        "Timestamp": "2018/06/08 19:29:20",
                        "Approver": "丁斌",
                        "Comments": "退件.3434",
                        "Stage": "MM_Manager"
                    }, {
                        "Timestamp": "2018/06/08 19:30:32",
                        "Approver": "劉紅霞",
                        "Comments": "抽單(2018/06/08 19:30:32)",
                        "Stage": "*開始"
                    }]
                },
                "EFormNO": "NVR201806080002",
                "message": "",
                "stage": "F03_E",
                "method": "call",
                "inf_call_id": "2378"
            },
            "approve_status": True,
            "data": {
                "id": 24
            }
        }
        api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

        model = api.model('iac.vendor.copy')
        model.browse(24).vendor_block_unblock_callback(context)
    elif test_flag == 2:
        context = {
            "rpc_callback_data": {
                "status": "true",
                "FormStatus": "C",
                "jsonrpc": "2.0",
                "id": 10,
                "tokens": ["aHR0cDovL3d3dy5vc2NnLmNuLCBJQUNfREIsIGFkbWluLCAxLCAxNTI4NDQ3NjM5"],
                "params": {
                    "FlowList": [{
                        "Timestamp": "2018/06/08 19:25:02",
                        "Approver": "劉紅霞",
                        "Comments": "申請.",
                        "Stage": "開始"
                    }, {
                        "Timestamp": "2018/06/08 19:29:20",
                        "Approver": "丁斌",
                        "Comments": "退件.3434",
                        "Stage": "MM_Manager"
                    }, {
                        "Timestamp": "2018/06/08 19:30:32",
                        "Approver": "劉紅霞",
                        "Comments": "抽單(2018/06/08 19:30:32)",
                        "Stage": "*開始"
                    }]
                },
                "EFormNO": "NVR201806080002",
                "message": "",
                "stage": "F03_E",
                "method": "call",
                "inf_call_id": "2378"
            },
            "approve_status": True,
            "data": {
                "id": 10
            }
        }
        api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'iacadmin')

        model = api.model('iac.vendor.block')
        model.browse(10).vendor_block_unblock_callback(context)
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