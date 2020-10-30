# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions


class IacAsnCustomsSasSearchLine(models.Model):
    _inherit = 'iac.customs.sas.line'
    _name = 'iac.asn.customs.sas.search.line'
    _table = 'iac_customs_sas_line'

    # sas_stock_line_ids = fields.One2many('iac.customs.sas.line.inherit', 'sas_stock_id', string=u'出入库单line ID', index=True)


class IacAsnCustomsSasSearchData(models.Model):
    _inherit = 'iac.customs.sas.header'
    _name = 'iac.asn.customs.sas.search.data'
    _table = 'iac_customs_sas_header'

    sas_stock_line_ids = fields.One2many('iac.asn.customs.sas.search.line', 'sas_stock_id', string=u'出入库单line ID', index=True)


class IacAsnCustomsSasReport(models.TransientModel):

    _name = 'iac.asn.customs.sas.report.wizard'
    # _auto = False

    plant_id = fields.Many2one('pur.org.data',string='Plant *')
    vendor_code = fields.Many2one('iac.vendor',string='Vendor Code')
    sas_dcl_no = fields.Char(string=u'业务申报表编号')
    # part_no = fields.Char(string=u'料号')
    sas_stock_no = fields.Char(string=u'出入库单编号')
    sas_stock_preent_no = fields.Char(string=u'预录入编号')
    stock_typecd = fields.Selection([("I", u"进区"), ("E", u"出区")], string=u"出入库单类型")
    state = fields.Selection([("wait_mm_approve", u"待采购确认"),
                              ("wait_lg_approve", u"待关务确认"),
                              ("mm_reject", u"采购拒绝"),
                              ('lg_approved', u'关务核准'),
                              ("lg_reject", u"关务拒绝"),
                              ("interface_submit_success", u"推送海关系统成功"),
                              ("interface_submit_fail", u"推送海关系统失败"),
                              ('cancel', u'厂商取消'),
                              ("to_cancel", u"作废中"),
                              ("done", "done")], string=u"状态")
    from_date = fields.Date(string='From Date *')
    to_date = fields.Date(string='To Date *')

    @api.multi
    def search_customs_sas_data(self):
        self.ensure_one()
        # result = []
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain += [('plant_id', '=', wizard.plant_id.id)]
            if wizard.vendor_code:
                domain += [('vendor_id', '=', wizard.vendor_code.id)]
            if wizard.sas_dcl_no:
                domain += [('sas_dcl_no', '=', wizard.sas_dcl_no)]
            if wizard.sas_stock_no:
                domain += [('sas_stock_no', '=', wizard.sas_stock_no)]
            if wizard.sas_stock_preent_no:
                domain += [('sas_stock_preent_no', '=', wizard.sas_stock_preent_no)]
            if wizard.stock_typecd:
                domain += [('stock_typecd', '=', wizard.stock_typecd)]
            if wizard.state:
                domain += [('state', '=', wizard.state)]
            if wizard.from_date and not wizard.to_date:
                domain += [('create_date', '>=', wizard.from_date)]
            if wizard.to_date and not wizard.from_date:
                domain += [('create_date', '<=', wizard.to_date)]

            if wizard.from_date and wizard.to_date:
                if wizard.from_date > wizard.to_date:
                    raise exceptions.ValidationError(u'查询日期条件不正确！')
                else:
                    domain += [('create_date', '>=', wizard.from_date), ('create_date', '<=', wizard.to_date)]

            for item in self.env.user.groups_id:
                if item.name == 'External vendor' and not wizard.vendor_code:
                    raise exceptions.ValidationError(u'厂商必须选择vendor code')

            result = self.env['iac.asn.customs.sas.search.data'].search(domain)
            if not result:
                raise exceptions.ValidationError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': 'customs sas',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'iac.asn.customs.sas.search.data'

        }
        return action
