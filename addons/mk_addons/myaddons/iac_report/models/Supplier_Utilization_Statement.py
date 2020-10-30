# -*- coding: utf-8 -*-

from odoo import models,fields,api,tools

class IacSupplierKeyActionLog(models.Model):
    _name = 'iac.supplier.key.action.log'

    menu_id = fields.Many2one('ir.ui.menu')
    action_type = fields.Char(index=1)
    vendor_id = fields.Many2one('iac.vendor',index=1)

class IacSupplierUtilizationStatement(models.Model):
    _name = 'iac.supplier.utilization.statement'
    _order = 'has_action desc'
    _auto = False

    vendor_account = fields.Char(string='Vendor Account')
    vendor_code = fields.Char(string='Vendor Code')
    vendor_name = fields.Char(string='Vendor Name')
    plant_code = fields.Char(string='Plant Code')
    last_ff_date = fields.Char(string='最近一次 fill form 下載時間')
    last_vu_date = fields.Char(string='最近一次 Delivery 上傳時間')
    last_reply_date = fields.Char(string='最近一次單筆 Delivery 填寫時間')
    last_ca_date = fields.Char(string='最近一次開立 ASN 時間')
    last_cala_date = fields.Char(string='最近一次 Cancel ASN 時間')
    last_confirm_date = fields.Char(string='最近一次 Confirm/Exception PO 時間')
    buyer_email = fields.Char(string='Buyer Email')
    has_action = fields.Char(string='是否有操作记录')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'iac_supplier_utilization_statement')
        self._cr.execute("""
        CREATE OR REPLACE VIEW "public"."iac_supplier_utilization_statement" AS 
 SELECT view_data.id,
    view_data.vendor_account,
    view_data.vendor_code,
    view_data.vendor_name,
    view_data.plant_code,
    view_data.last_ff_date,
    view_data.last_vu_date,
    view_data.last_reply_date,
    view_data.last_ca_date,
    view_data.last_cala_date,
    view_data.last_confirm_date,
    view_data.buyer_email,
        CASE
            WHEN ((((((view_data.last_ff_date IS NULL) AND (view_data.last_vu_date IS NULL)) AND (view_data.last_reply_date IS NULL)) AND (view_data.last_ca_date IS NULL)) AND (view_data.last_cala_date IS NULL)) AND (view_data.last_confirm_date IS NULL)) THEN 'N'::text
            ELSE 'Y'::text
        END AS has_action
   FROM ( SELECT iv.id,
            ru.login AS vendor_account,
            iv.vendor_code,
            iv.name AS vendor_name,
            pod.plant_code,
            t1.last_ff_date,
            t2.last_vu_date,
            t3.last_reply_date,
            t4.last_ca_date,
            t5.last_cala_date,
            t6.last_confirm_date,
            iv.buyer_email
           FROM (((((((((( SELECT DISTINCT td.vendor_id
                   FROM iac_traw_data td
                  WHERE (((((td.vendor_ori)::text !~~ '00006%'::text) AND ((td.fpversion)::text = ( SELECT max((iac_tcolumn_title.fpversion)::text) AS max
                           FROM iac_tcolumn_title))) AND (td.vendor_id IS NOT NULL)) AND ((td.open_po > (0)::double precision) OR ((((((((((((((((((((((td.qty_m1 + td.qty_m2) + td.qty_m3) + td.qty_m4) + td.qty_m5) + td.qty_m6) + td.qty_m7) + td.qty_m8) + td.qty_m9) + td.qty_w1) + td.qty_w2) + td.qty_w3) + td.qty_w4) + td.qty_w5) + td.qty_w6) + td.qty_w7) + td.qty_w8) + td.qty_w9) + td.qty_w10) + td.qty_w11) + td.qty_w12) + td.qty_w13) > (0)::double precision)))) traw
             LEFT JOIN iac_vendor iv ON ((traw.vendor_id = iv.id)))
             JOIN res_users ru ON ((iv.user_id = ru.id)))
             JOIN pur_org_data pod ON ((iv.plant = pod.id)))
             LEFT JOIN ( SELECT iskal.vendor_id,
                    max(iskal.create_date) AS last_ff_date
                   FROM iac_supplier_key_action_log iskal
                  WHERE ((iskal.action_type)::text = 'Vendor Fill Form'::text)
                  GROUP BY iskal.vendor_id) t1 ON ((t1.vendor_id = iv.id)))
             LEFT JOIN ( SELECT iskal2.vendor_id,
                    max(iskal2.create_date) AS last_vu_date
                   FROM iac_supplier_key_action_log iskal2
                  WHERE ((iskal2.action_type)::text = 'Vendor Upload'::text)
                  GROUP BY iskal2.vendor_id) t2 ON ((t2.vendor_id = iv.id)))
             LEFT JOIN ( SELECT iskal3.vendor_id,
                    max(iskal3.create_date) AS last_reply_date
                   FROM iac_supplier_key_action_log iskal3
                  WHERE ((iskal3.action_type)::text = 'Reply'::text)
                  GROUP BY iskal3.vendor_id) t3 ON ((t3.vendor_id = iv.id)))
             LEFT JOIN ( SELECT iskal4.vendor_id,
                    max(iskal4.create_date) AS last_ca_date
                   FROM iac_supplier_key_action_log iskal4
                  WHERE ((iskal4.action_type)::text = 'Vendor Create ASN'::text)
                  GROUP BY iskal4.vendor_id) t4 ON ((t4.vendor_id = iv.id)))
             LEFT JOIN ( SELECT iskal5.vendor_id,
                    max(iskal5.create_date) AS last_cala_date
                   FROM iac_supplier_key_action_log iskal5
                  WHERE ((iskal5.action_type)::text = 'Vendor Cancel ASN'::text)
                  GROUP BY iskal5.vendor_id) t5 ON ((t5.vendor_id = iv.id)))
             LEFT JOIN ( SELECT iskal6.vendor_id,
                    max(iskal6.create_date) AS last_confirm_date
                   FROM iac_supplier_key_action_log iskal6
                  WHERE ((iskal6.action_type)::text = 'Vendor Confirm PO'::text)
                  GROUP BY iskal6.vendor_id) t6 ON ((t6.vendor_id = iv.id)))
          WHERE (1 = 1)) view_data
  ORDER BY
        CASE
            WHEN ((((((view_data.last_ff_date IS NULL) AND (view_data.last_vu_date IS NULL)) AND (view_data.last_reply_date IS NULL)) AND (view_data.last_ca_date IS NULL)) AND (view_data.last_cala_date IS NULL)) AND (view_data.last_confirm_date IS NULL)) THEN 'N'::text
            ELSE 'Y'::text
        END DESC, view_data.plant_code, view_data.vendor_code;
                                    """)

class IacSupplierUtilizationStatementWizard(models.TransientModel):
    _name = 'iac.supplier.utilization.statement.wizard'

    plant_id = fields.Many2one('pur.org.data',string='Plant *')
    vendor_id = fields.Many2one('iac.vendor',string='Vendor')
    # flag = fields.Boolean(string='只显示有操作记录的vendor',default=True)

    @api.multi
    def search_supplier_utilization(self):
        for wizard in self:
            domain = []
            if wizard.plant_id:
                domain+=[('plant_code','=',wizard.plant_id.plant_code)]
            if wizard.vendor_id:
                domain+=[('vendor_code','=',wizard.vendor_id.vendor_code)]
            # if wizard.plant_id and wizard.vendor_id:
            #     result = self.env['iac.supplier.utilization.statement'].search([('plant_code','=',wizard.plant_id.plant_code),('vendor_code','=',wizard.vendor_id.vendor_code)],order='has_action desc')
            # if wizard.plant_id and not wizard.vendor_id:
            #     result = self.env['iac.supplier.utilization.statement'].search(
            #         [('plant_code', '=', wizard.plant_id.plant_code)], order='has_action desc')
            # if wizard.flag:
            #     domain+=['|','|','|','|','|',('last_ff_date','!=',None),('last_vu_date','!=',None),('last_reply_date','!=',None),('last_ca_date','!=',None),('last_cala_date','!=',None),('last_confirm_date','!=',None)]
            result = self.env['iac.supplier.utilization.statement'].search(domain)
        action = {
            'domain':[('id','in',[x.id for x in result])],
            'name':'Supplier Utilization Statement Report',
            'type':'ir.actions.act_window',
            'view_mode':'tree',
            'res_model':'iac.supplier.utilization.statement'
        }
        return action