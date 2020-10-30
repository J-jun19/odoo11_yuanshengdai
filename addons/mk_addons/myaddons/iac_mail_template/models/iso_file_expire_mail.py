# -*- coding: utf-8 -*-
from odoo import api
from odoo import models
from odoo.odoo_env import odoo_env


class IsoFileExpireMail(models.Model):
    _name = 'iac.iso.file.expire.mail'
    _auto = False

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
