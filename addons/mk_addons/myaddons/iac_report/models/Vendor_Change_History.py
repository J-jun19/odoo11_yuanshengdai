# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class VendorChangeHistoryReport(models.Model):
    """    報表 檔
        """
    _name = 'v.vendor.change.history'
    _description = "VendorChangeHistory Report"
    _auto = False
    _order = 'plant_code desc,sc_code'

    plant_code = fields.Char(string="plant")
    sc_code = fields.Char(string="sc_code")
    sc_name = fields.Char(string="sc_name")
    vendor_code = fields.Char(string="vendor_code")
    vendor_name = fields.Char(string="vendor_name")
    current_class = fields.Char(string="current_class")
    vendor_sap_status = fields.Char(string="vendor_sap_status")
    create_date = fields.Char(string="create_date")
    action = fields.Char(string="action")
    state = fields.Char(string="state")
    login = fields.Char(string="login")
    display_name = fields.Char(string="display_name")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_change_history')
        self._cr.execute("""
                        CREATE OR REPLACE VIEW v_vendor_change_history AS
                            SELECT row_number() OVER () AS id,
                                        porg.plant_code AS plant_code,
                                        sc.company_no AS sc_code,
                                        sc.name AS sc_name,
                                        v.vendor_code,
                                        v.name AS vendor_name,
                                        sc.current_class,
                                        v.vendor_sap_status,
                                        t1.create_date,
                                        t1.action,
                                        t1.state,
                                        ru.login,
                                        rp.display_name
                           FROM ( SELECT iac_vendor_block.vendor_id,
                                    iac_vendor_block.create_date,
                                    iac_vendor_block.create_uid,
                                    iac_vendor_block.is_block AS action,
                                    iac_vendor_block.state
                                   FROM iac_vendor_block
                                UNION
                                 SELECT v_1.id AS vendor_id,
                                    ivcb.create_date,
                                    ivcb.create_uid,
                                    'change basic data'::character varying AS action,
                                    ivcb.state
                                   FROM iac_vendor_change_basic ivcb
                                     JOIN iac_vendor_register reg ON reg.id = ivcb.vendor_reg_id
                                     JOIN iac_vendor v_1 ON reg.id = v_1.vendor_reg_id
                                UNION
                                 SELECT iac_vendor_copy.ori_vendor_id AS vendor_id,
                                    iac_vendor_copy.create_date,
                                    iac_vendor_copy.create_uid,
                                    'vendor copy'::character varying AS action,
                                    iac_vendor_copy.state
                                   FROM iac_vendor_copy
                                UNION
                                 SELECT iac_vendor_change_terms.vendor_id,
                                    iac_vendor_change_terms.create_date,
                                    iac_vendor_change_terms.create_uid,
                                    'change terms code'::character varying AS action,
                                    iac_vendor_change_terms.state
                                   FROM iac_vendor_change_terms
                                UNION
                                 SELECT iac_vendor_change_master.vendor_id,
                                    iac_vendor_change_master.create_date,
                                    iac_vendor_change_master.create_uid,
                                    'change master data'::character varying AS action,
                                    iac_vendor_change_master.state
                                   FROM iac_vendor_change_master) t1
                             JOIN iac_vendor v ON v.id = t1.vendor_id
                             JOIN iac_supplier_company sc ON v.supplier_company_id = sc.id
                             JOIN res_users ru ON ru.id = t1.create_uid
                             JOIN res_partner rp ON rp.id = ru.partner_id
                             JOIN pur_org_data porg ON porg.id = v.plant
                          ORDER BY porg.plant_code, sc.company_no, v.vendor_code, t1.create_date """)


class VendorChangeHistoryWizard(models.TransientModel):
    _name = 'iac.vendor.change.history.wizard'
    # search 模型  model

    # plant_id = fields.Many2one('pur.org.data',string="Plant **",index=True)  # 用戶登入后選擇的plant
    plant_id = fields.Many2one('pur.org.data', u'Plant *', domain=lambda self: [
        ('id', 'in', self.env.user.plant_id_list
         )])
    sc_code = fields.Char(string="Supplier Company No")
    vendor_code = fields.Char(string="Vendor Code")

    @api.multi
    def search_vendor_change_history_report(self):
        print ' *62: ', self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        for wizard in self:
            domain = []

            if wizard.vendor_code:
                domain += [('vendor_code', '=', wizard.vendor_code.zfill(10).strip())]
            # if wizard.plant_id:
            # domain += [('plant_code', '=', wizard.plant_id.plant_code)]
            if wizard.plant_id:
                domain += [('plant_code', '=', wizard.plant_id.plant_code)]
            if wizard.sc_code:
                domain += [('sc_code', '=', wizard.sc_code)]
            print '*76:', domain

            result = self.env['v.vendor.change.history'].search(domain)
            print '*78:', result

        act = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor Change HistoryReport'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.vendor.change.history'
        }
        return act
