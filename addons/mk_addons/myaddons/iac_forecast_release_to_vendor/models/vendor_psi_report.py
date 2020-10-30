# -*- coding: utf-8 -*-

from odoo import models,fields,api
from StringIO import StringIO
import xlwt
import base64
from odoo.exceptions import UserError
import time
from odoo.odoo_env import odoo_env
from datetime import datetime,timedelta


class JobInsertDateIntoSetting(models.Model):
    _name = 'job.insert.into.setting'
    _auto = False

    #根据begin date和间隔天数获取end date
    @api.multi
    def get_end_date_by_begin_date(self,begin_date,interval):
        return begin_date+timedelta(days=interval-1)


    #导入配置表的job，每周导入一次
    @odoo_env
    @api.multi
    def job_insert_date_into_setting(self):
        #配置表日期字段导入的日期
        setting_date_str = (self.env['iac.vendor.psi.setting'].search([('interval','!=',0)],order='column',limit=1).write_date).split(' ')[0]
        #当天日期
        now_date_str = datetime.strftime(datetime.now(),'%Y-%m-%d')
        #日期相同说明今天导入过资料，方法后续不执行
        if setting_date_str == now_date_str:
            return
        else:
            self.env.cr.execute("""
                    SELECT * FROM "ep_temp_master"."extractlog" where extractname in (
                        SELECT extractname FROM "ep_temp_master"."extractgroup" where extractgroup='FORECAST'
                            ) and extractdate>=%s and extractstatus='STEP2DONE'
                    """,(now_date_str,))
            result = self.env.cr.dictfetchone()
            if result:
                #当前的年月日
                real_year = str(time.localtime(time.time()).tm_year)
                real_month = str(time.localtime(time.time()).tm_mon)
                real_day = str(time.localtime(time.time()).tm_mday)

                if len(real_month) == 1:
                    real_month = '0' + real_month
                if len(real_day) == 1:
                    real_day = '0' + real_day
                # print real_year,real_month,real_day
                fpversion = real_year + real_month + real_day
                #只抓当天最新的一笔title资料
                tcolumn_title = self.env['iac.tcolumn.title'].sudo().search(
                    [('fpversion', '>=', fpversion)], order='fpversion desc',
                    limit=1)  # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add

                if not tcolumn_title:
                    raise UserError('title資料未導入!')
                else:
                    qty_w1_r = tcolumn_title.qty_w1_r
                    #根据qty_w1_r字段拆分出起始的日期
                    year = int(real_year)
                    month = int(qty_w1_r[5:7])
                    day = int(qty_w1_r[7:9])
                    #如果拆分出来的月份大于当前实际月份，说明跨年，excel里的起始年应该是当前年份-1
                    if month > int(real_month):
                        year = year - 1
                    begin_date_str = str(year)+'-'+str(month)+'-'+str(day)
                    #将字符串转成日期类型
                    begin_date = datetime.strptime(begin_date_str, '%Y-%m-%d')
                    vendor_begin_date = begin_date
                    internal_begin_date = begin_date
                    buyer_fcst_begin_date = begin_date
                    vendor_fcst_begin_date = begin_date
                    #两周前的日期
                    vendor_fcst_two_weeks_ago = begin_date-timedelta(days=14)
                    #抓出配置表中所有日期相关的字段，根据列号升序排列
                    for vendor_psi in self.env['iac.vendor.psi.setting'].search([('interval','!=',0)],order='column'):
                        #获取对应的结束日期
                        end_date = self.get_end_date_by_begin_date(vendor_begin_date,vendor_psi.interval)
                        vendor_psi.write({'begin_date':vendor_begin_date,'end_date':end_date})
                        #下一次的开始日期等于上一次的结束日期+1
                        vendor_begin_date = end_date+timedelta(days=1)
                    # 抓出配置表中所有日期相关的字段，根据列号升序排列
                    for internal_psi in self.env['iac.internal.psi.setting'].search([('interval', '!=', 0)], order='column'):
                        # 获取对应的结束日期
                        end_date = self.get_end_date_by_begin_date(internal_begin_date, internal_psi.interval)
                        internal_psi.write({'begin_date': internal_begin_date, 'end_date': end_date})
                        # 下一次的开始日期等于上一次的结束日期+1
                        internal_begin_date = end_date + timedelta(days=1)
                    # 抓出配置表中所有日期相关的字段，根据列号升序排列
                    for buyer_fcst in self.env['iac.buyer.fcst.setting'].search([('interval', '!=', 0)],
                                                                                    order='column_begin'):
                        # 获取对应的结束日期
                        end_date = self.get_end_date_by_begin_date(buyer_fcst_begin_date, buyer_fcst.interval)
                        buyer_fcst.write({'begin_date': buyer_fcst_begin_date, 'end_date': end_date})
                        # 下一次的开始日期等于上一次的结束日期+1
                        buyer_fcst_begin_date = end_date + timedelta(days=1)
                    # 抓出配置表中所有日期相关的字段，根据列号升序排列
                    for vendor_fcst in self.env['iac.vendor.fcst.setting'].search([('interval', '!=', 0)],
                                                                                order='column_begin'):
                        #先判断该日期字段是不是从2周前开始计算
                        if vendor_fcst.restart_flag == True:
                            #判断该日期字段是不是第三行固定为delta，如果是则写入上一次的日期
                            if vendor_fcst.delta_flag == True:
                                vendor_fcst.write({'begin_date':vendor_fcst_two_weeks_ago-timedelta(days=vendor_fcst.interval),'end_date':vendor_fcst_two_weeks_ago-timedelta(days=1)})
                            else:
                                # 获取对应的结束日期
                                end_date = self.get_end_date_by_begin_date(vendor_fcst_two_weeks_ago, vendor_fcst.interval)
                                vendor_fcst.write({'begin_date': vendor_fcst_two_weeks_ago, 'end_date': end_date})
                                # 下一次的开始日期等于上一次的结束日期+1
                                vendor_fcst_two_weeks_ago = end_date + timedelta(days=1)
                        else:
                            # 获取对应的结束日期
                            end_date = self.get_end_date_by_begin_date(vendor_fcst_begin_date, vendor_fcst.interval)
                            vendor_fcst.write({'begin_date': vendor_fcst_begin_date, 'end_date': end_date})
                            # 下一次的开始日期等于上一次的结束日期+1
                            vendor_fcst_begin_date = end_date + timedelta(days=1)

class IacVendorPSISetting(models.Model):
    #报表的配置表
    _name = 'iac.vendor.psi.setting'

    title = fields.Char()  #excel上的字段名
    merged = fields.Char()  #判断是否为合并字段，如果是初始化为X
    column = fields.Integer() #当前的列号
    interval = fields.Integer() #时间间隔，如果是日期字段则必填
    begin_date = fields.Date()  #开始日期
    end_date = fields.Date()    #结束日期
    pattern_color = fields.Char()       #背景色 如果是日期字段，该颜色只维护excel第一行的颜色
    num_format_flag = fields.Boolean()  #判断该字段的值是否需要千分位
    source_field_name = fields.Char()   #对应iac_tconfirm_data表里具体的字段名，如果需要表中取值必填
    source_field_type = fields.Char()   #如果是many2one字段必填
    # column_eng = fields.Char()  #英文排序

class IacVendorPSIReportWizard(models.TransientModel):
    """mm下载rfq,选择查询条件进行下载：
    """
    _name = 'iac.vendor.psi.report.wizard'

    plant_id = fields.Many2one('pur.org.data',string='Plant',index=True)
    buyer_id = fields.Many2one('buyer.code',string='Buyer Code',index=True)
    vendor_id = fields.Many2one('iac.vendor',string='Vendor Code',index=True)
    storage_location_id = fields.Many2one('iac.storage.location.address',string='Storage Location',index=True)

    #根据plant显示location
    @api.onchange('plant_id')
    def _onchange_plant_on_storage_location(self):
        self.storage_location_id = False
        if self.plant_id:
            return {'domain':{'storage_location_id':[('plant','=',self.plant_id.plant_code)]}}

    #根据plant显示vendor
    @api.onchange('plant_id')
    def _onchange_plant_on_vendor(self):
        self.vendor_id = False
        if self.plant_id:
            return {'domain': {'vendor_id': [('plant', '=', self.plant_id.id)]}}

    #根据颜色获取合并字段的背景色以及底线加粗格式
    @api.multi
    def get_merged_type_by_pattern_color(self,pattern_color):
        if pattern_color:
            return xlwt.easyxf('align: horiz center,vertical center;'
                                'border:bottom THICK;'
                               'pattern: pattern solid, pattern_fore_colour %s' % pattern_color)
        else:
            return xlwt.easyxf('align: horiz center,vertical center;'
                               'border:bottom THICK;')

    # 根据颜色获取日期字段的背景色（只包括excel第一行）
    @api.multi
    def get_date_stype_by_pattern_color(self,pattern_color):
        if pattern_color:
            return xlwt.easyxf('align: horiz center,vertical center;'
                'pattern: pattern solid, pattern_fore_colour %s'  %pattern_color)
        else:
            return xlwt.easyxf('align: horiz center,vertical center;')

    #数据前两行是否需要千分位格式（同一个厂商+料号会有三行资料）
    @api.multi
    def get_first_two_line_stype_by_num_format_flag(self,num_format_flag):
        if num_format_flag == True:
            return xlwt.easyxf(num_format_str='#,##0')
        else:
            return ''

    # 数据第三行是否需要千分位格式（同一个厂商+料号会有三行资料）
    #每一个厂商+料号第三行资料会有底线加粗格式，所以方法分开写
    @api.multi
    def get_last_line_stype_by_num_format_flag(self, num_format_flag):
        if num_format_flag == True:
            style = xlwt.easyxf('border:bottom THICK;')
            style.num_format_str = '#,##0'
            return style
        else:
            return xlwt.easyxf('border:bottom THICK;')

    #根据传入值的正负获取格式，负数字体要变成红色
    @api.multi
    def get_delta_style_by_number(self,number):
        if number>=0:
            style = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz left;'
            'pattern: pattern solid, pattern_fore_colour yellow')
            style.num_format_str = '#,##0'
            return style
        else:
            style = xlwt.easyxf(
                'border:bottom THICK;'
                'font: colour_index red;'
                'align: horiz left;'
                'pattern: pattern solid, pattern_fore_colour yellow')
            style.num_format_str = '#,##0'
            return style

    # #根据传入字段名获取列号
    # @api.multi
    # def get_column_by_name(self,name):
    #     return self.env['iac.vendor.psi.setting'].search([('title','=',name)]).column

    #根据数字列号以及配置表的模型名获取英文列号
    # @api.multi
    # def get_column_eng_by_column(self,column,model_str):
    #     return self.env[model_str].search([('column', '=', column)]).column_eng

    #根据传入字段名和配置表的模型名获取开始和结束日期
    @api.multi
    def get_date_by_name(self,name,model_str):
        setting_obj = self.env[model_str].search([('title', '=', name)])
        begin_date = datetime.strptime(setting_obj.begin_date,'%Y-%m-%d')
        end_date = datetime.strptime(setting_obj.end_date,'%Y-%m-%d')
        return begin_date,end_date

    #获取po cancel的数据
    @api.multi
    def get_po_cancel(self,tconfirm_line):
        po_cancel_all = self.env['iac.purchase.order.unconfirm.summary'].search(
            [('vendor_erp_id', '=', tconfirm_line.vendor_id.vendor_code), ('data_type', '=', 'current')])
        po_cancel = []
        for po_cancel_list in po_cancel_all:
            if int(po_cancel_list.part_id) == tconfirm_line.material_id.id and po_cancel_list.buyer_erp_id == tconfirm_line.buyer_id.buyer_erp_id:
                po_cancel.append(po_cancel_list)

        po_cancel_result = 0
        if po_cancel:
            for item in po_cancel:
                po_cancel_result += abs(item.unconqtyd + item.unconqtyr)
        return po_cancel_result

    #将每个厂商+料号对应的第一行资料全部写入(包括demand qty)
    #传参为配置表对象，confirm data对象，excel页签，行数,显示的格式
    @api.multi
    def write_confirm_data_and_demand_qty(self,item,tconfirm_line,sheet,row,style):
        #先判断该字段是否需要从confirm data表中抓值
        if item.source_field_name:
            if item.source_field_type == 'many2one':
                tconfirm_obj = tconfirm_line
                #如果是many2one字段，则根据.来拆分字段
                field_list = item.source_field_name.split('.')
                for field in field_list:
                    tconfirm_obj = tconfirm_obj[field]
            else:
                tconfirm_obj = tconfirm_line[item.source_field_name]
        else:
            return

        sheet.write(row, item.column, tconfirm_obj,style)



    #写入supply的值
    #传参为confirm data对象，excel的sheet页签，行数,supply_dic(用来存supply值的字典),需要抓的配置表的模型名,格式
    @api.multi
    def write_all_supply_qty(self,tconfirm_line,sheet,row,supply_dic,model_str,style):
        shipping_date_list = []
        qty_list = []
        #抓创建日期最大的表名，用来确定从那张表读取资料
        self._cr.execute(
            " select  type,cdt  from (SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,storage_location_id,status  " \
            "from iac_tdelivery_edi EDI  where EDI.material_id = %s and EDI.plant_id = %s and EDI.vendor_id = %s and EDI.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
            " SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
            " from iac_tvendor_upload Vendor where Vendor.material_id = %s and Vendor.plant_id = %s and Vendor.vendor_id = %s and Vendor.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status) a " \
            " where   status='T' order by Cdt desc LIMIT 1"
            , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
               tconfirm_line.storage_location_id.id,
               tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
               tconfirm_line.storage_location_id.id))

        item = self.env.cr.dictfetchone()
        if item:
            if item['type'] == 'iac_tvendor_upload':
                #抓出所有的交期
                self._cr.execute(
                    " select  shipping_date,qty from " + item[
                        'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))

                # print dic
                for dic in self.env.cr.dictfetchall():
                    shipping_date_list.append(dic['shipping_date'])
                    qty_list.append(dic['qty'])
                #抓出所有的日期字段
                for setting in self.env[model_str].search([('interval', '!=', 0)],
                                                                         order='column'):
                    qty = 0
                    for date_str in shipping_date_list:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        begin_date, end_date = self.get_date_by_name(setting.title,model_str)
                        #如果有多个交期在某个日期字段对应的日期范围内，则数量累加
                        if date >= begin_date and date <= end_date:
                            index = shipping_date_list.index(date_str)
                            qty += qty_list[index]
                    sheet.write(row, setting.column, qty,style)
                    # style = self.get_first_two_line_stype_by_num_format_flag(setting.num_format_flag)
                    # if style:
                    #     sheet.write(row, setting.column, qty, style)
                    # else:
                    #     sheet.write(row, setting.column, qty)
                    supply_dic[setting.column] = qty
            if item['type'] == 'iac_tdelivery_edi':
                #抓出所有的交期
                self._cr.execute(
                    "SELECT DISTINCT shipping_date, qty FROM " + item[
                        'type'] + " A WHERE 1 = 1 AND VALID = 1 AND fcst_version = ( SELECT fcst_version FROM iac_tdelivery_edi C WHERE C.ID = ( SELECT MAX (ID) FROM iac_tdelivery_edi b WHERE 1 = 1 AND A.plant_id = b.plant_id AND A.material_id = b.material_id AND A.vendor_id = b.vendor_id AND A.storage_location_id = b.storage_location_id)) AND A.material_id = %s AND A.plant_id = %s AND A.vendor_id = %s AND A.storage_location_id = %s AND A.status = 'T'" \
                    , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                       tconfirm_line.storage_location_id.id))

                for dic2 in self.env.cr.dictfetchall():
                    # print dic2
                    shipping_date_list.append(dic2['shipping_date'])
                    qty_list.append(dic2['qty'])
                # 抓出所有的日期字段
                for setting in self.env[model_str].search([('interval', '!=', 0)],
                                                                         order='column'):
                    qty = 0
                    for date_str in shipping_date_list:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        begin_date, end_date = self.get_date_by_name(setting.title,model_str)
                        # 如果有多个交期在某个日期字段对应的日期范围内，则数量累加
                        if date >= begin_date and date <= end_date:
                            index = shipping_date_list.index(date_str)
                            qty += qty_list[index]
                    sheet.write(row, setting.column, qty,style)
                    # style = self.get_first_two_line_stype_by_num_format_flag(setting.num_format_flag)
                    # if style:
                    #     sheet.write(row, setting.column, qty, style)
                    # else:
                    #     sheet.write(row, setting.column, qty)
                    supply_dic[setting.column] = qty
        else:
            #如果两张表都没有交期，supply全部为0
            for setting in self.env[model_str].search([('interval', '!=', 0)],
                                                                     order='column'):
                sheet.write(row, setting.column, 0,style)
                # style = self.get_first_two_line_stype_by_num_format_flag(setting.num_format_flag)
                # if style:
                #     sheet.write(row, setting.column, 0, style)
                # else:
                #     sheet.write(row, setting.column, 0)
                supply_dic[setting.column] = 0
    #写入所有的delta qty
    #传参分别为excel页签，行数，demand，supply,delta对应的字典
    @api.multi
    def write_all_delta_qty(self,sheet,row,demand_dic,supply_dic,delta_dic):
        # 底线加粗，字体红色，居左对齐，背景色黄色，千分位
        for_header4 = xlwt.easyxf(
            'border:bottom THICK;'
            'font: colour_index red;'
            'align: horiz left;'
            'pattern: pattern solid, pattern_fore_colour yellow')
        for_header4.num_format_str = '#,##0'
        # 底线加粗，居左对齐，背景色黄色，千分位
        for_header5 = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz left;'
            'pattern: pattern solid, pattern_fore_colour yellow')
        for_header5.num_format_str = '#,##0'
        #从配置表抓出日期字段中最小的列号
        self.env.cr.execute("""
                select min("column") from iac_vendor_psi_setting where interval !=0""")
        min_column = self.env.cr.dictfetchone()['min']
        # 抓出所有的日期字段
        for setting in self.env['iac.vendor.psi.setting'].search([('interval', '!=', 0)],
                                                                 order='column'):
            #如果是第一列，则delta qty的计算公式为当前列的supply-当前列的demand
            if min_column == setting.column:
                delta_dic[setting.column] = supply_dic[setting.column] - demand_dic[setting.column]
                if delta_dic[setting.column]>=0:
                    sheet.write(row,setting.column,xlwt.Formula(self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column)+str(row)+'-'+
                                                            self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column)+str(row-1)),
                                                                for_header5)
                else:
                    sheet.write(row, setting.column, xlwt.Formula(
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(
                            row) + '-' +
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(
                            row - 1)),
                                for_header4)
            #如果不是第一列，则delta qty的计算公式为前一列的delta+当前列的supply-当前列的demand
            else:
                delta_dic[setting.column] = delta_dic[setting.column-1] + supply_dic[setting.column] - demand_dic[setting.column]
                if delta_dic[setting.column]>=0:
                    sheet.write(row, setting.column, xlwt.Formula(self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column-1)+str(row+1)+'+'+
                                                              self.env[
                                                                  'iac.vendor.forecast.delivery.report'].get_eng_by_column(
                                                                  setting.column)+str(row)+'-'+self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column)+str(row-1)),
                                                                        for_header5)
                else:
                    sheet.write(row, setting.column, xlwt.Formula(
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column - 1) + str(
                            row + 1) + '+' +
                        self.env[
                            'iac.vendor.forecast.delivery.report'].get_eng_by_column(
                            setting.column) + str(row) + '-' + self.env[
                            'iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(row - 1)),
                                for_header4)

    @api.multi
    def action_confirm(self):
        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)
        #背景色蓝色，字体居中格式
        for_header1 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        #背景色蓝色，字体居中，底线加粗格式
        for_header1_bottom = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        #字体居中，背景色橘黄色
        for_header2 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour light_orange')
        #背景色黄色，底线加粗格式
        for_header3 = xlwt.easyxf(
            'border:bottom THICK;'
            'pattern: pattern solid, pattern_fore_colour yellow')

        #千分位格式
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        #底线加粗，千分位格式
        for_body1_bottom = xlwt.easyxf('border:bottom THICK;')
        for_body1_bottom.num_format_str = '#,##0'
        #每个字段的宽度是3500
        for i in range(len(self.env['iac.vendor.psi.setting'].search([]))):
            sheet1.col(i).width = 3500
        for wizard in self:
            domain = []
            #print wizard
            # user input的查詢條件 ____________s
            domain += [('status', '=', 'T')]  # 只顯示  status = T: true有效
            if wizard.plant_id:
                domain += [('plant_id','=',wizard.plant_id.id)]
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
                # print wizard.buyer_id
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.storage_location_id:
                domain += [('storage_location_id','=',wizard.storage_location_id.id)]

            tconfirm_export = self.env['iac.tconfirm.data'].sudo().search(domain)
            if not tconfirm_export:
                raise UserError('查無資料! ')
            else:
                real_year = str(time.localtime(time.time()).tm_year)
                real_month = str(time.localtime(time.time()).tm_mon)
                real_day = str(time.localtime(time.time()).tm_mday)

                if len(real_month) == 1:
                    real_month = '0' + real_month
                if len(real_day) == 1:
                    real_day = '0' + real_day
                # print real_year,real_month,real_day
                fpversion = real_year + real_month + real_day
                tcolumn_title = self.env['iac.tcolumn.title'].sudo().search(
                    [('fpversion', '>=', fpversion)], order='fpversion desc',
                    limit=1)  # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add

                if not tcolumn_title:
                    raise UserError('title資料未導入!')
                else:
                    #将所有的title写入excel
                    for item in self.env['iac.vendor.psi.setting'].search([]):
                        if item.merged == 'X':
                            sheet1.write_merge(0,2,item.column,item.column,item.title,for_header1_bottom)
                        else:
                            if item.interval == 28:
                                sheet1.write(0,item.column,item.title,for_header2)
                            else:
                                sheet1.write(0, item.column, item.title, for_header1)
                            sheet1.write(1,item.column,item.begin_date.replace('-','/'),for_header1)
                            sheet1.write(2, item.column,item.end_date.replace('-','/'), for_header1_bottom)
        r = 3
        for tconfirm_line in tconfirm_export:
            demand_dic = {}
            supply_dic = {}
            delta_dic = {}
            for setting in self.env['iac.vendor.psi.setting'].search([('interval', '!=', 0)],
                                                                     order='column'):
                demand_dic[setting.column] = tconfirm_line[setting.source_field_name]
            for num in range(3):
                if num == 0:
                    for item in self.env['iac.vendor.psi.setting'].search([]):
                        #因为psi对应的3个固定值，po cancel不是抓取表中字段的值，所以单独写，后面不再赘述
                        if item.title == 'PSI':
                            sheet1.write(r, item.column, 'Demand')
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r, item.column, 'Demand',style)
                            # else:
                            #     sheet1.write(r,item.column,'Demand')
                        elif item.title == 'PO_Cancel':
                            sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line), for_body1)
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),style)
                            # else:
                            #     sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line))
                        else:
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            self.write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1)
                if num == 1:
                    for item in self.env['iac.vendor.psi.setting'].search([('merged','=','X')]):
                        if item.title == 'PSI':
                            sheet1.write(r, item.column, 'Supply')
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r, item.column, 'Supply',style)
                            # else:
                            #     sheet1.write(r,item.column,'Supply')
                        elif item.title == 'PO_Cancel':
                            sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line), for_body1)
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),style)
                            # else:
                            #     sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line))
                        else:
                            # style = self.get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            self.write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1)
                    self.write_all_supply_qty(tconfirm_line,sheet1,r,supply_dic,'iac.vendor.psi.setting',for_body1)
                if num == 2:
                    for item in self.env['iac.vendor.psi.setting'].search([('merged','=','X')]):
                        if item.title == 'PSI':
                            sheet1.write(r,item.column,'Delta',for_header3)
                        elif item.title == 'PO_Cancel':
                            # style = self.get_last_line_stype_by_num_format_flag(item.num_format_flag)
                            sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),for_body1_bottom)
                        else:
                            # style = self.get_last_line_stype_by_num_format_flag(item.num_format_flag)
                            self.write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1_bottom)
                    self.write_all_delta_qty(sheet1,r,demand_dic,supply_dic,delta_dic)
                r+=1
        wb2.save(output)

        # 文件输出成功之后,跳转链接，浏览器下载文件
        vals = {
            'name': 'vendor_psi_report',
            'datas_fname': 'vendor_psi_report.xls',
            'description': 'Vendor PSI Report',
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
