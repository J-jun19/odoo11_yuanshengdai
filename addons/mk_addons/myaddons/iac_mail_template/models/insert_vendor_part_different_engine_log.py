# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.odoo_env import odoo_env
import traceback


class InsertVendorPartDifferentEngineLog(models.Model):
    _name = 'insert.vendor.part.different.engine.log'
    _auto = False

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
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", "Update_Maxqty 执行成功", [], [],
                                                          'engine')
        except:
            # traceback.print_exc()
            self.env.cr.rollback()
            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, "", "Update_Maxqty 执行失败", ['以下是报错信息：'],
                                                      [[(traceback.format_exc())]], 'engine')
