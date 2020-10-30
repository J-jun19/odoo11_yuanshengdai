# -*- coding: utf-8 -*-
from odoo import api
from odoo import models
from odoo.odoo_env import odoo_env


class SupplierCompanyAbnormalCurrentClass(models.Model):
    _name = 'supplier.company.abnormal.current.class'
    _auto = False

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
