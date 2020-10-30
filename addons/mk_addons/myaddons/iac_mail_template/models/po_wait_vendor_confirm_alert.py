# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from datetime import datetime, timedelta
import traceback
from odoo.odoo_env import odoo_env


class PoWaitVendorConfirmAlert(models.Model):
    _name = 'po.wait.vendor.confirm.alert'
    _order = 'id desc'

    def _mail_alert_vendor_confirm_pos(self,sql_string,po_type):
        """
        给不同的类型的po_comfirm调用
        :param sql_string:
        :param po_type:
        :return:
        """
        self._cr.execute(sql_string)
        po_results = self._cr.dictfetchall()
        vendor_email_list = []
        for po_res in po_results:
            # 得到所有的vendor and email 列表
            # 只有查出来的资料vendor_code和email不为空的时候才会塞进这个list里面，才会发邮件
            if po_res['vendor'] and po_res['other_emails'] and [po_res['vendor'], po_res['other_emails']] not in vendor_email_list:
                vendor_email_list.append([po_res['vendor'], po_res['other_emails']])
        # 对vendor_email_list去重
        # vendor_email_list_single = set(vendor_email_list)
        # vendor_email_list_single = filter(lambda r:vendor_email_list.count(r) == 1,vendor_email_list)
        # 根据vendor分组发送邮件
        for vendor, email in vendor_email_list:
            body_lists = []
            for po_single in po_results:
                if po_single['vendor'] == vendor and po_single['other_emails'] == email:
                    vm_partno_lambda = lambda r: r if r not in (False, None) else ''
                    if po_type == 'new_po':
                        body_list = [str(po_single['plant']), str(po_single['po']), str(po_single['item']),
                                     vm_partno_lambda(po_single['part_no']),vm_partno_lambda(po_single['vendor_part_no']),
                                     vm_partno_lambda(po_single['manufacturer_part_no']),str(po_single['quantity']), str(po_single['price']),
                                     str(po_single['delivery_date']),str(po_single['storage_location']), str(po_single['buyer_name'])]
                        mail_subject = '[NO REPLY] Please log on IAC Supplier Portal to confirm your new POs'
                        header_list = ['Plant', 'Po#', 'Item', 'part_no', 'Vendor_part_no','Manufacturer_part_no',
                                       'Quantity', 'Price', 'Delivery_Date','Storage_Location', 'Buyer_Name']
                    else:
                        body_list = [po_single['plant'], po_single['po'], po_single['item'],po_single['part_no'],
                                     vm_partno_lambda(po_single['vendor_part_no']),vm_partno_lambda(po_single['manufacturer_part_no']),
                                     str(po_single['last_qty']), str(po_single['new_qty']),str(po_single['last_price']),
                                     str(po_single['new_price']), po_single['storage_location'],po_single['buyer_name']]
                        mail_subject = '[NO REPLY] Please log on IAC Supplier Portal to confirm your changed POs'
                        header_list = ['Plant', 'Po#', 'Item', 'part_no', 'Vendor_part_no','Manufacturer_part_no',
                                       'Last_qty', 'New_qty', 'Last_price', 'New_price','Storage_Location', 'Buyer_Name']
                    body_lists.append(body_list)

            # 调用通用的发送邮件的方法
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", mail_subject,header_list,
                                                      body_lists,"Po Confirm Mail Alert")


    @odoo_env
    @api.model
    def job_alert_change_po_vendor_confirm(self):

        # 查询到持续vendor未confirm的change po
        sql_string = """ select po.changed as changed,
                               mm.part_no as part_no,
                               vr.sales_email as vendor_email,
                               vr.other_emails as other_emails,
                               pod.plant_code as plant,
                               v.vendor_code as vendor,
                               po.document_erp_id as po,
                               pol.order_line_code as item,
                               pol.vendor_part_no,
                               pol.manufacturer_part_no,
                               polc.ori_price as last_price,
                               polc.new_price,       
                               polc.ori_qty as last_qty,
                               polc.new_qty,       
                               polc.ori_deletion_flag as last_deletion_flag,
                               polc.deletion_flag as new_deletion_flag,
                               bc.buyer_name,
                               pol.storage_location
                          from iac_purchase_order po
                            inner join iac_purchase_order_line pol on pol.order_id = po.id
                            inner join pur_org_data pod on pod.id = po.plant_id
                            inner join iac_vendor v on v.id = po.vendor_id
                                                    and v.state = 'done'
                            inner join material_master mm on mm.id = pol.part_id
                            inner join buyer_code bc on bc.id = po.buyer_id
                            inner join iac_purchase_order_line_change polc on polc.id = pol.last_order_line_change_id
                            inner join iac_vendor_register vr on vr.id = v.vendor_reg_id
                            inner join iac_vendor_account_group vg on vg.account_group = v.vendor_account_group
                                                                   and vg.vendor_type = 'normal'
                        where po.state = 'wait_vendor_confirm' 
                          and po.changed = 't'
                        order by plant, vendor, po,item """
        # 调用公用方法发邮件
        self._mail_alert_vendor_confirm_pos(sql_string,'change_po')

    @odoo_env
    @api.model
    def job_alert_new_po_vendor_confirm(self):
        # 找到持续未confirm的new po
        sql_string = """ select po.changed as changed,
                               mm.part_no as part_no,
                               vr.sales_email as vendor_email,
                               vr.other_emails as other_emails,
                               pod.plant_code as plant,
                               v.vendor_code as vendor,
                               po.document_erp_id as po,
                               pol.order_line_code as item,
                               pol.vendor_part_no,
                               pol.manufacturer_part_no,
                               pol.quantity as quantity,
                               pol.price as price,
                               pol.delivery_date as delivery_date,
                               bc.buyer_name,
                               pol.storage_location
                          from iac_purchase_order po
                            inner join iac_purchase_order_line pol on pol.order_id = po.id
                            inner join pur_org_data pod on pod.id = po.plant_id
                            inner join iac_vendor v on v.id = po.vendor_id
                                                    and v.state = 'done'
                            inner join material_master mm on mm.id = pol.part_id
                            inner join buyer_code bc on bc.id = po.buyer_id
                            inner join iac_vendor_register vr on vr.id = v.vendor_reg_id
                            inner join iac_vendor_account_group vg on vg.account_group = v.vendor_account_group
                                                                   and vg.vendor_type = 'normal'
                        where po.state = 'wait_vendor_confirm' 
                          and po.changed is null
                        order by plant, vendor, po,item """
        # 调用公用方法发邮件
        self._mail_alert_vendor_confirm_pos(sql_string, 'new_po')

            # """ 暂时废弃以下代码，为保后续需求又改变，不删除代码 """
                    # if i == 1:
                    #     vendor_email.append(new_po_single['vendor_email'])
                    #     vendor_email.append(new_po_single['other_emails'])
                    #     i += 1
            # 对vendor_email去重并且去None
            # vendor_email_single = set(vendor_email)
            # vendor_email_none = vendor_email_single.remove(None)
            # finn_vendor_email = vendor_email_none.remove('')
            # finn_email_list = filter(lambda r: r not in (None, ''), vendor_email_single)

            # 如果系统内查询不到vendor_email，就把邮件发给负责这家厂商的buyer
            # if len(finn_email_list) == 0:
                # email = body_lists[0][-1]
                # 取出body_list里面所有buyer_name,再去重
                # buyer_list = []
                # buy_email_list = []
                # for body in body_lists:
                #     buyer_list.append(body[-1])
                # buyer_list_single = set(buyer_list)
                # 查询去重后的buyer对应的buyer_email
                # for buyer_name in buyer_list_single:
                #     buyer_obj = self.env['buyer.code'].search([('buyer_name','=',buyer_name)],limit=1)
                #     user_obj = self.env['res.users'].search([('login', '=', buyer_obj.buyer_ad_account)])
                #     partner_obj = self.env['res.partner'].search([('id', '=', user_obj.partner_id.id)])
                #     buy_email_list.append(partner_obj.email)
                #
                # buy_email_lambda = filter(lambda r: r if r not in (False,None) else '',buy_email_list)
                # if len(buy_email_lambda) != 0:
                #     email = ';'.join(buy_email_lambda)
                #     mail_subject = '系统无法获取vendor(%s)的邮箱，请buyer联系该厂商Confirm以下New POs' % vendor
            #     else:
            #         email = 'Zhang.Pei-Wu@iac.com.tw' + ';' + 'Wang.Ningg@iac.com.tw' \
            #              + ';' + 'jiang.shier@iac.com.tw' + ';' + 'li.zhen@iac.com.tw'
            #         mail_subject = '系统无法获取vendor(%s)以及buyer的邮箱，请buyer联系该厂商Confirm以下New POs' % vendor
            # else:
            #     email = ';'.join(finn_email_list)
            #     # email = ';'.join(vendor_email)
            #     mail_subject = '[Odoo Alert] IAC New POs are waiting for your confirmation'

            # 调用通用的发送邮件的方法
            # self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", mail_subject,
            #                                           ['Plant', 'Po#', 'Item', 'part_no', 'Vendor_part_no',
            #                                            'Manufacturer_part_no','Quantity', 'Price', 'Delivery_Date',
            #                                            'Storage_Location', 'Buyer_Name'], body_lists,
            #                                           "Daily PO New Mail Alert")






