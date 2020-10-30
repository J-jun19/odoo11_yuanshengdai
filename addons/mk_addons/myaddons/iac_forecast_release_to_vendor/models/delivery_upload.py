# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import time,base64
import datetime
import os
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError

class Group_tDeliveryUpload(models.Model):
    # 建立一model  for  call API group_id用 (可整批拋,只call 一次API)
    _name = 'iac.tdelivery.upload.group'

    group_ids = fields.One2many('iac.tdelivery.upload', 'group_id')

class tDeliveryUpload(models.Model):
    # 目的：iac_tdelivery_upload : 將  buyer 回寫的LT報表 寫入iac_tdelivery_upload檔
    _name = 'iac.tdelivery.upload'
    # _inherit = 'iac.tvendor.upload'
    _description = "tdelivery upload"
    _order = 'status desc,id desc'

    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code', string="採購代碼", index=True)
    material_id = fields.Many2one('material.master', 'Material', index=True)
    material_code = fields.Char(string='Material_code', related='material_id.part_no')
    qty = fields.Integer(string='QTY')
    shipping_date = fields.Date(string="shipping date")
    buyer_remark = fields.Char(string="Remark")
    uploader = fields.Many2one('res.users', string="uploader", index=True)
    cdt = fields.Datetime(string="cdt") # cdt = fields.Date(string="cdt")
    key_part = fields.Char(string="key part")

    vendor_id = fields.Many2one('iac.vendor', string="廠商代碼",index=True)
    vendor_code = fields.Char(string="Vendor_code", related="vendor_id.vendor_code")
    iac_pn_vendor = fields.Char(string="iac_pn vendor")

    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)

    # 紀錄 "调用SAP接口"是否成功的欄位____s
    state = fields.Selection([
        ('pending', 'Pending'),  # 等待拋轉中
        ('fp error(Update)', 'FP Error(Update)'),  # 通知FP失敗 Update
        ('fp error(Delete)', 'FP Error(Delete)'),  # 通知FP失敗 Delete
        ('fp error(Insert)', 'FP Error(Insert)'),  # 通知FP失敗 Insert
        ('finished(Update)', 'Finished(Update)'),  # 更新FP成功 Update
        ('finished(Delete)', 'Finished(Delete)'),  # 更新FP成功 Delete
        ('finished(Insert)', 'Finished(Insert)')  # 更新FP成功  Insert
    ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char()
    # 紀錄 "调用SAP接口"是否成功的欄位____e

    reply_id = fields.Many2one('iac.tconfirm.data', index=True)
    group_id = fields.Many2one('iac.tdelivery.upload.group')

    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

class tDeliveryEDI(models.Model):
    # 目的：iac_tdelivery_edi  :  廠商EDI上傳LT
    _name = 'iac.tdelivery.edi'
    _inherit = 'iac.tvendor.upload'

    plant = fields.Char(string="plant")  # CP21  #存原始資料
    iac_pn = fields.Char(string="iac_pn")   # 6019A0936301  #存原始資料
    vendor_code = fields.Char(string="vendor_code")  # 0000381107  #存原始資料
    fcst_version = fields.Char(string="fcst_version")  # 612201709270003  #存原始資料
    valid = fields.Integer(string="valid") # 用來 判斷對方重覆送的  #存原始資料
    buyer_code = fields.Char(string="buyer_code")  # 512  #存原始資料