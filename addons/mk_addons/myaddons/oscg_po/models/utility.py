# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
import datetime
_logger = logging.getLogger(__name__)


def po_mail_to_vendor(self,lines,po_type):
    """
    new_po和change_po完成时调用此函数给vendor发邮件
    :param self:
    :param po_obj:
    :param field_str:
    :param po_type:
    :return:
    """
    # 因为po执行起来效率就比较慢，如果用(select * from iac_vendor
    #                        where vendor_account_group
    #   in (select account_group from  iac_vendor_account_group where vendor_type = 'normal')
    #        and state = 'done')
    # 查出所有的normal厂商塞进一个list，然后再判断此笔po的厂商在不在这个list里面，有点耗时
    # 所以还是采用直接判断此厂商是不是normal的方式

    vendor_type_list = []
    vendor_account_groups = self.env['iac.vendor.account.group'].search([('vendor_type', '=', 'normal')])
    for vendor_group in vendor_account_groups:
        vendor_type_list.append(vendor_group.account_group)
    vendor_obj = self.env['iac.vendor'].search([('id', '=', self.vendor_id.id),
                                               ('state', '=', 'done')])
    if vendor_obj and vendor_obj.vendor_account_group in vendor_type_list:
        vendor_reg_obj = self.env['iac.vendor.register'].browse(vendor_obj.vendor_reg_id.id)
        # 如果能找到other_emails就发邮件，找不到就不发
        if vendor_reg_obj.sudo().other_emails not in (False, ''):
            body_lists = []
            for order_line in lines:
                v_partno_lambda = lambda r: r if r != False else ''
                if po_type == 'change_po':
                    body_list = [self.plant_id.plant_code, order_line.order_code,order_line.order_line_code,
                                 order_line.part_id.part_no, v_partno_lambda(order_line.vendor_part_no),
                                 str(order_line.ori_qty),str(order_line.new_qty), str(order_line.ori_price),
                                 str(order_line.new_price),v_partno_lambda(order_line.storage_location),
                                 v_partno_lambda(self.buyer_id.buyer_name)]
                    mail_subject = '[NO REPLY] Please log on IAC Supplier Portal to confirm your changed POs'
                    header_list = ['Plant', 'PO#', 'Item', 'Part No', 'Vendor Part No','Last QTY', 'New QTY',
                                    'Last Price', 'New Price','Storage Location', 'Buyer Name']
                else:
                    body_list = [order_line.plant_id.plant_code, order_line.document_erp_id,order_line.document_line_erp_id,
                                 order_line.part_no, v_partno_lambda(order_line.vendor_part_no),
                                 v_partno_lambda(order_line.manufacturer_part_no),str(order_line.quantity), str(order_line.price),
                                 order_line.delivery_date,v_partno_lambda(order_line.storage_location),v_partno_lambda(order_line.buyer_id.buyer_name)]
                    header_list = ['Plant', 'PO#', 'Item', 'Part No', 'Vendor Part No', 'Manufacturer Part No', 'QTY', 'Price',
                                    'Delivery Date', 'Storage Location', 'Buyer Name']
                    mail_subject = '[NO REPLY] Please log on IAC Supplier Portal to confirm your new POs'
                body_lists.append(body_list)
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', vendor_reg_obj.sudo().other_emails,"",mail_subject,
                                                      header_list,body_lists, "Po Mail Alert")