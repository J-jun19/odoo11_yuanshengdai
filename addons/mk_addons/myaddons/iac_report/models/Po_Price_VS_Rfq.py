# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request
import datetime
# 報表名稱：PO Price 不同於 Info Record Price 報表 (改變寫法: call SP,將資料寫到 table裡 )
#  Category :  Report: PO
#  數據源   select * from "public"."v_po_price_vs_rfq"
# author : IAC.Laura  20180523
#這種報表的寫法為建立模型，包含報表的所有字段，呼叫事先寫好的SP，取得SP返回的ID，此處ID對應
#SP中根據邏輯算出來的報表要顯示的值，注意並不是直接把全部欄位取回來，而是只要ID,再利用domain的
#寫法，從模型中把真正需要的各個欄位取回來顯示在屏幕上
#這些值是SP insert進去的，相當於臨時表
class PoPriceVSRfqReport(models.Model):

    """    報表 檔
        """
    _name = 'v.po.price.vs.rfq.report'
    _description = "po price vs rfq report"
    #_auto = False  #必須注釋掉，需要模型先建立起來
    #     #    _order = 'id'

	##***注意***：模型字段定義必須用簡單類型，不可以link到其他模型，以免刪除資料時，產生級聯刪除

    plant = fields.Char(string='plant',readonly=True)
    vendor_code = fields.Char(string='vendor_code',readonly=True)
    vendor_name = fields.Char(string='vendor_name',readonly=True)
    part = fields.Char(string='part',readonly=True)
    po_no = fields.Char(string='po_no',readonly=True)
    po_line = fields.Float(string='po_line',readonly=True)
    po_qty = fields.Float(string='po_qty',readonly=True)
    open_qty = fields.Float(string='open_qty',readonly=True)
    rfq_price = fields.Float(string='rfq_price',readonly=True)
    po_price = fields.Float(string='po_price',readonly=True)
    buyer_code = fields.Char(string='buyer code',readonly=True)
    price_control = fields.Char(string='Price Control',readonly=True)
  
class PoPriceVSRfqReportWizard(models.TransientModel):
    _name = 'v.po.price.vs.rfq.report.wizard'

    # search 模型  model
    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True,domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)
    part_id = fields.Many2one('material.master', string="Part No", index=True)
    po_no = fields.Char(string="PO")

    @api.multi
    def search_po_price_vs_rfq_report(self):
        self.ensure_one()  #检验某数据集是否只包含单条数据，如果不是则报错
        lc_plant_id = ""
        lc_vendor_id = ""
        lc_part_id = ""
        lc_po_no = ""
        domain = []


        for wizard in self:

            if not wizard.plant_id:
                lc_plant_id = ""
            else:
                lc_plant_id = wizard.plant_id.plant_code

            if not wizard.vendor_id:
                lc_vendor_id = ""
            else:
                lc_vendor_id = wizard.vendor_id.vendor_code

            if not wizard.part_id:
                lc_part_id = ""
            else:
                lc_part_id = wizard.part_id.part_no

            if not wizard.po_no:
                lc_po_no = ""
            else:
                lc_po_no = wizard.po_no

         #呼叫sp proc_report_vendor_terms_change_history，傳入參數，取得id
        self.env.cr.execute('select v_id from public.proc_report_po_price_vs_rfq'
                            ' (%s,%s,%s,%s) as (v_id int8)',
                            (lc_plant_id,lc_vendor_id,
                             lc_part_id,lc_po_no))

        result_po_price_vs_rfq = self.env.cr.fetchall()
        result_ids = []
        for result_po_price_vs_rfq_wa in result_po_price_vs_rfq:
            result_ids.append(result_po_price_vs_rfq_wa)

        action = {
            'domain': [('id', 'in', result_ids)],
            'name': _('po price vs rfq report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.po.price.vs.rfq.report'
        }
        return action
		
  