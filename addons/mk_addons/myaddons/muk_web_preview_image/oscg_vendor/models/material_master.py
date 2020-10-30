# -*- coding: utf-8 -*-
import random
from odoo import models, fields, api
from odoo.osv import expression

class MaterialDescription(models.Model):
    _name = "material.description"

    part_no = fields.Char(string="Part No",index=True)
    language_key = fields.Char(string="Language Key")
    part_description = fields.Char(string="Part Description")
    part_description1 = fields.Char(string="Part Description1")
    plant_code = fields.Char(string="Plant Code",index=True)

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class MaterialMaster(models.Model):
    _name = "material.master"
    _rec_name = 'part_no'

    part_no = fields.Char(string="Part No",index=True)
    creation_date = fields.Date(string="Creation Date")
    change_date = fields.Date(string="Change Date")
    part_type = fields.Char(string="Part Type")
    material_group = fields.Char(string="Material Group")
    unit = fields.Char(string="Unit")
    order_uom = fields.Char(string="Order Uom")
    division = fields.Char(string="Division",index=True)
    material_category = fields.Char(string="Material Category")
    plant_code = fields.Char(string="Plant Code",index=True)
    buyer_code = fields.Char(string='buyer_erp_id',index=True)

    #copy from material.description
    part_description = fields.Char(string="Part Description")
    part_description1 = fields.Char(string="Part Description1")

    #copy from material.plant
    part_status = fields.Char(string="Part Status")
    abc_indicator = fields.Char(string="Abc Indicator")
    critical_part_flag = fields.Char(string="Critical Part Flag")
    buyer_erp_id = fields.Char(string="Buyer Code")
    planner_erp_id = fields.Char(string="Planner Erp Id")
    ltime = fields.Float(string="Ltime",precision=(18,4))
    procurement_type = fields.Char(string="Procurement Type")
    record_point = fields.Float(string="Record Point",precision=(18,4))
    safety_stock = fields.Float(string="Safety Stock",precision=(18,4))
    maximum_stock_level = fields.Float(string="Maximum Stock Level")
    quota_arrangement_usage = fields.Char(string="Quota Arrangement Usage")
    auto_po_allowed = fields.Char(string="Auto Po Allowed")
    commodity_code = fields.Char(string="Commodity Code")
    issue_storage_location = fields.Char(string="Issue Storage Location")
    special_procurement_type = fields.Char(string="Special Procurement Type")
    post_to_insp_stock = fields.Char(string="Post To Insp Stock")
    deletion_flag = fields.Char(string="Deletion Flag")
    rounding_value = fields.Float(string="Rounding Value",precision=(18,6))
    gr_days = fields.Integer(string="Gr Days")

    #copy from material.custmaster
    buy_sell_flag = fields.Char(string="Buy Sell Flag")
    last_buy_flag = fields.Char(string="Last Buy Flag")
    material_group_cn = fields.Char(string="Material Group Cn")
    rma_flag = fields.Char(string="Rma Flag")
    sourcer = fields.Char(string="Sourcer")
    gr_location = fields.Char(string="Gr Location")
    part_status_by_site = fields.Char(string="Part Status By Site")

    #copy from material.division
    division = fields.Char(string="Division")
    creation_date = fields.Date(string="Creation Date")
    created_by = fields.Char(string="Created By")
    change_date = fields.Date(string="Change Date")
    changed_by = fields.Char(string="Changed By")
    deletion_flag = fields.Char(string="Deletion Flag")

    #lwt add relation fields
    division_id=fields.Many2one('division.code',string='Division Info')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)

    #copy from material.division
    part_unique_code = fields.Char(string="Part Unique Code;PartNo+PlantCode",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

    buyer_code_id = fields.Many2one('buyer.code', string="Buyer Info")
    material_group_id = fields.Many2one('material.group', string="Material Group")
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    #废弃字段
    #part_id = fields.Many2one('source.list', 'Part No')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('part_no', '=ilike', name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        res = self.search(domain + args, limit=limit)
        return res.name_get()

    # Ning add begin
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record['part_description']:
                name = record['part_description']
            else:
                name = ''
            if record['part_no']:
                name = record['part_no'] + ' ' + name
            res.append((record['id'], name))
        return res


class MaterialPlant(models.Model):
    _name = "material.plant"

    part_no = fields.Char(string="Part No",index=True)
    plant_code = fields.Char(string="Plant Code",index=True)
    part_status = fields.Char(string="Part Status")
    abc_indicator = fields.Char(string="Abc Indicator")
    critical_part_flag = fields.Char(string="Critical Part Flag")
    buyer_erp_id = fields.Char(string="Buyer Code",index=True)
    planner_erp_id = fields.Char(string="Planner Erp Id")
    ltime = fields.Float(string="Ltime",precision=(18,4))
    procurement_type = fields.Char(string="Procurement Type")
    record_point = fields.Float(string="Record Point",precision=(18,4))
    safety_stock = fields.Float(string="Safety Stock",precision=(18,4))
    maximum_stock_level = fields.Float(string="Maximum Stock Level")
    quota_arrangement_usage = fields.Char(string="Quota Arrangement Usage")
    auto_po_allowed = fields.Char(string="Auto Po Allowed")
    commodity_code = fields.Char(string="Commodity Code")
    issue_storage_location = fields.Char(string="Issue Storage Location")
    special_procurement_type = fields.Char(string="Special Procurement Type")
    post_to_insp_stock = fields.Char(string="Post To Insp Stock")
    deletion_flag = fields.Char(string="Deletion Flag")
    rounding_value = fields.Float(string="Rounding Value",precision=(18,6))
    gr_days = fields.Integer(string="Gr Days")

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class MaterialMAP(models.Model):
    _name = "material.map"

    part_no = fields.Char(string="Part No",index=True)
    price = fields.Float(string="Price",precision=(12,2))
    price_unit = fields.Integer(string="Price Unit")
    plant_code = fields.Char(string="Plant Code",index=True)

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class MaterialCustMaster(models.Model):
    _name = "material.custmaster"

    plant_code = fields.Char(string="Plant Code",index=True)
    part_no = fields.Char(string="Part No",index=True)
    buy_sell_flag = fields.Char(string="Buy Sell Flag")
    last_buy_flag = fields.Char(string="Last Buy Flag")
    material_group_cn = fields.Char(string="Material Group Cn")
    rma_flag = fields.Char(string="Rma Flag")
    sourcer = fields.Char(string="Sourcer")
    gr_location = fields.Char(string="Gr Location")
    part_status_by_site = fields.Char(string="Part Status By Site")

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
class MaterialDivision(models.Model):
    _name = "material.division"
    _rec_name = 'division'

    plant_code = fields.Char(string="Plant Code",index=True)
    part_no = fields.Char(string="Part No",index=True)
    division = fields.Char(string="Division")
    creation_date = fields.Date(string="Creation Date")
    created_by = fields.Char(string="Created By")
    change_date = fields.Date(string="Change Date")
    changed_by = fields.Char(string="Changed By")
    deletion_flag = fields.Char(string="Deletion Flag")

    #lwt add relation fields
    division_id=fields.Many2one('division.code',string='Division Info')
    part_id = fields.Many2one('material.master', 'Part No')
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
    del_flag = fields.Integer(string="Miss Flag",default=0,index=True)