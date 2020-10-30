# -*- coding: utf-8 -*-

import xlwt
import time,base64
import datetime
from odoo.exceptions import UserError
from odoo import models, fields, api
from StringIO import StringIO

class IacTDeliveryHoliday(models.Model):

    _name = 'iac.tdelivery.holiday'

    plant = fields.Char()
    holiday = fields.Date()
    cdt = fields.Datetime()
    uploader = fields.Char()

class IacBuyerFcstSetting(models.Model):
    #报表的配置表
    _name = 'iac.buyer.fcst.setting'

    title = fields.Char()  #excel上的字段名
    merged = fields.Char()  #判断是否为行合并字段，如果是初始化为X
    column_begin = fields.Integer() #起始的列号
    column_end = fields.Integer()  # 结束的列号
    interval = fields.Integer() #时间间隔，如果是日期字段则必填
    begin_date = fields.Date()  #开始日期
    end_date = fields.Date()    #结束日期
    pattern_color = fields.Char()       #背景色 如果是日期字段，该颜色只维护excel第一行的颜色
    font_color = fields.Char()          #字体色 如果是日期字段，该颜色只维护excel第一行的颜色
    num_format_flag = fields.Boolean()  #判断该字段的值是否需要千分位
    source_field_name = fields.Char()   #对应iac_tconfirm_data表里具体的字段名，如果需要表中取值必填
    source_field_type = fields.Char()   #如果是many2one字段必填
    frozen_flag = fields.Boolean()      #是否根据该字段冻结视窗（只有一个字段）


class IacBuyerFCSTDeliveryReportWizard(models.TransientModel):
    _name = 'iac.buyer.fcst.delivery.report.wizard'
    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst',index=True)
    division_id = fields.Many2one('division.code', string='Division Info',index=True)
    vendor_id = fields.Many2one('iac.vendor',string='Vendor Code',index=True)

    #根据传入字段名和模型字符串获取起始列号
    @api.multi
    def get_begin_column_by_name(self,name,model_str):
        return self.env[model_str].search([('title','=',name)]).column_begin

    #字体蓝色
    #获取日期字段第2行和第3行的格式
    @api.multi
    def get_style_except_first(self):
        return xlwt.easyxf('font:bold 1,color blue,height 200;'
                             'align: horiz center;')

    #字体蓝色，有背景色
    #周末两天的格式单独写（只包含日期字段第2行和第3行的格式）
    def get_style_on_weekend(self):
        return xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')

    #周末有数量时的格式
    def get_style_on_weekend_number(self):
        return xlwt.easyxf('pattern: pattern solid, pattern_fore_colour 22')

    # 根据字体颜色和背景颜色获取字段的格式（如果是日期类型，只维护excel第一行的格式）
    @api.multi
    def get_type_by_color(self, font_color,pattern_color):
        if font_color and pattern_color:
            return xlwt.easyxf('font:bold 1,color %s,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour %s' % (font_color,pattern_color))
        if font_color and not pattern_color:
            return xlwt.easyxf('font:bold 1,color %s,height 200;'
                               'align: horiz center,vertical center;' % font_color)
        if not font_color and pattern_color:
            return xlwt.easyxf('font:bold 1,height 200;'
                               'align: horiz center,vertical center;'
                               'pattern: pattern solid, pattern_fore_colour %s' % pattern_color)
        if not font_color and not pattern_color:
            return xlwt.easyxf('font:bold 1,height 200;'
                               'align: horiz center,vertical center;')

    #根据传入的字符串格式的日期返回周几
    def get_weekday_by_date_str(self,date_str):
        #建立字典来存weekday返回值和周几的对照关系
        week_dic = {0:u'週一',1:u'週二',2:u'週三',3:u'週四',4:u'週五',5:u'週六',6:u'週日'}
        #将传入的字符串转成日期格式
        date = datetime.datetime.strptime(date_str,'%Y-%m-%d')
        week = date.weekday()
        return week_dic[week]

    # 传参为配置表对象，confirm data对象，excel页签，行数，显示的格式
    @api.multi
    def write_confirm_data(self, item, tconfirm_line, sheet, row,style):
        # 先判断该字段是否需要从confirm data表中抓值
        if item.source_field_name:
            if item.source_field_type == 'many2one':
                tconfirm_obj = tconfirm_line
                # 如果是many2one字段，则根据.来拆分字段
                field_list = item.source_field_name.split('.')
                for field in field_list:
                    tconfirm_obj = tconfirm_obj[field]
            else:
                tconfirm_obj = tconfirm_line[item.source_field_name]
        else:
            return
        if item.title == '廠商代碼':
            sheet.write(row, item.column_begin, tconfirm_obj[4:])
        elif item.title == '廠商名稱':
            sheet.write(row, item.column_begin, tconfirm_obj[:6])
        else:
            if style:
                sheet.write(row, item.column_begin, tconfirm_obj,style)
            else:
                sheet.write(row, item.column_begin, tconfirm_obj)

    #写入交期下所有的数量
    #传参为confirm data对象，eta_trans，假期字符串的集合，excel的sheet页签，行数
    @api.multi
    def write_all_qty(self,tconfirm_line,eta_trans,holiday_list,sheet,row,style):
        self._cr.execute(
            " select  type,cdt  from (SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,storage_location_id,status  " \
            "from iac_tdelivery_edi EDI  where EDI.material_id = %s and EDI.plant_id = %s and EDI.vendor_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
            " SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
            " from iac_tvendor_upload Vendor where Vendor.material_id = %s and Vendor.plant_id = %s and Vendor.vendor_id = %s and Vendor.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
            " SELECT 'iac_tdelivery_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
            " from  iac_tdelivery_upload Buyer   where Buyer.material_id = %s and Buyer.plant_id = %s and Buyer.vendor_id = %s and Buyer.storage_location_id = %s group by material_id,plant_id,vendor_id,storage_location_id,status) a " \
            " where  status='T' order by Cdt desc LIMIT 1"
            , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
               tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
               tconfirm_line.storage_location_id.id, tconfirm_line.material_id.id, tconfirm_line.plant_id.id,
               tconfirm_line.vendor_id.id, tconfirm_line.storage_location_id.id))

        for item in self.env.cr.dictfetchall():
            # print item['type']
            if item['type'] == 'iac_tdelivery_edi':
                self._cr.execute(
                    " select  distinct shipping_date,qty from " + item[
                        'type'] + " a where valid=1 and exists (select 1 from iac_tdelivery_edi b where a.plant_id=b.plant_id and a.material_id=b.material_id and a.vendor_id=b.vendor_id  having SUBSTRING(a.FCST_version,4,12)=MAX(SUBSTRING(b.FCST_version,4,12)))" \
                                  "and a.material_id = %s and plant_id = %s and a.vendor_id =%s and status='T'" \
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id))

                for dic in self.env.cr.dictfetchall():
                    # print dic
                    now_date = datetime.datetime.strptime(dic['shipping_date'],'%Y-%m-%d')
                    #抓出来的shipping date要加上eta trans
                    now_date_1 = now_date + datetime.timedelta(days=eta_trans)
                    # print now_date_1
                    for record in holiday_list:
                        record_date = datetime.datetime.strptime(record,'%Y-%m-%d')
                        if now_date_1 == record_date:
                            #如果日期在假期范围内，则往后推1天
                            now_date_1 = now_date_1 + datetime.timedelta(days=1)
                    # print now_date_1
                    #抓出所有的日期字段
                    for buyer_fcst in self.env['iac.buyer.fcst.setting'].search([('interval', '!=', 0)],
                                                                                order='column_begin'):
                        #根据字段名和模型名获取开始和结束日期
                        begin_date, end_date = self.env['iac.vendor.psi.report.wizard'].get_date_by_name(buyer_fcst.title, 'iac.buyer.fcst.setting')
                        if now_date_1 >= begin_date and now_date_1 <= end_date:
                            #如果当前日期在日期范围内且开始列号等于结束列号，则说明是后4个月，qty直接写入
                            if buyer_fcst.column_begin == buyer_fcst.column_end:
                                sheet.write(row,buyer_fcst.column_begin,dic['qty'])
                            else:
                                #获取当前日期的列号
                                column = buyer_fcst.column_begin + (now_date_1-begin_date).days
                                date_str = datetime.datetime.strftime(now_date_1,'%Y-%m-%d')
                                #判断当前日期是周几
                                weekday = self.get_weekday_by_date_str(date_str)
                                if weekday == u'週六' or weekday == u'週日':
                                    sheet.write(row,column,dic['qty'],style)
                                else:
                                    sheet.write(row, column, dic['qty'])


                self._cr.execute(
                    " select cdt,buyer_remark,storage_location_id from   (select max(cdt) as cdt,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
                    " from  " + item[
                        'type'] + "  group by  buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a " \
                                  " where a.material_id = %s  and a.plant_id = %s  and vendor_id = %s   and status = 'T' order by cdt desc LIMIT 1  "
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id))
                for dic1 in self.env.cr.dictfetchall():
                    sheet.write(row, self.get_begin_column_by_name('Remark','iac.buyer.fcst.setting'), dic1['buyer_remark'])
                    sheet.write(row, self.get_begin_column_by_name('最后上传时间','iac.buyer.fcst.setting'), dic1['cdt'])
                    sheet.write(row, self.get_begin_column_by_name('上傳帳號','iac.buyer.fcst.setting'), 'SCM b2b')

            if item['type'] == 'iac_tdelivery_upload':
                self._cr.execute(
                    " select  shipping_date,qty from " + item[
                        'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))
                for dic in self.env.cr.dictfetchall():
                    # print dic
                    now_date = datetime.datetime.strptime(dic['shipping_date'], '%Y-%m-%d')
                    # 抓出所有的日期字段
                    for buyer_fcst in self.env['iac.buyer.fcst.setting'].search([('interval', '!=', 0)],
                                                                                order='column_begin'):
                        # 根据字段名和模型名获取开始和结束日期
                        begin_date, end_date = self.env['iac.vendor.psi.report.wizard'].get_date_by_name(buyer_fcst.title, 'iac.buyer.fcst.setting')
                        if now_date >= begin_date and now_date <= end_date:
                            # 如果当前日期在日期范围内且开始列号等于结束列号，则说明是后4个月，qty直接写入
                            if buyer_fcst.column_begin == buyer_fcst.column_end:
                                sheet.write(row,buyer_fcst.column_begin,dic['qty'])
                            else:
                                # 获取当前日期的列号
                                column = buyer_fcst.column_begin + (now_date-begin_date).days
                                date_str = datetime.datetime.strftime(now_date, '%Y-%m-%d')
                                # 判断当前日期是周几
                                weekday = self.get_weekday_by_date_str(date_str)
                                if weekday == u'週六' or weekday == u'週日':
                                    sheet.write(row,column,dic['qty'],style)
                                else:
                                    sheet.write(row, column, dic['qty'])

                self._cr.execute(
                    " select a.cdt,a.write_uid,a.buyer_remark,u.login  from   (select max(create_date) as cdt,write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
                    " from  " + item[
                        'type'] + "  group by  write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a, res_users u " \
                                  " where a.material_id = %s  and a.plant_id = %s  and a.vendor_id = %s  and a.storage_location_id=%s and a.status = 'T' and a.write_uid=u.id  order by a.cdt desc LIMIT 1  "
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))
                for dic1 in self.env.cr.dictfetchall():
                    sheet.write(row, self.get_begin_column_by_name('Remark','iac.buyer.fcst.setting'), dic1['buyer_remark'])
                    sheet.write(row, self.get_begin_column_by_name('最后上传时间','iac.buyer.fcst.setting'), dic1['cdt'])
                    sheet.write(row, self.get_begin_column_by_name('上傳帳號','iac.buyer.fcst.setting'), dic1['login'])
                    # sheet1.write(r, 109, tconfirm_line.storage_location_id.storage_location)

            if item['type'] == 'iac_tvendor_upload':
                self._cr.execute(
                    " select  shipping_date,qty from " + item[
                        'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))
                for dic in self.env.cr.dictfetchall():
                    now_date = datetime.datetime.strptime(dic['shipping_date'], '%Y-%m-%d')
                    # 抓出来的shipping date要加上eta trans
                    now_date_1 = now_date + datetime.timedelta(days=eta_trans)

                    for record in holiday_list:
                        record_date = datetime.datetime.strptime(record, '%Y-%m-%d')
                        if now_date_1 == record_date:
                            # 如果日期在假期范围内，则往后推1天
                            now_date_1 = now_date_1 + datetime.timedelta(days=1)
                    # 抓出所有的日期字段
                    for buyer_fcst in self.env['iac.buyer.fcst.setting'].search([('interval', '!=', 0)],
                                                                                order='column_begin'):
                        # 根据字段名和模型名获取开始和结束日期
                        begin_date, end_date = self.env['iac.vendor.psi.report.wizard'].get_date_by_name(buyer_fcst.title, 'iac.buyer.fcst.setting')
                        if now_date_1 >= begin_date and now_date_1 <= end_date:
                            # 如果当前日期在日期范围内且开始列号等于结束列号，则说明是后4个月，qty直接写入
                            if buyer_fcst.column_begin == buyer_fcst.column_end:
                                sheet.write(row,buyer_fcst.column_begin,dic['qty'])
                            else:
                                # 获取当前日期的列号
                                column = buyer_fcst.column_begin + (now_date_1-begin_date).days
                                date_str = datetime.datetime.strftime(now_date_1, '%Y-%m-%d')
                                # 判断当前日期是周几
                                weekday = self.get_weekday_by_date_str(date_str)
                                if weekday == u'週六' or weekday == u'週日':
                                    sheet.write(row,column,dic['qty'],style)
                                else:
                                    sheet.write(row,column,dic['qty'])

                self._cr.execute(
                    " select a.cdt,a.write_uid,a.buyer_remark,u.login  from   (select max(create_date) as cdt,write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status " \
                    " from  " + item[
                        'type'] + "  group by  write_uid,buyer_remark,material_id,plant_id,vendor_id,storage_location_id,status) a, res_users u " \
                                  " where a.material_id = %s  and a.plant_id = %s  and a.vendor_id = %s and a.storage_location_id = %s  and a.status = 'T' and a.write_uid=u.id  order by a.cdt desc LIMIT 1  "
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))
                for dic1 in self.env.cr.dictfetchall():
                    sheet.write(row, self.get_begin_column_by_name('Remark','iac.buyer.fcst.setting'), dic1['buyer_remark'])
                    sheet.write(row, self.get_begin_column_by_name('最后上传时间','iac.buyer.fcst.setting'), dic1['cdt'])
                    sheet.write(row, self.get_begin_column_by_name('上傳帳號','iac.buyer.fcst.setting'), dic1['login'])


    @api.multi
    def action_confirm(self):
        """  Buyer Fill Form
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

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)

        #抓取到冻结视窗字段的列号
        # column = self.env['iac.buyer.fcst.setting'].search([('frozen_flag','=','t')]).column_begin
        # 凍結視窗
        sheet1.panes_frozen = True
        sheet1.horz_split_pos = 3  # 行
        sheet1.vert_split_pos = 10
        # sheet1.vert_split_pos = column+1  # 列
        #字体黑色居中，背景色灰色
        for_header1 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        #字体蓝色居中，背景色绿色
        for_header2 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 3')
        #字体蓝色居中
        for_header3 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  )
        #字体蓝色居中，背景色灰色
        for_header4 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        #千分位
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        #背景色灰色
        style3 = xlwt.easyxf('pattern: pattern solid, pattern_fore_colour 22')
        #将所有周末的列号存入，来判断格式
        pattern_color = []
        # 每个字段的宽度是3000
        for i in range(self.env['iac.buyer.fcst.setting'].search([],order='column_end desc',limit=1).column_end+1):
            sheet1.col(i).width = 3000

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
                for tconfirm in tconfirm_export:
                    plant_code = tconfirm.plant_id.plant_code
                    break
                # 将所有的title写入excel
                for item in self.env['iac.buyer.fcst.setting'].search([]):
                    if item.merged == 'X':
                        sheet1.write_merge(0, 2, item.column_begin, item.column_end, item.title,for_header1)
                    else:
                        sheet1.write_merge(0,0, item.column_begin, item.column_end,item.title, for_header2)
                        #列号相同说明是后4个月
                        if item.column_begin == item.column_end:
                            sheet1.write(1,item.column_begin,item.end_date.replace('-','/'),for_header3)
                            sheet1.write(2, item.column_begin, item.begin_date.replace('-','/'),for_header3)
                        else:
                            column = item.column_begin
                            date_str = item.begin_date
                            while column<=item.column_end:
                                #如果是周末，格式带有背景色
                                if self.get_weekday_by_date_str(date_str) == u'週六' or self.get_weekday_by_date_str(date_str) == u'週日':
                                    #将周末的列号存入list
                                    pattern_color.append(column)
                                    sheet1.write(1, column, self.get_weekday_by_date_str(date_str),
                                                 for_header4)
                                    sheet1.write(2, column, date_str.replace('-', '/'), for_header4)
                                else:
                                    sheet1.write(1,column,self.get_weekday_by_date_str(date_str),for_header3)
                                    sheet1.write(2,column,date_str.replace('-','/'),for_header3)
                                column+=1
                                date = datetime.datetime.strptime(date_str,'%Y-%m-%d')+datetime.timedelta(days=1)
                                date_str = datetime.datetime.strftime(date,'%Y-%m-%d')

        r = 3
        #存放假期的list
        holiday_list = []
        for item in self.env['iac.tdelivery.holiday'].sudo().search([('plant','=',plant_code)]):
            holiday_list.append(item.holiday)
        # print holiday_list
        for tconfirm_line in tconfirm_export:
            #先将r行所有周末的列给上背景色
            for item in pattern_color:
                sheet1.write(r, item, '', style3)
            control_table_obj = self.env['iac.control.table.real'].sudo().search(
                [('vendor', '=', tconfirm_line.vendor_id.vendor_code),
                 ('buyer_id', '=', tconfirm_line.buyer_id.id), ('plant_id', '=', tconfirm_line.plant_id.id)])

            #200613 ning 调整 Jocelyn提出新逻辑
            #如果 X1>0，ETD 需要加上 X4
            #如果X1=0，ETD需要加上ETA_Trans
            if control_table_obj.x1>0:
                eta_trans = control_table_obj.x4
            else:
                eta_trans = control_table_obj.eta_trans

            #抓出所有行合并字段
            for item in self.env['iac.buyer.fcst.setting'].search([('merged', '=', 'X')]):
                #key part的值固定是Y，单独写
                if item.title == 'Key Part':
                    sheet1.write(r, item.column_begin, 'Y')
                #remark，最后上传时间，上传帐号需要根据不同的表抓值，先跳过，会在write all qty方法中赋值
                elif item.title == 'Remark' or item.title == '最后上传时间' or item.title == '上傳帳號':
                    continue
                else:
                    # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                    self.write_confirm_data(item,tconfirm_line,sheet1,r,for_body1)
            self.write_all_qty(tconfirm_line,eta_trans,holiday_list,sheet1,r,style3)
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