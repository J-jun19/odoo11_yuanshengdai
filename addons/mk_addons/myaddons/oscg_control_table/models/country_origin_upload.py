# -*- coding: utf-8 -*-
import xlrd
from odoo.modules.registry import RegistryManager
from datetime import datetime, timedelta,date
from odoo.modules.registry import RegistryManager
from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import time,base64
import datetime
import os
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError



class CountryOriginUpload(models.TransientModel):
    # buyer 上傳LT的程式。選擇上傳檔案路徑的 wizard table
    _name = 'iac.country.origin.upload'
    file_name = fields.Char(u'File Name')
    file = fields.Binary(u'File')



    @api.multi
    def action_confirm_country_origin_upload(self):
        # 讀 buyer upload LT 的報表
        excel_obj = open_workbook(file_contents=base64.decodestring(self.file))
        sheet_obj = excel_obj.sheet_by_index(0)

        if sheet_obj.cell(0, 0).value <> 'Plant' or sheet_obj.cell(0, 8).value <> 'Updated On':
            # print '*24:',sheet_obj.cell(0, 0).value,'。',sheet_obj.cell(2, 158).value
            raise exceptions.ValidationError("匯入檔案錯誤!")
        error_num = ''
        error_str = ''
        error_num1 = ''
        error_num2 = ''
        error_num3 = ''
        error_count = 0
        for rx in range(sheet_obj.nrows):
            if rx>=1:
                error_count = 0
                plant_code = sheet_obj.cell(rx,0).value
                if sheet_obj.cell(rx,2).value:
                    vendor_code = sheet_obj.cell(rx,2).value.split()[0]
                else:
                    vendor_code=''
                if sheet_obj.cell(rx,3).value:
                    material_code = sheet_obj.cell(rx,3).value.split()[0]
                else:
                    material_code=''
                if sheet_obj.cell(rx,4).value:
                    country = sheet_obj.cell(rx,4).value
                else:
                    error_num3 = error_num3 + str(rx + 1) + ' , '
                    error_count = 1
                city = sheet_obj.cell(rx,5).value
                remark = sheet_obj.cell(rx,6).value
                # print vendor_code,material_code,country,city,remark
                if vendor_code:
                    vendor_id = self.env['iac.vendor'].search([('vendor_code','=',vendor_code)]).id
                else:
                    error_num1 = error_num1 + str(rx + 1) + ' , '
                    error_count = 1
                if material_code:
                    material_id = self.env['material.master'].search([('part_no','=',material_code),('plant_code','=',plant_code)]).id
                else:
                    error_num2 = error_num2 + str(rx + 1) + ' , '
                    error_count = 1
                if error_count == 0:
                    country_origin = self.env['iac.country.origin'].search([('vendor','=',vendor_id),('material','=',material_id)])
                    if country_origin:
                        print 1
                    else:
                        error_num = error_num + str(rx + 1) + ' , '
                        error_count = 1

        if error_num <> '':
            # print '*66:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num + '行錯誤，Vendor Code+Material 不存在!'
        if error_num1 <> '':
            # print '*66:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num1 + '行錯誤，Vendor Code不能為空!'
        if error_num2 <> '':
            # print '*66:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num2 + '行錯誤，Material 不能為空!'
        if error_num3 <> '':
            # print '*66:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num3 + '行錯誤，Country 不能為空!'

        if error_num=='' and error_num1=='' and error_num2=='' and error_num3=='':
            for rx in range(sheet_obj.nrows):
                if rx >= 1:
                    plant_code = sheet_obj.cell(rx,0).value
                    vendor_code = sheet_obj.cell(rx, 2).value.split()[0]
                    material_code = sheet_obj.cell(rx, 3).value.split()[0]
                    # country_code = sheet_obj.cell(rx, 4).value.split()[0].upper()
                    city = sheet_obj.cell(rx, 5).value
                    remark = sheet_obj.cell(rx, 6).value
                    vendor_id = self.env['iac.vendor'].search([('vendor_code', '=', vendor_code)]).id
                    material_id = self.env['material.master'].search([('part_no', '=', material_code),('plant_code','=',plant_code)]).id
                    # country_id = self.env['res.country'].search([('code','=',country_code)]).id
                    country_id = sheet_obj.cell(rx, 4).value
                    country_origin = self.env['iac.country.origin'].search(
                        [('vendor', '=', vendor_id), ('material', '=', material_id)])
                    # print country_origin
                    country_origin_update = {
                        'country_id':country_id,
                        'city':city,
                        'remark':remark
                    }
                    country_origin.write(country_origin_update)
                    country_origin.env.cr.commit()


        if error_str <> '':
            raise exceptions.ValidationError(error_str)
        else:

            raise exceptions.ValidationError('上傳成功')