# -*- coding: utf-8 -*-

from odoo import api, models, fields, api, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import time,base64
import datetime

class ConfirmData(models.Model):
    _name = 'iac.tconfirm.data'
    _description = "tConfirm data"
    _order = 'id desc, fpversion'

    raw_id = fields.Many2one('iac.traw.data', string="raw data id",index=True)

    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)

    vendor_code = fields.Char(string="Vendor_code", related="vendor_id.vendor_code")
    material_code = fields.Char(string='Material_code', related='material_id.part_no')
    division_code = fields.Char(string='Division_code', related='division_id.division')
    version = fields.Char(string="version", required=True)
    fpversion = fields.Char(string="FP Version", required=True)
    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    plant_code = fields.Char(string='Plant', related='plant_id.plant_code')
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code", index=True)
    buyer_code = fields.Char(string="buyer_code", related="buyer_id.buyer_erp_id")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info",index=True)
    material_id = fields.Many2one('material.master', 'Material', index=True)  # 料號
    release_flag= fields.Char(string="release_flag", required=True)
    division_id = fields.Many2one('division.code', string='Division Info',index=True)
    description = fields.Char(string="品名")
    alt_grp = fields.Char(string="Alternate Group")
    alt_flag = fields.Char(string="是否替代料")
    stock = fields.Float(string='庫存量')
    open_po = fields.Float(string='total open po qty')
    intransit_qty = fields.Float(string='在途量')
    quota = fields.Float(string='配額')  # 配額
    round_value = fields.Float(string='Round value')
    leadtime = fields.Integer(string="L/T")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration",index=True)
    vendor_name = fields.Char(string='vendor name')
    buyer_name_en = fields.Char(related='buyer_id.buyer_name')
    buyer_name_cn = fields.Char(related='buyer_id.name_cn')
    department = fields.Char(related='buyer_id.department')
    vendor_name_cn = fields.Char(string='vendor name cn', related='vendor_id.name')
    vendor_name_en = fields.Char(related='vendor_reg_id.name1_en')
    qty_w1 = fields.Float(string='W1 MAX ASN QTY')
    qty_w1_r = fields.Float(string="qty_w1_r")
    qty_w2 = fields.Float(string="qty_w2")
    qty_w3 = fields.Float(string="qty_w3")
    qty_w4 = fields.Float(string="qty_w4")
    qty_w5 = fields.Float(string="qty_w5")
    qty_w6 = fields.Float(string="qty_w6")
    qty_w7 = fields.Float(string="qty_w7")
    qty_w8 = fields.Float(string="qty_w8")
    qty_w9 = fields.Float(string="qty_w9")
    qty_w10 = fields.Float(string="qty_w10")
    qty_w11 = fields.Float(string="qty_w11")
    qty_w12 = fields.Float(string="qty_w12")
    qty_w13 = fields.Float(string="qty_w13")

    qty_m1 = fields.Float(string="qty_m1")
    qty_m2 = fields.Float(string="qty_m2")
    qty_m3 = fields.Float(string="qty_m3")
    qty_m4 = fields.Float(string="qty_m4")
    qty_m5 = fields.Float(string="qty_m5")
    qty_m6 = fields.Float(string="qty_m6")
    qty_m7 = fields.Float(string="qty_m7")
    qty_m8 = fields.Float(string="qty_m8")
    qty_m9 = fields.Float(string="qty_m9")

    creation_date = fields.Date(string="creation Date")
    create_by = fields.Char(string="create_by")
    po = fields.Char(string="po")
    pr = fields.Char(string="pr")
    remark = fields.Char(string="Remark")

    b001 = fields.Float(string="B_001")
    b002 = fields.Float(string="B_002")
    b004 = fields.Float(string="B_004")
    b005 = fields.Float(string="B_005")
    b012 = fields.Float(string="B_012")
    b017b = fields.Float(string="B_017B")
    b902s = fields.Float(string="B_902S")
    b902q = fields.Float(string="B_902Q")
    custpn_info = fields.Char(string="Cust PN")
    mfgpn_info = fields.Char(string="MFG PN")
    flag = fields.Char(string="試產料")
    max_surplus_qty = fields.Char(string="SurplusMaxQty")
    mquota_flag = fields.Char(string="未維護Quota")

    reply_ids = fields.One2many("iac.tvendor.upload", "reply_id", string="Temp reply vendors",index=True)
    reply2_ids = fields.One2many("iac.tdelivery.upload", "reply_id", string="Temp reply buyers", index=True)
    reply3_ids = fields.One2many("iac.max.cdt.upload", "reply_id", string="Temp reply max cdt", index=True) #20180709 laura add

    key_part = fields.Selection([('Y','Y'),('N','N')],string='key part',index=True,copy=False,default='Y')

    buyer_remark = fields.Char(string="Remark")

    # 紀錄 "调用SAP接口"是否成功的欄位____s
    state = fields.Selection([
        ('pending', 'Pending'),  # 等待拋轉中
        ('fp error(Update)', 'FP Error(Update)'),  # 通知FP失敗 Update
        ('fp error(Delete)', 'FP Error(Delete)'),  # 通知FP失敗 Delete
        ('fp error(Insert)', 'FP Error(Insert)'),  # 通知FP失敗 Insert
        ('finished(Update)', 'Finished(Update)'),  # 更新FP成功 Update
        ('finished(Delete)', 'Finished(Delete)'),  # 更新FP成功 Delete
        ('finished(Insert)', 'Finished(Insert)')  # 更新FP成功  Insert
    ], string='Status', readonly=True, index=True, copy=False,default='pending',track_visibility='onchange')
    state_msg = fields.Char()
    # 紀錄 "调用SAP接口"是否成功的欄位____e

    group_id = fields.Many2one('iac.tconfirm.data.group')  #20180702 laura add  for整批拋FP
    edi_version = fields.Char(string="EDI Version" )  # EDI 830 用  version 20180704 laura add
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

    # buyer 的 Reply -- '回覆LT'  '確認'
    @api.multi
    def buyer_action_confirm(self, values):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # fields.Char(string="今天日期",
        error_num = ''
        error_str = ''

        val = {}
        group = self.env['iac.tdelivery.upload.group'].sudo().create(val)
        group.env.cr.commit()

        tdelivery = self.env['iac.tdelivery.upload'].sudo().search([('reply_id','=',self.id),('status', '=', 'T')])
        vals = {}
        vals['group_id'] = group.id
        vals['write_date'] = today_str  # 20180803 laura add
        # print '*129:', vals
        tdelivery.write(vals)
        tdelivery.env.cr.commit()

        # 檢查 Qty = 0 or 空白，Remark 必填____s
        if (self.buyer_remark == '' or self.buyer_remark == False):
            print '*135:', self.key_part ,',',  self.id ,',', self.buyer_remark
            qty_check = self.env['iac.tdelivery.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T'), ('qty', '>', '0')])
            # print '*138:', qty_check
            if qty_check:
                print '*140'
            else:
                error_str = error_str + ' Qty = 0 or 空白，[Remark]  必填。/[Remark] is required when all the shipping quantity is blank or equals to 0.    ';
        # 檢查 Qty = 0 or 空白，Remark 必填____e

        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----s
        if self.key_part == 'N':
            # print '*145:', self.id
            qty_ck2 = self.env['iac.tdelivery.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T'), ('qty', '>', '0')])
            # print '*148:', qty_ck2
            if qty_ck2:
                # 1. 先報錯誤訊息
                error_str = error_str + ' Key Part 欄位為"N"，56天交期不允許有數量! Qty 需= 0 or 空白。/Remove all shipping quantity and leave it blank when [Key Part] is ‘N’.    ';
                # 2. 再把 qty>0,數量改0
                qty_ck2.write({"qty": "0"})
        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----e

        #檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___s
        if self.key_part=='N' and (self.buyer_remark=='' or self.buyer_remark==False) :
            # print '*158:  "Key Part 欄位為‘N’，[Remark] 欄位不可空白" '
            error_str = error_str + ' Key Part 欄位為 ‘N’，[Remark] 欄位不可空白。/[Remark] is required when [Key Part] is ‘N’.    ' ;
        # 檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___e

        for item in self.reply2_ids:
            # 逐筆檢查 iac.tdelivery.upload：料+vendor+buyer+日期 是否有回填多筆數量
            self._cr.execute(" select  count(*) as count from iac_tdelivery_upload "
                             "   where status='T' and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s"
                             ,( self.id,self.plant_id.id,self.material_id.id,self.buyer_id.id,item.shipping_date))
            for row in self.env.cr.dictfetchall():
                count = row['count']
            if count >=2:
                error_num = error_num + str(item.shipping_date) + ' , '

        if error_num <> '':
            # 把同shipping_date 重覆產生的資料刪除後抱錯
            self._cr.execute(" delete from iac_tdelivery_upload "
                             "   where status='T' and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s"
                             , (self.id, self.plant_id.id, self.material_id.id, self.buyer_id.id, item.shipping_date))
            self.env.cr.commit()
            error_str = error_str + '日期：'+ error_num +'錯誤，同天日期回填多筆數量。/Shipping Date is duplicate.    ' ;

        if error_str <> '':
            raise exceptions.ValidationError(error_str)

        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___s
        if self.key_part == 'N':
            fpversion = self.fpversion
            day1 = self.getDay1(fpversion)  # 函數：給fpversion ?取day1的日期
            iac_pn_vendor = str(self.material_id.part_no) + self.vendor_id.vendor_code
            # print '*167:', iac_pn_vendor, ',', self.fpversion, ',', day1
            # print " 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 "

            # 先檢查有效的舊資料中是否已存在day1的資料,沒有在insert
            check = self.env['iac.tdelivery.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T'), ('shipping_date', '=', day1)])
            # print '*266:', check.id
            if not check:
                # print '*162:', check.id
                ins_vendor_upload_val = {
                    'status': 'T',  # T: true有效
                    'plant_id': self.plant_id.id,
                    'buyer_id': self.buyer_id.id,
                    'material_id': self.material_id.id,
                    'vendor_id': self.vendor_id.id,
                    'key_part': self.key_part,
                    'iac_pn_vendor': iac_pn_vendor,
                    'qty': 0,
                    'shipping_date': day1,
                    'buyer_remark': self.buyer_remark,
                    'write_date': today_str,  # 20180803 laura add
                    # 'write_uid': self._uid,
                    # 'create_uid': self._uid,
                    'reply_id': self.id
                }
                # print '*191:', ins_vendor_upload_val
                t_data = self.env['iac.tdelivery.upload'].sudo().create(ins_vendor_upload_val)
                t_data.env.cr.commit()
                t_data.write(vals)
                t_data.env.cr.commit()

                t_data._cr.execute("  update iac_tdelivery_upload set write_uid= %s , create_uid =%s ,write_date=%s"  #20180803 laura add
                                   "      where id=  %s   ", (self._uid, self._uid, today_str,t_data.id))
                print '*224:', self._uid, ',', t_data.id
        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___e

        # call 接口-----s
        #  2. 调用SAP接口執行更新FP数据的 SP : ___s
        #      (2) update iac_tdelivery_upload 資料的這筆 id
        print '* 236 : confirm_data.py  開始調用SAP接口'
        biz_object = {
            "id": group.id,
            "biz_object_id": group.id,
            "sql_type": "U"  # I : insert , U : update
        }

        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_005", biz_object)

        if rpc_result:
            # 调用SAP接口 成功的情况下,修改记录状态
            tdelivery.write({"state": "finished(Update)"})
        else:
            tdelivery.write({'state': 'fp error(Update)', 'state_msg': u'拋轉FP失败(Update)'})
        print '*252 :   vendor_upload_lt.py 結束 調用SAP接口 '
        #  2. 调用SAP接口執行更新FP数据的 SP : ___e
        #      (2) update iac_tdelivery_upload 資料的這筆 id
        # call 接口-----e

        # 將 iac.tconfirm.data 的  key_part , buyer_remark  更新到 iac.tdelivery.upload , iac.tdelivery.upload
        # print '*186', self.buyer_remark
        if self.buyer_remark == False:
            self.buyer_remark = ''

        tdelivery._cr.execute(" update iac_tdelivery_upload set write_uid= %s ,create_uid =%s,"
                              "              key_part = %s, buyer_remark = %s ,write_date=%s " #20180803 laura add
                              "   where reply_id= %s and status='T'  "
                        , (self._uid,self._uid,self.key_part,self.buyer_remark,today_str,self.id))
    #取得day1 的函數---s
    @api.model
    def getDay1(self,fpversion):
        """  給fpversion 获取day1的日期
               :param fpversion:
               :return: day1
               """
        # print '*204:',fpversion

        real_year = str(time.localtime(time.time()).tm_year)
        real_month = str(time.localtime(time.time()).tm_mon)
        real_day = str(time.localtime(time.time()).tm_mday)

        tcolumn_title = self.env['iac.tcolumn.title'].sudo().search([('fpversion', '=', fpversion)])
        if not tcolumn_title:
            raise UserError('此筆FCST錯誤(找不到對應的iac_tconfirm_data)。/FCST record missed (Cannot find corresponding iac_tconfirm_data).    ')
        else:
            qty_w1_r = tcolumn_title.qty_w1_r
            month = int(qty_w1_r[5:7])
            month_1 = int(qty_w1_r[5:7])
            if month_1 > 1 and month_1 < 12:
                year = int(real_year)
            else:
                if month_1 == int(real_month):
                    year = int(real_year)
                else:
                    year = int(real_year) - 1
            start_date = str(year) + '-' + qty_w1_r[5:7] + '-' + qty_w1_r[7:9]

        # print '*227:', start_date ,',',qty_w1_r ,',',fpversion
        return start_date
    # 取得day1 的函數---e

    # vendor 的  Reply  -- '回覆LT'  '確認'
    @api.multi
    def vendor_action_confirm(self, values):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # fields.Char(string="今天日期",

        error_num = ''
        error_str = ''
        val = {}
        group = self.env['iac.tvendor.upload.group'].sudo().create(val)
        group.env.cr.commit()
        # print '*217:', group, ',', group.id, ',', val, ',', self.id

        tvendor = self.env['iac.tvendor.upload'].sudo().search([('reply_id', '=', self.id),('status', '=', 'T')])
        vals = {}
        vals['group_id'] = group.id
        vals['write_date'] = today_str   # 20180803 laura add
        print '*316:', vals
        tvendor.write(vals)
        tvendor.env.cr.commit()
        # print '*229:', group, ',', group.id, ',', val, ',', self.id

        # 檢查 Qty = 0 or 空白，Remark 必填____s
        if  (self.buyer_remark == '' or self.buyer_remark == False):
            print '*312:', self.key_part, ',', self.id, ',', self.buyer_remark
            qty_check = self.env['iac.tvendor.upload'].sudo().search([('reply_id', '=', self.id),('status', '=', 'T'),('qty', '>', '0')])
            print '*300:',qty_check
            if qty_check:
                print '*317'
            else:
                error_str = error_str + ' Qty = 0 or 空白，[Remark]  必填。/[Remark] is required when all the shipping quantity is blank or equals to 0.    ';

        # 檢查 Qty = 0 or 空白，Remark 必填____e

        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----s
        if self.key_part == 'N':
            print '*324:', self.id
            qty_ck2 = self.env['iac.tvendor.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T'), ('qty', '>', '0')])
            print '*327:', qty_ck2
            if qty_ck2:
                # 1. 先報錯誤訊息
                error_str = error_str + ' Key Part 欄位為"N"，56天交期不允許有數量! Qty 需= 0 or 空白。/Remove all shipping quantity and leave it blank when [Key Part] is ‘N’.    ';
                # 2. 再把 qty>0,數量改0
                qty_ck2.write({"qty": "0"})
        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----e

        # 檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___s
        if self.key_part == 'N' and (self.buyer_remark == '' or self.buyer_remark == False):
            # print '*229:  "Key Part 欄位為‘N’，[Remark] 欄位不可空白" '
            error_str = error_str + ' Key Part 欄位為 ‘N’，[Remark] 欄位不可空白。/[Remark] is required when [Key Part] is ‘N’.    ';
        # 檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___e

        for item in self.reply_ids:

            # 逐筆檢查 iac.tvendor.upload：料+vendor+buyer+日期 是否有回填多筆數量
            self._cr.execute(" select  count(*) as count from iac_tvendor_upload "
                             "   where status='T'  and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s "
                             ,( self.id,self.plant_id.id,self.material_id.id,self.buyer_id.id,item.shipping_date))
            for row in self.env.cr.dictfetchall():
                count = row['count']
            if count >=2:
                error_num = error_num + str(item.shipping_date) + ' , '

        if error_num <> '':
            # 把同shipping_date 重覆產生的資料刪除後抱錯
            self._cr.execute(" delete from iac_tvendor_upload "
                             "   where status='T' and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s "
                             , (self.id, self.plant_id.id, self.material_id.id, self.buyer_id.id, item.shipping_date))
            self.env.cr.commit()
            error_str = error_str + '日期：' + error_num + '錯誤，同天日期回填多筆數量。/Shipping Date is duplicate.    ';

        if error_str <> '':
            raise exceptions.ValidationError(error_str)


        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___s
        if self.key_part == 'N':
            fpversion = self.fpversion
            day1 = self.getDay1(fpversion)  # 函數：給fpversion 获取day1的日期
            iac_pn_vendor = str(self.material_id.part_no) + self.vendor_id.vendor_code
            print '*261:', iac_pn_vendor,',', self.fpversion,',', day1
            # print " 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 "

            # 先檢查有效的舊資料中是否已存在day1的資料,沒有在insert
            check = self.env['iac.tvendor.upload'].sudo().search([('reply_id', '=', self.id), ('status', '=', 'T'), ('shipping_date', '=', day1)])
            # print '*266:', check.id
            if not check:
                print '*268:', check.id
                ins_vendor_upload_val = {
                    'status': 'T',  # T: true有效
                    'plant_id': self.plant_id.id,
                    'buyer_id': self.buyer_id.id,
                    'material_id': self.material_id.id,
                    'vendor_id': self.vendor_id.id,
                    'key_part': self.key_part,
                    'iac_pn_vendor': iac_pn_vendor,
                    'qty': 0,
                    'shipping_date': day1,
                    'buyer_remark': self.buyer_remark,
                    'write_date': today_str,  # 20180803 laura add
                    'write_uid': self._uid,
                    'create_uid': self._uid,
                    'reply_id': self.id
                }
                print '*396:', ins_vendor_upload_val
                t_data = self.env['iac.tvendor.upload'].sudo().create(ins_vendor_upload_val)
                t_data.env.cr.commit()
                t_data.write(vals)
                t_data.env.cr.commit()

                t_data._cr.execute("  update iac_tvendor_upload set write_uid= %s , create_uid =%s ,write_date =%s"
                                   "      where id=  %s   ",(self._uid, self._uid,today_str,t_data.id))

                print '*413:', self._uid,',',t_data.id
        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___e

        # call 接口-----s
        #  2. 调用SAP接口執行更新FP数据的 SP : ___s
        #      (2) update iac_tvendor_upload 資料的這筆 id
        print '* 415 : confirm_data.py  開始調用SAP接口'
        biz_object = {
            "id": group.id,
            "biz_object_id": group.id,
            "sql_type": "U"  # I : insert , U : update , D: delete
        }

        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_004", biz_object)

        if rpc_result:
            print '*426 : state :  finished(Update) ' ,',',self.id,',',group.id
            # 调用SAP接口 成功的情况下,修改记录状态
            tvendor.write({"state": "finished(Update)"})
        else:
            tvendor.write({'state': 'fp error(Update)', 'state_msg': u'拋轉FP失败(Update)'})
        print '*425:   confirm_data.py 結束 調用SAP接口 '
        #  2. 调用SAP接口執行更新FP数据的 SP : ___e
        #      (2) update iac_tvendor_upload 資料的這筆 id
        # call 接口-----e

        # 將 iac.tconfirm.data 的  key_part , buyer_remark  更新到 iac.tvendor.upload
        print '*431', self.buyer_remark
        if self.buyer_remark == False :
            self.buyer_remark = ''

        tvendor._cr.execute("  update iac_tvendor_upload set write_uid= %s, create_uid =%s,"
                            "              key_part = %s,buyer_remark = %s ,write_date = %s" #20180803 laura add
                            "   where status='T' and reply_id= %s   "
                         , (self._uid,self._uid,self.key_part,self.buyer_remark,today_str,self.id))

    # max_cdt 的 Reply -- '回覆LT'  '確認'
    @api.multi
    def max_cdt_action_confirm(self, values):
        # 20180710 laura add
        # self 是 iac.tconfirm.data
        today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # fields.Char(string="今天日期",

        error_num = ''
        error_str = ''
        val = {}
        group = self.env['iac.max.cdt.upload.group'].sudo().create(val)
        group.env.cr.commit()
        # print '*454', group, ',', group.id, ',', val, ',', self.id

        # update  confirm_data  set group_id
        vals = {}
        vals['group_id'] = group.id
        self.write(vals)
        self.env.cr.commit()

        # update  iac.max.cdt.upload  set group_id
        vals = {}
        vals['group_id'] = group.id
        max_cdt = self.env['iac.max.cdt.upload'].sudo().search([('reply_id', '=', self.id)])
        # print '*466:',group.id ,',',self.id
        # print '*467:',max_cdt
        max_cdt.write(vals)
        max_cdt.env.cr.commit()

        # 檢查 Qty = 0 or 空白，Remark 必填____s
        if  (self.buyer_remark == '' or self.buyer_remark == False):
            # print '*464:', self.key_part, ',', self.id, ',', self.buyer_remark
            qty_check = self.env['iac.max.cdt.upload'].sudo().search([('reply_id', '=', self.id),('status', '=', 'T'),('qty', '>', '0')])
            # print '*466:',qty_check
            if qty_check:
                print '*477'
            else:
                error_str = error_str + ' Qty = 0 or 空白，[Remark]  必填。/[Remark] is required when all the shipping quantity is blank or equals to 0.    ';

        # 檢查 Qty = 0 or 空白，Remark 必填____e

        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----s
        if self.key_part == 'N':
            # print '*476:', self.id
            qty_ck2 = self.env['iac.max.cdt.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T'), ('qty', '>', '0')])
            # print '*479:', qty_ck2
            if qty_ck2:
                # 1. 先報錯誤訊息
                error_str = error_str + ' Key Part 欄位為"N"，56天交期不允許有數量! Qty 需= 0 or 空白。/Remove all shipping quantity and leave it blank when [Key Part] is ‘N’.    ';
                # 2. 再把 qty>0,數量改0
                qty_ck2.write({"qty": "0"})
        # 檢查 "Key Part 欄位為 ‘N’，56天交期不允許有數量!  qty 只能填0----e

        # 檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___s
        if self.key_part == 'N' and (self.buyer_remark == '' or self.buyer_remark == False):
            # print '*229:  "Key Part 欄位為‘N’，[Remark] 欄位不可空白" '
            error_str = error_str + ' Key Part 欄位為 ‘N’，[Remark] 欄位不可空白。/[Remark] is required when [Key Part] is ‘N’.    ';
        # 檢查 "Key Part 欄位為 ‘N’，[Remark] 欄位不可空白" ___e

        for item in self.reply3_ids:
            # 逐筆檢查 max_cdt 表 ：料+vendor+buyer+日期 是否有回填多筆數量
            self._cr.execute(" select  count(*) as count from iac_max_cdt_upload  "
                             "   where status='T'  and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s and storage_location_id=%s "
                             ,( self.id,self.plant_id.id,self.material_id.id,self.buyer_id.id,item.shipping_date,self.storage_location_id.id))
            for row in self.env.cr.dictfetchall():
                count = row['count']
            if count >=2:
                error_num = error_num + str(item.shipping_date) + ' , '

        if error_num <> '':
            # 把同shipping_date 重覆產生的資料刪除後抱錯
            self._cr.execute(" delete from iac_max_cdt_upload "
                             "   where status='T' and reply_id= %s  and plant_id= %s and material_id= %s"
                             "       and buyer_id = %s and shipping_date= %s and storage_location_id=%s "
                             , (self.id, self.plant_id.id,self.material_id.id,
                                self.buyer_id.id, item.shipping_date,self.storage_location_id.id))
            self.env.cr.commit()
            error_str = error_str + '日期：' + error_num + '錯誤，同天日期回填多筆數量。/Shipping Date is duplicate.    ';

        if error_str <> '':
            raise exceptions.ValidationError(error_str)

        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___s
        if self.key_part == 'N':
            fpversion = self.fpversion
            day1 = self.getDay1(fpversion)  # 函數：給fpversion 获取day1的日期
            iac_pn_vendor = str(self.material_id.part_no) + self.vendor_id.vendor_code
            print '*522:', iac_pn_vendor,',', self.fpversion,',', day1
            # print " 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 "

            # 先檢查有效的舊資料中是否已存在day1的資料,沒有在insert
            print '*527:', self.id, ',', self.fpversion, ',', day1
            check = self.env['iac.max.cdt.upload'].sudo().search([('reply_id', '=', self.id), ('status', '=', 'T'), ('shipping_date', '=', day1)]) #day1
            # print '*266:', check.id
            if not check:
                print '*530:', check.id
                ins_max_cdt_upload_val = {
                    'status': 'T',  # T: true有效
                    'plant_id': self.plant_id.id,
                    'buyer_id': self.buyer_id.id,
                    'material_id': self.material_id.id,
                    'vendor_id': self.vendor_id.id,
                    'key_part': self.key_part,
                    'iac_pn_vendor': iac_pn_vendor,
                    'qty': 0,
                    'shipping_date': day1,
                    'buyer_remark': self.buyer_remark,
                    'write_uid': self._uid,
                    'create_uid': self._uid,
                    'reply_id': self.id,
                    'group_id': group.id,
                    'storage_location_id':self.storage_location_id.id
                }
                print '*547:', ins_max_cdt_upload_val
                t_data = self.env['iac.max.cdt.upload'].sudo().create(ins_max_cdt_upload_val)
                t_data.env.cr.commit()
                # t_data.write(vals)
                # t_data.env.cr.commit()

                vals = {}
                vals['write_uid'] = self._uid
                vals['create_uid'] = self._uid
                vals['write_date'] = today_str   # 20180803 laura add
                t_data.write(vals)
                # t_data._cr.execute("  update iac_max_cdt_upload set write_uid= %s , create_uid =%s "
                #                    "      where id=  %s   ",(self._uid, self._uid,t_data.id))

                print '*569:', self._uid,',',t_data.id
        # 若填寫 Key Part=N, 程式要自動塞一筆 Shipping Date=Day 1, Qty=0 的記錄到 table 中 ___e

        # 將 iac.tconfirm.data 的  key_part , buyer_remark  更新到 iac.tvendor.upload
        print '*573', self.buyer_remark
        if self.buyer_remark == False:
            self.buyer_remark = ''

        vals = {}
        vals['write_uid'] = self._uid
        vals['create_uid'] = self._uid
        vals['key_part'] = self.key_part
        vals['buyer_remark'] = self.buyer_remark
        vals['write_date'] =  today_str  # 20180803 laura add
        self.write(vals)

        # self._cr.execute("  update iac_max_cdt_upload set write_uid= %s, create_uid =%s,"
        #                     "              key_part = %s,buyer_remark = %s "
        #                     "   where status='T' and reply_id= %s   "
        #                     , (self._uid, self._uid, self.key_part, self.buyer_remark, self.id))

        print '*589:',self.id ,',',group.id
        # 1.判斷 使用者是 buyer / vendor判斷法： if res_partner.Supplier = 't' then  'vendor'  else  '內部user'
        All_max_cdt = self.env['iac.max.cdt.upload'].sudo().search([('reply_id', '=', self.id), ('status', '=', 'T')])

        supplier = self.env.user.partner_id.supplier
        if supplier == True:
            print '*584'
            #Vendor
            # 1.將 iac_max_cdt_upload 結果 insert into & update 舊版 status=F
            #  1.1 先update 舊版 status=F
            old_update = self.env['iac.tvendor.upload'].sudo().search([('reply_id', '=', self.id), ('status', '=', 'T')])
            old_u_vals = {}
            old_u_vals['status'] = 'F'
            old_u_vals['write_date'] =  today_str  # 20180803 laura add
            old_update.write(old_u_vals)
            print '*603:',old_u_vals ,',', old_update
            old_update.env.cr.commit()

            #  1.2 先  insert into 對應的 iac.tvendor.upload.group
            val = {}
            vendor_group = self.env['iac.tvendor.upload.group'].sudo().create(val)
            vendor_group.env.cr.commit()
            # vendor_group.id

            #  1.3 再  insert into update 舊版 status=F
            for item in All_max_cdt:
                iac_pn_vendor = str(item.material_id.part_no) + item.vendor_id.vendor_code
                ins_max_cdt_upload_val = {
                    'status': 'T',  # T: true有效
                    'plant_id': item.plant_id.id,
                    'buyer_id': item.buyer_id.id,
                    'material_id': item.material_id.id,
                    'vendor_id': item.vendor_id.id,
                    'key_part': self.key_part,
                    'iac_pn_vendor':  iac_pn_vendor,
                    'qty': item.qty,
                    'shipping_date': item.shipping_date,
                    'buyer_remark': self.buyer_remark,
                    'write_date': today_str,  # 20180803 laura add
                    'write_uid': item._uid,
                    'create_uid': item._uid
                    ,'reply_id': self.id
                    ,'group_id': vendor_group.id,
                    'storage_location_id':self.storage_location_id.id
                }
                ins_vendor = self.env['iac.tvendor.upload'].sudo().create(ins_max_cdt_upload_val)
                ins_vendor.env.cr.commit()
                print '*622:',ins_max_cdt_upload_val
                print '*623:',vendor_group.id,',',group.id,',',self.id,',',item.id,',',self.reply_ids
            #Vendor  2. call 接口----s
            # 2.1. call 接口: 先 delete  t_vendor_upload 同plant、iac_pn、vendor_code   ODOO_FP_006
            biz_object = {
                "id": vendor_group.id,
                "biz_object_id": vendor_group.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_006", biz_object)
            # 2.2. call 接口: 再依照 group_id  insert into  t_vendor_upload  ODOO_FP_004  sql_type": "I"
            biz_object2 = {
                "id": vendor_group.id,
                "biz_object_id": vendor_group.id,
                "sql_type": "I"  # I : insert , U : update
            }
            rpc_result2, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_004", biz_object2)
            #Vendor  2. call 接口----e

            vals = {
                'action_type': 'Reply',
                'vendor_id':self.vendor_id.id
            }
            self.env['iac.supplier.key.action.log'].create(vals)
            self.env.cr.commit()
        else:
            # Buyer
            # 1.將 iac_max_cdt_upload 結果 insert into & update 舊版 status=F
            #  1.1 先update 舊版 status=F
            old_update = self.env['iac.tdelivery.upload'].sudo().search(
                [('reply_id', '=', self.id), ('status', '=', 'T')])
            old_u_vals = {}
            old_u_vals['status'] = 'F'
            old_u_vals['write_date'] = today_str  # 20180803 laura add
            old_update.write(old_u_vals)
            print '*671:', old_u_vals, ',', old_update
            old_update.env.cr.commit()

            #  1.2 先  insert into 對應的 iac.tdelivery.upload.group
            val = {}
            buyer_group = self.env['iac.tdelivery.upload.group'].sudo().create(val)
            buyer_group.env.cr.commit()
            # buyer_group.id

            #  1.3 再  insert into update 舊版 status=F
            for item in All_max_cdt:
                iac_pn_vendor = str(item.material_id.part_no) + item.vendor_id.vendor_code
                ins_max_cdt_upload_val = {
                    'status': 'T',  # T: true有效
                    'plant_id': item.plant_id.id,
                    'buyer_id': item.buyer_id.id,
                    'material_id': item.material_id.id,
                    'vendor_id': item.vendor_id.id,
                    'key_part': self.key_part,
                    'iac_pn_vendor': iac_pn_vendor,
                    'qty': item.qty,
                    'shipping_date': item.shipping_date,
                    'buyer_remark': self.buyer_remark,
                    'write_date': today_str,  # 20180803 laura add
                    'write_uid': item._uid,
                    'create_uid': item._uid
                    , 'reply_id': self.id
                    , 'group_id': buyer_group.id,
                    'storage_location_id':self.storage_location_id.id
                }
                ins_vendor = self.env['iac.tdelivery.upload'].sudo().create(ins_max_cdt_upload_val)
                ins_vendor.env.cr.commit()
                print '*680:', ins_max_cdt_upload_val
                print '*681:', buyer_group.id, ',', group.id, ',', self.id, ',', item.id, ',', self.reply_ids
            # Buyer  2. call 接口----s
            # 2.1. call 接口: 先 delete  t_delivery_upload 同plant、iac_pn、vendor_code   ODOO_FP_007
            biz_object = {
                "id": buyer_group.id,
                "biz_object_id": buyer_group.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_007", biz_object)
            # 2.2. call 接口: 再依照 group_id  insert into  t_delivery_upload  ODOO_FP_005  sql_type": "I"
            biz_object2 = {
                "id": buyer_group.id,
                "biz_object_id": buyer_group.id,
                "sql_type": "I"  # I : insert , U : update
            }
            rpc_result2, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_005", biz_object2)
            # Buyer  2. call 接口----e
        # call 接口-----s


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        print '*667'
        # return self.env['warning_box'].info(title='error! ', message='93!')
        qty_w1_r=''
        # 動態field_name：將 file name 改為從 DB select ( iac_tcolumn_title ) 出來
        self._cr.execute( " select fpversion,qty_w1_r, qty_w2,qty_w3,qty_w4,qty_w5,"
                          "qty_w6,qty_w7,qty_w8,qty_w9,qty_w10,"
                          "qty_w11,qty_w12,qty_w13,"
                          "qty_m1,qty_m2,qty_m3,qty_m4,qty_m5,qty_m6,"
                          "qty_m7,qty_m8,qty_m9 "
                          "from iac_tcolumn_title "
                          "where fpversion in ( select max (fpversion) from iac_traw_data ) " )
        for row in self.env.cr.dictfetchall():
            fpversion = str(row['fpversion'])
            qty_w1_r = str(row['qty_w1_r'])
            qty_w2 = str(row['qty_w2'])
            qty_w3 = str(row['qty_w3'])
            qty_w4 = str(row['qty_w4'])
            qty_w5 = str(row['qty_w5'])
            qty_w6 = str(row['qty_w6'])
            qty_w7 = str(row['qty_w7'])
            qty_w8 = str(row['qty_w8'])
            qty_w9 = str(row['qty_w9'])
            qty_w10 = str(row['qty_w10'])
            qty_w11 = str(row['qty_w11'])
            qty_w12 = str(row['qty_w12'])
            qty_w13 = str(row['qty_w13'])
            qty_m1 = str(row['qty_m1'])
            qty_m2 = str(row['qty_m2'])
            qty_m3 = str(row['qty_m3'])
            qty_m4 = str(row['qty_m4'])
            qty_m5 = str(row['qty_m5'])
            qty_m6 = str(row['qty_m6'])
            qty_m7 = str(row['qty_m7'])
            qty_m8 = str(row['qty_m8'])
            qty_m9 = str(row['qty_m9'])

        if qty_w1_r == '' :
            print '*479'
            raise exceptions.ValidationError('此筆FCST錯誤(找不到對應的iac_tconfirm_data)。/FCST record missed (Cannot find corresponding iac_tconfirm_data).    ')
        else:
            print '*482'
            tree_view_id = self.env['ir.model.data'].xmlid_to_res_id('iac_forecast_release_to_vendor.view_confirm_data_list')
            tree2_view_id = self.env['ir.model.data'].xmlid_to_res_id('iac_forecast_release_to_vendor.view_upload_lt_web')

            res = super(ConfirmData, self).fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)

            if self.env.cr.dictfetchall() and view_id==tree_view_id or view_id==tree2_view_id  :
                print ' 489 :', view_id
                res['arch'] = res['arch'].replace('<field name="qty_w1_r" string="qty_w1_r" ','<field name="qty_w1_r" string="%s" ')% (qty_w1_r)
                res['arch'] = res['arch'].replace('<field name="qty_w2" string="qty_w2" ','<field name="qty_w2" string="%s" ') % (qty_w2)
                res['arch'] = res['arch'].replace('<field name="qty_w3" string="qty_w3" ','<field name="qty_w3" string="%s" ') % (qty_w3)
                res['arch'] = res['arch'].replace('<field name="qty_w4" string="qty_w4" ','<field name="qty_w4" string="%s" ') % (qty_w4)
                res['arch'] = res['arch'].replace('<field name="qty_w5" string="qty_w5" ','<field name="qty_w5" string="%s" ') % (qty_w5)
                res['arch'] = res['arch'].replace('<field name="qty_w6" string="qty_w6" ','<field name="qty_w6" string="%s" ') % (qty_w6)
                res['arch'] = res['arch'].replace('<field name="qty_w7" string="qty_w7" ','<field name="qty_w7" string="%s" ') % (qty_w7)
                res['arch'] = res['arch'].replace('<field name="qty_w8" string="qty_w8" ','<field name="qty_w8" string="%s" ') % (qty_w8)
                res['arch'] = res['arch'].replace('<field name="qty_w9" string="qty_w9" ','<field name="qty_w9" string="%s" ') % (qty_w9)
                res['arch'] = res['arch'].replace('<field name="qty_w10" string="qty_w10" ','<field name="qty_w10" string="%s" ') % (qty_w10)
                res['arch'] = res['arch'].replace('<field name="qty_w11" string="qty_w11" ','<field name="qty_w11" string="%s" ') % (qty_w11)
                res['arch'] = res['arch'].replace('<field name="qty_w12" string="qty_w12" ','<field name="qty_w12" string="%s" ') % (qty_w12)
                res['arch'] = res['arch'].replace('<field name="qty_w13" string="qty_w13" ','<field name="qty_w13" string="%s" ') % (qty_w13)

                res['arch'] = res['arch'].replace('<field name="qty_m1" string="qty_m1" ','<field name="qty_m1" string="%s" ') % (qty_m1)
                res['arch'] = res['arch'].replace('<field name="qty_m2" string="qty_m2" ','<field name="qty_m2" string="%s" ') % (qty_m2)
                res['arch'] = res['arch'].replace('<field name="qty_m3" string="qty_m3" ','<field name="qty_m3" string="%s" ') % (qty_m3)
                res['arch'] = res['arch'].replace('<field name="qty_m4" string="qty_m4" ','<field name="qty_m4" string="%s" ') % (qty_m4)
                res['arch'] = res['arch'].replace('<field name="qty_m5" string="qty_m5" ','<field name="qty_m5" string="%s" ') % (qty_m5)
                res['arch'] = res['arch'].replace('<field name="qty_m6" string="qty_m6" ','<field name="qty_m6" string="%s" ') % (qty_m6)
                res['arch'] = res['arch'].replace('<field name="qty_m7" string="qty_m7" ','<field name="qty_m7" string="%s" ') % (qty_m7)
                res['arch'] = res['arch'].replace('<field name="qty_m8" string="qty_m8" ','<field name="qty_m8" string="%s" ') % (qty_m8)
                res['arch'] = res['arch'].replace('<field name="qty_m9" string="qty_m9" ','<field name="qty_m9" string="%s" ') % (qty_m9)

            print ' 514 :', view_id
            return res

    @api.multi
    def method_lt(self):
        # Reply  --回覆LT, insert iac.tvendor.upload,remark
        print '*726:' ,self.id ,',',\
            self.material_id.id ,',',self.plant_id.id,',',self.vendor_id.id,self.storage_location_id.id

        #20180706 laura add:  reply 改成 從3個表比,抓cdt最新的資料出來-----s
        # 1. 找該料 在3個表中最新的表
        self._cr.execute(
            " select  type,cdt  from ("
            "SELECT 'iac_tdelivery_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,status "
            "           from iac_tdelivery_upload Buyer"
            "         group by material_id,plant_id,vendor_id,status"
            "   union"
            "    SELECT 'iac_tdelivery_edi' as type ,max(cdt) as  Cdt ,material_id,plant_id,vendor_id,status  "
            "          from iac_tdelivery_edi EDI   "
            "         group by material_id,plant_id,vendor_id,status"
            "   union "
            "   SELECT 'iac_tvendor_upload' as type ,max(create_date) as  Cdt,material_id,plant_id,vendor_id,status "
            "          from iac_tvendor_upload Vendor  "
            "         group by material_id,plant_id,vendor_id,status"
            "   ) a "
            " where a.material_id = %s and a.plant_id = %s and vendor_id =%s and status='T' "
            "   order by Cdt desc LIMIT 1"
            , (self.material_id.id, self.plant_id.id, self.vendor_id.id))

        for item in self.env.cr.dictfetchall():
            print '*548:', item['type']

            # 2. 把最新表的data 塞入 'iac.max.cdt.upload' (先刪除,在insert)
            #  2.1.先刪除
            self._cr.execute(
                " delete from iac_max_cdt_upload where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id=%s"
                , (self.material_id.id, self.plant_id.id, self.vendor_id.id,self.storage_location_id.id))
            print '*555:', item['type']

            #  2.2. 在insert
            self._cr.execute(
                "insert into iac_max_cdt_upload (plant_id,status,material_id, source_cdt,source_table,"
                "                  shipping_date,qty,key_part,buyer_remark,buyer_id,create_date,vendor_id,"
                "                   iac_pn_vendor,reply_id,storage_location_id) "
                " select  plant_id,status, material_id,create_date as source_cdt, '"+item['type']+"' as source_table,"
                "            shipping_date,qty,key_part,buyer_remark,buyer_id,now(),vendor_id,"
                "           iac_pn_vendor,reply_id,storage_location_id "
                "  from " + item['type'] +
                " where material_id = %s and plant_id = %s and vendor_id =%s and storage_location_id = %s and status='T' " \
                , (self.material_id.id, self.plant_id.id, self.vendor_id.id,self.storage_location_id.id))
            print '*568:', item['type']
        #20180706 laura add:  reply 改成 從3個表比,抓cdt最新的資料出來-----e

        # 20180709 laura add: 帶出 iac_max_cdt_upload 的結果  ____s
        print '*740:', self.id,',',self.material_id.id,',',self.plant_id.id,',',self.vendor_id.id
        res = {
            'name': 'Max cdt confirm data form',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id(
                'iac_forecast_release_to_vendor.tconfirm_data_max_cdt_form'),
            'res_model': 'iac.tconfirm.data',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id
        }
        # 20180709 laura add: 帶出 iac_max_cdt_upload 的結果  ____e

        # 20180709 laura mark ----s
        # # 1.  需判斷登入者是buyer/vendor. 判斷法： if res_partner.Supplier = 't' then  'vendor'  else  '內部user'
        # supplier = self.env.user.partner_id.supplier
        # # print ' *208: ' , supplier ,'。',self.env.user.name,'。',self.env.user.id
        #
        # if supplier == True:
        #     # 2.1. Vendor ： 帶  tconfirm_data_vendor_open_form
        #     # vendor
        #     res = {
        #         'name': 'Vendor Confirm data open form',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'view_id': self.env['ir.model.data'].xmlid_to_res_id(
        #             'iac_forecast_release_to_vendor.tconfirm_data_vendor_open_form'),
        #         'res_model': 'iac.tconfirm.data',
        #         'domain': [],
        #         'type': 'ir.actions.act_window',
        #         'target': 'new',
        #         'res_id': self.id
        #     }
        # else:
        #     # 2.2. Buyer ： 帶  tconfirm_data_buyer_open_form
        #     # 內部user
        #     res = {
        #         'name': 'Buyer Confirm data open form',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'view_id': self.env['ir.model.data'].xmlid_to_res_id(
        #             'iac_forecast_release_to_vendor.tconfirm_data_buyer_open_form'),
        #         'res_model': 'iac.tconfirm.data',
        #         'domain': [],
        #         'type': 'ir.actions.act_window',
        #         'target': 'new',
        #         'res_id': self.id
        #     }
        # 20180709 laura mark ----e

        return res

class ConfirmDataTemp(models.Model):

    _name = 'iac.tconfirm.data.temp'
    _description = "tConfirm data temp table"
    _order = 'id desc, fpversion'

    _inherit = ['iac.tconfirm.data']



class MaxCdtUpload(models.Model):
    # 目的： iac_tdelivery_edi 、iac_tvendor_upload :、iac_tdelivery_upload   3張表中最新的
    # 20180706 laura add
    _name = 'iac.max.cdt.upload'
    _description = "max cdt upload "
    _order = 'id desc'

    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code', string="採購代碼", index=True)
    material_id = fields.Many2one('material.master', 'Material', index=True)
    material_code = fields.Char(string='Material_code', related='material_id.part_no')
    qty = fields.Integer(string='QTY')
    shipping_date = fields.Date(string="shipping date")
    buyer_remark = fields.Char(string="Remark")
    uploader = fields.Many2one('res.users', string="uploader", index=True)
    cdt = fields.Datetime(string="cdt") # cdt = fields.Date(string="cdt")
    key_part = fields.Char(string="key part")

    vendor_id = fields.Many2one('iac.vendor', string="廠商代碼",index=True)
    vendor_code = fields.Char(string="Vendor_code", related="vendor_id.vendor_code")
    iac_pn_vendor = fields.Char(string="iac_pn vendor")

    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)

    # 紀錄 "调用SAP接口"是否成功的欄位____s
    state = fields.Selection([
        ('pending', 'Pending'),  # 等待拋轉中
        ('fp error(Update)', 'FP Error(Update)'),  # 通知FP失敗 Update
        ('fp error(Delete)', 'FP Error(Delete)'),  # 通知FP失敗 Delete
        ('fp error(Insert)', 'FP Error(Insert)'),  # 通知FP失敗 Insert
        ('finished(Update)', 'Finished(Update)'),  # 更新FP成功 Update
        ('finished(Delete)', 'Finished(Delete)'),  # 更新FP成功 Delete
        ('finished(Insert)', 'Finished(Insert)')  # 更新FP成功  Insert
    ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char()
    # 紀錄 "调用SAP接口"是否成功的欄位____e

    reply_id = fields.Many2one('iac.tconfirm.data', index=True)
    group_id = fields.Many2one('iac.max.cdt.upload.group')

    source_cdt = fields.Datetime(string="source cdt")
    source_table = fields.Char(string="source table")
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

class Group_MaxCdtUpload(models.Model):
    # 建立一model  for  call API group_id用 (可整批拋,只call 一次API)
    _name = 'iac.max.cdt.upload.group'

    group_ids = fields.One2many('iac.max.cdt.upload', 'group_id')