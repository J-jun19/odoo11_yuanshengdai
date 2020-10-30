# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GoodsReceipts(models.Model):
    _name = "goods.receipts"
    _description = u"Goods Receipts"

    sap_control_no = fields.Char(string="SAP NO",index=True)
    document_erp_id = fields.Char(string="SAP ID",index=True)#purchase order code
    po_line_no = fields.Char(string="Po Line No",index=True)#purchase order line code
    gr_document_year = fields.Integer(string="GR Year")
    gr_document_no = fields.Char(string="GR No",index=True)
    gr_document_line_no = fields.Char(string="GR Line No",index=True)
    asn_no = fields.Char(string="ASN NO",index=True)
    asn_line_no = fields.Integer(string="ASN Line NO",index=True)
    gr_document_date = fields.Date(string="GR Date")
    gr_document_time = fields.Datetime(string="GR Time")
    company_code = fields.Char(string="Company Code",index=True)
    buyer_erp_id = fields.Char(string="Buyer Code",index=True)
    plant_code = fields.Char(string="Plant Code",index=True)
    part_no = fields.Char(string="Part No",index=True)
    movement_type = fields.Char(string="Move Type")
    qty_total = fields.Float(string="Total Quantity")
    qty_received = fields.Float(string="Received Quantity")
    vendor_code = fields.Char(string="Vendor Code", index=True)

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No', index=True)
    plant_id = fields.Many2one('pur.org.data', 'Plant', index=True)
    vendor_id = fields.Many2one('iac.vendor', 'Vendor Info', index=True)
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
    #废弃字段
    # po_line_id = fields.Many2one('iac.po.item', string='PO Line')

class VsWebflowIQCData(models.Model):
    _name = "vs.webflow.iqc.data"

    supplier_company_id = fields.Char(string="Supplier Company Id",index=True)
    plant_code = fields.Char(string="Plant Code",index=True)
    vendor_code = fields.Char(string="Vendor Code",index=True)
    material_group = fields.Char(string="Material Group",index=True)
    gr_ma = fields.Float(string="Gr Ma", precision=(18, 6))
    gr_mi = fields.Float(string="Gr Mi", precision=(18, 6))
    qual_qty = fields.Float(string="Qual Qty", precision=(18, 6))
    return_qty = fields.Float(string="Return Qty", precision=(18, 6))
    tc_qty = fields.Float(string="Tc Qty", precision=(18, 6))
    gr_qty = fields.Float(string="Gr Qty", precision=(18, 6))
    rma_ma = fields.Float(string="Rma Ma", precision=(18, 6))
    rma_mi = fields.Float(string="Rma Mi", precision=(18, 6))
    mo_cnf_qty = fields.Float(string="Mo Cnf Qty", precision=(18, 6))
    lurking_cost = fields.Float(string="Lurking Cost", precision=(18, 6))
    hardness_cost = fields.Float(string="Hardness Cost", precision=(18, 6))
    creation_date = fields.Date(string="Creation Date")
    flag = fields.Char(string="Flag")
    cdt = fields.Char(string="Cdt")
    part_no = fields.Char(string="Part No",index=True)

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    plant_id = fields.Many2one('pur.org.data', 'Plant')
    material_group_id = fields.Many2one('material.group', 'Material Group')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class ASNMaxQTY(models.Model):
    _name = "asn.maxqty"

    version = fields.Char(string="Version")
    vendorcode = fields.Char(string="Vendorcode",index=True)
    plant = fields.Char(string="Plant",index=True)
    material = fields.Char(string="Material",index=True)
    deliverytype = fields.Char(string="Deliverytype")
    maxqty = fields.Integer(string="Maxqty")
    engineid = fields.Selection([("IACD","IACD"),("IACW","IACW")],string="Engineid")
    createdate = fields.Date(string="Createdate")
    division = fields.Char(string="Division",index=True)

    #lwt add relation fields
    division_id=fields.Many2one('division.code',string='Division Info')
    part_id = fields.Many2one('material.master', string='Part No')
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    plant_id = fields.Many2one('pur.org.data', 'Plant')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
    del_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class ASNJITRule(models.Model):
    _name = "asn.jitrule"

    plant_code = fields.Char("Plant Code",index=True)
    buyer_erp_id = fields.Char("Buyer Erp Id",index=True)
    vendor_code = fields.Char("Vendor Code",index=True)
    pulling_type = fields.Char("Pulling Type")
    part_no = fields.Char("Part No",index=True)
    rule_type = fields.Char("Rule Type")

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No')
    vendor_id = fields.Many2one('iac.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    plant_id = fields.Many2one('pur.org.data', 'Plant')
    buyer_id = fields.Many2one('buyer.code', 'Buyer Info')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)