# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PLMActualVendor(models.Model):
    _name = "plm.actual.vendor"
    
    name = fields.Char(string="name")
    fullname = fields.Char(string="Full Name")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

class PLMSubclass(models.Model):
    _name = "plm.subclass"

    plm_id = fields.Char(string="PLM ID")
    subclass = fields.Char(string="SubClass")
    class_code = fields.Char(string="Class Code")
    material_code = fields.Char(string="MaterialCode")
    cht_name = fields.Char(string="CHT Name")
    full_name = fields.Char(string="Full Name")
    material_group = fields.Char(string="Material Group")
    created_by = fields.Char(string="Created By")
    created_date = fields.Char(string="Created Date")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info")
    sap_temp_id = fields.Integer(string="Sap Temp Info")
    need_re_update = fields.Integer(string="Need Call Update Func",default=0)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0)
    material_group_id = fields.Many2one('material.group', string="Material Group",index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    @api.multi
    def name_get(self):
        return [(request.id, request.subclass) for request in self]
