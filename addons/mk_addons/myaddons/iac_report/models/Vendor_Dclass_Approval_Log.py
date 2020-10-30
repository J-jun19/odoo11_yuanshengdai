# -*- coding: utf-8 -*-

from odoo import api,fields,models,tools
from odoo.tools.translate import _



class VendorDclassApprovalLog(models.Model):
    _name = "v.vendor.dclass.approval.log"
    _description = "Vendor D Class Approval Log"
    _auto = False


    company_no = fields.Char('Company No')
    sc_name = fields.Char('Sc Name')
    name = fields.Char('User Name')
    user_score = fields.Char('User Score')
    user_class = fields.Char('User Class')
    memo = fields.Text('Memo')
    create_date = fields.Datetime('Creation Date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_vendor_dclass_approval_log')
        self._cr.execute("""
        CREATE OR REPLACE VIEW public.v_vendor_dclass_approval_log AS
                    select ical.id,
                 sc.company_no,
                 sc."name" as sc_name,
                 rp.name,
                 icsc.user_score,
                 ical.user_class,
                 ical.memo,
                 ical.create_date
          from iac_class_approve_log ical inner
          join iac_class_supplier_company icsc on icsc.id = ical.class_supplier_company_id
          join iac_supplier_company sc on sc.id = icsc.supplier_company_id
          join res_users ru on ru.id = ical.user_id
          join res_partner rp on rp.id = ru.partner_id
          where ical.user_class = 'D'
        """)

class VendorDclassApprovalLogWizard(models.TransientModel):
    _name = 'vendor.dclass.approval.log.wizard'


    supplier_company_id = fields.Many2one('iac.supplier.company', string="Supplier Company", index=True)
    starttime = fields.Date(string="Create Date From")
    endtime = fields.Date(string="Create Date To")

    @api.multi
    def search_vendor_dclass_approval_log(self):
        self.ensure_one()
        result = []
        domain = []
        for wizard in self:
            if wizard.supplier_company_id:
                domain += [('company_no', '=', wizard.supplier_company_id.company_no)]
            if wizard.starttime:
                domain += [('create_date', '>=', wizard.starttime)]
            if wizard.endtime:
                domain += [('create_date', '<=', wizard.endtime)]

            result = self.env['v.vendor.dclass.approval.log'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor D Class Approval Log'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.vendor.dclass.approval.log'
        }
        return action
