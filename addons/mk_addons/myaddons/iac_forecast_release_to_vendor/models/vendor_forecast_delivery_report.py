# -*- coding: utf-8 -*-

import xlwt
import time, base64
import datetime
from odoo.exceptions import UserError
from odoo import models, fields, api
from StringIO import StringIO


class IacVendorFcstSetting(models.Model):
    #报表的配置表
    _name = 'iac.vendor.fcst.setting'

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
    restart_flag = fields.Boolean()     #判断该日期字段是否要从两周前开始计算
    delta_flag = fields.Boolean()       #判断该日期字段第三行是不是固定为delta


class VendorForecastDeliveryReport(models.Model):
    _name = "iac.vendor.forecast.delivery.report"

    buyer_id = fields.Many2one('buyer.code', string="IAC Buyer Code", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)  # 只要顯示該vendor的資料&必填

    #根据中文列号获取对应的英文列号
    @api.multi
    def get_eng_by_column(self,column):
        #列从0开始，所以小于26说明只有一位字母
        if column<26:
            column_eng = chr(ord('A')+column)
        else:
            first_eng = chr(column/26+ord('A')-1)
            second_eng = chr(column%26+ord('A'))
            column_eng = first_eng+second_eng
        return column_eng

    #字体黑色，有背景色
    # 获取日期字段第2行和第3行的格式
    @api.multi
    def get_style_except_first(self):
        return xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')

    # 字体黑色，无背景色
    # 获取日期字段第2行和第3行的格式
    @api.multi
    def get_style_except_first_no_pattern(self):
        return xlwt.easyxf('font:bold 1,color black,height 200;'
                           'align: horiz center,vertical center;')

    # 传参为配置表对象，confirm data对象，excel页签，行数，显示的格式
    @api.multi
    def write_confirm_data(self, item, tconfirm_line, sheet, row, style):
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
        if item.title == 'Vendor Code':
            sheet.write(row, item.column_begin, tconfirm_obj[4:])
        elif item.title == 'Vendor Name':
            sheet.write(row, item.column_begin, tconfirm_obj[:6])
        else:
            if style:
                sheet.write(row, item.column_begin, tconfirm_obj, style)
            else:
                sheet.write(row, item.column_begin, tconfirm_obj)

    # 写入所有的delta qty
    # 传参分别为excel页签，行数
    @api.multi
    def write_all_delta_qty(self, sheet, row):
        # 从配置表抓出delta字段中最小的列号
        self.env.cr.execute("""
                select min("column_begin") from iac_vendor_fcst_setting where delta_flag ='t' """)
        min_column = self.env.cr.dictfetchone()['min']
        # 抓出所有的delta字段
        for setting in self.env['iac.vendor.fcst.setting'].search([('delta_flag', '=', 't')],
                                                                 order='column_begin'):
            # 如果是第一列，则delta qty的计算公式为它前一个字段所有列的和减去与它起始日期相同的字段的值
            if min_column == setting.column_begin:
                #先找到delta字段对应的前一个字段
                title_obj = self.env['iac.vendor.fcst.setting'].search([('column_end','=',setting.column_begin-1)])
                column = title_obj.column_begin
                eng_str = ''
                while column <= title_obj.column_end:
                    if column == title_obj.column_begin:
                        eng_str = self.get_eng_by_column(column)+str(row+1)
                    else:
                        eng_str = eng_str+'+'+self.get_eng_by_column(column)+str(row+1)
                    column+=1
                #抓取与该delta字段起始日期相同的字段
                date_obj = self.env['iac.vendor.fcst.setting'].search([('begin_date', '=', setting.begin_date),('end_date','=',setting.end_date),('restart_flag','=',False)])
                eng_str = eng_str+'-'+self.get_eng_by_column(date_obj.column_begin)+str(row+1)
                sheet.write(row,setting.column_begin,xlwt.Formula(eng_str))
            # 如果不是第一列，则delta qty的计算公式为它前一个字段所有列的和加上前一个delta qty的值减去与它起始日期相同的字段的值
            else:
                # 先找到delta字段对应的前一个字段
                title_obj = self.env['iac.vendor.fcst.setting'].search([('column_end', '=', setting.column_begin - 1)])
                column = title_obj.column_begin
                eng_str = ''
                while column <= title_obj.column_end:
                    if column == title_obj.column_begin:
                        eng_str = self.get_eng_by_column(column) + str(row + 1)
                    else:
                        eng_str = eng_str + '+' + self.get_eng_by_column(column) + str(row + 1)
                    column += 1

                end_date = datetime.datetime.strptime(setting.begin_date,'%Y-%m-%d')-datetime.timedelta(days=1)
                # 抓取该delta字段前一个delta字段的值
                delta_obj = self.env['iac.vendor.fcst.setting'].search([('end_date', '=', end_date),('delta_flag','=','t')])
                eng_str = eng_str+'+'+self.get_eng_by_column(delta_obj.column_begin)+str(row+1)
                # 抓取与该delta字段起始日期相同的字段
                date_obj = self.env['iac.vendor.fcst.setting'].search(
                    [('begin_date', '=', setting.begin_date), ('end_date', '=', setting.end_date),
                     ('restart_flag', '=', False)])
                eng_str = eng_str + '-' + self.get_eng_by_column(date_obj.column_begin) + str(row + 1)
                sheet.write(row, setting.column_begin, xlwt.Formula(eng_str))



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

        output = StringIO()
        wb1 = xlwt.Workbook()
        sheet1 = wb1.add_sheet('sheet1', cell_overwrite_ok=True)
        #字体黑色居中，背景色灰色
        for_header1 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center,vertical center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        #字体蓝色居中
        for_header3 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  )
        #字体蓝色居中，背景色灰色
        for_header4 = xlwt.easyxf('font:bold 1,color blue,height 200;'
                                  'align: horiz center;'
                                  'pattern: pattern solid, pattern_fore_colour 22')
        #字体黑色居中
        for_header5 = xlwt.easyxf('font:bold 1,color black,height 200;'
                                  'align: horiz center;'
                                  )
        #千分位
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        # 背景色灰色
        style3 = xlwt.easyxf('pattern: pattern solid, pattern_fore_colour 22')
        # 抓取到冻结视窗字段的列号
        # column = self.env['iac.vendor.fcst.setting'].search([('frozen_flag', '=', 't')]).column_begin
        sheet1.panes_frozen = True
        sheet1.horz_split_pos = 3  # 行
        sheet1.vert_split_pos = 9  # 列
        # sheet1.vert_split_pos = column+1  # 列

        # 将所有周末的列号存入，来判断格式
        pattern_color = []
        # 每个字段的宽度是3000
        for i in range(self.env['iac.vendor.fcst.setting'].search([], order='column_end desc', limit=1).column_end+1):
            sheet1.col(i).width = 3000

        for wizard in self:
            domain = []
            # user input的查詢條件 ____________s
            domain += [('status', '=', 'T')]  # 只顯示  status = T: true有效
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            # print '*130: ', domain
            tconfirm_export = self.env['iac.tconfirm.data'].sudo().search(domain)
            # l = xrange(len(traw_export))
            # print '*133: ',  traw_export[0].fpversion
            if not tconfirm_export:
                raise UserError('查無資料! ')
            else:
                title_export = self.env['iac.tcolumn.title'].sudo().search(
                    [('fpversion', '=', tconfirm_export[0].fpversion)])
                if not title_export:
                    title_err_msg = tconfirm_export[0].fpversion, 'title資料未維護! '
                    raise UserError(title_err_msg)
                else:
                    # 将所有的title写入excel
                    for item in self.env['iac.vendor.fcst.setting'].search([]):
                        if item.merged == 'X':
                            sheet1.write_merge(0,2,item.column_begin,item.column_end,item.title,for_header1)
                        else:
                            sheet1.write_merge(0,0,item.column_begin,item.column_end,item.title,for_header4)
                            # 如果restart flag不存在，说明是前13周加9个月的日期
                            if not item.restart_flag:
                                sheet1.write(1, item.column_begin, item.begin_date.replace('-', '/'),
                                             for_header1)
                                sheet1.write(2, item.column_begin, item.end_date.replace('-', '/'),
                                             for_header1)
                            else:
                                #如果delta flag存在，则说明第二行是开始日期-结束日期，第三行固定是delta
                                if item.delta_flag == True:
                                    sheet1.write(1, item.column_begin, item.begin_date.replace('-', '/')+'-'+item.end_date.replace('-', '/'),
                                                 for_header5)
                                    sheet1.write(2, item.column_begin, 'Delta',
                                                 for_header5)
                                else:
                                    #如果开始列和结束列相同，第二行是开始日期，第三行是结束日期
                                    if item.column_begin == item.column_end:
                                        sheet1.write(1, item.column_begin, item.begin_date.replace('-', '/'),
                                                     for_header5)
                                        sheet1.write(2, item.column_begin, item.end_date.replace('-', '/'),
                                                     for_header5)
                                    else:
                                        column = item.column_begin
                                        date_str = item.begin_date
                                        while column <= item.column_end:
                                            # 如果是周末，格式带有背景色
                                            if self.env['iac.buyer.fcst.delivery.report.wizard'].get_weekday_by_date_str(date_str) == u'週六' or self.env['iac.buyer.fcst.delivery.report.wizard'].get_weekday_by_date_str(
                                                    date_str) == u'週日':
                                                # 将周末的列号存入list
                                                pattern_color.append(column)
                                                sheet1.write(2, column, self.env['iac.buyer.fcst.delivery.report.wizard'].get_weekday_by_date_str(date_str),
                                                             for_header4)
                                                sheet1.write(1, column, date_str.replace('-', '/'), for_header4)
                                            else:
                                                sheet1.write(2, column, self.env['iac.buyer.fcst.delivery.report.wizard'].get_weekday_by_date_str(date_str),
                                                             for_header5)
                                                sheet1.write(1, column, date_str.replace('-', '/'),
                                                             for_header5)
                                            column += 1
                                            date = datetime.datetime.strptime(date_str, '%Y-%m-%d') + datetime.timedelta(days=1)
                                            date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
        r = 3
        for tconfirm_line in tconfirm_export:  # for tconfirm_line in tconfirm_export:
            # 先将r行所有周末的列给上背景色
            for item in pattern_color:
                sheet1.write(r, item, '', style3)
            # 抓出所有行合并字段
            for item in self.env['iac.vendor.fcst.setting'].search([]):
                # key part的值固定是Y，单独写
                if item.title == 'Key Part':
                    sheet1.write(r, item.column_begin, 'Y')
                #remark不需要写入值
                elif item.title == 'Remark':
                    continue
                #从两周前开始计算的日期字段不从表中抓数据，直接跳过
                elif item.restart_flag == True:
                    continue
                else:
                    # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(
                    #     item.num_format_flag)
                    self.write_confirm_data(item, tconfirm_line, sheet1, r, for_body1)
            self.write_all_delta_qty(sheet1,r)
            r+=1


        wb1.save(output)
        vals = {
            'action_type': 'Vendor Fill Form',
            'vendor_id': self.vendor_id.id
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





