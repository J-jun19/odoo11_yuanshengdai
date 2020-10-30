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

# menu name：Vendor Upload  - Vendor Fill Form report
# description： 給 Vendor用來上傳 Vendor Fill Form report,回覆delivery ( 主要更新 iac_tvendor_upload )
# author： IAC.Laura
# create date： 2018.1
# modify date：20181019 Ning 檢查每個數字欄位 =空值or空白鍵 不寫入 , 只有float类型并且大于0的值 才寫入
# modify date：

class VendorUploadLT(models.TransientModel):
    # vendor 上傳LT的程式。選擇上傳檔案路徑的 wizard table
    _name = 'iac.vendor.upload.lt.wizard'
    file_name = fields.Char(u'File Name')
    file = fields.Binary(u'File')

    def send_to_email(self, object_id=None,template_name=None):
        template = self.env.ref(template_name)
        return template.send_mail(object_id,force_send=True)

    def get_local_cr(self):
        db_name = self.env.registry.db_name
        registry = RegistryManager.get(db_name)
        cr = registry.cursor()
        return cr

    @api.multi
    def action_confirm(self):
        # 只能在 8:00 ~ 22:00 間做上传操作
        now_date = datetime.datetime.strptime(datetime.datetime.now().strftime('%H:%M:%S'), '%H:%M:%S')
        begin_date = datetime.datetime.strptime('8:00:00', '%H:%M:%S')
        end_date = datetime.datetime.strptime('22:00:00', '%H:%M:%S')
        if now_date < begin_date or now_date > end_date:
            raise UserError('Please update supply plan from 8:00 to 22:00!')
        # Vendor Upload
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
        print '*40'
        # 讀 vendor upload LT 的報表
        excel_obj = open_workbook(file_contents=base64.decodestring(self.file))
        sheet_obj = excel_obj.sheet_by_index(0)
        today = fields.Datetime.now() # 当前时间字符串  #print '*25:', fields.Datetime.now()
        login_id = self.env.user.id
        # print '*26:', today,'。',login_id

        # 1. 匯入前先檢查匯入的報表格式是否正確：檢查 A1='BuyerName' , FC3='Version ID'
        # 先抓取配置表里第一个字段和最后一个字段，以及最后一个字段的列号
        first_title = self.env['iac.vendor.fcst.setting'].search([], order='column_begin', limit=1).title
        end_field = self.env['iac.vendor.fcst.setting'].search([], order='column_end desc', limit=1)
        end_title = end_field.title
        end_column = end_field.column_end
        if sheet_obj.cell(0, 0).value <> first_title or sheet_obj.cell(0, end_column).value <> end_title:
            # print '*31:',sheet_obj.cell(0, 0).value,'。',sheet_obj.cell(0, 158).value
            raise exceptions.ValidationError("匯入檔案錯誤!")  # return self.env['warning_box'].info(title='Error', message='匯入檔案錯誤!')

        buyer_all = [] # for mail用
        new_buyer_all = []
        new_part_ids = []
        email = []
        buyer_email_now = []
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
        error_count=0
        delta_list = [] #用来存放所有的delta字段的列号
        # 抓取日期字段的起始列
        date_begin_column = self.env['iac.vendor.fcst.setting'].search([('interval', '!=', 0)], order='column_begin',
                                                                      limit=1).column_begin
        #抓取从两周前开始的日期字段的起始列和结束列
        date_restart_begin_column = self.env['iac.vendor.fcst.setting'].search([('restart_flag', '=', 't')], order='column_begin',
                                                                    limit=1).column_begin
        date_restart_end_column = self.env['iac.vendor.fcst.setting'].search([('restart_flag', '=', 't')],
                                                                               order='column_end desc',
                                                                               limit=1).column_end
        for delta in self.env['iac.vendor.fcst.setting'].search([('delta_flag', '=', 't')]):
            delta_list.append(delta.column_begin)
        # 先判斷 excel cell的格式 是 date 還是 text
        w1_r_start_type = str(sheet_obj.cell(1,date_begin_column)).split(':')[0]

        if w1_r_start_type=='xldate':
            w1_r_start = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(1, date_begin_column).value, 0)
        else: # text
            w1_r_start = sheet_obj.cell(1, date_begin_column).value
        # print '*43:', w1_r_start_type ,'。',w1_r_start

        # 讀取AG~FB欄 所有日期,並寫入array裡
        header_date = []

        for i in range(date_restart_begin_column, date_restart_end_column):
            type = ''
            title = ''

            if i in delta_list: # 這幾欄不讀
                title=''
            else:

                type = str(sheet_obj.cell(1, i)).split(':')[0] #先判斷 excel cell的格式 是 date 還是 text
                if type=='xldate':
                    title = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(1, i).value, 0)
                    # print '*61:', i,'。', title ,'。',type
                else:
                    title = sheet_obj.cell(1, i).value
                    # print '*64:', i, '。', title,'。',type
            header_date.append(title)

        # print '*69:', i ,'。', title ,'。',header_date

        val = {}
        group = self.env['iac.tvendor.upload.group'].create(val)
        group.env.cr.commit()
        print '*100:',group,',',group.id,',',val
        t_data1 = False
        t_data2 = False
        t_data3 = False
        vendor_list = []
        material_list = []
        storage_location_list = []
        vendor_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Vendor Code',
                                                                                                   'iac.vendor.fcst.setting')
        material_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('IAC Part No.',
                                                                                                     'iac.vendor.fcst.setting')
        location_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Location',
                                                                                                     'iac.vendor.fcst.setting')
        plant_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Plant',
                                                                                                  'iac.vendor.fcst.setting')
        buyer_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('BuyerCode',
                                                                                                  'iac.vendor.fcst.setting')
        key_part_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Key Part',
                                                                                                     'iac.vendor.fcst.setting')
        remark_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Remark',
                                                                                                   'iac.vendor.fcst.setting')
        version_column = self.env['iac.buyer.fcst.delivery.report.wizard'].get_begin_column_by_name('Version ID',
                                                                                                   'iac.vendor.fcst.setting')
        for rx in range(sheet_obj.nrows):
            # print sheet_obj.nrows
            # print sheet_obj.cell(rx, 0).value
            if rx >= 3 and sheet_obj.cell(rx, 0).value:
                is_exist = 0
                if rx == 3:
                    vendor_list.append(sheet_obj.cell(rx, vendor_column).value)
                    material_list.append(sheet_obj.cell(rx, material_column).value)
                    storage_location_list.append(sheet_obj.cell(rx,location_column).value)
                else:
                    for i in range(len(vendor_list)):
                        if sheet_obj.cell(rx, vendor_column).value == vendor_list[i] \
                                and sheet_obj.cell(rx, material_column).value == material_list[i]\
                                and sheet_obj.cell(rx,location_column).value == storage_location_list[i]:
                            is_exist = 1
                            first_exist = i
                            error_num8 = error_num8 + str(rx + 1) + ' , '
                            error_count = 1
                            # raise exceptions.ValidationError("料號+廠商代碼  不可重複!")

                    if is_exist == 0:
                        vendor_list.append(sheet_obj.cell(rx, vendor_column).value)
                        material_list.append(sheet_obj.cell(rx, material_column).value)
                        storage_location_list.append(sheet_obj.cell(rx, location_column).value)
                is_remark_list = []
                is_remark_list1 = []
                qty_sum =0
                vendor_code_list = []

                if sheet_obj.cell(rx,version_column).value == '':
                    version_id = ''
                else:
                    version_id = str(sheet_obj.cell(rx, version_column).value)  # version_id = str(int(sheet_obj.cell(rx, 158).value))
                # print '*75:', rx, '。', version_id
                # vendor_name = str(str(sheet_obj.cell(rx, 160).value))

                # 181212 ning add 检查plant和location是否存在
                if not self.env['iac.storage.location.address'].search(
                        [('plant', '=', sheet_obj.cell(rx, plant_column).value.upper()),
                         ('storage_location', '=', sheet_obj.cell(rx, location_column).value.upper())]):
                    storage_location_id = ''
                    error_num9 = error_num9 + str(rx + 1) + ' , '
                    error_count = 1
                else:
                    storage_location_id = self.env['iac.storage.location.address'].search(
                        [('plant', '=', sheet_obj.cell(rx, plant_column).value.upper()),
                         ('storage_location', '=', sheet_obj.cell(rx, location_column).value.upper())]).id

                if sheet_obj.cell(rx,material_column).value == '':
                    material_code = ''
                else:
                    material_code = str(sheet_obj.cell(rx, material_column).value)
                if sheet_obj.cell(rx, vendor_column).value == '':
                    vendor_code = ''
                    iac_pn_vendor = ''
                else:

                    vendor_code = str(int(sheet_obj.cell(rx, vendor_column).value)).zfill(10)  # 補 0   #str(int(sheet_obj.cell(rx, 159).value))
                    iac_pn_vendor = str(sheet_obj.cell(rx, material_column).value) + str(sheet_obj.cell(rx, vendor_column).value)
                    login = self.env.user.login
                    user_id = self.env['res.users'].search([('login', '=', login)]).id
                    # print user_id

                    #檢查 匯入的vendor_code 是否是該login ---  Ning add ----s
                    print '*146:', error_count ,',',self.env.user.login
                    if self.env.user.login <> 'admin' :
                        print '*148:' ,error_count
                        for item in self.env['iac.vendor'].search([('user_id', '=', user_id)]):
                            if item.vendor_code:
                                vendor_code_list.append(item.vendor_code)
                        if vendor_code not in vendor_code_list:
                            error_num3 = error_num3 + str(rx + 1) + ','
                            error_count = 1

                    # 檢查 匯入的vendor_code 是否是該login ---  Ning add ----e

                # print '*79:', rx,'。', vendor_code,'。',sheet_obj.cell(rx, 159).value
                buyer_code = str(sheet_obj.cell(rx, buyer_column).value)  # str(int(sheet_obj.cell(rx, 0).value[:3])) # A  0
                if sheet_obj.cell(rx, key_part_column).value == '' or (str(sheet_obj.cell(rx, key_part_column).value).upper() != 'Y' and str(
                        sheet_obj.cell(rx, key_part_column).value).upper() != 'N'):
                    error_num4 = error_num4 + str(rx + 1) + ' , '
                    error_count =  1
                    key_part = ''
                    # raise exceptions.ValidationError("Key Part 欄位必需為'Y'或'N' !")
                else:
                    key_part = str(sheet_obj.cell(rx, key_part_column).value).upper()  # C  2

                for i in range(date_restart_begin_column, date_restart_end_column):
                    if i in delta_list:
                        # print i
                        continue
                    else:
                        # print i
                        if sheet_obj.cell(rx, i).value != '' and sheet_obj.cell(rx, i).value != 0:
                            is_remark_list.append(sheet_obj.cell(rx, i).value)

                for i in range(date_restart_begin_column, date_restart_end_column):
                    if i in delta_list:
                        continue
                    else:
                        print sheet_obj.cell(rx,i).value
                        if sheet_obj.cell(rx, i).value != '':
                            is_remark_list1.append(sheet_obj.cell(rx, i).value)
                            qty_sum =qty_sum +sheet_obj.cell(rx, i).value
                # print '*81:', rx, '。', buyer_code
                # key_part = str(sheet_obj.cell(rx, 2).value)# C  2
                vendor_remark = sheet_obj.cell(rx, remark_column).value  # AF
                # 2.1. 逐筆讀資料：如果Version ID or vendor_code or material 任一欄是空,就報錯&跳過
                if len(version_id) == 0 or len(vendor_code) == 0 or len(material_code) == 0:
                    error_num = error_num + str(rx + 1) + ' , '
                    error_count = 1
                # 2.2. 逐筆讀資料：用VersionID+vendor+material 去檢查 iac_tconfirm_data 是否存在
                tconfirm_export = self.env['iac.tconfirm.data'].sudo().search([
                    ('vendor_code', '=', vendor_code), ('material_code', '=', material_code),
                    ('version', '=', version_id),('storage_location_id','=',storage_location_id), ('status', '=', 'T')])
                print '*195:',vendor_code ,',',material_code ,',', version_id
                buyer_id = tconfirm_export.buyer_id
                plant_id = tconfirm_export.plant_id
                material_id = tconfirm_export.material_id
                vendor_id = tconfirm_export.vendor_id
                tconfirm_id = tconfirm_export.id

                if not tconfirm_export:
                    # print '*100:', rx, '。', vendor_code, '。', version_id, '。', material_code
                    error_num2 = error_num2 + str(rx+1) +' , '
                    error_count = 1
                if key_part.upper() == 'Y':
                    if len(is_remark_list)==0:
                        if sheet_obj.cell(rx,remark_column).value=='':
                            error_num5 = error_num5 + str(rx + 1) + ' , '
                            error_count =  1

                if key_part.upper()=='N':
                    # if len(is_remark_list1) != 0:
                    if qty_sum > 0:
                        error_num7 = error_num7 + str(rx + 1) + ' , '
                        error_count =  1
                        # raise exceptions.ValidationError("Key Part 欄位為 'N'，56天交期不允許有數量!")
                    if sheet_obj.cell(rx,remark_column).value=='':
                        error_num6 = error_num6 + str(rx + 1) + ' , '
                        error_count =  1
                        # raise exceptions.ValidationError("Key Part 欄位為 'N'，[Remark] 欄位不可空白 !")

        if error_num9 <> '':
            error_str = ' 第' + error_num9 + '行錯誤，Location不存在。'+'\n'+'Please check Row#'+error_num9+'Location does not exist.' +'\n'+ error_str

        if error_num8 <> '':
            # print vendor_list,material_list
            error_str = ' 第' + str(first_exist+4)+','+ error_num8 + '行錯誤，料號 (IAC Part No.)+廠商代碼(Vendor Code) 不可重複!'+'\n'+'Please check Row#'+str(first_exist+4)+','+ error_num8+'[IAC Part No.] and [Vendor Code] has duplicate value.'
        if error_num2 <> '':
            # print '*238:', vendor_code, ',', material_code, ',', version_id
            error_str = ' 第' + error_num2 + '行錯誤，此筆FCST錯誤(找不到對應的iac_tconfirm_data)。'+'\n'+'Please check Row#'+error_num2+'FCST record missed (Cannot find corresponding iac_tconfirm_data).'
        if error_num <> '':
            error_str = ' 第' + error_num + '行錯誤，沒有基本資料(versionID,vendor,material)。'+'\n'+'Please check Row#'+error_num+'Basic data missed (buyer, vendor, material).'+'\n' + error_str

        if error_num3 <> '' :
            error_str = ' 第' + error_num3 + '行錯誤，Vendor Code 不正確!'+'\n'+'Please check Row#'+error_num3+'Incorrect Vendor Code.'
        if error_num4 <> '':
            error_str = ' 第' + error_num4 + '行錯誤，Key Part 欄位必需為Y或N !'+'\n'+'Please check Row#'+error_num4+'You have to enter either "Y" or "N" in [Key Part].'

        if error_num5 <> '':
            error_str = ' 第' + error_num5 + '行錯誤，56天交期為空或0時，[Remark] 欄位不可空白 !'+'\n'+'Please check Row#'+error_num5+'[Remark] is required when all the shipping quantity is blank or equals to 0.'

        if error_num6 <> '':
            error_str = ' 第' + error_num6 + '行錯誤，Key Part 欄位為 N，[Remark] 欄位不可空白 !'+'\n'+'Please check Row#'+error_num6+'[Remark] is required when [Key Part] is "N".'

        if error_num7 <> '':
            error_str = ' 第' + error_num7 + '行錯誤，Key Part 欄位為 N，56天交期不允許有數量!'+'\n'+'Please check Row#'+error_num7+'Remove all shipping quantity and leave it blank when [Key Part] is "N".'

        for rx in range(sheet_obj.nrows):  # 讀取：第4行~最後行   # range(0, 6):    temp  for test 先讀到第6行

            # 2. 逐筆讀資料
            if rx >= 3 and error_count==0 and sheet_obj.cell(rx, 0).value: # 從第4行開始讀
                # error_count = 0
                is_remark_list1 = []
                qty_sum = 0
                version_id = str(sheet_obj.cell(rx, version_column).value) # version_id = str(int(sheet_obj.cell(rx, 158).value))
                # print '*75:', rx, '。', version_id
                # vendor_name = str(str(sheet_obj.cell(rx, 160).value))
                material_code = str(sheet_obj.cell(rx, material_column).value)
                vendor_code = str(int(sheet_obj.cell(rx, vendor_column).value)).zfill(10)# 補 0   #str(int(sheet_obj.cell(rx, 159).value))
                iac_pn_vendor = str(sheet_obj.cell(rx, material_column).value) + str(sheet_obj.cell(rx, vendor_column).value)
                buyer_code = str(sheet_obj.cell(rx, buyer_column).value) #str(int(sheet_obj.cell(rx, 0).value[:3])) # A  0
                key_part = str(sheet_obj.cell(rx, key_part_column).value).upper()# C  2
                vendor_remark = sheet_obj.cell(rx, remark_column).value # AF
                storage_location_id = self.env['iac.storage.location.address'].search(
                    [('plant', '=', sheet_obj.cell(rx, plant_column).value.upper()),
                     ('storage_location', '=', sheet_obj.cell(rx, location_column).value.upper())]).id

                for i in range(date_restart_begin_column, date_restart_end_column):
                    if i in delta_list:
                        continue
                    else:
                        if sheet_obj.cell(rx, i).value != '':
                            is_remark_list1.append(sheet_obj.cell(rx, i).value)
                            qty_sum = qty_sum+sheet_obj.cell(rx, i).value
                            print '*278:', qty_sum
                # print '*98:', rx,'。',material_code,'。',buyer_code ,'。',  version_id

				# 發郵件 20180409 Ning add____s

                vendor_reg_id = self.env['iac.vendor'].sudo().search([('vendor_code', '=', vendor_code)]).vendor_reg_id.id
                # print '*111: 發郵件 ' ,vendor_id
                if vendor_reg_id != False:

                    buyer_email = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).buyer_email
                    if buyer_email:
                        print '*117: ', buyer_email
                        buyer_email_now.append(buyer_email)
                        mix = (set(buyer_email_now)&set(email))
                        if len(mix) == 0:

                            print '*120: ', vendor_reg_id
                            #使用現程發mail,畫面就不會卡在這段轉圈圈___s
                            mail_task_vals = {
                                "object_id": vendor_reg_id,
                                "template_id": "iac_forecast_release_to_vendor.vendor_delivery_upload_notice"
                            }
                            print '*127: ', mail_task_vals
                            self.env["iac.mail.task"].add_mail_task(**mail_task_vals)
                            # 使用現程發mail,畫面就不會卡在這段轉圈圈___e

                            #直接發mail
                            #self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.vendor_delivery_upload_notice')
                            email.append(buyer_email)
                        buyer_email_now = []
                            # print 111

                else:
                    raise exceptions.ValidationError("vendor_code不存在 ")
                # 發郵件 20180409 Ning add____e

				 
                # 2.2. 逐筆讀資料：用VersionID+vendor+material 去檢查 iac_tconfirm_data 是否存在
                tconfirm_export = self.env['iac.tconfirm.data'].sudo().search([
                    ('vendor_code', '=', vendor_code),('material_code','=',material_code),
                    ('version','=',version_id),('storage_location_id','=',storage_location_id),('status','=','T')])
                buyer_id = tconfirm_export.buyer_id
                plant_id = tconfirm_export.plant_id
                material_id = tconfirm_export.material_id
                vendor_id = tconfirm_export.vendor_id
                tconfirm_id = tconfirm_export.id
                storage_location_id = tconfirm_export.storage_location_id

                # print '*115:',rx,'。',buyer_code,'。',buyer_id,'。',vendor_id,'。',material_id,'。',tconfirm_id

                if key_part.upper()=='N' and error_count==0:

                    year =  sheet_obj.cell(1,date_restart_begin_column).value.split('/')[0]
                    month = sheet_obj.cell(1, date_restart_begin_column).value.split('/')[1]
                    # if len(month)==1:
                    #     month = '0'+month
                    day = sheet_obj.cell(1, date_restart_begin_column).value.split('/')[2]
                    # print sheet_obj.cell(0,9).value
                    # shipping_date = xlrd.xldate.xldate_as_datetime(sheet_obj.cell(1, 32).value, 0)
                    shipping_date = datetime.datetime(int(year),int(month),int(day))
                    uid = self._uid
                    self._cr.execute(
                        "update iac_tvendor_upload set status='F' "
                        "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id = %s",
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
                        'write_date': today_str,  # 20180803 laura add
                        'write_uid': uid,
                        'create_uid': uid,
                        'reply_id': tconfirm_id,
                        'storage_location_id': storage_location_id.id
                    }
                    print '*358:', ins_vendor_upload_val
                    t_data1 = self.env['iac.tvendor.upload'].sudo().create(ins_vendor_upload_val)
                    t_data1.env.cr.commit()
                    # print t_data1.id
                    vals = {}
                    vals['group_id'] = group.id
                    vals['write_date'] = today_str  # 20180803 laura add

                    # print '*181:', vals
                    t_data1.write(vals)
                    self._cr.execute("update iac_tvendor_upload  set create_uid = %s ,write_uid= %s  ,"
                                     " write_date= %s"
                                     "where id = %s",
                                     (uid, uid, today_str,t_data1.id))
                    t_data1.env.cr.commit()

                if key_part.upper() == 'Y' and error_count==0 and len(is_remark_list1)==0: # len(is_remark_list1)==0:

                    # year = sheet_obj.cell(1, 32).value.split('/')[0]
                    # month = sheet_obj.cell(1, 32).value.split('/')[1]
                    # day = sheet_obj.cell(1, 32).value.split('/')[2]
                    # shipping_date = datetime.datetime(int(year), int(month), int(day))
                    # shipping_date = datetime.datetime(int(record[0:4]),int(record[5:7]),int(record[8:10]))
                    uid = self._uid
                    self._cr.execute(
                        "update iac_tvendor_upload set status='F' "
                        "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id = %s",
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
                        'shipping_date': today_str,
                        'buyer_remark': vendor_remark,
                        'write_date': today_str,  # 20180803 laura add
                        'write_uid': uid,
                        'create_uid': uid,
                        'reply_id': tconfirm_id,
                        'storage_location_id': storage_location_id.id
                    }
                    print '*401:', ins_vendor_upload_val
                    t_data2 = self.env['iac.tvendor.upload'].sudo().create(ins_vendor_upload_val)
                    t_data2.env.cr.commit()
                    vals = {}
                    vals['group_id'] = group.id
                    vals['write_date'] = today_str  # 20180803 laura add

                    # print '*181:', vals
                    t_data2.write(vals)
                    self._cr.execute("update iac_tvendor_upload  set create_uid = %s ,write_uid= %s ,write_date=%s" # 20180803 laura add
                                     "where id = %s",
                                     (uid, uid, today_str,t_data2.id))
                    t_data2.env.cr.commit()

                # 2.3. 檢查都沒錯,再開始逐筆 insert：1. iac_tvendor_remark
                if error_count == 0 and vendor_remark <> '':
                    # 2.3.1. 先  iac_tvendor_remark where 有相同 plant,vendor,material 的改為 F:  false 無效
                    self._cr.execute("update iac_tvendor_remark  set status='F',write_date = %s ,write_uid= %s "   
                                     "where  status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id=%s",
                                     (today_str,login_id,plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

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

                # 2.4. 檢查都沒錯,再開始逐筆 insert：2. iac_tvendor_upload
                if error_count == 0: #沒錯誤再寫入
                    sum = 0
                    for j in range(date_restart_begin_column, date_restart_end_column):
                        if sheet_obj.cell(rx, j).value and sheet_obj.cell(rx, j).value >= 0 and isinstance(sheet_obj.cell(rx, j).value,(float)):
                            sum = sheet_obj.cell(rx, j).value + sum
                    # print '*138: ' ,rx ,'。', sum

                    # 2.4.1.該欄(vendor+material)的demand_qty 總和>=1,就把 iac_tvendor_upload 有相同 plant,vendor,material 的改為 F:  false 無效
                    if sum >= 0:
                        # 紀錄  匯入且資料正確的 all buyer (for mail準備)
                        # 1. 將歷史資料,  status 改 'F'   false 無效
                        self._cr.execute(
                            "update iac_tvendor_upload set status='F',write_date = %s ,write_uid= %s  "      
                            "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id = %s",
                            (today_str, login_id , plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

                        tvendor = self.env['iac.tvendor.upload'].sudo().search([
                            ('status','=','T'),('plant_id','=',plant_id.id),('material_id','=',material_id.id),('vendor_id','=',vendor_id.id),('storage_location_id','=',storage_location_id.id)])
                        # tvendor.id  # 本次 insert 資料的這筆 id
 
                    for i in range(date_restart_begin_column, date_restart_end_column):
                        if i in delta_list:  # 這幾欄不讀
                            t = 0
                            # print '*201: 不讀欄位: Delta公式'
                        else:
                            if sheet_obj.cell(rx, i).value !='' and sheet_obj.cell(rx, i).value >= 0 and isinstance(sheet_obj.cell(rx, i).value,(float)):
                                demand_qty = 0
                                demand_qty = int(sheet_obj.cell(rx, i).value)  # 每欄位的需求
                                demand_date = header_date[i-date_restart_begin_column]
                                print '*338:',rx,',',i,',',demand_qty,',',demand_date
                                # 2.4.2. 再 insert into iac_tvendor_upload
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
                                    'write_uid': uid,
                                    'create_uid': uid,
                                    'reply_id':tconfirm_id,
                                    'storage_location_id': storage_location_id.id
                                }
                                print '*238:',ins_vendor_upload_val
                                t_data3 = self.env['iac.tvendor.upload'].sudo().create(ins_vendor_upload_val)
                                # t_data3.id  # 本次 insert 資料的這筆 id
                                t_data3.env.cr.commit()
                                vals = {}
                                vals['group_id'] = group.id
                                print '*496:', vals
                                t_data3.write(vals)
                                self._cr.execute("update iac_tvendor_upload  set create_uid = %s ,"
                                                 "write_uid= %s  ,write_date= %s"  # 20180803 laura add
                                                 "where id = %s",
                                                 (uid, uid,today_str,t_data3.id))

                                t_data3.env.cr.commit()
                                print '*504:',  group.id

                if error_count == 0:
                    self._cr.execute("update iac_tconfirm_data set buyer_remark=%s,key_part=%s "
                                     "where status = 'T' and  plant_id  = %s and material_id = %s and vendor_id = %s and storage_location_id = %s",
                                     (vendor_remark, key_part, plant_id.id, material_id.id, vendor_id.id,storage_location_id.id))

        # call 接口 ----s
        val = {}
        t_all = self.env['iac.tvendor.upload'].sudo().search([('group_id', '=', group.id)])

        if error_count==0:
            # 调用SAP接口執行更新FP数据的 SP :  1. 先 delete 資料 ODOO_FP_006___s
            print '* 503 :  vendor_upload_lt.py  開始調用SAP接口'
            biz_object = {
                "id": group.id,
                "biz_object_id": group.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_006", biz_object)

            if rpc_result:
                print '*516 : state :  finished(Delete)',',',self.id,',',group.id
                # 调用SAP接口 成功的情况下,修改记录状态
                val['state'] = "finished(Delete)"
                val['state_msg'] = ''
                val['write_date'] =  today_str  # 20180803 laura add
            else:
                val['state'] = "fp error(Delete)"
                val['state_msg'] = u'拋轉FP失败(Delete)'
                val['write_date'] = today_str  # 20180803 laura add
            t_all.write(val)

            self._cr.execute("update iac_tvendor_upload  set create_uid = %s ,write_uid= %s, write_date= %s " # 20180803 laura add
                             "where group_id = %s",
                             (login_id, login_id, today_str,group.id))

            print '*541:', login_id, ',', val
            print '*542:   vendor_upload_lt.py 結束 調用SAP接口 '
            # 调用SAP接口執行更新FP数据的 SP :  1. 先 delete 資料  ODOO_FP_006 ___e

            # 调用SAP接口執行更新FP数据的 SP :   2. insert 資料ODOO_FP_004 ___s
            print '* 262 :  vendor_upload_lt.py  開始調用SAP接口'
            biz_object2 = {
                "id": group.id,
                "biz_object_id": group.id,
                "sql_type": "I"  # I : insert , U : update , D: delete
            }
            rpc_result2, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_004", biz_object2)
            if rpc_result2:

                # 调用SAP接口 成功的情况下,修改记录状态
                val['state'] = "finished(Insert)"
                val['state_msg'] = ''
                val['write_date'] = today_str  # 20180803 laura add
            else:
                val['state'] = "fp error(Insert)"
                val['state_msg'] = u'拋轉FP失败(Insert)'
                val['write_date'] = today_str  # 20180803 laura add
            t_all.write(val)

            self._cr.execute("update iac_tvendor_upload  set create_uid = %s ,write_uid= %s ,write_date = %s "  # 20180803 laura add
                             "where group_id = %s",
                             (login_id, login_id, today_str, group.id))
            print '*560:' ,login_id,',',val
            print '*561:   vendor_upload_lt.py 結束 調用SAP接口 '
            # 调用SAP接口執行更新FP数据的 SP :   2. insert 資料 ODOO_FP_004___e
        # call 接口 ----e

        if error_str <> '':
            raise exceptions.ValidationError(error_str)
        else:
            # mail 功能 ___________s
            # print '*183: mail 出去。' , buyer_all
            # buyer_all = list(set(buyer_all)) #抓出 distinct  buyer list
            # print '*185:', buyer_all

            # mail 功能 ___________e
            print self
            vals = {
                'action_type': 'Vendor Upload',
                'vendor_id':vendor_id.id
            }
            self.env['iac.supplier.key.action.log'].create(vals)
            self.env.cr.commit()
            raise exceptions.ValidationError('上傳成功')

class Group_tVendorUpload(models.Model):
    # 建立一model  for  call API group_id用 (可整批拋,只call 一次API)
    _name = 'iac.tvendor.upload.group'

    group_ids = fields.One2many('iac.tvendor.upload', 'group_id')

class tVendorUpload(models.Model):
    # 目的：iac_tvendor_upload : 將  vendor 回寫的LT報表 寫入iac_tvendor_upload檔
    _name = 'iac.tvendor.upload'
    _description = "tvendor upload"
    _order = 'status desc,id desc'

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
    # key_part = fields.Selection([('',''),('Y','Y'),('N','N')],string='key part',index=True,copy=False)

    vendor_id = fields.Many2one('iac.vendor', string="廠商代碼",index=True)
    vendor_code = fields.Char(string="Vendor_code", related="vendor_id.vendor_code")
    iac_pn_vendor = fields.Char(string="iac_pn vendor")

    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)

    reply_id = fields.Many2one('iac.tconfirm.data',index=True)
    group_id = fields.Many2one('iac.tvendor.upload.group')

    # 紀錄 "调用SAP接口"是否成功的欄位____s
    state = fields.Selection([
        ('pending', 'Pending'), # 等待拋轉中
        ('fp error(Update)', 'FP Error(Update)'),  # 通知FP失敗 Update
        ('fp error(Delete)', 'FP Error(Delete)'),  # 通知FP失敗 Delete
        ('fp error(Insert)', 'FP Error(Insert)'),  # 通知FP失敗 Insert
        ('finished(Update)', 'Finished(Update)'),  # 更新FP成功 Update
        ('finished(Delete)', 'Finished(Delete)'),  # 更新FP成功 Delete
        ('finished(Insert)', 'Finished(Insert)')  # 更新FP成功  Insert
    ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char()
    # 紀錄 "调用SAP接口"是否成功的欄位____e

    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add
    # storage_location_ad = fields.Char()
    storage_location = fields.Char()

class tVendorRemark(models.Model):
    # 目的：iac_tvendor_remark : 將  vendor 回寫的LT報表 中的 '備註' 寫入 iac_tvendor_remark檔
    _name = 'iac.tvendor.remark'
    _description = "tvendor remark"
    _order = 'status desc,id desc'

    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code', string="採購代碼", index=True)
    material_id = fields.Many2one('material.master', 'Material', index=True)
    vendor_id = fields.Many2one('iac.vendor', string="廠商代碼",index=True)
    vendor_remark = fields.Char(string="Remark")
    iac_pn_vendor = fields.Char(string="iac_pn vendor")
    basicdate = fields.Date(string="basicd ate") #基準日 W1_R 的起始日
    cdt = fields.Date(string="cdt")
    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add



