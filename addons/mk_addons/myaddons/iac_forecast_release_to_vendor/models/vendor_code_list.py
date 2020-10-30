# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
import raw_data_list
from odoo.exceptions import UserError, ValidationError
# from odoo.osv import fields,osv

class RawDataVendorList(models.Model):
    _name = 'iac.traw.data.vendor.list'
    _description = "traw data vendor list"
    # _order = 'id , fpversion'

    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True) #廠商代碼
    last_version =fields.Char(string='Last Release Ver.') # max Release Ver
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code", index=True)
    edi_830 = fields.Char(string='EDI 830') # 顯示屬於EDI830的廠商  20180806 laura add
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add

    @api.multi
    def get_version(self):
        # 取得歷史release版本 open window

        ids = []
        # 抓vendor_code下的所有 iac.tconfirm.version 版本
        for rawid in self:
            print '*27:' , rawid.vendor_id.id ,',',rawid.buyer_id.id
            tversion_exist = self.env['iac.tconfirm.version'].sudo().search(
                [ ('vendor_id', '=', rawid.vendor_id.id )  #,('fpversion', '=', rawid.fpversion)
                  # ,('buyer_id', '=', rawid.buyer_id.id) # history 只能看到 該 buyer release 過的料 20181018 laura add
                ])

            for tv in tversion_exist:
                ids += [(tv.id)]

        action = {
            'name': _('confirm version open tree'),
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'iac.tconfirm.version',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('iac_forecast_release_to_vendor.confirm_version_open_tree').id,
            'act_window_id': self.env.ref('iac_forecast_release_to_vendor.action_confirm_version_open_tree').id,
            'domain': [('id', 'in', ids)]
        }
        return action

    @api.multi
    def button_to_list_material(self):
        print '*50'

        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___s
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'FORECAST' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0 :
                raise UserError(' 正在轉資料 ,請勿操作 ! ')
        # 轉資料的job正在執行,就不能執行程式20181015 laura add ___e

        allids = []
        today_str = fields.Datetime.now()[:10].replace('-','').replace(' ','')

        # 20180815 laura 先找出 max_fpversion ( 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion )---s
        tcolumn_title = self.env['iac.tcolumn.title'].sudo().search(
            [('fpversion', '>=', today_str)], order='fpversion desc',
            limit=1)  # 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion,否則抓title會出錯 20180809 laura add
        print '*59:', tcolumn_title.fpversion
        # 20180815 laura 先找出 max_fpversion ( 如果系統日有多筆 fpversion ,只抓最新的一筆 fpversion )---e


        for item in self:
            all_item = self.env['iac.traw.data.vendor.list'].sudo().browse(item.id)
            print '*65:', all_item
            traw_exist = self.env['iac.traw.data'].sudo().search(
                [('plant_id', '=', all_item.plant_id.id),
                 ('buyer_id', '=', all_item.buyer_id.id),
                 ('vendor_id', '=', all_item.vendor_id.id),
                 ('material_id','!=', False ),
                 ('storage_location_id','=',all_item.storage_location_id.id),
                 ('fpversion', '=', tcolumn_title.fpversion) #today_str
                 ]) # 條件： 1. 料號<>null。 2. 只抓 fpversion='當天' 的資料。
            print '*73:', traw_exist
            print '*74: test second -end', fields.Datetime.now()
            print '*86:', all_item.plant_id.id
            #201807 Ning add for 帶出代用料---s
            for pi in traw_exist:
                allids += [(pi.id)]
                pi.write({'alt_grp_sort':'T','state':'1'})
                pi.env.cr.commit()
                if pi.alt_grp != '':
                    print '*93:', all_item.plant_id.id
                    material_exist = self.env['iac.traw.data'].sudo().search([
                        ('alt_grp', '=', pi.alt_grp),('fpversion', '=', tcolumn_title.fpversion),('plant_id', '=', all_item.plant_id.id),('storage_location_id','=',all_item.storage_location_id.id)]) #20181114 laura add: FCST帶出代用料排除CP22
                    for item in material_exist:
                        if not item.id in allids:
                            allids += [(item.id)]
                            item.write({'alt_grp_sort': 'F','state':'0'})
                            item.env.cr.commit()
            # 201807 Ning add for 帶出代用料---e

        # List Materials  選擇FCST
        print '*92'
        action = {
            'name': _('Action raw data form 2 '),
            'type': 'ir.actions.act_window',
            'res_model': 'iac.traw.data',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('iac_forecast_release_to_vendor.view_raw_data_tree_2').id,
            'act_window_id': self.env.ref('iac_forecast_release_to_vendor.action_raw_data_form_2').id,
            'domain': [('id', 'in', allids)]

        }
        return action

    @api.multi
    def button_remind_mail(self):
        """  催簽mail通知_功能"""

        for item in self:
            # print '*102:', item.id
            vendor_id = item.vendor_id.id # self.env['iac.traw.data'].sudo().browse(item.raw_id.id).vendor_id.id
            # print '*104:',vendor_id
            if vendor_id != False:

                vendor_reg_id = self.env['iac.vendor'].sudo().browse(vendor_id).vendor_reg_id.id
                if vendor_reg_id != False:
                    sales_email = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).sales_email
                    other_emails = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).other_emails
                    #print sales_email,other_emails
                    if sales_email or other_emails:
                        self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.remind_email')
                    else:
                        raise exceptions.ValidationError("email為空，無法發送郵件")
                else:

                    raise exceptions.ValidationError("資料錯誤或未維護! (iac_vendor) ")
            else:
                raise exceptions.ValidationError("資料錯誤或未維護! (iac_traw_data) ")

    def send_to_email(self, object_id=None, template_name=None):
        template = self.env.ref(template_name)
        return template.send_mail(object_id, force_send=True)


    @api.multi
    def button_changeFCST_mail(self):
        """  Cancel Release   FCST變更通知_功能"""

        today = fields.Datetime.now()  # 当前时间字符串  #print '*25:', fields.Datetime.now()
        login_id = self.env.user.id

        for item in self:
            print '*135:', item.id
            vendor_id = item.vendor_id.id  # self.env['iac.traw.data'].sudo().browse(item.raw_id.id).vendor_id.id
            print '*137:', vendor_id

            # # 動作1. 把 該vendor_id的所有已release的資料 失效 ( iac_tconfirm_data.status 改F: 無效 ), release_flag改N
            self._cr.execute("update iac_tconfirm_version set status = 'F',write_date = %s ," \
                             "            write_uid= %s where vendor_id = %s ", \
                             (today, login_id, vendor_id))

            self._cr.execute("update iac_tconfirm_data set status = 'F',release_flag='N', "
                             "            write_date = %s ,write_uid= %s  where vendor_id = %s",
                             (today,login_id,vendor_id))
            message = u' release資料失效成功。 '

            # 動作2. mail 給vendor
            for item in self:
                print '*152:', item.id

                vendor_id = item.vendor_id.id  #self.env['iac.traw.data'].sudo().browse(item.raw_id.id).vendor_id.id
                if vendor_id != False:
                    vendor_reg_id = self.env['iac.vendor'].sudo().browse(vendor_id).vendor_reg_id.id
                    if vendor_reg_id != False:
                        sales_email = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).sales_email
                        other_emails = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id).other_emails
                        # print sales_email,other_emails
                        if sales_email or other_emails:
                            self.send_to_email(vendor_reg_id, 'iac_forecast_release_to_vendor.change_email')
                        else:
                            message = message + u' email發送失敗：資料錯誤或未維護! (email為空，無法發送郵件)。 '
                    else:
                        message = message + u' email發送失敗：資料錯誤或未維護! (iac_vendor)。 '
                else:
                    message = message + u' email發送失敗：資料錯誤或未維護! (iac_traw_data)。 '

            return self.env['warning_box'].info(title='error! ', message=message)


class IacVendorCodeWizard(models.TransientModel):
    """ 查询 VendorCodeList
       <取得RawData及當前confirmdata下指定BuyerCode下的所有Vendor>
        參考  StoredProcedure [VSM].[dbo].[SP_GetVendorList]
        VendorCodeList 檔
         # Search vendor list 的畫面檔
        """
    _name = 'iac.vendor.code.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    buyer_id = fields.Many2one('buyer.code.fcst', string='Buyer Code fcst', index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info",index=True)
    lastversion = fields.Char(string="lastversion")
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Location')  # 181211 ning add

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        self.vendor_id=False
        self.storage_location_id = False


    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):

        if self.plant_id:
            return {'domain': {'storage_location_id': [('plant', '=', self.plant_id.plant_code)]}}

    @api.multi
    def search_buyer_confirm(self):

        # print '*175:' , self.env.user ,' , ',self.env.user.work_user_id ,' , ',self.env.user.work_user_id.partner_id ,' , ',self.env.user.work_user_id.partner_id.plant_ids
        today_str = fields.Datetime.now()[:10].replace('-', '').replace(' ', '')
        # print '*177:',today_str
        # # 1. 先清除之前的資料
        # sql_del = " delete from iac_traw_data_vendor_list "
        # self._cr.execute(sql_del)

        for wizard in self:
            # print '*194:', wizard.buyer_id.id

            # 1. 先清除之前的資料(條件+ buyer_id ) 20180723 laura add
            print '*199:', wizard.buyer_id.id
            delete_old = self.env['iac.traw.data.vendor.list'].sudo().search(
                [('buyer_id', '=', wizard.buyer_id.id)])
            print '*202:', delete_old
            delete_old.sudo().unlink()  # 把舊的查詢紀錄刪掉 unlink

            # 2. 把當日所有的 vendor code list  寫入  iac_traw_data_vendor_list
            self._cr.execute("insert into iac_traw_data_vendor_list (vendor_id,plant_id, last_version,buyer_id,edi_830,storage_location_id) " #顯示屬於EDI830的廠商  20180806 laura add
                             "  (  select DISTINCT  A.vendor_id,A.plant_id,max(v.Version) as LastVersion,A.buyer_id,"
                             "                                    (CASE WHEN edi.vendor_code is null THEN null ELSE 'EDI 830' END) ,A.storage_location_id" #顯示屬於EDI830的廠商  20180806 laura add
                             "   from  "
                             "    (  Select distinct vendor_id,plant_id,buyer_id,storage_location_id  from public.iac_traw_data "
                             "       Where vendor_id is not null and material_id is not null and division_id is not null "
                             "           and buyer_id = %s  and fpversion >=  %s  "
                             "      Union  "
                             "      Select distinct vendor_id, plant_id,buyer_id,storage_location_id  from public.iac_tconfirm_data  "
                             "       Where vendor_id is not null and material_id is not null and division_id is not null  "
                             "            and buyer_id = %s  "
                             "    ) A  left Join public.iac_tconfirm_version  v on v.Vendor_id = A.vendor_id and status='T' and v.buyer_id= %s "
                             "            left Join public.iac_edi_vendor_list edi on edi.vendor_id=A.vendor_id " #顯示屬於EDI830的廠商  20180806 laura add
                             "Group By  A.vendor_id,A.plant_id,A.buyer_id,edi.vendor_code,A.storage_location_id "
                             " )", (wizard.buyer_id.id,today_str,wizard.buyer_id.id, wizard.buyer_id.id))
            domain = []
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.buyer_id:
                domain += [('buyer_id', '=', wizard.buyer_id.id)]
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]

            if wizard.storage_location_id:
                domain += [('storage_location_id', '=', wizard.storage_location_id.id)]
            print '*228:',wizard.buyer_id.id,',',today_str,',',wizard.buyer_id.id,',',wizard.buyer_id.id
            print '*229:',domain
            order_ids = self.env['iac.traw.data.vendor.list'].sudo().search(domain)
            print '*231:', order_ids

            # vals = {}
            # vals['buyer_id'] = wizard.buyer_id.id
            # print '*237:', order_ids,',',wizard.buyer_id.id
            # order_ids.write(vals)

            if not order_ids:
                raise UserError('查無資料! ')

            pv = []
            for pi in order_ids:
                pv.append(pi.id)

            action = {
                'name': _('Vendor Code List'),
                'type': 'ir.actions.act_window',
                'res_model': 'iac.traw.data.vendor.list',
                'view_mode': 'tree',
                'view_type': 'form',
                'act_window_id': self.env.ref('iac_forecast_release_to_vendor.action_vendor_code_list_form').id,
                'domain': [('id', 'in', pv)]
            }

        return action

class EDIVendorList(models.Model):
    _name = 'iac.edi.vendor.list'
    _description = "edi vendor list"

    # EDI的vendor list  資料來源：
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True) #廠商代碼
    partnername = fields.Char(string='partner_name')
    active =  fields.Char(string='active')
    vendor_code = fields.Char(string='vendor_code')
