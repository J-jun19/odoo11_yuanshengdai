# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class VendorEvaluationApprovalLog(models.Model):
    _name = "v.vendor.evaluation.approval.log"
    _description = "Vendor Evaluation Approval Log"
    _auto = False

    company_no = fields.Char('Company No')
    plant_code = fields.Char('Plant')
    sc_name = fields.Char('Sc Name')
    part_category = fields.Char('Part Category')
    part_class = fields.Char('Part Class')
    score_snapshot = fields.Char('Score Snapshot')
    approve_role = fields.Text('Approval Role')
    approve_status = fields.Text('Approval Status')
    user_score = fields.Char('User Score')
    memo = fields.Text('Memo')
    create_date = fields.Datetime('Creation Date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_evaluation_approval_log')
        self._cr.execute("""
        CREATE OR REPLACE VIEW public.v_vendor_evaluation_approval_log AS
        select isal.id, 
               sc.company_no,
               pod.plant_code,
               sc."name" as sc_name,
               ipc."name" as part_category,
               pc."name" as part_class,
               isal.score_snapshot,
               isal.approve_role,
               isal.approve_status,
               isal.user_score,
               isal.memo,
               isal.create_date
           from iac_score_approve_log  isal
              inner join iac_score_part_category icpc  on icpc.id = isal.score_part_category_id
              inner join iac_part_category ipc on ipc.id = isal.part_category_id
              inner join res_users ru on ru.id = isal.user_id
              inner join pur_org_data pod on pod.id = icpc.plant_id
              inner join iac_supplier_company sc on sc.id = icpc.supplier_company_id
              inner join iac_part_class pc on pc.id = ipc.part_class
        order by pod.plant_code, sc.company_no, part_class, part_category, score_snapshot, create_date desc
                                         """)


class VendorEvaluationApprovalLogWizard(models.TransientModel):
    _name = 'vendor.evaluation.approval.log.wizard'

    plant_id = fields.Many2one('pur.org.data', string="Plant *",
                               domain=lambda self: [('id', 'in', self.env.user.plant_id_list)], index=True)
    supplier_company_id = fields.Many2one('iac.supplier.company', string="Supplier Company", index=True)
    part_category_id = fields.Many2one('iac.part.category', string="Part Category", index=True)
    starttime = fields.Date(string="Create Date From *")
    endtime = fields.Date(string="Create Date To")

    @api.multi
    def search_vendor_evaluation_approval_log(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain += [('plant_code', '=', wizard.plant_id.plant_code)]
            if wizard.supplier_company_id:
                domain += [('company_no', '=', wizard.supplier_company_id.company_no)]
            if wizard.part_category_id:
                domain += [('part_category', '=', wizard.part_category_id.name)]
            if wizard.starttime:
                domain += [('create_date', '>=', wizard.starttime)]
            if wizard.endtime:
                domain += [('create_date', '<=', wizard.endtime)]

            result = self.env['v.vendor.evaluation.approval.log'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor Evaluation Approval Log'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.vendor.evaluation.approval.log'
        }
        return action
