# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.http import request


class VendorEvaluationDetailReport(models.Model):
    _name = "v.vendor.evaluation.detail"
    # _description = "Global Vendor"
    _auto = False
    #    _order = 'gv_code'

    create_date = fields.Datetime('Date')
    plant = fields.Char('Plant')
    plant_id = fields.Integer()
    supplier_company_id = fields.Integer()
    sc_code = fields.Char('SC Code')
    sc_name = fields.Char('SC Name')
    sc_status = fields.Char('SC Status')
    vendor_codes = fields.Char(string="Vendor Code",
                               compute='_taken_vendor_codes')  # SC 中参与评核的Vendor Code，多个Vendor Code用逗号隔开
    vendor_types = fields.Char(string='Vendor Type', compute='_taken_vendor_types')
    part_class = fields.Char('Part Class')
    part_category = fields.Char('Part Category')
    part_status = fields.Char('Part Status')
    qm_controller = fields.Char('QM Controller')
    qm_user = fields.Char('QM User')
    scm_controller = fields.Char('SCM Controller')
    scm_user = fields.Char('SCM User')
    qm_score = fields.Char('QM Score')
    scm_score = fields.Char('SCM Score')
    gr_qty = fields.Float('GR Qty')
    gr_amount = fields.Float('GR Amount')
    score_group = fields.Char('Score Group')
    score_item = fields.Char('Score Item')
    score_criteria = fields.Char('Score Criteria')
    item_status = fields.Char('Item Status')
    weight = fields.Char()
    user_score = fields.Char()
    supplier_final_score = fields.Float('SC Final Score')
    supplier_final_class = fields.Char('SC Final Class')
    part_class_final_score = fields.Float('Part Category Final Score')
    part_category_final_class = fields.Char('Part Category Final Class')

    @api.depends('supplier_company_id', 'plant_id')
    def _taken_vendor_codes(self):
        for v in self:
            domain = [('supplier_company_id', '=', v.supplier_company_id)]
            domain += [('plant', '=', v.plant_id)]
            vendor_list = self.env["iac.vendor"].search(domain)
            vendor_codes = []
            for vendor_rec in vendor_list:
                vendor_codes.append(vendor_rec.vendor_code)
            v.vendor_codes = ','.join(vendor_codes)

    @api.depends('supplier_company_id', 'plant_id')
    def _taken_vendor_types(self):
        for v in self:
            domain = [('supplier_company_id', '=', v.supplier_company_id)]
            domain += [('plant', '=', v.plant_id)]
            vendor_list = self.env["iac.vendor"].search(domain)
            vendor_types = []
            for vendor_rec in vendor_list:
                vendor_type = self.env['iac.vendor.register'].search(
                    [('state', '=', 'done'), ('vendor_id', '=', vendor_rec.id)]).supplier_type
                if vendor_type:
                    vendor_types.append(vendor_type)
                else:
                    vendor_types.append('N/A')
            v.vendor_types = ','.join(vendor_types)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_evaluation_detail')
        self._cr.execute("""
CREATE OR REPLACE VIEW public.v_vendor_evaluation_detail
AS SELECT row_number() OVER () AS id,
    sl.plant_id,
    pod.plant_code AS plant,
    sl.state AS sc_status,
    sl.supplier_company_id,
    sc.company_no AS sc_code,
    sc.name AS sc_name,
    sl.score_type,
    ispc.create_date,
    ru_qm_ctl.login AS qm_ctl_login,
    rp_qm_ctl.name AS qm_controller,
    ru_scm_ctl.login AS scm_ctl_login,
    rp_scm_ctl.name AS scm_controller,
    ru_scm.login AS scm_user_login,
    rp_scm.name AS scm_user,
    ru_qm.login AS scm_qm_login,
    rp_qm.name AS qm_user,
    ipc.name AS part_category,
    ipc.part_class,
    ispc.state AS part_status,
    ispc.scm_user_score AS scm_score,
    ispc.qm_user_score AS qm_score,
    isd.group_code AS score_group,
    isd.description AS score_item,
    isd.score_standard AS score_criteria,
    isd.ratio AS weight,
    ispcl.state AS item_status,
    ispcl.calculate_score,
    ispcl.user_score,
    ispc.gr_qty,
    ispc.gr_amount,
    icpc.user_score AS part_class_final_score,
    icpc.user_part_class AS part_category_final_class,
    icpc.state AS part_category_final_status,
    icsc.user_score AS supplier_final_score,
    icsc.user_class AS supplier_final_class,
    icsc.state AS supplier_company_final_status
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
     JOIN pur_org_data pod ON pod.id = sl.plant_id
     LEFT JOIN res_users ru_scm ON rp_scm.id = ru_scm.partner_id
     LEFT JOIN res_users ru_qm ON rp_qm.id = ru_qm.partner_id
     LEFT JOIN res_users ru_scm_ctl ON rp_scm_ctl.id = ru_scm_ctl.partner_id
     LEFT JOIN res_users ru_qm_ctl ON rp_qm_ctl.id = ru_qm_ctl.partner_id
     LEFT JOIN iac_class_part_category icpc ON icpc.id = ispc.class_part_category_id AND ispc.part_category_id = icpc.part_category_id AND icpc.score_snapshot::text = sl.score_snapshot::text AND icpc.supplier_company_id = sl.supplier_company_id
     LEFT JOIN iac_class_supplier_company icsc ON icsc.supplier_company_id = sl.supplier_company_id AND icsc.score_snapshot::text = sl.score_snapshot::text
  ORDER BY pod.plant_code, sc.company_no;


                                    """)


class VendorEvaluationDetailtWizard(models.TransientModel):
    _name = 'vendor.evaluation.detail.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)])
    # plant_id = fields.Many2one('pur.org.data',string='Plant')
    supplier_company = fields.Many2one('iac.supplier.company', string="Supplier Company")
    part_category_id = fields.Many2one('iac.part.category', string="Part Category")
    starttime = fields.Date(string="Create Date From")
    endtime = fields.Date(string="Create Date To")

    @api.multi
    def search_vendor_evaluation_detail_report(self):
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

            result = self.env['v.vendor.evaluation.detail'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            # 'domain': domain,
            'name': _('Vendor Evaluation Detail Report'),
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'v.vendor.evaluation.detail'
        }
        return action
