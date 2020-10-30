# -*- coding: utf-8 -*-

import json
import xlwt
import time, base64
import datetime
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
from odoo import models, fields, api
import psycopg2
import logging
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
import pdb
import math
import traceback
import utility
from iac_rfq_import import IacRfqImport

_logger = logging.getLogger(__name__)


def is_float_valid(str_val):
    """
    返回2个值
    对出现科学计数法的字符串转换为标准字符串
    1   处理是否成功
    2   转换成的数值
    :param str_val:
    :return:
    """
    try:
        float_val = float(str_val)
        # 获取允许范围之外的小数部分
        input_price = float_val

        # 扩大10 的6次方倍
        try_price = input_price * math.pow(10, 6)

        # 减去整数部分获得小数部分
        digits_part = abs(round(try_price - round(try_price), 2))
        price_unit = 0
        # 如果小数部分大于0.0001 那么表示超过6位，反之小于6位
        if (digits_part > 0.0001):
            # 1000的不满足,尝试10000
            return False, "%f" % (float_val,)
        else:
            return True, "%f" % (float_val,)
    except:
        traceback.print_exc()
        pass
    return False, 0


class IacRfqChangeTerm(models.Model):
    """rfq修改交易条件的模型
    """
    _name = 'iac.rfq.change.term'
    _inherit = 'iac.rfq'
    _table = "iac_rfq"

    @api.multi
    def action_send(self):
        # for r in self:
        #     r.send_to_email(r.vendor_id.user_id.partner_id.id)
        self.write({'state': 'rfq', 'type': 'rfq'})

    @api.multi
    def action_cancel(self):
        if self.filtered(lambda x: x.state not in ['draft', 'replay']):
            raise UserError(_('State must be draft or replay!'))
        self.write({'state': 'cancel', 'active': False})

    @api.multi
    def action_restate_rfq(self):
        self.filtered(lambda x: x.state in ['wf_fail', 'sap_fail']).write({'state': 'rfq'})

    @api.model
    def create(self, vals):
        if not vals.get("last_rfq_id", False):
            raise UserError("No RFQ Found !")
        last_rfq_rec = self.env["iac.rfq"].browse(vals["last_rfq_id"])
        # vals["buyer_code"]=last_rfq_rec.buyer_code.id
        # vals["division_id"]=last_rfq_rec.division_id.id
        vals["input_price"] = last_rfq_rec.input_price
        vals["valid_from"] = last_rfq_rec.valid_from
        vals["valid_to"] = last_rfq_rec.valid_to
        vals["currency_id"] = last_rfq_rec.currency_id.id
        vals["price_control"] = last_rfq_rec.price_control
        vals["new_type"] = "change_term"
        vals["type"] = "rfq"
        vals["state"] = "rfq"
        result = super(IacRfqChangeTerm, self).create(vals)
        val = {}
        # print rfq_line.id
        val['rfq_id'] = result.id
        val['create_by'] = self._uid
        val['create_timestamp'] = datetime.datetime.now()
        val['action_type'] = 'MM submit terms change'
        self.env['iac.rfq.quote.history'].create(val)
        result.validate_record()
        return result

    @api.one
    def validate_record(self):
        if self.lt <= 0:
            raise UserError('LTime must greater than zero')
        if self.moq <= 0:
            raise UserError('MOQ must greater than zero')
        if self.mpq <= 0:
            raise UserError('MPQ must greater than zero')
        if self.input_price <= 0:
            raise UserError(_('Price must greater than zero!'))
        if self.mpq > self.moq:
            raise UserError(_('moq must greater than mpq!'))

        # 禁止录入重复数据
        if self.last_rfq_id.exists():
            if self.lt == self.last_rfq_id.lt \
                    and self.moq == self.last_rfq_id.moq \
                    and self.mpq == self.last_rfq_id.mpq \
                    and self.cw == self.last_rfq_id.cw \
                    and self.rw == self.last_rfq_id.rw \
                    and self.valid_from == self.last_rfq_id.valid_from \
                    and self.valid_to == self.last_rfq_id.valid_to \
                    and self.tax == self.last_rfq_id.tax \
                    and self.input_price == self.last_rfq_id.input_price \
                    and self.price_control == self.last_rfq_id.price_control:
                raise UserError(u"存在所有交易条件都相同的RFQ,RFQ 编码为%s" % (self.last_rfq_id.name))

    @api.onchange('vendor_id', 'part_id', 'currency_id')
    def onchange_vendor_id_part_id(self):
        if not self.vendor_id.exists():
            return
        if self.part_id.exists():
            self.buyer_code = self.part_id.buyer_code_id
            self.division_id = self.part_id.division_id

        if not self.vendor_id or not self.part_id or not self.currency_id:
            return

        currency = self.currency_id.name
        if self.plant_id.exists() and self.plant_id.plant_code == 'CP22':
            if currency == 'RMB':
                self.tax = 'J2'
            elif currency == 'TWD':
                self.tax = False
            else:
                self.tax = 'J0'
        elif self.plant_id.exists() and self.plant_id.plant_code == 'CP21':
            pass
        else:
            self.tax = False

        domain = [('part_id', '=', self.part_id.id), ('vendor_id', '=', self.vendor_id.id), ('state', '=', 'sap_ok')]
        domain += [('currency_id', '=', self.currency_id.id)]
        rec = self.search(domain, limit=1, order='create_date desc')
        if rec:
            self.last_rfq_id = rec.id
            self.rfq_price = rec.rfq_price
            self.input_price = rec.input_price
            self.lt = rec.lt
            self.moq = rec.moq
            self.mpq = rec.mpq
            self.cw = rec.cw
            self.rw = rec.rw
            self.tax = rec.tax
            self.valid_from = rec.valid_from
            self.valid_to = rec.valid_to
            self.currency_id = rec.currency_id
            self.price_control = rec.price_control
            self.vendor_part_no = rec.vendor_part_no
            self.reason_code = rec.reason_code

        if not rec.exists():
            self.last_rfq_id = False
            self.rfq_price = 0
            self.input_price = 0
            self.lt = 0
            self.moq = 0
            self.mpq = 0
            self.cw = False
            self.rw = False
            self.tax = False
            self.valid_from = False
            self.valid_to = False
            self.currency_id = False
            self.price_control = False
            self.vendor_part_no = False


class IacRfqChangeTermWizard(models.TransientModel):
    _name = 'iac.rfq.change.term.wizard'
    _inherit = 'iac.file.import'

    @api.multi
    def action_upload_file(self):
        """
        上传文件按钮入口
        :return:
        """

        excel_obj = open_workbook(file_contents=base64.decodestring(self.file))
        sheet_obj = excel_obj.sheet_by_index(0)
        error_str = ''
        error_num1 = ''
        error_num2 = ''
        error_num3 = ''
        error_num4 = ''
        error_num5 = ''
        error_num6 = ''
        error_num7 = ''
        error_num8 = ''
        error_num9 = ''
        error_num10 = ''
        error_num11 = ''
        error_num12 = ''
        error_num13 = ''
        error_num14 = ''
        error_num15 = ''
        error_num16 = ''
        error_num17 = ''
        error_num18 = ''
        error_num19 = ''
        error_num20 = ''
        error_num21 = ''
        error_flag = 0
        validate_list = []
        show_list = []
        slist = []
        slist1 = []
        for rx in range(sheet_obj.nrows):
            if rx >= 1:
                plant_id = self.env['pur.org.data'].search(
                    [('plant_code', '=', (sheet_obj.cell(rx, 0).value).strip())]).id
                vendor_id = self.env['iac.vendor.asn'].search(
                    [('vendor_code', '=', (sheet_obj.cell(rx, 1).value).strip())]).id
                material_id = self.env['material.master.asn'].search(
                    [('part_no', '=', (sheet_obj.cell(rx, 2).value).strip()), ('plant_id', '=', plant_id)]).id

                # 判断plant+vendor+material是否在rfq表存在
                if not self.env['iac.rfq'].search(
                        [('plant_id', '=', plant_id), ('vendor_id', '=', vendor_id), ('part_id', '=', material_id)]):
                    error_num1 = error_num1 + str(rx + 1) + ','
                    error_flag = 1

                # 判断相同RFQ的状态是否能做change_term
                rfq = self.env['iac.rfq'].search(
                    [('plant_id', '=', plant_id), ('vendor_id', '=', vendor_id), ('part_id', '=', material_id)],
                    order='id desc', limit=1)
                if rfq.state not in ('sap_ok', 'cancel'):
                    error_num21 = error_num21 + str(rx + 1) + ','
                    error_flag = 1

                # 判断RW是否存在
                recs = self.env['iac.cw.rw'].search([('code_master_id', '=', 'Reschedule window')])
                for item in recs:
                    slist.append(item.description)
                if sheet_obj.cell(rx, 6).value not in slist:
                    error_num2 = error_num2 + str(rx + 1) + ','
                    error_flag = 1

                # 判断CW是否存在
                recs = self.env['iac.cw.rw'].search([('code_master_id', '=', 'Cancel window')])
                for item in recs:
                    slist1.append(item.description)
                if sheet_obj.cell(rx, 7).value not in slist1:
                    error_num3 = error_num3 + str(rx + 1) + ','
                    error_flag = 1

                # 判断Tax是否存在
                if sheet_obj.cell(rx, 8).value not in (
                        'J0', 'J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'JA', '11', 'V0'):
                    error_num4 = error_num4 + str(rx + 1) + ','
                    error_flag = 1

                # 判断Currency是否存在
                self._cr.execute("select name from res_currency where name = %s",
                                        ((sheet_obj.cell(rx, 9).value).strip(),))
                currency = self.env.cr.fetchall()
                if not currency:
                    error_num5 = error_num5 + str(rx + 1) + ','
                    error_flag = 1

                # LTIME必填
                if not sheet_obj.cell(rx, 3).value:
                    error_num6 = error_num6 + str(rx + 1) + ','
                    error_flag = 1

                # MOQ必填
                if not sheet_obj.cell(rx, 4).value:
                    error_num7 = error_num7 + str(rx + 1) + ','
                    error_flag = 1

                # MPQ必填
                if not sheet_obj.cell(rx, 5).value:
                    error_num8 = error_num8 + str(rx + 1) + ','
                    error_flag = 1

                # plant + vendor + material是否有重复
                plant_part_vendor_str = str((sheet_obj.cell(rx, 0).value).strip()) + \
                                        ',' + str((sheet_obj.cell(rx, 1).value).strip()) + \
                                        ',' + str((sheet_obj.cell(rx, 2).value).strip())
                if plant_part_vendor_str not in validate_list:
                    validate_list.append(plant_part_vendor_str)
                else:
                    show_list.append(plant_part_vendor_str)

                # 判断LTIME是否为非数字
                if isinstance(sheet_obj.cell(rx, 3).value, unicode):
                    error_num9 = error_num9 + str(rx + 1) + ','
                    error_flag = 1

                else:
                    # 判断LTIME是否小于0
                    if sheet_obj.cell(rx, 3).value <= 0:
                        error_num10 = error_num10 + str(rx + 1) + ','
                        error_flag = 1

                    else:
                        # 判断LTIME是否为整数
                        if sheet_obj.cell(rx, 3).value % 1 != 0:
                            error_num11 = error_num11 + str(rx + 1) + ','
                            error_flag = 1

                # 判断MOQ是否为非数字
                if isinstance(sheet_obj.cell(rx, 4).value, unicode):
                    error_num12 = error_num12 + str(rx + 1) + ','
                    error_flag = 1

                else:
                    # 判断MOQ是否小于0
                    if sheet_obj.cell(rx, 4).value <= 0:
                        error_num13 = error_num13 + str(rx + 1) + ','
                        error_flag = 1

                    else:
                        # 判断MOQ是否为整数
                        if sheet_obj.cell(rx, 4).value % 1 != 0:
                            error_num14 = error_num14 + str(rx + 1) + ','
                            error_flag = 1

                # 判断MPQ是否为非数字
                if isinstance(sheet_obj.cell(rx, 5).value, unicode):
                    error_num15 = error_num15 + str(rx + 1) + ','
                    error_flag = 1

                else:
                    # 判断MPQ是否小于0
                    if sheet_obj.cell(rx, 5).value <= 0:
                        error_num16 = error_num16 + str(rx + 1) + ','
                        error_flag = 1

                    else:
                        # 判断MPQ是否为整数
                        if sheet_obj.cell(rx, 5).value % 1 != 0:
                            error_num17 = error_num17 + str(rx + 1) + ','
                            error_flag = 1

                # MOQ必须大于MPQ
                if sheet_obj.cell(rx, 5).value > sheet_obj.cell(rx, 4).value:
                    error_num18 = error_num18 + str(rx + 1) + ','
                    error_flag = 1

                # 检查是否已有所有交易条件都存在的rfq
                old_rfq = self.env['iac.rfq'].search([('plant_id', '=', plant_id),
                                                      ('vendor_id', '=', vendor_id),
                                                      ('part_id', '=', material_id),
                                                      ('state', '=', 'sap_ok')],
                                                     order='valid_from desc, id desc', limit=1)
                if sheet_obj.cell(rx, 3).value == old_rfq.lt and \
                        sheet_obj.cell(rx, 4).value == old_rfq.moq and \
                        sheet_obj.cell(rx, 5).value == old_rfq.mpq and \
                        sheet_obj.cell(rx, 6).value == old_rfq.rw and \
                        sheet_obj.cell(rx, 7).value == old_rfq.cw and \
                        sheet_obj.cell(rx, 8).value == old_rfq.tax and \
                        sheet_obj.cell(rx, 9).value == old_rfq.currency_id.name:
                    error_num20 = error_num20 + str(rx + 1) + ','
                    error_flag = 1

        for item in list(set(show_list)):
            error_num19 = error_num19 + '(' + item + ')' + ','
            error_flag = 1

        if error_num1:
            raise UserError('第' + error_num1 + '行资料错误，在rfq里没有当前plant；vendor和material，请检查！')
        if error_num2:
            raise UserError('第' + error_num2 + '行资料错误，RW不存在，请检查！')
        if error_num3:
            raise UserError('第' + error_num3 + '行资料错误，CW不存在，请检查！')
        if error_num4:
            raise UserError('第' + error_num4 + '行资料错误，TAX不存在，请检查！')
        if error_num5:
            raise UserError('第' + error_num5 + '行资料错误，Currency不存在，请检查！')
        if error_num6:
            raise UserError('第' + error_num6 + '行资料错误，LTIME不能为空，请检查！')
        if error_num7:
            raise UserError('第' + error_num7 + '行资料错误，MOQ不能为空，请检查！')
        if error_num8:
            raise UserError('第' + error_num8 + '行资料错误，MPQ不能为空，请检查！')
        if error_num9:
            raise UserError('第' + error_num9 + '行资料错误，LTIME不能为非数字，请检查！')
        if error_num10:
            raise UserError('第' + error_num10 + '行资料错误，LTIME不能小于0，请检查！')
        if error_num11:
            raise UserError('第' + error_num11 + '行资料错误，LTIME必须是整数，请检查！')
        if error_num12:
            raise UserError('第' + error_num12 + '行资料错误，MOQ不能为非数字，请检查！')
        if error_num13:
            raise UserError('第' + error_num13 + '行资料错误，MOQ不能小于0，请检查！')
        if error_num14:
            raise UserError('第' + error_num14 + '行资料错误，MOQ必须是整数，请检查！')
        if error_num15:
            raise UserError('第' + error_num15 + '行资料错误，MPQ不能为非数字，请检查！')
        if error_num16:
            raise UserError('第' + error_num16 + '行资料错误，MPQ不能小于0，请检查！')
        if error_num17:
            raise UserError('第' + error_num17 + '行资料错误，MPQ必须是整数，请检查！')
        if error_num18:
            raise UserError('第' + error_num18 + '行资料错误，MOQ不能小于MPQ，请检查！')
        if error_num19:
            raise UserError(error_num19 + '存在重复资料，请检查！')
        if error_num20:
            raise UserError('第' + error_num20 + '行资料错误，已经存在所有交易条件都相同的RFQ，请检查！')
        if error_num21:
            raise UserError('第' + error_num21 + '行资料错误，当前RFQ状态正在流程中不能做change term，请检查！')

        if error_flag == 0:
            for rx in range(sheet_obj.nrows):
                if rx >= 1:
                    plant = self.env['pur.org.data'].search(
                        [('plant_code', '=', (sheet_obj.cell(rx, 0).value).strip())])
                    vendor = self.env['iac.vendor.asn'].search(
                        [('vendor_code', '=', (sheet_obj.cell(rx, 1).value).strip())])
                    material = self.env['material.master.asn'].search(
                        [('part_no', '=', (sheet_obj.cell(rx, 2).value).strip()), ('plant_id', '=', plant.id)])
                    currency = self.env['res.currency'].search(
                        [('name', '=', (sheet_obj.cell(rx, 9).value).strip())])

                    last_rfq_rec = self.env["iac.rfq"].search([('plant_id', '=', plant.id),
                                                               ('vendor_id', '=', vendor.id),
                                                               ('part_id', '=', material.id),
                                                               ('state', '=', 'sap_ok')],
                                                              order='valid_from desc, id desc', limit=1)

                    name = self.env['ir.sequence'].next_by_code('iac.rfq')

                    self._cr.execute(
                        'insert into iac_rfq(plant_id,vendor_id,part_id,lt,moq,mpq,rw,cw,tax,currency_id,name,last_rfq_id,'
                        'input_price,valid_from,valid_to,price_control,buyer_code,company_id,new_type,type,state,active,'
                        'price_unit,write_uid,source_code,vendor_part_no,create_date,create_uid,user_id,division_id,'
                        'rfq_price,write_date,change_factor_price,last_price)'
                        'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (plant.id, vendor.id, material.id, sheet_obj.cell(rx, 3).value, sheet_obj.cell(rx, 4).value,
                         sheet_obj.cell(rx, 5).value, sheet_obj.cell(rx, 6).value, sheet_obj.cell(rx, 7).value,
                         sheet_obj.cell(rx, 8).value, currency.id, name, last_rfq_rec.id, last_rfq_rec.input_price,
                         last_rfq_rec.valid_from, last_rfq_rec.valid_to, last_rfq_rec.price_control,
                         last_rfq_rec.buyer_code.id, '1', 'change_term', 'rfq', 'rfq', True,
                         last_rfq_rec.price_unit, self._uid, last_rfq_rec.source_code, last_rfq_rec.vendor_part_no,
                         datetime.datetime.now(), self._uid, self._uid, material.division_id.id, last_rfq_rec.rfq_price,
                         datetime.datetime.now(), last_rfq_rec.change_factor_price, last_rfq_rec.input_price))
                    self.env.cr.commit()

                    result = self.env['iac.rfq'].search([('plant_id', '=', plant.id),
                                                         ('vendor_id', '=', vendor.id),
                                                         ('part_id', '=', material.id),
                                                         ('new_type', '=', 'change_term')],
                                                        order='id desc', limit=1)

                    vals = {
                        'rfq_id': result.id,
                        'create_by': self._uid,
                        'create_timestamp': datetime.datetime.now(),
                        'action_type': 'MM submit terms change'
                    }
                    self.env['iac.rfq.quote.history'].create(vals)
                    self.env.cr.commit()

        if error_str <> '':
            raise UserError(error_str)
        else:
            raise UserError('上传成功')

    @api.multi
    def action_download_file(self):
        file_dir = self.env["muk_dms.directory"].search([('name', '=', 'file_template')], limit=1, order='id desc')
        if not file_dir.exists():
            raise UserError('File dir file_template does not exists!')
        file_template = self.env["muk_dms.file"].search([('filename', '=', 'rfq_change_term.xls')], limit=1,
                                                        order='id desc')
        if not file_template.exists():
            raise UserError('File Template with name ( %s ) does not exists!' % ("rfq_change_term.xls",))
        action = {
            'type': 'ir.actions.act_url',
            'url': '/dms/file/download/%s' % (file_template.id,),
            'target': 'new',
        }
        return action
