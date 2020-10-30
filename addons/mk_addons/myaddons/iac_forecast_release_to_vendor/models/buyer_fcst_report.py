# -*- coding: utf-8 -*-

import os
import json
import xlwt
import time, base64
import datetime
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
from odoo import models, fields, api
import psycopg2
import logging
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
import pdb
# Buyer Download FCST
# Laura  add
# Laura  modify 20180710 : 需 帶出代用料。同步修改上傳程式：在上傳時要判斷不是歸屬該buyer的材料,上傳時資料不寫入

_logger = logging.getLogger(__name__)

class iacBuyerFsctReportWizard(models.TransientModel):
    """ buyer fsct report  , 資料來源: iac_traw_data   """
    _name = 'iac.buyer.fsct.report.wizard'

    # plant_ids = fields.Many2many('pur.org.data', string="Plants")
    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst', index=True)
    # buyer_id = fields.Many2one('buyer.code', string='Buyer Code',
    #                            domain=lambda self: [('id', 'in', self.env.user.buyer_id_list)], index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    division_ids = fields.Many2many('division.code', string="Division",index=True)
    material_ids = fields.Many2many('material.master', string="Material",index=True)
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):
        self.storage_location_id = False
        if self.plant_id:
            return {'domain': {'storage_location_id': [('plant', '=', self.plant_id.plant_code)]}}

    @api.multi
    def action_confirm(self):
        #Buyer Download FCST

        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        # print '*38:'
        allids = []
        today_str = fields.Datetime.now()[:10].replace('-', '').replace(' ', '')
        # print '*40:', today_str
        # 20180815 laura 先找出 max_fpversion ( 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion )---s
        tcolumn_title = self.env['iac.tcolumn.title'].sudo().search(
            [('fpversion', '>=', today_str)], order='fpversion desc', limit=1)  # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add
        # print '*45:', tcolumn_title.fpversion
        # 20180815 laura 先找出 max_fpversion ( 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion )---e

        # search 查詢條件：表身 ___s
        for wizard in self:

            ##多選 divisions 處理______s
            division_codes_list = []
            for division_id in wizard.division_ids:
                division_codes_list.append(division_id.division)
            wizard.division_codes_list = ','.join(division_codes_list)
            # print '147:',division_codes_list
            ##多選 divisions 處理______e

            ##多選 materials 處理______s
            material_codes_list = []
            for material_id in wizard.material_ids:
                material_codes_list.append(material_id.part_no)
            wizard.material_codes_list = ','.join(material_codes_list)
            ##多選 materials 處理______e

            domain = []
            # user input的查詢條件 ____________s

            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)] # domain += [('plant_code', 'in', plant_codes_list)]
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.division_codes_list:
                domain += [('division_code', 'in', division_codes_list)] # domain += [('division_id', '=', wizard.division_ids.id)]
            if wizard.material_codes_list:
                domain += [('material_code', 'in', material_codes_list)]

            if wizard.storage_location_id:
                domain += [('storage_location_id', '=', wizard.storage_location_id.id)]

            # 條件： 1. vendor,material,buyer,plant,division<>null。 2. 只抓 fpversion='當天' 的資料。
            domain += [('vendor_id', '!=', False),('material_code', '!=',False),('buyer_id', '!=',False),('plant_id', '!=',False),('division_code', '!=',False)]
            domain += [('fpversion', '=', tcolumn_title.fpversion)]

            # print '*84 :',domain
            traw_export = self.env['iac.traw.data'].sudo().search(domain)
            print '*98:', wizard.plant_id.id
            #20180710 Laura add for 帶出代用料---s
            for pi in traw_export:
                allids += [(pi.id)]
                pi.write({'alt_grp_sort':'T','state':'1'})
                pi.env.cr.commit()
                if pi.alt_grp != '':
                    print '*105:', wizard.plant_id.id
                    material_exist = self.env['iac.traw.data'].sudo().search([
                        ('alt_grp', '=', pi.alt_grp),('fpversion', '>=', tcolumn_title.fpversion),('plant_id', '=', wizard.plant_id.id),('storage_location_id','=',wizard.storage_location_id.id)]) #20181114 laura add: FCST帶出代用料排除CP22   181216 ning update 代用料加location校验
                    for item in material_exist:
                        if not item.id in allids:
                            allids += [(item.id)]
                            item.write({'alt_grp_sort': 'F','state':'0'})
                            item.env.cr.commit()
            # print '*93:', allids
            domain = [('id', 'in', allids)]

            # print '*102:',tcolumn_title.fpversion,',',   domain
            traw_export = self.env['iac.traw.data'].sudo().search(domain)
            # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180815 laura add

            # print '*107:',traw_export
            # 20180710 Laura add for 帶出代用料---e

            if not traw_export: #tconfirm_export:
                raise UserError('查無資料! ')
            # user input的查詢條件 ____________e
        # search 查詢條件：表身 ___e

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True) #增加 sheet & 命名 sheet_name
        qty_w1_r = ''

        # excel 的格式______s

        # 凍結視窗
        sheet1.panes_frozen = True
        sheet1.horz_split_pos = 1 #直的
        sheet1.vert_split_pos = 4 #橫的

        #設定欄寬
        for i in range(0, 54):
            sheet1.col(i).width = 3000 # 256* 11.7 =3000

        for i in [2,11,45,47]:
            sheet1.col(i).width = 4400  # 256* 17

        for i in [3, 48, 49]:
            sheet1.col(i).width = 9300  # 256* 36
        # excel 的格式______e

        # 表頭的格式__________s
        # 表頭,灰底,黑字,字體大小240/20=12
        for_header1 = xlwt.easyxf('font: bold 1,color black, height 240;'  
                                  'align:  wrap on;'
                                  'pattern: pattern solid, pattern_fore_colour gray_ega')

        # 表頭,灰底,紅字,字體大小240/20=12
        for_header2 = xlwt.easyxf('font: bold 1,color red, height 240;'
                                  'align:  wrap on;'
                                  'pattern: pattern solid, pattern_fore_colour gray_ega')

        # 表頭,灰底,綠字,字體大小240/20=12
        for_header3 = xlwt.easyxf('font: bold 1,color green, height 240;'
                                  'align:  wrap on;'
                                  'pattern: pattern solid, pattern_fore_colour gray_ega')
        # 表頭的格式__________e

        # 表身的格式__________s
        # 文字格式： 黑字,字體大小240/20=12
        for_body1 = xlwt.easyxf('font: color black, height 240;')

        # 數字格式： 黑字,字體大小240/20=12,  #,##0.00
        for_body2 = xlwt.easyxf('font: color black, height 240;',num_format_str='#,##0')
        # 表身的格式__________e

        # 寫 表身 資料 + 格式 ___s
        #表頭變數_________s
        header_field_list = []
        list1 = []
        list2 = []

        header_field_list = [u'採購代碼', 'Division', u'料號', u'品名', 'Alternate Group',
                             u'是否替代料', u'庫存量', 'total open po qty', u'在途量', u'配額',
                             u'廠商','Round value', 'L/T', 'W1 MAX ASN QTY']
        self._cr.execute(" select qty_w1_r, qty_w2,qty_w3,qty_w4,qty_w5,"
                         "qty_w6,qty_w7,qty_w8,qty_w9,qty_w10,"
                         "qty_w11,qty_w12,qty_w13,"
                         "qty_m1,qty_m2,qty_m3,qty_m4,qty_m5,qty_m6,"
                         "qty_m7,qty_m8,qty_m9 "
                         "from iac_tcolumn_title "
                         "where fpversion in ( select max (fpversion) from iac_traw_data ) ")
        for row in self.env.cr.dictfetchall():
            qty_w1_r = str(row['qty_w1_r'])
            list1 = [ str(row['qty_w1_r']),str(row['qty_w2']),str(row['qty_w3']),str(row['qty_w4']),str(row['qty_w5']),
                      str(row['qty_w6']),str(row['qty_w7']),str(row['qty_w8']),str(row['qty_w9']),
                      str(row['qty_w10']),str(row['qty_w11']),str(row['qty_w12']),str(row['qty_w13']),
                      str(row['qty_m1']),str(row['qty_m2']),str(row['qty_m3']),str(row['qty_m4']),
                      str(row['qty_m5']),str(row['qty_m6']),str(row['qty_m7']),str(row['qty_m8']),
                      str(row['qty_m9']) ]
            header_field_list.extend(list1)

        if qty_w1_r == '':
            # print '*119'
            raise UserError('錯誤!!! 基本資料沒維護 ( iac_tcolumn_title) buyer_fcst_report.py ')
        # else:
        #     print '*122'

        list2 = ['B_001','B_002','B_004','B_005','B_012','B_017B','B_902S',
                 'B_902Q',u'試產料','SurplusMaxQty',u'未維護Quota','Cust PN',
                 'MFG PN','Remark','id','fpversion','Plant','Location']
        header_field_list.extend(list2)
        # 表頭變數_________e

        # 寫入 excel文件的表頭文字+格式 __________s
        for i in range(0, 54):
            sheet1.write(0, i, header_field_list[i], for_header1) # 灰底,黑字

        for i in [8, 13]:
            sheet1.write(0, i, header_field_list[i], for_header2)  # 灰底,紅字

        for i in range(14, 27):
            sheet1.write(0, i, header_field_list[i], for_header3)  # 灰底,綠字
        # 寫入 excel文件的表頭文字+格式 __________e

        r = 1

        for traw_line in traw_export:    # for tconfirm_line in tconfirm_export:
            # print '*199:', traw_line
            for i in xrange(len(traw_line.ids)):
                sheet1.write(r, 0, traw_line.buyer_id.buyer_erp_id,for_body1)
                sheet1.write(r, 1, traw_line.division_id.division,for_body1)
                sheet1.write(r, 2, traw_line.material_id.part_no,for_body1)
                sheet1.write(r, 3, traw_line.description,for_body1)
                sheet1.write(r, 4, traw_line.alt_grp,for_body1)
                sheet1.write(r, 5, traw_line.alt_flag,for_body1)
                sheet1.write(r, 6, traw_line.stock,for_body2) #表身數字格式：黑字,  # ,##0.00
                sheet1.write(r, 7, traw_line.open_po,for_body2)
                sheet1.write(r, 8, traw_line.intransit_qty,for_body2)
                sheet1.write(r, 9, traw_line.quota,for_body1)

                if traw_line.vendor_id.vendor_code:
                    vendor_code=traw_line.vendor_id.vendor_code
                else:
                    vendor_code = ''

                if traw_line.vendor_id.name:
                    vendor_name=traw_line.vendor_id.name[:6]
                else:
                    vendor_name = ''

                vendor = vendor_code +' ' + vendor_name
                sheet1.write(r, 10, vendor,for_body1)

                sheet1.write(r, 11, traw_line.round_value,for_body2)
                sheet1.write(r, 12, traw_line.leadtime,for_body1)
                sheet1.write(r, 13, traw_line.qty_w1,for_body2)
                sheet1.write(r, 14, traw_line.qty_w1_r,for_body2)
                sheet1.write(r, 15, traw_line.qty_w2,for_body2)
                sheet1.write(r, 16, traw_line.qty_w3,for_body2)
                sheet1.write(r, 17, traw_line.qty_w4,for_body2)
                sheet1.write(r, 18, traw_line.qty_w5,for_body2)
                sheet1.write(r, 19, traw_line.qty_w6, for_body2)
                sheet1.write(r, 20, traw_line.qty_w7, for_body2)
                sheet1.write(r, 21, traw_line.qty_w8, for_body2)
                sheet1.write(r, 22, traw_line.qty_w9, for_body2)
                sheet1.write(r, 23, traw_line.qty_w10, for_body2)
                sheet1.write(r, 24, traw_line.qty_w11, for_body2)
                sheet1.write(r, 25, traw_line.qty_w12, for_body2)
                sheet1.write(r, 26, traw_line.qty_w13, for_body2)
                sheet1.write(r, 27, traw_line.qty_m1, for_body2)
                sheet1.write(r, 28, traw_line.qty_m2, for_body2)
                sheet1.write(r, 29, traw_line.qty_m3, for_body2)
                sheet1.write(r, 30, traw_line.qty_m4, for_body2)
                sheet1.write(r, 31, traw_line.qty_m5, for_body2)
                sheet1.write(r, 32, traw_line.qty_m6, for_body2)
                sheet1.write(r, 33, traw_line.qty_m7, for_body2)
                sheet1.write(r, 34, traw_line.qty_m8, for_body2)
                sheet1.write(r, 35, traw_line.qty_m9, for_body2)
                sheet1.write(r, 36, traw_line.b001, for_body2)
                sheet1.write(r, 37, traw_line.b002, for_body2)
                sheet1.write(r, 38, traw_line.b004, for_body2)
                sheet1.write(r, 39, traw_line.b005, for_body2)
                sheet1.write(r, 40, traw_line.b012, for_body2)
                sheet1.write(r, 41, traw_line.b017b, for_body2)
                sheet1.write(r, 42, traw_line.b902s, for_body2)
                sheet1.write(r, 43, traw_line.b902q, for_body2)

                if traw_line.flag : # 試產料
                    sheet1.write(r, 44, traw_line.flag,for_body1)
                else:
                    sheet1.write(r, 44, "")

                if traw_line.max_surplus_qty:   # SurplusMaxQty
                    sheet1.write(r, 45, traw_line.max_surplus_qty,for_body2)
                else:
                    sheet1.write(r, 45, "")

                if traw_line.mquota_flag:   # 未維護Quota
                    sheet1.write(r, 46, traw_line.mquota_flag,for_body1)
                else:
                    sheet1.write(r, 46, "")

                if traw_line.custpn_info:   # Cust PN
                    sheet1.write(r, 47, traw_line.custpn_info,for_body1)
                else:
                    sheet1.write(r, 47, "")

                if traw_line.mfgpn_info:   #  MFG PN
                    sheet1.write(r, 48, traw_line.mfgpn_info,for_body1)
                else:
                    sheet1.write(r, 48, "")

                if traw_line.remark:   #  Remark
                    sheet1.write(r, 49, traw_line.remark,for_body1)
                else:
                    sheet1.write(r, 49, "")

                sheet1.write(r, 50, traw_line.id, for_body1)  # id

                sheet1.write(r, 51, traw_line.fpversion, for_body1)  # id # 20180815 laura add

                sheet1.write(r,52,traw_line.plant_id.plant_code,for_body1) #plant 181212 ning add
                sheet1.write(r, 53, traw_line.storage_location_id.storage_location, for_body1)  # location 181212 ning add

                r += 1
        wb2.save(output)
        # 寫 表身 資料 + 格式 ___e

        # 文件?出成功之后,跳??接，??器下?文件
        vals = {
            'name': 'buyer_fsct_report_downloads',
            'datas_fname': 'buyer_fsct_report_downloads.xls',
            'description': 'Buyer FCST Report',
            'type': 'binary',
            'db_datas': base64.encodestring(output.getvalue()),
        }
        file = self.env['ir.attachment'].sudo().create(vals)
        # print '*164:',file.id
        # print '*227:', '/web/content/%s/buyerFCST_report%s.xls' % (file.id, file.id)
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/buyer_FCST_report_%s.xls' % (file.id, file.id),
            'target': 'new',
        }

        return action

