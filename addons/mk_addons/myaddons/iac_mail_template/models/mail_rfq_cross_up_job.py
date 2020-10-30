# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.odoo_env import odoo_env
import datetime


class MailRfqCrossUpJob(models.Model):
    _name = 'mail.rfq.cross.up.job'

    @odoo_env
    @api.model
    def job_mail_rfq_cross_up_job(self):

        now_time = datetime.datetime.now()
        yes_time = now_time + datetime.timedelta(days=-1)
        yes_date = yes_time.strftime('%Y-%m-%d')
        self._cr.execute("""select rno.id,
               r.webflow_number as webflow_number,
               r.approve_date_web as approve_date_web,
               pod.plant_code as new_plant,
               v.vendor_code as new_vendor,
               v."name" as new_vendor_name,
               mm.part_no as material,
               md.part_description as material_desc,
               r.buyer_code as new_buyer_code,
               bc.buyer_name as new_buyer_name,
               rc."name" as new_currency,
               r.input_price as new_price,
               dc.division as new_division,
               dc.division_description as new_division_desc,
               rno.price_compare as diff,
               pod1.plant_code as old_plant,
               v1.vendor_code as old_vendor,
               v1."name" as old_vendor_name,
               rc1."name" as old_currency,
               r1.input_price as old_price,
               dc1.division as old_division,
               dc1.division_description as old_division_desc,
               r.cost_up_reason_id as cost_up_reason_id,
               rcur.description as cost_up_reason_desc,
               r.buyer_code as old_buyer_code,
               bc1.buyer_name as old_buyer_name
               from iac_rfq_new_vs_old rno
         inner join iac_rfq r on r.id = rno.current_rfq_id
         inner join iac_rfq r1 on r1.id = rno.old_rfq_id
         inner join iac_vendor v on v.id = r.vendor_id
         inner join iac_vendor_account_group ivag on ivag.account_group = v.vendor_account_group
         inner join pur_org_data pod on pod.id = r.plant_id
         inner join material_master mm on mm.id = r.part_id
         inner join material_description md on md.part_no = mm.part_no and md.plant_code = mm.plant_code  
         inner join buyer_code bc on bc.id = r.buyer_code
         inner join res_currency rc on rc.id = r.currency_id
         inner join division_code dc on dc.id = r.division_id
         inner join division_code dc1 on dc1.id = r1.division_id
         inner join iac_vendor v1 on v1.id = r1.vendor_id
         inner join iac_vendor_account_group ivag1 on ivag1.account_group = v1.vendor_account_group
         inner join pur_org_data pod1 on pod1.id = r1.plant_id
         inner join res_currency rc1 on rc1.id = r1.currency_id
         inner join buyer_code bc1 on bc1.id = r1.buyer_code
         inner join iac_rfq_cost_up_reason rcur on rcur.id = r.cost_up_reason_id
         where rno.new_flag = 'Y' 
               and ivag.vendor_type <> 'bvi'
               and ivag1.vendor_type <> 'bvi'
               and cast( to_char(r.approve_date_web, 'yyyy-mm-dd' ) as date )  = cast( to_char( now(), 'yyyy-mm-dd' ) as date ) - 1
               and (rno.id,rno.current_rfq_id,rno.old_rfq_id) 
                 in (select max(id),max(current_rfq_id),max(old_rfq_id) 
                        from iac_rfq_new_vs_old rno1
                        where rno1.current_rfq_id = rno.current_rfq_id and rno1.old_rfq_id = rno.old_rfq_id) and r.approve_date_web is not null
           and r.valid_from <= cast(now() as date)-1 and r.valid_to >= cast(now() as date)-1
           and r1.valid_from <= cast(now() as date)-1 and r1.valid_to >= cast(now() as date)-1
           and r.approve_date_web is not null
           and abs(rno.ratio) > 0.03""")

        search_storage = self._cr.dictfetchall()

        body_lists = []
        email = 'IACPG1813@iac.com.tw'

        if search_storage:
            for storage_obj in search_storage:
                # print storage_obj, str(storage_obj['cost_up_reason_id']), str(storage_obj['new_buyer_code']), str(storage_obj['new_price']), str(storage_obj['old_price']), str(storage_obj['old_buyer_code'])
                vm_extract_lambda = lambda r: r if r not in (False, None) else ''
                body_list = [storage_obj['webflow_number'], storage_obj['approve_date_web'], storage_obj['new_plant'],
                             storage_obj['new_vendor'], storage_obj['new_vendor_name'], storage_obj['material'],
                             storage_obj['material_desc'], str(storage_obj['new_buyer_code']),
                             storage_obj['new_buyer_name'], storage_obj['new_currency'], str(storage_obj['new_price']),
                             storage_obj['new_division'], storage_obj['new_division_desc'], storage_obj['diff'],
                             storage_obj['old_plant'],
                             storage_obj['old_vendor'], storage_obj['old_vendor_name'], storage_obj['old_currency'],
                             str(storage_obj['old_price']), storage_obj['old_division'],
                             storage_obj['old_division_desc'], vm_extract_lambda(str(storage_obj['cost_up_reason_id'])),
                             vm_extract_lambda(storage_obj['cost_up_reason_desc']), str(storage_obj['old_buyer_code']),
                             storage_obj['old_buyer_name']]
                body_lists.append(body_list)

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', '價格異動通知' + str(yes_date),
                                                      ['Webflow 單號', 'Info Record 建立日期', '廠區', '廠商代碼', '廠商名稱', '料號',
                                                       'Desc', '採購代碼',
                                                       '採購名稱', '幣別', 'Info Record價格', 'Division Code', 'Division Name',
                                                       '高價/低價', '廠區', '廠商代碼', '廠商名稱', '幣別', 'RFQ價格', 'Division Code',
                                                       'Division Name', '高於其他原因說明代碼（AS）', '高於其他原因說明（AS）', '採購代碼',
                                                       '採購名稱'], body_lists, 'RFQ_COST_UP_JOB')
