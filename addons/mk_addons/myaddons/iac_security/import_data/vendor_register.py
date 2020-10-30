# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
import xlrd
import erppeek
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)

# 定时任务
class IacVendorRegImport(models.TransientModel):
    _name = 'iac.vendor.reg.import'
    _description = 'Vendor Reg Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        """
       1.跳过user login不存在的记录；
       2.如果name1_cn，name2_cn，name1_en，name2_en为空，根据user_id从已经存在的资料中查找栏位补充到当前记录上；
       3.如果vendor_code已经存在则write，否则create
       """

        index = begin

        while index <= end and index <= sheet.nrows - 1:
            int_plant_id = False
            int_currency_id = False
            int_country_id = False
            int_user_id = False
            int_reason_id = False



            if sheet.cell_value(index, 17):
                #object_id = api.model('res.users').get([('login', '=', sheet.cell_value(index, 17))])
                #if object_id:
                #    int_user_id = object_id.id
                object_id=self.env["res.users"].search([('login', '=', sheet.cell_value(index, 17))],limit=1,order='id desc')
                if object_id.exists():
                    int_user_id = object_id.id

            if sheet.cell_value(index, 0):
                #object_id = api.model('pur.org.data').get([('plant_code', '=', sheet.cell_value(index, 0))])
                #int_plant_id = object_id.id
                object_id=self.env["pur.org.data"].search([('plant_code', '=', sheet.cell_value(index, 0))],limit=1,order='id desc')
                if object_id.exists():
                    int_plant_id = object_id.id

            if sheet.cell_value(index, 12):
                #object_id = api.model('res.currency').get([('name', '=', sheet.cell_value(index, 12))])
                #if object_id:
                #    int_currency_id = object_id.id
                object_id=self.env["res.currency"].search([('name', '=', sheet.cell_value(index, 12))],limit=1,order='id desc')
                if object_id.exists():
                    int_currency_id = object_id.id

            if sheet.cell_value(index, 14):
                #object_id = api.model('res.country').get([('name', '=', sheet.cell_value(index, 14))])
                #if object_id:
                #    int_country_id = object_id.id
                object_id=self.env["res.country"].search([('name', '=', sheet.cell_value(index, 14))],limit=1,order='id desc')
                if object_id.exists():
                    int_country_id = object_id.id

            if sheet.cell_value(index, 37):
                #object_id = api.model('iac.vendor.reason').get([('name', '=', sheet.cell_value(index, 37))])
                #if object_id:
                #    int_reason_id = object_id.id
                object_id=self.env["iac.vendor.reason"].search([('name', '=', sheet.cell_value(index, 37))],limit=1,order='id desc')
                if object_id.exists():
                    int_reason_id = object_id.id

            # 对缺少很多栏位的资料根据user login查询已经导入过的资料，如果找到历史资料，将历史资料的栏位赋值给新的资料
            if sheet.cell_value(index, 1) == '' and sheet.cell_value(index, 2) == '' \
                    and sheet.cell_value(index, 3) == '' and sheet.cell_value(index, 4) == '' \
                    and sheet.cell_value(index, 5) == '' and sheet.cell_value(index, 6) == '':
                exists_vendor_id = False

                #exists_vendor_ids = api.model('iac.vendor.register').browse([('user_id', '=', int_user_id)])
                exists_vendor_ids=self.env["iac.vendor.register"].search([('user_id', '=', int_user_id)])
                for record in exists_vendor_ids:
                    if record.name1_cn and record.name1_cn != '':
                        exists_vendor_id = record
                        break
                if exists_vendor_id and exists_vendor_id.name1_cn and exists_vendor_id.name1_en:
                    vendor_reg_vals = {
                        'plant_id': int_plant_id,
                        'name1_cn': exists_vendor_id.name1_cn,
                        'name2_cn': exists_vendor_id.name2_cn,
                        'name1_en': exists_vendor_id.name1_en,
                        'name2_en': exists_vendor_id.name2_en,
                        'short_name': exists_vendor_id.short_name,
                        'mother_name_en': exists_vendor_id.mother_name_en,
                        'vendor_code': sheet.cell_value(index, 7),
                        'buyer_email': sheet.cell_value(index, 8).lower(),
                        'delivery_hours': exists_vendor_id.delivery_hours,
                        'address_pobox': exists_vendor_id.address_pobox,
                        'is_outerbuy': sheet.cell_value(index, 11),
                        'currency': int_currency_id,
                        'vat_number': exists_vendor_id.vat_number,
                        'address_country': int_country_id,
                        'mother_name_cn': exists_vendor_id.mother_name_cn,
                        'shareholders': exists_vendor_id.shareholders,
                        'user_id': int_user_id,
                        'address_postalcode': exists_vendor_id.address_postalcode,
                        'web_site': exists_vendor_id.web_site,
                        'address_street': exists_vendor_id.address_street,
                        'factory_count': exists_vendor_id.factory_count,
                        'address_district': exists_vendor_id.address_district,
                        'project_status': exists_vendor_id.project_status,
                        'apply_memo': exists_vendor_id.apply_memo,
                        'sales_mobile': exists_vendor_id.sales_mobile,
                        'sales_telephone': exists_vendor_id.sales_telephone,
                        'capital': exists_vendor_id.capital,
                        'use_project': exists_vendor_id.use_project,
                        'supplier_category': sheet.cell_value(index, 29),
                        'company_telephone1': exists_vendor_id.company_telephone1,
                        'company_telephone2': exists_vendor_id.company_telephone2,
                        'corporation_description': exists_vendor_id.corporation_description,
                        'supplier_description': exists_vendor_id.supplier_description,
                        'conglomerate': exists_vendor_id.conglomerate,
                        'applyfile_id': False,
                        'supplier_type': exists_vendor_id.supplier_type,
                        'reason_one': int_reason_id,
                        'state': sheet.cell_value(index, 38),
                        'address_city': exists_vendor_id.address_city,
                        'sales_email': exists_vendor_id.sales_email,
                        'company_fax': exists_vendor_id.company_fax,
                        'license_number': exists_vendor_id.license_number,
                        'mother_address_en': exists_vendor_id.mother_address_en,
                        'is_scene': sheet.cell_value(index, 44),
                        'mother_address_cn': exists_vendor_id.mother_address_cn,
                        'contact_person': exists_vendor_id.contact_person,
                        'material_use_range': exists_vendor_id.material_use_range,
                        'duns_number': exists_vendor_id.duns_number,
                        'other_emails': exists_vendor_id.other_emails,
                        'message_last_post': exists_vendor_id.message_last_post,
                        'employee_number': exists_vendor_id.employee_number,
                        'reject_reason': exists_vendor_id.reject_reason,
                        'comment': exists_vendor_id.comment
                    }
                else:
                    vendor_reg_vals = {
                        'plant_id': int_plant_id,
                        'name1_cn': False,
                        'name2_cn': False,
                        'name1_en': False,
                        'name2_en': False,
                        'short_name': False,
                        'mother_name_en': False,
                        'vendor_code': sheet.cell_value(index, 7),
                        'buyer_email': False,
                        'delivery_hours': False,
                        'address_pobox': False,
                        'is_outerbuy': sheet.cell_value(index, 11),
                        'currency': int_currency_id,
                        'vat_number': False,
                        'address_country': int_country_id,
                        'mother_name_cn': False,
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
                        'supplier_category': sheet.cell_value(index, 29),
                        'company_telephone1': False,
                        'company_telephone2': False,
                        'corporation_description': False,
                        'supplier_description': False,
                        'conglomerate': False,
                        'applyfile_id': False,
                        'supplier_type': False,
                        'reason_one': int_reason_id,
                        'state': sheet.cell_value(index, 38),
                        'address_city': False,
                        'sales_email': False,
                        'company_fax': False,
                        'license_number': False,
                        'mother_address_en': False,
                        'is_scene': sheet.cell_value(index, 44),
                        'mother_address_cn': False,
                        'contact_person': False,
                        'material_use_range': False,
                        'duns_number': False,
                        'other_emails': '',
                        'message_last_post': False,
                        'employee_number': False,
                        'reject_reason': False,
                        'comment': False
                    }
            else:
                vendor_reg_vals = {
                    'plant_id': int_plant_id,
                    'name1_cn': sheet.cell_value(index, 1),
                    'name2_cn': sheet.cell_value(index, 2),
                    'name1_en': sheet.cell_value(index, 3),
                    'name2_en': sheet.cell_value(index, 4),
                    'short_name': sheet.cell_value(index, 5),
                    'mother_name_en': sheet.cell_value(index, 6),
                    'vendor_code': sheet.cell_value(index, 7),
                    'buyer_email': sheet.cell_value(index, 8).lower(),
                    'delivery_hours': sheet.cell_value(index, 9),
                    'address_pobox': sheet.cell_value(index, 10),
                    'is_outerbuy': sheet.cell_value(index, 11),
                    'currency': int_currency_id,
                    'vat_number': sheet.cell_value(index, 13),
                    'address_country': int_country_id,
                    'mother_name_cn': sheet.cell_value(index, 15),
                    'shareholders': sheet.cell_value(index, 16),
                    'user_id': int_user_id,
                    'address_postalcode': sheet.cell_value(index, 18),
                    'web_site': sheet.cell_value(index, 19),
                    'address_street': sheet.cell_value(index, 20),
                    'factory_count': sheet.cell_value(index, 21),
                    'address_district': sheet.cell_value(index, 22),
                    'project_status': sheet.cell_value(index, 23),
                    'apply_memo': sheet.cell_value(index, 24),
                    'sales_mobile': sheet.cell_value(index, 25),
                    'sales_telephone': sheet.cell_value(index, 26),
                    'capital': sheet.cell_value(index, 27),
                    'use_project': sheet.cell_value(index, 28),
                    'supplier_category': sheet.cell_value(index, 29),
                    'company_telephone1': sheet.cell_value(index, 30),
                    'company_telephone2': sheet.cell_value(index, 31),
                    'corporation_description': sheet.cell_value(index, 32),
                    'supplier_description': sheet.cell_value(index, 33),
                    'conglomerate': sheet.cell_value(index, 34),
                    'applyfile_id': False,
                    'supplier_type': sheet.cell_value(index, 36),
                    'reason_one': int_reason_id,
                    'state': sheet.cell_value(index, 38),
                    'address_city': sheet.cell_value(index, 39),
                    'sales_email': sheet.cell_value(index, 40),
                    'company_fax': sheet.cell_value(index, 41),
                    'license_number': sheet.cell_value(index, 42),
                    'mother_address_en': sheet.cell_value(index, 43),
                    'is_scene': sheet.cell_value(index, 44),
                    'mother_address_cn': sheet.cell_value(index, 45),
                    'contact_person': sheet.cell_value(index, 46),
                    'material_use_range': sheet.cell_value(index, 47),
                    'duns_number': sheet.cell_value(index, 48),
                    'other_emails': sheet.cell_value(index, 49),
                    'message_last_post': False if sheet.cell_value(index, 50) == '' else sheet.cell_value(index,
                                                                                                          50),
                    'employee_number': sheet.cell_value(index, 51),
                    'reject_reason': sheet.cell_value(index, 52),
                    'comment': sheet.cell_value(index, 53)
                }

            try:
                object_id = False
                #object_ids = api.model('iac.vendor.register').browse([('plant_id', '=', int_plant_id),
                #                                                      ('vendor_code', '=',
                #                                                       sheet.cell_value(index, 7))])
                #for record in object_ids:
                #    object_id = record
                #    break
                #
                #if object_id:
                #    object_id.write(vendor_reg_vals)
                #    vendor_reg_id = object_id
                #else:
                #    vendor_reg_id = api.model('iac.vendor.register').create(vendor_reg_vals)

                domain=[
                        ('vendor_code', '=',sheet.cell_value(index, 7))]
                object_ids=self.env["iac.vendor.register"].search(domain,limit=1,order='id desc')
                vendor_reg_id=None
                if object_ids.exists():
                    object_ids.write(vendor_reg_vals)
                    vendor_reg_id=object_ids
                else:
                    vendor_reg_id=self.env["iac.vendor.register"].create(vendor_reg_vals)
                self.env.cr.commit()
                logging.warn(u'第 %s 个vendor register 处理 %s 成功。vendor_register_id=%s' % (
                index, vendor_reg_id.vendor_code, vendor_reg_id.id))
            except:
                logging.error(u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 7)))
                logging.error(traceback.format_exc())
                traceback.print_exc()
                raise u'No.%s 行异常，vendor_code=%s' % (index, sheet.cell_value(index, 7))
            index += 1
        logging.warn(u'成功处理 %s 个vendor_register' % (end - begin + 1))

if __name__ == "__main__":
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.reg.import')
    #model.import_xls('d:/lwt/vendor_data/vendor_register.xlsx')
    model.import_xls('C:/iac/data/data_import/vendor_register.xls')