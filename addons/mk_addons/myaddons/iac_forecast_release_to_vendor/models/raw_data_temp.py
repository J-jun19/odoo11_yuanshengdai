# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import datetime

class IacFlowNo(models.Model):
    #用来存流水号的表
    _name = 'iac.flow.no'

    plant_code = fields.Char()
    storage_location = fields.Char()
    buyer_code = fields.Char()
    release_date_str = fields.Char()
    flow_no = fields.Integer()

class VendorRegisterFcst(models.Model):
    # 201807 Ning add for 跳过ir_rule的检查 (因为iac_vendor_register中会根据buyer_email检查 ,所以发邮件会有报错)

    _name = 'iac.vendor.register.fcst'
    _inherit = ['iac.vendor.register']

    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)

    _table = 'iac_vendor_register'
	
class Group_ConfirmData(models.Model):
    # 建立一model  for  call API group_id用 (可整批拋,只call 一次API) #20180702 laura add  for整批拋FP
    _name = 'iac.tconfirm.data.group'
    group_ids = fields.One2many('iac.tconfirm.data', 'group_id')

class Group_ConfirmVersion(models.Model):
    # 建立一model  for  call API group_id用 (可整批拋,只call 一次API) #20180702 laura add  for整批拋FP

    _name = 'iac.tconfirm.version.group'
    group_ids = fields.One2many('iac.tconfirm.version', 'group_id')

class RawDataTemp(models.Model):

    _name = 'iac.traw.data.temp'
    _description = "traw data temp table"
    _order = 'id desc , fpversion'

    _inherit = ['iac.traw.data']

    raw_id = fields.Many2one('iac.traw.data', string="raw data id")
    plant_code = fields.Char(string='Plant', related='plant_id.plant_code')

    # status = fields.Char(stringb="status") # T: true有效,F:  false無效,D: done已發出
    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('D', '已發出')   #  D: done已發出
    ], string='Status', readonly=True, index=True, copy=False)

    # today_str = fields.Char(string='今天日期', compute='get_today_str')  # 取得今天日期
    today_str = datetime.datetime.now().strftime("%Y%m%d") # fields.Char(string="今天日期", compute="get_today_str")


    print '*39:',today_str

    def get_today_str(self):
        # 取得今天日期
        print '*31:'
        for rawid in self:
            print '*32:', rawid.today_str
            rawid.today_str = fields.Datetime.now()[:10].replace('-', '').replace(' ', '')

    #根据plant code,location,buyer code,当天日期的字符串（yyyymmdd）获取唯一的版号
    @api.multi
    def get_edi_version(self,plant_code,storage_location,buyer_code,today_str):
        #先确认流水号表里是否有对应记录
        flow_no_obj = self.env['iac.flow.no'].search([('plant_code','=',plant_code),('storage_location','=',storage_location),
                                        ('buyer_code','=',buyer_code),('release_date_str','=',today_str)])
        if flow_no_obj:
            #如果有记录，则流水号+1
            flow_no = flow_no_obj.flow_no+1
            #去对照表中抓plant和location对应的代码
            code_mapping = self.env['plant.location.code.mapping'].search([('plant_code','=',plant_code),
                                                            ('storage_location','=',storage_location)])
            edi_version = buyer_code+today_str+code_mapping.plant_code_mapping\
                          +code_mapping.storage_location_mapping+str(flow_no).zfill(2)
            flow_no_obj.write({'flow_no':flow_no})
            flow_no_obj.env.cr.commit()
            return edi_version
        else:
            #如果没有记录，则创建一笔流水号为1的记录
            vals = {
                'plant_code':plant_code,
                'storage_location':storage_location,
                'buyer_code':buyer_code,
                'release_date_str':today_str,
                'flow_no':1
            }
            self.env['iac.flow.no'].create(vals)
            self.env.cr.commit()
            # 去对照表中抓plant和location对应的代码
            code_mapping = self.env['plant.location.code.mapping'].search([('plant_code', '=', plant_code),
                                                                           ('storage_location', '=', storage_location)])
            edi_version = buyer_code + today_str + code_mapping.plant_code_mapping \
                          + code_mapping.storage_location_mapping + '01'
            return edi_version

    @api.multi
    def button_to_release_fsct_to_vendor(self):
        # raise UserError('button_to_release_fsct_to_vendor')
        # release to vendor
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        today = fields.Datetime.now()  # 当前时间字符串  #print '*25:', fields.Datetime.now()
        login_id = self.env.user.id

        count = 0 #紀錄第幾筆資料的  20180704 laura add
        #buyer_code_last ='' #前一筆buyer_code
        #buyer_code_this ='' #這一筆buyer_code
        #20180702  laura add for整批拋FP---s
        val = {}
        group_confirm = self.env['iac.tconfirm.data.group'].sudo().create(val)
        group_version = self.env['iac.tconfirm.version.group'].sudo().create(val)
        group_confirm.env.cr.commit()
        group_version.env.cr.commit()
        # print '*77',group_confirm ,',', group_version
        # 20180702  laura add for整批拋FP---e

        #先判断需要release的资料是否正确维护plant和location对应的代码，如果没有则报错
        for item in self.ids:
            ori_raw_data = self.env['iac.traw.data.temp'].sudo().browse(item)
            code_mapping = self.env['plant.location.code.mapping'].search([
                ('plant_code', '=', ori_raw_data.plant_code),
                ('storage_location', '=', ori_raw_data.storage_location_id.storage_location)])
            if not code_mapping:
                raise UserError('Plant'+ori_raw_data.plant_code+'和Location'+
                                ori_raw_data.storage_location_id.storage_location+'没有维护代码的对照关系，请联系IT')


        #抓取所有release资料对应的 plant code,location以及buyer code作为key
        plant_location_buyer_list = []
        for item in self.ids:
            ori_raw_data = self.env['iac.traw.data.temp'].sudo().browse(item)
            key = str(ori_raw_data.plant_code)+','\
                  +str(ori_raw_data.storage_location_id.storage_location)+','\
                  +str(ori_raw_data.buyer_code)
            if key not in plant_location_buyer_list:
                plant_location_buyer_list.append(key)

        #plant code，location，buyer code和edi version的对应关系
        plant_location_buyer_edi_version = {}
        for key in plant_location_buyer_list:
            plant_code = key.split(',')[0]
            storage_location = key.split(',')[1]
            buyer_code = key.split(',')[2]
            today_str = datetime.datetime.now().strftime("%Y%m%d")  # yyyymmdd  fields.Char(string="今天日期",
            plant_location_buyer_edi_version[key] = self.get_edi_version(plant_code,
                                                                         storage_location,buyer_code,today_str)
            # next_edi_version = ''
            # # edi version 今天日期+流水號   20180704 laura add
            #
            # # 逐筆檢查 iac.tvendor.upload：料+vendor+buyer+日期 是否有回填多筆數量
            # self._cr.execute(
            #     "   select distinct max( substr(edi_version,1,3) || cast(cast (substr(edi_version,4,12) as numeric )+1 as text)) as  next_edi_version "
            #     "   FROM public.iac_tconfirm_version"
            #     "    where  substr(edi_version,4,8) = %s    and substr(edi_version,1,3) = %s   "
            #     , (today_str, buyer_code))
            # for row in self.env.cr.dictfetchall():
            #     next_edi_version = row['next_edi_version']
            #
            # if not next_edi_version:
            #     next_edi_version = buyer_code + today_str + '0001'
            #     print '*107:', next_edi_version

            # buyer_code_edi_version[buyer_code] = next_edi_version

        vendor_all_list = []
        # 產生資料：iac.tconfirm.version
        for item in self.ids:
            count += 1  # 紀錄第幾筆資料的  20180704 laura add

            print '*82:', self.ids ,',', count
            message = ''
            title = ''
            edi_version ='' #20180704 laura add
            ori_raw_data = self.env['iac.traw.data.temp'].sudo().browse(item)
            string_parameters = {}

            # 20180704 laura add  for EDI_version : 一次release 只要統一給一個版號：Buyer Code 3碼 + yyyyMMdd + 流水號4碼----s
            #  yyyymmdd+ 當日的流水號
            #  release 中的 第一筆在抓 edi_version
            # if count == 1 : #紀錄第幾筆資料的  20180704 laura add
            #
            #     today_str = datetime.datetime.now().strftime("%Y%m%d")  # yyyymmdd  fields.Char(string="今天日期",
            #     next_edi_version = ''
            #     # edi version 今天日期+流水號   20180704 laura add
            #
            #     # 逐筆檢查 iac.tvendor.upload：料+vendor+buyer+日期 是否有回填多筆數量
            #     self._cr.execute("   select distinct max( substr(edi_version,1,3) || cast(cast (substr(edi_version,4,12) as numeric )+1 as text)) as  next_edi_version "
            #                      "   FROM public.iac_tconfirm_version"
            #                      "    where  substr(edi_version,4,8) = %s    and substr(edi_version,1,3) = %s   "
            #                      , (today_str , ori_raw_data.buyer_code) )
            #     for row in self.env.cr.dictfetchall():
            #         next_edi_version = row['next_edi_version']
            #
            #     if row['next_edi_version'] :
            #         print '*104:', next_edi_version
            #     else:
            #         next_edi_version = ori_raw_data.buyer_code + today_str + '0001'
            #         print '*107:', next_edi_version
            #
            #     print '*108:', next_edi_version
                # return self.env['warning_box'].info(title='test ', message='*103')
            # 20180704 laura add  for EDI_version : 一次release 只要統一給一個版號：Buyer Code 3碼 + yyyyMMdd + 流水號4碼----e

            # 版本號的编码规则：Buyer Code 3碼 + yyyyMMdd + 流水號4碼
            version = ori_raw_data.buyer_code + self.env['ir.sequence'].next_by_code('iac.forecast.release.to.vendor')
            key = str(ori_raw_data.plant_code) + ',' \
                  + str(ori_raw_data.storage_location_id.storage_location) + ',' \
                  + str(ori_raw_data.buyer_code)
            # 1.產生資料： insert  iac.tconfirm.version
            tconfirm_version_val = {
                'status': 'T',  # status 有效 # T: true有效,F:  false無效, O: old 舊版
                'version' : version,
                'raw_id' : ori_raw_data.raw_id.id,
                'buyer_id' : ori_raw_data.buyer_id.id,
                'fpversion' : ori_raw_data.fpversion,
                'division_id' : ori_raw_data.division_id.id ,
                'vendor_id' : ori_raw_data.vendor_id.id ,
                'material_id' : ori_raw_data.material_id.id,
                'edi_version' : plant_location_buyer_edi_version[key],  # 20180704 laura add
                'group_id': group_version.id, # 20180702 laura add for整批拋FP
                'storage_location_id':ori_raw_data.storage_location_id.id
            }
            print '*127:',tconfirm_version_val
            t_version = self.env['iac.tconfirm.version'].sudo().create(tconfirm_version_val)
            # t_version.id # 本次 insert 資料的這筆 id

            # 2.更新資料：update iac.tconfirm.version ,將相同vendor&material的status改 O: old 舊版
            upd_version_status = self.env['iac.tconfirm.version'].sudo().search(
                [('vendor_id', '=', ori_raw_data.vendor_id.id), ('status', '<>', 'F'),
                 ('material_id', '=', ori_raw_data.material_id.id), ('id', '<>', t_version.id),('storage_location_id','=',ori_raw_data.storage_location_id.id)])
            vals = {}
            vals['status'] = 'O'
            print '*142:', vals
            upd_version_status.write(vals)
            upd_version_status.env.cr.commit()

            # self._cr.execute("update iac_tconfirm_version set status = 'O',"
            #                  "write_date = %s ,write_uid= %s  "
            #                  "where  status <> 'F' and vendor_id = %s and material_id = %s and id <> %s",
            #                 (today,login_id,ori_raw_data.vendor_id.id, ori_raw_data.material_id.id , t_version.id) )
            # uid = self._uid
            # t_version._cr.execute("update iac_tconfirm_version  set create_uid = %s ,write_uid= %s "
            #                       "where id = %s", (uid, uid, t_version.id))
            # t_version.env.cr.commit()
            # print '*145:', uid, ', ', self._uid, ', ', t_version.create_uid, ', ', t_version.id

            # 1.產生資料： insert  iac.tconfirm.data
            tconfirm_data_val = {
                'status': 'T', # status 有效 # T: true有效,F:  false無效, O: old 舊版
                'release_flag': 'Y',
                'flag': ori_raw_data.flag,
                'material_id': ori_raw_data.material_id.id,
                'vendor_id': ori_raw_data.vendor_id.id,
                'division_id': ori_raw_data.division_id.id,
                'plant_id': ori_raw_data.plant_id.id,
                'vendor_reg_id': ori_raw_data.vendor_reg_id.id,
                'raw_id': ori_raw_data.raw_id.id,
                'buyer_id': ori_raw_data.buyer_id.id,
                'fpversion': ori_raw_data.fpversion,
                'version': version,
                'description': ori_raw_data.description,
                'alt_grp': ori_raw_data.alt_grp,
                'alt_flag': ori_raw_data.alt_flag,
                'stock': ori_raw_data.stock,
                'open_po': ori_raw_data.open_po,
                'intransit_qty': ori_raw_data.intransit_qty,
                'quota': ori_raw_data.quota,
                'vendor_name': ori_raw_data.vendor_name,
                'round_value': ori_raw_data.round_value,
                'leadtime': ori_raw_data.leadtime,
                'qty_w1': ori_raw_data.qty_w1,
                'qty_w1_r': ori_raw_data.qty_w1_r,
                'qty_w2': ori_raw_data.qty_w2,
                'qty_w3': ori_raw_data.qty_w3,
                'qty_w4': ori_raw_data.qty_w4,
                'qty_w5': ori_raw_data.qty_w5,
                'qty_w6': ori_raw_data.qty_w6,
                'qty_w7': ori_raw_data.qty_w7,
                'qty_w8': ori_raw_data.qty_w8,
                'qty_w9': ori_raw_data.qty_w9,
                'qty_w10': ori_raw_data.qty_w10,
                'qty_w11': ori_raw_data.qty_w11,
                'qty_w12': ori_raw_data.qty_w12,
                'qty_w13': ori_raw_data.qty_w13,
                'qty_m1': ori_raw_data.qty_m1,
                'qty_m2': ori_raw_data.qty_m2,
                'qty_m3': ori_raw_data.qty_m3,
                'qty_m4': ori_raw_data.qty_m4,
                'qty_m5': ori_raw_data.qty_m5,
                'qty_m6': ori_raw_data.qty_m6,
                'qty_m7': ori_raw_data.qty_m7,
                'qty_m8': ori_raw_data.qty_m8,
                'qty_m9': ori_raw_data.qty_m9,
                'create_date':ori_raw_data.create_date,
                'po':ori_raw_data.po,
                'pr':ori_raw_data.pr,
                'remark':ori_raw_data.remark,
                'b001': ori_raw_data.b001,
                'b002': ori_raw_data.b002,
                'b004': ori_raw_data.b004,
                'b005': ori_raw_data.b005,
                'b012': ori_raw_data.b012,
                'b017b': ori_raw_data.b017b,
                'b902q': ori_raw_data.b902q,
                'b902s': ori_raw_data.b902s,
                'custpn_info': ori_raw_data.custpn_info,
                'mfgpn_info': ori_raw_data.mfgpn_info,
                'max_surplus_qty': ori_raw_data.max_surplus_qty,
                'mquota_flag': ori_raw_data.mquota_flag,
                'edi_version': plant_location_buyer_edi_version[key],  # 20180704 laura add,
                'group_id': group_confirm.id,  # 20180702 laura add for整批拋FP
                'storage_location_id':ori_raw_data.storage_location_id.id
            }
            print '*213:',tconfirm_data_val
            t_data = self.env['iac.tconfirm.data'].sudo().create(tconfirm_data_val)
            # t_data.id  # 本次 insert 資料的這筆 id

            # 2.更新資料：update iac.tconfirm.data ,將相同vendor&material的status改 O: old 舊版, release_flag改N
            upd_confirm_status = self.env['iac.tconfirm.data'].sudo().search(
                [('vendor_id', '=', ori_raw_data.vendor_id.id), ('status', '<>', 'F'),
                 ('material_id', '=', ori_raw_data.material_id.id),('id', '<>', t_data.id),('storage_location_id','=',ori_raw_data.storage_location_id.id)])
            vals = {}
            vals['status'] = 'O'
            vals['release_flag'] = 'N'
            print '*233:',vals
            upd_confirm_status.write(vals)
            upd_confirm_status.env.cr.commit()

            # self._cr.execute("update iac_tconfirm_data set status = 'O' ,release_flag='N',"
            #                  "write_date = %s ,write_uid= %s "
            #                  "where  status <> 'F' and vendor_id =%s  and material_id=%s and id<>%s ",
            #                 (today,login_id,ori_raw_data.vendor_id.id, ori_raw_data.material_id.id , t_data.id) )
            # self.env.cr.commit()

            # t_data.id  # 本次 insert 資料的這筆 id
           
            t_data._cr.execute("update iac_tconfirm_data  set create_uid = %s ,write_uid= %s "
                               "where id = %s",
                               (login_id, login_id, t_data.id))
            t_data.env.cr.commit()
            print '*249:', login_id, ', ', self._uid, ', ', t_data.create_uid, ', ', t_data.id

            # 更改資料：update  iac.traw.data.temp  , status =  D: done已發出
            traw_data_temp_val = {
                'status': 'D'
            }
            super(RawDataTemp, self).write(traw_data_temp_val)
            message = message + u' 此筆已release成功 。'
            title = "Release FCST to vendor"
            # 發送 mail to vendor  ___ IAC-Laura add___s

            # 批次 release to vendor時,同個vendor只要收到一封mail ___ IAC-Laura add
            vendor_id = self.env['iac.traw.data.temp'].sudo().browse(item).vendor_id.id

            print '*263:', vendor_id, ',', vendor_all_list

            if vendor_id not in vendor_all_list:
                vendor_all_list.append(vendor_id)
                print '*267:', vendor_id ,',',vendor_all_list

                # 修改添加发mail---shier add
                if vendor_id != False:
                    vendor_reg_id = self.env['iac.vendor'].sudo().browse(vendor_id).vendor_reg_id.id
                    vendor_reg_code = self.env['iac.vendor'].sudo().browse(vendor_id).vendor_code

                    if vendor_reg_id != False:
                        sales_email = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).sales_email
                        other_emails = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).other_emails
                        if not sales_email and not other_emails:
                            raise exceptions.ValidationError(u'厂商代码为%s的Email Notice Recipients为空，请前往vendor registration页面补全资料'%vendor_reg_code)

                        elif sales_email and not other_emails:
                            emails = sales_email
                            body_list = [
                                ['The latest forecast report has been released, please log on IAC Supplier Portal'],
                                ['and reply your supply plan accordingly.  Thank you.']]
                            # self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.release_fcst_to_vendor')
                            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', emails, "",
                                                                      'IAC FCST Release Notice',
                                                                      ['Dear Valued Partner:'],
                                                                      body_list, 'RELEASE_FCST_TO_VENDOR')
                        elif other_emails and not sales_email:
                            emails = other_emails
                            body_list = [['The latest forecast report has been released, please log on IAC Supplier Portal'],['and reply your supply plan accordingly.  Thank you.']]
                            # self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.release_fcst_to_vendor')
                            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', emails, "", 'IAC FCST Release Notice', ['Dear Valued Partner:'],
                                                                      body_list,'RELEASE_FCST_TO_VENDOR')
                        elif sales_email and other_emails:
                            emails = sales_email + ';' + other_emails
                            body_list = [
                                ['The latest forecast report has been released, please log on IAC Supplier Portal'],
                                ['and reply your supply plan accordingly.  Thank you.']]
                            # self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.release_fcst_to_vendor')
                            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', emails, "",
                                                                      'IAC FCST Release Notice',
                                                                      ['Dear Valued Partner:'],
                                                                      body_list, 'RELEASE_FCST_TO_VENDOR')
                        else:
                            message = message + u' email為空，無法發送郵件。 '
                    else:
                        message = message + u' 資料錯誤或未維護! (iac_vendor) 。 '
                else:
                    message = message + u' 資料錯誤或未維護! (iac_traw_data)。 '
            # 發送 mail to vendor  ___ IAC-Laura add___e
        #end for

        # call 接口--FP_002 & FP_003-----s
        # 改為整批指拋轉1次,加快速度 20180702 laura add
        # 因為EDI 830 需要從sql server抓此table資料,進行加工處理,so要再把此表資料轉回 sql server VSM 的 tConfirmData __ IAC-Laura remove mark 20180628
        # Jocelyn說  tconfirm_version & tconfirm_data 不用回傳FP,所以此段temp mark IAC-Laura 20180329
        # 本機測試環境,無法?用SAP接口,加入此段會報錯,於本機端暫時 temp mark  IAC-Laura20180320
        #  3. 調用SAP接口執行更新FP數据的 SP : insert  iac.tconfirm.data  & update iac.tconfirm.data,將相同vendor&material的status改 O: old 舊版
        print '*292"' ,group_confirm.id

        test = self.env['iac.tconfirm.data'].sudo().search([('group_id', '=', group_confirm.id)])
        for item in test:
            print '*296:', test,',', item ,',', item.buyer_id.id ,',', item.buyer_id ,',',   item.status

        print '*298"', test
        print '* 299 : raw_data_temp.py 開始調用SAP接口 FP_003 (tconfirm_version)'
        # 1.   tconfirm_version    FP_003
        biz_object = {
            "id": group_version.id,
            "biz_object_id": group_version.id
        }

        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_003", biz_object)

        # if rpc_result:
        #     print '*234: fp_state :  finished '
        #     # 調用SAP接口 成功的情況下,修改狀態
        #     self.write({"fp_state": "finished"})
        # else:
        #     print '258: state :  fp error '
        #     self.write({'state': 'fp error', 'state_msg': u'拋轉FP失敗'})

        # 2.   tconfirm_data    FP_002
        print '* 318 : raw_data_temp.py 開始調用SAP接口 FP_002 (tconfirm_data)'
        biz_object = {
            "id": group_confirm.id,
            "biz_object_id": group_confirm.id
        }

        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log("ODOO_FP_002", biz_object)

        # if rpc_result:
        #     print '*258: state :  finished '
        #     # 調用SAP接口 成功的情況下,修改狀態
        #     self.write({"state": "finished"})
        # else:
        #     print '*262: state :  fp error '
        #     self.write({'state': 'fp error', 'state_msg': u'拋轉FP失敗'})
        # call 接口--FP_002 & FP_003-----e

        return self.env['warning_box'].info(title=title, message=message)


    def send_to_email(self, object_id=None, template_name=None):
        template = self.env.ref(template_name)
        return template.send_mail(object_id, force_send=True)

    @api.multi
    def action_confirm_open_form(self, values):
        # open form 的 save button
        values['status'] = 'T' # status 改成 有效 # T: true有效,F:  false無效,D: done已發出
        values['qty_w1'] = self.qty_w1
        values['qty_w1_r'] = self.qty_w1_r
        values['qty_w2'] = self.qty_w2
        values['qty_w3'] = self.qty_w3
        values['qty_w4'] = self.qty_w4
        values['qty_w5'] = self.qty_w5
        values['qty_w6'] = self.qty_w6
        values['qty_w7'] = self.qty_w7
        values['qty_w8'] = self.qty_w8
        values['qty_w9'] = self.qty_w9
        values['qty_w10'] = self.qty_w10
        values['qty_w11'] = self.qty_w11
        values['qty_w12'] = self.qty_w12
        values['qty_w13'] = self.qty_w13
        values['qty_m1'] = self.qty_m1
        values['qty_m2'] = self.qty_m2
        values['qty_m3'] = self.qty_m3
        values['qty_m4'] = self.qty_m4
        values['qty_m5'] = self.qty_m5
        values['qty_m6'] = self.qty_m6
        values['qty_m7'] = self.qty_m7
        values['qty_m8'] = self.qty_m8
        values['qty_m9'] = self.qty_m9
        values['storage_location_id'] = self.storage_location_id.id
        change = super(RawDataTemp, self).write(values)

        return change

