# -*- coding: utf-8 -*-

import json
import xlwt
import time, base64
import datetime
from xlrd import open_workbook
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api
import psycopg2
import logging
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
import pdb

class VendorForecastDeliveryReportBK(models.Model):
    _name = "iac.vendor.forecast.delivery.report.bk"

    buyer_id = fields.Many2one('buyer.code', string="IAC Buyer Code", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True) #只要顯示該vendor的資料&必填

    @api.multi
    def action_confirm(self):
        # Vendor Fill Form

        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        #筛选条件
        # vendor_id_list = []
        # vendor_forecast_line = self.env["iac.tconfirm.data"].search([('status', '=', 'T')])
        # buyer_id_list = []
        # vendor_id_list = []
        # for report_line in self:
        #     buyer_id_list.append(report_line.buyer_id)
        #     vendor_id_list.append(report_line.vendor_id)
        # if not buyer_id_list and not vendor_id_list :
        #     raise UserError('请选择筛选条件! ')
        #
        # if vendor_forecast_line.vendor_id not in vendor_id_list :
        #     raise UserError('查无资料!')
        # if vendor_forecast_line.buyer_id not in vendor_id_list:
        #     raise UserError('查无资料!')

        output = StringIO()
        wb1 = xlwt.Workbook()
        sheet1 = wb1.add_sheet('sheet1', cell_overwrite_ok=True)

        sheet1.col(0).width = 3000
        sheet1.col(1).width = 3500
        sheet1.col(2).width = 3000
        sheet1.col(3).width = 3000
        sheet1.col(4).width = 4000
        sheet1.col(5).width = 3000
        sheet1.col(6).width = 3000
        sheet1.col(7).width = 2000
        sheet1.col(8).width = 3000
        #sheet1.col(11).width = 0
        # sheet1.col(106).width = 4000
        sheet1.col(158).width = 3500
        sheet1.col(159).width = 3000
        sheet1.col(160).width = 3000
        #sheet1.col(106).width = 3000

        for_header1 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        for_header2 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  )
        for_header3 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  )
        for_header4 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        for_header5 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                 )
        for_body1 = xlwt.easyxf(num_format_str='#,##0')

        sheet1.panes_frozen = True
        sheet1.horz_split_pos = 3  # 行
        sheet1.vert_split_pos = 6  # 列


        # 表頭變數_________s
        header_field_list = []
        header_field_list = ['BuyerName','IAC Part No.', 'Key Part', 'Description', 'total open po qty', 'In Transit',
                             'Round value', 'L/T', 'W1 MAX ASN QTY',
                             'W1_R','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','M1',
                             'M2','M3','M4','M5','M6','M7','M8','M9','Remark','ETD W-2','ETD W-1',
                             'ETD W1','ETD W2','ETD W3',
                             'ETD W4','ETD W5','ETD W6','ETD W7','ETD W8','ETD W9','ETD W10','ETD W11','ETD W12',
                             'ETD W13','W14-W17','W18-W21',
                            'W22-W25','W26-W29','Version ID','Vendor Code','Vendor Name','Plant','Location','CM_VENDOR']
        # self._cr.execute(" select qty_w1_r, qty_w2,qty_w3,qty_w4,qty_w5,"
        #                  "qty_w6,qty_w7,qty_w8,qty_w9,qty_w10,"
        #                  "qty_w11,qty_w12,qty_w13,"
        #                  "qty_m1,qty_m2,qty_m3,qty_m4,qty_m5,qty_m6,"
        #                  "qty_m7,qty_m8,qty_m9 "
        #                  "from iac_tcolumn_title "
        #                  )

        # for row in self.env.cr.dictfetchall():
        #     list1 = [str(row['qty_w1_r']), str(row['qty_w2']), str(row['qty_w3']), str(row['qty_w4']),
        #              str(row['qty_w5']),
        #              str(row['qty_w6']), str(row['qty_w7']), str(row['qty_w8']), str(row['qty_w9']),
        #              str(row['qty_w10']), str(row['qty_w11']), str(row['qty_w12']), str(row['qty_w13']),
        #              str(row['qty_m1']), str(row['qty_m2']), str(row['qty_m3']), str(row['qty_m4']),
        #              str(row['qty_m5']), str(row['qty_m6']), str(row['qty_m7']), str(row['qty_m8']),
        #              str(row['qty_m9'])]
        #     header_field_list.extend(list1)
        #     list2 = ['Version ID',u'廠商代碼',u'廠商名稱']
            # header_field_list.extend(list2)

        # for i in range(0, 51):
        #         sheet1.write(0, i, header_field_list[i])  # 灰底,黑字
        # for i in [8, 13]:
        #         sheet1.write(0, i, header_field_list[i])  # 灰底,紅字
        # for i in range(14, 27):
        #         sheet1.write(0, i, header_field_list[i])  # 灰底,綠字

        #iac_tcolumn_title 资料
        qty_w1_list = []
        qty_w2_list = []
        qty_m1_list = []
        for wizard in self:
                    domain = []
                    # user input的查詢條件 ____________s
                    domain += [( 'status', '=', 'T')] # 只顯示  status = T: true有效
                    if wizard.buyer_id:
                        domain += [('buyer_id', '=', wizard.buyer_id.id)]
                    if wizard.vendor_id:
                        domain += [('vendor_id', '=', wizard.vendor_id.id)]
                    # print '*130: ', domain
                    traw_export = self.env['iac.tconfirm.data'].sudo().search(domain)
                    # l = xrange(len(traw_export))
                    # print '*133: ',  traw_export[0].fpversion
                    if not traw_export:
                        raise UserError('查無資料! ')
                    else:
                        title_export = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)])
                        if not title_export:
                            title_err_msg = traw_export[0].fpversion, 'title資料未維護! '
                            raise UserError(title_err_msg)
                    # else:
                        # print tconfirm_export[0].fpversion
                        vendor_code = self.env['iac.tcolumn.title'].sudo().search([('fpversion', '=', traw_export[0].fpversion)]).vendor_code
                        vendor_name = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).vendor_name
                        qty_w1_r = self.env['iac.tcolumn.title'].sudo().search([('fpversion', '=', traw_export[0].fpversion)]).qty_w1_r
                        qty_w2 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w2
                        qty_w1_list.append(qty_w2)
                        qty_w3 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w3
                        qty_w1_list.append(qty_w3)
                        qty_w4 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w4
                        qty_w1_list.append(qty_w4)
                        qty_w5 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w5
                        qty_w1_list.append(qty_w5)
                        qty_w6 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w6
                        qty_w1_list.append(qty_w6)
                        qty_w7 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w7
                        qty_w1_list.append(qty_w7)
                        qty_w8 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w8
                        qty_w1_list.append(qty_w8)
                        qty_w9 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w9
                        qty_w1_list.append(qty_w9)
                        qty_w10 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w10
                        qty_w2_list.append(qty_w10)
                        qty_w11 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w11
                        qty_w2_list.append(qty_w11)
                        qty_w12 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w12
                        qty_w2_list.append(qty_w12)
                        qty_w13 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_w13
                        qty_w2_list.append(qty_w13)
                        qty_m1 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m1
                        qty_m1_list.append(qty_m1)
                        qty_m2 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m2
                        qty_m1_list.append(qty_m2)
                        qty_m3 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m3
                        qty_m1_list.append(qty_m3)
                        qty_m4 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m4
                        qty_m1_list.append(qty_m4)
                        qty_m5 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m5
                        qty_m1_list.append(qty_m5)
                        qty_m6 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m6
                        qty_m1_list.append(qty_m6)
                        qty_m7 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m7
                        qty_m1_list.append(qty_m7)
                        qty_m8 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m8
                        qty_m1_list.append(qty_m8)
                        qty_m9 = self.env['iac.tcolumn.title'].sudo().search(
                            [('fpversion', '=', traw_export[0].fpversion)]).qty_m9
                        qty_m1_list.append(qty_m9)

                        print '*192:', traw_export[0].fpversion,',',qty_w1_r ,',',qty_w1_r[5:9]
                        month = int(qty_w1_r[5:7])
                        day = int(qty_w1_r[7:9])
                        # print month,day
                        real_year = time.localtime(time.time()).tm_year
                        real_month = time.localtime(time.time()).tm_mon
                        if month > 1 and month < 12:
                            year = real_year
                            # year1为填交期的年份
                            year1 = real_year
                        else:
                            if month == real_month:
                                year = real_year
                                year1 = real_year
                            else:
                                if month == 1:
                                    year = real_year
                                    year1 = real_year
                                elif month == 12:
                                    year = real_year - 1
                                    year1 = real_year-1

                        if (year % 4) == 0 and (year % 100) != 0 or (year % 400) == 0:
                            is_leap = 0  # 閏年
                        else:
                            is_leap = 1  # 平年
                            # 写excel文件的表头

                        if day-14 >0:
                            day=day-14
                        elif day-14 <=0 and (month ==2 or month==4 or month == 6 or month == 9 or month == 11 or month == 8):
                            day=31+(day-14)
                            month=month-1
                        elif day-14 <=0 and (month==5 or month == 7 or month == 10 or month == 12):
                            day=30+(day-14)
                            month = month - 1
                        elif day - 14 <= 0 and month == 3 and is_leap == 0:
                            day=29+(day-14)
                            month==2
                        elif day - 14 <= 0 and month == 3 and is_leap == 1:
                            day = 28 + (day - 14)
                            month == 2
                        elif day - 14 <= 0 and month==1:
                            day = 31+(day-14)
                            month = 12
                            year1 = year1 - 1

                        for i in xrange(len(header_field_list)):
                            if i <= 8:
                                # print header_field_list[i]
                                sheet1.write_merge(0, 2, i, i, header_field_list[i],for_header1)
                            elif i>8 and i<=30:
                                if i == 9:
                                    if qty_w1_r[5:7]>qty_w1_r[10:12]:
                                        sheet1.write(0, i, str(year) + '/' + qty_w1_r[5:7] + '/' + qty_w1_r[7:9], for_header1)
                                        sheet1.write(1, i, str(year+1) + '/' + qty_w1_r[10:12] + '/' + qty_w1_r[12:14],
                                                 for_header1)
                                        year = year+1
                                    elif int(qty_w1_r[10:12]) == 12 and int(qty_w1_r[12:14]) == 31:
                                        sheet1.write(0, i, str(year) + '/' + qty_w1_r[5:7] + '/' + qty_w1_r[7:9],
                                                     for_header1)
                                        sheet1.write(1, i,
                                                     str(year) + '/' + qty_w1_r[10:12] + '/' + qty_w1_r[12:14],
                                                     for_header1)
                                        year = year+1
                                    else:
                                        sheet1.write(0, i, str(year) + '/' + qty_w1_r[5:7] + '/' + qty_w1_r[7:9],
                                                     for_header1)
                                        sheet1.write(1, i,
                                                     str(year) + '/' + qty_w1_r[10:12] + '/' + qty_w1_r[12:14],
                                                     for_header1)
                                if i>9 and i<=17:
                                    # print qty_w1_list,qty_w2_list,qty_m1_list
                                    if qty_w1_list[i-10][3:5]>qty_w1_list[i-10][8:10]:
                                        sheet1.write(0, i, str(year) + '/' + qty_w1_list[i-10][3:5] + '/' + qty_w1_list[i-10][5:7], for_header1)
                                        sheet1.write(1, i, str(year+1) + '/' + qty_w1_list[i-10][8:10] + '/' + qty_w1_list[i-10][10:12], for_header1)
                                        year = year + 1
                                    elif int(qty_w1_list[i-10][8:10]) == 12 and int(qty_w1_list[i-10][10:12]) == 31:
                                        sheet1.write(0, i,str(year) + '/' + qty_w1_list[i - 10][3:5] + '/' + qty_w1_list[i - 10][5:7],
                                                     for_header1)
                                        sheet1.write(1, i,str(year) + '/' + qty_w1_list[i - 10][8:10] + '/' + qty_w1_list[i - 10][10:12],
                                                     for_header1)
                                        year = year+1
                                    else:
                                        sheet1.write(0, i,str(year) + '/' + qty_w1_list[i - 10][3:5] + '/' + qty_w1_list[i - 10][5:7],for_header1)
                                        sheet1.write(1, i, str(year) + '/' + qty_w1_list[i - 10][8:10] + '/' +qty_w1_list[i - 10][10:12], for_header1)

                                if i>17 and i<=21:
                                    if qty_w2_list[i-18][4:6]>qty_w2_list[i-18][9:11]:
                                        sheet1.write(0, i, str(year) + '/' + qty_w2_list[i-18][4:6] + '/' + qty_w2_list[i-18][6:8], for_header1)
                                        sheet1.write(1, i, str(year+1) + '/' + qty_w2_list[i-18][9:11] + '/' + qty_w2_list[i-18][11:13], for_header1)
                                        year = year + 1
                                    elif int(qty_w2_list[i-18][9:11]) == 12 and int(qty_w2_list[i-18][11:13]) == 31:
                                        sheet1.write(0, i,str(year) + '/' + qty_w2_list[i - 18][4:6] + '/' + qty_w2_list[i - 18][6:8],
                                                     for_header1)
                                        sheet1.write(1, i,str(year) + '/' + qty_w2_list[i - 18][9:11] + '/' + qty_w2_list[i - 18][11:13],
                                                     for_header1)
                                        year = year+1
                                    else:
                                        sheet1.write(0, i,str(year) + '/' + qty_w2_list[i - 18][4:6] + '/' + qty_w2_list[ i - 18][ 6:8],for_header1)
                                        sheet1.write(1, i, str(year) + '/' + qty_w2_list[i - 18][9:11] + '/' +qty_w2_list[i - 18][11:13], for_header1)

                                if i>21 and i<=30:
                                    if qty_m1_list[i-22][3:5]>qty_m1_list[i-22][8:10]:
                                        sheet1.write(0, i, str(year) + '/' + qty_m1_list[i-22][3:5] + '/' + qty_m1_list[i-22][5:7], for_header1)
                                        sheet1.write(1, i, str(year+1) + '/' + qty_m1_list[i-22][8:10] + '/' + qty_m1_list[i-22][10:12], for_header1)
                                        year = year + 1
                                    elif int(qty_m1_list[i-22][8:10]) == 12 and int(qty_m1_list[i-22][10:12]) == 31:
                                        sheet1.write(0, i,str(year) + '/' + qty_m1_list[i - 22][3:5] + '/' + qty_m1_list[i - 22][5:7],
                                                     for_header1)
                                        sheet1.write(1, i,str(year) + '/' + qty_m1_list[i - 22][8:10] + '/' + qty_m1_list[i - 22][10:12],
                                                     for_header1)
                                        year = year +1
                                    else:
                                        sheet1.write(0, i, str(year) + '/' + qty_m1_list[i - 22][3:5]+ '/' + qty_m1_list[i-22][5:7], for_header1)
                                        sheet1.write(1, i, str(year) + '/' + qty_m1_list[i - 22][8:10]+ '/' + qty_m1_list[i-22][10:12], for_header1)


                                sheet1.write_merge(2, 2, i, i, header_field_list[i], for_header4)
                            elif i ==31:
                                sheet1.write_merge(0, 2, i, i, header_field_list[i])
                            elif i >31 and i <=33:
                                # print sheet1.cell(0,32).value
                                # print sheet1.cell(0,33).value
                                # if i<33:
                                    count = 32 + 7 * (i - 32)   #32-38, 39-45
                                    sheet1.write_merge(0, 0, count, count + 6, header_field_list[i],for_header4)
                                # #做前两周运算
                                #     if day-14 >0:
                                #        day=day-14
                                #     elif day-14 <=0 and (month ==2 or month==4 or month == 6 or month == 9 or month == 11 or month == 8):
                                #        day=31+(day-14)
                                #        month=month-1
                                #     elif day-14 <=0 and (month==5 or month == 7 or month == 10 or month == 12):
                                #        day=30+(day-14)
                                #        month = month - 1
                                #     elif day - 14 <= 0 and month == 3 and is_leap == 0:
                                #        day=29+(day-14)
                                #        month==2
                                #     elif day - 14 <= 0 and month == 3 and is_leap == 1:
                                #         day = 28 + (day - 14)
                                #         month == 2
                                #     elif day - 14 <= 0 and month==1:
                                #         day = 31+(day-14)
                                #         month = 12
                                #         year = year - 1

                                    for num in range(7):
                                            #sheet1.col(count).hidden = True
                                            date_str = str(year1)+'/'+str(month) + '/' + str(day)  # 待定
                                            # print date_str
                                            week_day = datetime.datetime(year1, month, day).weekday()  # *
                                            #sheet1.col(count).hidden = True
                                            # print week_day
                                            if week_day == 0:
                                                week_day_str = u'週一'
                                            if week_day == 1:
                                                week_day_str = u'週二'
                                            if week_day == 2:
                                                week_day_str = u'週三'
                                            if week_day == 3:
                                                week_day_str = u'週四'
                                            if week_day == 4:
                                                week_day_str = u'週五'
                                            if week_day == 5:
                                                week_day_str = u'週六'
                                            if week_day == 6:
                                                week_day_str = u'週日'
                                            if week_day == 5 or week_day == 6:
                                                sheet1.write(2, count, week_day_str,for_header4)
                                                sheet1.write(1, count, date_str,for_header4)
                                            else:
                                                sheet1.write(2, count, week_day_str,for_header5)
                                                sheet1.write(1, count, date_str,for_header5)
                                            count += 1
                                            if ((
                                                                                    month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12) and day < 31) \
                                                    or ((
                                                                                month == 4 or month == 6 or month == 9 or month == 11) and day < 30) \
                                                    or (month == 2 and is_leap == 0 and day < 29) \
                                                    or (month == 2 and is_leap == 1 and day < 28):
                                                day += 1
                                            elif ((
                                                                                  month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10) and day >= 31) \
                                                    or ((
                                                                                month == 4 or month == 6 or month == 9 or month == 11) and day >= 30) \
                                                    or (month == 2 and is_leap == 0 and day >= 29) \
                                                    or (month == 2 and is_leap == 1 and day >= 28):
                                                month += 1
                                                day = 1
                                            elif month == 12 and day >= 31:
                                                month = 1
                                                day = 1
                                                year1 += 1
                            elif i > 33 and i <= 46:
                                # month = int(qty_w1_r[5:7])
                                # day = int(qty_w1_r[7:9])
                                # # print month,day
                                # real_year = time.localtime(time.time()).tm_year
                                # real_month = time.localtime(time.time()).tm_mon
                                # if month > 1 and month < 12:
                                #     year = real_year
                                # else:
                                #     if month == real_month:
                                #         year = real_year
                                #     else:
                                #         year = real_year - 1
                                #
                                # if (year % 4) == 0 and (year % 100) != 0 or (year % 400) == 0:
                                #     is_leap = 0  # 閏年
                                # else:
                                #     is_leap = 1  # 平年
                                #46
                                code = i-34
                                code2=header_field_list[i]
                                code3=code2[3:]
                                if i==34:
                                    count = 34 + 7 * (i - 34) + 12
                                    sheet1.write_merge(0, 0, count, count + 6, header_field_list[i],for_header4)
                                    for num in range(7):
                                        date_str =  str(year1)+'/'+str(month) + '/' + str(day)  # 待定
                                        week_day = datetime.datetime(year1, month, day).weekday()  # *
                                        if num == 0:
                                            date_str2 = date_str
                                        if num == 6:
                                            # sheet1.col(count).hidden = False
                                            sheet1.col(count).show_auto_page_breaks = True  # 忽略
                                            date_str3 = date_str
                                            # sheet1.write(2, count,'Delta')
                                            sheet1.write_merge(1, 1, count + 1, count + 1, date_str2 + "-" + date_str3)
                                            sheet1.write_merge(0, 0, count + 1, count + 1, code3,for_header4)
                                            sheet1.write_merge(2, 2, count + 1, count + 1, 'Delta',for_header5)
                                        # else:
                                        #     sheet1.col(count).hidden = True
                                        if week_day == 0:
                                            week_day_str = u'週一'
                                        if week_day == 1:
                                            week_day_str = u'週二'
                                        if week_day == 2:
                                            week_day_str = u'週三'
                                        if week_day == 3:
                                            week_day_str = u'週四'
                                        if week_day == 4:
                                            week_day_str = u'週五'
                                        if week_day == 5:
                                            week_day_str = u'週六'
                                        if week_day == 6:
                                            week_day_str = u'週日'
                                        if week_day == 5 or week_day == 6:
                                            sheet1.write(2, count, week_day_str,for_header4)
                                            sheet1.write(1, count, date_str,for_header4)
                                        else:
                                            sheet1.write(2, count, week_day_str,for_header5)
                                            sheet1.write(1, count, date_str,for_header5)
                                        count += 1
                                        if ((
                                                                                month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12) and day < 31) \
                                                or ((
                                                                            month == 4 or month == 6 or month == 9 or month == 11) and day < 30) \
                                                or (month == 2 and is_leap == 0 and day < 29) \
                                                or (month == 2 and is_leap == 1 and day < 28):
                                            day += 1
                                        elif ((
                                                                              month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10) and day >= 31) \
                                                or ((
                                                                            month == 4 or month == 6 or month == 9 or month == 11) and day >= 30) \
                                                or (month == 2 and is_leap == 0 and day >= 29) \
                                                or (month == 2 and is_leap == 1 and day >= 28):
                                            month += 1
                                            day = 1
                                        elif month == 12 and day >= 31:
                                            month = 1
                                            day = 1
                                            year1 += 1
                                else:
                                    count = 34 + 7 * (i - 34)+12+code
                                    sheet1.write_merge(0, 0, count, count + 6, header_field_list[i],for_header4)
                                    for num in range(7):
                                        date_str = str(year1)+'/'+str(month) + '/' + str(day)  # 待定
                                        week_day = datetime.datetime(year1, month, day).weekday()  # *
                                        if num ==0:
                                            date_str2 = date_str
                                        if num == 6:
                                            # sheet1.col(count).hidden = False
                                            sheet1.col(count).show_auto_page_breaks = True  # 忽略
                                            date_str3 = date_str
                                            # sheet1.write(2, count,'Delta')
                                            sheet1.write_merge(1, 1, count+1,count+1,date_str2+"-"+date_str3)
                                            sheet1.write_merge(0, 0, count + 1, count + 1,code3,for_header4)
                                            sheet1.write_merge(2, 2, count + 1, count + 1, 'Delta',for_header5)
                                        # else:
                                        #     sheet1.col(count).hidden = True
                                        # else:
                                        #     sheet1.col(count).hidden = True
                                        # print week_day
                                        if week_day == 0:
                                            week_day_str = u'週一'
                                        if week_day == 1:
                                            week_day_str = u'週二'
                                        if week_day == 2:
                                            week_day_str = u'週三'
                                        if week_day == 3:
                                            week_day_str = u'週四'
                                        if week_day == 4:
                                            week_day_str = u'週五'
                                        if week_day == 5:
                                            week_day_str = u'週六'
                                        if week_day == 6:
                                            week_day_str = u'週日'
                                        if week_day == 5 or week_day == 6:
                                            sheet1.write(2, count, week_day_str,for_header4)
                                            sheet1.write(1, count, date_str,for_header4)
                                        else:
                                            sheet1.write(2, count, week_day_str,for_header5)
                                            sheet1.write(1, count, date_str,for_header5)
                                        count += 1
                                        if ((
                                                                                month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12) and day < 31) \
                                                or ((
                                                                    month == 4 or month == 6 or month == 9 or month == 11) and day < 30) \
                                                or (month == 2 and is_leap == 0 and day < 29) \
                                                or (month == 2 and is_leap == 1 and day < 28):
                                            day += 1
                                        elif ((
                                                                              month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10) and day >= 31) \
                                                or ((
                                                                    month == 4 or month == 6 or month == 9 or month == 11) and day >= 30) \
                                                or (month == 2 and is_leap == 0 and day >= 29) \
                                                or (month == 2 and is_leap == 1 and day >= 28):
                                            month += 1
                                            day = 1
                                        elif month == 12 and day >= 31:
                                            month = 1
                                            day = 1
                                            year1 += 1
                            elif i > 46 and i <= 50 :
                                    count = count + 1
                                    date_start =   str(year1)+'/'+str(month) + '/' + str(day)
                                    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                                        day -= 4
                                        # month+=1
                                        if day <= 0:
                                            day += 31
                                        elif day > 0 and month != 12:
                                            month += 1
                                        elif day > 0 and month == 12:
                                            month = 1
                                            year1 += 1


                                    elif month == 4 or month == 6 or month == 9 or month == 11:
                                        day -= 3
                                        if day <= 0:
                                            day += 30
                                        elif day > 0:
                                            month += 1

                                    elif month == 2 and is_leap == 0:
                                        day -= 2
                                        if day <= 0:
                                            day += 29
                                        elif day > 0:
                                            month = 3
                                    elif month == 2 and is_leap == 1:
                                        day-=1
                                        if day <= 0:
                                            day += 28
                                        elif day > 0:
                                            month = 3

                                    count2=count+1
                                    date_end = str(year1)+'/'+str(month) + '/' + str(day)
                                    sheet1.write(0, count, header_field_list[i],for_header4)
                                    sheet1.write(2, count, date_end,for_header5)
                                    sheet1.write(1, count, date_start)
                                    sheet1.write(0, count2, header_field_list[i], for_header4)
                                    sheet1.write(2, count2, 'Delta',for_header5)
                                    sheet1.write(1, count2, date_start+'-'+date_end)
                                    #     # sheet1.write(2, count, date_str, for_header3)
                                    count+=1
                                    # sheet1.write(2, count, date_str, for_header3)
                                    if ((
                                                                            month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12) and day < 31) \
                                            or ((month == 4 or month == 6 or month == 9 or month == 11) and day < 30) \
                                            or (month == 2 and is_leap == 0 and day < 29) \
                                            or (month == 2 and is_leap == 1 and day < 28):
                                        day += 1
                                    elif ((
                                                                          month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10) and day >= 31) \
                                            or ((month == 4 or month == 6 or month == 9 or month == 11) and day >= 30) \
                                            or (month == 2 and is_leap == 0 and day >= 29) \
                                            or (month == 2 and is_leap == 1 and day >= 28):
                                        month += 1
                                        day = 1
                                    elif month == 12 and day >= 31:
                                        month = 1
                                        day = 1
                                        year1 += 1
                            else:
                                count += 1
                                sheet1.write_merge(0, 2, count, count, header_field_list[i],for_header5)
                                # sheet1.write(3, 159, vendor_code)
                                # sheet1.write(3, 160, vendor_name)


                            # listlength =  len(traw_export)
                            r1=3
                            # r2=3+(listlength-1)
                            # for r in r2
                            r2=4

                            for traw_line2 in traw_export:  # for tconfirm_line in tconfirm_export:
                                for i in xrange(len(traw_line2.ids)):
                                        buyer = traw_line2.buyer_id.buyer_erp_id,' / ', traw_line2.buyer_id.buyer_name
                                        sheet1.write(r1, 0, buyer)
                                        sheet1.write(r1, 1, traw_line2.material_id.part_no)
                                        sheet1.write(r1, 2, 'Y')
                                        sheet1.write(r1, 3, traw_line2.description)
                                        # sheet1.write(r1, 4, traw_line2.total_open_po_qty)
                                        sheet1.write(r1, 4, traw_line2.open_po,for_header2)
                                        sheet1.write(r1, 5, traw_line2.intransit_qty,for_header2)  # 表身數字格式：黑字,  # ,##0.00
                                        sheet1.write(r1, 6, traw_line2.round_value)
                                        sheet1.write(r1, 7, traw_line2.leadtime)
                                        sheet1.write(r1, 8, traw_line2.qty_w1,for_header2)
                                        sheet1.write(r1, 9, traw_line2.qty_w1_r)
                                        sheet1.write(r1, 10, traw_line2.qty_w2)
                                        sheet1.write(r1, 11, traw_line2.qty_w3)
                                        sheet1.write(r1, 12, traw_line2.qty_w4)
                                        sheet1.write(r1, 13, traw_line2.qty_w5)
                                        sheet1.write(r1, 14, traw_line2.qty_w6)
                                        sheet1.write(r1, 15, traw_line2.qty_w7)
                                        sheet1.write(r1, 16, traw_line2.qty_w8)
                                        sheet1.write(r1, 17, traw_line2.qty_w9)
                                        sheet1.write(r1, 18, traw_line2.qty_w10)
                                        sheet1.write(r1, 19, traw_line2.qty_w11)
                                        sheet1.write(r1, 20, traw_line2.qty_w12)
                                        sheet1.write(r1, 21, traw_line2.qty_w13)
                                        sheet1.write(r1, 22, traw_line2.qty_m1)
                                        sheet1.write(r1, 23, traw_line2.qty_m2)
                                        sheet1.write(r1, 24, traw_line2.qty_m3)
                                        sheet1.write(r1, 25, traw_line2.qty_m4)
                                        sheet1.write(r1, 26, traw_line2.qty_m5)
                                        sheet1.write(r1, 27, traw_line2.qty_m6)
                                        sheet1.write(r1, 28, traw_line2.qty_m7)
                                        sheet1.write(r1, 29, traw_line2.qty_m8)
                                        sheet1.write(r1, 30, traw_line2.qty_m9)
                                        # sheet1.write(3, 159, vendor_code)
                                        # sheet1.write(3, 160, vendor_name)
                                        sheet1.write(r1, 159, traw_line2.vendor_id.vendor_code[4:])

                                        if traw_line2.vendor_id.name:
                                            vendor_name = traw_line2.vendor_id.name[:6]
                                        else:
                                            vendor_name = ''
                                        sheet1.write(r1, 160, vendor_name)

                                        sheet1.write(r1, 161, traw_line2.plant_id.plant_code)
                                        if traw_line2.storage_location_id.storage_location:
                                            sheet1.write(r1, 162, traw_line2.storage_location_id.storage_location)
                                        else:
                                            sheet1.write(r1, 162, '')
                                        sheet1.write(r1, 163, traw_line2.storage_location_id.CM_VENDOR)

                                        sheet1.write(r1, 158, traw_line2.version)
                                        sheet1.write(r1,53, xlwt.Formula("AU"+str(r2)+"+"+"AV"+str(r2)+"+"+"AW"+str(r2)+"+"+"AX"+str(r2)+"+"+"AY"+str(r2)+"+"+"AZ"+str(r2)+"+"+"BA"+str(r2)+"-"+"J"+str(r2)))
                                        sheet1.write(r1, 61, xlwt.Formula("BC"+str(r2)+"+"+"BD"+str(r2)+"+"+"BE"+str(r2)+"+"+"BF"+str(r2)+"+"+"BG"+str(r2)+"+"+"BH"+str(r2)+"+"+"BI"+str(r2)+"+"+"BB"+str(r2)+"-"+"K"+str(r2)))
                                        sheet1.write(r1, 69, xlwt.Formula("BK"+str(r2)+"+"+"BL"+str(r2)+"+"+"BM"+str(r2)+"+"+"BN"+str(r2)+"+"+"BO"+str(r2)+"+"+"BP"+str(r2)+"+"+"BQ"+str(r2)+"+"+"BJ"+str(r2)+"-"+"L"+str(r2)))
                                        sheet1.write(r1, 77, xlwt.Formula("BS"+str(r2)+"+"+"BT"+str(r2)+"+"+"BU"+str(r2)+"+"+"BV"+str(r2)+"+"+"BW"+str(r2)+"+"+"BX"+str(r2)+"+"+"BY"+str(r2)+"+"+"BR"+str(r2)+"-"+"M"+str(r2)))
                                        sheet1.write(r1, 85, xlwt.Formula("CA"+str(r2)+"+"+"CB"+str(r2)+"+"+"CC"+str(r2)+"+"+"CD"+str(r2)+"+"+"CE"+str(r2)+"+"+"CF"+str(r2)+"+"+"CG"+str(r2)+"+"+"BZ"+str(r2)+"-"+"N"+str(r2)))
                                        sheet1.write(r1, 93, xlwt.Formula("CI"+str(r2)+"+"+"CJ"+str(r2)+"+"+"CK"+str(r2)+"+"+"CL"+str(r2)+"+"+"CM"+str(r2)+"+"+"CN"+str(r2)+"+"+"CO"+str(r2)+"+"+"CH"+str(r2)+"-"+"O"+str(r2)))
                                        sheet1.write(r1, 101, xlwt.Formula("CQ"+str(r2)+"+"+"CR"+str(r2)+"+"+"CS"+str(r2)+"+"+"CT"+str(r2)+"+"+"CU"+str(r2)+"+"+"CV"+str(r2)+"+"+"CW"+str(r2)+"+"+"CP"+str(r2)+"-"+"P"+str(r2)))
                                        sheet1.write(r1, 109, xlwt.Formula("CY"+str(r2)+"+"+"CZ"+str(r2)+"+"+"DA"+str(r2)+"+"+"DB"+str(r2)+"+"+"DC"+str(r2)+"+"+"DD"+str(r2)+"+"+"DE"+str(r2)+"+"+"CX"+str(r2)+"-"+"Q"+str(r2)))
                                        sheet1.write(r1, 117, xlwt.Formula("DG"+str(r2)+"+"+"DH"+str(r2)+"+"+"DI"+str(r2)+"+"+"DJ"+str(r2)+"+"+"DK"+str(r2)+"+"+"DL"+str(r2)+"+"+"DM"+str(r2)+"+"+"DF"+str(r2)+"-"+"R"+str(r2)))
                                        sheet1.write(r1, 125, xlwt.Formula("DO"+str(r2)+"+"+"DP"+str(r2)+"+"+"DQ"+str(r2)+"+"+"DR"+str(r2)+"+"+"DS"+str(r2)+"+"+"DT"+str(r2)+"+"+"DU"+str(r2)+"+"+"DN"+str(r2)+"-"+"S"+str(r2)))
                                        sheet1.write(r1, 133, xlwt.Formula("DW"+str(r2)+"+"+"DX"+str(r2)+"+"+"DY"+str(r2)+"+"+"DZ"+str(r2)+"+"+"EA"+str(r2)+"+"+"EB"+str(r2)+"+"+"EC"+str(r2)+"+"+"DV"+str(r2)+"-"+"T"+str(r2)))
                                        sheet1.write(r1, 141, xlwt.Formula("EE"+str(r2)+"+"+"EF"+str(r2)+"+"+"EG"+str(r2)+"+"+"EH"+str(r2)+"+"+"EI"+str(r2)+"+"+"EJ"+str(r2)+"+"+"EK"+str(r2)+"+"+"ED"+str(r2)+"-"+"U"+str(r2)))
                                        sheet1.write(r1, 149, xlwt.Formula("EM"+str(r2)+"+"+"EN"+str(r2)+"+"+"EO"+str(r2)+"+"+"EP"+str(r2)+"+"+"EQ"+str(r2)+"+"+"ER"+str(r2)+"+"+"ES"+str(r2)+"+"+"EL"+str(r2)+"-"+"V"+str(r2)))
                                        sheet1.write(r1, 151, xlwt.Formula("EU"+str(r2)+"+"+"ET"+str(r2)+"-"+"W"+str(r2)))
                                        sheet1.write(r1, 153, xlwt.Formula("EW"+str(r2)+"+"+"EV"+str(r2)+"-"+"X"+str(r2)))
                                        sheet1.write(r1, 155, xlwt.Formula("EY"+str(r2)+"+"+"EX"+str(r2)+"-"+"Y"+str(r2)))
                                        sheet1.write(r1, 157, xlwt.Formula("FA"+str(r2)+"+"+"EZ"+str(r2)+"-"+"Z"+str(r2)))

















                                r1+=1
                                r2+=1
        wb1.save(output)
        vals = {
            'action_type':'Vendor Fill Form',
            'vendor_id':self.vendor_id.id
        }
        self.env['iac.supplier.key.action.log'].create(vals)
        self.env.cr.commit()
        vals = {
            'name': 'vendor forecast delivery report',
            'datas_fname': 'vendor_forecast_delivery_report.xls',
            'description': 'Vendor Forecast Delivery Report',
            'type': 'binary',
            'db_datas': base64.encodestring(output.getvalue()),
        }
        file = self.env['ir.attachment'].sudo().create(vals)
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s.xls' % (file.id, file.id,),
            'target': 'new',
        }


        return action

        # # 設定欄寬
        # for i in range(0, 51):
        #     sheet1.col(i).width = 3000  # 256* 11.7 =3000
        # for i in [2, 11, 45, 47]:
        #     sheet1.col(i).width = 4400  # 256* 17
        # for i in [3, 48, 49]:
        #     sheet1.col(i).width = 9300  # 256* 36




        
