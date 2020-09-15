# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tz = fields.Selection(default='Asia/Shanghai')

    birthday = fields.Date('Birthday')
    nation_id = fields.Many2one('res.nation', string='Nation')

    district_id = fields.Many2one('res.city.district', string="District", domain="[('city_id','=',city_id)]")

    qq = fields.Char('QQ')
    wechat = fields.Char('Wechat')
    taobao = fields.Char('Taobao')
    alipay = fields.Char('Alipay')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        try:
            hide = self.env.user.has_group('mk_base.group_hide_customer')
        except Exception:
            hide = False
        if hide:
            args.append(('customer', '=', False))

        try:
            hide = self.env.user.has_group('mk_base.group_hide_supplier')
        except Exception:
            hide = False
        if hide:
            args.append(('supplier', '=', False))

        return super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation == 'write' and self.env.user.has_group('mk_base.group_disable_edit_partner'):
            return False
        elif operation == 'unlink' and self.env.user.has_group('mk_base.group_disable_delete_partner'):
            return False
        else:
            return super(ResPartner, self).check_access_rights(operation, raise_exception)

    @api.onchange('name', 'mobile', 'phone', 'email')
    def onchange_duplicate_warning(self):
        def fields_to_domain(fields):
            domain = []
            for field in fields:
                value = safe_eval('self.'+field)
                if value:
                    domain.append((field, '=', value))
            count = len(domain)
            if count > 0:
                domain.insert(['|']*count)

        if self.active and (self.name or self.phone or self.mobile or self.email or self.vat):
            res = self.search(
                ['&', '|', '|', '|', '|', ('name', '=', self.name), ('phone', '=', self.phone), ('vat', '=', self.vat),
                 ('mobile', '=', self.mobile), ('email', '=', self.email), ('active', '=', True)])
            if len(res) >= 1:
                warning = {}
                title = _("Warning")
                message = _('Duplicate Contact\nName: %s\nEmail: %s\nMobile: %s\nPhone: %s\nVat: %s') % (
                    self.name or '', self.email or '', self.mobile or '', self.phone or '', self.vat or '')
                warning['title'] = title
                warning['message'] = message
                return {'warning': warning}
        return {}
