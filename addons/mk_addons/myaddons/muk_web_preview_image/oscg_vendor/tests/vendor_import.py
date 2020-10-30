# -*- coding: utf-8 -*-

from odoo import fields
import erppeek
import xlrd
import logging
import traceback
import threading
import time

"""
导入vendor数据
"""

URL = 'http://localhost:8069'
DB = 'IAC_DB'
USERNAME = 'admin'
PASSWORD = 'admin'

class myThread (threading.Thread):
    def __init__(self, threadID, sheet, begin, end):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.sheet = sheet
        self.begin = begin
        self.end = end
    def run(self):
        logging.warn("Begin thread: %s @ %s" % (self.threadID, fields.Datetime.now()))
        import_vendor(self.sheet, self.begin, self.end)
        logging.warn("End thread: %s @ %s" % (self.threadID, fields.Datetime.now()))

"""
根据总数计算并返回需要的线程起止对
例如：[{'begin': 1, 'end': 100}, {'begin': 101, 'end': 200}, {'begin': 201, 'end': 300}, {'begin': 301, 'end': 400}, {'begin': 401, 'end': 500}]
"""
def calc_counter(total, step):
    thread_list = []
    counter = 1
    while (counter + step - 1 <= total):
        thread_list.append({'begin': counter, 'end': counter + step - 1})
        counter += step
    if counter <= total:
        thread_list.append({'begin': counter, 'end': total})

    return thread_list

def import_vendor(sheet, begin, end):
    api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    index = begin

    # 执行导入数据
    while index < end and index <= sheet.nrows - 1:
        int_plant_id = False
        int_vendor_reg_id = False
        int_currency_id = False
        int_country_id = False
        int_user_id = False
        int_payment_term_id = False
        int_incoterm_id = False

        if sheet.cell_value(index, 0):
            object_id = api.model('pur.org.data').get([('plant_code', '=', sheet.cell_value(index, 0))])
            if object_id:
                int_plant_id = object_id.id

        if sheet.cell_value(index, 2):
            object_id = api.model('iac.vendor.register').get(
                [('plant_id', '=', int_plant_id), ('vendor_code', '=', sheet.cell_value(index, 2))])
            if object_id:
                int_vendor_reg_id = object_id.id

        if sheet.cell_value(index, 4):
            object_id = api.model('res.users').get([('login', '=', sheet.cell_value(index, 4))])
            if object_id:
                int_user_id = object_id.id

        if sheet.cell_value(index, 7):
            object_id = api.model('payment.term').get([('payment_term', '=', sheet.cell_value(index, 7))])
            if object_id:
                int_payment_term_id = object_id.id

        if sheet.cell_value(index, 8):
            object_id = api.model('incoterm').get([('incoterm', '=', sheet.cell_value(index, 8))])
            if object_id:
                int_incoterm_id = object_id.id

        if sheet.cell_value(index, 9):
            object_id = api.model('res.country').get([('code', '=', sheet.cell_value(index, 9))])
            if object_id:
                int_country_id = object_id.id

        if sheet.cell_value(index, 53):
            object_id = api.model('res.currency').get([('name', '=', sheet.cell_value(index, 53))])
            if object_id:
                int_currency_id = object_id.id

        if int_user_id:
            if not int_vendor_reg_id:
                # 当缺少vendor register时新增vendor register资料
                vendor_reg_vals = {
                    'plant_id': int_plant_id,
                    'name1_cn': sheet.cell_value(index, 1),
                    'name2_cn': sheet.cell_value(index, 1),
                    'name1_en': sheet.cell_value(index, 1),
                    'name2_en': sheet.cell_value(index, 1),
                    'short_name': sheet.cell_value(index, 1),
                    'mother_name_en': sheet.cell_value(index, 1),
                    'vendor_code': sheet.cell_value(index, 2),
                    'buyer_email': sheet.cell_value(index, 3).lower(),
                    'delivery_hours': False,
                    'address_pobox': False,
                    'is_outerbuy': 'Y' if sheet.cell_value(index, 61) == 'foreign' else 'N',
                    'currency': int_currency_id,
                    'vat_number': sheet.cell_value(index, 14),
                    'address_country': int_country_id,
                    'mother_name_cn': sheet.cell_value(index, 1),
                    'shareholders': False,
                    'user_id': int_user_id,
                    'address_postalcode': False,
                    'web_site': False,
                    'address_street': False,
                    'factory_count': False,
                    'address_district': False,
                    'project_status': False,
                    'apply_memo': False,
                    'sales_mobile': False,
                    'sales_telephone': False,
                    'capital': False,
                    'use_project': False,
                    'supplier_category': False,
                    'company_telephone1': False,
                    'company_telephone2': False,
                    'corporation_description': False,
                    'supplier_description': False,
                    'conglomerate': False,
                    'applyfile_id': False,
                    'supplier_type': False,
                    'reason_one': False,
                    'state': sheet.cell_value(index, 12),
                    'address_city': False,
                    'sales_email': 'zhang.pei-wu@iac.com.tw',
                    'company_fax': False,
                    'license_number': False,
                    'mother_address_en': False,
                    'is_scene': False,
                    'mother_address_cn': False,
                    'contact_person': False,
                    'material_use_range': False,
                    'duns_number': False,
                    'other_emails': '',
                    'message_last_post': False if sheet.cell_value(index, 71) == '' else sheet.cell_value(index,
                                                                                                          71),
                    'employee_number': False,
                    'reject_reason': False,
                    'comment': False
                }
                vendor_reg_id = api.model('iac.vendor.register').create(vendor_reg_vals)
                int_vendor_reg_id = vendor_reg_id.id

            vendor_vals = {
                'plant': int_plant_id,
                'vendor_reg_id': int_vendor_reg_id,
                'name': sheet.cell_value(index, 1),
                'vendor_code': sheet.cell_value(index, 2),
                'buyer_email': sheet.cell_value(index, 3).lower(),
                'user_id': int_user_id,
                'bank_name': sheet.cell_value(index, 5),
                'branch_name': sheet.cell_value(index, 6),
                'payment_term': int_payment_term_id,
                'incoterm': int_incoterm_id,
                'bank_country': int_country_id,
                'bank_city': sheet.cell_value(index, 10),
                'bank_street': sheet.cell_value(index, 11),
                'state': sheet.cell_value(index, 12),
                'spotflag': sheet.cell_value(index, 13),
                'vat_reg_no': sheet.cell_value(index, 14),
                'sh_import_flag': sheet.cell_value(index, 15),
                'show_in': sheet.cell_value(index, 16),
                'parent_id': sheet.cell_value(index, 17),
                'vendor_title': sheet.cell_value(index, 18),
                'finance': sheet.cell_value(index, 19),
                'z_confirmation_control': sheet.cell_value(index, 20),
                'payment_block': sheet.cell_value(index, 21),
                'ship_code': sheet.cell_value(index, 22),
                'vendor_group': sheet.cell_value(index, 23),
                'creation_date': False if sheet.cell_value(index, 24) == '' else sheet.cell_value(index, 24).replace('/', '-'),
                'vendor_quality_rating': sheet.cell_value(index, 25),
                'swift_code': sheet.cell_value(index, 26),
                'purchase_contract': sheet.cell_value(index, 27),
                'vendor_site_id_1': sheet.cell_value(index, 28),
                'reason': sheet.cell_value(index, 29),
                'z_fob2': sheet.cell_value(index, 30),
                'transfer_number': sheet.cell_value(index, 31),
                'vmi_due_in_weeks': sheet.cell_value(index, 32),
                'vendor_sap_status': sheet.cell_value(index, 33),
                'sap_vendor_cert_id': sheet.cell_value(index, 34),
                'probity_agreement': sheet.cell_value(index, 35),
                'vmi_due': sheet.cell_value(index, 36),
                'si_supplier': sheet.cell_value(index, 37),
                'destination': sheet.cell_value(index, 38),
                'real_online': sheet.cell_value(index, 39),
                'vmi_supplier': 'yes' if sheet.cell_value(index, 40) == 'Y' else 'no',
                'z_buyer_erp_id': sheet.cell_value(index, 41),
                'language_key': sheet.cell_value(index, 42),
                'it_level': sheet.cell_value(index, 43),
                'vendor_account_group': sheet.cell_value(index, 44),
                'last_si_no': sheet.cell_value(index, 45),
                'sort_field': sheet.cell_value(index, 46),
                'last_asn_no': sheet.cell_value(index, 47),
                'last_asn_no_sec': sheet.cell_value(index, 48),
                'si_flag': sheet.cell_value(index, 49),
                'z_fob': sheet.cell_value(index, 50),
                'z_terms_code': sheet.cell_value(index, 51),
                'vendor_url': sheet.cell_value(index, 52),
                'currency': int_currency_id,
                'erp_system_id': sheet.cell_value(index, 54),
                'purchasing_block': sheet.cell_value(index, 55),
                'order_currency': sheet.cell_value(index, 56),
                'vmi_enabled': sheet.cell_value(index, 57),
                'partner_bank_type': sheet.cell_value(index, 58),
                'current_class': sheet.cell_value(index, 59),
                'vendor_delivery_rating': sheet.cell_value(index, 60),
                'local_foreign': sheet.cell_value(index, 61),
                'z_eval_receipt_stlmt': sheet.cell_value(index, 62),
                'rma_terms': False if sheet.cell_value(index, 63) == '' else sheet.cell_value(index, 63),
                'last_update_date': False if sheet.cell_value(index, 64) == '' else sheet.cell_value(index, 64).replace('/', '-'),
                'vendor_property': sheet.cell_value(index, 65),
                'vendor_type': sheet.cell_value(index, 66),
                'import_required': 'yes' if sheet.cell_value(index, 67) == 'Y' else 'no',
                'account_number': sheet.cell_value(index, 68),
                'vendor_site_id': sheet.cell_value(index, 69),
                'class_date': False if sheet.cell_value(index, 70) == '' else sheet.cell_value(index, 70).replace('/', '-'),
                'message_last_post': False if sheet.cell_value(index, 71) == '' else sheet.cell_value(index, 71)
            }
            try:
                object_id = False
                object_ids = api.model('iac.vendor').browse([('plant', '=', int_plant_id),
                                                         ('vendor_code', '=', sheet.cell_value(index, 2))])
                for record in object_ids:
                    object_id = record
                    break

                if object_id:
                    object_id.write(vendor_vals)
                else:
                    object_id = api.model('iac.vendor').create(vendor_vals)
                    object_id.vendor_reg_id.vendor_id = object_id.id
                logging.warn(u'第 %s 个vendor 处理 %s 成功。vendor_id=%s' % (index, object_id.vendor_code, object_id.id))
            except:
                traceback.print_exc()
                logging.warn(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 2)))
        else:
            logging.warn(u'No.%s 行user login %s 为空，跳过vendor，vendor_code=%s' % (index, sheet.cell_value(index, 4), sheet.cell_value(index, 2)))

        index += 1

    logging.warn(u'成功处理 %s 个vendor' % (end - begin + 1))

if __name__ == "__main__":
    workbook = xlrd.open_workbook('d:/temp/vendor.xls')
    sheet = workbook.sheet_by_name('Sheet1')

    thread_list = calc_counter(sheet.nrows - 1, 500)
    index = 1
    for item in thread_list:
        thread = myThread("Thread-%s" % (index), sheet, item['begin'], item['end'])
        thread.start()
        index += 1