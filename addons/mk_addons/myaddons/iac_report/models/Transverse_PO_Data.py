# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, exceptions
from odoo.tools.translate import _

class IacTransversePoData(models.Model):
    _name = "v.po.report.list"
    _description = "Vendor terms code change history"
    #_auto = False  #必須注釋掉，需要模型先建立起來

##***注意***：模型字段定義必須用簡單類型，不可以link到其他模型，以免刪除資料時，產生級聯刪除
    
    plant_code = fields.Char(string="Plant", readonly=True)
    division = fields.Char(string="Division", readonly=True)
    part_no = fields.Char(string='Part No',readonly=True)
    part_description = fields.Char(string='Part desc', readonly=True)
    po_date = fields.Date(string='PO date', readonly=True)
    po_quantity = fields.Float(string='PO qty', readonly=True)
    gr_quantity = fields.Float(string='GR qty', readonly=True)
    asn_quantity = fields.Float(string='In-trans ASN', readonly=True)
    open_quantity = fields.Float(string='Open PO qty', readonly=True)
    open_amount = fields.Float(string='Open PO amount', readonly=True)
    price = fields.Float(string='Price', readonly=True)
    price_unit = fields.Integer(string='Price unit', readonly=True)
    document_erp_id = fields.Char(string='PO number', readonly=True)
    document_line_erp_id = fields.Char(string='PO line no', readonly=True)
    delivery_date = fields.Date(string='Delivery date', readonly=True)
    vendor_code = fields.Char(string='Vendor code', readonly=True)
    buyer_erp_id = fields.Char(string='Buyer code', readonly=True)
    buyer_name = fields.Char(string='Buyer name', readonly=True)
    deletion_flag = fields.Char(string='Deletion flag', readonly=True)
    currency_id = fields.Char(string='Currency')

class IacTransversePODataWizard(models.TransientModel):
    _name = 'v.po.report.list.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *", required="1",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])

    po_number = fields.Char(string='PO number')
    part_no = fields.Char(string='Part no')
    buyer_code = fields.Char(string='Buyer code')
    division = fields.Char(string='Division')

    # Odoo會把start_date自動變成字符類型取到程序中，呼叫SP時不需要再轉換字符類型
    po_start_date = fields.Date(string="PO date from *", required='1')
    po_end_date = fields.Date(string="PO date to *", required='1')

    vendor_id = fields.Many2one('iac.vendor', string="Vendor Code")

    # Boolean對應屏幕上的checkbox，配合sp傳入值使用，本例子sp中選中= 'X'，否則等於空或者其他值
    only_open_po = fields.Boolean(string="Only open PO")

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def search_transverse_po_report(self):
        self.ensure_one()  #检验某数据集是否只包含单条数据，如果不是则报错

        lc_plant = ""
        lc_only_open = "" #默認為not closed
        lc_start_date = '2000-01-01'
        lc_end_date = '2000-01-01'
        lc_vendor_code = ""
        lc_po_number = ""
        lc_part_no = ""
        lc_division = ""
        lc_buyer_code = ""
        domain = []
        record_vendor = 0
        for item in self.env.user.groups_id:
            if item.name == 'External vendor':
                record_vendor = 1
        for wizard in self:

            # print self
            if not wizard.plant_id:
                lc_plant = ""
            else:
                lc_plant = wizard.plant_id.plant_code

            if not wizard.po_start_date:
                lc_start_date = '2000-01-01'
            else:
                lc_start_date = wizard.po_start_date

            if not wizard.po_end_date:
                lc_end_date = '2000-01-01'
            else:
                lc_end_date = wizard.po_end_date

            if wizard.only_open_po:  #表示only open = True，意味著check box被選中
                lc_only_open = "X"
            else:
                lc_only_open = ""

            if not wizard.vendor_id:
                if record_vendor == 0:
                    lc_vendor_code = ""
                else:
                    raise exceptions.ValidationError('请选择一个Vendor Code')
            else:
                lc_vendor_code = wizard.vendor_id.vendor_code

            if not wizard.po_number:
                lc_po_number = ""
            else:
                lc_po_number = wizard.po_number

            if not wizard.part_no:
                lc_part_no = ""
            else:
                lc_part_no = wizard.part_no

            if not wizard.division:
                lc_division = ""
            else:
                lc_division = wizard.division

            if not wizard.buyer_code:
                lc_buyer_code = ""
            else:
                lc_buyer_code = wizard.buyer_code

#呼叫sp proc_report_vendor_terms_change_history，傳入參數，取得id
        self.env.cr.execute('select v_id from public.proc_report_pol_info (%s,%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                            (lc_plant, lc_po_number, lc_part_no, lc_buyer_code, lc_start_date, lc_end_date, lc_division, lc_vendor_code, lc_only_open))

        result_po_line_report = self.env.cr.fetchall()
        result_ids = []
        for result_po_line_report_wa in result_po_line_report:
            result_ids.append(result_po_line_report_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('PO info'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.report.list'
        }
        return action