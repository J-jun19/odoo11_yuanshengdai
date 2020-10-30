# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
import xlrd
import xmlrpclib
import erppeek
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)
"""
调用远程计算机的补充文件空栏位信息
"""

if __name__=="__main__":
    URL = 'http://localhost:8071'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.attachment.import')
    model.fill_attachment_data()
