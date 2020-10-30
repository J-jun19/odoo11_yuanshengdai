# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class VendorBuyerEmailWizard(models.TransientModel):
    _name = 'iac.vendor.buyer_email.wizard'

    # vendor_id = fields.Many2one('iac.vendor', string="Vendor *", domain=lambda self: [('plant', 'in', self.env.user.partner_id.plant_ids.ids)], required=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor *", required=True)
    buyer_email = fields.Char(string="Buyer Email *", required=True)
    sales_email = fields.Char(string='Sales Email *')
    other_emails = fields.Char(string='Other Email *')

    @api.onchange('vendor_id')
    def onchange_vendor_id(self):
        if self.vendor_id:
            # print self.vendor_id.id
            vendor_reg_id = self.vendor_id.vendor_reg_id.id
            vendor_reg = self.env['iac.vendor.register.fcst'].sudo().browse(vendor_reg_id)
            self.buyer_email = vendor_reg.buyer_email
            self.sales_email = vendor_reg.sales_email
            self.other_emails = vendor_reg.other_emails

    @api.multi
    def change_buyer_email(self):
        if self.vendor_id:
            # 校验buyer email
            # buyer_flag = False
            # for user in self.env.ref('oscg_vendor.IAC_buyer_groups').users:
            #    if self.buyer_email and self.buyer_email.lower() == user.email.lower():
            #        buyer_flag = True
            # if not buyer_flag:
            #    raise UserError(u'Buyer Email不存在，请核实后重新输入！')
            buyer_email = self.buyer_email.lower()
            sales_email = self.sales_email.lower()
            self.env.cr.execute("select email  from res_partner where lower(email) = %s", (buyer_email,))
            mail_exist = self.env.cr.fetchall()
            if not mail_exist:
                raise UserError('请确认维护的buyer email是否正确！')
            if self.other_emails:
                other_emails = self.other_emails.lower()
            else:
                other_emails = ''
            self.env.cr.execute("select vendor_reg_id from iac_vendor where id=%s", (self.vendor_id.id,))
            pg_result = self.env.cr.fetchall()
            vendor_reg_id = pg_result[0][0]

            self.vendor_id.buyer_email = self.buyer_email.lower()
            # self.vendor_id.vendor_reg_id.buyer_email = self.buyer_email.lower()
            self.env.cr.execute(
                "update iac_vendor_register set buyer_email=%s,sales_email=%s,other_emails=%s where id =%s",
                (buyer_email, sales_email, other_emails, vendor_reg_id))
            self.env.cr.execute(
                "update iac_vendor_change_basic set buyer_email=%s,sales_email=%s where vendor_reg_id =%s and state  not in ('done','cancel')",
                (buyer_email, sales_email, vendor_reg_id))
            return self.env['warning_box'].info(title=u"提示", message=u"Buyer/Vendor email修改成功！")
