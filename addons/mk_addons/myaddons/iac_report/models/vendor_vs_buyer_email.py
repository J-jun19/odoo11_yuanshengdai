# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class VendorVsBuyerEmail(models.Model):
    """    報表 檔
        """
    _name = 'v.vendor.vs.buyer.email'
    _description = "VendorVsBuyerEmail"
    _auto = False
    _order = 'vendor_code'

    plant = fields.Char(string="plant")
    vendor_code = fields.Char(string="vendor_code")
    vendor_name = fields.Char(string="vendor_name")
    buyer_email = fields.Char(string="buyer_email")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_vs_buyer_email')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW v_vendor_vs_buyer_email AS
                    SELECT v.id  
                                    ,v.plant                                
                                    ,lpad(v.vendor_code::text, 10, '0'::text) AS vendor_code
                                    ,sr.name1_cn AS vendor_name
                                    ,sr.buyer_email
                     FROM iac_vendor v
                     JOIN iac_vendor_register sr ON v.id = sr.vendor_id                              
                     ORDER BY (lpad(v.vendor_code::text, 10, '0'::text)) 
                      """)


class VendorVsBuyerEmailWizard(models.TransientModel):
    _name = 'vendor.vs.buyer.email.wizard'
    # search 模型  model

    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)],
                               index=True)
    # plant_id = fields.Many2one('pur.org.data',string="Plant",index=True)  # 用戶登入后選擇的plant
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info", index=True)
    buyer_email = fields.Char(string="Buyer Email")

    @api.multi
    def search_vendor_vs_buyer_email(self):
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []


            if wizard.plant_id:
               domain += [('plant', '=', wizard.plant_id.id)]

            if wizard.vendor_id:
                domain += [('vendor_code', '=', wizard.vendor_id.vendor_code)]

            if wizard.buyer_email:
                domain += [('buyer_email', '=', wizard.buyer_email)]

            result = self.env['v.vendor.vs.buyer.email'].search(domain)


        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('VendorVsBuyerEmail'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.vendor.vs.buyer.email'
        }
        return action