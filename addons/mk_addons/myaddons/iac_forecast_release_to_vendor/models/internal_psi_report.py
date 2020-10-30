# -*- coding: utf-8 -*-

from odoo import models,fields,api
from StringIO import StringIO
import xlwt
import base64
from odoo.exceptions import UserError
import time
from odoo.odoo_env import odoo_env
from datetime import datetime,timedelta

# menu name： Internal PSI Report
# description：
# author：
# create date：
# modify date：
# modify date：

class IacInternalPSISetting(models.Model):
    #报表的配置表
    _name = 'iac.internal.psi.setting'

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


class IacInternalPSIReportWizard(models.TransientModel):
    """  internal.psi.report
    """
    _name = 'iac.internal.psi.report.wizard'

    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code', index=True)
    vendor_id = fields.Many2one('iac.vendor', string='Vendor Code', index=True)  # 只能看到自己的vendor
    plant_id = fields.Many2one('pur.org.data',string='Plant',index=True)
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location',index=True)  # 181211 ning add

    # 根据plant显示location
    @api.onchange('plant_id')
    def _onchange_plant_on_storage_location(self):
        self.storage_location_id = False
        if self.plant_id:
            return {'domain': {'storage_location_id': [('plant', '=', self.plant_id.plant_code)]}}

    # 根据plant显示vendor
    @api.onchange('plant_id')
    def _onchange_plant_on_vendor(self):
        self.vendor_id = False
        if self.plant_id:
            return {'domain': {'vendor_id': [('plant', '=', self.plant_id.id)]}}

    # 写入所有的delta qty
    # 传参分别为excel页签，行数，demand，supply,delta对应的字典
    @api.multi
    def write_all_delta_qty(self, sheet, row, demand_dic, supply_dic, delta_dic):
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
        # 从配置表抓出日期字段中最小的列号
        self.env.cr.execute("""
                select min("column") from iac_internal_psi_setting where interval !=0""")
        min_column = self.env.cr.dictfetchone()['min']
        # 抓出所有的日期字段
        for setting in self.env['iac.internal.psi.setting'].search([('interval', '!=', 0)],
                                                                 order='column'):
            # 如果是第一列，则delta qty的计算公式为当前列的supply-当前列的demand
            if min_column == setting.column:
                delta_dic[setting.column] = supply_dic[setting.column] - demand_dic[setting.column]
                if delta_dic[setting.column]>=0:
                    sheet.write(row, setting.column, xlwt.Formula(self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(row) + '-' +
                                                              self.env[
                                                                  'iac.vendor.forecast.delivery.report'].get_eng_by_column(
                                                                  setting.column) + str(row - 1)),
                                                                    for_header5)
                else:
                    sheet.write(row, setting.column, xlwt.Formula(
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(
                            row) + '-' +
                        self.env[
                            'iac.vendor.forecast.delivery.report'].get_eng_by_column(
                            setting.column) + str(row - 1)),
                                for_header4)
            # 如果不是第一列，则delta qty的计算公式为前一列的delta+当前列的supply-当前列的demand
            else:
                delta_dic[setting.column] = delta_dic[setting.column - 1] + supply_dic[setting.column] - \
                                            demand_dic[setting.column]
                if delta_dic[setting.column]>=0:
                    sheet.write(row, setting.column, xlwt.Formula(
                    self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column-1) + str(row + 1) + '+' +
                    self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(row) + '-' + self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(row - 1)),
                           for_header5)
                else:
                    sheet.write(row, setting.column, xlwt.Formula(
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column - 1) + str(
                            row + 1) + '+' +
                        self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(setting.column) + str(
                            row) + '-' + self.env['iac.vendor.forecast.delivery.report'].get_eng_by_column(
                            setting.column) + str(row - 1)),
                                for_header4)

    # 获取po cancel的数据
    @api.multi
    def get_po_cancel(self,tconfirm_line):
        po_cancel_all = self.env['iac.purchase.order.unconfirm.summary'].search(
            [('buyer_erp_id', '=', self.buyer_id.buyer_erp_id), ('data_type', '=', 'current')])

        po_cancel = []
        for po_cancel_list in po_cancel_all:
            if int(po_cancel_list.part_id) == tconfirm_line.material_id.id and po_cancel_list.buyer_erp_id == tconfirm_line.buyer_id.buyer_erp_id:
                po_cancel.append(po_cancel_list)

        po_cancel_result = 0
        if po_cancel:
            for item in po_cancel:
                # print str(item.current_qty).split('.')[0]
                po_cancel_result += abs(item.unconqtyd + item.unconqtyr)
        return po_cancel_result

    @api.multi
    def action_confirm_internal_psi_report(self):
        """
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)

        # red_color_font = 'FF0000'
        # styles = xlwt.XFStyle()
        # red_font = styles.Font(size=14, bold=True, color=red_color_font)
        # sheet1.conditional_formatting()
        # sheet1.conditional_formatting.add('A9:K9',formatting.rule.CellIsRule(operator='lessThan', formula=['0'], font=red_font))

        # 每个字段的宽度是3500
        for i in range(len(self.env['iac.internal.psi.setting'].search([]))):
            sheet1.col(i).width = 3500
        # 背景色蓝色，字体居中格式
        for_header1 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        # 背景色蓝色，字体居中，底线加粗格式
        for_header1_bottom = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        # 字体居中，背景色橘黄色
        for_header2 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour light_orange')
        # 背景色黄色，底线加粗格式
        for_header3 = xlwt.easyxf(
            'border:bottom THICK;'
            'pattern: pattern solid, pattern_fore_colour yellow')

        # 千分位格式
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        # 底线加粗，千分位格式
        for_body1_bottom = xlwt.easyxf('border:bottom THICK;')
        for_body1_bottom.num_format_str = '#,##0'
        for wizard in self:
            domain = []
            # print wizard
            # user input的查詢條件 ____________s
            domain += [('status', '=', 'T')]  # 只顯示  status = T: true有效
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
                # print wizard.buyer_id
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.storage_location_id:
                domain += [('storage_location_id', '=', wizard.storage_location_id.id)]

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
                    [('fpversion', '>=', fpversion)],order='fpversion desc', limit=1) # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add

                if not tcolumn_title:
                    raise UserError('title資料未導入!')
                else:
                    # 将所有的title写入excel
                    for item in self.env['iac.internal.psi.setting'].search([]):
                        if item.merged == 'X':
                            sheet1.write_merge(0, 2, item.column, item.column, item.title,
                                               for_header1_bottom)

                        else:
                            if item.interval == 28:
                                sheet1.write(0, item.column, item.title, for_header2)
                            else:
                                sheet1.write(0, item.column, item.title, for_header1)
                            sheet1.write(1, item.column, item.begin_date.replace('-', '/'), for_header1)
                            sheet1.write(2, item.column, item.end_date.replace('-', '/'), for_header1_bottom)
        r = 3
        for tconfirm_line in tconfirm_export:
            demand_dic = {}
            supply_dic = {}
            delta_dic = {}
            for setting in self.env['iac.internal.psi.setting'].search([('interval', '!=', 0)],
                                                                     order='column'):
                demand_dic[setting.column] = tconfirm_line[setting.source_field_name]
            for num in range(3):
                # print num
                if num == 0:
                    for item in self.env['iac.internal.psi.setting'].search([]):
                        #因为psi对应的3个固定值，po cancel不是抓取表中字段的值，所以单独写，后面不再赘述
                        if item.title == 'PSI':
                            sheet1.write(r, item.column, 'Demand')
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r, item.column, 'Demand',style)
                            # else:
                            #     sheet1.write(r,item.column,'Demand')

                        elif item.title == 'PO_Cancel':
                            sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line), for_body1)
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),style)
                            # else:
                            #     sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line))

                        else:
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            self.env['iac.vendor.psi.report.wizard'].write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1)


                if num == 1:
                    for item in self.env['iac.internal.psi.setting'].search([('merged','=','X')]):
                        if item.title == 'PSI':
                            sheet1.write(r, item.column, 'Supply')
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r, item.column, 'Supply',style)
                            # else:
                            #     sheet1.write(r,item.column,'Supply')

                        elif item.title == 'PO_Cancel':
                            sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line), for_body1)
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            # if style:
                            #     sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),style)
                            # else:
                            #     sheet1.write(r, item.column, self.get_po_cancel(tconfirm_line))

                        else:
                            # style = self.env['iac.vendor.psi.report.wizard'].get_first_two_line_stype_by_num_format_flag(item.num_format_flag)
                            self.env['iac.vendor.psi.report.wizard'].write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1)
                    self.env['iac.vendor.psi.report.wizard'].write_all_supply_qty(tconfirm_line,sheet1,r,supply_dic,'iac.internal.psi.setting',for_body1)

                if num == 2:
                    for item in self.env['iac.internal.psi.setting'].search([('merged','=','X')]):
                        if item.title == 'PSI':
                            sheet1.write(r,item.column,'Delta',for_header3)
                        elif item.title == 'PO_Cancel':
                            # style = self.env['iac.vendor.psi.report.wizard'].get_last_line_stype_by_num_format_flag(item.num_format_flag)
                            sheet1.write(r,item.column,self.get_po_cancel(tconfirm_line),for_body1_bottom)
                        else:
                            # style = self.env['iac.vendor.psi.report.wizard'].get_last_line_stype_by_num_format_flag(item.num_format_flag)
                            self.env['iac.vendor.psi.report.wizard'].write_confirm_data_and_demand_qty(item,tconfirm_line,sheet1,r,for_body1_bottom)
                    self.write_all_delta_qty(sheet1,r,demand_dic,supply_dic,delta_dic)

                r += 1
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

