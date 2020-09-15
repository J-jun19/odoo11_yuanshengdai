# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    origin = fields.Char(string='Source Document', states={
        'posted': [('readonly', True)],
        'sent': [('readonly', True)],
        'reconciled': [('readonly', True)],
        'cancelled': [('readonly', True)]
    })
