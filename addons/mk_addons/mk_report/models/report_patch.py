# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report'

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """ call the method get_empty_list_help of the model and set the window action help message
        """
        result = super(IrActionsReportXml, self).read(fields, load=load)
        if not fields:
            for values in result:
                values['docx_template'] = False

        return result
