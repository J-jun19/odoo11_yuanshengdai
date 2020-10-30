# -*- coding: utf-8 -*-
import xlrd
from odoo.modules.registry import RegistryManager
from datetime import datetime, timedelta,date
from odoo.modules.registry import RegistryManager
from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import time,base64
import datetime
import os
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError


# menu name：Buyer Upload  - Buyer Fill Form report
# description： 給buyer 用來上傳 Buyer Fill Form report,回覆delivery ( 主要更新 iac_tdelivery_upload )
# author： IAC.Laura
# create date： 2018.1
# modify date：20181019 Ning 檢查每個數字欄位 =空值or空白鍵 不寫入 , 只有float类型并且大于0的值 才寫入
# modify date：

class BuyerUploadLTBK(models.TransientModel):
    # buyer 上傳LT的程式。選擇上傳檔案路徑的 wizard table
    _name = 'iac.buyer.upload.lt.wizard.bk'
    file_name = fields.Char(u'File Name')
    file = fields.Binary(u'File')

    @api.multi
    def action_confirm_buyer_upload_lt(self):
        # 讀 buyer upload LT 的報表
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # fields.Char(string="今天日期",
        print '*33:', today_str
        # 讀 buyer upload LT 的報表
        excel_obj = open_workbook(file_contents=base64.decodestring(self.file))
        sheet_obj = excel_obj.sheet_by_index(0)
        login_id = self.env.user.id
        #today = fields.Datetime.now() # 当前时间字符串  #print '*25:', fields.Datetime.now()
        #login_id = self.env.user.id
        # print '*26:', today,'。',login_id
        # 1. 匯入前先檢查匯入的報表格式是否正確：檢查 A1='BuyerName' , FC3='Version ID'
        if sheet_obj.cell(0, 0).value <> u'採購代碼' or sheet_obj.cell(0, 107).value <> u'上傳帳號':
            # print '*24:',sheet_obj.cell(0, 0).value,'。',sheet_obj.cell(2, 158).value
            raise exceptions.ValidationError("匯入檔案錯誤!")  # return self.env['warning_box'].info(title='Error', message='匯入檔案錯誤!')

        #buyer_all = [] # for mail用
        error_str = ''
        error_num = ''
        error_num2 = ''
        error_num3 = ''
        error_num4 = ''
        error_num5 = ''
        error_num6 = ''
        error_num7 = ''
        error_num8 = ''
        error_num9 = ''
        error_count = 0

        # 先判斷 excel cell的格式 是 date 還是 text
        w1_r_start_type = str(sheet_obj.cell(2,11)).split(':')[0]

        # print '*48:', w1_r_start_type ,',',sheet_obj.cell(2,11)

        if w1_r_start_type == 'xldate':
            w1_r_start = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(2, 11).value, 0)
        else: # text
            w1_r_start = sheet_obj.cell(2, 11).value
        # print '*43:', w1_r_start_type ,'。',w1_r_start

        # 讀取AG~FB欄 所有日期,並寫入array裡
        header_date = []

        for i in range(11, 106)  :
            type = ''
            title = ''

            type = str(sheet_obj.cell(2, i)).split(':')[0] #先判斷 excel cell的格式 是 date 還是 text
            if type=='xldate':
                title = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(2, i).value, 0)
            else:
                title = sheet_obj.cell(2, i).value
            header_date.append(title)
        # print '*69:', i ,'。', title ,'。',header_date

        val = {}
        group = self.env['iac.tdelivery.upload.group'].create(val)
        group.env.cr.commit()
        # print '*70:', group, ',', group.id, ',', val
        t_data_1 = False
        t_data_2 = False
        t_data_3 = False
        vendor_list = []
        material_list = []
        storage_location_list = []
        for rx in range(sheet_obj.nrows):

            if rx >= 3 and sheet_obj.cell(rx, 0).value:
                is_exist = 0
                if rx == 3:
                    vendor_list.append(sheet_obj.cell(rx, 8).value)
                    material_list.append(sheet_obj.cell(rx, 2).value)
                    storage_location_list.append(sheet_obj.cell(rx, 109).value)
                else:
                    for i in range(len(vendor_list)):
                        if sheet_obj.cell(rx,8).value == vendor_list[i] \
                                and sheet_obj.cell(rx,2).value == material_list[i]\
                                and sheet_obj.cell(rx,109).value == storage_location_list[i]:
                            is_exist = 1
                            first_exist = i
                            error_num8 = error_num8 + str(rx + 1) + ' , '
                            error_count = 1
                            # raise exceptions.ValidationError("料號+廠商代碼  不可重複!")
                    if is_exist == 0:
                        vendor_list.append(sheet_obj.cell(rx, 8).value)
                        material_list.append(sheet_obj.cell(rx, 2).value)
                        storage_location_list.append(sheet_obj.cell(rx, 109).value)
                is_remark_list = []
                is_remark_list1 = []

                #181212 ning add 检查plant和location是否存在
                if not self.env['iac.storage.location.address'].search([('plant','=',sheet_obj.cell(rx,108).value.upper()),('storage_location','=',sheet_obj.cell(rx,109).value.upper())]):
                    storage_location_id = ''
                    error_num9 = error_num9 + str(rx + 1) + ' , '
                    error_count = 1
                else:
                    storage_location_id = self.env['iac.storage.location.address'].search(
                        [('plant', '=', sheet_obj.cell(rx, 108).value.upper()),
                         ('storage_location', '=', sheet_obj.cell(rx, 109).value.upper())]).id
                # version_id = str(int(sheet_obj.cell(rx, 158).value))
                if sheet_obj.cell(rx, 2).value == '':
                    material_code = ''
                else:
                    material_code = str(sheet_obj.cell(rx, 2).value)
                if sheet_obj.cell(rx, 8).value == '':
                    vendor_code = ''
                    iac_pn_vendor = ''

                    # raise exceptions.ValidationError("Vendor Code(廠商代碼) 不可空白!")
                else:
                    vendor_code = str(int(sheet_obj.cell(rx, 8).value)).zfill(10)  # 補 0
                    iac_pn_vendor = str(sheet_obj.cell(rx, 2).value) + str(int(sheet_obj.cell(rx, 8).value))
                if sheet_obj.cell(rx, 0).value == '':
                    buyer_code = ''
                else:
                    buyer_code = str(int(sheet_obj.cell(rx, 0).value))  # A  0
                if sheet_obj.cell(rx,3).value =='' or (str(sheet_obj.cell(rx,3).value).upper() != 'Y' and str(sheet_obj.cell(rx,3).value).upper() !='N'):
                    error_num4 = error_num4 + str(rx + 1) + ' , '
                    error_count = 1
                    key_part=''
                    # raise exceptions.ValidationError("Key Part 欄位必需為'Y'或'N' !")
                else:
                    key_part = str(sheet_obj.cell(rx, 3).value).upper()# C  2

                for i in range(11,106):
                    if sheet_obj.cell(rx, i).value !='' and sheet_obj.cell(rx,i).value !=0:
                        is_remark_list.append(sheet_obj.cell(rx,i).value)

                for i in range(11,106):
                    if sheet_obj.cell(rx, i).value !='':
                        is_remark_list1.append(sheet_obj.cell(rx,i).value)

                vendor_remark = sheet_obj.cell(rx, 10).value  # AF
                buyer_list = []
                if self.env.user.login <> 'admin':
                    buyer_id = self.env['buyer.code'].search([('buyer_erp_id', '=', buyer_code)]).id
                    for item in self.env.user.buyer_id_list:
                        # print item
                        buyer_list.append(item)

                    if buyer_id not in buyer_list:
                        error_num3 = error_num3 + str(rx + 1) + ','
                        error_count = 1
                        # raise exceptions.ValidationError("Buyer Code 不正確!")
                # 2.1. 逐筆讀資料：如果Version ID or vendor_code or material 任一欄是空,就報錯&跳過
                if len(buyer_code) == 0 or len(vendor_code) == 0 or len(material_code) == 0:
                    error_num = error_num + str(rx + 1) + ' , '
                    error_count = 1

                # 2.2. 逐筆讀資料：用VersionID+vendor+material 去檢查 iac_tconfirm_data 是否存在
                tconfirm_export = self.env['iac.tconfirm.data'].sudo().search([
                    ('vendor_code', '=', vendor_code), ('material_code', '=', material_code),
                    ('buyer_code', '=', buyer_code), ('storage_location_id','=',storage_location_id),('status', '=', 'T')])
                buyer_id = tconfirm_export.buyer_id
                plant_id = tconfirm_export.plant_id
                material_id = tconfirm_export.material_id
                vendor_id = tconfirm_export.vendor_id
                id = tconfirm_export.id

                if not tconfirm_export:
                    # print '*100:', rx, '。', vendor_code, '。', version_id, '。', material_code
                    error_num2 = error_num2 + str(rx+1) +' , '
                    error_count =  1

                if key_part.upper() == 'Y':
                    if len(is_remark_list)==0:
                        if sheet_obj.cell(rx,10).value=='':
                            error_num5 = error_num5 + str(rx + 1) + ' , '
                            error_count =  1
                if key_part.upper()=='N':
                    if len(is_remark_list1) != 0:
                        error_num7 = error_num7 + str(rx + 1) + ' , '
                        error_count = error_count + 1
                        # raise exceptions.ValidationError("Key Part 欄位為 'N'，56天交期不允許有數量!")
                    if sheet_obj.cell(rx,10).value=='':
                        error_num6 = error_num6 + str(rx + 1) + ' , '
                        error_count =  1
                        # raise exceptions.ValidationError("Key Part 欄位為 'N'，[Remark] 欄位不可空白 !")

        if error_num9 <> '':
            error_str = ' 第' + error_num9 + '行錯誤，Location不存在。'+'\n'+'Please check Row#'+error_num9+'Location does not exist.' +'\n'+ error_str

        if error_num8 <> '':
            # print vendor_list,material_list
            error_str = ' 第' + str(first_exist+4)+','+ error_num8 + '行錯誤，料號 (IAC Part No.)+廠商代碼(Vendor Code) 不可重複!'+'\n'+'Please check Row#'+str(first_exist+4)+','+ error_num8+'[IAC Part No.] and [Vendor Code] has duplicate value.'
        if error_num2 <> '':
            # print '*66:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num2 + '行錯誤，此筆FCST錯誤(找不到對應的iac_tconfirm_data)。'+'\n'+'Please check Row#'+error_num2+'FCST record missed (Cannot find corresponding iac_tconfirm_data).'

        if error_num <> '':
            error_str = ' 第' + error_num + '行錯誤，沒有基本資料(buyer,vendor,material)。'+'\n'+'Please check Row#'+error_num+'Basic data missed (buyer, vendor, material).' +'\n'+ error_str

        if error_num3 <> '':
            error_str = ' 第' + error_num3 + '行錯誤，Buyer Code 不正確!'+'\n'+'Please check Row#'+error_num3+'Incorrect Buyer Code.'

        if error_num4 <> '':
            error_str = ' 第' + error_num4 + '行錯誤，Key Part 欄位必需為Y或N !'+'\n'+'Please check Row#'+error_num4+'You have to enter either "Y" or "N" in [Key Part].'
        if error_num5 <> '':
            error_str = ' 第' + error_num5 + '行錯誤，56天交期為空或0時，[Remark] 欄位不可空白 !'+'\n'+'Please check Row#'+error_num5+'[Remark] is required when all the shipping quantity is blank or equals to 0.'

        if error_num6 <> '':
            error_str = ' 第' + error_num6 + '行錯誤，Key Part 欄位為 N，[Remark] 欄位不可空白 !'+'\n'+'Please check Row#'+error_num6+'[Remark] is required when [Key Part] is "N".'

        if error_num7 <> '':
            error_str = ' 第' + error_num7 + '行錯誤，Key Part 欄位為 N，56天交期不允許有數量!'+'\n'+'Please check Row#'+error_num7+'Remove all shipping quantity and leave it blank when [Key Part] is "N".'

        for rx in range(sheet_obj.nrows):  # range(0, 6):    temp  for test 先讀到第6行
            #print sheet_obj.nrows
            # 2. 逐筆讀資料
            if rx >= 3 and error_count==0 and sheet_obj.cell(rx, 0).value: # 從第4行開始讀

                #print vendor_code,material_code,buyer_code
                # print '*81:',vendor_code,'。',material_code,'。',vendor_code,'。',buyer_code,'。',key_part,'。',vendor_remark
                is_remark_list1 = []
                material_code = str(sheet_obj.cell(rx, 2).value)

                vendor_code = str(int(sheet_obj.cell(rx, 8).value)).zfill(10)  # 補 0
                iac_pn_vendor = str(sheet_obj.cell(rx, 2).value) + str(int(sheet_obj.cell(rx, 8).value))

                buyer_code = str(int(sheet_obj.cell(rx, 0).value))  # A  0

                key_part = str(sheet_obj.cell(rx, 3).value).upper()  # C  2
                storage_location_id = self.env['iac.storage.location.address'].search(
                    [('plant', '=', sheet_obj.cell(rx, 108).value.upper()),
                     ('storage_location', '=', sheet_obj.cell(rx, 109).value.upper())]).id



                for i in range(11, 106):
                    if sheet_obj.cell(rx, i).value != '':
                        is_remark_list1.append(sheet_obj.cell(rx, i).value)

                vendor_remark = sheet_obj.cell(rx, 10).value  # AF
                # 2.2. 逐筆讀資料：用VersionID+vendor+material 去檢查 iac_tconfirm_data 是否存在
                tconfirm_export = self.env['iac.tconfirm.data'].sudo().search([
                    ('vendor_code', '=', vendor_code), ('material_code', '=', material_code),
                    ('buyer_code', '=', buyer_code), ('storage_location_id','=',storage_location_id),('status', '=', 'T')])
                buyer_id = tconfirm_export.buyer_id
                plant_id = tconfirm_export.plant_id
                material_id = tconfirm_export.material_id
                vendor_id = tconfirm_export.vendor_id
                id = tconfirm_export.id
                storage_location_id = tconfirm_export.storage_location_id

                # print '*97:',rx ,'。',vendor_code,'。',version_id,'。', material_code

                if key_part.upper()=='N' and error_count==0:

                    shipping_date = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(2, 11).value, 0)
                    # shipping_date = datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]))
                    uid = self._uid
                    self._cr.execute("update iac_tdelivery_upload set status='F' "
                                     "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and  storage_location_id = %s",
                                     (plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))
                    ins_vendor_upload_val = {
                        'status': 'T',  # T: true有效
                        'plant_id': plant_id.id,
                        'buyer_id': buyer_id.id,
                        'material_id': material_id.id,
                        'vendor_id': vendor_id.id,
                        'key_part': key_part,
                        'iac_pn_vendor': iac_pn_vendor,
                        'qty': 0,
                        'shipping_date': shipping_date,
                        'buyer_remark': vendor_remark,
                        'write_date':today_str, #20180803 laura add
                        'write_uid':uid,
                        'create_uid':uid,
                        'reply_id': id,
                        'storage_location_id':storage_location_id.id
                    }
                    print '*194:', ins_vendor_upload_val
                    # print self
                    t_data_1 = self.env['iac.tdelivery.upload'].sudo().create(ins_vendor_upload_val)

                    t_data_1.env.cr.commit()
                    # print t_data.id
                    vals = {}
                    vals['group_id'] = group.id
                    vals['write_date'] = today_str # 20180803 laura add

                    # print '*181:', vals
                    t_data_1.write(vals)
                    self._cr.execute("update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s ,write_date=%s"  #20180803 laura add
                                     "where id = %s",
                                     (uid, uid, today_str,t_data_1.id))
                    t_data_1.env.cr.commit()

                if key_part.upper() == 'Y' and error_count==0 and len(is_remark_list1)==0:
                    # print sheet_obj.cell(2, 11).value
                    # shipping_date = xlrd.xldate.xldate_as_datetime(today_str, 0)
                    # shipping_date = datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]))
                    uid = self._uid
                    self._cr.execute("update iac_tdelivery_upload set status='F' "
                                     "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id = %s ",
                                     (plant_id.id, material_id.id, vendor_id.id, storage_location_id.id))
                    ins_vendor_upload_val = {
                        'status': 'T',  # T: true有效
                        'plant_id': plant_id.id,
                        'buyer_id': buyer_id.id,
                        'material_id': material_id.id,
                        'vendor_id': vendor_id.id,
                        'key_part': key_part,
                        'iac_pn_vendor': iac_pn_vendor,
                        'qty': 0,
                        'shipping_date': today_str,
                        'buyer_remark': vendor_remark,
                        'write_date': today_str,  # 20180803 laura add
                        'write_uid': uid,
                        'create_uid': uid,
                        'reply_id': id,
                        'storage_location_id':storage_location_id.id
                    }
                    print '*194:', ins_vendor_upload_val
                    t_data_2 = self.env['iac.tdelivery.upload'].sudo().create(ins_vendor_upload_val)
                    t_data_2.env.cr.commit()
                    # print t_data.id
                    vals = {}
                    vals['group_id'] = group.id
                    vals['write_date'] = today_str # 20180803 laura add
                    # print '*181:', vals
                    t_data_2.write(vals)
                    self._cr.execute("update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s , write_date=%s "  # 20180803 laura add
                                     "where id = %s",
                                     (uid, uid,today_str, t_data_2.id))
                    t_data_2.env.cr.commit()


                # 2.3. 檢查都沒錯,再開始逐筆 insert：1. iac_tvendor_remark
                if error_count == 0 and vendor_remark <> '':
                    # 2.3.1. 先  iac_tvendor_remark where 有相同 plant,vendor,material 的改為 F:  false 無效
                    self._cr.execute("update iac_tvendor_remark  set status='F' "
                                     "where  status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id=%s",
                                     (plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

                    # 2.3.2. 再 insert into iac_tvendor_remark
                    ins_vendor_remark_val = {
                        'status': 'T', # T: true有效
                        'plant_id': plant_id.id,
                        'buyer_id': buyer_id.id,
                        'material_id': material_id.id,
                        'vendor_id': vendor_id.id,
                        'vendor_remark': vendor_remark,
                        'iac_pn_vendor': iac_pn_vendor,
                        'storage_location_id': storage_location_id.id,
                        'basicdate': w1_r_start  #,
                        # 'cdt': time.localtime(time.time())
                    }
                    # print '*91:',time.localtime(time.time())

                    self.env['iac.tvendor.remark'].sudo().create(ins_vendor_remark_val)
                    self.env.cr.commit()

                    # raise exceptions.ValidationError(' insert：1. iac_tvendor_remark !')

                # 2.5. 檢查都沒錯,再開始逐筆 insert：2. iac_tdelivery_upload
                if error_count == 0: #沒錯誤再寫入
                    sum = 0
                    for j in range(11, 106):
                        # print sheet_obj.cell(rx,j).value.isspace(),'1'
                        # print isinstance(sheet_obj.cell(rx, j).value,(float))
                        if sheet_obj.cell(rx, j).value and sheet_obj.cell(rx, j).value >= 0 and isinstance(sheet_obj.cell(rx, j).value,(float)):
                            sum = sheet_obj.cell(rx, j).value + sum
                    # print '*138: ' ,rx ,'。', sum

                    # 2.5.1.該欄(vendor+material)的demand_qty 總和>=1,就把 iac_tvendor_upload 有相同 plant,vendor,material 的改為 F:  false 無效
                    if sum >= 0:
                        # 紀錄  匯入且資料正確的 all buyer (for mail準備)
                        #buyer_all.append(buyer_id.id)  # for mail用

                        self._cr.execute("update iac_tdelivery_upload set status='F' "
                                         "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id=%s",
                                         (plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

                        tdelivery = self.env['iac.tdelivery.upload'].sudo().search([
                            ('status', '=', 'T'), ('plant_id', '=', plant_id.id), ('material_id', '=', material_id.id),
                            ('vendor_id', '=', vendor_id.id),('storage_location_id','=',storage_location_id.id)])
                        # tdelivery.id  # 本次 insert 資料的這筆 id

                    for i in range(11, 106):
                        # print sheet_obj.cell(rx,i).value
                        if sheet_obj.cell(rx, i).value >= 0 and sheet_obj.cell(rx, i).value !='' and isinstance(sheet_obj.cell(rx, i).value,(float)):
                            demand_qty = 0
                            demand_qty = int(sheet_obj.cell(rx, i).value)  # 每欄位的需求
                            demand_date = header_date[i-11]
                            # 2.5.2. 再 insert into iac_tdelivery_upload
                            uid = self._uid
                            ins_vendor_upload_val = {
                                'status': 'T',  # T: true有效
                                'plant_id': plant_id.id,
                                'buyer_id': buyer_id.id,
                                'material_id': material_id.id,
                                'vendor_id': vendor_id.id,
                                'key_part': key_part,
                                'iac_pn_vendor': iac_pn_vendor,
                                'qty':demand_qty,
                                'shipping_date':demand_date,
                                'buyer_remark': vendor_remark,
                                'write_date': today_str,  # 20180803 laura add
                                'create_uid':uid,
                                'write_uid':uid,
                                'reply_id': id,
                                'storage_location_id':storage_location_id.id
                            }
                            print '*401:', ins_vendor_upload_val
                            t_data_3 = self.env['iac.tdelivery.upload'].sudo().create(ins_vendor_upload_val)
                            t_data_3.env.cr.commit()
                            # print t_data.id

                            # t_data.id  # 本次 insert 資料的這筆 id
                            vals = {}
                            vals['group_id'] = group.id
                            vals['write_date'] = today_str # 20180803 laura add

                            print '*414:', vals
                            t_data_3.write(vals)
                            self._cr.execute("update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s  ,write_date= %s " # 20180803 laura add
                                             "where id = %s",
                                             (uid, uid, today_str,t_data_3.id))
                            t_data_3.env.cr.commit()
                            print '*184:', group.id
                if error_count == 0:
                    self._cr.execute("update iac_tconfirm_data set buyer_remark=%s,key_part=%s "
                                     "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id=%s",
                                     (vendor_remark,key_part,plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

        val = {}
        t_all = self.env['iac.tdelivery.upload'].sudo().search([('group_id', '=', group.id)])

        # call 接口 ----s
        if error_count==0:
            # 调用SAP接口執行更新FP数据的 SP :  1. 先 delete 資料 ODOO_FP_007 ___s
            print '* 321 :  buyer_upload_lt.py  開始調用SAP接口'
            print '*320 : ',  self.id, ',', group.id
            biz_object = {
                "id": group.id,
                "biz_object_id": group.id  #,
                # "sql_type": "D"  # I : insert , U : update , D: delete
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_007", biz_object)
            if rpc_result:
                print '*209 : state :  finished(Delete)', ',', self.id, ',', group.id
                # 调用SAP接口 成功的情况下,修改记录状态
                # val['state'] = 'finished(Delete)'
                # val['state_msg'] = ''
                self._cr.execute("update iac_tdelivery_upload  set create_uid = %s "
                                 ",write_uid= %s,state=%s,state_msg=%s ,write_date=%s"
                                 "where group_id = %s",
                                 (login_id, login_id,'finished(Delete)','' ,today_str, group.id))
            else:
                print '*446 : state :  fp error(Delete)', ',', self.id, ',', group.id
                # t_data.write({'state': 'fp error(Delete)', 'state_msg': u'拋轉FP失败(Delete)'})
                # val['state'] = "fp error(Delete)"
                # val['state_msg'] = u'拋轉FP失败(Delete)'
                self._cr.execute(
                    "update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s,state=%s,"
                    "state_msg=%s,write_date= %s"  # 20180803 laura add
                    "where group_id = %s",
                    (login_id, login_id, 'fp error(Delete)', '拋轉FP失败(Delete)', today_str, group.id))
            # t_all.write(val)

            print '*461:   buyer_upload_lt.py 結束 調用SAP接口 '
            # 调用SAP接口執行更新FP数据的 SP :  1. 先 delete 資料 ODOO_FP_007 ___e

            # 调用SAP接口執行更新FP数据的 SP :   2. insert 資料 ODOO_FP_005___s
            print '* 465 :  buyer_upload_lt.py  開始調用SAP接口'
            biz_object = {
                "id": group.id,
                "biz_object_id": group.id,
                "sql_type": "I"  # I : insert , U : update
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_005", biz_object)
            if rpc_result:
                print '*474 : state :  finished(Insert)',',',self.id,',',group.id
                # 调用SAP接口 成功的情况下,修改记录状态
                # val['state'] = "finished(Insert)"
                # val['state_msg'] = ''
                self._cr.execute(
                    "update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s,state=%s,"
                    "state_msg=%s ,write_date=%s"  # 20180803 laura add            
                    "where group_id = %s",
                    (login_id, login_id, 'finished(Insert)', '',today_str, group.id))
            else:
                print '*480 : state :  fp error(Insert)',',',self.id,',',group.id
                # val['state'] = "fp error(Insert)"
                # val['state_msg'] = u'拋轉FP失败(Insert)'
                self._cr.execute(
                    "update iac_tdelivery_upload  set create_uid = %s ,write_uid= %s,state=%s,"
                    "state_msg=%s ,write_date =%s"  # 20180803 laura add
                    "where group_id = %s",
                    (login_id, login_id, 'fp error(Insert)', '拋轉FP失败(Insert)', today_str,group.id))
            # t_all.write(val)

            print '*234:   vendor_upload_lt.py 結束 調用SAP接口 '
            # 调用SAP接口執行更新FP数据的 SP :   2. insert 資料 ODOO_FP_005___e
        # call 接口 ----e

        if error_str <> '':
            raise exceptions.ValidationError(error_str)
        else:

            raise exceptions.ValidationError('上傳成功')