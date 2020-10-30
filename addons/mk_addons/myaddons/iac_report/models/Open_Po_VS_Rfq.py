# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, exceptions, _
from odoo.tools.translate import _
from odoo.http import request
import datetime
from odoo.exceptions import UserError, ValidationError

class PoPriceVSRfqReport(models.Model):
    """    報表 檔
        """
    _name = 'v.report.open.po.vs.rfq'
    _description = "po price vs rfq report"
    # _auto = False  #必須注釋掉，需要模型先建立起來
    #     #    _order = 'id'

    ##***注意***：模型字段定義必須用簡單類型，不可以link到其他模型，以免刪除資料時，產生級聯刪除

    plant_code = fields.Char(string='plant', readonly=True)
    buyer_code = fields.Char(string='buyer code', readonly=True)
    buyer_name = fields.Char(string='buyer name',readonly=True)
    vendor_code = fields.Char(string='vendor_code', readonly=True)
    name1_cn = fields.Char(string='name1_cn',readonly=True)
    part_no = fields.Char(string='part', readonly=True)
    part_description = fields.Char(string='part description',readonly=True)
    currency = fields.Char()
    item_cost = fields.Float(digits=(18,6))
    info_currency = fields.Char()
    inforecord = fields.Float(digits=(18,6))
    difference = fields.Float(digits=(18,6))
    document_no = fields.Char()
    document_line_no = fields.Char()
    total_qty = fields.Float()
    open_qty = fields.Float(string='open_qty', readonly=True)
    price_control = fields.Char(string='Price Control', readonly=True)
    po_create_date = fields.Date()
    po_line_delivery_date = fields.Date()
    division = fields.Char()
    info_create = fields.Date()
    info_begin = fields.Date()
    info_end = fields.Date()



class OpenPoVSRfqReportWizard(models.TransientModel):
    _name = 'v.open.po.vs.rfq.report.wizard'

    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True,domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    buyer_id = fields.Many2one('buyer.code',string='Buyer',domain=lambda self: [('id', 'in', self.env.user.buyer_id_list
)],index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)
    part_id = fields.Many2one('material.master', string="Part No", index=True)
    po_no = fields.Many2one('iac.purchase.order',string="PO",index=True)

    @api.multi
    def search_po_price_vs_rfq_report(self):
        self.ensure_one()  # 检验某数据集是否只包含单条数据，如果不是则报错
        lc_plant_id = 0
        lc_vendor_id = 0
        lc_buyer_id = 0
        lc_part_id = 0
        lc_po_no = 0
        super_flag = False
        domain = []

        for wizard in self:

            if not wizard.plant_id:
                lc_plant_id = 0
            else:
                lc_plant_id = wizard.plant_id.id

            if not wizard.buyer_id:
                for item in self.env.user.groups_id:
                    if item.name == 'Super Buyer':
                        super_flag = True
                        break
                if not super_flag == True:
                    for item in self.env.user.groups_id:
                        if item.name == 'Buyer':
                            raise exceptions.ValidationError('请选择Buyer')
                lc_buyer_id = 0
            else:
                lc_buyer_id = wizard.buyer_id.id

            if not wizard.vendor_id:
                lc_vendor_id = 0
            else:
                lc_vendor_id = wizard.vendor_id.id

            if not wizard.part_id:
                lc_part_id = 0
            else:
                lc_part_id = wizard.part_id.id

            if not wizard.po_no:
                lc_po_no = 0
            else:
                lc_po_no = wizard.po_no.id

                # 呼叫sp proc_report_vendor_terms_change_history，傳入參數，取得id
        self.env.cr.execute('select v_id from public.proc_report_open_po_vs_rfq'
                            ' (%s,%s,%s,%s,%s) as (v_id int8)',
                            (lc_plant_id, lc_part_id,lc_vendor_id,
                             lc_po_no, lc_buyer_id))

        result_po_price_vs_rfq = self.env.cr.fetchall()
        result_ids = []
        for result_po_price_vs_rfq_wa in result_po_price_vs_rfq:
            result_ids.append(result_po_price_vs_rfq_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('po price vs rfq report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.report.open.po.vs.rfq'
        }
        return action

