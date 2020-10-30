# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request
import datetime
from odoo.exceptions import UserError, ValidationError

class IacRFQPriceDifferenceReport(models.Model):
    """    報表 檔
        """
    _name = 'v.report.rfq.compare.with.other.vendor'
    _description = "rfq price difference report"
    # _auto = False  #必須注釋掉，需要模型先建立起來
    #     #    _order = 'id'

    part_id = fields.Char(string='part_id', readonly=True)
    part_no = fields.Char(string='part_no', readonly=True)
    vendor_id = fields.Integer(string='vendor_id', readonly=True)
    vendor_code = fields.Char(string='vendor_code', readonly=True)
    vendor_name = fields.Char(string='vendor_name', readonly=True)
    global_vendor_code = fields.Char(string='global_vendor_code', readonly=True)
    gv_name = fields.Char(string='gv_name', readonly=True)
    valid_from = fields.Date(string='valid_from', readonly=True)
    valid_to = fields.Date(string='valid_to', readonly=True)
    currency_id = fields.Char(string='currency_id', readonly=True)
    currency = fields.Char(string='currency', readonly=True)
    input_price = fields.Float(digits=(18, 6))
    rfq_price = fields.Float(digits=(18, 6))
    price_unit = fields.Integer(string='price_unit', readonly=True)
    rfq_no = fields.Char(string='rfq_no', readonly=True)
    creation_date = fields.Date(string='creation_date', readonly=True)
    buyer_code_id = fields.Integer(string='buyer_code_id', readonly=True)
    buyer_erp_id = fields.Char(string='buyer_erp_id', readonly=True)
    buyer_name = fields.Char(string='buyer_name', readonly=True)
    vendor_code_other = fields.Char(string='vendor_code_other', readonly=True)
    vendor_name_other = fields.Char(string='vendor_name_other', readonly=True)
    global_vendor_code_other = fields.Char(string='global_vendor_code_other', readonly=True)
    input_price_other = fields.Float(string='input_price_other', digits=(18, 6), readonly=True)
    currency_other = fields.Char(string='currency_other', readonly=True)
    price_other = fields.Float(digits=(18, 6))
    price_unit_other = fields.Integer(string='price_unit_other', readonly=True)
    create_date_other = fields.Date(string='create_date_other', readonly=True)
    valid_from_other = fields.Date(string='valid_from_other', readonly=True)
    valid_to_other = fields.Date(string='valid_to_other', readonly=True)
    create_date = fields.Date(string='create_date', readonly=True)


class IacRFQPriceDifferenceReportWizard(models.TransientModel):
    _name = 'v.report.rfq.compare.with.other.vendor.wizard'

    division_id = fields.Many2one('division.code', string='Division')
    material_group = fields.Many2one('material.group', string='Material Group', domain=[('material_group', '!=', ' ')])
    material_start = fields.Char('Material(Start with)')
    create_from = fields.Date('Create From')
    create_to = fields.Date('Create To')
    vendor_comparison = fields.Selection([
        ('SAME_GV', 'Same Global Vendor'),
        ('All', 'All Vendor')],
        string="Vendor Comparison *")
    rfq_comparison = fields.Selection([
        ('VALID', 'Exclude Expired RFQ'),
        ('All', 'All RFQ')],
        string="RFQ Comparison *")
    display_result = fields.Selection([
        ('ONLY_LOW', 'Only Display Lowest'),
        ('ALL', 'Display diff RFQ')],
        string="Display Result *")
    rfq_status = fields.Selection([
        ('CLOSED', 'Closed'),
        ('NOT_CLOSED', 'Not Closed')],
        string="RFQ Status *")

    @api.multi
    def search_rfq_price_difference_report(self):
        self.ensure_one()  # 检验某数据集是否只包含单条数据，如果不是则报错
        lc_division_id = ""
        lc_material_group = ""
        lc_material_start = ""
        lc_create_from = ""
        lc_create_to = ""
        lc_vendor_comparison = ""
        lc_rfq_comparison = ""
        lc_display_result = ""
        lc_rfq_status = ""

        domain = []

        for wizard in self:

            if not wizard.division_id:
                lc_division_id = ""
            else:
                lc_division_id = wizard.division_id.division

            if not wizard.material_group:
                lc_material_group = ""
            else:
                lc_material_group = wizard.material_group.material_group

            if not wizard.material_start:
                lc_material_start = ""
            else:
                lc_material_start = wizard.material_start

            if not wizard.create_from:
                lc_create_from = ""
            else:
                lc_create_from = wizard.create_from

            if not wizard.create_to:
                lc_create_to = ""
            else:
                lc_create_to = wizard.create_to

            if not wizard.vendor_comparison:
                lc_vendor_comparison = ""
            else:
                lc_vendor_comparison = wizard.vendor_comparison

            if not wizard.rfq_comparison:
                lc_rfq_comparison = ""
            else:
                lc_rfq_comparison = wizard.rfq_comparison

            if not wizard.display_result:
                lc_display_result = ""
            else:
                lc_display_result = wizard.display_result

            if not wizard.rfq_status:
                lc_rfq_status = ""
            else:
                lc_rfq_status = wizard.rfq_status



                # 呼叫sp proc_report_rfq_diff_from_other_vendor，傳入參數，取得id
        self.env.cr.execute('select v_id from public.proc_report_rfq_diff_from_other_vendor'
                            ' (%s,%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                            (lc_division_id, lc_material_group, lc_material_start, lc_create_from, lc_create_to,
                             lc_vendor_comparison, lc_rfq_comparison, lc_display_result, lc_rfq_status))

        result_rfq_price_difference = self.env.cr.fetchall()
        result_ids = []
        for result_rfq_price_difference_wa in result_rfq_price_difference:
            result_ids.append(result_rfq_price_difference_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('Info Record Price Difference Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.report.rfq.compare.with.other.vendor'
        }
        return action





