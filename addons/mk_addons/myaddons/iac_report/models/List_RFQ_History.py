# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from datetime import datetime, timedelta,date
from odoo.modules.registry import RegistryManager
from odoo.exceptions import UserError, ValidationError
import time


class RfqHistory(models.Model):
    _name='v.report.rfq.history'
    _description = "Rfq History"
    # _auto = False

    vendor_code=fields.Char()
    vendor_name=fields.Char()
    part_no=fields.Char()
    description=fields.Char()
    purchase_org=fields.Char()
    creation_date=fields.Date()
    valid_from=fields.Date()
    valid_to=fields.Date()
    currency=fields.Char()
    price=fields.Float(digits=(18,6))
    previous_price = fields.Float(digits=(18,6))
    price_unit=fields.Char()
    price_control=fields.Char()
    pur_grp=fields.Char()
    buyer_name=fields.Char()
    division=fields.Char()
    final_status=fields.Char()
    ep_status=fields.Char()
    detail_status = fields.Char()
    rfq_no=fields.Char()
    reason=fields.Char()
    cw=fields.Char()
    rw=fields.Char()
    ltime=fields.Char()
    moq=fields.Char()
    mpq=fields.Char()
    taxcode=fields.Char()
    create_mode=fields.Char()
    material_group=fields.Char()
    vendor_part_no = fields.Char(string='manuafacturer part no')

    # @api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'v_rfq_history')
    #     self._cr.execute("""
    #                         CREATE OR REPLACE VIEW public.v_rfq_history AS
    #                                      SELECT row_number() OVER () AS id,
    #                                         a.vendor_code,
    #                                         a.vendor_name,
    #                                         a.part_no,
    #                                         a.description,
    #                                         a.purchase_org,
    #                                         a.creation_date,
    #                                         a.valid_from,
    #                                         a.valid_to,
    #                                         a.currency,
    #                                         a.price,
    #                                         a.price_unit,
    #                                         a.price_control,
    #                                         a.pur_grp,
    #                                         a.buyer_name,
    #                                         a.division,
    #                                         a.final_status,
    #                                         a.ep_status,
    #                                         a.rfq_no,
    #                                         a.reason,
    #                                         a.cw,
    #                                         a.rw,
    #                                         a.ltime,
    #                                         a.moq,
    #                                         a.mpq,
    #                                         a.taxcode,
    #                                         a.create_mode,
    #                                         a.material_group
    #                                        FROM ( SELECT ih.vendor_code,
    #                                                 iv.name AS vendor_name,
    #                                                 ih.part_no,
    #                                                 mm.part_description AS description,
    #                                                 ih.purchase_org,
    #                                                 ih.creation_date,
    #                                                 ih.valid_from,
    #                                                 ih.valid_to,
    #                                                 ih.currency,
    #                                                 ih.price,
    #                                                 ih.price_unit,
    #                                                 ih.price_control,
    #                                                 mm.buyer_erp_id AS pur_grp,
    #                                                 bc.buyer_name,
    #                                                 mm.division,
    #                                                 'Finished'::character varying AS final_status,
    #                                                 'sap_ok'::character varying AS ep_status,
    #                                                 ''::text AS rfq_no,
    #                                                 ''::text AS reason,
    #                                                 ih.cw,
    #                                                 ih.rw,
    #                                                 ih.ltime,
    #                                                 ih.moq,
    #                                                 ih.mpq,
    #                                                 ih.taxcode,
    #                                                 ''::text AS create_mode,
    #                                                 mm.material_group
    #                                                FROM inforecord_history ih,
    #                                                 iac_vendor iv,
    #                                                 material_master mm,
    #                                                 buyer_code bc
    #                                               WHERE ih.vendor_id = iv.id AND ih.part_id = mm.id AND mm.buyer_erp_id::text = bc.buyer_erp_id::text
    #                                             UNION
    #                                              SELECT iv.vendor_code,
    #                                                 iv.name AS vendor_name,
    #                                                 mm.part_no,
    #                                                 mm.part_description AS description,
    #                                                 ir.purchase_org,
    #                                                 ir.create_date AS creation_date,
    #                                                 ir.valid_from,
    #                                                 ir.valid_to,
    #                                                 rc.name AS currency,
    #                                                 ir.rfq_price AS price,
    #                                                 ir.price_unit,
    #                                                 ir.price_control,
    #                                                 mm.buyer_erp_id AS pur_grp,
    #                                                 bc.buyer_name,
    #                                                 mm.division,
    #                                                 ir.state AS final_status,
    #                                                 ir.state AS ep_status,
    #                                                 ''::text AS rfq_no,
    #                                                 ''::text AS reason,
    #                                                 ir.cw,
    #                                                 ir.rw,
    #                                                 ir.lt AS ltime,
    #                                                 ir.moq,
    #                                                 ir.mpq,
    #                                                 ir.tax AS taxcode,
    #                                                 ''::text AS create_mode,
    #                                                 mm.material_group
    #                                                FROM iac_rfq ir,
    #                                                 iac_vendor iv,
    #                                                 material_master mm,
    #                                                 buyer_code bc,
    #                                                 res_currency rc
    #                                               WHERE ir.vendor_id = iv.id AND ir.part_id = mm.id AND mm.buyer_erp_id::text = bc.buyer_erp_id::text AND ir.currency_id = rc.id AND ir.state::text <> 'sap_ok'::text) a;
    #                           """)



class IacRfqHistoryWizard(models.TransientModel):
       _name = "iac.rfq.history.wizard"

       plant_id = fields.Many2one('pur.org.data',u'Plant',domain=lambda self: [
           ('id','in',self.env.user.plant_id_list)])
       material_id = fields.Many2one('material.group',string="Material Group")
       part_no = fields.Char(string="Part No")
       buyer_code = fields.Char(string="Buyer Code")
       date_from  = fields.Date(string="开始日期")
       date_to = fields.Date(string="结束日期")
       valid_from = fields.Date(string="Valid From")
       valid_to = fields.Date(string="Valid To")
       division_id = fields.Char(string="Division")
       vendor_code = fields.Char(string="Vendor Code")

       plant_ids = fields.Many2one('pur.org.data',u'Plant')
       buyer_codes = fields.Many2one('buyer.code',u'Buyer_Code')

       # @api.onchange('plant_id')
       # def _onchange_plant_id(self):
       #  # 判断当前user是否有某用户组的权限 if self.env.user.has_group('sale.group_show_price_subtotal'):
       #      if self.plant_id:
       #          return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
       #                                       ('state', 'in', ('done', 'block'))]}}
       #      else:
       #          return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

       def get_local_cr(self):
           db_name = self.env.registry.db_name
           registry = RegistryManager.get(db_name)
           cr = registry.cursor()
           return cr

       def turn_to_timestamp(self,strValue):
           d = datetime.strptime(strValue, "%Y-%m-%d")
           t = d.timetuple()
           timeStamp = int(time.mktime(t))
           timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
           return timeStamp

       @api.multi
       def search_rfq_history_report(self):
           cr = self.get_local_cr()
           lc_purchase_orgs = ''
           lc_material_id = ''
           lc_part_no = ''
           lc_buyer_code = ''
           lc_division_id = ''
           lc_vendor_code = ''
           lc_date_from = ''
           lc_date_to = ''
           lc_valid_from = ''
           lc_valid_to = ''
           for wizard in self:
               domain = []
               if wizard.plant_id:
                   print wizard.plant_id.purchase_org
                   lc_purchase_orgs = wizard.plant_id.purchase_org
                   # domain += [('purchase_org', '=', purchase_orgs)]

               print domain
               if wizard.material_id:
                   lc_material_id = wizard.material_id.material_group
                   domain += [('material_group', '=', wizard.material_id.material_group)]

               if wizard.part_no:
                   lc_part_no = wizard.part_no
                   domain += [('part_no', '=', wizard.part_no)]
               if wizard.buyer_code:
                   lc_buyer_code = wizard.buyer_code
                   domain += [('pur_grp', '=', wizard.buyer_code)]

               #self.env['iac.vendor.register.attachment'].search([('active', '=', True),('time_sensitive', '=', True),('expiration_date', '<=',fields.Datetime.to_string(deadline))]):
               #before_days = self.env['ir.config_parameter'].get_param('attachment_before_days', False)
               #deadline = datetime.now() - timedelta(days=int(before_days))

               # if wizard.date_from and not wizard.date_to:
               #     print wizard.date_from
               #     # new_timestamp = self.turn_to_timestamp(wizard.date_from)
               #     # fromtime = fields.Datetime.to_string(wizard.date_from)
               #     domain += [('creation_date', '>=', wizard.date_from)]
               #     # cr_date = datetime(2013, 10, 31, 18, 23, 29, 227)
               #     # >> > cr_date.strftime('%m/%d/%Y')
               # if wizard.date_to and not wizard.date_from:
               #     # strftime2 = fields.datetime.to_string(wizard.date_to)
               #     domain += [('creation_date', '<=', wizard.date_to)]
               # #('expiration_date', '<=', fields.Datetime.to_string(deadline))]):
               # if wizard.date_from and wizard.date_to :
               # # 比较大小
               # #     strftime = fields.datetime.to_string(wizard.date_from)
               # #     strftime2 = fields.datetime.to_string(wizard.date_to)
               #     if wizard.date_from>wizard.date_to :
               #         raise UserError('查询日期不符合条件！')
               #     else:
               #         # new_timestamp = self.turn_to_timestamp(wizard.date_from)
               #         # new_timestamp2 = self.turn_to_timestamp(wizard.date_to)
               #         # a = ('state', '><', 'draft')
               #         # b = ('tians', '<=', 1)
               #         # a and b:[a, b]
               #         # 或['&', a, b]
               #         # a or b:['|', a, b]
               #         domain += ["&",('creation_date', '>=', wizard.date_from),('creation_date', '<=', wizard.date_to)]
               # if wizard.valid_from and not wizard.valid_to:
               #     # strftime = fields.datetime.to_string(wizard.valid_from)
               #     domain += [('valid_from', '>=',wizard.valid_from )]
               # if wizard.valid_to and not wizard.valid_from:
               #     # strftime2 = fields.datetime.to_string(wizard.valid_to)
               #     domain += [('valid_to', '<=', wizard.valid_to)]
               # if wizard.valid_from and wizard.valid_to :
               # # 比较大小
               # #     strftime = fields.datetime.to_string(wizard.valid_from)
               # #     strftime2 = fields.datetime.to_string(wizard.valid_to)
               #     if wizard.valid_from>wizard.valid_to :
               #         raise UserError('查询日期不符合条件！')
               #     else:
               #         domain += [('valid_from', '>=', wizard.valid_from)]
               #         domain += [('valid_to', '<=', wizard.valid_to)]
               if wizard.date_from:
                   lc_date_from = wizard.date_from
               if wizard.date_to:
                   lc_date_to = wizard.date_to
               if wizard.valid_from:
                   lc_valid_from = wizard.valid_from
               if wizard.valid_to:
                   lc_valid_to = wizard.valid_to
               if wizard.division_id:
                   lc_division_id = wizard.division_id
                   domain += [('division', '=', wizard.division_id)]
               if wizard.vendor_code:
                   lc_vendor_code = wizard.vendor_code
                   domain += [('vendor_code', '=', wizard.vendor_code)]
               result = self.env['v.report.rfq.history'].search(domain)
           cr.close()
           self.env.cr.execute('select v_id from public.proc_report_rfq_history_report'
                               ' (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) as (v_id int8)',
                               (lc_purchase_orgs, lc_material_id, lc_part_no,
                                lc_buyer_code, lc_date_from,lc_date_to,lc_valid_from,
                                lc_valid_to,lc_division_id,lc_vendor_code))

           result_rfq_history = self.env.cr.fetchall()
           result_ids = []
           for result_rfq_history_wa in result_rfq_history:
               result_ids.append(result_rfq_history_wa)

           action = {
               'domain': [('id', 'in', result_ids)],
               'name': _('Rfq History'),
               'type': 'ir.actions.act_window',
               'view_mode': 'tree',
               'res_model': 'v.report.rfq.history'
           }
           return action

       # def search_rfq_history_report(self):
       #     self.ensure_one()
       #     result = []
       #     result = self.get_user_palnt()


# class VendorAttachmentCustReport(models.AbstractModel):
#     _name = "report.oscg_vendor.vendor_attachment_cust_report"
#
#     @api.model
#     def render_html(self, docids, data=None):
#         report_obj = self.env['report']
#         report = report_obj._get_report_from_name('oscg_vendor.vendor_attachment_cust_report')
#         docs = self.env['iac.vendor.attachment.report'].browse(docids)
#         country_ids = self.env['res.country'].search([])
#
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': report.model,
#             'docs': docs,
#             'country_ids': country_ids
#         }
#         return report_obj.render(report.report_name, docargs)






