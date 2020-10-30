# -*- coding: utf-8 -*-

import json
import xlwt
import time,base64
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


_logger = logging.getLogger(__name__)

class IacTDeliveryHoliday(models.Model):

    _name = 'iac.tdelivery.holiday'

    plant = fields.Char()
    holiday = fields.Date()
    cdt = fields.Datetime()
    uploader = fields.Char()

class IacBuyerFCSTDeliveryReportWizardBK(models.TransientModel):
    """mm下载rfq,选择查询条件进行下载：
    """
    _name = 'iac.buyer.fcst.delivery.report.wizard.bk'
    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst',index=True)
    # buyer_id = fields.Many2one('buyer.code', string='Buyer Code',domain=lambda self: [('id', 'in', self.env.user.buyer_id_list)], index=True)
    division_id = fields.Many2one('division.code', string='Division Info',index=True)
    vendor_id = fields.Many2one('iac.vendor',string='Vendor Code',index=True)

    @api.multi
    def action_confirm(self):
        """  Buyer Fill Form
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        header_field_list = []
        header_field_list = [u'採購代碼','Division',u'料號','Key Part',u'品名',u'庫存量','total open po qty',u'在途量',u'廠商代碼',
                             u'廠商名稱','Remark','W1  ETA','W2  ETA','W3  ETA','W4  ETA','W5  ETA','W6  ETA','W7  ETA',
                             'W8  ETA','W9  ETA','W10  ETA','W11  ETA','W12  ETA','W13  ETA','W14-W17','W18-W21','W22-W25',
                             'W26-W29',u'最后上传时间',u'上傳帳號','Plant','Location']

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)
        sheet1.col(0).width = 3000
        sheet1.col(2).width = 4000
        sheet1.col(6).width = 5000
        sheet1.col(8).width = 3000
        sheet1.col(9).width = 3000
        sheet1.col(10).width = 3000
        #sheet1.col(11).width = 0
        sheet1.col(106).width = 4000
        #sheet1.col(106).width = 3000
        # 凍結視窗
        sheet1.panes_frozen = True
        sheet1.horz_split_pos = 3  # 行
        sheet1.vert_split_pos = 10  # 列

        for_header1 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        for_header2 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 3')
        for_header3 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  )
        for_header4 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        #工作日的日期格式
        style1 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                             'align: horiz center;')
        style1.num_format_str = 'yyyy/m/d'
        #週末的日期樣式
        style2 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                             'align: horiz center;'
                             'pattern: pattern solid, pattern_fore_colour 22')
        style2.num_format_str = 'yyyy/m/d'
        style3 = xlwt.easyxf('pattern: pattern solid, pattern_fore_colour 22')
        pattern_color = []

        for wizard in self:
            domain = []
            # user input的查詢條件 ____________s
            domain += [('status', '=', 'T')]  # 只顯示  status = T: true有效
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.division_id:
                domain += [('division_id', '=', wizard.division_id.id)]
            tconfirm_export = self.env['iac.tconfirm.data'].sudo().search(domain)

            if not tconfirm_export:
                raise UserError('查無資料! ')
            else:
                #print tconfirm_export[0].fpversion
                qty_w1_r = self.env['iac.tcolumn.title'].sudo().search([('fpversion','=',tconfirm_export[0].fpversion)]).qty_w1_r
                print '*109' ,tconfirm_export[0].fpversion ,',',qty_w1_r[5:9]

                month = int(qty_w1_r[5:7])
                day = int(qty_w1_r[7:9])
                #print month,day
                real_year = time.localtime(time.time()).tm_year
                real_month = time.localtime(time.time()).tm_mon
                if month >1 and month<12:
                    year = real_year
                else:
                    if month == real_month:
                        year = real_year
                    else:
                        if month ==1:
                            year=real_year
                        elif month==12:
                            year = real_year-1

                if  (year % 4) == 0 and (year % 100) != 0 or (year % 400) == 0:
                    is_leap = 0 #閏年
                else:
                    is_leap = 1 #平年
                        # 写excel文件的表头
                date_time_list = []
                # 记录最后4个日期段
                date_time_between = []
                for i in xrange(len(header_field_list)):
                    if i <= 10:
                        # print header_field_list[i]
                        sheet1.write_merge(0, 2, i, i, header_field_list[i], for_header1)
                    elif i > 10 and i <= 24:
                        # print header_field_list[i]
                        count = 11 + 7 * (i - 11)
                        if i<24:
                            sheet1.write_merge(0, 0, count, count + 6, header_field_list[i], for_header2)
                            for num in range(7):
                                # if num == 6:
                                #     sheet1.col(count).hidden = False
                                #
                                # else:
                                #     sheet1.col(count).hidden = True
                                date_time = datetime.datetime(year, month, day)
                                date_time_list.append(date_time)

                                week_day = datetime.datetime(year,month,day).weekday()
                                #print week_day
                                if week_day==0:
                                    week_day_str = u'週一'
                                if week_day==1:
                                    week_day_str = u'週二'
                                if week_day==2:
                                    week_day_str = u'週三'
                                if week_day==3:
                                    week_day_str = u'週四'
                                if week_day==4:
                                    week_day_str = u'週五'
                                if week_day==5:
                                    week_day_str = u'週六'
                                if week_day==6:
                                    week_day_str = u'週日'
                                if week_day == 5 or week_day == 6:
                                    pattern_color.append(count)
                                    sheet1.write(1, count, week_day_str, for_header4)
                                    sheet1.write(2, count, date_time, style2)
                                else:
                                    sheet1.write(1, count, week_day_str, for_header3)
                                    sheet1.write(2, count, date_time, style1)
                                count += 1
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
                                    year += 1

                        else:

                            date_start = datetime.datetime(year, month, day)
                            date_time_between.append(date_start)


                            if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                                day -= 4

                                #month+=1
                                if day <= 0:
                                    day += 31
                                elif day >0 and month !=12:
                                    month+=1
                                elif day>0 and month==12:
                                    month = 1
                                    year +=1


                            elif month == 4 or month == 6 or month == 9 or month == 11:
                                day -= 3

                                if day <= 0:
                                    day += 30
                                elif day >0:
                                    month+=1

                            elif month == 2 and is_leap == 0:
                                day -= 2

                                if day <= 0:
                                    day += 29
                                elif day >0:
                                    month = 3
                            elif month == 2 and is_leap == 1:
                                day -= 1
                                if day <= 0:
                                    day += 28
                                elif day > 0:
                                    month = 3
                            #date_end = str(year)+ '/' +str(month) + '/' + str(day)
                            date_end = datetime.datetime(year, month, day)
                            date_time_between.append(date_end)
                            sheet1.write(0, count, header_field_list[i], for_header2)
                            sheet1.write(1, count, date_end, style1)
                            sheet1.write(2, count, date_start, style1)
                    elif i >24 and i<=27:
                        # print header_field_list[i]
                        count = count + 1
                        # print count
                        #print month,day,year
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
                            year += 1
                        #date_start = str(year)+ '/' +str(month) + '/' + str(day)
                        date_start = datetime.datetime(year, month, day)
                        # print date_start
                        # print date_start+3
                        date_time_between.append(date_start)
                        if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                            day -= 4

                            # month+=1
                            if day <= 0:
                                day += 31
                            elif day > 0 and month != 12:
                                month += 1
                            elif day > 0 and month == 12:
                                month = 1
                                year += 1


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
                            day -= 1
                            if day <= 0:
                                day += 28
                            elif day > 0:
                                month = 3
                        #date_end = str(year)+ '/' +str(month) + '/' + str(day)
                        date_end = datetime.datetime(year, month, day)
                        date_time_between.append(date_end)
                        sheet1.write(0, count, header_field_list[i],for_header2)
                        sheet1.write(1, count, date_end, style1)
                        sheet1.write(2, count, date_start, style1)
                        #sheet1.write(2, count, date_str, for_header3)
                    else:
                        count += 1
                        sheet1.write_merge(0, 2, count, count, header_field_list[i], for_header1)

        r = 3
        #print pattern_color
        #print date_time_list
        holiday_list = []
        for item in self.env['iac.tdelivery.holiday'].sudo().search([]):
            holiday_list.append(item.holiday)
        # print holiday_list
        for tconfirm_line in tconfirm_export:

            eta_trans = self.env['iac.control.table.real'].sudo().search(
                [('vendor', '=', tconfirm_line.vendor_id.vendor_code),
                 ('buyer_id', '=', tconfirm_line.buyer_id.id), ('plant_id', '=', tconfirm_line.plant_id.id)]).eta_trans
            sheet1.write(r, 0, tconfirm_line.buyer_id.buyer_erp_id)
            sheet1.write(r, 1, tconfirm_line.division_id.division)
            sheet1.write(r, 2, tconfirm_line.material_id.part_no)
            sheet1.write(r, 3, 'Y')
            sheet1.write(r, 4, tconfirm_line.description)
            sheet1.write(r, 5, tconfirm_line.stock,for_body1)
            sheet1.write(r, 6, tconfirm_line.open_po,for_body1)  # 表身數字格式：黑字,  # ,##0.00
            sheet1.write(r, 7, tconfirm_line.intransit_qty,for_body1)
            sheet1.write(r, 8, tconfirm_line.vendor_id.vendor_code[4:])

            if tconfirm_line.vendor_id.name:
                vendor_name = tconfirm_line.vendor_id.name[:6]
            else:
                vendor_name = ''
            sheet1.write(r, 9, vendor_name)


            sheet1.write(r, 108, tconfirm_line.plant_id.plant_code)  #plant 181212 ning add
            # if tconfirm_line.storage_location_id.storage_location:
            sheet1.write(r, 109, tconfirm_line.storage_location_id.storage_location)   #location 181212 ning add
            # else:
            #     sheet1.write(r, 109, "")
            # if tconfirm_line.remark:  # Remark
            #     sheet1.write(r, 10, tconfirm_line.remark)
            #
            #
            # else:
            #     sheet1.write(r, 10, "")
            #
            # sheet1.write(r, 106, tconfirm_line.create_date)
            # sheet1.write(r, 107, tconfirm_line.create_uid.name)
            for item in pattern_color:
                sheet1.write(r,item,'',style3)
            self._cr.execute(" select  type,cdt  from (SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,storage_location_id,status  " \
                            "from iac_tdelivery_edi EDI  where EDI.material_id = %s and EDI.plant_id = %s and EDI.vendor_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
                             " SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
                             " from iac_tvendor_upload Vendor where Vendor.material_id = %s and Vendor.plant_id = %s and Vendor.vendor_id = %s and Vendor.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
                             " SELECT 'iac_tdelivery_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
                             " from  iac_tdelivery_upload Buyer   where Buyer.material_id = %s and Buyer.plant_id = %s and Buyer.vendor_id = %s and Buyer.storage_location_id = %s group by material_id,plant_id,vendor_id,storage_location_id,status) a " \
                             " where  status='T' order by Cdt desc LIMIT 1"
                             , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id,tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))


            for item in self.env.cr.dictfetchall():
                #print item['type']
                if item['type'] =='iac_tdelivery_edi':
                    # self._cr.execute(
                    #     " select  shipping_date,qty from " + item[
                    #         'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and status='T'" \
                    #     , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id))

                    self._cr.execute(
                        " select  distinct shipping_date,qty from " + item[
                            'type'] + " a where valid=1 and exists (select 1 from iac_tdelivery_edi b where a.plant_id=b.plant_id and a.material_id=b.material_id and a.vendor_id=b.vendor_id  having SUBSTRING(a.FCST_version,4,12)=MAX(SUBSTRING(b.FCST_version,4,12)))" \
                                      "and a.material_id = %s and plant_id = %s and a.vendor_id =%s and status='T'" \
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id))

                    for dic in self.env.cr.dictfetchall():
                        # print dic
                        now_date = datetime.datetime(int(dic['shipping_date'][0:4]), int(dic['shipping_date'][5:7]),
                                                     int(dic['shipping_date'][8:10]))
                        now_date_1 = now_date+datetime.timedelta(days=eta_trans)
                        # print now_date_1
                        for record in holiday_list:
                            record_date =  datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]))
                            if now_date_1 == record_date:
                                now_date_1 = now_date_1+datetime.timedelta(days=1)
                        # print now_date_1
                        for i in range(len(date_time_list)):
                            # print date_time_list[i]

                            if now_date_1 == date_time_list[i]:
                                if (i + 11) in pattern_color:
                                    sheet1.write(r, i + 11, dic['qty'], style3)
                                else:
                                    sheet1.write(r, i + 11, dic['qty'])

                        index = 0
                        for count_index in range(4):
                            if now_date_1 >= date_time_between[index] and now_date_1 <= date_time_between[index + 1]:
                                sheet1.write(r, count_index + 102, dic['qty'])
                                break
                            else:
                                index += 2

                    self._cr.execute(
                        " select cdt,buyer_remark,storage_location_id from   (select max(cdt) as cdt,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
                        " from  " + item[
                            'type'] + "  group by  buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a " \
                                      " where a.material_id = %s  and a.plant_id = %s  and vendor_id = %s   and status = 'T' order by cdt desc LIMIT 1  "
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id))
                    for dic1 in self.env.cr.dictfetchall():
                        sheet1.write(r, 10, dic1['buyer_remark'])
                        sheet1.write(r, 106, dic1['cdt'])
                        sheet1.write(r, 107, 'SCM b2b')
                    # if dic1['storage_location_id']:
                    #     storage_location = self.env['iac.storage.location.address'].browse(dic1['storage_location_id']).storage_location
                    #     sheet1.write(r, 109, storage_location)
                    # else:
                    #     sheet1.write(r, 109, 'SW01')
                    # sheet1.write(r, 109, tconfirm_line.storage_location_id.storage_location)

                if item['type'] =='iac_tdelivery_upload':
                    self._cr.execute(
                        " select  shipping_date,qty from "+item['type']+" where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))
                    for dic in self.env.cr.dictfetchall():
                        #print dic
                        now_date = datetime.datetime(int(dic['shipping_date'][0:4]), int(dic['shipping_date'][5:7]),
                                                     int(dic['shipping_date'][8:10]))
                        for i in range(len(date_time_list)):
                            #print date_time_list[i]

                            if now_date == date_time_list[i]:

                                if (i + 11) in pattern_color:
                                    sheet1.write(r, i + 11, dic['qty'],style3)
                                else:
                                    sheet1.write(r, i + 11, dic['qty'])

                        index = 0
                        for count_index in range(4):
                            if now_date >= date_time_between[index] and now_date <= date_time_between[index + 1]:
                                sheet1.write(r, count_index + 102, dic['qty'])
                                break
                            else:
                                index += 2

                    self._cr.execute(
                        " select a.cdt,a.write_uid,a.buyer_remark,u.login  from   (select max(create_date) as cdt,write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
		                " from  " +item['type']+ "  group by  write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a, res_users u " \
                        " where a.material_id = %s  and a.plant_id = %s  and a.vendor_id = %s  and a.storage_location_id=%s and a.status = 'T' and a.write_uid=u.id  order by a.cdt desc LIMIT 1  "
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id,tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))
                    for dic1 in self.env.cr.dictfetchall():
                        sheet1.write(r,10,dic1['buyer_remark'])
                        sheet1.write(r,106,dic1['cdt'])
                        sheet1.write(r,107,dic1['login'])
                    # sheet1.write(r, 109, tconfirm_line.storage_location_id.storage_location)

                if item['type'] == 'iac_tvendor_upload':
                    self._cr.execute(
                        " select  shipping_date,qty from " + item[
                            'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))
                    for dic in self.env.cr.dictfetchall():
                        now_date = datetime.datetime(int(dic['shipping_date'][0:4]), int(dic['shipping_date'][5:7]),
                                                     int(dic['shipping_date'][8:10]))
                        now_date_1 = now_date + datetime.timedelta(days=eta_trans)

                        for record in holiday_list:
                            record_date =  datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]))
                            if now_date_1 == record_date:
                                now_date_1 = now_date_1+datetime.timedelta(days=1)
                        for i in range(len(date_time_list)):
                            if now_date_1 == date_time_list[i]:

                                if (i + 11) in pattern_color:
                                    sheet1.write(r, i + 11, dic['qty'],style3)
                                else:
                                    sheet1.write(r, i + 11, dic['qty'])
                        index = 0
                        for count_index in range(4):
                            if now_date_1>=date_time_between[index] and now_date_1<=date_time_between[index+1]:
                                sheet1.write(r, count_index+102, dic['qty'])
                                break
                            else:
                                index+=2


                    self._cr.execute(
                        " select a.cdt,a.write_uid,a.buyer_remark,u.login  from   (select max(create_date) as cdt,write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
                        " from  " + item[
                            'type'] + "  group by  write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a, res_users u " \
                                      " where a.material_id = %s  and a.plant_id = %s  and a.vendor_id = %s and a.storage_location_id = %s  and a.status = 'T' and a.write_uid=u.id  order by a.cdt desc LIMIT 1  "
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))
                    for dic1 in self.env.cr.dictfetchall():
                        sheet1.write(r, 10, dic1['buyer_remark'])
                        sheet1.write(r, 106, dic1['cdt'])
                        sheet1.write(r, 107, dic1['login'])
                    # sheet1.write(r, 109, tconfirm_line.storage_location_id.storage_location)
            #
            # if item == 99:
            #     sheet1.write(r, 109, 'SW01')

            r += 1

        wb2.save(output)

        # 文件输出成功之后,跳转链接，浏览器下载文件
        vals = {
            'name': 'buyer_fcst_delivery_report',
            'datas_fname': 'buyer_fcst_delivery_report.xls',
            'description': 'Buyer FCST Delivery Report',
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