# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
import  traceback
import threading
import types
from StringIO import StringIO
import xlwt
import base64
from xlrd import open_workbook
from odoo.exceptions import ValidationError,UserError
from odoo import exceptions
from mm_create import IacPurchaseOrderApprovalLog
# import datetime


class IacPurchaseOrderIMApproval(models.Model):

    _name = "iac.purchase.order.im.special.approval.import"
    _order = 'id desc'

    batch_id = fields.Char(string='upload batch num')
    batch_item_no = fields.Char()
    plant_id = fields.Many2one('pur.org.data',index=True)
    part_id = fields.Many2one('material.master',index=True)
    buyer_code = fields.Char(string='Buyer Code Id',related='part_id.buyer_code_id.buyer_erp_id')
    buyer_name = fields.Char(string='Buyer Name',related='part_id.buyer_code_id.buyer_name')
    part_description = fields.Char(string='Material description',related='part_id.part_description')
    part_no = fields.Char(string='Part No',related='part_id.part_no')
    upload_name = fields.Many2one('res.users',index=True)
    division_id = fields.Many2one('division.code',index=True)
    division = fields.Char(string='Division',related='division_id.division')
    division_description = fields.Char(string='Division Name', related='division_id.division_description')
    quantity = fields.Float()
    upload_time = fields.Date(string='Upload Time')
    state = fields.Selection([
        ('im uploaded', 'IM Uploaded'),
        ('im cancelled', 'IM Cancelled'),
        ('mm send to sap', 'MM Send To SAP'),
        ('sap ok', 'SAP OK'),
        ('sap fail', 'SAP Fail'),
    ], readonly=True, index=True, copy=False)
    data_file_id = fields.Integer()
    evidence_file_id = fields.Integer()
    comment = fields.Char()
    comment1 = fields.Char()
    comment2 = fields.Char()

    @api.multi
    def Update_data(self):
        for record in self:
            # if records.state != 'im uploaded' or records.state != 'sap fail':
            if record.state not in ('im uploaded', 'sap fail'):
                raise exceptions.ValidationError(u'选中的资料state不是‘im uploaded’或者‘sap fail’，无法完成此操作！')
            print record.id,type(record.id)
            try:
                record.write({'state': 'im cancelled'})
                record.env.cr.commit()

            except:
                self.env.cr.rollback()
                raise exceptions.ValidationError(u'更新状态失败！')

            try:
                # 更新好状态之后call New_audit_log記錄log

                self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(record.id, '', 'Im Cancelled', record.comment)
                # raise exceptions.ValidationError(u'更新状态成功！')
            except:
                self.env.cr.rollback()
                raise exceptions.ValidationError(u'写入操作记录失败！')
        message = u'更新状态成功'
        return self.env['warning_box'].info(title="Message", message=message)

    @api.constrains('comment')
    def _compute_front_lens(self):
        for obj in self:
            if len(obj.comment) > 50:
                obj.comment1 = obj.comment[0:50]
                obj.comment2 = obj.comment[50:101]
                comment_vals = {
                    'comment1': obj.comment1,
                    'comment2': obj.comment2
                }
                self.env['iac.purchase.order.im.special.approval.import'].write(comment_vals)

    def download_file(self):
        action = {
            'type': 'ir.actions.act_url',
            'url': '/dms/file/download/%s' % (self.evidence_file_id,),
            'target': 'new',
        }
        return action



                    # print self.comment1
        # self.env['iac.purchase.order.im.special.approval.import'].write({'comment1':comment1})


class ImUpload(models.Model):

    _name = 'iac.im.upload'
    _inherits = {'muk_dms.file': 'file_id'}
    _order = 'id desc'

    file_name1 = fields.Char(string='File Name')
    # file_name2 = fields.Char(string='File Name')
    file1 = fields.Binary(string='File')
    # file2 = fields.Binary(string='File')
    file_id = fields.Many2one('muk_dms.file', string='file info', ondelete='cascade', index=True)
    # batch_id_line = fields.Many2one('iac.purchase.order.im.special.approval.import', string='upload info', index=True)

    # 暂时不用按钮下载模板文件
    # @api.multi
    # def Download_template(self):
    #     """
    #     IM下载模板文件
    #     :return:
    #     """
    #     header_list = ['plant_id', 'part_id', 'quantity', 'division_id', 'Comment']
    #
    #     # 创建StringIO对象，用于读写字符串的缓冲
    #     output = StringIO()
    #
    #     # 创建一个excel
    #     wb = xlwt.Workbook()
    #
    #     # 创建一个表单
    #     sheet = wb.add_sheet('sheet', cell_overwrite_ok=True) ##第二参数用于确认同一个cell单元是否可以重设值。
    #
    #     for i in range(0, 6):
    #         sheet.write(0, i, header_list[i])
    #
    #     # 保存输出表单
    #     wb.save(output)
    #
    #     # 文件保存输出成功后，跳转链接，浏览器下载文件
    #     vals = {
    #         'name': 'Im Upload',
    #         'datas_fname': 'im_upload.xls',
    #         'description': 'Im Upload List',
    #         'type': 'binary',
    #         'db_datas': base64.encodestring(output.getvalue()),
    #     }
    #     file = self.env['ir.attachment'].create(vals)
    #
    #     action = {
    #         'type': 'ir.actions.act_url',
    #         'url': '/web/content/%s/%s.xls' % (file.id, file.id,),
    #         'target': 'new',
    #     }
    #
    #     return action

    # 校验excel表格
    @api.multi
    def validate_data(self):

        # 获取今天的时间
        date = datetime.now().strftime("%Y-%m-%d")
        # today_str = time.strptime(date,'%Y-%m-%d')
        # today = datetime.strptime()
        # today = datetime.date.today()
        print date,type(date)
        print self.file1
        if not self.file1:
            raise exceptions.ValidationError(u'PO明细资料档案和佐证文件必须同时上传')

        # 读取im upload 文件
        # 打开excel文件
        excel_obj = open_workbook(file_contents=base64.decodestring(self.file1))
        # 根据索引确定表
        sheet_obj = excel_obj.sheet_by_index(0)
        # print sheet_obj.cell(0,0)

        # 上传资料前判断表头是否正确
        if sheet_obj.cell(0, 0).value != '工廠' or sheet_obj.cell(0, 1).value != '料號' or sheet_obj.cell(0, 2).value != '數量' or sheet_obj.cell(0, 3).value != 'Division':
            raise exceptions.ValidationError(u'传入excel文件格式错误')

        # trim掉工廠、料號、數量,division欄位的空格
        # 1.获取表格的行数
        rows = sheet_obj.nrows
        print rows

        # 这个for循环用来先检验
        plant_part_list= []
        for i in range(1,rows):
            # 如果•	工廠、料號、數量、Division欄位為空的報錯
            # print sheet_obj.cell(i, 0).value,sheet_obj.cell(i, 1).value,sheet_obj.cell(i, 2).value
            if len(sheet_obj.cell(i, 0).value) == 0:
                raise exceptions.UserError(u'excel第%s行的工厂栏位为空，请检查！'%(i+1))

            if len(sheet_obj.cell(i, 1).value) == 0:
                raise exceptions.ValidationError(u'excel第%s行的料号栏位为空，请检查！'%(i+1))

            # print int(sheet_obj.cell(i, 2).value).replace(' ', '')
            # if int(str(sheet_obj.cell(i, 2).value).replace(' ', '')) < 1:
            #
            #     raise exceptions.ValidationError(u'数量不能小于1，请检查！')

            if str(sheet_obj.cell(i, 2).value).startswith('-'):
                raise exceptions.ValidationError(u'第%s数量不能为负数,请检查！'%(i+1))

            if str(sheet_obj.cell(i, 2).value) == "":

                raise exceptions.ValidationError(u'excel第%s行数量栏位为空，请检查！'%(i+1))


            print type(sheet_obj.cell(i, 2).value)
            if len(str(sheet_obj.cell(i, 3).value)) == 0:
                raise exceptions.ValidationError(u'excel第%s行Division栏位为空，请检查！' %(i+1))

            sheet_i0 = sheet_obj.cell(i,0).value.replace(' ', '')
            # print sheet_i0
            sheet_i1 = sheet_obj.cell(i,1).value.replace(' ', '')
            val = {'plant':sheet_i0,'part':sheet_i1}
            if i == 1:
                plant_part_list.append(val)
            else:
                print i
                if val not in plant_part_list:
                    plant_part_list.append(val)
                else:
                    raise exceptions.ValidationError(u'excel第%s行出现相同的资料(存在工厂和料号相同的资料)，请检查！' %(i+1))

            if type(sheet_obj.cell(i, 2).value) != float:
                raise exceptions.ValidationError(u'excel第%s行数量栏位不是数字类型，请检查！' %(i+1))

            if str(sheet_obj.cell(i, 2).value).count(" "):
                sheet_i2 = str(int(sheet_obj.cell(i, 2).value.replace(' ', '')))
            else:
                sheet_i2 = str(int(sheet_obj.cell(i, 2).value))
            print sheet_obj.cell(i, 3).value,type(sheet_obj.cell(i, 3).value)

            if str(sheet_obj.cell(i, 3).value).count(" "):
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value.replace(' ', '')))
                sheet_13 = str(int(sheet_obj.cell(1, 3).value.replace(' ', '')))
            else:
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value))
                sheet_13 = str(int(sheet_obj.cell(1, 3).value))

            if len(sheet_i3) == 1:
                sheet_i3 = sheet_i3.zfill(2)
            if len(sheet_13)==1:
                sheet_13 = sheet_i3.zfill(2)
            print sheet_i3
            # print sheet_obj.cell(i, 0).value,sheet_obj.cell(i,1).value.replace,sheet_obj.cell(i,2).value.replace,sheet_obj.cell(i,3).value.replace

            # 判断工厂和料号之间是否存在对应关系
            source_part_id = self.env['material.master'].search(['&', ('plant_code', '=', str(sheet_i0)), ('part_no', '=', str(sheet_i1))])
            print source_part_id
            if not source_part_id:

            # if sheet_obj.cell(i,1).value != source_part_id:
                raise exceptions.ValidationError(u'excel第%s行工厂和料号之间不存在对应关系，请检查！' %(i+1))

            # 判断数量栏位的合法性
            # if sheet_i2.count('.'):
            #     raise exceptions.ValidationError(u'数量不能为小数,请检查！')
            print sheet_i2, type(sheet_i2)
            # if not sheet_i2.isdigit():
            #     raise exceptions.ValidationError(u'excel第%s行数量不是数字，请检查！' %(i+1))
            if not int(sheet_i2) >= 1:

                raise exceptions.ValidationError(u'excel第%s行数量不能小于1，请检查！' %(i+1))

            # 检查division是否存在

            division_objt = self.env['division.code'].search([('division', '=', sheet_i3)]).id
            if not division_objt:
                raise exceptions.ValidationError(u'excel第%s行Division不存在，请检查！' %(i+1))

            if i > 1:
                if sheet_i3 != sheet_13:
                    raise exceptions.ValidationError(u'excel第%s行Division不相同，无法上传！' %(i+1))

            # 判断数据表中是否已经存在相同的po
            # 根据工厂id去IAC_PURCHASE_ORDRE_IM_SPECIAL_APPROVAL_IMPORT表中查询，
            upload_plant_id = self.env['pur.org.data'].search([('plant_code', '=', sheet_i0)]).id
            part_id = self.env['material.master'].search(['&', ('plant_code', '=', sheet_i0), ('part_no', '=', sheet_i1)]).id
            division_id = self.env['division.code'].search([('division', '=', sheet_i3)]).id
            target = self.env['iac.purchase.order.im.special.approval.import'].search([
                '&',
                ('plant_id', '=', upload_plant_id),
                ('part_id','=',part_id),
                ('division_id', '=', division_id),
                ('state', 'in',('im uploaded','mm send to sap', 'sap fail'))
            ])

            if target.exists():

                raise exceptions.ValidationError(u'excel第%s行流程中已经存在此笔授权下单资料，请检查！' %(i+1))

            # 根据料号去inforecord_history表里抓单价，检验当前单价的有效性
            # target_export = self.env['inforecord.history'].search([
            #     '&',
            #     ('plant_id', '=', upload_plant_id),
            #     ('part_id', '=', part_id),
            #     ('valid_from', '<=', date),
            #     ('valid_to', '>=', date)
            # ])
            #
            # if not target_export:
            #     raise exceptions.ValidationError(u'excel第%s行系统当前不存在有效的单价，请检查！' %(i+1))

        id_list = []
        # 2.这个用来存资料
        for i in range(1,rows):
            # 如果•	工廠、料號、數量、Division欄位為空的報錯
            # print sheet_obj.cell(i, 0).value,sheet_obj.cell(i, 1).value,sheet_obj.cell(i, 2).value
            if len(sheet_obj.cell(i, 0).value) == 0:
                raise exceptions.UserError(u'excel第%s行的工厂栏位为空，请检查！'%(i+1))

            if len(sheet_obj.cell(i, 1).value) == 0:
                raise exceptions.ValidationError(u'excel第%s行的料号栏位为空，请检查！'%(i+1))

            # print int(sheet_obj.cell(i, 2).value).replace(' ', '')
            # if int(str(sheet_obj.cell(i, 2).value).replace(' ', '')) < 1:
            #
            #     raise exceptions.ValidationError(u'数量不能小于1，请检查！')

            if str(sheet_obj.cell(i, 2).value).startswith('-'):
                raise exceptions.ValidationError(u'第%s数量不能为负数,请检查！'%(i+1))

            if str(sheet_obj.cell(i, 2).value) == "":

                raise exceptions.ValidationError(u'excel第%s行数量栏位为空，请检查！'%(i+1))


            print type(sheet_obj.cell(i, 2).value)
            if len(str(sheet_obj.cell(i, 3).value)) == 0:
                raise exceptions.ValidationError(u'excel第%s行Division栏位为空，请检查！' %(i+1))

            sheet_i0 = sheet_obj.cell(i,0).value.replace(' ', '')
            # print sheet_i0
            sheet_i1 = sheet_obj.cell(i,1).value.replace(' ', '')
            # print type(sheet_i1)
            #
            # print type(sheet_obj.cell(i, 2).value)
            # print type(sheet_obj.cell(i,3).value)

            if str(sheet_obj.cell(i, 2).value).count(" "):
                sheet_i2 = str(int(sheet_obj.cell(i, 2).value.replace(' ', '')))
            else:
                sheet_i2 = str(int(sheet_obj.cell(i, 2).value))
            print type(sheet_i2)

            if str(sheet_obj.cell(i, 3).value).count(" "):
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value.replace(' ', '')))
            else:
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value))

            if len(sheet_i3) == 1:
                sheet_i3 = sheet_i3.zfill(2)


            # print sheet_obj.cell(i, 0).value,sheet_obj.cell(i,1).value.replace,sheet_obj.cell(i,2).value.replace,sheet_obj.cell(i,3).value.replace

            # 判断工厂和料号之间是否存在对应关系
            source_part_id = self.env['material.master'].search(['&', ('plant_code', '=', sheet_i0), ('part_no', '=', sheet_i1)])
            print source_part_id
            if not source_part_id:

            # if sheet_obj.cell(i,1).value != source_part_id:
                raise exceptions.ValidationError(u'excel第%s行工厂和料号之间不存在对应关系，请检查！' %(i+1))

            # 判断数量栏位的合法性
            # if sheet_i2.count('.'):
            #     raise exceptions.ValidationError(u'数量不能为小数,请检查！')

            if not int(sheet_i2) >= 1:

                raise exceptions.ValidationError(u'excel第%s行数量不能小于1，请检查！' %(i+1))

            # 检查division是否存在

            if not self.env['division.code'].search([('division', '=', sheet_i3)]).id:
                raise exceptions.ValidationError(u'excel第%s行Division不存在，请检查！' %(i+1))

            # 判断数据表中是否已经存在相同的po
            # 根据工厂id去IAC_PURCHASE_ORDRE_IM_SPECIAL_APPROVAL_IMPORT表中查询，
            upload_plant_id = self.env['pur.org.data'].search([('plant_code', '=', sheet_i0)]).id
            part_id = self.env['material.master'].search(['&', ('plant_code', '=', sheet_i0), ('part_no', '=', sheet_i1)]).id
            division_id = self.env['division.code'].search([('division', '=', sheet_i3)]).id
            target = self.env['iac.purchase.order.im.special.approval.import'].search([
                '&',
                ('plant_id', '=', upload_plant_id),
                ('part_id','=',part_id),
                ('division_id', '=', division_id),
                ('state', 'in',('im uploaded','mm send to sap', 'sap fail'))
            ])

            if target.exists():

                raise exceptions.ValidationError(u'excel第%s行流程中已经存在此笔授权下单资料，请检查！' %(i+1))

            # 根据料号去inforecord_history表里抓单价，检验当前单价的有效性
            # target_export = self.env['inforecord.history'].search([
            #     '&',
            #     ('plant_id', '=', upload_plant_id),
            #     ('part_id', '=', part_id),
            #     ('valid_from', '<=', date),
            #     ('valid_to', '>=', date)
            # ])
            #
            # if not target_export:
            #     raise exceptions.ValidationError(u'excel第%s行系统当前不存在有效的单价，请检查！' %(i+1))

            part_description = self.env['material.description'].search([
                ('part_no','=',sheet_i1),
                ('plant_code', '=', sheet_i0)]).part_description

            division = self.env['division.code'].search([('division','=',sheet_i3)]).division
            division_description = self.env['division.code'].search([('division', '=',
                                                                      division)]).division_description
            upload_time = datetime.now().strftime("%Y-%m-%d")
            upload_name = self._uid

            # 进行数据库保存
            vals = {
                'plant_id': upload_plant_id,
                'part_id': part_id,
                'quantity': sheet_i2,
                'division_id': division_id,
                'comment': sheet_obj.cell(i,4).value,
                'part_description': part_description,
                'part_no': sheet_i1,
                'division': division,
                'division_description': division_description,
                'upload_time': upload_time,
                'upload_name': upload_name

            }

            try:
                # with self.env.cr.savepoint():
                # save_point = self.env.cr.savepoint()
                current_object=self.env['iac.purchase.order.im.special.approval.import'].create(vals)

                self.env.cr.commit()
                # print current_object.comment1
                # print current_object.comment2

                im_upload_id = self.env['iac.purchase.order.im.special.approval.import'].search([
                    '&',
                    ('plant_id', '=', upload_plant_id),
                    ('part_id', '=', part_id),
                    ('division_id', '=', division_id),
                ], order='id desc', limit=1).id
                print im_upload_id
                id_list.append(im_upload_id)

                # 获取记录的ID
                ID = str(id_list[0])

                # 调用方法生成batch_id
                batch_id = self._Generate_batch_id(ID)
                batch_item_no = str(i * 10)
                state = 'im uploaded'
                upload_file_id = self.env['muk_dms.file'].search([('create_uid', '=', self._uid)], order='id desc',
                                                                 limit=1).id
                save_vals = {
                    'batch_id': batch_id,
                    'batch_item_no': batch_item_no,
                    'state': state,
                    'evidence_file_id': upload_file_id,
                }

                current_object.write(save_vals)
                current_object.env.cr.commit()

            except:
                self.env.cr.rollback()
                raise exceptions.ValidationError(u'保存资料文件失败，请重新上传！')


            # current_object=self.env['iac.purchase.order.im.special.approval.import'].create(vals)
            #
            # self.env.cr.commit()
            #
            # im_upload_id = self.env['iac.purchase.order.im.special.approval.import'].search([
            #     '&',
            #     ('plant_id', '=', upload_plant_id),
            #     ('part_id', '=', part_id),
            #     ('division_id', '=', division_id),
            # ],order = 'id desc', limit = 1).id
            # print im_upload_id
            # id_list.append(im_upload_id)
            #
            # # 获取记录的ID
            # ID = str(id_list[0])
            # # ID = self.env['iac.purchase.order.im.special.approval.import'].search([
            # #     '&',
            # #     ('plant_id' ,'=', upload_plant_id),
            # #     ('part_id', '=', part_id),
            # #     ('division_id', '=', division_id),
            # #     # ('create_uid', '=', ),
            # # ],order = 'id desc', limit = 1).id
            # #
            # # ID = str(ID)
            #
            # # 调用方法生成batch_id
            # batch_id = self._Generate_batch_id(ID)
            # batch_item_no = str(i*10)
            # state = 'im uploaded'
            # upload_file_id = self.env['muk_dms.file'].search([('create_uid','=',self._uid)],order='id desc', limit=1).id
            # save_vals = {
            #         'batch_id': batch_id,
            #         'batch_item_no': batch_item_no,
            #         'state': state,
            #         'evidence_file_id': upload_file_id,
            #     }
            #
            # current_object.write(save_vals)
            # current_object.env.cr.commit()


            # 上传excel资料完成后，调 New_audit_log接口记录操作记录

            # sheet_i4 = sheet_obj.cell(i, 4).value
            # IacPurchaseOrderApprovalLog.New_audit_log(im_upload_id, "", "Im Upload", sheet_i4)
            try:
                sheet_i4 = sheet_obj.cell(i, 4).value
                self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(im_upload_id, '', 'Im Upload',
                                                                                        sheet_i4)
            except:
                self.env.cr.rollback()
                raise exceptions.ValidationError(u'保存操作记录失败！')

        # 遍历excel资料得到所有的buyer_email,塞进一个list
        buyer_email_list = []
        for i in range(1, rows):
            sheet_i0 = sheet_obj.cell(i, 0).value.replace(' ', '')
            sheet_i1 = sheet_obj.cell(i, 1).value.replace(' ', '')
            if str(sheet_obj.cell(i, 3).value).count(" "):
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value.replace(' ', '')))
            else:
                sheet_i3 = str(int(sheet_obj.cell(i, 3).value))
            upload_plant_id = self.env['pur.org.data'].search([('plant_code', '=', sheet_i0)]).id
            part_id = self.env['material.master'].search(
                ['&', ('plant_code', '=', sheet_i0), ('part_no', '=', sheet_i1)]).id
            division_id = self.env['division.code'].search([('division', '=', sheet_i3)]).id
            buyer_code_id = self.env['material.master'].search([
                '&',
                ('plant_id', '=', upload_plant_id),
                ('part_no', '=', sheet_i1)]).buyer_code_id
            buyer_ad_account = self.env['buyer.code'].search([('id', '=', buyer_code_id.id)]).buyer_ad_account
            partner_id = self.env['res.users'].search([('login', '=', buyer_ad_account)]).partner_id
            buyer_email = self.env['res.partner'].search([('id', '=', partner_id.id)]).email
            # im_email = self.env['res.users'].browse(self._uid).partner_id.email
            # email = buyer_email + ';' + im_email
            if buyer_email not in buyer_email_list:
                buyer_email_list.append(buyer_email)
        try:
            for buyer_email_list_one in buyer_email_list:
                im_email = self.env['res.users'].browse(self._uid).partner_id.email
                email = buyer_email_list_one + ';' + im_email
                batch_id = self.env['iac.purchase.order.im.special.approval.import'].search([('create_uid','=',self._uid)],order='id desc',limit=1).batch_id
                body_list = []
                for i in range(1, rows):
                    sheet_i0 = sheet_obj.cell(i, 0).value.replace(' ', '')
                    sheet_i1 = sheet_obj.cell(i, 1).value.replace(' ', '')
                    if str(sheet_obj.cell(i, 3).value).count(" "):
                        sheet_i3 = str(int(sheet_obj.cell(i, 3).value.replace(' ', '')))
                    else:
                        sheet_i3 = str(int(sheet_obj.cell(i, 3).value))
                    upload_plant_id = self.env['pur.org.data'].search([('plant_code', '=', sheet_i0)]).id
                    part_id = self.env['material.master'].search(
                        ['&', ('plant_code', '=', sheet_i0), ('part_no', '=', sheet_i1)]).id
                    division_id = self.env['division.code'].search([('division', '=', sheet_i3)]).id
                    buyer_code_id = self.env['material.master'].search([
                        '&',
                        ('plant_id', '=', upload_plant_id),
                        ('part_no', '=', sheet_i1)]).buyer_code_id
                    print buyer_code_id,buyer_code_id.buyer_ad_account
                    buyer_ad_account = self.env['buyer.code'].search([('id', '=', buyer_code_id.id)]).buyer_ad_account
                    partner_id = self.env['res.users'].search([('login', '=', buyer_ad_account)]).partner_id
                    buyer_email = self.env['res.partner'].search([('id', '=', partner_id.id)]).email
                    if buyer_email == buyer_email_list_one:
                        search_object = self.env['iac.purchase.order.im.special.approval.import'].search([
                            '&',
                            ('plant_id', '=', upload_plant_id),
                            ('part_id', '=', part_id),
                            ('division_id', '=', division_id),
                        ], order='id desc', limit=1)
                        # print search_object.comment,type(search_object.comment)
                        im_upload_list = [str(search_object.batch_id), str(search_object.batch_item_no), str(search_object.plant_id.plant_code),
                                          str(search_object.part_no), str(search_object.part_description), str(search_object.quantity),
                                          str(search_object.division),
                                          str(search_object.division_description),str(search_object.comment)]
                        body_list.append(im_upload_list)
                self.Send_email(email, batch_id, body_list)
        except:
            pass

    @api.onchange('filename')
    def upload_prove_file(self):
        # 上传保存佐证文件
        po_dir_rec = self.env["muk_dms.directory"].sudo().search([('name', '=', 'po_attachment')], order='id desc', limit=1)
        if not po_dir_rec.exists():
            raise UserError("Dir 'po_attachment' has not found")

        self.directory = po_dir_rec.id

    # 生成batch_id
    @api.multi
    def _Generate_batch_id(self, ID):

        today = datetime.now().strftime("%Y%m%d")
        batch_id = 'SA' + today + ID.zfill(8)

        return batch_id


    # 发邮件的方法
    def Send_email(self,email,batch_id,body_list):
        # self.env['iac.email.pool'].button_to_mail()
        try:
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", "以下授權下單明細請轉PO-%s"%batch_id,
                ['授权单号', 'Item No', '工厂', '料号', '描述','数量', 'Division','BU NBA','备注'], body_list, 'SPECIAL_APPROVAL_PO')

        except:
            raise exceptions.ValidationError(u'发送邮件失败！')


class ImUploadListSearchWizard(models.TransientModel):
    _name = 'im.upload.list.search.wizard'

    plant_code = fields.Many2one('pur.org.data', string='plant', domain=lambda self: [('id', 'in', self.env.user.plant_id_list)])
    material = fields.Many2one('material.master', string='Material')
    upload_date_from = fields.Date(string='upload date from')
    upload_date_to = fields.Date(string='upload date to')
    state = fields.Selection([
        ('im uploaded', 'IM Uploaded'),
        ('im cancelled', 'IM Cancelled'),
        ('mm send to sap', 'MM Send To SAP'),
        ('sap ok', 'SAP OK'),
        ('sap fail', 'SAP Fail'),
    ], index=True, copy=False)

    @api.multi
    def im_upload_list(self):

        result = []

        for wizard in self:
            domain = []
            if wizard.plant_code:
                domain += [('plant_id', '=', wizard.plant_code.id)]

            if wizard.material:
                domain += [('part_id', '=', wizard.material.id)]

            if wizard.upload_date_from and not wizard.upload_date_to:
                domain += [('upload_time', '>=', wizard.upload_date_from)]

            if wizard.upload_date_to and not wizard.upload_date_from:
                domain += [('upload_time', '<=', wizard.upload_date_to)]

            if wizard.upload_date_from and wizard.upload_date_to:

                if wizard.upload_date_from > wizard.upload_date_to:
                    raise exceptions.ValidationError(u'查询日期不符合条件！')
                else:

                    domain += ['&', ('upload_time', '>=', wizard.upload_date_from), ('upload_time', '<=', wizard.upload_date_to)]

            if wizard.state:
                domain += [('state', '=', wizard.state)]

            if not wizard.state:
                domain += [('state', 'in', ('im uploaded','im cancelled','mm send to sap','sap ok','sap fail'))]

            result = self.env['iac.purchase.order.im.special.approval.import'].search(domain)
            # result_list.append(result)

            if not result:
                raise exceptions.ValidationError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': 'im upload list',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.purchase.order.im.special.approval.import'

        }
        return action