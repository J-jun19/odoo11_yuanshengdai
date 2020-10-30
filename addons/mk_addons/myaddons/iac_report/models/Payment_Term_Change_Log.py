# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request
import datetime

#這種報表的寫法為建立模型，包含報表的所有字段，呼叫事先寫好的SP，取得SP返回的ID，此處ID對應
#SP中根據邏輯算出來的報表要顯示的值，注意並不是直接把全部欄位取回來，而是只要ID,再利用domain的
#寫法，從模型中把真正需要的各個欄位取回來顯示在屏幕上
#這些值是SP insert進去的，相當於臨時表

class VendorTermsCodeChangeHistory(models.Model):
    _name = "v.terms.change_history"
    _description = "Vendor terms code change history"
    #_auto = False  #必須注釋掉，需要模型先建立起來
    #     #    _order = 'id'

##***注意***：模型字段定義必須用簡單類型，不可以link到其他模型，以免刪除資料時，產生級聯刪除

    v_plant_code = fields.Char(string="Plant", readonly=True)
    v_vendor_code = fields.Char(string="Vendor_code", readonly=True)
    v_vendor_name = fields.Char(string="Vendor_name", readonly=True)
    v_ori_payment_term = fields.Char(string="Old_payment", readonly=True)
    v_ori_payment_description = fields.Char(string="Old_payment_desc", readonly=True)
    v_ori_incoterm = fields.Char(string="Old_incoterm", readonly=True)
    v_ori_incoterm_description = fields.Char(string="Old_incoterm_description", readonly=True)
    v_ori_destination = fields.Char(string="Old_destination", readonly=True)
    v_new_payment = fields.Char(string="New_payment", readonly=True)
    v_new_description = fields.Char(string="New_payment_desc", readonly=True)
    v_new_incoterm = fields.Char(string="New_incoterm", readonly=True)
    v_new_incoterm_description = fields.Char(string="New_incoterm_desc", readonly=True)
    v_new_destination = fields.Char(string="New_destination", readonly=True)
    v_change_reason = fields.Char(string="Change_reason", readonly=True)
    v_effective_date = fields.Date(string="Effective_date", readonly=True)
    v_create_date = fields.Datetime(string="Create_date", readonly=True)
    v_state = fields.Char(string="Status", readonly=True)
    v_state_msg = fields.Char(string="Message", readonly=True)
    v_login = fields.Char(string="Creator_Login", readonly=True)
    v_user_name = fields.Char(string="Creator_name", readonly=True)
    v_webflow_number = fields.Char(string="Webflow_no", readonly=True)


class IacPaymentTermChangeLogReportWizard(models.TransientModel):
    _name = 'v.terms.change_history.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])

    # Odoo會把start_date自動變成字符類型取到程序中，呼叫SP時不需要再轉換字符類型
    start_date = fields.Date(string="Change from date")

    vendor_id = fields.Many2one('iac.vendor', string="Vendor Code")

    #Boolean對應屏幕上的checkbox，配合sp傳入值使用，本例子sp中選中= 'X'，否則等於空或者其他值
    not_closed = fields.Boolean(string="Process not closed")

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def search_terms_change_history(self):
        self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()  #检验某数据集是否只包含单条数据，如果不是则报错

        lc_not_closed = "X" #默認為not closed
        lc_start_date = '2000-01-01'
        lc_vendor_code = ""
        lc_plant_id = ''
        domain = []

        for wizard in self:

            if not wizard.plant_id:
                lc_plant_id = ""
            else:
                lc_plant_id = wizard.plant_id.plant_code

            if not wizard.start_date:
                lc_start_date = '2000-01-01'
            else:
#                lc_start_date = wizard.start_date.strftime('%Y-%m-%d')
                lc_start_date = wizard.start_date

            if wizard.not_closed:  #表示not_closed = True，意味著check box被選中
                lc_not_closed = "X"
            else:
                lc_not_closed = ""

            if not wizard.vendor_id:
                lc_vendor_code = ""
            else:
                lc_vendor_code = wizard.vendor_id.vendor_code
        # self.env.cr.execute("select * from public.proc_report_vendor_terms_change_history" \
        #                     "   (%s,%s,%s,%s) " \
        #                     "       as ( " \
        #                     "       v_id int4, " \
        #                     "       v_plant_code varchar, " \
        #                     "       v_vendor_code varchar, " \
        #                     "       v_vendor_name varchar, " \
        #                     "       v_ori_payment_term varchar, " \
        #                     "       v_ori_payment_description varchar, " \
        #                     "       v_ori_incoterm varchar,  " \
        #                     "       v_ori_incoterm_description varchar, " \
        #                     "       v_ori_destination varchar, " \
        #                     "       v_new_payment varchar, " \
        #                     "       v_new_description varchar, " \
        #                     "       v_new_incoterm varchar, " \
        #                     "       v_new_incoterm_description varchar, " \
        #                     "       v_new_destination varchar, " \
        #                     "       v_change_reason varchar, " \
        #                     "       v_effective_date date, " \
        #                     "       v_create_date timestamp, " \
        #                     "       v_state varchar, " \
        #                     "       v_state_msg varchar, " \
        #                     "       v_login varchar, " \
        #                     "       v_user_name varchar, " \
        #                     "       v_webflow_number varchar)",
        #                     (wizard.plant_id.plant_code, lc_start_date, lc_vendor_code, lc_not_closed))


#呼叫sp proc_report_vendor_terms_change_history，傳入參數，取得id
        self.env.cr.execute('select v_id from public.proc_report_vendor_terms_change_history (%s,%s,%s,%s) as (v_id int8)',
                            (lc_plant_id, lc_start_date, lc_vendor_code, lc_not_closed))

        result_terms_change_history = self.env.cr.fetchall()
        result_ids = []
        for result_terms_change_history_wa in result_terms_change_history:
            result_ids.append(result_terms_change_history_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('Vendor terms code change history'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.terms.change_history'
        }
        return action