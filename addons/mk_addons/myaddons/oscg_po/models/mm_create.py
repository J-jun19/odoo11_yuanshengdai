# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
import  traceback
import threading
import types
from datetime import datetime, timedelta



class IacStorageLoaction(models.Model):
    _name = 'iac.storage.location'
    _rec_name = 'storage_location'


    plant_code = fields.Char()
    storage_location = fields.Char()
    warehouse = fields.Char()


class IacPurchaseOrderMMApproval(models.Model):

    _name = "iac.purchase.order.mm.special.approval.create"

    batch_id = fields.Char(related='im_upload_id.batch_id',string='授权单号')
    batch_item_no = fields.Char(related='im_upload_id.batch_item_no')
    im_upload_id = fields.Many2one('iac.purchase.order.im.special.approval.import',index=True)
    vendor_id = fields.Many2one('iac.vendor',index=True)
    vendor_name = fields.Char(related='vendor_id.name')
    buyer_id = fields.Many2one('buyer.code',index=True)
    document_type = fields.Selection([
        ('NB','NB'),
        ('RD','RD'),
    ])
    plant_id = fields.Many2one('pur.org.data',index=True)
    part_id = fields.Many2one('material.master',index=True)
    material_description = fields.Char(related='part_id.part_description')
    quantity = fields.Float(related='im_upload_id.quantity')
    delivery_date = fields.Date()
    state = fields.Selection([
        ('im uploaded', 'IM Uploaded'),
        ('im cancelled', 'IM Cancelled'),
        ('mm send to sap', 'MM Send To SAP'),
        ('sap ok', 'SAP OK'),
        ('sap fail', 'SAP Fail'),
    ],  readonly=True, index=True, copy=False)
    storage_location = fields.Char()
    document_erp_id = fields.Char()
    document_erp_line_no = fields.Char()
    comment = fields.Char(related='im_upload_id.comment')
    division_id = fields.Many2one('division.code')
    # division_code = fields.Char(related='im_upload_id.division_id.division')
    message = fields.Char()
    group_id = fields.Many2one('iac.purchase.order.mm.special.approval.create.group')
    # file_id = fields.Many2one('muk_dms.file')
    # file = fields.Binary(string="File")


    @api.multi
    def download_file(self):

        action = {
            'type': 'ir.actions.act_url',
            'url': '/dms/file/download/%s' % (self.im_upload_id.evidence_file_id,),
            'target': 'new',
        }
        return action
        # print self.im_upload_id.evidence_file_id

    @api.multi
    def validate(self):
        batch_id_list = []
        for item in self:
            if item.state == 'im uploaded' or item.state == 'sap fail':
                print 1
            else:
                raise UserError('SAP OK和MM Send To SAP和IM Cancelled状态的PO无法送SAP')
            if len(batch_id_list) == 0:
                batch_id_list.append(item.batch_id)
            else:
                if item.batch_id not in batch_id_list:
                    raise UserError('送SAP的PO必须拥有相同的授权单号')
            if item.delivery_date < datetime.now().strftime('%Y-%m-%d'):
                raise UserError('Delivery Date不能小于今天')
            ih_exist = self.env['iac.rfq'].search(
                [('part_id', '=', item.part_id.id), ('plant_id', '=', item.plant_id.id),
                 ('vendor_id', '=', item.vendor_id.id),('state', '=', 'sap_ok'),
                 ('valid_from', '<=', datetime.now().strftime('%Y-%m-%d')),
                 ('valid_to', '>=', datetime.now().strftime('%Y-%m-%d'))])
            if not ih_exist:
                raise UserError(item.part_id.part_no+','+item.plant_id.plant_code+','+item.vendor_id.vendor_code+'不存在有效单价')

    @api.multi
    def button_to_sap(self):
        self.validate()
        val = {}
        change = self.env['iac.purchase.order.mm.special.approval.create.group'].create(val)
        for item in self:
            item.write({'state':'mm send to sap','group_id':change.id})
            item.env.cr.commit()
            im_upload = self.env['iac.purchase.order.im.special.approval.import'].browse(item.im_upload_id.id)
            im_upload.write({'state':'mm send to sap'})
            im_upload.env.cr.commit()
            self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(im_upload.id,item.id,'mm send to sap','')

        msg = self.send_to_sap(change.id)
        return self.env['warning_box'].info(title="Message", message=msg)

    @api.model
    def get_callback_data(self, method,group_id):
        # sequence = self.env['ir.sequence'].next_by_code('iac.interface.rpc')
        mm_object = self.env['iac.purchase.order.mm.special.approval.create'].search([('group_id', '=', group_id)],
                                                                                     limit=1)
        vals = {
            "id": group_id,
            "biz_object_id": group_id,
            "group_id": group_id,
            "vendor_code": mm_object.vendor_id.vendor_code,
            "buyer_code": mm_object.buyer_id.buyer_erp_id,
            "plant": mm_object.plant_id.plant_code,
            "purchase_org": mm_object.plant_id.purchase_org,
            "storage_location": mm_object.storage_location,
            "document_type": mm_object.document_type
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env['iac.interface.rpc'].invoke_web_call_with_log(
            method, vals)
        return rpc_result, rpc_json_data, exception_log

    @api.multi
    def send_to_sap(self,group_id):
        # print group_id
        # mm_object = self.env['iac.purchase.order.mm.special.approval.create'].search([('group_id','=',group_id)],limit=1)
        # # 调用SAP接口
        # biz_object = {
        #     "id":group_id,
        #     "biz_object_id": group_id,
        #     "group_id": group_id,
        #     "vendor_code": mm_object.vendor_id.vendor_code,
        #     "buyer_code":mm_object.buyer_id.buyer_erp_id,
        #     "plant":mm_object.plant_id.plant_code,
        #     "purchase_org":mm_object.plant_id.purchase_org,
        #     "storage_location":mm_object.storage_location,
        #     "document_type":mm_object.document_type
        # }

        try:
            rpc_result, rpc_json_data , exception_log= self.env['iac.purchase.order.mm.special.approval.create'].get_callback_data('ODOO_PO_007',group_id)
            # rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            #     "iac.interface.rpc"].invoke_web_call_with_log(
            #     "ODOO_PO_007", biz_object)

            if rpc_result:
                # msg = rpc_json_data.get("rpc_callback_data").get('Message').get('Message')
                mm_list = rpc_json_data.get("rpc_callback_data").get('Document').get('ITEM')

                for item in self:
                    item.write({'state': 'sap ok'})
                    item.env.cr.commit()
                    im_upload = self.env['iac.purchase.order.im.special.approval.import'].browse(item.im_upload_id.id)
                    im_upload.write({'state': 'sap ok'})
                    im_upload.env.cr.commit()
                    self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(im_upload.id, item.id,
                                                                                            'sap ok', '')

                for mm in mm_list:
                    plant_id = self.env['pur.org.data'].search([('plant_code','=',mm.get('PLANT'))]).id
                    material_id = self.env['material.master'].search([('part_no','=',mm.get('PART_NO')),('plant_id','=',plant_id)]).id
                    mm_special = self.env['iac.purchase.order.mm.special.approval.create'].search([('group_id','=',group_id),('part_id','=',material_id)])
                    mm_special.write({'document_erp_id':mm.get('PO_NO'),'document_erp_line_no':mm.get('PO_LINE_NO'),'message':''})
                msg = '通知SAP成功'

            else:
                msg = exception_log[0]['Message']
                for item in self:
                    item.write({'state': 'sap fail','message':msg})
                    item.env.cr.commit()
                    im_upload = self.env['iac.purchase.order.im.special.approval.import'].browse(item.im_upload_id.id)
                    im_upload.write({'state': 'sap fail'})
                    im_upload.env.cr.commit()
                    self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(im_upload.id, item.id,
                                                                                         'sap fail', '')




        except:
            for item in self:
                item.write({'state': 'sap fail','message':'Call接口异常,请联系IT处理'})
                item.env.cr.commit()
                im_upload = self.env['iac.purchase.order.im.special.approval.import'].browse(item.im_upload_id.id)
                im_upload.write({'state': 'sap fail'})
                im_upload.env.cr.commit()
                self.env['iac.purchase.order.special.approval.audit.log'].New_audit_log(im_upload.id, item.id,
                                                                                        'sap fail', '')
            msg = 'Call接口异常,请联系IT处理'
        return msg












class IacPurchaseOrderMMApprovalWizard(models.TransientModel):

    _name = 'iac.purchase.order.mm.special.approval.create.wizard'

    plant_id = fields.Many2one('pur.org.data',string='Plant*',required=1,domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    buyer_id = fields.Many2one('buyer.code',string='Buyer*',required=1,domain=lambda self: [('id', 'in', self.env.user.buyer_id_list
)])
    document_type = fields.Selection([
        ('NB', 'NB'),
        ('RD', 'RD'),
    ],default='NB',required=1,string='Document Type*')
    vendor_id = fields.Many2one('iac.vendor',required=1,string='Vendor(不显示block或delete的Vendor)*')
    part_id = fields.Many2one('material.master',string='Material')

    storage_location = fields.Many2one('iac.storage.location',string='Storage Location*',required=1)
    batch_id = fields.Char(string='授權單號')
    state = fields.Selection([
        ('im uploaded', 'IM Uploaded'),
        ('im cancelled', 'IM Cancelled'),
        ('mm send to sap', 'MM Send To SAP'),
        ('sap ok', 'SAP OK'),
        ('sap fail', 'SAP Fail'),
    ], default='im uploaded',string='授權單號狀態')

    @api.onchange('plant_id')
    def _onchange_location(self):
        location = self.env["iac.storage.location"].search([('storage_location', '=', 'SW01'),('plant_code','=',self.plant_id.plant_code)])
        # if not po_dir_rec.exists():
        #     raise UserError("Dir 'po_attachment' has not found")
        self.storage_location = location.id

    @api.onchange('plant_id')
    def _onchange_plant_id_on_vendor(self):

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}

    @api.onchange('plant_id')
    def _onchange_plant_id_on_location(self):

        if self.plant_id:
            return {'domain': {'storage_location': [('plant_code', '=', self.plant_id.plant_code)]}}

    @api.onchange('buyer_id')
    def _onchange_buyer_id(self):

        if self.buyer_id:
            return {'domain': {'part_id': [('buyer_code_id', '=', self.buyer_id.id)]}}

    @api.multi
    def search_purchase_order_mm(self):
        domain = []
        part_id_list = []
        for wizard in self:

            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.part_id:
                domain += [('part_id', '=', wizard.part_id.id)]
            else:
                for item in self.env['material.master'].search([('buyer_code_id','=',wizard.buyer_id.id)]):
                    part_id_list.append(item.id)
                domain += [('part_id', 'in', part_id_list)]
            if wizard.batch_id:
                domain += [('batch_id', '=', wizard.batch_id)]
            if wizard.state:
                domain += [('state', '=', wizard.state)]


        # print self.vendor_id
        mm_create_ids = []
        result = self.env['iac.purchase.order.im.special.approval.import'].search(domain)
        for item in result:

            mm_exist = self.env['iac.purchase.order.mm.special.approval.create'].search([('im_upload_id','=',item.id)])
            if not mm_exist:
                ih_exist = self.env['inforecord.history'].search([('part_id','=',item.part_id.id),('plant_id','=',item.plant_id.id),
                                                                  ('vendor_id','=',self.vendor_id.id),
                                                                  ('valid_from','<=',datetime.now().strftime('%Y-%m-%d')),
                                                                  ('valid_to','>=',datetime.now().strftime('%Y-%m-%d'))])
                if ih_exist:
                    delivery_date = (datetime.now() + timedelta(days=int(ih_exist.ltime))).strftime('%Y-%m-%d')
                    # print int(ih_exist.ltime)
                else:
                    part_exist = self.env['material.master'].browse(item.part_id.id)
                    if part_exist:
                        delivery_date = (datetime.now() + timedelta(days=int(part_exist.ltime))).strftime('%Y-%m-%d')
                    else:
                        delivery_date = datetime.now().strftime('%Y-%m-%d')
                vals = {
                    'im_upload_id':item.id,
                    'vendor_id':self.vendor_id.id,
                    'buyer_id':self.buyer_id.id,
                    'document_type':self.document_type,
                    'plant_id':item.plant_id.id,
                    'state':item.state,
                    'storage_location':self.storage_location.storage_location,
                    'part_id':item.part_id.id,
                    'division_id':item.division_id.id,
                    'delivery_date':delivery_date

                }
                mm_id = self.env['iac.purchase.order.mm.special.approval.create'].create(vals)
                mm_id.env.cr.commit()
                mm_create_ids.append(mm_id.id)
                delivery_date = ''

            else:
                # print (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                # print datetime.now().strftime('%Y-%m-%d')
                if mm_exist.state == 'im uploaded' or mm_exist.state == 'sap fail':
                    ih_exist = self.env['inforecord.history'].search(
                        [('part_id', '=', item.part_id.id), ('plant_id', '=', item.plant_id.id),
                         ('vendor_id', '=', self.vendor_id.id),
                         ('valid_from', '<=', datetime.now().strftime('%Y-%m-%d')),
                         ('valid_to', '>=', datetime.now().strftime('%Y-%m-%d'))])
                    if ih_exist:
                        delivery_date = (datetime.now() + timedelta(days=int(ih_exist.ltime))).strftime('%Y-%m-%d')
                        # print int(ih_exist.ltime)
                    else:
                        part_exist = self.env['material.master'].browse(item.part_id.id)
                        if part_exist:
                            delivery_date = (datetime.now() + timedelta(days=int(part_exist.ltime))).strftime(
                                '%Y-%m-%d')
                        else:
                            delivery_date = datetime.now().strftime('%Y-%m-%d')
                    vals = {
                        'buyer_id':self.buyer_id.id,
                        'document_type':self.document_type,
                        'storage_location': self.storage_location.storage_location,
                        'vendor_id':self.vendor_id.id,
                        'delivery_date':delivery_date
                    }
                    mm_exist.write(vals)
                    mm_create_ids.append(mm_exist.id)
                    delivery_date = ''
                else:
                    mm_create_ids.append(mm_exist.id)

            # print '*54:', result

        action = {
            'domain': [('id', 'in',mm_create_ids)],
            'name': _('MM Create'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.purchase.order.mm.special.approval.create'
        }
        return action


class IacPurchaseOrderApprovalLog(models.Model):

    _name = 'iac.purchase.order.special.approval.audit.log'

    im_upload_id = fields.Many2one('iac.purchase.order.im.special.approval.import')
    mm_submit_id = fields.Many2one('iac.purchase.order.mm.special.approval.create')
    action_type = fields.Char()
    comment = fields.Char()

    @api.multi
    def New_audit_log(self,im_upload_id,mm_submit_id,action_type,comment):
        val = {
            'im_upload_id':im_upload_id,
            'mm_submit_id':mm_submit_id,
            'action_type':action_type,
            'comment':comment
        }
        self.env['iac.purchase.order.special.approval.audit.log'].create(val)


class IacPurchaseOrderMMApprovalGroup(models.Model):

    _name = "iac.purchase.order.mm.special.approval.create.group"

    group_ids = fields.One2many('iac.purchase.order.mm.special.approval.create','group_id')