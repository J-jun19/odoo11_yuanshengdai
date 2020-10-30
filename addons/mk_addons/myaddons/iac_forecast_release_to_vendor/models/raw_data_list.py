# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


#专用来  buyer.code 模型 限定 只能看到 自己的 buyer_code 筛选规则,专门用在 FCST 相关表中
#专用来  buyer.code 模型 限定 只能看到 自己的 buyer_code 筛选规则,专门用在 FCST 相关表中
class BuyerCodeFCST(models.Model):
    _inherit="buyer.code"
    _name='buyer.code.fcst'
    _table='buyer_code'
    _description = u"Buyer Code"

#专用来避免iac.vendor 模型应用buyer_email筛选规则,专门用在 FCST 相关表中
class IacVendorFCST(models.Model):
    _inherit="iac.vendor"
    _name='iac.vendor.fcst'
    _table='iac_vendor'
    _description = u"Vendor Info"


class RawData(models.Model):
    _name = 'iac.traw.data'
    _description = "traw data"
    _order = 'alt_grp,alt_grp_sort desc'

    fpversion = fields.Char(string="FP Version", required=True,index=True) #fpver
    plant_id = fields.Many2one('pur.org.data', string="Plant",index=True)
    plant_code = fields.Char(string='Plant', related='plant_id.plant_code')

    #'Plant'
    buyer_id = fields.Many2one('buyer.code', string="採購代碼", index=True)
    buyer_code = fields.Char(string="buyer_code", related="buyer_id.buyer_erp_id")
    vendor_id = fields.Many2one('iac.vendor', string="廠商代碼",index=True )
    vendor_code = fields.Char(string="Vendor_code",  related="vendor_id.vendor_code")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration",index=True)
    vendor_name = fields.Char(string='vendor name')
    vendor_name_cn = fields.Char(string='vendor name cn', related='vendor_id.name')
    material_id = fields.Many2one('material.master', 'Material', index=True)
    material_code = fields.Char(string='Material_code',related='material_id.part_no')
    division_id = fields.Many2one('division.code', string='Division',index=True)
    division_code = fields.Char(string='Division_code',related='division_id.division')
    description = fields.Char(string="品名")
    alt_grp = fields.Char(string="Alternate Group",index=True) # 20180706 因為 search條件,所以須加上 index,以加快速度
    alt_flag = fields.Char(string="是否替代料") #是否替代料
    stock = fields.Float(string='庫存量')
    open_po = fields.Float(string='total open po qty')
    intransit_qty = fields.Float(string='在途量')
    quota = fields.Float(string='配額') #配額
    round_value = fields.Float(string='Round value')
    leadtime = fields.Integer(string="L/T")
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

    tconfirm_version_id = fields.One2many('iac.tconfirm.version', 'raw_id', string="tconfirm version id",index=True)
    need_re_update = fields.Integer()
    need_update_id = fields.Integer()
    plant_ori = fields.Char(index=True)
    material_ori = fields.Char(index=True)
    vendor_ori = fields.Char(index=True)
    buyer_ori = fields.Char(index=True)
    division_ori = fields.Char(index=True)
    sap_log_id = fields.Char(string="Sap log Info", index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info", index=True)

    raw_temp_ids = fields.One2many("iac.traw.data.temp", "raw_id", string="raw_ids", index=True)
    fcst_status = fields.Char(string='數量確認', compute='_get_fcst_status') # FCST回覆狀態

    alt_grp_sort = fields.Char()  # 用來進行代用料排序判斷
    state = fields.Selection(selection=[('0', '隱藏'), ('1', '顯示'), ], default='0', )  # 删除标记  #用來判斷按鈕的顯示或者隱藏 # state='1'藍色字&可以點按鈕, 0 黑色字&不能點update按鈕
    storage_location_id = fields.Many2one('iac.storage.location.address',string='Storage Location') #181211 ning add
    storage_location = fields.Char()

    def _get_fcst_status(self):
        # 抓  raw_data_temp 中 '數量確認' 'FCST回覆狀態'。 若 raw_data_temp.status =  T: true有效 or   D: done已發出 ->已回覆過FCST
        for rawid in self:

            traw_temp_exist = self.env['iac.traw.data.temp'].sudo().search([
                ('raw_id', '=', rawid.id ),('status', 'in', ("T","D"))])
            if traw_temp_exist:
                # print '*99 :', rawid.id
                rawid.fcst_status = 'Y'
            else:
                # print '*102 :', rawid.id
                rawid.fcst_status = 'N'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        qty_w1_r = ''
        # 動態field_name：將 file name 改為從 DB select ( iac_tcolumn_title ) 出來
        self._cr.execute( " select fpversion,qty_w1_r, qty_w2,qty_w3,qty_w4,qty_w5,"
                          "qty_w6,qty_w7,qty_w8,qty_w9,qty_w10,"
                          "qty_w11,qty_w12,qty_w13,"
                          "qty_m1,qty_m2,qty_m3,qty_m4,qty_m5,qty_m6,"
                          "qty_m7,qty_m8,qty_m9 "
                          "from iac_tcolumn_title "
                          "where fpversion in ( select max (fpversion) from iac_traw_data ) ")
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
            print '*130'
            raise exceptions.ValidationError('錯誤!  基本資料沒維護 ( iac_tcolumn_title) raw_data_list.py')
        else:
            print '*133'
            tree_view_id = self.env['ir.model.data'].xmlid_to_res_id('iac_forecast_release_to_vendor.view_raw_data_tree_2')
            open_form_view_id = self.env['ir.model.data'].xmlid_to_res_id('iac_forecast_release_to_vendor.raw_data_open_form')

            res = super(RawData, self).fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)

            #  if self.env.cr.dictfetchall() : 有值才帶動態欄位
            if self.env.cr.dictfetchall() and ( view_id == tree_view_id or view_id == open_form_view_id ) :
                print ' 123 :', fpversion
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
            return res

    @api.multi
    def button_to_all_release(self):
        # Send to Release 的 button
        """  Send to 待Release 整批拋到待release：直接將 iac_traw_data 寫入iac_traw_data_temp and status=T """
        sum=0
        # 逐筆 copy RawData 到 RawDataTemp ：

        for item in self.ids:

            ori_raw_data = self.env['iac.traw.data'].sudo().browse(item)
            print '*210:', item, ',', ori_raw_data.fcst_status, ',', ori_raw_data.fpversion

            # 不是該buyer_code的跳過不處理 20180705 laura add
            if ori_raw_data.buyer_id.id in self.env.user.buyer_id_list:
                #print '*216: ',self.env.user.buyer_id_list,',',ori_raw_data.buyer_id.id

                if ori_raw_data.fcst_status=='Y':
                    sum=sum+1

                raw_data_temp_val = {
                    'status': 'T',  # T: true有效,F:  false無效,D: done已發出
                    'buyer_id': ori_raw_data.buyer_id.id,
                    'raw_id': ori_raw_data.id,
                    'division_id': ori_raw_data.division_id.id,
                    'material_id': ori_raw_data.material_id.id,
                    'plant_id': ori_raw_data.plant_id.id,
                    'vendor_id': ori_raw_data.vendor_id.id,
                    'vendor_reg_id': ori_raw_data.vendor_reg_id.id,
                    'alt_flag': ori_raw_data.alt_flag,
                    'alt_grp': ori_raw_data.alt_grp,
                    'b001': ori_raw_data.b001,
                    'b002': ori_raw_data.b002,
                    'b004': ori_raw_data.b004,
                    'b005': ori_raw_data.b005,
                    'b012': ori_raw_data.b012,
                    'b017b': ori_raw_data.b017b,
                    'b902q': ori_raw_data.b902q,
                    'b902s': ori_raw_data.b902s,
                    'creation_date': ori_raw_data.creation_date,
                    'custpn_info': ori_raw_data.custpn_info,
                    'description': ori_raw_data.description,
                    'flag': ori_raw_data.flag,
                    'fpversion': ori_raw_data.fpversion,
                    'intransit_qty': ori_raw_data.intransit_qty,
                    'leadtime': ori_raw_data.leadtime,
                    'max_surplus_qty': ori_raw_data.max_surplus_qty,
                    'mfgpn_info': ori_raw_data.mfgpn_info,
                    'mquota_flag': ori_raw_data.mquota_flag,
                    'open_po': ori_raw_data.open_po,
                    'po': ori_raw_data.po,
                    'pr': ori_raw_data.pr,
                    'qty_m1': ori_raw_data.qty_m1,
                    'qty_m2': ori_raw_data.qty_m2,
                    'qty_m3': ori_raw_data.qty_m3,
                    'qty_m4': ori_raw_data.qty_m4,
                    'qty_m5': ori_raw_data.qty_m5,
                    'qty_m6': ori_raw_data.qty_m6,
                    'qty_m7': ori_raw_data.qty_m7,
                    'qty_m8': ori_raw_data.qty_m8,
                    'qty_m9': ori_raw_data.qty_m9,
                    'qty_w1': ori_raw_data.qty_w1,
                    'qty_w1_r': ori_raw_data.qty_w1_r,
                    'qty_w10': ori_raw_data.qty_w10,
                    'qty_w11': ori_raw_data.qty_w11,
                    'qty_w12': ori_raw_data.qty_w12,
                    'qty_w13': ori_raw_data.qty_w13,
                    'qty_w2': ori_raw_data.qty_w2,
                    'qty_w3': ori_raw_data.qty_w3,
                    'qty_w4': ori_raw_data.qty_w4,
                    'qty_w5': ori_raw_data.qty_w5,
                    'qty_w6': ori_raw_data.qty_w6,
                    'qty_w7': ori_raw_data.qty_w7,
                    'qty_w8': ori_raw_data.qty_w8,
                    'qty_w9': ori_raw_data.qty_w9,
                    'quota': ori_raw_data.quota,
                    'remark': ori_raw_data.remark,
                    'round_value': ori_raw_data.round_value,
                    'stock': ori_raw_data.stock,
                    'vendor_name': ori_raw_data.vendor_name,
                    'storage_location_id':ori_raw_data.storage_location_id.id
                }
                record = self.env['iac.traw.data.temp'].sudo().create(raw_data_temp_val)

                uid =  self._uid

                print '*272:', uid ,', ', self._uid  ,', ', record.create_uid
                # uid =  8
                print '*275:', uid, ', ', self._uid,', ', record.create_uid

                record._cr.execute("update iac_traw_data_temp  set create_uid = %s ,write_uid= %s "
                                 "where id = %s",
                                 (uid, uid, record.id))
                record.env.cr.commit()
                print '*280:', uid, ', ', self._uid, ', ', record.create_uid, ', ',record.id
                # print '*275:', item, ', ', raw_data_temp_val

                print '*294:', sum
        if sum >= 1:
            return self.env['warning_box'].info(title="send to release", message=u'send to release成功。 注意：請檢查資料，有些材料已經修改過數量！')

    @api.multi

    def method_name(self):
        # Update : 更改數量 update iac.traw.data.temp  (iac.traw.data還是原始資料) ,
        # 此 open form 帶出的是 iac.traw.data.temp 被改過數量的資料

        print '*304:', self.buyer_id.id, ',', self.env.user.buyer_id_list
        # 不是該buyer_code的跳過不處理,且秀error msg  20180713 laura add
        if self.buyer_id.id not in self.env.user.buyer_id_list:
            raise exceptions.ValidationError("此料非所屬buyer_code,不能進行修改數量! ")
        else:
            # 先 copy RawData 到 RawDataTemp
            for item in self.ids:
                ori_raw_data = self.env['iac.traw.data'].sudo().browse(item)

                raw_data_temp_val = {
                    'status': '', # T: true有效,F:  false無效,D: done已發出
                    'buyer_id': ori_raw_data.buyer_id.id,
                    'raw_id': ori_raw_data.id,
                    'division_id': ori_raw_data.division_id.id,
                    'material_id': ori_raw_data.material_id.id,
                    'plant_id': ori_raw_data.plant_id.id,
                    'vendor_id': ori_raw_data.vendor_id.id,
                    'vendor_reg_id': ori_raw_data.vendor_reg_id.id,
                    'alt_flag': ori_raw_data.alt_flag,
                    'alt_grp': ori_raw_data.alt_grp,
                    'b001': ori_raw_data.b001,
                    'b002': ori_raw_data.b002,
                    'b004': ori_raw_data.b004,
                    'b005': ori_raw_data.b005,
                    'b012': ori_raw_data.b012,
                    'b017b': ori_raw_data.b017b,
                    'b902q': ori_raw_data.b902q,
                    'b902s': ori_raw_data.b902s,
                    'creation_date': ori_raw_data.creation_date,
                    'custpn_info': ori_raw_data.custpn_info,
                    'description': ori_raw_data.description,
                    'flag': ori_raw_data.flag,
                    'fpversion': ori_raw_data.fpversion,
                    'intransit_qty': ori_raw_data.intransit_qty,
                    'leadtime': ori_raw_data.leadtime,
                    'max_surplus_qty': ori_raw_data.max_surplus_qty,
                    'mfgpn_info': ori_raw_data.mfgpn_info,
                    'mquota_flag': ori_raw_data.mquota_flag,
                    'open_po': ori_raw_data.open_po,
                    'po': ori_raw_data.po,
                    'pr': ori_raw_data.pr,
                    'qty_m1': ori_raw_data.qty_m1,
                    'qty_m2': ori_raw_data.qty_m2,
                    'qty_m3': ori_raw_data.qty_m3,
                    'qty_m4': ori_raw_data.qty_m4,
                    'qty_m5': ori_raw_data.qty_m5,
                    'qty_m6': ori_raw_data.qty_m6,
                    'qty_m7': ori_raw_data.qty_m7,
                    'qty_m8': ori_raw_data.qty_m8,
                    'qty_m9': ori_raw_data.qty_m9,
                    'qty_w1': ori_raw_data.qty_w1,
                    'qty_w1_r': ori_raw_data.qty_w1_r,
                    'qty_w10': ori_raw_data.qty_w10,
                    'qty_w11': ori_raw_data.qty_w11,
                    'qty_w12': ori_raw_data.qty_w12,
                    'qty_w13': ori_raw_data.qty_w13,
                    'qty_w2': ori_raw_data.qty_w2,
                    'qty_w3': ori_raw_data.qty_w3,
                    'qty_w4': ori_raw_data.qty_w4,
                    'qty_w5': ori_raw_data.qty_w5,
                    'qty_w6': ori_raw_data.qty_w6,
                    'qty_w7': ori_raw_data.qty_w7,
                    'qty_w8': ori_raw_data.qty_w8,
                    'qty_w9': ori_raw_data.qty_w9,
                    'quota': ori_raw_data.quota,
                    'remark': ori_raw_data.remark,
                    'round_value': ori_raw_data.round_value,
                    'stock': ori_raw_data.stock,
                    'vendor_name': ori_raw_data.vendor_name,
                    'storage_location_id':ori_raw_data.storage_location_id.id
                }
                record = self.env['iac.traw.data.temp'].sudo().create(raw_data_temp_val)

            # 再把 RawDataTemp 的值帶出來
            res = {
                'name': 'raw data open form',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env['ir.model.data'].xmlid_to_res_id(
                    'iac_forecast_release_to_vendor.raw_data_open_form'),
                'res_model': 'iac.traw.data.temp',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': record.id
            }
            return res

class IacTrawDataBK(models.Model):

    _name = 'iac.traw.data.bk'
    _inherit = 'iac.traw.data'


