# -*- coding:utf-8  -*-

from odoo import fields,models

class IacVendorClassCallSap(models.Model):

    _name = 'iac.vendor.class.call.sap'

    vendor_id = fields.Many2one('iac.vendor')
    cdt = fields.Datetime()
    score_snapshot = fields.Char()
    supplier_company_id = fields.Many2one('iac.supplier.company')
    final_class = fields.Char()
    interface_code = fields.Char()
    send_flag = fields.Boolean(default=False)