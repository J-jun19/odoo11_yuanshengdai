# -*- coding: utf-8 -*-
import traceback

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError


class IacAdminUpdateCustomsHeader(models.Model):
    _name = 'iac.admin.update.customs.header'
    _inherit = "iac.customs.sas.header"
    _table = 'iac_customs_sas_header'

    sas_stock_line_ids = fields.One2many('iac.admin.update.customs.line', 'sas_stock_id', string=u'出入库单line ID', index=True)

    # orig_sas_id = fields.One2many('iac.customs.sas.header','update_customs_id',string='出入库单id')
    # def button_restore_export(self):
    #     pass


class IacAdminUpdateCustomsLine(models.Model):
    _name = 'iac.admin.update.customs.line'
    _inherit = "iac.customs.sas.line"
    _table = 'iac_customs_sas_line'

    sas_stock_id = fields.Many2one('iac.admin.update.customs.header', string=u'出入库单header ID', index=True)

    def restore_sas_valid_export_qty(self):
        if self.state == 'mm_reject':
            raise exceptions.ValidationError('不可重复还原数量')
        try:
            log_vals = {
                'customs_no': self.sas_stock_no,
                'sas_enter_header_id': self.sas_stock_id.orig_sas_id,
                'sas_out_header_id': self.sas_stock_id.id,
                'sas_line_id': self.id,
                'action_type': 'update sas line valid export qty',
                'modify_before_export_qty': self.orig_sas_line_id.valid_export_qty,
                # 'modify_after_export_qty': self.orig_sas_line_id.valid_export_qty + self.dcl_qty,
                'dcl_qty': self.dcl_qty,
                'part_id': self.part_id.id
            }
            # 还原入库单line的可退数量
            self._cr.execute(""" update iac_customs_sas_line csl 
                                set valid_export_qty=csl.valid_export_qty+t.dcl_qty
                                from (
                                    select * from iac_customs_sas_line where sas_stock_id=%s
                                ) t
                                where csl.id=t.orig_sas_line_id """, (self.id,))
            self.write({'state':'mm_reject'})
            # 记log
            self.write_update_log(**log_vals)
            message = u'数量还原成功！'
            return self.env['warning_box'].info(title="Message", message=message)

        except Exception as e:
            self.env.cr.rollback()
            raise exceptions.ValidationError(e)

    def write_update_log(self,**kwargs):
        # log_vals = {
        #     'customs_no': self.sas_stock_no,
        #     'sas_enter_header_id': self.sas_stock_id.orig_sas_id,
        #     'sas_out_header_id': self.sas_stock_id.id,
        #     'sas_line_id': self.id,
        #     'action_type': 'update sas line valid export qty',
        #     'modify_before_export_qty': self.orig_sas_line_id.valid_export_qty,
        #     'modify_after_export_qty': self.orig_sas_line_id.valid_export_qty+self.dcl_qty,
        #     'dcl_qty': self.dcl_qty,
        #     'part_id': self.part_id.id
        # }
        kwargs.update({'modify_after_export_qty': self.orig_sas_line_id.valid_export_qty+self.dcl_qty})
        self.env['iac.admin.update.customs.log'].create(kwargs)


class IacAdminUpdateCustomsLog(models.Model):
    _name = 'iac.admin.update.customs.log'
    _table = "iac_admin_update_customs_log"
    _order = 'id desc'

    customs_no = fields.Char('customns nub')
    sas_enter_header_id = fields.Many2one('iac.customs.sas.header',string='入库单id',index=True)
    sas_out_header_id = fields.Many2one('iac.customs.sas.header',string='出库单id',index=True)
    sas_line_id = fields.Many2one('iac.customs.sas.line',string='sas line id',index=True)
    pass_port_header_id = fields.Many2one('iac.customs.pass.port.header',string='pass port header id',index=True)
    action_type = fields.Selection([
        ('update sas line valid export qty', 'update sas line valid export qty'),
    ], string="Admin Action Type")
    modify_before_export_qty = fields.Float(string=u'原入库单可退数量',digits=(19,5))
    modify_after_export_qty = fields.Float(string=u'还原后入库单可退数量',digits=(19,5))
    dcl_qty = fields.Float(string=u'出库单申报数量', digits=(19, 5))
    part_id = fields.Many2one('material.master', string=u'料号ID', index=True)


class AdminSearchCustomsLineWizard(models.TransientModel):
    _name = 'iac.admin.search.customs.line.wizard'

    # id = fields.Integer(string=u'出库单id')
    sas_stock_id = fields.Integer(string=u'出库单id')
    sas_stock_no = fields.Char(string=u'出库单编号')
    sas_dcl_no = fields.Char(string=u'业务申报表编号')

    @api.multi
    def search_customs_qty(self):
        self.ensure_one()
        result = []
        domain = [('stock_typecd','=','E')]
        for record in self:
            if record.sas_stock_id:
                domain += [('id','=',record.sas_stock_id)]
            elif record.sas_stock_no:
                domain += [('sas_stock_no', '=', record.sas_stock_no)]
            elif record.sas_dcl_no:
                domain += [('sas_dcl_no', '=', record.sas_dcl_no)]
            else:
                domain += []

            result = self.env['iac.admin.update.customs.header'].search(domain)
            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': u'还原入库单可退数量',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'iac.admin.update.customs.header'

        }
        return action


class IacAdminUpdateCustomsState(models.Model):
    _name = 'iac.admin.update.customs.state'
    # _inherit = "iac.admin.update.customs.header"
    _inherit = ['iac.customs.sas.header','iac.customs.pass.port.header']
    # _inherits = {
    #     'iac.customs.sas.header': 'id',
    #     'iac.customs.pass.port.header': 'id',
    # }
    # # _table = 'iac_customs_sas_header'
    # sas_stock_id = fields.Many2one('iac.customs.sas.header', required=True, ondelete='cascade')
    # pass_port_id = fields.Many2one('iac.customs.pass.port.header', required=True, ondelete='cascade')

    def button_to_change_state(self):
        try:
            if self.state == 'interface_submit_fail':
                self.write({'state':'wait_lg_approve'})
                self.env['iac.admin.update.customs.log'].create()
                pass

        except Exception as e:
            self.env.cr.rollback()
            raise exceptions.ValidationError(e)


class AdminSearchCustomsStateWizard(models.TransientModel):
    _name = 'iac.admin.search.customs.state.wizard'

    list_type = fields.Selection([
        ('出入库单', '出入库单'),
        ('核放单', '核放单')
    ], string="查询单据类型")
    sas_stock_id = fields.Integer(string=u'出库单id')
    pass_port_id = fields.Integer(string=u'核放单id')
    sas_stock_no = fields.Char(string=u'出库单编号')
    pass_port_no = fields.Char(string=u'核放单编号')

    @api.multi
    def search_customs_state(self):
        self.ensure_one()
        result = []
        domain = []
        for record in self:
            if record.sas_stock_id:
                domain += [('id','=',record.sas_stock_id)]
            elif record.sas_stock_no:
                domain += [('sas_stock_no', '=', record.sas_stock_no)]
            elif record.pass_port_id:
                domain += [('id', '=', record.pass_port_id)]
            elif record.pass_port_no:
                domain += [('pass_port_no', '=', record.pass_port_no)]
            else:
                domain += []

            if record.sas_stock_id or record.sas_stock_no:
                model_name = 'iac.customs.sas.header'
            else:
                model_name = 'iac.customs.pass.port.header'

            result = self.env[model_name].search(domain)
            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': u'变动海关单据状态',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.admin.update.customs.state'

        }
        return action
