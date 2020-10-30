# -*- coding: utf-8 -*-
import traceback

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError


class IacAdminUpdatePoFlag(models.Model):
    _inherit = 'iac.purchase.order'
    _name = 'iac.admin.update.po.flag'
    _table = 'iac_purchase_order'

    @api.multi
    def write(self, vals):
        try:
            for record in self:
                update_result = self.env['iac.admin.update.po.history'].write_notes(po_nub=record.document_erp_id, po_header_id=record.id,display_flag=vals.get('display_flag',record.display_flag),
                                                                                    version_no=vals.get('version_no',record.version_no),modify_before='display_flag:{},version_no:{}'.format(record.display_flag,record.version_no),
                                                                                    modify_after='display_flag:{},version_no:{}'.format(vals.get('display_flag',record.display_flag),vals.get('version_no',record.version_no)))
                po_result = super(IacAdminUpdatePoFlag, record).write(vals)
                return po_result
        except Exception as e:
            self.env.cr.rollback()
            raise exceptions.ValidationError(e)


class AdminUpdatePoHistory(models.Model):
    _name = 'iac.admin.update.po.history'
    _table = "iac_admin_update_po_history"
    _order = 'id desc'

    po_nub = fields.Char(string="Po Number")
    display_flag = fields.Boolean(string='Display Flag')
    version_no = fields.Char(string="Version No")
    po_header_id = fields.Many2one('iac.purchase.order', string=" Po Header ID", index=True)
    po_line_id = fields.Many2one('iac.purchase.order.line', string=" Po Line ID", index=True)
    action_type = fields.Selection([
                                 ('update po approve state', 'update po approve state'),
                                 ('update po display_flag or version_no', 'update po display_flag or version_no'),
                                    ], string="Admin Action Type")
    modify_before = fields.Char(string="Modify Before")
    modify_after = fields.Char(string="Modify After")

    @api.multi
    def write_notes(self, **kwargs):
        # if kwargs.get('display_flag') and not kwargs.get('version_no'):
        #     kwargs['action_type'] = 'update po display_flag is true'
        #     return self.create(kwargs)
        # elif kwargs.get('version_no') and kwargs.get('display_flag'):
        #     kwargs['action_type'] = 'update po version_no'
        #     return self.create(kwargs)
        # else:
        if kwargs.has_key('display_flag'):
            kwargs['action_type'] = 'update po display_flag or version_no'

        elif kwargs.get('modify_after') == 'state:wait_vendor_confirm':
            kwargs['action_type'] = 'update po approve state'
        return self.create(kwargs)


class AdminSearchPoFlagWizard(models.TransientModel):
    _name = 'iac.admin.search.po.form.wizard'

    po_nub = fields.Char(string='Po Number')
    display_flag = fields.Boolean(string='Display Flag',default=False)
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")

    @api.multi
    def search_po_display_flag(self):
        self.ensure_one()
        result = []
        domain = []
        for record in self:
            if record.po_nub:
                domain += [('name','=',record.po_nub)]
            elif record.display_flag:
                domain += [('display_flag', '=', record.display_flag)]
            elif not record.display_flag:
                domain += [('display_flag', '=', False)]
            else:
                domain += []

            result = self.env['iac.admin.update.po.flag'].search(domain)
            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': 'Po Display Flag',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.admin.update.po.flag'

        }
        return action


class IacAdminUpdatePoStates(models.Model):
    _inherit = 'iac.purchase.order'
    _name = 'iac.admin.update.po.states'
    _table = 'iac_purchase_order'

    def button_to_change_state(self):
        if self.state != 'to_approve':
            raise exceptions.ValidationError('只能变更状态为to_approve的资料')
        try:
            self.write({
                'state':'wait_vendor_confirm'
            })
            self._cr.execute(""" update iac_purchase_order_line pol
                                    set state='wait_vendor_confirm'
                                    where order_id=%s """, (self.id,))

            self.env['iac.admin.update.po.history'].write_notes(po_nub=self.document_erp_id, po_header_id=self.id,
                                                                modify_before='state:{}'.format(self.state),
                                                                modify_after='state:wait_vendor_confirm')
            message = u'更新状态成功！'
            return self.env['warning_box'].info(title="Message", message=message)
        except Exception as e:
            self.env.cr.rollback()
            raise exceptions.ValidationError(e)
            # raise exceptions.ValidationError(traceback.format_exc())


# class IacAdminUpdatePoLineStates(models.Model):
#     _inherit = 'iac.purchase.order.line'
#     _name = 'iac.admin.update.po.line.states'
#     _table = 'iac_purchase_order_line'
#
#     def write(self, vals):
#         super(IacPurchaseOrderLine,self).write(vals)


class AdminSearchPoStateWizard(models.TransientModel):
    _name = 'iac.admin.search.po.approve.wizard'

    po_nub = fields.Char(string='Po Number')
    # display_flag = fields.Boolean(string='Display Flag',default=False)
    # valid_from = fields.Date(string="Valid From")
    # valid_to = fields.Date(string="Valid To")

    @api.multi
    def search_po_approve_state(self):
        self.ensure_one()
        result = []
        domain = []
        for record in self:
            if record.po_nub:
                domain += [('name','=',record.po_nub)]
            # elif record.display_flag:
            #     domain += [('display_flag', '=', record.display_flag)]
            # elif not record.display_flag:
            #     domain += [('display_flag', '=', False)]
            else:
                domain += []

            result = self.env['iac.admin.update.po.states'].search(domain)
            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': 'Po Approve Sate',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'iac.admin.update.po.states'

        }
        return action

