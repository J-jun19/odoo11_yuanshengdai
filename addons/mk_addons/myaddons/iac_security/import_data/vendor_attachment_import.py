# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
import xlrd
import base64
from datetime import timedelta
import erppeek
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)
"""
导入supplier_company,包含supplier_company包含vendor 的信息
"""

class IacVendorAttachmentImport(models.TransientModel):
    _name = 'iac.vendor.attachment.import'
    _description = 'Vendor Attachment Import'

    @api.model
    def import_xls(self,xls_path):
        workbook = xlrd.open_workbook(xls_path)
        sheet = workbook.sheet_by_index(0)
        self.import_xls_sheet(sheet,1,sheet.nrows-1)


    def import_xls_sheet(self,sheet, begin, end):
        index = begin
        # 执行导入数据
        while index <= sheet.nrows - 1:
            logging.warn('do index=%s' % (index))

            int_vendor_id = False
            int_vendor_reg_id = False
            int_attachment_type_id = False
            time_sensitive = False
            group = 'basic'

            if sheet.cell_value(index, 0):
                domain=[('vendor_code', '=', sheet.cell_value(index,0))]
                object_id=self.env['iac.vendor'].search(domain,limit=1)
                if object_id.exists():
                    int_vendor_id = object_id.id
                    if object_id.vendor_reg_id:
                        int_vendor_reg_id = object_id.vendor_reg_id.id
                else:
                    logging.error('row:%s no vendor,vendor code %s' % (index, sheet.cell_value(index, 0)))
                    continue

            if int_vendor_id:
                if sheet.cell_value(index, 4):
                    domain=[('name', '=', sheet.cell_value(index,4))]
                    object_id=self.env['iac.attachment.type'].search(domain,limit=1)
                    if object_id.exists():
                        int_attachment_type_id = object_id.id
                        time_sensitive = object_id.time_sensitive
                        if object_id.name in ['A24','A15','A16']:
                            group = 'bank'

                # 处理文件
                directory = 1# basic
                if group == 'bank':
                    domain=[('name', '=', 'vendor_bank')]
                    object_id=self.env['muk_dms.directory'].search(domain,limit=1)
                    if object_id.exists():
                        directory=object_id.id
                    else:
                        pass

                try:
                    open_file = open(r'//odoo-files//EP_FILE//%s' % (sheet.cell_value(index, 1)), 'rb')  # 二进制方式打开文件
                    base64_file_content = base64.b64encode(open_file.read())  # 读取文件内容，转换为base64编码
                    open_file.close()

                    file_vals = {
                        'filename': sheet.cell_value(index, 1),
                        'file': base64_file_content,
                        'directory': directory
                    }
                    file_id = self.env['muk_dms.file'].create(file_vals)
                    # 如果文档类型需要过期日期管理，但上传文件中没有过期日期，则使用upload_date + 2年
                    str_upload_date = False
                    str_expiration_date = False
                    if sheet.cell_value(index, 5):
                        upload_date = fields.Date.from_string(sheet.cell_value(index, 5))
                    else:
                        upload_date = fields.Date.from_string(fields.Date.today())
                    str_upload_date = fields.Date.to_string(upload_date)
                    if time_sensitive:
                        if not sheet.cell_value(index, 6):
                            str_expiration_date = fields.Date.to_string(upload_date + timedelta(days=int(365 * 2)))
                        else:
                            str_expiration_date = sheet.cell_value(index, 6)
                    attachment_vals = {
                        'type': int_attachment_type_id,
                        'file_id': file_id.id,
                        'description': sheet.cell_value(index, 2),
                        'group': group,
                        'expiration_date': str_expiration_date,
                        'state': sheet.cell_value(index, 7)
                    }
                    if group == 'basic':
                        if int_vendor_reg_id:
                            attachment_vals['vendor_reg_id'] = int_vendor_reg_id
                            self.env["iac.vendor.register.attachment"].create(attachment_vals)
                            self.env.cr.commit()
                        else:
                            logging.error('row:%s no vendor register,vendor code %s' % (index, sheet.cell_value(index, 0)))
                            raise 'row:%s no vendor register,vendor code %s' % (index, sheet.cell_value(index, 0))
                    if group == 'bank':
                        if int_vendor_id:
                            attachment_vals['vendor_id'] = int_vendor_id
                            #api.model('iac.vendor.attachment').create(attachment_vals)
                            self.env["iac.vendor.attachment"].create(attachment_vals)
                            self.env.cr.commit()
                        else:
                            logging.error('row:%s no vendor,vendor code %s' % (index, sheet.cell_value(index, 0)))
                            raise 'row:%s no vendor register,vendor code %s' % (index, sheet.cell_value(index, 0))
                except:
                    #traceback.print_exc()
                    logging.warn(u'row %s error,vendor_code=%s' % (index, sheet.cell_value(index, 0)))
                    logging.error(traceback.format_exc())
                    raise u'row %s error,vendor_code=%s' % (index, sheet.cell_value(index, 0))
            else:
                logging.warn('no vendor %s' % (sheet.cell_value(index, 0)))
            index += 1
        logging.warn(u'成功处理 %s 个attachment' % (index - 1))

    @api.model
    def fill_attachment_data(self):
        """
        补充文件栏位
        :return:
        """
        #A15 A16 A24
        self.env.cr.execute("select id from \"public\".iac_attachment_type where name in ('A15','A16','A24') ")
        attachment_type_ids=self.env.cr.fetchall()

        #遍历所有vendor
        vendor_ids=self.env["iac.vendor"].search([])
        for vendor_id in vendor_ids:
            logging.warn('do vendor_code=%s' % (vendor_id.vendor_code))
            domain=[('vendor_id','=',vendor_id.id)]
            try:
                for attachment_type_id in attachment_type_ids:
                    domain+=[('type','=',attachment_type_id[0])]
                    attachment_rec=self.env["iac.vendor.attachment"].search(domain)
                    #不存在附件的情况下建立一个空档案
                    if not attachment_rec.exists():
                        attachment_vals = {
                            'vendor_id': vendor_id.id,
                            'type': attachment_type_id[0],
                            'group': 'bank',
                        }
                        attachment_rec=self.env["iac.vendor.attachment"].create(attachment_vals)
                        self.env.cr.commit()
                logging.warn('vendor bank info fill success. vendor_code=%s' % (vendor_id.vendor_code))
            except:
                logging.error('vendor bank info fill error. vendor_code=%s' % (vendor_id.vendor_code))
                logging.error(traceback.format_exc())
                traceback.print_exc()

    @api.model
    def fill_attachment_data_2(self):
        #vendor_rec=self.env["iac.vendor"].browse(980)
        #vendor_rec.fill_blank_attachment()

        #vendor_reg_rec=self.env["iac.vendor.register"].browse(14344)
        #vendor_reg_rec.fill_blank_attachment()

        #遍历所有vendor
        #vendor_ids=self.env["iac.vendor"].search([])
        #for vendor_id in vendor_ids:
        #    try:
        #        vendor_id.fill_blank_attachment()
        #        logging.warn('vendor bank info fill success. vendor_code=%s' % (vendor_id.vendor_code))
        #        self.env.cr.commit()
        #    except:
        #        logging.error('vendor bank info fill error. vendor_code=%s' % (vendor_id.vendor_code))
        #        logging.error(traceback.format_exc())
        #        traceback.print_exc()
        #        self.env.cr.rollback()
#
#
        #vendor_ids=self.env["iac.vendor.register"].search([])
        #for vendor_reg_id in vendor_ids:
        #    try:
        #        vendor_reg_id.fill_blank_attachment()
        #        logging.warn('vendor base info fill success. vendor_code=%s' % (vendor_reg_id.vendor_code))
        #        self.env.cr.commit()
        #    except:
        #        logging.error('vendor base info fill error. vendor_code=%s' % (vendor_reg_id.vendor_code))
        #        logging.error(traceback.format_exc())
        #        traceback.print_exc()
        #        self.env.cr.rollback()

        vendor_change_ids=self.env["iac.vendor.change.basic"].search([])
        for vendor_change_id in vendor_change_ids:
            try:
                vendor_change_id.fill_blank_attachment()
                logging.warn('vendor base info fill success. vendor_code=%s' % (vendor_change_id.vendor_reg_id.vendor_code))
                self.env.cr.commit()
            except:
                logging.error('vendor base info fill error. vendor_code=%s' % (vendor_change_id.vendor_reg_id.vendor_code))
                logging.error(traceback.format_exc())
                traceback.print_exc()
                self.env.cr.rollback()

        pass

if __name__=="__main__":
    #URL = 'http://10.158.2.31:8069'
    #URL = 'http://10.158.2.32'
    #DB = 'IAC_DB'
    #USERNAME = 'admin'
    #PASSWORD = 'iacadmin'
    #erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    #model = erp_peek_api.model('iac.vendor.attachment.import')
    #model.import_xls('//odoo-files//EP_FILE//PRD_files.xls')

    URL = 'http://localhost:8069'
    DB = 'IAC_DB'
    USERNAME = 'admin'
    PASSWORD = 'iacadmin'
    erp_peek_api = erppeek.Client(URL, DB, USERNAME, PASSWORD)
    model = erp_peek_api.model('iac.vendor.attachment.import')
    model.fill_attachment_data_2()


