# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.odoo_env import odoo_env


class IacRfqSpotLast(models.Model):
    _name = 'iac.rfq.spot.last'
    _table = 'iac_rfq_spot_last'
    _description = "Iac Rfq Spot Last"
    _order = 'id desc'

    vendor_id = fields.Integer()
    part_id = fields.Integer()
    plant_id = fields.Integer()
    currency_id = fields.Integer()
    buyer_code = fields.Integer()
    input_price = fields.Float()
    division_id = fields.Integer()
    valid_from = fields.Datetime()
    valid_to = fields.Datetime()

    @odoo_env
    @api.multi
    def job_select_spot_rfq_last(self):
        self._cr.execute("""
                   select distinct
                          ir1.vendor_id,
                          ir1.part_id,
                          ir1.plant_id,
                          ir1.currency_id,
                          ir1.buyer_code,
                          ir1.input_price,
                          ir1.division_id,
                          ir1.valid_from,
                          ir1.valid_to
                     from iac_rfq ir1
                     inner join iac_vendor vs1 on vs1.id = ir1.vendor_id
                     inner join iac_vendor_account_group ivag1 on ivag1.account_group = vs1.vendor_account_group
                     where (ir1.vendor_id,ir1.part_id,ir1.id
                           ) in
                     (select vs.id,mm1.id,max(rs.id) from   material_master mm1
                                                    inner join iac_rfq rs on rs.part_id = mm1.id
                                                    inner join iac_vendor vs on vs.id = rs.vendor_id
                                                    inner join iac_vendor_account_group ivag on ivag.account_group = vs.vendor_account_group
                      where exists (select irnvo.current_rfq_id from iac_rfq_new_vs_old irnvo
                                            inner join iac_rfq ir on ir.id = irnvo.current_rfq_id
                                            inner join material_master mms on mms.id = ir.part_id
                                   where mms.part_no = mm1.part_no
                                  )
          and rs.valid_from <= cast(now() as date)
          and rs.state = 'sap_ok'
          group by vs.id,mm1.id
                     )and ivag1.vendor_type = 'spot' """)
        result = self.env.cr.dictfetchall()
        # print result
        for vendor_part in result:
            spot_rfq = self.env['iac.rfq.spot.last'].search(
            [('vendor_id', '=', vendor_part['vendor_id']), ('part_id', '=', vendor_part['part_id'])])
            if spot_rfq:
                spot_rfq.write({'plant_id': vendor_part['plant_id'], 'currency_id': vendor_part['currency_id'],
                                'buyer_code': vendor_part['buyer_code'], 'input_price': vendor_part['input_price'],
                                'division_id': vendor_part['division_id'], 'valid_from': vendor_part['valid_from'],
                                'valid_to': vendor_part['valid_to']})
                # self._cr.execute(
                #     "update iac_rfq_spot_last set plant_id=%s,currency_id=%s,buyer_code=%s,input_price=%s,division_id=%s,valid_from=%s,valid_to=%s where vendor_id=%s and part_id=%s",
                #     (vendor_part['plant_id'], vendor_part['currency_id'], vendor_part['buyer_code'],
                #      vendor_part['input_price'], vendor_part['division_id'], vendor_part['valid_from'],
                #      vendor_part['valid_to'], vendor_part['vendor_id'], vendor_part['part_id']))
            else:
                val = {'vendor_id': vendor_part['vendor_id'], 'part_id': vendor_part['part_id'],
                       'plant_id': vendor_part['plant_id'], 'currency_id': vendor_part['currency_id'],
                       'buyer_code': vendor_part['buyer_code'], 'input_price': vendor_part['input_price'],
                       'division_id': vendor_part['division_id'], 'valid_from': vendor_part['valid_from'],
                       'valid_to': vendor_part['valid_to']}
                self.create(val)
                # self._cr.execute("insert into iac_rfq_spot_last values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                #                  (vendor_part['vendor_id'], vendor_part['part_id'], vendor_part['plant_id'],
                #                   vendor_part['currency_id'], vendor_part['buyer_code'], vendor_part['input_price'],
                #                   vendor_part['division_id'], vendor_part['valid_from'], vendor_part['valid_to']))
