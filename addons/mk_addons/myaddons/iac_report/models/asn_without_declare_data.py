# -*- coding: utf-8 -*-

from odoo import models,fields
from odoo.exceptions import UserError
from datetime import datetime,timedelta


class AsnWithoutDeclareWizard(models.TransientModel):

    _name = 'asn.without.declare.data.wizard'

    vendor_code = fields.Many2one('iac.vendor', string='Vendor Code *') # domain=lambda self: [('id', 'in', self.env.user.)]
    manu_no = fields.Char(string='廠商編碼(海关系统)')
    transit_time = fields.Date(string='入區日期')
    last_entry_time = fields.Date(string='最後報關日期')
    only_days = fields.Boolean(string='只查詢15天內未報關資料')

    def asn_without_declare_data(self):

        # result = []
        for wizard in self:
            domain = []
            if wizard.vendor_code:
                domain += [
                    '&',
                    ('vendor_code', '=', wizard.vendor_code.vendor_code),
                    ('entry_apply_no', '=', False)]

            if wizard.manu_no:
                domain += [('manu_no', '=', wizard.manu_no)]

            if wizard.transit_time:
                domain += [('transit_time', '=', wizard.transit_time)]

            if wizard.last_entry_time:
                domain += [('last_entry_time', '=', wizard.last_entry_time)]

            if wizard.transit_time and wizard.last_entry_time:
                if wizard.transit_time >= wizard.last_entry_time:
                    raise UserError(u'入區日期和最後報關日期不符合条件！')

            if wizard.only_days:
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                now_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                last_time = now_date + timedelta(days=15)
                print last_time
                domain += [('last_entry_time', '<=', str(last_time))]

            """
            如果查询条件vendor_code是必填，根据vendor_code查询时，不管是vendor还是buyer只能查询
            到vendor_code维护正常的资料，也就是说sap的vendor_code维护正常的资料才能被查询到，如果是
            sap vandor_code维护不正常，海关编号维护正常的资料就查询不了
            如果vendor_code不是必选，可以
            """

            result = self.env['iac.custom.data.unfinished.pub'].search(domain)
            result_list = list(result)
            result_list_re = result_list[:]
            # print result_list[0]

            # 对查询出来的结果进行筛选
            for result in result_list_re:
                print result
                if not result.manu_no:
                    result_list.remove(result)
                    print result_list

            if not result_list:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result_list])],
            'name': 'ASN Without declare data',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.custom.data.unfinished.pub'

        }
        return action





