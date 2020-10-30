from odoo import api, fields, models, tools
from odoo.tools.translate import _

class PurchaseGroupList(models.Model):
    _name = "v.buyer.code"
    _description = "Purchase Group List Report"
    _auto = False
    _order = 'ep_buyer_code'

    plant = fields.Char(string="Plant", readonly=True)
    ep_buyer_code = fields.Char(string="EP Buyer Code", readonly=True)
    ep_buyer_id = fields.Char(string="EP Buyer ID", readonly=True)
    ep_buyer_name = fields.Char(string="EP Buyer Name", readonly=True)
    sap_purchase_id = fields.Char(string = "SAP Purchase ID", readonly=True)
    sap_purchase_group_name = fields.Char(string = "SAP Purchase Group Name", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_buyer_code')
        self._cr.execute("""
            CREATE OR REPLACE VIEW v_buyer_code AS (
                 SELECT bc.id,
                    bcp."PLANT_ID" AS plant,
                    bc.buyer_erp_id AS ep_buyer_code,
                    ru.login AS ep_buyer_id,
                    rp.display_name AS ep_buyer_name,
                    bc.buyer_ad_account AS sap_purchase_id,
                    bc.buyer_name AS sap_purchase_group_name
                   FROM buyer_code bc
                     JOIN buyer_code_plant bcp ON bcp."BDC_VALUE"::text = bc.buyer_erp_id::text
                     LEFT JOIN res_partner_buyer_code_line rpb ON rpb.buyer_code_id = bc.id
                     LEFT JOIN res_partner rp ON rp.id = rpb.partner_id
                     LEFT JOIN res_users ru ON rp.id = ru.partner_id
                  ORDER BY bcp."PLANT_ID", bc.buyer_erp_id
               )
                        """)

class PurchaseGroupListWizard(models.TransientModel):
    _name = 'v.buyer.code.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *", index=True,domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    ep_buyer_code = fields.Text (string="Buyer Code",  index=True)

    @api.multi
    def search_purchasegroup(self):
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []
            if wizard.plant_id:
                domain += [('plant', '=', wizard.plant_id.plant_code)]
            if wizard.ep_buyer_code:
                ep_buyer_code = wizard.ep_buyer_code.split('\n')
                domain += [('ep_buyer_code', 'in', ep_buyer_code)]

            result = self.env['v.buyer.code'].search(domain)
        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': ('Purchase Group List Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.buyer.code'
        }
        return action