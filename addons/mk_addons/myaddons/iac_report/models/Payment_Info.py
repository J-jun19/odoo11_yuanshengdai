# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions,tools
from odoo.tools.translate import _

class IacPaymentInfoReport(models.Model):
    _name = "v.payment.info.report"
    _auto = False
    _order = 'vendor_code,clear_date,assignment,document'

    @api.depends('amount')
    def _total(self):
        vendor_list = []
        record_list1 = []
        record_list = []
        clear_date_list = []
        record_list2 = []
        record_list3 = []
        assignment_list = []
        document_list = []
        total_count = 0.0

        for item in self:
            total_count += item.amount
            vendor_list.append(item.vendor_code)
            record_list.append(item)

        for i in range(len(vendor_list)):
            if max(vendor_list) == vendor_list[i]:
                record_list1.append(record_list[i])
            else:
                record_list[i].update({
                'total':'',
            })
        if len(record_list1)>1:
            for j in range(len(record_list1)):
                clear_date_list.append(record_list1[j].clear_date)
            for k in range(len(clear_date_list)):
                if max(clear_date_list) == clear_date_list[k]:
                    record_list2.append(record_list1[k])
            if len(record_list2)>1:
                for m in range(len(record_list2)):
                    assignment_list.append(record_list2[m].assignment)
                for n in range(len(assignment_list)):
                    if max(assignment_list) == assignment_list[n]:
                        record_list3.append(record_list2[n])
                if len(record_list3)>1:
                    for p in range(len(record_list3)):
                        document_list.append(record_list3[p].document)
                    for o in range(len(document_list)):
                        if max(document_list) == document_list[o]:
                            index = document_list.index(max(document_list))
                            record_list3[index].update({
                                'total': format(float(str(total_count)),','),
                            })
                else:
                    index = assignment_list.index(max(assignment_list))
                    record_list2[index].update({
                        'total': format(float(str(total_count)),','),
                    })
            else:
                index = clear_date_list.index(max(clear_date_list))
                record_list1[index].update({
                    'total': format(float(str(total_count)),','),
                })
        else:
            index = vendor_list.index(max(vendor_list))
            record_list[index].update({
                'total':format(float(str(total_count)),','),
            })



    vendor_code = fields.Char(string='Vendor')
    clear_date = fields.Char(string='Payment Date')
    assignment = fields.Char()
    document = fields.Char()
    referenece = fields.Char()
    text = fields.Char()
    currency = fields.Char()
    amount = fields.Float()

    total = fields.Char(compute='_total')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_payment_info_report')
        self._cr.execute("""
                    create or replace view v_payment_info_report as (
                        SELECT
                            id, 
                            vendor_code,
                            assignment,
                            document,
                            referenece,
                            text,
                            currency,
                            b,
                            amount,
                            clear_date
                        FROM 
                            payment_info order by vendor_code,clear_date,assignment,document)
                                """)

class IacPaymentInfoReportWizard(models.TransientModel):
    _name = 'payment.info.report.wizard'

    # plant_code = fields.Many2one('pur.org.data',string='Plant')
    vendor_code = fields.Many2one('iac.vendor',string='Vendor *',required=1)
    posting_date_from = fields.Date(string='Payment Date From')
    posting_date_to = fields.Date(string='Payment Date To')


    @api.multi
    def search_payment_info_report(self):
        for item in self.env.user.groups_id:
            if item.name == 'External vendor':
                if not self.env.user.vendor_id:
                    raise exceptions.ValidationError("please go to workspace to set vendor code")
        self.ensure_one()
        # self._cr.execute("delete from payment_info_report")
        result = []
        # print self.env.user.vendor_ids.ids
        vendor_code_list = []
        for wizard in self:
            domain = []

            if wizard.vendor_code:
                domain += [('vendor_code', '=', wizard.vendor_code.vendor_code)]
            else:
                for item in self.env.user.groups_id:
                    if item.name == 'External vendor':
                        for item in self.env.user.vendor_ids:
                            vendor_code = self.env['iac.vendor'].search([('id', '=', item.id)]).vendor_code
                            vendor_code_list.append(vendor_code)
                        domain += [('vendor_code', 'in', vendor_code_list)]
                    if item.name == 'CM':
                        break

            if wizard.posting_date_from:
                domain += [('clear_date', '>=', wizard.posting_date_from)]
            if wizard.posting_date_to:
                domain += [('clear_date', '<=', wizard.posting_date_to)]
            result = self.env['v.payment.info.report'].search(domain)



        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Payment Info Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'v.payment.info.report'
        }
        return action