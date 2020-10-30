# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
import time,base64
import traceback
from StringIO import StringIO
import xlwt
import psycopg2
import logging
from odoo.osv.osv import osv
import os
import datetime


_logger = logging.getLogger(__name__)


class IacVendorControlTable(models.Model):
    _inherit="iac.vendor"
    _name='iac.vendor.control.table'
    _table='iac_vendor'


class ControlTable(models.Model):
    _name = 'iac.control.table'


    plant_code = fields.Many2one('pur.org.data','Plant Code *',domain=lambda self:[('id','in',self.env.user.plant_id_list)])
    type = fields.Char(readonly=True,default='ALL')
    buyer = fields.Many2one('buyer.code','Buyer Code *',domain=lambda self:[('id','in',self.env.user.buyer_id_list)],index=True)
    vendor = fields.Char(string="Vendor Code *")
    vendor_id = fields.Many2one('iac.vendor.control.table',string="Vendor Info")
    b2b_control = fields.Char(readonly=True,string="B2B Control",default='Y')
    pulling_type = fields.Many2one('iac.control.table.newtable','Pulling Type *')
    trans_lt = fields.Integer(string="Trans_LT *")
    safety_lt = fields.Integer(readonly=True,string="Safety_LT")
    frequency = fields.Integer(readonly=True)
    operator = fields.Many2one('res.users', readonly=True)
    optime = fields.Datetime(readonly=True)
    table_class = fields.Char(default="ALL",readonly=True,string="Class")
    bu = fields.Char(default="ALL",readonly=True )
    frequency_pr = fields.Integer(readonly=True,string="Frequency_PR")
    eta_trans = fields.Integer(string="ETA_Trans *")
    reason = fields.Text()
    group_id = fields.Many2one('iac.control.table.group')
    # group_id_next = fields.Integer()
    state = fields.Selection([
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('in review', 'In Review'),  # buyer review后提交webflow签核，送签
        ('fp error', 'FP Error') , # 通知FP失敗
        ('approved', 'Approved'),#webflow送簽成功
        ('finished','Finished'),#更新FP成功
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(readonly=True)
    orig_pulling_type = fields.Char()
    orig_trans_lt = fields.Integer()
    orig_eta_trans = fields.Integer()
    webflow_number = fields.Char(readonly=True,string='Webflow Number')
    x1 = fields.Integer(string='Vessel Booking ->Vendor ->Hub->MY',default=0)
    x2 = fields.Integer(string='IACP->MY',default=0)
    x3 = fields.Integer(string='PGI->MY',default=0)
    x4 = fields.Integer(string='Vendor ->Hub->MY',default=0)
    x5 = fields.Integer(string='IACP->IANB',default=0)



    @api.onchange('pulling_type')
    def onchange_pulling_type(self):
        if self.pulling_type.pulling_type == 'SOI':
            self.frequency = 3
            self.frequency_pr = 7
            self.safety_lt = 0
        if self.pulling_type.pulling_type == 'JIT':
            self.frequency = 1
            self.frequency_pr = 3
            self.safety_lt = 0

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record['vendor']:
                name = record['vendor']
            else:
                name = ''
            if record['buyer']:
                name = record['buyer'].buyer_erp_id + ' ' + name
            res.append((record['id'], name))
        return res
    @api.model
    def create(self, values):
        #print self.env.user.buyer_id_list


        if not values['trans_lt']:
            raise UserError(_(u'Trans_LT不能为空！'))
        if not values['eta_trans']:
            raise UserError(_(u'ETA_Trans不能为空！'))
        if values['trans_lt'] < 0:
            raise UserError(_(u'Trans_LT不能为負值！'))
        if values['eta_trans'] < 0:
            raise UserError(_(u'ETA_Trans不能为負值！'))
        if values['x1'] < 0:
            raise UserError('Vessel Booking ->Vendor ->Hub->MY不能小于0')
        if values['x2'] < 0:
            raise UserError('IACP->MY不能小于0')
        if values['x3'] < 0:
            raise UserError('PGI->MY不能小于0')
        if values['x4'] < 0:
            raise UserError('Vendor ->Hub->MY不能小于0')
        if values['x5'] < 0:
            raise UserError('IACP->IANB不能小于0')
        if values['x1'] > 1000:
            raise UserError('Vessel Booking ->Vendor ->Hub->MY不能大于1000')
        if values['x2'] > 1000:
            raise UserError('IACP->MY不能大于1000')
        if values['x3'] > 1000:
            raise UserError('PGI->MY不能大于1000')
        if values['x4'] > 1000:
            raise UserError('Vendor ->Hub->MY不能大于1000')
        if values['x5'] > 1000:
            raise UserError('IACP->IANB不能大于1000')
        #print self._uid
        values['optime'] = fields.datetime.now()
        values['operator'] = self._uid
        # print self.operator
        # print self
        if values['pulling_type']:
            pulling_type_create = self.env['iac.control.table.newtable'].browse(values['pulling_type'])
            values['frequency'] = pulling_type_create.frequency
            values['frequency_pr'] = pulling_type_create.frequency_pr
            values['safety_lt'] = pulling_type_create.safety_lt
        if values.get('vendor',False):
            if values['vendor'].isdigit():
                if len(values['vendor']) <= 10:
                    final_num = str(values['vendor'].zfill(10))

                    vendor_exist = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', final_num)])

                    if len(vendor_exist) > 0:
                        vendor_create = self.env['iac.control.table'].search([('vendor', '=', final_num)])
                        if vendor_create:
                            if values.get('buyer', False):

                                for r in range(len(vendor_create)):
                                    #print vendor_create[r].buyer.id
                                    #print values['buyer']
                                    if vendor_create[r].buyer.id == values['buyer']:
                                        raise exceptions.ValidationError("Control table already exists")
                                values['vendor'] = final_num
                                values['vendor_id'] = vendor_exist.id
                                change = super(ControlTable, self).create(values)

                                return change


                        else:
                            values['vendor'] = final_num
                            values['vendor_id'] = vendor_exist.id
                            change = super(ControlTable, self).create(values)

                            return change
                    else:
                        raise exceptions.ValidationError(values['vendor'] + u'不存在')
                else:
                    raise exceptions.ValidationError(values['vendor'] + u'不存在')
            else:
                vendor_exist = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', values['vendor'])])

                if len(vendor_exist) > 0:
                    vendor_create = self.env['iac.control.table'].search([('vendor', '=', values['vendor'])])
                    if vendor_create:
                        if values.get('buyer', False):

                            for r in range(len(vendor_create)):
                                # print vendor_create[r].buyer.id
                                # print values['buyer']
                                if vendor_create[r].buyer.id == values['buyer']:
                                    raise exceptions.ValidationError("Control table already exists")
                            # values['vendor'] = values['vendor']
                            values['vendor_id'] = vendor_exist.id
                            change = super(ControlTable, self).create(values)

                            return change


                    else:
                        # values['vendor'] = final_num
                        values['vendor_id'] = vendor_exist.id
                        change = super(ControlTable, self).create(values)

                        return change
                else:
                    raise exceptions.ValidationError(values['vendor'] + u'不存在')
            # else:
            #     raise exceptions.ValidationError(values['vendor'] + u'輸入有誤')
    @api.multi
    def new_create(self,value):
        order_change = super(ControlTable, self).create(value)
        return order_change

    @api.multi
    def new_write(self, value):
        if (value.get('plant_code',False) or value.get('buyer',False) or value.get('vendor', False) or value.get('pulling_type', False) or value.get('trans_lt', False) or value.get('eta_trans', False) or value.get('x1', False) or value.get('x2', False) or value.get('x3', False) or value.get('x4',False) or value.get('x5',False) or value.get('trans_lt',-1) ==0 or value.get('eta_trans',-1) ==0 or value.get('x1',-1) ==0 or value.get('x2',-1) ==0 or value.get('x3',-1) ==0 or value.get('x4',-1) ==0 or value.get('x5',-1) ==0):
            value['state'] = 'draft'
            value['state_msg'] = ' '
            value['webflow_number'] = ' '
        order_change = super(ControlTable, self).write(value)
        return order_change

    @api.multi
    def write(self, values):
        # print 1
        if (values.get('plant_code',False) or values.get('buyer',False) or values.get('vendor', False) or values.get('pulling_type', False) or values.get('trans_lt', False)  or values.get('eta_trans', False) or values.get('x1', False) or values.get('x2', False) or values.get('x3', False) or values.get('x4',False) or values.get('x5',False) or values.get('trans_lt',-1) ==0 or values.get('eta_trans',-1) ==0 or values.get('x1',-1) ==0 or values.get('x2',-1) ==0 or values.get('x3',-1) ==0 or values.get('x4',-1) ==0 or values.get('x5',-1) ==0):
            values['state'] = 'draft'
            values['state_msg'] = ' '
            values['webflow_number'] = ' '

        if values.get('trans_lt', False):
            if values['trans_lt'] < 0:
                raise UserError(_(u'Trans_LT不能为負值！'))
        if values.get('eta_trans', False):
            if values['eta_trans'] < 0:
                raise UserError(_(u'ETA_Trans不能为負值！'))
        if values.get('x1',False):
            if values['x1'] < 0:
                raise UserError('Vessel Booking ->Vendor ->Hub->MY不能小于0')
            if values['x1'] > 1000:
                raise UserError('Vessel Booking ->Vendor ->Hub->MY不能大于1000')
        if values.get('x2',False):
            if values['x2'] < 0:
                raise UserError('IACP->MY不能小于0')
            if values['x2'] > 1000:
                raise UserError('IACP->MY不能大于1000')
        if values.get('x3',False):
            if values['x3'] < 0:
                raise UserError('PGI->MY不能小于0')
            if values['x3'] > 1000:
                raise UserError('PGI->MY不能大于1000')
        if values.get('x4',False):
            if values['x4'] < 0:
                raise UserError('Vendor ->Hub->MY不能小于0')
            if values['x4'] > 1000:
                raise UserError('Vendor ->Hub->MY不能大于1000')
        if values.get('x5',False):
            if values['x5'] < 0:
                raise UserError('IACP->IANB不能小于0')
            if values['x5'] > 1000:
                raise UserError('IACP->IANB不能大于1000')

        values['optime'] = fields.datetime.now()
        values['operator'] = self._uid

        # print self.operator
        if values.get('pulling_type', False):
            pulling_type_create = self.env['iac.control.table.newtable'].browse(values['pulling_type'])
            values['frequency'] = pulling_type_create.frequency
            values['frequency_pr'] = pulling_type_create.frequency_pr
            values['safety_lt'] = pulling_type_create.safety_lt
            change = super(ControlTable, self).write(values)

            return change
        elif values.get('vendor',False):
            if values['vendor'].isdigit():
                if len(values['vendor']) <= 10:
                    final_num = values['vendor'].zfill(10)
                    vendor_exist = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', final_num)])
                    if len(vendor_exist) > 0:
                        vendor_create = self.env['iac.control.table'].search([('vendor', '=', final_num)])

                        if vendor_create:
                            if values.get('buyer', False):
                                for r in range(len(vendor_create)):

                                    if vendor_create[r].buyer.id == values['buyer']:
                                        raise exceptions.ValidationError("Control table already exists")
                                values['vendor'] = final_num
                                change = super(ControlTable, self).write(values)

                                return change
                            else:
                                for r in range(len(vendor_create)):

                                    if vendor_create[r].buyer.id == self.buyer.id:
                                        raise exceptions.ValidationError("Control table already exists")
                                values['vendor'] = final_num
                                values['vendor_id'] = vendor_exist.id
                                change = super(ControlTable, self).write(values)

                                return change
                        else:
                            values['vendor'] = final_num
                            values['vendor_id'] = vendor_exist.id
                            change = super(ControlTable, self).write(values)

                            return change

                    else:
                        raise exceptions.ValidationError(values['vendor'] + u'不存在')
                else:
                    raise exceptions.ValidationError(values['vendor'] + u'不存在')
            else:
                # raise exceptions.ValidationError(values['vendor'] + u'輸入有誤')

                vendor_exist = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', values['vendor'])])
                if len(vendor_exist) > 0:
                    vendor_create = self.env['iac.control.table'].search([('vendor', '=', values['vendor'])])

                    if vendor_create:
                        if values.get('buyer', False):
                            for r in range(len(vendor_create)):

                                if vendor_create[r].buyer.id == values['buyer']:
                                    raise exceptions.ValidationError("Control table already exists")
                            # values['vendor'] = final_num
                            change = super(ControlTable, self).write(values)

                            return change
                        else:
                            for r in range(len(vendor_create)):

                                if vendor_create[r].buyer.id == self.buyer.id:
                                    raise exceptions.ValidationError("Control table already exists")
                            # values['vendor'] = final_num
                            values['vendor_id'] = vendor_exist.id
                            change = super(ControlTable, self).write(values)

                            return change
                    else:
                        # values['vendor'] = final_num
                        values['vendor_id'] = vendor_exist.id
                        change = super(ControlTable, self).write(values)

                        return change

                else:
                    raise exceptions.ValidationError(values['vendor'] + u'不存在')
        elif values.get('buyer',False):
            buyer_create = self.env['iac.control.table'].search([('buyer', '=', values['buyer'])])

            if buyer_create:
                if not values.get('vendor',False):
                    for r in range(len(buyer_create)):
                        print buyer_create[r].vendor
                        print self.vendor
                        if buyer_create[r].vendor == self.vendor:

                            raise exceptions.ValidationError("Control table already exists")
                    change = super(ControlTable, self).write(values)

                    return change
            else:
                change = super(ControlTable, self).write(values)

                return change
        else:
            change = super(ControlTable, self).write(values)

            return change


    @api.multi
    def button_to_approve(self):
        val = {}
        change = self.env['iac.control.table.group'].create(val)
        change1 = self.env['iac.control.table.group'].create(val)

        #print change.id
        record = 0
        record1 = 0
        for item in self.ids:
            #print order
            buyer_item = self.env['iac.control.table'].browse(item)
            # print buyer_item.operator.id


            #print buyer_order.vendor
            if buyer_item.state == 'in review' or buyer_item.state == 'finished' or buyer_item.state == 'approved' or buyer_item.state == 'fp error':
                print 1

            else:

                buyer_exist = self.env['iac.control.table.real'].search([('buyer', '=', buyer_item.buyer.buyer_erp_id) ,('vendor', '=', buyer_item.vendor)])

                if len(buyer_exist) > 0:
                    #record = 1

                    if ((buyer_item.pulling_type.pulling_type == 'SOI' and buyer_exist.pulling_type == 'JIT') or (buyer_item.trans_lt > buyer_exist.trans_lt)):
                        record = 1
                        vals = {}
                        vals['group_id'] = change.id
                        vals['orig_pulling_type'] = buyer_exist.pulling_type
                        vals['orig_trans_lt'] = buyer_exist.trans_lt
                        vals['orig_eta_trans'] = buyer_exist.eta_trans
                        buyer_item.new_write(vals)
                        buyer_item.env.cr.commit()
                        if not buyer_item.reason:
                            raise UserError(_(u'reason不能为空！'))
                        #if buyer_item.state == 'draft':
                            #buyer_item.write({'state': 'in review'})
                        #print 2

                    if ((buyer_item.trans_lt <= buyer_exist.trans_lt) and not(buyer_item.pulling_type.pulling_type == 'SOI' and buyer_exist.pulling_type == 'JIT')):
                        record1 = 2

                        if buyer_item.state == 'draft':
                            buyer_item.new_write({'state': 'finished','group_id':change1.id})
                            buyer_item.env.cr.commit()
                        # print buyer_item.operator.id


                else:
                    # print self.plant_code.plant_code
                    # print self.buyer.buyer_code
                    # print self.vendor
                    # print self.pulling_type.pulling_type

                    record1 = 3

                    if buyer_item.state == 'draft':
                        buyer_item.new_write({'state': 'finished','group_id':change1.id})
                        buyer_item.env.cr.commit()
                    # print buyer_item.operator
        # print self.group_id_next

        if record1 ==2 or record1==3:
            self.sudo().button_to_fp(change1.id)


        if record == 1:
            biz_object = {
                "id": change.id,
                "biz_object_id": change.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "F08_B", biz_object)
            control_table_group = self.env['iac.control.table'].search(
                [('group_id', '=', change.id)])
            message = ''
            if rpc_result:
                # control_table_group.write({'state': 'in review','webflow_number': rpc_json_data.get('EFormNO'),'state_msg': u'送签成功'})
                for control_table in control_table_group:
                    control_table.new_write({'state': 'in review','webflow_number': rpc_json_data.get('EFormNO'),'state_msg': u'送签成功'})

                message = u'送签成功'
            else:
                for control_table in control_table_group:
                    control_table.new_write({'webflow_number': rpc_json_data.get('EFormNO'),'state_msg': u'送签失败'})
                message = u'送签失败'

            title = _("Tips for %s") % change.id
            return self.env['warning_box'].info(title=title,message=message)

    @api.multi
    def button_to_fp(self, object_id=None):
        #print self
        #ning add 181123 判断call fp的方式
        if type(object_id) == int:
            control_table_group_id = self.browse(object_id).id
        else:
            control_table_group_id = self.group_id.id

        # 调用FP接口
        biz_object = {
            "id": control_table_group_id,
            "biz_object_id": control_table_group_id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_FP_001", biz_object)
        control_table_group = self.env['iac.control.table'].search(
            [('group_id', '=', control_table_group_id)])
        if rpc_result:
            # control_table_group.write({'state': 'finished', 'state_msg': u'通知FP成功'})
            for item in control_table_group:
                item.new_write({'state': 'finished', 'state_msg': u'通知FP成功'})
                control_table_real = self.env['iac.control.table.real'].search(
                    [('vendor', '=', item.vendor), ('buyer', '=', item.buyer.buyer_erp_id)])
                if not control_table_real:
                    save_vals = {}
                    save_vals['plant_code'] = item.plant_code.plant_code
                    save_vals['plant_id'] = item.plant_code.id
                    save_vals['type'] = item.type
                    save_vals['buyer'] = item.buyer.buyer_erp_id
                    save_vals['buyer_id'] = item.buyer.id
                    save_vals['vendor'] = item.vendor
                    save_vals['b2b_control'] = item.b2b_control
                    save_vals['pulling_type'] = item.pulling_type.pulling_type
                    save_vals['trans_lt'] = item.trans_lt
                    save_vals['safety_lt'] = item.safety_lt
                    save_vals['frequency'] = item.frequency
                    save_vals['operator'] = item.operator.id
                    save_vals['optime'] = item.optime
                    save_vals['ctrl_class'] = item.table_class
                    save_vals['bu'] = item.bu
                    save_vals['frequency_pr'] = item.frequency_pr
                    save_vals['eta_trans'] = item.eta_trans
                    save_vals['x1'] = item.x1
                    save_vals['x2'] = item.x2
                    save_vals['x3'] = item.x3
                    save_vals['x4'] = item.x4
                    save_vals['x5'] = item.x5
                    item.env["iac.control.table.real"].sudo().create(save_vals)
                    item.env["iac.control.table.history"].sudo().create(save_vals)
                else:
                    save_val = {}
                    save_val['plant_code'] = control_table_real.plant_code
                    save_val['plant_id'] = control_table_real.plant_id.id
                    save_val['type'] = control_table_real.type
                    save_val['buyer'] = control_table_real.buyer
                    save_val['buyer_id'] = control_table_real.buyer_id.id
                    save_val['vendor'] = control_table_real.vendor
                    save_val['b2b_control'] = control_table_real.b2b_control
                    save_val['pulling_type'] = control_table_real.pulling_type
                    save_val['trans_lt'] = control_table_real.trans_lt
                    save_val['safety_lt'] = control_table_real.safety_lt
                    save_val['frequency'] = control_table_real.frequency
                    save_val['operator'] = control_table_real.operator.id
                    save_val['optime'] = control_table_real.optime
                    save_val['ctrl_class'] = control_table_real.ctrl_class
                    save_val['bu'] = control_table_real.bu
                    save_val['frequency_pr'] = control_table_real.frequency_pr
                    save_val['eta_trans'] = control_table_real.eta_trans
                    save_val['x1'] = item.x1
                    save_val['x2'] = item.x2
                    save_val['x3'] = item.x3
                    save_val['x4'] = item.x4
                    save_val['x5'] = item.x5
                    control_table_real.env["iac.control.table.history"].sudo().create(save_val)
                    save_vals = {}
                    save_vals['plant_code'] = item.plant_code.plant_code
                    save_vals['plant_id'] = item.plant_code.id
                    save_vals['type'] = item.type
                    save_vals['buyer'] = item.buyer.buyer_erp_id
                    save_vals['buyer_id'] = item.buyer.id
                    save_vals['vendor'] = item.vendor
                    save_vals['b2b_control'] = item.b2b_control
                    save_vals['pulling_type'] = item.pulling_type.pulling_type
                    save_vals['trans_lt'] = item.trans_lt
                    save_vals['safety_lt'] = item.safety_lt
                    save_vals['frequency'] = item.frequency
                    save_vals['operator'] = item.operator.id
                    save_vals['optime'] = item.optime
                    save_vals['ctrl_class'] = item.table_class
                    save_vals['bu'] = item.bu
                    save_vals['frequency_pr'] = item.frequency_pr
                    save_vals['eta_trans'] = item.eta_trans
                    save_vals['x1'] = item.x1
                    save_vals['x2'] = item.x2
                    save_vals['x3'] = item.x3
                    save_vals['x4'] = item.x4
                    save_vals['x5'] = item.x5
                    control_table_real.sudo().write(save_vals)
            return True
        else:
            for control_table in control_table_group:
                control_table.new_write({'state': 'fp error', 'state_msg': u'通知FP失败'})
            return False

    def control_table_callback(self, context=None):
        """
        回调函数说明
        供应商提供银行资料后审核通过变更为正常状态
        模型为 iac.vendor
        context={"approve_status": True,"data":{"id":1376,}}

        返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
        :param context:
        :return:
        """
        proc_result = False
        proc_ex = []
        try:
            # 校验接口入参
            if not context["approve_status"] or not context.get("data") or not context.get("data").get("id"):
                proc_result = False
                proc_ex.append(u"接口调用参数异常")
                _logger(u"接口调用参数异常")
                return proc_result, proc_ex
            else:
                if context["approve_status"] and context["rpc_callback_data"]["FormStatus"] == "C":
                    control_table_id = self.browse(context.get("data").get("id"))

                    control_table_group = self.env['iac.control.table'].search(
                        [('group_id', '=', control_table_id.id)])
                    for control_table in control_table_group:
                        control_table.new_write({'state': 'approved','state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 调用FP接口
                    if self.button_to_fp(context.get("data").get("id")):
                        proc_result = True
                        return proc_result, proc_ex
                    else:
                        proc_result = True
                        proc_ex.append(u'通知FP失败')
                        return proc_result, proc_ex



                else:
                    control_table_id = self.browse(context.get("data").get("id"))
                    control_table_group = self.env['iac.control.table'].search(
                        [('group_id', '=', control_table_id.id)])
                    for control_table in control_table_group:
                        control_table.new_write(
                        {'state': 'draft', 'state_msg': u'webflow(%s)签核未通过' % context["rpc_callback_data"]["EFormNO"]})

                proc_result = True
                return proc_result, proc_ex
        except:
            ex_string = traceback.format_exc()
            proc_result = False
            proc_ex.append(ex_string)
            traceback.print_exc()
            return proc_result, proc_ex


class DocumentUpload(models.Model):
    _name = 'iac.control.table.upload'
    buyer = fields.Many2one('buyer.code', 'Buyer Code',domain=lambda self:[('id','in',self.env.user.buyer_id_list)])
    excel = fields.Binary('File')

    @api.multi
    def action_confirm(self):

        if len(self.buyer) == 0 or self.excel==None:
            raise exceptions.ValidationError('Please select Buyer Code or File.')
        excel_obj = open_workbook(file_contents=base64.decodestring(self.excel))
        sheet_obj = excel_obj.sheet_by_index(0)
        # sc_list = self.env['iac.supplier.company'].search_read([('company_no', '!=', ''),
        #                                                         ('current_class', 'not in', ['D', 'DW'])],
        #                                                        ['id', 'create_date', 'current_class', 'class_date'])

        if sheet_obj.cell(0,0).value == 'plant_code' and sheet_obj.cell(0,1).value == 'vendor_code' and sheet_obj.cell(0,2).value == 'pulling_type' and sheet_obj.cell(0,3).value == 'trans_lt' and sheet_obj.cell(0,4).value == 'eta_trans' and sheet_obj.cell(0,5).value == 'reason' and sheet_obj.cell(0,6).value == 'Vessel Booking ->Vendor ->Hub->MY' and sheet_obj.cell(0,7).value == 'IACP->MY' and sheet_obj.cell(0,8).value == 'PGI->MY' and sheet_obj.cell(0,9).value == 'Vendor ->Hub->MY' and sheet_obj.cell(0,10).value == 'IACP->IANB':

            for rx in range(sheet_obj.nrows):
                if rx >= 1:
                    #print self.buyer.buyer_code
                    save_vals = {}
                    plant_exist = self.env['pur.org.data'].search([('plant_code','=',sheet_obj.cell(rx,0).value.upper())])
                    if len(plant_exist) > 0:
                        save_vals['plant_code'] = plant_exist.id
                    else:
                        raise exceptions.ValidationError(sheet_obj.cell(rx, 0).value + u'不存在')


                    # if str(sheet_obj.cell(rx,1).value).isdigit():
                    if type(sheet_obj.cell(rx,1).value) == float:
                        if len(str(int(sheet_obj.cell(rx, 1).value))) <= 10:
                            final_num =  str(int(sheet_obj.cell(rx, 1).value)).zfill(10)
                            vendor_exist = self.env['iac.vendor.control.table'].sudo().search([('vendor_code','=',final_num)])
                            if len(vendor_exist) > 0:
                                save_vals['vendor'] = final_num

                            else:
                                raise exceptions.ValidationError(str(int(sheet_obj.cell(rx, 1).value)) + '不存在')
                        else:
                            raise exceptions.ValidationError(str(int(sheet_obj.cell(rx, 1).value)) + '不存在')

                    else:
                        raise exceptions.ValidationError(sheet_obj.cell(rx, 1).value + u'輸入有誤')
                    save_vals['buyer'] = self.buyer.id

                    if sheet_obj.cell(rx, 2).value.upper() == 'SOI':
                        save_vals['pulling_type'] = 1
                    elif sheet_obj.cell(rx, 2).value.upper() == 'JIT':
                        save_vals['pulling_type'] = 2
                    elif isinstance(sheet_obj.cell(rx, 2).value, float):
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 2).value)+'輸入有誤')
                    else:
                        raise exceptions.ValidationError(sheet_obj.cell(rx, 2).value+u'輸入有誤')

                    #print type(sheet_obj.cell(rx,3).value)
                    if type(sheet_obj.cell(rx,3).value) == float:
                        num = int(sheet_obj.cell(rx,3).value)
                        if num >= 0:

                            save_vals['trans_lt'] = num
                        else:
                            raise exceptions.ValidationError(sheet_obj.cell(rx, 3).value + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(sheet_obj.cell(rx, 3).value + u'輸入有誤')
                    if type(sheet_obj.cell(rx, 4).value) == float:
                        num1 = int(sheet_obj.cell(rx, 4).value)
                        if num1 >= 0:

                            save_vals['eta_trans'] = num1
                        else:
                            raise exceptions.ValidationError(sheet_obj.cell(rx, 4).value + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(sheet_obj.cell(rx, 4).value + u'輸入有誤')
                    save_vals['reason'] = sheet_obj.cell(rx, 5).value
                    if type(sheet_obj.cell(rx,6).value) == float:
                        num = int(sheet_obj.cell(rx,6).value)
                        if num >= 0 and num<=1000:

                            save_vals['x1'] = num
                        else:
                            raise exceptions.ValidationError(str(sheet_obj.cell(rx, 6).value) + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 6).value) + u'輸入有誤')
                    if type(sheet_obj.cell(rx,7).value) == float:
                        num = int(sheet_obj.cell(rx,7).value)
                        if num >= 0 and num<=1000:

                            save_vals['x2'] = num
                        else:
                            raise exceptions.ValidationError(str(sheet_obj.cell(rx, 7).value) + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 7).value) + u'輸入有誤')

                    if type(sheet_obj.cell(rx,8).value) == float:
                        num = int(sheet_obj.cell(rx,8).value)
                        if num >= 0 and num<=1000:

                            save_vals['x3'] = num
                        else:
                            raise exceptions.ValidationError(str(sheet_obj.cell(rx, 8).value) + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 8).value) + u'輸入有誤')

                    if type(sheet_obj.cell(rx,9).value) == float:
                        num = int(sheet_obj.cell(rx,9).value)
                        if num >= 0 and num<=1000:

                            save_vals['x4'] = num
                        else:
                            raise exceptions.ValidationError(str(sheet_obj.cell(rx, 9).value) + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 9).value) + u'輸入有誤')
                    if type(sheet_obj.cell(rx,10).value) == float:
                        num = int(sheet_obj.cell(rx,10).value)
                        if num >= 0 and num<=1000:

                            save_vals['x5'] = num
                        else:
                            raise exceptions.ValidationError(str(sheet_obj.cell(rx, 10).value) + u'輸入有誤')
                    else:
                        raise exceptions.ValidationError(str(sheet_obj.cell(rx, 10).value) + u'輸入有誤')
                    self.env["iac.control.table.temporary"].create(save_vals)
                    # buyer_item.env.cr.commit()

            change = self.env["iac.control.table.temporary"].search([('state','=','draft')])
            for item in change:

                is_exist = item.search([('vendor','=',item.vendor),('buyer','=',item.buyer),('state','=','draft')])
                #print item.plant_code
                #print len(is_exist)
                if len(is_exist) > 1:
                    raise exceptions.ValidationError('上傳的內容有重複,請檢查後重新上傳.')
                else:
                    buyer = int(item.buyer)
                    # print buyer
                    control_table_exist = self.env["iac.control.table"].search(
                        [('vendor', '=', item.vendor), ('buyer', '=', buyer)])
                    # print control_table_exist

                    if len(control_table_exist) > 0:
                        save_vals = {}
                        save_vals['plant_code'] = item.plant_code.id
                        save_vals['vendor'] = item.vendor
                        vendor_find = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', item.vendor)])
                        save_vals['vendor_id'] = vendor_find.id
                        save_vals['pulling_type'] = item.pulling_type
                        save_vals['operator'] = self._uid
                        save_vals['optime'] = fields.datetime.now()
                        save_vals['trans_lt'] = item.trans_lt
                        save_vals['eta_trans'] = item.eta_trans
                        save_vals['reason'] = item.reason
                        save_vals['buyer'] = buyer
                        save_vals['x1'] = item.x1
                        save_vals['x2'] = item.x2
                        save_vals['x3'] = item.x3
                        save_vals['x4'] = item.x4
                        save_vals['x5'] = item.x5
                        pulling_type_create = self.env['iac.control.table.newtable'].browse(int(item.pulling_type))
                        save_vals['frequency'] = pulling_type_create.frequency
                        save_vals['frequency_pr'] = pulling_type_create.frequency_pr
                        save_vals['safety_lt'] = pulling_type_create.safety_lt
                        if control_table_exist.state == 'in review':
                            raise exceptions.ValidationError('有正在送簽中的記錄,請檢查後重新上傳.')
                        elif control_table_exist.state == 'approved':
                            raise exceptions.ValidationError('有待通知FP的記錄,請檢查後重新上傳.')
                        elif control_table_exist.state == 'fp error':
                            raise exceptions.ValidationError('有通知FP失敗的記錄,請檢查後重新上傳.')
                        else:
                            control_table_exist.write({'state': 'draft'})
                            control_table_exist.new_write(save_vals)
                            item.write({'state': 'finished'})
                    else:
                        save_vals = {}

                        save_vals['plant_code'] = item.plant_code.id
                        save_vals['vendor'] = item.vendor
                        vendor_find = self.env['iac.vendor.control.table'].sudo().search([('vendor_code', '=', item.vendor)])
                        save_vals['vendor_id'] = vendor_find.id
                        save_vals['pulling_type'] = item.pulling_type
                        save_vals['operator'] = self._uid
                        save_vals['optime'] = fields.datetime.now()
                        save_vals['trans_lt'] = item.trans_lt
                        save_vals['eta_trans'] = item.eta_trans
                        save_vals['reason'] = item.reason
                        save_vals['buyer'] = buyer
                        save_vals['x1'] = item.x1
                        save_vals['x2'] = item.x2
                        save_vals['x3'] = item.x3
                        save_vals['x4'] = item.x4
                        save_vals['x5'] = item.x5
                        pulling_type_create = self.env['iac.control.table.newtable'].browse(int(item.pulling_type))
                        save_vals['frequency'] = pulling_type_create.frequency
                        save_vals['frequency_pr'] = pulling_type_create.frequency_pr
                        save_vals['safety_lt'] = pulling_type_create.safety_lt
                        self.env['iac.control.table'].new_create(save_vals)

                        item.write({'state': 'finished'})


        else:
            raise exceptions.ValidationError('上傳的Excel內容格式不正確,请检查內容是否匹配.')
        return self.env['warning_box'].info(title='提示信息', message='上传成功')

    @api.multi
    def action_confirm_download(self):
        """
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """
        header_field_list = []
        header_field_list = ['plant_code', 'vendor_code', 'pulling_type', 'trans_lt', 'eta_trans', 'reason','Vessel Booking ->Vendor ->Hub->MY','IACP->MY','PGI->MY','Vendor ->Hub->MY','IACP->IANB']

        output = StringIO()
        wb2 = xlwt.Workbook()
        sheet1 = wb2.add_sheet('sheet1', cell_overwrite_ok=True)

        for i in range(0, 11):
            sheet1.write(0, i, header_field_list[i])  # 灰底,黑字

        wb2.save(output)

        # 文件输出成功之后,跳转链接，浏览器下载文件
        vals = {
            'name': 'control_table_report',
            'datas_fname': 'control_table_report.xls',
            'description': 'Control Table Report',
            'type': 'binary',
            'db_datas': base64.encodestring(output.getvalue()),
        }
        file = self.env['ir.attachment'].create(vals)
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s.xls' % (file.id, file.id,),
            'target': 'new',
        }

        return action

class Real_ControlTable(models.Model):
    _name = 'iac.control.table.real'

    plant_code = fields.Char(string='Plant Code',related='plant_id.plant_code')
    plant_id = fields.Many2one('pur.org.data')
    type = fields.Char()
    buyer = fields.Char(string='Buyer Code',related='buyer_id.buyer_erp_id')
    buyer_id = fields.Many2one('buyer.code')
    vendor = fields.Char()
    b2b_control = fields.Char(string='B2B Control')
    pulling_type = fields.Char(string='Pulling Type')
    trans_lt = fields.Integer(string='Trans_LT')
    safety_lt = fields.Integer(string='Safety_LT')
    frequency = fields.Integer()
    operator = fields.Many2one('res.users')
    optime = fields.Datetime()
    ctrl_class = fields.Char(string='Class')
    bu = fields.Char()
    frequency_pr = fields.Integer(string='Frequency_PR')
    eta_trans = fields.Integer(string='ETA_Trans')
    x1 = fields.Integer(string='Vessel Booking ->Vendor ->Hub->MY', default=0)
    x2 = fields.Integer(string='IACP->MY', default=0)
    x3 = fields.Integer(string='PGI->MY', default=0)
    x4 = fields.Integer(string='Vendor ->Hub->MY', default=0)
    x5 = fields.Integer(string='IACP->IANB',default=0)


class Temporary_ControlTable(models.Model):
    _name = 'iac.control.table.temporary'

    plant_code = fields.Many2one('pur.org.data')
    vendor = fields.Char()
    pulling_type = fields.Char()
    trans_lt = fields.Integer()
    eta_trans = fields.Integer()
    buyer = fields.Char()
    reason = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('finished', 'Finished'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    x1 = fields.Integer(string='Vessel Booking ->Vendor ->Hub->MY', default=0)
    x2 = fields.Integer(string='IACP->MY', default=0)
    x3 = fields.Integer(string='PGI->MY', default=0)
    x4 = fields.Integer(string='Vendor ->Hub->MY', default=0)
    x5 = fields.Integer(string='IACP->IANB',default=0)



class History_ControlTable(models.Model):
    _name = 'iac.control.table.history'

    plant_code = fields.Char(related='plant_id.plant_code')
    plant_id = fields.Many2one('pur.org.data')
    type = fields.Char()
    buyer = fields.Char(related='buyer_id.buyer_erp_id')
    buyer_id = fields.Many2one('buyer.code')
    vendor = fields.Char()
    b2b_control = fields.Char()
    pulling_type = fields.Char()
    trans_lt = fields.Integer()
    safety_lt = fields.Integer()
    frequency = fields.Integer()
    operator = fields.Many2one('res.users')
    optime = fields.Datetime()
    ctrl_class = fields.Char()
    bu = fields.Char()
    frequency_pr = fields.Integer()
    eta_trans = fields.Integer()
    x1 = fields.Integer(string='Vessel Booking ->Vendor ->Hub->MY', default=0)
    x2 = fields.Integer(string='IACP->MY', default=0)
    x3 = fields.Integer(string='PGI->MY', default=0)
    x4 = fields.Integer(string='Vendor ->Hub->MY', default=0)
    x5 = fields.Integer(string='IACP->IANB',default=0)

class Group_ControlTable(models.Model):
    _name = 'iac.control.table.group'

    group_ids = fields.One2many('iac.control.table','group_id')



