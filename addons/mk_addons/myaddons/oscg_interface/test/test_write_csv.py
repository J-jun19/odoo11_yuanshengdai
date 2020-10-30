# -*- coding: utf-8 -*-
from decimal import Decimal
import math

from odoo.tools import float_utils
from contextlib import contextmanager
import xlrd
import base64
import hashlib
@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError, err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


#读取xls文件输出 res.groups 的菜单配置
if __name__ == "__main__":


    file_path="D:\\file\\security\\po_attachment\\38.xls"
    with opened_w_error(file_path, "rb") as (file_handler, exc):
        if exc:
            print str(exc)

        else:
            file = file_handler.read()
            encode_file = base64.b64encode(file)
            print 'file hash:'+str(hashlib.sha1(file).hexdigest())
