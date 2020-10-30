# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging
import base64
from odoo import fields
from datetime import datetime, timedelta
import traceback

"""
针对没有bank资料的vendor补充vendor_attachment资料
"""

if __name__=="__main__":
    # api = erppeek.Client('http://10.158.6.102:8069', 'IAC_DB', 'admin', 'iacadmin')
    api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

    type_id = api.model('iac.attachment.type').get([('name', '=', 'A24')])

    vendor_ids = api.model('iac.vendor').browse([])
    for vendor_id in vendor_ids:
        logging.warn('do vendor_code=%s' % (vendor_id.vendor_code))
        vendor_attachment_id = api.model('iac.vendor.attachment').get([('vendor_id', '=', vendor_id.id)])
        if not vendor_attachment_id:
            logging.warn('vendor have not bank info. vendor_code=%s' % (vendor_id.vendor_code))
            attachment_vals = {
                'vendor_id': vendor_id.id,
                'type': type_id.id,
                'group': 'bank',
            }
            api.model('iac.vendor.attachment').create(attachment_vals)
        else:
            logging.warn('vendor have bank info. vendor_code=%s' % (vendor_id.vendor_code))