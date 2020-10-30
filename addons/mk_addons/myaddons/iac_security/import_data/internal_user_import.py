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
"""
导入内部user
"""

class IacUserInternalImport(models.TransientModel):
    _name = 'iac.user.internal.import'
    _description = 'User Internal Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        while index <=end and index <= sheet.nrows - 1:
            int_buyer_code_ids = []
            int_plant_ids = []
            int_division_code_ids = []
            int_source_code_ids = []
            int_groups_ids = []


            #当前的操作与user是否存在无关，每次必定更新这些字段
            if sheet.cell_value(index, 1)=='21222296':
                pass

            if sheet.cell_value(index, 4):
                for item in sheet.cell_value(index, 4).split('|'):
                    object_id=self.env["buyer.code"].search([('buyer_erp_id', '=', item)])
                    if object_id.exists():
                        int_buyer_code_ids.append((0,0,{"buyer_code_id":object_id.id}))

            if sheet.cell_value(index, 5):
                for item in sheet.cell_value(index, 5).split('|'):
                    object_id=self.env["pur.org.data"].search([('plant_code', '=', item)])
                    if object_id.exists():
                        int_plant_ids.append((4,object_id.id))

            if sheet.cell_value(index, 6):
                for item in sheet.cell_value(index, 6).split('|'):
                    object_id=self.env["division.code"].search([('division', '=', item)])
                    if object_id.exists():
                        int_division_code_ids.append((4,object_id.id))

            if sheet.cell_value(index, 7):
                for item in sheet.cell_value(index, 7).split('|'):
                    object_id=self.env["source.code"].search([('source_code', '=', item)])
                    if object_id.exists():
                        int_source_code_ids.append((0,0,{"source_code_id":object_id.id}))

            if sheet.cell_value(index, 8):
                for item in sheet.cell_value(index, 8).split('|'):
                    object_id=self.env.ref('oscg_vendor.' + item)
                    if object_id.exists():
                        int_groups_ids.append((4,object_id.id))

            exists_user_id=self.env["res.users"].search([('login', '=', sheet.cell_value(index, 1))])

            #user信息不存在的时候要进行创建操作
            if not exists_user_id:
                user_vals = {
                    'name': sheet.cell_value(index, 0),
                    'login': sheet.cell_value(index, 1),
                    'password': sheet.cell_value(index, 2),
                    'share': False,
                    'groups_id': int_groups_ids
                }
                exists_user_id = self.env['res.users'].create(user_vals)
            else:
                #已经存在的更新密码和组信息
                user_vals = {
                    'password': sheet.cell_value(index, 2),
                    'share': False,
                    'groups_id': int_groups_ids
                }
                exists_user_id.write(user_vals)

            partner_vals = {
                'email': sheet.cell_value(index, 3),
                'plant_ids': int_plant_ids,
                'buyer_code_ids': int_buyer_code_ids,
                'source_code_ids': int_source_code_ids,
                'division_code_ids': int_division_code_ids,
                'supplier': False
            }
            #exists_user_id.partner_id.plant_ids.unlink()
            try:
                self.env.cr.commit()
                exists_user_id.partner_id.buyer_code_ids.unlink()
                self.env.cr.commit()
                exists_user_id.partner_id.source_code_ids.unlink()
                self.env.cr.commit()
                #exists_user_id.partner_id.division_code_ids.unlink()
                self.env.cr.commit()
                exists_user_id.partner_id.write(partner_vals)
                self.env.cr.commit()
                logging.warn(u'第 %s 个user 处理 %s 成功。user_id=%s' % (index, exists_user_id.name, exists_user_id.id))
            except:
                traceback.print_exc()
                logging.error(u'第 %s 个user出现异常' % (index,))
                logging.error(traceback.format_exc())
                raise u'第 %s 个user出现异常' % (index,)
            index += 1

    def valid_xls_data(self,sheet,begin,end):
        check_flag=True
        index = begin
        while index <= sheet.nrows - 1:
            logging.warn(u'检查第 %s 行' % index)
            exists_user_id=self.env["res.users"].search([('login', '=', sheet.cell_value(index, 1))])
            if not exists_user_id.exists():
                if sheet.cell_value(index, 4):
                    for item in sheet.cell_value(index, 4).split('|'):
                        object_id=self.env["buyer.code"].search([('buyer_erp_id', '=', item)])
                        if not object_id.exists():
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到buyer_code=%s' % (index, item))

                if sheet.cell_value(index, 5):
                    for item in sheet.cell_value(index, 5).split('|'):
                        object_id=self.env["pur.org.data"].search([('plant_code', '=', item)])
                        if not object_id.exists():
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到plant_code=%s' % (index, item))

                if sheet.cell_value(index, 6):
                    for item in sheet.cell_value(index, 6).split('|'):
                        object_id=self.env["division.code"].search([('division', '=', item)])
                        if not object_id.exists():
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到division_code=%s' % (index, item))

                if sheet.cell_value(index, 7):
                    for item in sheet.cell_value(index, 7).split('|'):
                        object_id=self.env["source.code"].search([('source_code', '=', item)])
                        if not object_id.exists():
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到source_code=%s' % (index, item))

                if sheet.cell_value(index, 8):
                    for item in sheet.cell_value(index, 8).split('|'):
                        object_id=self.env.ref('oscg_vendor.'+item)
                        if not object_id.exists():
                            check_flag = check_flag & False
                            logging.error(u'No.%s 数据异常，未找到group_id=%s' % (index, item))
            else:
                logging.info(u'第 %s 个user %s 已经存在，跳过检查。user_id=%s' % (index, exists_user_id.name, exists_user_id.id))
            index += 1

if __name__=="__main__":
    """
    执行程序之前执行sql脚本禁止外键检查
    alter table res_partner_source_code_line disable trigger all;
    alter table res_partner_buyer_code_line disable trigger all;
    alter table partner_buyer_code_rel disable trigger all;
    alter table partner_plant_rel disable trigger all;

    程序完成之后,执行sql脚本启动外键检查
    alter table res_partner_source_code_line enable trigger all;
    alter table res_partner_buyer_code_line enable trigger all;
    alter table partner_buyer_code_rel enable trigger all;
    alter table partner_plant_rel enable trigger all;
    """
    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.user.internal.import')
    #model.import_xls('d:/lwt/vendor_data/internal_user.xls')
    model.import_xls('C:/iac/data/data_import/internal_user.xls')
    #model.import_xls('C:/Users/SAP01/Desktop/lwt/data_import/內部賬號.xlsx')