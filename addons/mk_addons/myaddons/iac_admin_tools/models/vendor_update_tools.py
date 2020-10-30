# -*- coding: utf-8 -*-
import traceback

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
import os


class IacAdminUpdateVendorVatHeader(models.Model):
    _name = 'iac.admin.maintain.vendor.vat'
    _inherit = "iac.vendor.register"
    _table = 'iac_vendor_register'

    @api.multi
    def write(self, vals):
        try:
            for record in self:
                update_result = self.env['iac.admin.update.vednor.log'].write_notes(vendor_register_id=record.id,
                                                                                    new_vendor_id=record.vendor_id.id,
                                                                                    action_type='maintain vendor vat nub',
                                                                modify_before='vat_number:{}'.format(record.vat_number),
                                                                modify_after='vat_number:{}'.format(vals.get('vat_number')))
                # os.path.join('D:\\GOdoo10_IAC\\myaddons\\oscg_vendor\\models\\vendor.py')
                # vendor_result = super(IacVendorRegister,record).write(vals)
                # return vendor_result
                self._cr.execute(""" update iac_vendor_register ivr 
                                        set vat_number=%s 
                                        where id=%s """,(vals.get('vat_number'),record.id))
                message = u'更新Vat Number成功！'
                return self.env['warning_box'].info(title="Message", message=message)
        except Exception as e:
            self.env.cr.rollback()
            raise exceptions.ValidationError(e)


class IacAdminMaintainVendorLog(models.Model):
    _name = 'iac.admin.update.vednor.log'
    _table = "iac_admin_update_vednor_log"
    _order = 'id desc'

    ori_vendor_id = fields.Many2one('iac.vendor', string="Ori Vendor",index=True)
    new_vendor_id = fields.Many2one('iac.vendor', string="New Vendor",index=True)
    action_type = fields.Selection([
        ('maintain vendor vat nub', 'maintain vendor vat nub'),
    ], string="Admin Action Type")
    vendor_register_id = fields.Many2one('iac.vendor.register', index=True)
    modify_before = fields.Char(string=u'操作之前')
    modify_after = fields.Char(string=u'操作之后')

    @api.multi
    def write_notes(self, **kwargs):
        self.create(kwargs)


class AdminSearchAsnVatWizard(models.TransientModel):
    _name = 'iac.admin.search.vendor.vat.wizard'

    vendor_id = fields.Many2one('iac.vendor',index=True)

    @api.multi
    def search_vendor_vat_nub(self):
        self.ensure_one()
        result = []
        domain = []
        for record in self:
            if record.vendor_id:
                domain += [('ori_vendor_id','=',record.vendor_id.id),('state','not in',['to sap','done','cancel'])]

            else:
                domain += []

            copy_results = self.env['iac.vendor.copy'].search(domain)
            new_vendor_list = []
            for copy in copy_results:
                new_vendor_list.append(copy.new_vendor_id.id)
            result = self.env['iac.admin.maintain.vendor.vat'].browse(new_vendor_list)
            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': u'维护Vat Number',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.admin.maintain.vendor.vat'

        }
        return action