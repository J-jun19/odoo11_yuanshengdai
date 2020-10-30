# -*- coding: utf-8 -*-

from odoo import models, fields, api
"""
当前模型已经废弃
"""
class POHeader(models.Model):
    _name = "po.header"

    document_erp_id = fields.Char(string="Document Erp Id")
    company_code = fields.Char(string="Company Code")
    document_category = fields.Char(string="Document Category")
    deletion_flag = fields.Char(string="Deletion Flag")
    status = fields.Char(string="Status")
    document_date = fields.Date(string="Document Date")
    created_by = fields.Char(string="Created By")
    vendor_code = fields.Char(string="Vendor Code")
    language_key = fields.Char(string="Language Key")
    payment_term = fields.Char(string="Payment Term")
    purchase_org = fields.Char(string="Purchase Org")
    buyer_erp_id = fields.Char(string="Buyer Erp Id")
    currency = fields.Char(string="Currency")
    exchange_rate = fields.Char(string="Exchange Rate")
    contact_person = fields.Char(string="Contact Person")
    contact_phone = fields.Char(string="Contact Phone")
    incoterm = fields.Char(string="Incoterm")
    incoterm1 = fields.Char(string="Incoterm1")
    document_release_status = fields.Char(string="Document Release Status")
    order_type = fields.Char(string="Order Type")
    address_id = fields.Char(string="Address Id")
    your_reference = fields.Char(string="Your Reference")
    our_reference = fields.Char(string="Our Reference")
    manually_po_reason = fields.Char(string="Manually Po Reason")
    manually_po_reason_type = fields.Char(string="Manually Po Reason Type")
    manually_po_comment = fields.Char(string="Manually Po Comment")
    manually_po_comment2 = fields.Char(string="Manually Po Comment2")

    #lwt add relation fields
    payment_term_id=fields.Many2one('payment.term',string="Payment Term")
    company_id=fields.Many2one('company',string="Company Info")
    purchase_org_id = fields.Many2one('pur.org.data',string="Purchase Org")
    incoterm_id=fields.Many2one('incoterm',string="Incoterm")
    address_odoo_id=fields.Many2one('address',string="Address Id")
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    sap_log_id = fields.Char(string="Sap log Info")
    sap_temp_id = fields.Integer(string="Sap Temp Info")

"""
当前模型已经废弃
"""
class POPartner(models.Model):
    _name = "po.partner"

    document_erp_id = fields.Char(string="Document Erp Id")
    document_line_erp_id  = fields.Char(string="Document Line Erp Id")
    purchase_org  = fields.Char(string="Purchase Org")
    partner_function  = fields.Char(string="Partner Function")
    creation_date = fields.Date(string="Creation Date")
    reference_vendor_code = fields.Char(string="Reference Vendor Code")

    #lwt add relation fields
    purchase_org_id = fields.Many2one('pur.org.data',string="Purchase Org")
    sap_log_id = fields.Char(string="Sap log Info")
    sap_temp_id = fields.Integer(string="Sap Temp Info")

"""
当前模型已经废弃
"""
class PODetail(models.Model):
    _name = "po.detail"

    document_erp_id = fields.Char(string="Document Erp Id")
    document_line_erp_id = fields.Char(string="Document Line Erp Id")
    deletion_flag = fields.Char(string="Deletion Flag")
    quantity = fields.Float(string="Quantity",precision=(18,4))
    rfq_status = fields.Char(string="Rfq Status")
    change_date = fields.Char(string="Change Date")
    short_text = fields.Char(string="Short Text")
    part_no = fields.Char(string="Part No")
    part_no1 = fields.Char(string="Part No1")
    plant_code = fields.Char(string="Plant Code")
    manufacturer_part_no = fields.Char(string="Manufacturer Part No")
    price = fields.Float(string="Price",precision=(18,4))
    storage_location = fields.Char(string="Storage Location")
    unit = fields.Char(string="Unit")
    tracking_number = fields.Char(string="Tracking Number")
    revision_level = fields.Char(string="Revision Level")
    vendor_part_no = fields.Char(string="Vendor Part No")
    purchase_req_no = fields.Char(string="Purchase Req No")
    purchase_req_item_no = fields.Char(string="Purchase Req Item No")
    rfq_no = fields.Char(string="Rfq No")
    tax_code = fields.Char(string="Tax Code")
    reject_flag = fields.Char(string="Reject Flag")
    price_determine_date = fields.Date(string="Price Determine Date")
    address_id = fields.Char(string="Address Id")
    vendor_to_be_supply = fields.Char(string="Vendor To Be Supply")
    delivery_complete = fields.Char(string="Delivery Complete")
    price_unit = fields.Float(string="Price Unit",precision=(18,4))

    #lwt add relation fields
    plant_id = fields.Many2one('vendor.plant', 'Plant')
    address_odoo_id = fields.Many2one('address', 'Address Id')
    part_id = fields.Many2one('material.master', 'Part No')
    sap_log_id = fields.Char(string="Sap log Info")
    sap_temp_id = fields.Integer(string="Sap Temp Info")