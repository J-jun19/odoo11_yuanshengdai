# -*- coding: utf-8 -*-

import json
import xlwt
# import xlsxwriter
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

# menu name： Internal PSI Report
# description：
# author：
# create date：
# modify date：
# modify date：

_logger = logging.getLogger(__name__)

class IacInternalPSIReportWizardBK(models.TransientModel):
    """  internal.psi.report
    """
    _name = 'iac.internal.psi.report.wizard.bk'

    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst', index=True)
    # buyer_id = fields.Many2one('buyer.code', string="Buyer Code", index=True)

    buyer_name_cn = fields.Selection(string='Buyer Name(Chinese)', selection='_selection_name_cn', index=True)
    buyer_name_en = fields.Selection(string='Buyer Name(English)', selection='_selection_buyer_name', index=True)
    department = fields.Selection(selection='_selection_department', index=True)
    vendor_id = fields.Many2one('iac.vendor', string='Vendor Code', index=True)  # 只能看到自己的vendor
    vendor_name_cn = fields.Selection(string='Vendor Name(Chinese)', selection='_selection_name', index=True)
    vendor_name_en = fields.Selection(string='Vendor Name(English)', selection='_selection_name1_en', index=True)
    plant_id = fields.Many2one('pur.org.data',string='Plant')
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add
    # buyer_id = fields.Many2one('buyer.code', string='Buyer Code',
    #                            domain=lambda self: [('id', 'in', self.env.user.buyer_id_list)], index=True)

    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):
        self.storage_location_id = False
        if self.plant_id:
            return {'domain': {'storage_location_id': [('plant', '=', self.plant_id.plant_code)]}}

    @api.model
    def _selection_buyer_name(self):
        res_iso = []
        iso_list = self.env['buyer.code'].sudo().search_read([], ['buyer_name'])
        # print iso_list
        for item in iso_list:
            # print item.key
            res_iso.append((item['buyer_name'], _(item['buyer_name'])))

        return res_iso

    @api.model
    def _selection_name_cn(self):
        res_iso1 = []
        iso_list1 = self.env['buyer.code'].sudo().search_read([], ['name_cn'])
        # print iso_list
        for item1 in iso_list1:
            # print item.key
            res_iso1.append((item1['name_cn'], _(item1['name_cn'])))

        return res_iso1

    @api.model
    def _selection_department(self):
        res_iso = []
        iso_list = self.env['buyer.code'].sudo().search_read([], ['department'])
        # print iso_list
        for item in iso_list:
            # print item.key
            res_iso.append((item['department'], _(item['department'])))

        return res_iso

    @api.model
    def _selection_name(self):
        res_iso = []
        iso_list = self.env['iac.vendor'].sudo().search_read([], ['name'])
        # print iso_list
        for item in iso_list:
            # print item.key
            res_iso.append((item['name'], _(item['name'])))

        return res_iso

    @api.model
    def _selection_name1_en(self):
        res_iso = []
        iso_list = self.env['iac.vendor.register'].sudo().search_read([], ['name1_en'])
        # print iso_list
        for item in iso_list:
            # print item.key
            # print item
            res_iso.append((item['name1_en'], _(item['name1_en'])))

        return res_iso

    @api.multi
    def action_confirm_internal_psi_report(self):
        """
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """

        # header_field_list = []
        header_field_list = ['Buyer Code','Vendor', 'Material', 'Material_description','Alternate Group', 'L/T', 'MOQ', 'PO', 'Stock','PO_Cancel',
                             'B_001','B_002','B_004','B_005','B_012','B_017B','B_902S','B_902Q','PSI',
                             'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'W11', 'W12', 'W13',
                             'WEEK40-44', 'WEEK44-48', 'WEEK48-52', 'WEEK52-56','Plant','Location','CM_VENDOR']

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)

        # red_color_font = 'FF0000'
        # styles = xlwt.XFStyle()
        # red_font = styles.Font(size=14, bold=True, color=red_color_font)
        # sheet1.conditional_formatting()
        # sheet1.conditional_formatting.add('A9:K9',formatting.rule.CellIsRule(operator='lessThan', formula=['0'], font=red_font))



        # sheet1.col(0).width = 3000
        # sheet1.col(1).width = 5000
        # sheet1.col(2).width = 5000
        # sheet1.col(6).width = 3000
        for i in range(36):
            sheet1.col(i).width = 3500
        # sheet1.col(33).width = 3000
        # sheet1.col(34).width = 3000
        # sheet1.col(35).width = 3000
        for_header1 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        for_header1_bottom = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour pale_blue')
        for_header2 = xlwt.easyxf(
            'align: horiz center,vertical center;'
            'pattern: pattern solid, pattern_fore_colour light_orange')
        for_header3 = xlwt.easyxf(
            'border:bottom THICK;'
            'pattern: pattern solid, pattern_fore_colour yellow')
        for_header4 = xlwt.easyxf(
            'border:bottom THICK;'
            'font: colour_index red;'
            'align: horiz left;'
            'pattern: pattern solid, pattern_fore_colour yellow')
        for_header5 = xlwt.easyxf(
            'border:bottom THICK;'
            'align: horiz left;'
            'pattern: pattern solid, pattern_fore_colour yellow')
        for_top = xlwt.easyxf('border:top THICK;')
        for_bottom = xlwt.easyxf('border:bottom THICK;')
        for_body1 = xlwt.easyxf(num_format_str='#,##0')
        for_body1_bottom = xlwt.easyxf('border:bottom THICK;')
        for_body1_bottom.num_format_str = '#,##0'
        for_header3.num_format_str = '#,##0'
        for_header4.num_format_str = '#,##0'
        for_header5.num_format_str = '#,##0'
        for wizard in self:
            domain = []
            # print wizard
            # user input的查詢條件 ____________s
            domain += [('status', '=', 'T')]  # 只顯示  status = T: true有效
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
                # print wizard.buyer_id
            if wizard.buyer_name_cn:
                domain += [('buyer_name_cn', '=', wizard.buyer_name_cn)]
            if wizard.buyer_name_en:
                domain += [('buyer_name_en', '=', wizard.buyer_name_en)]
            if wizard.department:
                domain += [('department', '=', wizard.department)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.vendor_name_cn:
                domain += [('vendor_name_cn', '=', wizard.vendor_name_cn)]
            if wizard.vendor_name_en:
                domain += [('vendor_name_en', '=', wizard.vendor_name_en)]
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
                print '*201:',fpversion

                tcolumn_title = self.env['iac.tcolumn.title'].sudo().search(
                    [('fpversion', '>=', fpversion)],order='fpversion desc', limit=1) # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add

                print '*206:', tcolumn_title, ',', tcolumn_title.fpversion

                if not tcolumn_title:
                    raise UserError('title資料未導入!')
                else:
                    # print tcolumn_title
                    date_list = []
                    date_list2 = []
                    date_list3 = []
                    date_list_all = [[0 for col in range(2)] for row in range(17)]
                    shipping_date_list = []
                    qty_list = []

                    qty_w1_r = tcolumn_title.qty_w1_r
                    # date_list.append(qty_w1_r)
                    qty_w2 = tcolumn_title.qty_w2
                    date_list.append(qty_w2)
                    qty_w3 = tcolumn_title.qty_w3
                    date_list.append(qty_w3)
                    qty_w4 = tcolumn_title.qty_w4
                    date_list.append(qty_w4)
                    qty_w5 = tcolumn_title.qty_w5
                    date_list.append(qty_w5)
                    qty_w6 = tcolumn_title.qty_w6
                    date_list.append(qty_w6)
                    qty_w7 = tcolumn_title.qty_w7
                    date_list.append(qty_w7)
                    qty_w8 = tcolumn_title.qty_w8
                    date_list.append(qty_w8)
                    qty_w9 = tcolumn_title.qty_w9
                    date_list.append(qty_w9)
                    qty_w10 = tcolumn_title.qty_w10
                    date_list2.append(qty_w10)
                    qty_w11 = tcolumn_title.qty_w11
                    date_list2.append(qty_w11)
                    qty_w12 = tcolumn_title.qty_w12
                    date_list2.append(qty_w12)
                    qty_w13 = tcolumn_title.qty_w13
                    date_list2.append(qty_w13)
                    qty_m1 = tcolumn_title.qty_m1
                    date_list3.append(qty_m1)
                    qty_m2 = tcolumn_title.qty_m2
                    date_list3.append(qty_m2)
                    qty_m3 = tcolumn_title.qty_m3
                    date_list3.append(qty_m3)
                    qty_m4 = tcolumn_title.qty_m4
                    date_list3.append(qty_m4)
                    # print date_list
                    month = int(qty_w1_r[5:7])
                    year = int(real_year)
                    for i in xrange(len(header_field_list)):
                        if i <= 17:
                            # print header_field_list[i]
                            sheet1.write(2, i, header_field_list[i], for_bottom)
                        if i == 18:
                            sheet1.write_merge(0, 2, i, i, header_field_list[i], for_header1_bottom)
                        if 18 < i <= 31:
                            sheet1.write(0, i, header_field_list[i], for_header1)
                            if i == 19:
                                month_1 = int(qty_w1_r[5:7])
                                month_2 = int(qty_w1_r[10:12])
                                # if month_1 > 1 and month_1 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_1 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                start_date = qty_w1_r[5:7] + '/' + qty_w1_r[7:9] + '/' + str(year)
                                date_list_all[i - 19].append(start_date)
                                # if month_2 > 1 and month_2 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_2 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                if month_2 < month_1:
                                    year += 1
                                end_date = qty_w1_r[10:12] + '/' + qty_w1_r[12:14] + '/' + str(year)
                                date_list_all[i - 19].append(end_date)
                                sheet1.write(1, i, start_date, for_header1)
                                sheet1.write(2, i, end_date, for_header1_bottom)
                                if month_2 == 12 and int(qty_w1_r[12:14]) == 31:
                                    year += 1
                            elif 19 < i <= 27:
                                # print date_list[i-9]
                                month_1 = int(date_list[i - 20][3:5])
                                month_2 = int(date_list[i - 20][8:10])
                                # if month_1 > 1 and month_1 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_1 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                start_date = date_list[i - 20][3:5] + '/' + date_list[i - 20][5:7] + '/' + str(year)
                                date_list_all[i - 19].append(start_date)
                                # if month_2 > 1 and month_2 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_2 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                if month_2 < month_1:
                                    year += 1
                                end_date = date_list[i - 20][8:10] + '/' + date_list[i - 20][10:12] + '/' + str(year)
                                date_list_all[i - 19].append(end_date)
                                sheet1.write(1, i, start_date, for_header1)
                                sheet1.write(2, i, end_date, for_header1_bottom)
                                if month_2 == 12 and int(date_list[i - 20][10:12]) == 31:
                                    year += 1
                            else:
                                month_1 = int(date_list2[i - 28][4:6])
                                month_2 = int(date_list2[i - 28][9:11])
                                # if month_1 > 1 and month_1 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_1 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                start_date = date_list2[i - 28][4:6] + '/' + date_list2[i - 28][6:8] + '/' + str(year)
                                date_list_all[i - 19].append(start_date)
                                # if month_2 > 1 and month_2 < 12:
                                #     year = int(real_year)
                                # else:
                                #     if month_2 == int(real_month):
                                #         year = int(real_year)
                                #     else:
                                #         year = int(real_year) - 1
                                if month_2 < month_1:
                                    year += 1
                                end_date = date_list2[i - 28][9:11] + '/' + date_list2[i - 28][11:13] + '/' + str(year)
                                date_list_all[i - 19].append(end_date)
                                sheet1.write(1, i, start_date, for_header1)
                                sheet1.write(2, i, end_date, for_header1_bottom)
                                if month_2 == 12 and int(date_list2[i - 28][11:13]) == 31:
                                    year += 1
                        if 31 < i <= 35:
                            sheet1.write(0, i, header_field_list[i], for_header2)
                            month_1 = int(date_list3[i - 32][3:5])
                            month_2 = int(date_list3[i - 32][8:10])
                            # if month_2<month_1:
                            #     year +=1
                            # if month_1 > 1 and month_1 < 12:
                            #     year = int(real_year)
                            # else:
                            #     if month_1 == int(real_month):
                            #         year = int(real_year)
                            #     else:
                            #         year = int(real_year) - 1
                            start_date = date_list3[i - 32][3:5] + '/' + date_list3[i - 32][5:7] + '/' + str(year)
                            date_list_all[i - 19].append(start_date)
                            # if month_2 > 1 and month_2 < 12:
                            #     year = int(real_year)
                            # else:
                            #     if month_2 == int(real_month):
                            #         year = int(real_year)
                            #     else:
                            #         year = int(real_year) - 1
                            if month_2<month_1:
                                year +=1

                            end_date = date_list3[i - 32][8:10] + '/' + date_list3[i - 32][10:12] + '/' + str(year)
                            date_list_all[i - 19].append(end_date)
                            sheet1.write(1, i, start_date, for_header1)
                            sheet1.write(2, i, end_date, for_header1_bottom)
                            if month_2 == 12 and int(date_list3[i - 32][10:12]) == 31:
                                year +=1

                        if 35 < i <= 38:
                            # print header_field_list[i]
                            sheet1.write(2, i, header_field_list[i], for_bottom)
        r = 3
        # print pattern_color
        # print len(date_list_all)
        # print date_list_all[0][2]
        # print date_list_all[0][3]
        po_cancel_all = self.env['iac.purchase.order.unconfirm.summary'].search([('buyer_erp_id','=',self.buyer_id.buyer_erp_id),('data_type','=','current')])
        for tconfirm_line in tconfirm_export:
            demand_list = [tconfirm_line.raw_id.qty_w1_r, tconfirm_line.qty_w2, tconfirm_line.qty_w3, tconfirm_line.qty_w4,
                           tconfirm_line.qty_w5
                , tconfirm_line.qty_w6, tconfirm_line.qty_w7, tconfirm_line.qty_w8, tconfirm_line.qty_w9,
                           tconfirm_line.qty_w10,
                           tconfirm_line.qty_w11, tconfirm_line.qty_w12, tconfirm_line.qty_w13, tconfirm_line.qty_m1,
                           tconfirm_line.qty_m2, tconfirm_line.qty_m3, tconfirm_line.qty_m4]
            supply_list = []
            delta_list = []
            po_cancel = []
            for po_cancel_list in po_cancel_all:
                if int(po_cancel_list.part_id) == tconfirm_line.material_id.id and po_cancel_list.buyer_erp_id == tconfirm_line.buyer_id.buyer_erp_id:
                    po_cancel.append(po_cancel_list)
            # po_cancel = self.env['v.po.cancel.history.report'].search([('vendor_id','=',tconfirm_line.vendor_id.id),(
            #     'plant_id','=',tconfirm_line.plant_id.id),('material_id','=',tconfirm_line.material_id.id),(
            #     'buyer_code','=',tconfirm_line.buyer_id.buyer_erp_id), ('storage_location_id', '=', tconfirm_line.storage_location_id.id)])


            po_cancel_result = 0
            if po_cancel:
                for item in po_cancel:
                    # print str(item.current_qty).split('.')[0]
                    po_cancel_result += abs(item.unconqtyd + item.unconqtyr)

            record_vendor_upload = 0
            record_delivery_edi = 0
            for num in range(3):
                # print num
                if num == 0:
                    sheet1.write(r, 0, tconfirm_line.buyer_id.buyer_erp_id)
                    sheet1.write(r, 1, tconfirm_line.vendor_id.vendor_code)
                    sheet1.write(r, 2, tconfirm_line.material_id.part_no)
                    sheet1.write(r, 3, tconfirm_line.description)
                    sheet1.write(r, 4, tconfirm_line.alt_grp)
                    sheet1.write(r, 5, tconfirm_line.leadtime)
                    sheet1.write(r, 6, tconfirm_line.round_value)
                    sheet1.write(r, 7, tconfirm_line.open_po, for_body1)
                    sheet1.write(r, 8, tconfirm_line.stock)
                    sheet1.write(r, 9, po_cancel_result, for_body1)
                    sheet1.write(r, 10, tconfirm_line.b001)
                    sheet1.write(r, 11, tconfirm_line.b002)
                    sheet1.write(r, 12, tconfirm_line.b004)
                    sheet1.write(r, 13, tconfirm_line.b005)
                    sheet1.write(r, 14, tconfirm_line.b012)
                    sheet1.write(r, 15, tconfirm_line.b017b)
                    sheet1.write(r, 16, tconfirm_line.b902s)
                    sheet1.write(r, 17, tconfirm_line.b902q)
                    sheet1.write(r, 18, 'Demand')
                    sheet1.write(r, 19, tconfirm_line.qty_w1_r, for_body1)
                    sheet1.write(r, 20, tconfirm_line.qty_w2, for_body1)
                    sheet1.write(r, 21, tconfirm_line.qty_w3, for_body1)
                    sheet1.write(r, 22, tconfirm_line.qty_w4, for_body1)
                    sheet1.write(r, 23, tconfirm_line.qty_w5, for_body1)
                    sheet1.write(r, 24, tconfirm_line.qty_w6, for_body1)
                    sheet1.write(r, 25, tconfirm_line.qty_w7, for_body1)
                    sheet1.write(r, 26, tconfirm_line.qty_w8, for_body1)
                    sheet1.write(r, 27, tconfirm_line.qty_w9, for_body1)
                    sheet1.write(r, 28, tconfirm_line.qty_w10, for_body1)
                    sheet1.write(r, 29, tconfirm_line.qty_w11, for_body1)
                    sheet1.write(r, 30, tconfirm_line.qty_w12, for_body1)
                    sheet1.write(r, 31, tconfirm_line.qty_w13, for_body1)
                    sheet1.write(r, 32, tconfirm_line.qty_m1, for_body1)
                    sheet1.write(r, 33, tconfirm_line.qty_m2, for_body1)
                    sheet1.write(r, 34, tconfirm_line.qty_m3, for_body1)
                    sheet1.write(r, 35, tconfirm_line.qty_m4, for_body1)
                    sheet1.write(r, 36, tconfirm_line.plant_id.plant_code)

                    # self._cr.execute(
                    #     " select  type,cdt  from (SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,storage_location_id,status  " \
                    #     "from iac_tdelivery_edi EDI  where EDI.material_id = %s and EDI.plant_id = %s and EDI.vendor_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status union " \
                    #     " SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
                    #     " from iac_tvendor_upload Vendor  where Vendor.material_id = %s and Vendor.plant_id = %s and Vendor.vendor_id = %s and Vendor.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status) a " \
                    #     " where  status='T' order by Cdt desc LIMIT 1"
                    #     , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                    #        tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,
                    #        tconfirm_line.storage_location_id.id))
                    #
                    # for item in self.env.cr.dictfetchall():
                    #     if item['type'] == 'iac_tvendor_upload':
                    #         record_vendor_upload = 1
                    #     if item['type'] == 'iac_tdelivery_edi':
                    #         record_delivery_edi = 1
                    # if record_vendor_upload == 1:
                    sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)
                    sheet1.write(r, 38, tconfirm_line.storage_location_id.CM_VENDOR)
                    # if record_delivery_edi == 1:
                    #     storage_location_id = self.env['iac.tdelivery.edi'].search(
                    #         ['&', ('material_id', '=', tconfirm_line.material_id.id),
                    #          ('plant_id', '=', tconfirm_line.plant_id.id),
                    #          ('vendor_id', '=', tconfirm_line.vendor_id.id)]).storage_location_id
                    #     if storage_location_id:
                    #         sheet1.write(r, 37, storage_location_id.storage_location)
                    #     else:
                    #         sheet1.write(r, 37, '')
                if num == 1:
                    sheet1.write(r, 0, tconfirm_line.buyer_id.buyer_erp_id)
                    sheet1.write(r, 1, tconfirm_line.vendor_id.vendor_code)
                    sheet1.write(r, 2, tconfirm_line.material_id.part_no)
                    sheet1.write(r, 3, tconfirm_line.description)
                    sheet1.write(r, 4, tconfirm_line.alt_grp)
                    sheet1.write(r, 5, tconfirm_line.leadtime)
                    sheet1.write(r, 6, tconfirm_line.round_value)
                    sheet1.write(r, 7, tconfirm_line.open_po, for_body1)
                    sheet1.write(r, 8, tconfirm_line.stock)
                    sheet1.write(r, 9, po_cancel_result, for_body1)
                    sheet1.write(r, 10, tconfirm_line.b001)
                    sheet1.write(r, 11, tconfirm_line.b002)
                    sheet1.write(r, 12, tconfirm_line.b004)
                    sheet1.write(r, 13, tconfirm_line.b005)
                    sheet1.write(r, 14, tconfirm_line.b012)
                    sheet1.write(r, 15, tconfirm_line.b017b)
                    sheet1.write(r, 16, tconfirm_line.b902s)
                    sheet1.write(r, 17, tconfirm_line.b902q)
                    sheet1.write(r, 36, tconfirm_line.plant_id.plant_code)
                    # if tconfirm_line.storage_location_id.storage_location:
                    #     sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)
                    # else:
                    #     sheet1.write(r, 37, '')
                    # if record_vendor_upload == 1:
                    sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)
                    sheet1.write(r, 38, tconfirm_line.storage_location_id.CM_VENDOR)
                    # if record_delivery_edi == 1:
                    #     if storage_location_id:
                    #         sheet1.write(r, 37, storage_location_id.storage_location)
                    #     else:
                    #         sheet1.write(r, 37, '')
                    sheet1.write(r, 18, 'Supply')
                    self._cr.execute(
                        " select  type,cdt  from (SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,storage_location_id,status  " \
                        "from iac_tdelivery_edi EDI  where EDI.material_id = %s and EDI.plant_id = %s and EDI.vendor_id = %s and EDI.storage_location_id = %s group by material_id,plant_id,vendor_id,storage_location_id,status union " \
                        " SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,storage_location_id,status " \
                        " from iac_tvendor_upload Vendor  where Vendor.material_id = %s and Vendor.plant_id = %s and Vendor.vendor_id = %s and Vendor.storage_location_id = %s  group by material_id,plant_id,vendor_id,storage_location_id,status) a " \
                        " where  status='T' order by Cdt desc LIMIT 1"
                        , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id,tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))
                    # self.env.cr.commit()
                    # print self.env.cr.dictfetchall()
                    for item in self.env.cr.dictfetchall():
                        if item['type'] == 'iac_tvendor_upload':
                            self._cr.execute(
                                " select  shipping_date,qty from " + item[
                                    'type'] + " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T'" \
                                , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id,tconfirm_line.storage_location_id.id))

                            # print dic
                            for dic in self.env.cr.dictfetchall():
                                # print dic['shipping_date']
                                # print dic['qty']
                                shipping_date_list.append(dic['shipping_date'])
                                qty_list.append(dic['qty'])
                            # print shipping_date_list,qty_list
                            for i in range(17):
                                qty = 0
                                record = 0
                                start_date1 = datetime.datetime(int(date_list_all[i][2][6:10]),
                                                                int(date_list_all[i][2][0:2]),
                                                                int(date_list_all[i][2][3:5]))
                                end_date1 = datetime.datetime(int(date_list_all[i][3][6:10]), int(date_list_all[i][3][0:2]),
                                                              int(date_list_all[i][3][3:5]))
                                for item1 in shipping_date_list:
                                    # print item
                                    # record = 0
                                    shipping_date = datetime.datetime(int(item1[0:4]), int(item1[5:7]), int(item1[8:10]))
                                    if shipping_date >= start_date1 and shipping_date <= end_date1:
                                        # print shipping_date
                                        # print qty_list[record]
                                        qty += qty_list[record]
                                    record += 1
                                sheet1.write(r, i + 19, qty, for_body1)
                                supply_list.append(qty)
                            # sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)

                        if item['type'] == 'iac_tdelivery_edi':
                            self._cr.execute(
                                "SELECT DISTINCT shipping_date, qty FROM " + item[
                                    'type'] + " A WHERE 1 = 1 AND VALID = 1 AND fcst_version = ( SELECT fcst_version FROM iac_tdelivery_edi C WHERE C.ID = ( SELECT MAX (ID) FROM iac_tdelivery_edi b WHERE 1 = 1 AND A.plant_id = b.plant_id AND A.material_id = b.material_id AND A.vendor_id = b.vendor_id AND A.storage_location_id = b.storage_location_id)) AND A.material_id = %s AND A.plant_id = %s AND A.vendor_id = %s and A.storage_location_id = %s AND A.status = 'T'" \
                                , (tconfirm_line.material_id.id, tconfirm_line.plant_id.id, tconfirm_line.vendor_id.id, tconfirm_line.storage_location_id.id))
                            for dic2 in self.env.cr.dictfetchall():
                                # print dic['shipping_date']
                                # print dic['qty']
                                shipping_date_list.append(dic2['shipping_date'])
                                qty_list.append(dic2['qty'])

                            for i in range(17):
                                qty = 0
                                record = 0
                                start_date1 = datetime.datetime(int(date_list_all[i][2][6:10]),
                                                                int(date_list_all[i][2][0:2]),
                                                                int(date_list_all[i][2][3:5]))
                                end_date1 = datetime.datetime(int(date_list_all[i][3][6:10]), int(date_list_all[i][3][0:2]),
                                                              int(date_list_all[i][3][3:5]))
                                for item2 in shipping_date_list:
                                    # print item
                                    # record = 0
                                    shipping_date = datetime.datetime(int(item2[0:4]), int(item2[5:7]), int(item2[8:10]))
                                    if shipping_date >= start_date1 and shipping_date <= end_date1:
                                        # print shipping_date
                                        # print qty_list[record]
                                        qty += qty_list[record]
                                    record += 1
                                sheet1.write(r, i + 19, qty, for_body1)
                                supply_list.append(qty)
                            # sheet1.write(r, 37, '')

                    if len(supply_list) == 0:
                        for i in range(17):
                            sheet1.write(r, i + 19, 0, for_body1)
                            supply_list.append(0)

                    shipping_date_list = []
                    qty_list = []

                    # print shipping_date

                if num == 2:
                    sheet1.write(r, 0, tconfirm_line.buyer_id.buyer_erp_id,for_bottom)
                    sheet1.write(r, 1, tconfirm_line.vendor_id.vendor_code,for_bottom)
                    sheet1.write(r, 2, tconfirm_line.material_id.part_no,for_bottom)
                    sheet1.write(r, 3, tconfirm_line.description,for_bottom)
                    sheet1.write(r, 4, tconfirm_line.alt_grp,for_bottom)
                    sheet1.write(r, 5, tconfirm_line.leadtime,for_bottom)
                    sheet1.write(r, 6, tconfirm_line.round_value,for_bottom)
                    sheet1.write(r, 7, tconfirm_line.open_po, for_body1_bottom)
                    sheet1.write(r, 8, tconfirm_line.stock,for_bottom)
                    sheet1.write(r, 9, po_cancel_result, for_body1_bottom)
                    sheet1.write(r, 10, tconfirm_line.b001,for_bottom)
                    sheet1.write(r, 11, tconfirm_line.b002,for_bottom)
                    sheet1.write(r, 12, tconfirm_line.b004,for_bottom)
                    sheet1.write(r, 13, tconfirm_line.b005,for_bottom)
                    sheet1.write(r, 14, tconfirm_line.b012,for_bottom)
                    sheet1.write(r, 15, tconfirm_line.b017b,for_bottom)
                    sheet1.write(r, 16, tconfirm_line.b902s,for_bottom)
                    sheet1.write(r, 17, tconfirm_line.b902q,for_bottom)
                    sheet1.write(r, 36, tconfirm_line.plant_id.plant_code)
                    # if tconfirm_line.storage_location_id.storage_location:
                    #     sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)
                    # else:
                    #     sheet1.write(r, 37, '')
                    # if record_vendor_upload == 1:
                    sheet1.write(r, 37, tconfirm_line.storage_location_id.storage_location)
                    sheet1.write(r, 38, tconfirm_line.storage_location_id.CM_VENDOR)
                    # if record_delivery_edi == 1:
                    #     if storage_location_id:
                    #         sheet1.write(r, 37, storage_location_id.storage_location)
                    #     else:
                    #         sheet1.write(r, 37, '')
                    sheet1.write(r, 18, 'Delta', for_header3)
                    # print demand_list,supply_list
                    # print supply_list[0]-demand_list[0]
                    delta_list.append(supply_list[0] - demand_list[0])
                    if delta_list[0] >= 0:
                        sheet1.write(r, 19, delta_list[0], for_header5)

                    else:
                        # str_show = str(int(abs(delta_list[0]))).num_format_str='#,##0'
                        sheet1.write(r, 19, abs(delta_list[0]), for_header4)


                        # print str_show

                    for i in range(16):
                        delta_list.append(delta_list[i] + supply_list[i + 1] - demand_list[i + 1])
                        if delta_list[i] + supply_list[i + 1] - demand_list[i + 1] >= 0:

                            sheet1.write(r, i + 20, delta_list[i + 1], for_header5)
                        else:
                            sheet1.write(r, i + 20, abs(delta_list[i + 1]), for_header4)
                # print tconfirm_line.qty_w1


                    if delta_list[0]>=0:
                        sheet1.write(r, 19, xlwt.Formula("T" + str(r) + "-" + "T" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 19, xlwt.Formula("T" + str(r) + "-" + "T" + str(r - 1)), for_header4)
                    if delta_list[1]>=0:
                        sheet1.write(r, 20, xlwt.Formula("T"+ str(r+1) +"+" + "U" + str(r) + "-" + "U" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 20,xlwt.Formula("T" + str(r + 1) + "+" + "U" + str(r) + "-" + "U" + str(r - 1)),for_header4)
                    if delta_list[2] >= 0:
                        sheet1.write(r, 21,xlwt.Formula("U" + str(r + 1) + "+" + "V" + str(r) + "-" + "V" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 21,
                                     xlwt.Formula("U" + str(r + 1) + "+" + "V" + str(r) + "-" + "V" + str(r - 1)),
                                     for_header4)
                    if delta_list[3] >= 0:
                        sheet1.write(r, 22,xlwt.Formula("V" + str(r + 1) + "+" + "W" + str(r) + "-" + "W" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 22,
                                     xlwt.Formula("V" + str(r + 1) + "+" + "W" + str(r) + "-" + "W" + str(r - 1)),
                                     for_header4)
                    if delta_list[4] >= 0:
                        sheet1.write(r, 23,xlwt.Formula("W" + str(r + 1) + "+" + "X" + str(r) + "-" + "X" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 23,
                                     xlwt.Formula("W" + str(r + 1) + "+" + "X" + str(r) + "-" + "X" + str(r - 1)),
                                     for_header4)
                    if delta_list[5] >= 0:
                        sheet1.write(r, 24,xlwt.Formula("X" + str(r + 1) + "+" + "Y" + str(r) + "-" + "Y" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 24,
                                     xlwt.Formula("X" + str(r + 1) + "+" + "Y" + str(r) + "-" + "Y" + str(r - 1)),
                                     for_header4)
                    if delta_list[6] >= 0:
                        sheet1.write(r, 25,xlwt.Formula("Y" + str(r + 1) + "+" + "Z" + str(r) + "-" + "Z" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 25,
                                     xlwt.Formula("Y" + str(r + 1) + "+" + "Z" + str(r) + "-" + "Z" + str(r - 1)),
                                     for_header4)
                    if delta_list[7] >= 0:
                        sheet1.write(r, 26,xlwt.Formula("Z" + str(r + 1) + "+" + "AA" + str(r) + "-" + "AA" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 26,
                                     xlwt.Formula("Z" + str(r + 1) + "+" + "AA" + str(r) + "-" + "AA" + str(r - 1)),
                                     for_header4)
                    if delta_list[8] >= 0:
                        sheet1.write(r, 27,xlwt.Formula("AA" + str(r + 1) + "+" + "AB" + str(r) + "-" + "AB" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 27,
                                     xlwt.Formula("AA" + str(r + 1) + "+" + "AB" + str(r) + "-" + "AB" + str(r - 1)),
                                     for_header4)
                    if delta_list[9] >= 0:
                        sheet1.write(r, 28,xlwt.Formula("AB" + str(r + 1) + "+" + "AC" + str(r) + "-" + "AC" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 28,
                                     xlwt.Formula("AB" + str(r + 1) + "+" + "AC" + str(r) + "-" + "AC" + str(r - 1)),
                                     for_header4)
                    if delta_list[10] >= 0:
                        sheet1.write(r, 29,xlwt.Formula("AC" + str(r + 1) + "+" + "AD" + str(r) + "-" + "AD" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 29,
                                     xlwt.Formula("AC" + str(r + 1) + "+" + "AD" + str(r) + "-" + "AD" + str(r - 1)),
                                     for_header4)
                    if delta_list[11] >= 0:
                        sheet1.write(r, 30,xlwt.Formula("AD" + str(r + 1) + "+" + "AE" + str(r) + "-" + "AE" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 30,
                                     xlwt.Formula("AD" + str(r + 1) + "+" + "AE" + str(r) + "-" + "AE" + str(r - 1)),
                                     for_header4)
                    if delta_list[12] >= 0:
                        sheet1.write(r, 31,xlwt.Formula("AE" + str(r + 1) + "+" + "AF" + str(r) + "-" + "AF" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 31,
                                     xlwt.Formula("AE" + str(r + 1) + "+" + "AF" + str(r) + "-" + "AF" + str(r - 1)),
                                     for_header4)
                    if delta_list[13] >= 0:
                        sheet1.write(r, 32,xlwt.Formula("AF" + str(r + 1) + "+" + "AG" + str(r) + "-" + "AG" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 32,
                                     xlwt.Formula("AF" + str(r + 1) + "+" + "AG" + str(r) + "-" + "AG" + str(r - 1)),
                                     for_header4)
                    if delta_list[14] >= 0:
                        sheet1.write(r, 33,xlwt.Formula("AG" + str(r + 1) + "+" + "AH" + str(r) + "-" + "AH" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 33,
                                     xlwt.Formula("AG" + str(r + 1) + "+" + "AH" + str(r) + "-" + "AH" + str(r - 1)),
                                     for_header4)
                    if delta_list[15] >= 0:
                        sheet1.write(r, 34,xlwt.Formula("AH" + str(r + 1) + "+" + "AI" + str(r) + "-" + "AI" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 34,
                                     xlwt.Formula("AH" + str(r + 1) + "+" + "AI" + str(r) + "-" + "AI" + str(r - 1)),
                                     for_header4)
                    if delta_list[16] >= 0:
                        sheet1.write(r, 35,xlwt.Formula("AI" + str(r + 1) + "+" + "AJ" + str(r) + "-" + "AJ" + str(r - 1)),for_header5)
                    else:
                        sheet1.write(r, 35,
                                     xlwt.Formula("AI" + str(r + 1) + "+" + "AJ" + str(r) + "-" + "AJ" + str(r - 1)),
                                     for_header4)

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

