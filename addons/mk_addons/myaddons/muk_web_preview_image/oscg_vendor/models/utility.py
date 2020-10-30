# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
_logger = logging.getLogger(__name__)


def contain_zh(word):
    """
    判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    """
    zh_pattern = re.compile(u'[\u2E80-\uFE4F]+')
    match = zh_pattern.search(word)

    return match

def is_phone(word):
    """
    判断是否电话号码，只检查数字、“-”、“+”字符
    :param word:
    :return:
    """
    if word:
        word = word.encode('utf-8')
        for i in range(len(word)):
            a = word[i]
            if not is_digital(word[i]) and not is_phone_special(word[i]):
                return False
        return True
    else:
        return False

def is_phone_special(ch):
    """
    判断是否是‘-’或 '+'
    :param ch:
    :return:
    """
    if ch:
        if ord(ch) == ord('-') or ord(ch) == ord('+'):
            return True
        return False
    else:
        return False

def is_digital(ch):
    """
    判断是否是数字
    :param ch:
    :return:
    """
    if ch:
        if ch.isdigit():
            return True
        else:
            return False
    else:
        return False

def check_float(string):
    #支付时，输入的金额可能是小数，也可能是整数
    s = str(string)
    if s.count('.') == 1: # 判断小数点个数
        sl = s.split('.') # 按照小数点进行分割
        left = sl[0] # 小数点前面的
        right = sl[1] # 小数点后面的
        if left.startswith('-') and left.count('-') == 1 and right.isdigit():
            lleft = left.split('-')[1] # 按照-分割，然后取负号后面的数字
            if lleft.isdigit():
                return False
        elif left.isdigit() and right.isdigit():
            # 判断是否为正小数
            return True
    elif s.isdigit():
        s = int(s)
        if s != 0:
            return True
    return False

def is_email(email):
    """
    判断是否是email
    :param str:
    :return:
    """
    if email:
        return re.match("^([a-zA-Z0-9_\.\-])+\@+[a-zA-Z0-9_\.\-]+\.+[a-zA-Z0-9]", email)
    else:
        return False

def checklen(pwd):
    return len(pwd) >= 6

def checkContainUpper(pwd):
    pattern = re.compile('[A-Z]+')
    match = pattern.findall(pwd)

    if match:
        return True
    else:
        return False

def checkContainNum(pwd):
    pattern = re.compile('[0-9]+')
    match = pattern.findall(pwd)
    if match:
        return True
    else:
        return False

def checkContainLower(pwd):
    pattern = re.compile('[a-z]+')
    match = pattern.findall(pwd)

    if match:
        return True
    else:
       return False

def checkSymbol(pwd):
    pattern = re.compile('([^a-z0-9A-Z])+')
    match = pattern.findall(pwd)

    if match:
        return True
    else:
        return False

def checkPassword(pwd):
    #判断密码长度是否合法
    lenOK=checklen(pwd)

    #判断是否包含大写字母
    upperOK=checkContainUpper(pwd)

    #判断是否包含小写字母
    lowerOK=checkContainLower(pwd)

    #判断是否包含数字
    numOK=checkContainNum(pwd)

    #判断是否包含符号
    symbolOK=checkSymbol(pwd)

    return (lenOK and (upperOK or lowerOK) and numOK and symbolOK)

"""邮件线程"""
class mailThread(threading.Thread):
    def __init__(self, object_id, template_name):
        threading.Thread.__init__(self)
        self.object_id = object_id
        self.template_name = template_name
    def run(self):
        try:
            template = self.env.ref(self.template_name)
            template.sudo().send_mail(self.object_id, force_send=True)
        except:
            pass

def send_to_email(self, object_id=None, template_name=None):
    """发送邮件"""
    #thread = mailThread(object_id, template_name)
    #thread.start()

    mail_task_vals={
        "object_id":object_id,
        "template_id":template_name
    }
    self.env.cr.commit()
    self.env["iac.mail.task"].add_mail_task(**mail_task_vals)