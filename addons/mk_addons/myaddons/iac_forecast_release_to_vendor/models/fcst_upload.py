# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import time,base64
import os
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError

# Fcst Upload
# Laura  add
# Laura  modify 20180710 : 需 帶出代用料。同步修改上傳程式：在上傳時要判斷不是歸屬該buyer的材料,上傳時資料不寫入

class FcstUpload(models.TransientModel):
    _name = 'iac.fcst.upload'
    file_name = fields.Char(u'File Name')
    file = fields.Binary(u'File')
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

    @api.multi
    def action_confirm(self):
        #Fcst Upload

        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0 :
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        excel_obj = open_workbook(file_contents=base64.decodestring(self.file))
        sheet_obj = excel_obj.sheet_by_index(0)

        num = 1
        vals = []
        location_val = []
        for rx in range(sheet_obj.nrows):
            if rx >= 1:

                #material
                #vendor_code
                if isinstance(sheet_obj.cell(rx, 10).value, float):
                    vendor_code_int = int(sheet_obj.cell(rx, 10).value)
                    # print '30:',vendor_code_int
                    vendor_code_str = str(vendor_code_int)
                    if len(vendor_code_str) <= 10:
                        vendor_code = vendor_code_str.zfill(10)
                else:
                    vendor_code_split = sheet_obj.cell(rx,10).value.split()[0]
                    # print '36:',vendor_code_split
                    if len(vendor_code_split) <= 10:
                        # vendor_code = vendor_code_split.zfill(10)
                        vendor_code = vendor_code_split
                #id
                traw_id = str(int(sheet_obj.cell(rx,50).value))
                # print '*45:', traw_id
                traw_export = self.env['iac.traw.data'].sudo().search([('id', '=', traw_id)])

                # 不是該buyer_code的跳過不處理 20180710 laura add
                print '*49:', traw_export.buyer_id.id,' , ',self.env.user.buyer_id_list,' , ',traw_id
                if traw_export.buyer_id.id in self.env.user.buyer_id_list:
                    print '*51:', traw_export.buyer_id.id,' , ',self.env.user.buyer_id_list,' , ',traw_id

                    # print '*44:', traw_export
                    num = num + 1

                    vendor_id = traw_export.vendor_id.id  #self.env['iac.vendor'].search([('vendor_code', '=', vendor_code)]).id
                    material_id = traw_export.material_id.id     # self.env['material.master'].search([('part_no', '=', sheet_obj.cell(rx, 2).value),()]).id
                    plant_id = traw_export.plant_id.id
                    plant_code = traw_export.plant_id.plant_code

                    # 181212 ning add 检查plant和location是否存在
                    location_exist = self.env['iac.storage.location.address'].search(
                            [('plant', '=', plant_code),
                             ('storage_location', '=', sheet_obj.cell(rx, 53).value.upper())])


                    # print '*52:',traw_id,' , ',vendor_id,' , ',material_id,' , ',plant_id
                    # fcst_exist = self.env['iac.traw.data'].search( [('vendor_id', '=', vendor_id),('material_id','=',material_id),('id','=',sheet_obj.cell(rx,50).value)])
                    #print len(fcst_exist)
                    if len(traw_export) == 0:
                        vals.append(str(num))

                    elif len(location_exist) == 0:
                        location_val.append(str(num))
                    else:
                        temp_data_val = {
                            'alt_flag': traw_export.alt_flag,
                            'alt_grp': traw_export.alt_grp,
                            'b001': traw_export.b001,
                            'b002': traw_export.b002,
                            'b004': traw_export.b004,
                            'b005': traw_export.b005,
                            'b012': traw_export.b012,
                            'b017b': traw_export.b017b,

                            'b902q': traw_export.b902q,
                            'b902s': traw_export.b902s,
                            'buyer_id': traw_export.buyer_id.id,
                            'creation_date': traw_export.creation_date,
                            'custpn_info': traw_export.custpn_info,
                            'description': traw_export.description,
                            'division_id': traw_export.division_id.id,
                            'flag': traw_export.flag,

                            'fpversion': traw_export.fpversion,
                            'intransit_qty': traw_export.intransit_qty,
                            'leadtime': traw_export.leadtime,
                            'material_id': traw_export.material_id.id,
                            'max_surplus_qty': traw_export.max_surplus_qty,
                            'mfgpn_info': traw_export.mfgpn_info,
                            'mquota_flag': traw_export.mquota_flag,
                            'open_po': traw_export.open_po,

                            'plant_id': traw_export.plant_id.id,
                            'po': traw_export.po,
                            'pr': traw_export.pr,
                            'qty_w1': sheet_obj.cell(rx,13).value,
                            'qty_w1_r': sheet_obj.cell(rx,14).value,
                            'qty_w2': sheet_obj.cell(rx,15).value,
                            'qty_w3': sheet_obj.cell(rx,16).value,
                            'qty_w4': sheet_obj.cell(rx,17).value,

                            'qty_w5': sheet_obj.cell(rx, 18).value,
                            'qty_w6': sheet_obj.cell(rx, 19).value,
                            'qty_w7': sheet_obj.cell(rx, 20).value,
                            'qty_w8': sheet_obj.cell(rx, 21).value,
                            'qty_w9': sheet_obj.cell(rx, 22).value,
                            'qty_w10': sheet_obj.cell(rx, 23).value,
                            'qty_w11': sheet_obj.cell(rx, 24).value,
                            'qty_w12': sheet_obj.cell(rx, 25).value,
                            'qty_w13': sheet_obj.cell(rx, 26).value,
                            'qty_m1': sheet_obj.cell(rx, 27).value,

                            'qty_m2': sheet_obj.cell(rx, 28).value,
                            'qty_m3': sheet_obj.cell(rx, 29).value,
                            'qty_m4': sheet_obj.cell(rx, 30).value,
                            'qty_m5': sheet_obj.cell(rx, 31).value,
                            'qty_m6': sheet_obj.cell(rx, 32).value,
                            'qty_m7': sheet_obj.cell(rx, 33).value,
                            'qty_m8': sheet_obj.cell(rx, 34).value,
                            'qty_m9': sheet_obj.cell(rx, 35).value,

                            'quota': traw_export.quota,
                            'raw_id': traw_export.id,
                            'remark': traw_export.remark,
                            'round_value': traw_export.round_value,
                            'status': 'T',
                            'stock': traw_export.stock,
                            'vendor_id': traw_export.vendor_id.id,
                            'vendor_name': traw_export.vendor_name,
                            'vendor_reg_id':traw_export.vendor_reg_id.id,
                            'storage_location_id': location_exist.id

                        }
                        self.env['iac.traw.data.temp'].sudo().create(temp_data_val)
                        self.env.cr.commit()
                        print '*136:',traw_id ,',',temp_data_val
        #print vals
        #print len(vals)
        if len(vals) > 0:
            show_str = ''
            show_num = 0
            for item in vals:
                #print item
                show_num += 1
                if show_num == len(vals):
                    show_str = show_str + item
                else:
                    show_str = show_str + item +','
            #print show_str
            raise exceptions.ValidationError("excel第"+show_str+"行，資料錯誤（無此id）")
        elif len(location_val) > 0 :
            show_str = ''
            show_num = 0
            for item in location_val:
                # print item
                show_num += 1
                if show_num == len(vals):
                    show_str = show_str + item
                else:
                    show_str = show_str + item + ','
            # print show_str
            raise exceptions.ValidationError("excel第" + show_str + "行，Location不存在")
        else:
            raise exceptions.ValidationError("匯入成功! ")
