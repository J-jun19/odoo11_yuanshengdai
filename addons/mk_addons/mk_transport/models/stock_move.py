# -*- coding: utf-8 -*-
# Copyright 2018 Jarvis (www.odoomod.com)

from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    def name_get(self):
        if self.env.context.get('stock_move_display') == 'product_name':
            res = []
            for move in self:
                res.append((move.id, '%s' % (move.product_id.name)))
            return res
        else:
            return super(StockMove, self).name_get()
