# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import models, api


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def object_to_xmlid(self, record, raise_if_not_found=False):
        res_id = self.sudo().search([('model', '=', record._name), ('res_id', '=', record.id)])

        if res_id:
            xid = '.'.join([res_id.module,res_id.name])
            return xid
        elif raise_if_not_found:
            raise ValueError('No unique ID found for record %s. It may have been deleted.' % (record.name))
        return None