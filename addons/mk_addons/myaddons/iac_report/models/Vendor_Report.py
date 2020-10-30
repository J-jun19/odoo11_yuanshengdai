# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class IacVendorReport(models.Model):
    _name = "iac.vendor.report"
    _inherit = ['iac.vendor']
    _description = "Vendor Report"
    _table = 'iac_vendor'

class IacVendorRegisterReport(models.Model):
    _name = "iac.vendor.register.report"
    _inherit = ['iac.vendor.register']
    _description = "Vendor Register Report"
    _table = 'iac_vendor_register'
#    _order = 'id desc'
    plant_id = fields.Many2one('pur.org.data', string="Plant *",domain=lambda self: [('id', 'in', self.env.user.plant_id_list
)])
    vendor_ref_id = fields.Many2one('iac.vendor.report', string="Vendor Code *", index="True")
    other_emails = fields.Char(String='Email Notice Recipients')
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", index=True)

    vendor_bank_city = fields.Char('Bank city', related='vendor_id.bank_city')
    vendor_bank_country = fields.Many2one('res.country', related='vendor_id.bank_country')
    vendor_bank_name = fields.Char('Bank name', related='vendor_id.bank_name')
    vendor_bank_street = fields.Char('Bank street', related='vendor_id.bank_street')
    vendor_branch_name = fields.Char('Branch name', related='vendor_id.branch_name')
    vendor_swift_code = fields.Char('Swift code', related='vendor_id.swift_code')
    vendor_transfer_number = fields.Char('Transfer number', related='vendor_id.transfer_number')
    vendor_state = fields.Selection('Status', related='vendor_id.state')
    vendor_state_msg = fields.Char('Status Message', related='vendor_id.state_msg')
    vendor_webflow_number = fields.Char('Webflow number', related='vendor_id.webflow_number')
    vendor_vendor_type = fields.Selection('Vendor type', related='vendor_id.vendor_type')
    vendor_creation_date = fields.Datetime('Creation  date', related='vendor_id.creation_date')
    vendor_order_currency = fields.Char('Order currency', related='vendor_id.order_currency')
    vendor_vendor_sap_status = fields.Char('Vendor sap status', related='vendor_id.vendor_sap_status')
# buyer approve bank info
    vendor_rma_terms = fields.Selection('RMA terms', related='vendor_id.rma_terms')
    vendor_it_level = fields.Selection('IT level', related='vendor_id.it_level')
    vendor_payment_term = fields.Many2one('payment.term', related='vendor_id.payment_term')
    vendor_incoterm = fields.Many2one('incoterm', related='vendor_id.incoterm')
    vendor_destination = fields.Char('Destination', related='vendor_id.destination')
    vendor_reason = fields.Text('Reason', related='vendor_id.reason')
    vendor_vmi_supplier = fields.Selection('VMI supplier', related='vendor_id.vmi_supplier')
    vendor_vmi_due = fields.Char('VMI due', related='vendor_id.vmi_due')
    vendor_si_supplier = fields.Selection('SI supplier', related='vendor_id.si_supplier')
    vendor_import_required = fields.Selection('Import ', related='vendor_id.import_required')
    vendor_local_foreign = fields.Selection('Local or foreign', related='vendor_id.local_foreign')
    vendor_purchase_contract = fields.Many2one('muk_dms.file', related='vendor_id.purchase_contract')
    vendor_probity_agreement = fields.Many2one('muk_dms.file', related='vendor_id.probity_agreement')

    account_number = fields.Char(related='vendor_id.account_number')

    @api.onchange('plant_id')
    def _onchange_plant_id(self):

        if self.plant_id:
            return {'domain': {'vendor_ref_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_ref_id': [('state', '=', 'done')]}}

    @api.onchange('vendor_ref_id')
    def _onchange_vendor_ref_id(self):

        if self.vendor_ref_id:
            rec = self.env["iac.vendor.register.report"].sudo().search([('vendor_id', '=', self.vendor_ref_id.id)], limit=1)
            if rec:
                self.user_id = rec.user_id
                self.name1_cn = rec.name1_cn
                self.name2_cn = rec.name2_cn
                self.name2_en = rec.name2_en
                self.mother_name_en = rec.mother_name_en
                self.mother_name_cn = rec.mother_name_cn
                self.mother_address_en = rec.mother_address_en
                self.mother_address_cn = rec.mother_address_cn
                self.capital = rec.capital
                self.employee_number = rec.employee_number
                self.conglomerate = rec.conglomerate
                self.shareholders = rec.shareholders
                self.company_telephone1 = rec.company_telephone1
                self.company_telephone2 = rec.company_telephone2
                self.company_fax = rec.company_fax
                self.duns_number = rec.duns_number
                self.iso_certificate = rec.iso_certificate
                self.state_msg = rec.state_msg
                self.webflow_number = rec.webflow_number
                self.buyer_email = rec.buyer_email
                self.web_site = rec.web_site
                self.license_number = rec.license_number
                self.vat_number = rec.vat_number
                self.short_name = rec.short_name
                self.contact_person = rec.contact_person
                self.sales_telephone = rec.sales_telephone
                self.sales_mobile = rec.sales_mobile
                self.sales_email = rec.sales_email
                self.address_street = rec.address_street
                self.address_city = rec.address_city
                self.address_district = rec.address_district
                self.address_pobox = rec.address_pobox
                self.address_country = rec.address_country
                self.address_postalcode = rec.address_postalcode
                self.currency = rec.currency
                self.factory_count = rec.factory_count
                self.supplier_type = rec.supplier_type
                self.supplier_category = rec.supplier_category
                self.other_emails = rec.other_emails
                self.reject_reason = rec.reject_reason
                self.product_ids = rec.product_ids
                self.factory_ids = rec.factory_ids
                self.reason_one = rec.reason_one
                self.material_use_range = rec.material_use_range
                self.corporation_description = rec.corporation_description
                self.supplier_description = rec.supplier_description
                self.use_project = rec.use_project
                self.project_status = rec.project_status
                self.apply_reason = rec.apply_reason
                self.applyfile_id = rec.applyfile_id
                self.apply_memo = rec.apply_memo
                self.is_scene = rec.is_scene
                self.is_outerbuy = rec.is_outerbuy
                self.delivery_hours = rec.delivery_hours
                self.comment = rec.comment
                self.material_ids = rec.material_ids
                self.vendor_id = rec.vendor_id
                self.account_number = rec.account_number
            else:
                self.user_id = False
                self.name1_cn = False
                self.name2_cn = False
                self.name2_en = False
                self.mother_name_en = False
                self.mother_name_cn = False
                self.mother_address_en = False
                self.mother_address_cn = False
                self.capital = False
                self.employee_number = False
                self.conglomerate = False
                self.shareholders = False
                self.company_telephone1 = False
                self.company_telephone2 = False
                self.company_fax = False
                self.duns_number = False
                self.iso_certificate = False
                self.state_msg = False
                self.webflow_number = False
                self.buyer_email = False
                self.web_site = False
                self.license_number = False
                self.vat_number = False
                self.short_name = False
                self.contact_person = False
                self.sales_telephone = False
                self.sales_mobile = False
                self.sales_email = False
                self.address_street = False
                self.address_city = False
                self.address_district = False
                self.address_pobox = False
                self.address_country = False
                self.address_postalcode = False
                self.currency = False
                self.factory_count = False
                self.supplier_type = False
                self.supplier_category = False
                self.other_emails = False
                self.reject_reason = False
                self.product_ids = False
                self.factory_ids = False
                self.reason_one = False
                self.material_use_range = False
                self.corporation_description = False
                self.supplier_description = False
                self.use_project = False
                self.project_status = False
                self.apply_reason = False
                self.applyfile_id = False
                self.apply_memo = False
                self.is_scene = False
                self.is_outerbuy = False
                self.delivery_hours = False
                self.comment = False
                self.material_ids = False
                self.vendor_id = False
                self.account_number = False
                #raise UserError(u'No register data exist for this vendor')
    @api.model
    def create(self, vals):
        raise UserError("do not save_create!")
        return self

    @api.multi
    def write(self, vals):
        raise UserError("do not save_write!")
        return False