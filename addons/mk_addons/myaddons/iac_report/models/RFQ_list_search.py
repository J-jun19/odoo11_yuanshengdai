# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _




class RfqListSearch(models.Model):
    _name = 'rfq.list.search'
    _inherit = 'iac.rfq'
    _table = 'iac_rfq'

    # rfq_id = fields.Many2one('iac.rfq')
    # rfq_no = fields.Char(related='last_rfq_id.name')


class RfqListSearchForm(models.TransientModel):
    _name = 'rfq.list.search.form'

    vendor = fields.Many2one('iac.vendor', string='Vendor Code')
    part_id = fields.Many2one('material.master', string='Part No')
    rfq_no = fields.Char(string='RFQ NO')
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")


    @api.multi
    def rfq_list(self):
        # print '1111111111111111111111'
        # print self.env.user.id
        self.ensure_one()
        result = []
        for record in self:

            domain = []
            # print record.vendor.vendor_code
            # print  record.part_id.part_no
            if record.vendor:
                domain += [('vendor_id', '=', record.vendor.id)]

            if record.part_id:
                domain += [('part_id', '=', record.part_id.id)]

            if record.rfq_no:
                domain += [('name', 'like', record.rfq_no)]

            if record.valid_from and not record.valid_to:
                domain += [('valid_from', '>=', record.valid_from)]

            if record.valid_to and not record.valid_from:
                domain += [('valid_to', '<=', record.valid_to)]

            if record.valid_from and record.valid_to:

                if record.valid_from > record.valid_to:
                    raise UserError(u'查询日期不符合条件')

                else:
                    domain += ['&', ('valid_from', '>=', record.valid_from), ('valid_to', '<=', record.valid_to)]

            result = self.env['rfq.list.search'].search(domain)

            if not result:
                raise UserError(u'查无资料！')

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': 'Info Record List',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'rfq.list.search'

        }
        return action









