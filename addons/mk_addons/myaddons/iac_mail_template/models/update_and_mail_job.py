# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.odoo_env import odoo_env
import datetime
import traceback
import logging

_logger = logging.getLogger(__name__)


class UpdateAndMailJob(models.Model):
    _name = 'update.and.mail.job'

    @odoo_env
    @api.model
    def job_mail_abnormal_job(self):
        self._cr.execute("""select * from ep_temp_master.extractlog 
                  where cast(extractdate as date) = cast(now() as date)
                   and extractstatus not in ('STEP2DONE','CLEAN')
                   and extractname not in ('POPartner')
                   order by extractname, extractdate """)

        search_storage = self._cr.dictfetchall()
        body_lists = []
        email = 'Zhang.Pei-Wu@iac.com.tw' + ';' + 'Wang.Ningg@iac.com.tw' + ';' + 'Jiang.Shier@iac.com.tw' + ';' + 'Li.Zhen@iac.com.tw'
        if search_storage:

            for storage_obj in search_storage:
                # print storage_obj, str(storage_obj['extractcount'])
                vm_extract_lambda = lambda r: r if r not in (False, None) else ''
                lambda r: r if r not in (False, None) else ''
                body_list = [storage_obj['extractwmid'], storage_obj['extractname'], storage_obj['sourcetable'],
                             storage_obj['desttable'],
                             storage_obj['extractdate'], vm_extract_lambda(str(storage_obj['extractcount'])),
                             storage_obj['extractstatus'], vm_extract_lambda(storage_obj['extractenddate'])]
                body_lists.append(body_list)
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', '今日job失败情况，请抓紧排查', [
                'extractwmid', 'extractname', 'sourcetable', 'desttable', 'extractdate', 'extractcount',
                'extractstatus', 'extractenddate'], body_lists, 'ABNORMAL_JOB')
        else:

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', '今日job正常跑完', [
                'extractwmid', 'extractname', 'sourcetable', 'desttable', 'extractdate', 'extractcount',
                'extractstatus', 'extractenddate'],
                                                      body_lists, 'ABNORMAL_JOB')

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

    @odoo_env
    @api.model
    def job_update_vendor_bank_id_job(self):
        self._cr.execute("""with aaa as
                                (with duplicate_bank as
                                    (select vb.vendor_code ,sum(1) as cnt from vendor_bank vb
                                        group by vb.vendor_code
                                           having sum(1) > 1)
                                              select vb1.id, vb1.vendor_code, vb1.bank_key, vb1.bank_number, 
                                                     vb1.vendor_id, vb1.vendor_reg_id, vb1.swift_code 
                                                  from vendor_bank vb1 inner join duplicate_bank db 
                                                                               on db.vendor_code = vb1.vendor_code
                                                where not exists (select 1 from iac_vendor v where v.bank_id = vb1.id )
                                            ) 
                            delete  from vendor_bank where id in (select id from  aaa)      
                         """)

        self._cr.execute("""update iac_vendor v set bank_id = vb.id
                                 from
                                (select vendor_code, id from vendor_bank ) vb
                                 where vb.vendor_code = v.vendor_code
                                 and v.bank_id is null""")

    @odoo_env
    @api.model
    def job_iso_file_expire_to_vendor_buyer(self, plant, email):

        sql_text = """SELECT 
                                        ivr.id,
            	                        isc.company_no as company_no,
            	                        iv.vendor_code as vendor_code,
            	                        ivr.name1_cn as name1_cn,
            	                        iat.description as file_descp,
            	                        ivra.state as state,
            	                        ivra.expiration_date as expiration_date,
            	                        iv.state as vendor_state,
            	                        rp."name" as buyer        	                        
            	                 from iac_vendor_register_attachment ivra	        
                                 inner join iac_vendor_register ivr on ivr.id = ivra.vendor_reg_id
            	                 inner join iac_vendor iv on iv.vendor_reg_id = ivr.id
            	                 inner join iac_supplier_company_line iscl ON iscl.vendor_id = iv.id
            	                 inner join iac_supplier_company isc on isc.id = iscl.supplier_company_id
            	                 inner join iac_attachment_type iat on iat.id = ivra."type"
            	                 inner join res_partner rp on rp.email = iv.buyer_email
            	                 where ivra.file_id is not null 
            	                 and iat.sub_group = 'iso'
            	                 and ivra.expiration_date is not NULL
                                 and ivra."type" is not null
                                 and (ivra.expiration_date-CURRENT_DATE < 15)
                                 and rp.supplier = false
                                 and iv.state = 'done'
                                 and ivr.plant_id = %s """ % (plant,)
        self.env.cr.execute(sql_text)

        result_all = self.env.cr.dictfetchall()

        body_lists = []

        if result_all:
            for storage_obj in result_all:
                # vm_extract_lambda = lambda r: r if r not in (False, None) else ''
                # lambda r: r if r not in (False, None) else ''
                body_list = [storage_obj['company_no'], storage_obj['vendor_code'],
                             storage_obj['name1_cn'],
                             storage_obj['file_descp'], storage_obj['state'],
                             storage_obj['expiration_date'],
                             storage_obj['vendor_state'], storage_obj['buyer']]
                body_lists.append(body_list)

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "",
                                                      "ISO类文件过期",
                                                      ['Company no', 'vendor code', 'Name',
                                                       'File Dsecp', 'State',
                                                       'Expiration Date', 'Vendor State', 'buyer'],
                                                      body_lists,
                                                      'ISO file expire alert')

    @odoo_env
    @api.model
    def job_supplier_company_abnormal_current_class(self, email):
        sql_text = """select company_no,
                                 "name",
                                 company_name2,
                                 current_class,
                                 score_snapshot,
                                 is_bind,
                                 supplier_type,
                                 create_date,
                                 write_date 
                          from iac_supplier_company isc 
                          where isc.current_class is null or isc.current_class = ''
                          order by company_no """
        self.env.cr.execute(sql_text)
        result_all = self.env.cr.dictfetchall()

        body_lists = []

        if result_all:
            for storage_obj in result_all:
                vm_extract_lambda = lambda r: r if r not in (False, None) else ''
                lambda r: r if r not in (False, None) else ''
                body_list = [storage_obj['company_no'], storage_obj['name'],
                             vm_extract_lambda(storage_obj['company_name2']),
                             vm_extract_lambda(storage_obj['current_class']),
                             vm_extract_lambda(storage_obj['score_snapshot']), str(storage_obj['is_bind']),
                             storage_obj['supplier_type'], storage_obj['create_date'],
                             storage_obj['write_date']]
                body_lists.append(body_list)

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "",
                                                      "Supplier Company Current Class异常，请抓紧时间处理",
                                                      ['company_no', 'name', 'company_name', 'current_class',
                                                       'score_snapshot', 'is_bind', 'supplier_type', 'create_date',
                                                       'write_date'], body_lists,
                                                      'Supplier Company Abnormal Current Class')

    @odoo_env
    @api.model
    def job_update_expiraton_iso_state_job(self):
        self._cr.execute("""update iac_vendor_register_attachment ivra set state = 'inactive' from 
                               (select id,sub_group from iac_attachment_type)iat
                               where ivra."type" = iat.id
                               and iat.sub_group = 'iso'
                               and (ivra.expiration_date < CURRENT_DATE)
                               and ivra.state = 'active'
                               """)

    @odoo_env
    @api.model
    def job_insert_vendor_part_different_engine_log(self, email):
        sql_text = """BEGIN;
                           with update_iacd as
                          (
                           update asn_maxqty amq set maxqty = amq.maxqty + t.maxqty
                           from 
                           (with duplicat_maxasn as (
                            select vendorcode,material,sum(1) from asn_maxqty am 
                            where state = 'done'
                            group by vendorcode,material
                            having sum(1) > 1
                                                    ) 
                           select am.id, am.vendorcode,am.material,am.maxqty,am.engineid from asn_maxqty am 
                           inner join duplicat_maxasn dm on dm.vendorcode = am.vendorcode and dm.material = am.material
                           where am.state = 'done'
                           and am.engineid = 'IACW'
                           ) t
                          where amq.state = 'done'
                          and amq.vendorcode = t.vendorcode
                          and amq.material = t.material
                          and amq.engineid = 'IACD'
                          returning  amq.*     
                         )
                         insert into asn_maxqty_duplicate_update_log select * from  update_iacd;

                         with update_iacw as
                        (
                         update asn_maxqty amq set state = 'cancel'
                         from 
                         (with duplicat_maxasn as (
                          select vendorcode,material,sum(1) from asn_maxqty am 
                          where state = 'done'
                          group by vendorcode,material
                          having sum(1) > 1
                                                  ) 
                         select am.id, am.vendorcode,am.material,am.maxqty,am.engineid from asn_maxqty am 
                         inner join duplicat_maxasn dm on dm.vendorcode = am.vendorcode and dm.material = am.material
                         where am.state = 'done'
                         and am.engineid = 'IACW'
                         ) t
                        where amq.state = 'done'
                        and amq.vendorcode = t.vendorcode
                        and amq.material = t.material
                        and amq.engineid = 'IACW'  
                        returning  amq.*     
                       )
                       insert into asn_maxqty_duplicate_update_log select * from  update_iacw;
                       COMMIT;"""
        try:
            self.env.cr.execute(sql_text)
            # result_all = self.env.cr.dictfetchall()
            # if result_all:
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", "Update_Maxqty 执行成功", [],
                                                      [],
                                                      'engine')
        except:
            # traceback.print_exc()
            self.env.cr.rollback()
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", "Update_Maxqty 执行失败",
                                                      ['以下是报错信息：'],
                                                      [[(traceback.format_exc())]], 'engine')

    @odoo_env
    @api.model
    def job_update_inforecord_id_patch(self):
        sql_text = """select * from ep_temp_master.sp_job_info_inforecord_history_ref_patch()
                         as(v_extractwmid_last varchar,
                            v_count_real integer,
                            v_job_log_last_id integer,
                            v_sp_name varchar)
                   """
        try:
            self.env.cr.execute(sql_text)
        except UserWarning:
            traceback.print_exc()
            err_msg = "打补丁更新inforecord history id异常\n %s" % (traceback.format_exc(),)
            _logger.error("打补丁更新inforecord history id异常\n %s" % (traceback.format_exc(),))
            raise Exception(err_msg)

    @odoo_env
    @api.model
    def job_delete_restful_log_90_days_ago(self):
        self._cr.execute("""delete from ep_temp_master.restful_log where cast(creation_date as date ) < (current_date - 90)""")


    @odoo_env
    def job_vendor_class_call_sap(self):
        vendor_class_objs = self.env['iac.vendor.class.call.sap'].search([('send_flag','=',False)])
        for vendor_class in vendor_class_objs:
            if vendor_class.interface_code == 'ODOO_VENDOR_006':
                sequence = self.env['ir.sequence'].next_by_code('iac.interface.rpc')
                # odoo vendor 006 传参
                vals_006 = {
                    "id": vendor_class.vendor_id.id,
                    "odoo_key": sequence,
                    "biz_object_id": vendor_class.vendor_id.id,
                    "vendor_code": vendor_class.vendor_id.vendor_code,
                    "purchase_org": vendor_class.vendor_id.plant.purchase_org,
                    "current_class": vendor_class.final_class
                }
                try:
                    # self.env.savepoint()
                    _logger.info('开始调用ODOO_VENDOR_006接口')
                    rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                        'iac.interface.rpc'].invoke_web_call_with_log('ODOO_VENDOR_006', vals_006)
                    _logger.info('ODOO_VENDOR_006接口调用结束')
                    if not rpc_result:
                        return exception_log[0]['Message']
                except:
                    self.env.cr.rollback()

            if vendor_class.interface_code == 'ODOO_VENDOR_005':
                if vendor_class.final_class == 'D':
                    vals_005 = {
                        'id': vendor_class.vendor_id.id,
                        'biz_object_id': vendor_class.vendor_id.id,
                        'delete_flag': '0'
                    }
                    try:
                        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                            'iac.interface.rpc'].invoke_web_call_with_log('ODOO_VENDOR_005', vals_005)
                        if rpc_result:
                            vendor_class.vendor_id.write({'state': 'deleted'})
                            vendor_class.vendor_id.vendor_reg_id.with_context({"no_check_short_name": True}).write(
                                {'state': 'deleted'})
                        else:
                            return exception_log[0]['Message']

                    except:
                        self.env.cr.rollback()
                else:
                    # odoo vendor 005 传参
                    vals_005 = {
                        'id': vendor_class.vendor_id.id,
                        'biz_object_id': vendor_class.vendor_id.id,
                        'delete_flag': '1'
                    }
                    try:
                        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                            'iac.interface.rpc'].invoke_web_call_with_log('ODOO_VENDOR_005', vals_005)
                        if rpc_result:
                            vendor_class.vendor_id.write({'state': 'done'})
                            vendor_class.vendor_id.vendor_reg_id.with_context({"no_check_short_name": True}).write(
                                {'state': 'done'})
                        else:
                            return exception_log[0]['Message']
                    except:
                        self.env.cr.rollback()
            vendor_class.write({'send_flag':True})




