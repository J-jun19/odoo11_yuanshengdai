# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import time,base64
import datetime
import os
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError


class UploadLTHistoryWizard(models.TransientModel):
    """ 查询  iac.tupload.lt.history 的 篩選畫面  UploadLTHistory
            條件： 1. plant,vendor,buyer,material,cdt
"""
    _name = 'iac.tupload.lt.history.wizard'
    _description = "tupload lt history wizard "

    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst', index=True)
    # buyer_id = fields.Many2one('buyer.code', string='Buyer Code',
    #                            domain=lambda self: [('id', 'in', self.env.user.buyer_id_list)], index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    material_id = fields.Many2one('material.master', string='Material', index=True)
    w_date = fields.Date('Write date')
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Location')  # 181211 ning add
    # date_from = fields.Date('Write date from')
    # date_to = fields.Date('Write date to')

    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):
        self.storage_location_id = False
        if self.plant_id:
            return {'domain': {'storage_location_id': [('plant', '=', self.plant_id.plant_code)]}}

    @api.multi
    def search_upload_lt_history(self):
        # 1. 把 iac.tupload.lt.history 刪除
        self._cr.execute(" delete from iac_tupload_lt_history ")

        # 2.1.  把必選條件帶入，將 vendor,buyer,EDI  3個表的資料寫入 iac.tupload.lt.history
        self._cr.execute(" insert into iac_tupload_lt_history  (type,status,plant_id,buyer_id,material_id,qty,"
                         "                  shipping_date,buyer_remark,key_part,iac_pn_vendor,vendor_id,"
                         "                  create_uid,create_date,write_date,write_uid,reply_id,storage_location_id) "                       
                         "(   "
                         "     select 'vendor'as type ,status,plant_id,buyer_id,material_id,qty,"
                         "                shipping_date, buyer_remark,key_part,iac_pn_vendor,vendor_id, "
                         "                create_uid,create_date,write_date,write_uid,reply_id,storage_location_id  "
                         "       from iac_tvendor_upload "
                         "     where plant_id = %s and to_char(write_date,'yyyy-mm-dd') = %s "
                         "     union  "
                         "      select 'buyer' as type,status,plant_id, buyer_id,material_id,qty,   "
                         "                shipping_date, buyer_remark,key_part,iac_pn_vendor,vendor_id, "
                         "                create_uid,create_date,write_date,write_uid,reply_id,storage_location_id"
                         "       from iac_tdelivery_upload "
                         "      where plant_id = %s and to_char(write_date,'yyyy-mm-dd') = %s "
                         "     union  "
                         "      select 'edi' as type,status,plant_id, buyer_id,material_id,qty,   "
                         "                shipping_date, buyer_remark,key_part,iac_pn_vendor,vendor_id, "
                         "                create_uid,cdt,cdt,write_uid,reply_id,storage_location_id"
                         "       from iac_tdelivery_edi "
                         "      where valid =1 and plant_id = %s and to_char(cdt,'yyyy-mm-dd') = %s "
                         " ) ",
                         (self.plant_id.id,self.w_date,self.plant_id.id,self.w_date,self.plant_id.id,self.w_date) )

        print '*63:' , self.plant_id.id ,',', self.w_date

        # 2.2.  把其他條件帶入，篩選 iac.tupload.lt.history
        domain = []
        if self.buyer_id:
            domain += [('buyer_id', '=', self.buyer_id.id)]
        if self.vendor_id:
            domain += [('vendor_id', '=', self.vendor_id.id)]
        if self.material_id:
            domain += [('material_id', '=', self.material_id.id)]
        if self.storage_location_id:
            domain += [('storage_location_id', '=', self.storage_location_id.id)]
        history_export = self.env['iac.tupload.lt.history'].sudo().search(domain)

        allids = []
        for item in history_export:
            allids += [(item.id)]

        # 2.3.  跳到另一個 視窗：upload LT history 的 tree 視圖
        action = {
            'name': _('Upload LT history'),
            'type': 'ir.actions.act_window',
            'res_model': 'iac.tupload.lt.history',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': self.env.ref('iac_forecast_release_to_vendor.view_tupload_lt_history').id,
            'act_window_id': self.env.ref('iac_forecast_release_to_vendor.action_tupload_lt_history').id,
            'domain': [('id', 'in', allids)]
        }
        return action

        # raise UserError(_(u'test_0206_2！ '))


class UploadLTHistory(models.Model):
    # 目的：查 vendor,buyer,edi 上傳LT所有紀錄的 table
    #  ( iac.tvendor.upload、iac.tdelivery.upload、iac.tdelivery.edi) 。
    _name = 'iac.tupload.lt.history'
    _description = "tupload lt history"
    _order = 'status desc, type desc ,id desc'

    _inherit = ['iac.tvendor.upload']

    type = fields.Selection([
        ('buyer', 'buyer'), ('vendor', 'vendor'), ('edi', 'edi')
    ], string='type', readonly=True, index=True, copy=False)

