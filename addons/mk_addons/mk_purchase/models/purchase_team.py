# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields, _
from odoo.exceptions import AccessError

class PurchaseTeam(models.Model):
    _name = "purchase.team"
    _inherit = ['mail.thread']
    _description = "Purchases Channel"
    _order = "name"

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        company_id = self.sudo(user_id).env.user.company_id.id
        team_id = self.env['purchase.team'].sudo().search([
            '|', ('user_id', '=', user_id), ('member_ids', '=', user_id),
            '|', ('company_id', '=', False), ('company_id', 'child_of', [company_id])
        ], limit=1)
        if not team_id and 'default_team_id' in self.env.context:
            team_id = self.env['purchase.team'].browse(self.env.context.get('default_team_id'))
        return team_id

    name = fields.Char('Purchases Channel', required=True, translate=True)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the purchases channel without removing it.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('purchase.team'))
    currency_id = fields.Many2one(
        "res.currency", related='company_id.currency_id',
        string="Currency", readonly=True)
    user_id = fields.Many2one('res.users', string='Channel Leader')
    member_ids = fields.Many2many('res.users', 'purchase_team_users_rel', string='Channel Members')

