# -*- coding: utf-8 -*-
import random
from odoo import models, fields, api
from odoo.osv import expression

class SourceList(models.Model):
    _name = "source.list"
    _rec_name = 'part_no'

    part_no=fields.Char(string="Part No",index=True)
    plant_code=fields.Char(string="Plant Code",index=True)
    record_number=fields.Integer(string="Record Number")
    creation_date=fields.Date(string="Creation Date")
    created_by=fields.Char(string="Created By")
    valid_from=fields.Date(string="Valid From",index=True)
    valid_to=fields.Date(string="Valid To",index=True)
    vendor_code=fields.Char(string="Vendor Code",index=True)
    isfix_flag=fields.Char(string="Is Fix Flag")
    agree_number=fields.Char(string="Agree Number")
    agree_item=fields.Integer(string="Agree Item")
    fixed_outline=fields.Char(string="Fixed Outline")
    procured_plant=fields.Char(string="Procured Plant")
    issue_plant=fields.Char(string="Issue Plant")
    manufacturer_part_no=fields.Char(string="Manufacturer Part NO")
    block_flag=fields.Char(string="Block Flag")
    purchase_org=fields.Char(string="Purchase Org",index=True)
    po_category=fields.Char(string="PO Category")
    record_category=fields.Char(string="Record Category")
    mrp_indicator=fields.Char(string="MRP Indicator")
    unit_of_measure=fields.Char(string="Unit Of Measure")
    logical_system=fields.Char(string="Logical System")
    special_stock_indicator=fields.Char(string="Special Stock Indicator")

    #lwt add relation fields
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    purchase_org_id=fields.Many2one("vendor.plant",string="Purchase Org Info")
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    part_id = fields.Many2one('material.master', string="Part Info")
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
    del_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class SourceCode(models.Model):
    _name = "source.code"
    _rec_name = 'source_code'

    source_code = fields.Char(string="Source Code", required=True)
    description = fields.Char(string="Description")
    is_bind = fields.Boolean(string="Is Bind", default=False, readonly=True)

class InforecordHistory(models.Model):
    _name = "inforecord.history"

    condition_record=fields.Char(string="ConditionRecord",index=True)
    application=fields.Char(string="Application")
    vendor_code=fields.Char(string="Vendor Code",index=True)
    part_no=fields.Char(string="Part NO",index=True)
    purchase_org=fields.Char(string="Purchase Org",index=True)
    plant_code=fields.Char(string="Plant Code",index=True)
    creation_date=fields.Date(string="Creation Date")
    valid_from=fields.Date(string="Valid From",index=True)
    valid_to=fields.Date(string="Valid To",index=True)
    currency=fields.Char(string="Currency",index=True)
    price=fields.Float(string="Price",precision=(18,4))
    price_unit=fields.Float(string="PriceUnit",precision=(18,1))
    ltime=fields.Float(string="Ltime")
    mpq=fields.Float(string="MPQ")
    moq=fields.Float(string="MOQ")
    rw=fields.Char(string="RW")
    cw=fields.Char(string="CW")
    taxcode=fields.Char(string="Taxcode",index=True)
    price_control=fields.Char(string="PriceControl")

    #lwt add relation fields
    part_id = fields.Many2one('material.master', 'Part No',index=True)
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info",index=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    purchase_org_id=fields.Many2one("vendor.plant",string="Purchase Org Info")
    plant_id = fields.Many2one('pur.org.data', string="Plant Info",index=True)
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class Company(models.Model):
    _name = "company"
    _table="company"
    company_code =fields.Char(string="Company Code",index=True)
    company_name =fields.Char(string="Company Name")
    city =fields.Char(string="City")
    company_code1 =fields.Char(string="Company Code1")
    address_id =fields.Char(string="Address ID")

    #lwt add relation fields
    address_odoo_id=fields.Many2one('address','Address Info')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['company_name']
            if record['company_code']:
                name = record['company_code'] + ' ' + name
            res.append((record['id'], name))
        return res

"""
当前模型存储的是工厂信息,不是采购组织信息
"""
class PurOrgData(models.Model):
    _name = "pur.org.data"
    _rec_name = 'plant_code'

    _sql_constraints = [
        ('pur_org_data_plant_code_uniq', 'unique (plant_code)', "plant_code already exists !"),
    ]
    plant_code=fields.Char(string="Plant Code",index=True)
    plant_name_cn=fields.Char(string="Plant Name Cn")
    plant_name_en=fields.Char(string="Plant Name En")
    purchase_org=fields.Char(string="Purchase Org")
    plant_code1=fields.Char(string="Plant Code1")
    address_id=fields.Char(string="Address ID",index=True)

    #lwt add relation fields
    address_odoo_id=fields.Many2one('address','Address Info')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    site_chi_name = fields.Char(string='Site Chinese Name')
    site_eng_name = fields.Char(string='Site Englist Name')
    site_city = fields.Char(string='Site City')
    site_address = fields.Char(string='Site Address')
    site_state = fields.Char(string='Site State')
    site_zip = fields.Char(string='Site ZIP')
    site_country = fields.Char(string='Site Country')
    #废弃字段
    plant_id=fields.Many2one("vendor.plant",string="Plant Info")
    purchase_org_code=fields.Char(string="Purchase Code")
    purchase_org_id = fields.Many2one('pur.org.data',string="Purchase Org")

class MaterialGroup(models.Model):
    _name = "material.group"
    _rec_name = "material_group"

    material_group=fields.Char(string="Material Group",index=True)
    description=fields.Char(string="Description")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    @api.multi
    def name_get(self):
        return [(request.id, request.material_group) for request in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('material_group', operator, name), ('description', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

class BuyerCode(models.Model):
    _name = "buyer.code"
    _rec_name = 'buyer_erp_id'

    plant_id = fields.Many2one('pur.org.data', string="Plant")
    buyer_erp_id=fields.Char(string="buyer SAP ID",index=True)
    buyer_name=fields.Char(string="Buyer Name")
    buyer_ad_account=fields.Char(string="Buyer Login Account")
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    name_cn = fields.Char(string="Buyer Chinese Name")
    department = fields.Char(string="Department")
    is_bind = fields.Boolean(string="Is Bind", default=False, readonly=True)

	
	# Ning add begin
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record['buyer_name']:
                name = record['buyer_name']
            else:
                name = ''
            if record['buyer_erp_id']:
                name = record['buyer_erp_id'] + ' ' + name
            res.append((record['id'], name))
        return res
        # end
		
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('buyer_erp_id', operator, name), ('buyer_name', operator, name)]

        objects = self.search(domain + args, limit=limit)
        return objects.name_get()

class ShipInstruct(models.Model):
    _name = "ship.instruct"
    language_key=fields.Char(string="Language Key")
    ship_id=fields.Char(string="Ship ID",index=True)
    ship_description=fields.Char(string="Ship Description")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class PaymentTerm(models.Model):
    _name = "payment.term"
    _rec_name = "payment_term"

    language_key=fields.Char("Language Key")
    payment_term=fields.Char("Payment Term",index=True)
    payment_description=fields.Char("Payment Description")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

    @api.multi
    def name_get(self):
        return [(request.id, request.payment_term) for request in self]

class VendorGroup(models.Model):
    _name = "vendor.group"
    language_key=fields.Char(string="Language Key")
    vendor_account_group=fields.Char(string="Vendor Account Group",index=True)
    account_group_name=fields.Char(string="Account Group Name")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

class IncoTerm(models.Model):
    _name = "incoterm"
    _rec_name = "incoterm"

    language_key=fields.Char(string="Language Key")
    incoterm=fields.Char(string="Incoterm",index=True)
    incoterm_description=fields.Char(string="Incoterm Description")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)
    @api.multi
    def name_get(self):
        return [(request.id, request.incoterm) for request in self]

class DivisionCode(models.Model):
    _name = "division.code"
    _rec_name = "division"
	# Ning add
    _order = 'division'
    # end

    division=fields.Char(string="Division",index=True)
    division_description=fields.Char(string="Division Description")
    language_key=fields.Char(string="Language Key")

    #lwt add relation fields
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

	# Ning add begin
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record['division_description']:
                name = record['division_description']
            else:
                name = ''
            if record['division']:
                name = record['division'] + ' ' + name
            res.append((record['id'], name))
        return res
        # end
		
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('division', operator, name), ('division_description', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

class PaymentInfo(models.Model):
    _name = "payment.info"
    vendor_code=fields.Char(string="Vendor_Code",index=True)
    assignment=fields.Char(string="Assignment")
    document=fields.Char(string="Document")
    referenece=fields.Char(string="Referenece")
    text=fields.Char(string="Text")
    currency=fields.Char(string="Currency")
    b=fields.Char(string="B")
    amount=fields.Float(string="Amount")
    m=fields.Char(string="M")
    vendor_name=fields.Char(string="Vendor_Name")
    post_date = fields.Date(string="Post Date")
    clear_date = fields.Date(string="Clear Date")

    #lwt add relation fields
    vendor_id=fields.Many2one('iac.vendor.vendor',string='Vendor Info')
    vendor_reg_id=fields.Many2one('iac.vendor.register',string='Vendor Info')
    currency_id=fields.Many2one('res.currency',string='Currency Info')
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
    miss_flag = fields.Integer(string="Miss Flag",default=0,index=True)

class Vendor(models.Model):
    _name = "vendor"
    name1_cn=fields.Char(string="Name1 Cn")
    address_street=fields.Char(string="Address Street")
    address_city=fields.Char(string="Address City")
    address_district=fields.Char(string="Address District")
    address_region=fields.Char(string="Address Region")
    address_postalcode=fields.Char(string="Address Postalcode")
    address_pobox=fields.Char(string="Address Pobox")
    address_country=fields.Char(string="Address Country")
    company_telephone1=fields.Char(string="Company Telephone1")
    company_telephone2=fields.Char(string="Company Telephone2")
    company_fax=fields.Char(string="Company Fax")
    vendor_code=fields.Char(string="Vendor Code",index=True)
    po_box=fields.Char(string="Po Box")
    language_key=fields.Char(string="Language Key")
    address_id=fields.Char(string="Address Id")
    short_name=fields.Char(string="Short Name")
    purchase_block=fields.Char(string="Purchase Block")
    vat_number=fields.Char(string="Vat Number")
    payment_block=fields.Char(string="Payment Block")
    plant_code=fields.Char(string="Plant Code",index=True)
    vendor_account_group=fields.Char(string="Vendor Account Group",index=True)
    title=fields.Char(string="Title")
    name2_cn=fields.Char(string="Name2 Cn")
    name1_en=fields.Char(string="Name1 En")
    name2_en=fields.Char(string="Name2 En")
    po_box_city=fields.Char(string="Po Box City")
    deletion_flag=fields.Char(string="Deletion Flag")
    deletion_block=fields.Char(string="Deletion Block")
    vendor_url=fields.Char(string="Vendor Url")

    #lwt add relation fields
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    address_country_id=fields.Many2one('res.country',string="Address Country Info")
    address_odoo_id=fields.Many2one('address',string="Address Id")
    plant_id=fields.Many2one('pur.org.data',string="Plant Code")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

"""
当前模型实际上存储的不是工厂信息
而是采购组织信息,真实的工厂信息通过plant_code 关联 pur_org_data 表得到
"""
class VendorPlant(models.Model):
    _name = "vendor.plant"
    _rec_name = 'name'

    name = fields.Char(string="Name")
    vendor_code=fields.Char(string="Vendor Code",index=True)
    purchase_org=fields.Char(string="Purchase Org",index=True)
    creation_date=fields.Date(string="Creation Date")
    purchase_block=fields.Char(string="Purchase Block")
    deletion_flag=fields.Char(string="Deletion Flag")
    incoterm=fields.Char(string="Incoterm",index=True)
    incoterm1=fields.Char(string="Incoterm1")
    payment_term=fields.Char(string="Payment Term")
    buyer_erp_id=fields.Char(string="Buyer Erp Id",index=True)
    sales_person=fields.Char(string="Sales Person")
    ers=fields.Char(string="Ers")
    confirmation_control_key=fields.Char(string="Confirmation Control Key")
    currency=fields.Char(string="Currency")
    sales_telephone=fields.Char(string="Sales_Telephone")
    name=fields.Char(string="Name")

    vendor_purchase_code=fields.Char(string="Vendor Purchase Code",index=True)#vendor_code+purchase_org 的组合
    #lwt add relation fields
    incoterm_id=fields.Many2one('incoterm',string="Incoterm")
    payment_term_id=fields.Many2one('payment.term',string="Incoterm")
    purchase_org_id=fields.Many2one("pur.org.data",string="Purchase Org Info")
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['purchase_org']
            res.append((record['id'], name))
        return res

class VendorBank(models.Model):
    _name = "vendor.bank"
    bank_country_code=fields.Char(string="Bank Country Code",index=True)
    bank_key=fields.Char(string="Bank Key",index=True)
    vendor_code=fields.Char(string="Vendor Code",index=True)
    account_number=fields.Char(string="Account Number")
    bank_control_key=fields.Char(string="Bank Control Key")
    partner_bank_type=fields.Char(string="Partner Bank Type")
    special_bank_detail=fields.Char(string="Special Bank Detail")
    account_hold_number=fields.Char(string="Account Hold Number")
    creation_date=fields.Char(string="Creation Date")
    create_by=fields.Char(string="Create By")
    name=fields.Char(string="Name")
    bank_region=fields.Char(string="Bank Region")
    lanuage_key=fields.Char(string="Lanuage Key")
    bank_city=fields.Char(string="Bank City")
    swift_code=fields.Char(string="Swift Code")
    bank_group=fields.Char(string="Bank Group")
    post_account=fields.Char(string="Post Account")
    deletion_flag=fields.Char(string="Deletion Flag")
    bank_number=fields.Char(string="Bank Number")
    post_current_bank_number=fields.Char(string="Post Current Bank Number")
    address_id=fields.Char(string="Address Id")
    branch=fields.Char(string="Branch")

    #lwt add relation fields
    bank_country_id=fields.Many2one('res.country',string="Bank Country Info")
    address_odoo_id=fields.Many2one('address',string="Address Id")
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

class VendorCertified(models.Model):
    _name = "vendor.certified"
    vendor_code=fields.Char(string="Vendor Code",index=True)
    vendor_email=fields.Char(string="Vendor Email")
    supplier_type=fields.Char(string="Supplier Type")
    score_thisyear=fields.Float(string="Score This Year",precision=(11,2))
    class_thisyear=fields.Char(string="Class This Year")
    score_previous=fields.Float(string="Score Previous",precision=(11,2))
    class_previous=fields.Char(string="Class Previous")

    #lwt add relation fields
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Info")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Registration")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

class Address(models.Model):
    _name = "address"
    address_id=fields.Char(string="ADDRESS ID")
    nam1=fields.Char(string="NAM1")
    nam2=fields.Char(string="NAM2")
    city1=fields.Char(string="CITY1")
    city2=fields.Char(string="CITY2")
    post_code1=fields.Char(string="POST CODE1")
    post_code2=fields.Char(string="POST CODE2")
    po_box=fields.Char(string="PO_BOX")
    street=fields.Char(string="STREET")
    house_num1=fields.Char(string="HOUSE NUM1")
    country_code=fields.Char(string="COUNTRY CODE")
    language_key=fields.Char(string="LANGUAGE KEY")
    region=fields.Char(string="REGION")
    telphone=fields.Char(string="TELPHONE")
    fax=fields.Char(string="FAX")
    name3=fields.Char(string="NAME3")
    name4=fields.Char(string="NAME4")
    street2=fields.Char(string="STREET2")
    street3=fields.Char(string="STREET3")
    street4=fields.Char(string="STREET4")

    #lwt add relation fields
    country_id=fields.Many2one('res.country',string="COUNTRY CODE")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)

class StorageLocation(models.Model):
    _name = "storage.location"
    plant_code=fields.Char(string="Plant Code",index=True)
    storage_location=fields.Char(string="Storage Location")
    description=fields.Char(string="Description")

    #lwt add relation fields
    plant_id = fields.Many2one('pur.org.data', string="Plant Info")
    sap_log_id = fields.Char(string="Sap log Info",index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info",index=True)
    need_re_update = fields.Integer(string="Need Call Update Func",default=0,index=True)
    need_update_id = fields.Integer(string="Need Call Update Func Seq",default=0,index=True)
