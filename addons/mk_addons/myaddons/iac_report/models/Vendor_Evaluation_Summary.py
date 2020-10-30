# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class VendorEvaluationSummaryReport(models.Model):
    _name = "v.vendor.evaluation.summary"
    # _description = "Global Vendor"
    _auto = False
    #    _order = 'gv_code'

    create_date = fields.Datetime('Creation Date')
    plant = fields.Char('Plant')
    plant_id = fields.Integer()
    supplier_company_id = fields.Integer()
    sc_code = fields.Char('Supplier Company No')
    sc_name = fields.Char('Company Name')
    state = fields.Char('State')
    part_category = fields.Char('Part Category')
    qm_controller = fields.Char('QM Controller')
    qm_user = fields.Char('QM User')
    scm_controller = fields.Char('SCM Controller')
    scm_user = fields.Char('SCM User')
    qm_score = fields.Char('QM Score')
    scm_score = fields.Char('SCM Score')
    supplier_final_score = fields.Float('SC Score')
    supplier_final_class = fields.Char('Final SC Class')
    part_class_final_score = fields.Float('Part Category Score')
    part_category_final_class = fields.Char('Final Part Class')
    qm_leader = fields.Char('QM Leader')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_evaluation_summary')
        self._cr.execute("""
CREATE OR REPLACE VIEW public.v_vendor_evaluation_summary
AS SELECT row_number() OVER () AS id,
    t.supplier_company_id,
    t.sc_code,
    t.sc_name,
    t.state,
    t.supplier_final_score,
    t.supplier_final_class,
    t.part_category,
    t.part_class_final_score,
    t.part_category_final_class,
    t.create_date,
    t.plant_id,
    t.plant,
    t.scm_user,
    t.scm_score,
    t.qm_user,
    t.qm_score,
    t.scm_controller,
    t.qm_controller,
    t.qm_leader
   FROM ( SELECT DISTINCT sl.id,
            sl.supplier_company_id,
            sc.company_no AS sc_code,
            sc.name AS sc_name,
            sl.state,
            icsc.user_class AS supplier_final_class,
            ipc.name AS part_category,
            icpc.user_part_class AS part_category_final_class,
            ispc.create_date,
            sl.plant_id,
            pod.plant_code AS plant,
            rp_scm.name AS scm_user,
            ispc.scm_user_score AS scm_score,
            rp_qm.name AS qm_user,
            ispc.qm_user_score AS qm_score,
            rp_scm_ctl.name AS scm_controller,
            rp_qm_ctl.name AS qm_controller,
            icpc.user_score AS part_class_final_score,
            icsc.user_score AS supplier_final_score,
            rp_qm_leader.name AS qm_leader
           FROM iac_score_list sl
             JOIN iac_score_part_category ispc ON ispc.score_list_id = sl.id
             JOIN iac_score_part_category_line ispcl ON ispcl.score_part_category_id = ispc.id
             JOIN iac_part_category ipc ON ipc.id = ispc.part_category_id
             JOIN iac_score_definition isd ON isd.id = ispcl.vs_def_id
             JOIN iac_supplier_company sc ON sc.id = sl.supplier_company_id
             LEFT JOIN res_partner rp_scm ON rp_scm.id = ispc.scm_partner_id
             LEFT JOIN res_partner rp_qm ON rp_qm.id = ispc.qm_partner_id
             LEFT JOIN res_partner rp_scm_ctl ON rp_scm_ctl.id = ispc.scm_controller_id
             LEFT JOIN res_partner rp_qm_ctl ON rp_qm_ctl.id = ispc.qm_controller_id
             LEFT JOIN res_partner rp_qm_leader ON rp_qm_leader.id = ispc.qm_leader_id
             JOIN pur_org_data pod ON pod.id = sl.plant_id
             LEFT JOIN res_users ru_scm ON rp_scm.id = ru_scm.partner_id
             LEFT JOIN res_users ru_qm ON rp_qm.id = ru_qm.partner_id
             LEFT JOIN res_users ru_scm_ctl ON rp_scm_ctl.id = ru_scm_ctl.partner_id
             LEFT JOIN res_users ru_qm_ctl ON rp_qm_ctl.id = ru_qm_ctl.partner_id
             LEFT JOIN res_users ru_qm_leader ON rp_qm_leader.id = ru_qm_leader.partner_id
             LEFT JOIN iac_class_part_category icpc ON icpc.id = ispc.class_part_category_id AND ispc.part_category_id = icpc.part_category_id AND icpc.score_snapshot::text = sl.score_snapshot::text AND icpc.supplier_company_id = sl.supplier_company_id
             LEFT JOIN iac_class_supplier_company icsc ON icsc.supplier_company_id = sl.supplier_company_id AND icsc.score_snapshot::text = sl.score_snapshot::text
          ORDER BY pod.plant_code, sc.company_no) t;
                                    """)


class VendorEvaluationSummaryWizard(models.TransientModel):
    _name = 'vendor.evaluation.summary.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)])
    # plant_id = fields.Many2one('pur.org.data',string='Plant')
    supplier_company = fields.Many2one('iac.supplier.company', string="Supplier Company")
    part_category_id = fields.Many2one('iac.part.category', string="Part Category")
    starttime = fields.Date(string="Create Date From")
    endtime = fields.Date(string="Create Date To")

    @api.multi
    def search_vendor_evaluation_summary_report(self):
        # self.env.user.id, ',', self.env.user.name, ',', request.session.get('session_plant_id', False)
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.supplier_company:
                domain += [('supplier_company_id', '=', wizard.supplier_company.id)]
            if wizard.part_category_id:
                domain += [('part_category', '=', wizard.part_category_id.name)]
            if wizard.starttime:
                domain += [('create_date', '>=', wizard.starttime)]
            if wizard.endtime:
                domain += [('create_date', '<=', wizard.endtime)]

            result = self.env['v.vendor.evaluation.summary'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            # 'domain': domain,
            'name': _('Vendor Evaluation Summary Report'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.vendor.evaluation.summary'
        }
        return action
