# -*- coding: utf-8 -*-
import random
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import traceback
import traceback, logging, types
import utility

_logger = logging.getLogger(__name__)

class IacSpotVendor(models.Model):
    """
    现货商表单，签核通过后生成iac.vendor.register和iac.vendor
    """
    _name = "iac.spot.vendor"
    _description = "Spot Vendor"
    _rec_name = 'name1_cn'

    _sql_constraints = [
        ('short_name_unique',
         'UNIQUE(short_name)',
         "Supplier Short Name不能重复！ / Duplicate Short Name!")
    ]

    user_id = fields.Many2one('res.users', string="Vendor User")
    plant = fields.Many2one('pur.org.data', string="Plant *", required=True)

    vendor_code = fields.Char(string="Vendor Code", readonly=True, size=10)
    buyer_email = fields.Char(string="Buyer Email *", required=True)
    buyer_id = fields.Many2one('res.partner', compute='_compute_buyer_id')
    name1_cn = fields.Char(string="Company Name 1(Chinese)*", required=True, size=35)
    name2_cn = fields.Char(string="Company Name 2(Chinese)", size=35)
    name1_en = fields.Char(string="Company Name 1(English)*", required=True, size=35)
    name2_en = fields.Char(string="Company Name 2(English)", size=35)
    company_telephone1 = fields.Char(string="Company Tel. 1 *", required=True, size=16)
    company_telephone2 = fields.Char(string="Company Tel. 2", size=16)
    company_fax = fields.Char(string="Company Fax *", required=True, size=31)
    sales_person = fields.Char(string="Contact Person *", required=True, size=30)
    short_name = fields.Char(string="Supplier Short Name(Only English)*", required=True, size=10)
    sales_email = fields.Char(string="Contact email *", required=True)
    sales_telephone = fields.Char(string="Contact Office Tel. *", required=True, size=16)
    vendor_url = fields.Char(String="Vendor URL", size=132)
    vendor_account_group = fields.Char(string='Vendor Account Group', compute='_taken_vendor_account_group')
    vendor_title = fields.Char(String="Vendor Title", default="", readonly=True, size=15)

    bank_id = fields.Many2one('vendor.bank', string="Bank Info From SAP")
    partner_bank_type = fields.Char(string='Partner Bank Type')
    bank_name = fields.Char(string="Bank Name*", required=True, size=60)
    branch_name = fields.Char(string="Bank Branch Name*", required=True, size=40)
    account_number = fields.Char(string="Bank Account No.*", required=True, size=35)
    account_number_1 = fields.Char(String="Bank Account No First 16", compute='_taken_account_number_1', store=True)
    account_number_2 = fields.Char(String="Bank Account No Last", compute='_taken_account_number_2', store=True)
    swift_code = fields.Char(String="SWIFT Code", size=11)
    bank_street = fields.Char(string="Bank - Street*", required=True, size=35)
    bank_city = fields.Char(string="Bank - City*", required=True, size=35)
    bank_country = fields.Many2one('res.country', string="Bank - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    address_street = fields.Char(string="Address - Street *", required=True, size=35)
    address_city = fields.Char(string="Address - City *", required=True, size=35)
    address_district = fields.Char(string="Address - District *", required=True, size=35)
    address_pobox = fields.Char(string="Address - P.O. Box", size=35)
    address_postalcode = fields.Char(string="Address - Postal Code *", required=True, size=10)
    address_country = fields.Many2one('res.country', string="Address - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    vat_number = fields.Char(string="VAT Number(Taiwan area supplier only)")
    payment_term = fields.Many2one('payment.term', string='Payment Term*', required=True)
    incoterm = fields.Many2one('incoterm', string='Incoterm*', required=True)
    destination = fields.Char(string="Destination*", required=True, size=28)
    currency = fields.Many2one('res.currency', string="Currency *", required=True)
    local_foreign = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Local or Foreign *', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),# webflow拒绝或抽单
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")
    webflow_number = fields.Char(string="Webflow Number", readonly=True)

    @api.depends('buyer_email')
    def _compute_buyer_id(self):
        for vendor in self:
            if vendor.buyer_email:
                buyer = self.env['res.partner'].search([('active', '=', True), ('email', '=', vendor.buyer_email)], limit=1)
                vendor.buyer_id = buyer.id

    @api.depends('plant', 'local_foreign')
    def _taken_vendor_account_group(self):
        for v in self:
            for account_group in self.env['iac.vendor.account.group'].search([]):
                if account_group.vendor_type == 'spot' \
                        and account_group.plant_id.id == v.plant.id and account_group.local_foreign == v.local_foreign:
                    v.vendor_account_group = account_group.account_group

    @api.depends('account_number')
    def _taken_account_number_1(self):
        for v in self:
            # if v.account_number and v.len(v.account_number) >= 16:
            if v.account_number and v.bank_country.code == 'GB':
                v.account_number_1 = v.account_number[0:15]
            else:
                v.account_number_1 = v.account_number[0:16]

    @api.depends('account_number')
    def _taken_account_number_2(self):
        for v in self:
            # if v.account_number and len(v.account_number) >= 16:
            if v.account_number and v.bank_country.code == 'GB':
                v.account_number_2 = v.account_number[15:]
            else:
                v.account_number_2 = v.account_number[16:]

    @api.constrains('name1_en')
    def _check_name1_en(self):
        for record in self:
            if utility.contain_zh(record.name1_en):
                raise ValidationError(_(u'Company Name 1(English)不能包含中文！/ Chinese character is not allowed in Company Name 1(English)!'))

    @api.constrains('name2_en')
    def _check_name2_en(self):
        for record in self:
            if utility.contain_zh(record.name2_en):
                raise ValidationError(_(u'Company Name 2(English)不能包含中文！/ Chinese character is not allowed in Company Name 2(English)!'))

    @api.constrains('short_name')
    def _check_short_name(self):
        for record in self:
            if utility.contain_zh(record.short_name):
                raise ValidationError(_(u'Supplier Short Name(Only English)不能包含中文！/ Chinese character is not allowed in Supplier Short Name(Only English)!'))

    @api.constrains('company_telephone1')
    def _check_company_telephone1(self):
        for record in self:
            if not utility.is_phone(record.company_telephone1):
                raise ValidationError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))

    @api.constrains('company_telephone2')
    def _check_company_telephone2(self):
        for record in self:
            if record.company_telephone2 and not utility.is_phone(record.company_telephone2):
                raise ValidationError(_(u'Company Tel. 2 必须填写有效的电话号码！/ Company Tel. 2 is invalid!'))

    @api.constrains('company_fax')
    def _check_company_fax(self):
        for record in self:
            if not utility.is_phone(record.company_fax):
                raise ValidationError(_(u'Company Fax 必须填写有效的传真号码！/ Company Fax is invalid!'))

    @api.constrains('sales_telephone')
    def _check_sales_telephone(self):
        for record in self:
            if not utility.is_phone(record.sales_telephone):
                raise ValidationError(_(u'Contact Office Tel. 必须填写有效的电话号码！/ Contact Office Tel. is invalid!'))

    @api.constrains('sales_email')
    def _check_sales_email(self):
        for record in self:
            if not utility.is_email(record.sales_email):
                raise ValidationError(_(u'Contact Email 必须填写有效的Email！/ Contact Email is invalid!'))

    @api.constrains('address_country')
    def _check_address_country(self):
        for record in self:
            country = self.env['res.country'].browse(record.address_country.id)
            if country.code == 'TW' and not record.vat_number:
                raise ValidationError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))

    @api.model
    def default_get(self, fields):
        result = super(IacSpotVendor, self).default_get(fields)
        if not self.env.user.partner_id.email:
            raise UserError(_(u'当前用户Email为空。无法自动获取Buyer Email，请联系管理员检查用户资料！'))
        else:
            result['buyer_email'] = self.env.user.partner_id.email

        return result

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name1_cn']
            if record['vendor_code']:
                name = record['vendor_code'] + ' ' + name
            res.append((record['id'], name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name1_cn', operator, name), ('vendor_code', operator, name)]
        vendor = self.search(domain + args, limit=limit)
        return vendor.name_get()

    @api.onchange('plant')
    def _onchange_plant(self):
        if self.plant.plant_code == 'CP21':
            user_id = self.env['res.users'].search([('login', '=', 'SPOTIACP')])
            if not user_id:
                raise UserError(_(u'系统未设置SPOTIACP用户，请联系管理员检查用户资料！'))
            else:
                self.user_id = user_id.id
        elif self.plant.plant_code == 'CP22':
            user_id = self.env['res.users'].search([('login', '=', 'SPOTIACJ')])
            if not user_id:
                raise UserError(_(u'系统未设置SPOTIACJ用户，请联系管理员检查用户资料！'))
            else:
                self.user_id = user_id.id
        elif self.plant.plant_code == 'TP02':
            user_id = self.env['res.users'].search([('login', '=', 'SPOTIACT')])
            if not user_id:
                raise UserError(_(u'系统未设置SPOTIACT用户，请联系管理员检查用户资料！'))
            else:
                self.user_id = user_id.id

    @api.multi
    def button_to_approve(self):
        """
        Buyer 送签webflow
        """

        # buyer补充的资料校验
        if not self.plant:
            raise UserError(_(u'Plant不能为空！/ Plant is required!'))
        if not self.payment_term:
            raise UserError(_(u'Payment Term不能为空！/ Payment Term is required!'))
        if not self.incoterm:
            raise UserError(_(u'Incoterm不能为空！'))
        if not self.destination:
            raise UserError(_(u'Destination不能为空！/ Destination is required!'))
        if not self.local_foreign:
            raise UserError(_(u'Ship Destination不能为空！/ Ship Destination is required!'))
        if self.address_country.code != 'TW' and self.vat_number!=False:
            raise UserError(_(u'非台湾不能填写VAT Number！/ VAT Number is required for none Taiwanese Vendor!'))
        if self.address_country.code == 'TW' and not self.vat_number:
            raise UserError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))


        # 调用webflow接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F05_B", biz_object)

        if rpc_result:
            self.write({'state': 'to approve', 'state_msg': u'送签webflow成功', 'webflow_number': rpc_json_data.get('EFormNO')})
            message = u'送签成功'
        else:
            self.write({'state_msg': u'送签webflow失败', 'webflow_number': rpc_json_data.get('EFormNO')})
            message = u'送签失败'

        title = _("Warning for %s") % self.name1_cn
        warning = {
            'title': title,
            'message': message
        }

        return warning

    def vendor_spot_register_callback(self, context=None):
        """
        回调函数说明
        现货商注册审核完成
        模型为 iac.spot.vendor
        context={"approve_status": True,"data":{"id":1376,}}


        返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
        :param context:
        :return:
        """

        proc_result = False
        proc_ex = []
        try:
            # 校验接口入参
            if not context["approve_status"] or not context.get("data") or not context.get("data").get("id"):
                proc_result = False
                proc_ex.append(u"接口调用参数异常")
                _logger(u"接口调用参数异常")
                return proc_result, proc_ex
            else:
                if context["approve_status"] and context["rpc_callback_data"]["FormStatus"] == "C":
                    # 修改state
                    model_obj = self.browse(context.get("data").get("id"))
                    model_obj.write(
                        {'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 调用SAP接口
                    self.button_to_sap(context.get("data").get("id"))
                else:
                    model_obj = self.browse(context.get("data").get("id"))
                    model_obj.write({'state': 'unapproved', 'state_msg': u'webflow(%s)签核未通过' % context["rpc_callback_data"]["EFormNO"]})

            proc_result = True
            return proc_result, proc_ex
        except:
            ex_string = traceback.format_exc()
            proc_result = False
            proc_ex.append(ex_string)
            traceback.print_exc()
            return proc_result, proc_ex

    @api.multi
    def button_to_sap(self, object_id=None):
        if self.id:
            model_obj = self
        else:
            model_obj = self.browse(object_id)
        # 调用SAP接口
        biz_object = {
            "id": model_obj.id,
            "biz_object_id": model_obj.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_VENDOR_002_01", biz_object)
        if rpc_result:
            model_obj.write({'state': 'done', 'state_msg': u'通知SAP成功'})
            model_obj.vendor_code = rpc_json_data['vendor_code']

            # 创建现货商
            vendor_reg_vals = {
                'user_id': model_obj.user_id.id,
                'buyer_email': model_obj.buyer_email,
                'name1_cn': model_obj.name1_cn,
                'name2_cn': model_obj.name2_cn,
                'name1_en': model_obj.name1_en,
                'name2_en': model_obj.name2_en,
                'plant_id': model_obj.plant.id,
                'company_telephone1': model_obj.company_telephone1,
                'company_telephone2': model_obj.company_telephone2,
                'company_fax': model_obj.company_fax,
                'contact_person': model_obj.sales_person,
                'short_name': model_obj.short_name,
                'sales_email': model_obj.sales_email,
                'sales_telephone': model_obj.sales_telephone,
                'address_street': model_obj.address_street,
                'address_city': model_obj.address_city,
                'address_district': model_obj.address_district,
                'address_pobox': model_obj.address_pobox,
                'address_postalcode': model_obj.address_postalcode,
                'address_country': model_obj.address_country.id,
                'vat_number': model_obj.vat_number,
                'currency': model_obj.currency.id,
                'state': 'done',
                'other_emails': model_obj.buyer_email,
                'vendor_code': rpc_json_data['vendor_code'],
            }
            vendor_reg_id = self.env['iac.vendor.register'].sudo().create(vendor_reg_vals)

            vendor_vals = {
                'user_id': model_obj.user_id.id,
                'vendor_reg_id': vendor_reg_id.id,
                'name': model_obj.name1_cn,
                'plant': model_obj.plant.id,
                'vendor_code': rpc_json_data['vendor_code'],
                'buyer_email': model_obj.buyer_email,
                'payment_term': model_obj.payment_term.id,
                'incoterm': model_obj.incoterm.id,
                'destination': model_obj.destination,
                'currency': model_obj.currency.id,
                'local_foreign': model_obj.local_foreign,
                'bank_name': model_obj.bank_name,
                'branch_name': model_obj.branch_name,
                'account_number': model_obj.account_number,
                'swift_code': model_obj.swift_code,
                'bank_street': model_obj.bank_street,
                'bank_city': model_obj.bank_city,
                'bank_country': model_obj.bank_country.id,
                'vendor_type': 'spot',
                'vendor_url': model_obj.vendor_url,
                'vendor_account_group': model_obj.vendor_account_group,
                'vendor_title': model_obj.vendor_title,
                'bank_id': model_obj.bank_id,
                'partner_bank_type': model_obj.partner_bank_type,
                'state': 'done'
            }
            vendor_id = self.env['iac.vendor'].sudo().create(vendor_vals)
            vendor_reg_id.vendor_id = vendor_id.id

            try:
                # 给buyer发邮件
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_spot_sap_buyer_email')
            except:
                traceback.print_exc()
            return False
        else:
            model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})

class IacMoldVendor(models.Model):
    """
    磨具厂商表单，签核通过后生成iac.vendor.register和iac.vendor
    """
    _name = "iac.mold.vendor"
    _description = "Mold Vendor"
    _rec_name = 'name1_cn'

    plant = fields.Many2one('pur.org.data', string="Plant *", required=True)
    vendor_code = fields.Char(string="Vendor Code", readonly=True, size=10)
    buyer_email = fields.Char(string="Buyer Email *", required=True)
    buyer_id = fields.Many2one('res.partner', compute='_compute_buyer_id')
    name1_cn = fields.Char(string="Company Name 1(Chinese)*", required=True, size=35)
    name2_cn = fields.Char(string="Company Name 2(Chinese)", size=35)
    name1_en = fields.Char(string="Company Name 1(English)*", required=True, size=35)
    name2_en = fields.Char(string="Company Name 2(English)", size=35)
    company_telephone1 = fields.Char(string="Company Tel. 1 *", required=True, size=16)
    company_telephone2 = fields.Char(string="Company Tel. 2", size=16)
    company_fax = fields.Char(string="Company Fax *", required=True, size=31)
    sales_person = fields.Char(string="Contact Person *", required=True, size=30)
    short_name = fields.Char(string="Supplier Short Name(Only English)*", required=True, size=10)
    sales_email = fields.Char(string="Contact email *", required=True)
    sales_telephone = fields.Char(string="Contact Office Tel. *", required=True, size=16)
    vendor_url = fields.Char(String="Vendor URL", size=132)
    vendor_account_group = fields.Char(string='Vendor Account Group', compute='_taken_vendor_account_group')
    vendor_title = fields.Char(String="Vendor Title", default="", readonly=True, size=15)

    bank_id = fields.Many2one('vendor.bank', string="Bank Info From SAP")
    partner_bank_type = fields.Char(string='Partner Bank Type')
    bank_name = fields.Char(string="Bank Name*", required=True, size=60)
    branch_name = fields.Char(string="Bank Branch Name*", required=True, size=40)
    account_number = fields.Char(string="Bank Account No.*", required=True, size=35)
    account_number_1 = fields.Char(String="Bank Account No First 16", compute='_taken_account_number_1', store=True)
    account_number_2 = fields.Char(String="Bank Account No Last", compute='_taken_account_number_2', store=True)
    swift_code = fields.Char(String="SWIFT Code", size=11)
    bank_street = fields.Char(string="Bank - Street*", required=True, size=35)
    bank_city = fields.Char(string="Bank - City*", required=True, size=35)
    bank_country = fields.Many2one('res.country', string="Bank - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    address_street = fields.Char(string="Address - Street *", required=True, size=35)
    address_city = fields.Char(string="Address - City *", required=True, size=35)
    address_district = fields.Char(string="Address - District *", required=True, size=35)
    address_pobox = fields.Char(string="Address - P.O. Box", size=35)
    address_postalcode = fields.Char(string="Address - Postal Code *", required=True, size=10)
    address_country = fields.Many2one('res.country', string="Address - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    vat_number = fields.Char(string="VAT Number(Taiwan area supplier only)")
    payment_term = fields.Many2one('payment.term', string='Payment Term*', required=True)
    incoterm = fields.Many2one('incoterm', string='Incoterm*', required=True)
    destination = fields.Char(string="Destination*", required=True, size=28)
    currency = fields.Many2one('res.currency', string="Currency *", required=True)
    local_foreign = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Local or Foreign *', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")

    @api.depends('buyer_email')
    def _compute_buyer_id(self):
        for vendor in self:
            if vendor.buyer_email:
                buyer = self.env['res.partner'].search([('active', '=', True), ('email', '=', vendor.buyer_email)], limit=1)
                vendor.buyer_id = buyer.id

    @api.depends('plant')
    def _taken_vendor_account_group(self):
        for v in self:
            for account_group in self.env['iac.vendor.account.group'].search([]):
                if account_group.vendor_type == 'mold' and account_group.plant_id.id == v.plant.id:
                    v.vendor_account_group = account_group.account_group

    @api.depends('account_number')
    def _taken_account_number_1(self):
        for v in self:
            if v.account_number and len(v.account_number) >= 16:
                v.account_number_1 = v.account_number[0:16]
            else:
                v.account_number_1 = v.account_number

    @api.depends('account_number')
    def _taken_account_number_2(self):
        for v in self:
            if v.account_number and len(v.account_number) >= 16:
                v.account_number_2 = v.account_number[16:]
            else:
                v.account_number_2 = ''

    @api.constrains('name1_en')
    def _check_name1_en(self):
        for record in self:
            if utility.contain_zh(record.name1_en):
                raise ValidationError(_(u'Company Name 1(English)不能包含中文！/ Chinese character is not allowed in Company Name 1(English)!'))

    @api.constrains('name2_en')
    def _check_name2_en(self):
        for record in self:
            if utility.contain_zh(record.name2_en):
                raise ValidationError(_(u'Company Name 2(English)不能包含中文！/ Chinese character is not allowed in Company Name 2(English)!'))

    @api.constrains('short_name')
    def _check_short_name(self):
        for record in self:
            if utility.contain_zh(record.short_name):
                raise ValidationError(_(u'Supplier Short Name(Only English)不能包含中文！/ Chinese character is not allowed in Supplier Short Name(Only English)!'))

    @api.constrains('company_telephone1')
    def _check_company_telephone1(self):
        for record in self:
            if not utility.is_phone(record.company_telephone1):
                raise ValidationError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))

    @api.constrains('company_telephone2')
    def _check_company_telephone2(self):
        for record in self:
            if record.company_telephone2 and not utility.is_phone(record.company_telephone2):
                raise ValidationError(_(u'Company Tel. 2 必须填写有效的电话号码！/ Company Tel. 2 is invalid!'))

    @api.constrains('company_fax')
    def _check_company_fax(self):
        for record in self:
            if not utility.is_phone(record.company_fax):
                raise ValidationError(_(u'Company Fax 必须填写有效的传真号码！/ Company Fax is invalid!'))

    @api.constrains('sales_telephone')
    def _check_sales_telephone(self):
        for record in self:
            if not utility.is_phone(record.sales_telephone):
                raise ValidationError(_(u'Contact Office Tel. 必须填写有效的电话号码！/ Contact Office Tel. is invalid!'))

    @api.constrains('sales_email')
    def _check_sales_email(self):
        for record in self:
            if not utility.is_email(record.sales_email):
                raise ValidationError(_(u'Contact Email 必须填写有效的Email！/ Contact Email is invalid!'))

    @api.constrains('address_country')
    def _check_address_country(self):
        for record in self:
            country = self.env['res.country'].browse(record.address_country.id)
            if country.code == 'TW' and not record.vat_number:
                raise ValidationError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor！'))

            if country.code != 'TW' and record.vat_number!=False:
                raise UserError(_(u'非台湾不能填写VAT Number！/ VAT Number is required for none Taiwanese Vendor!'))



    @api.model
    def default_get(self, fields):
        result = super(IacMoldVendor, self).default_get(fields)
        if not self.env.user.partner_id.email:
            raise UserError(_(u'当前用户Email为空。无法自动获取Buyer Email，请联系管理员检查用户资料！'))
        else:
            result['buyer_email'] = self.env.user.partner_id.email

        return result

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name1_cn']
            if record['vendor_code']:
                name = record['vendor_code'] + ' ' + name
            res.append((record['id'], name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name1_cn', operator, name), ('vendor_code', operator, name)]
        vendor = self.search(domain + args, limit=limit)
        return vendor.name_get()

    @api.multi
    def button_to_sap(self):
        # 调用SAP接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_VENDOR_002", biz_object)
        if rpc_result:
            self.write({'state': 'done', 'state_msg': u'通知SAP成功'})
            self.vendor_code = rpc_json_data['vendor_code']

            # 创建模具厂商
            vendor_reg_vals = {
                'buyer_email': self.buyer_email.lower(),
                'name1_cn': self.name1_cn,
                'name2_cn': self.name2_cn,
                'name1_en': self.name1_en,
                'name2_en': self.name2_en,
                'company_telephone1': self.company_telephone1,
                'company_telephone2': self.company_telephone2,
                'company_fax': self.company_fax,
                'contact_person': self.sales_person,
                'short_name': self.short_name,
                'sales_email': self.sales_email,
                'sales_telephone': self.sales_telephone,
                'address_street': self.address_street,
                'address_city': self.address_city,
                'address_district': self.address_district,
                'address_pobox': self.address_pobox,
                'address_postalcode': self.address_postalcode,
                'address_country': self.address_country.id,
                'vat_number': self.vat_number,
                'currency': self.currency.id,
                'state': 'done',
                'other_emails': self.buyer_email.lower(),
                'vendor_code': rpc_json_data['vendor_code'],
            }
            vendor_reg_id = self.env['iac.vendor.register'].sudo().create(vendor_reg_vals)

            vendor_vals = {
                'vendor_reg_id': vendor_reg_id.id,
                'plant': self.plant.id,
                'vendor_code': rpc_json_data['vendor_code'],
                'name': self.name1_cn,
                'buyer_email': self.buyer_email.lower(),
                'payment_term': self.payment_term.id,
                'incoterm': self.incoterm.id,
                'destination': self.destination,
                'currency': self.currency.id,
                'local_foreign': self.local_foreign,
                'bank_name': self.bank_name,
                'branch_name': self.branch_name,
                'account_number': self.account_number,
                'swift_code': self.swift_code,
                'bank_street': self.bank_street,
                'bank_city': self.bank_city,
                'bank_country': self.bank_country.id,
                'vendor_type': 'mold',
                'vendor_url': self.vendor_url,
                'vendor_account_group': self.vendor_account_group,
                'vendor_title': self.vendor_title,
                'bank_id': self.bank_id,
                'partner_bank_type': self.partner_bank_type,
                'state': 'done'
            }
            vendor_id = self.env['iac.vendor'].sudo().create(vendor_vals)
            vendor_reg_id.vendor_id = vendor_id.id

            try:
                # 给buyer发送邮件
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_mold_sap_buyer_email')
            except:
                traceback.print_exc()
                return False
        else:
            self.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})

class IacBVIVendor(models.Model):
    """
    BVI表单，签核通过后生成iac.vendor.register和iac.vendor
    """
    _name = "iac.bvi.vendor"
    _description = "BVI Vendor"
    _rec_name = 'name1_cn'

    _sql_constraints = [('vendor_code_unique', 'UNIQUE(vendor_code)', u"Vendor Code不能重复！/Duplicate Vendor Code!"), ]

    plant = fields.Many2one('pur.org.data', string="Plant *", required=True)
    vendor_code = fields.Char(string="Vendor Code*",  size=10)
    buyer_email = fields.Char(string="Buyer Email *", required=True)
    buyer_id = fields.Many2one('res.partner', compute='_compute_buyer_id')
    name1_cn = fields.Char(string="Company Name 1(Chinese)*", required=True, size=35)
    name2_cn = fields.Char(string="Company Name 2(Chinese)", size=35)
    name1_en = fields.Char(string="Company Name 1(English)*", required=True, size=35)
    name2_en = fields.Char(string="Company Name 2(English)", size=35)
    company_telephone1 = fields.Char(string="Company Tel. 1 *", required=True, size=16)
    company_telephone2 = fields.Char(string="Company Tel. 2", size=16)
    company_fax = fields.Char(string="Company Fax *", required=True, size=31)
    sales_person = fields.Char(string="Contact Person *", required=True, size=30)
    short_name = fields.Char(string="Supplier Short Name(Only English)*", required=True, size=10)
    sales_email = fields.Char(string="Contact email *", required=True)
    sales_telephone = fields.Char(string="Contact Office Tel. *", required=True, size=16)
    vendor_url = fields.Char(String="Vendor URL", size=132)
    vendor_account_group = fields.Char(string='Vendor Account Group', compute='_taken_vendor_account_group')
    vendor_title = fields.Char(String="Vendor Title", default="", readonly=True, size=15)

    bank_id = fields.Many2one('vendor.bank', string="Bank Info From SAP")
    partner_bank_type = fields.Char(string='Partner Bank Type', size=4)
    bank_name = fields.Char(string="Bank Name*", required=True, size=60)
    branch_name = fields.Char(string="Bank Branch Name*", required=True, size=40)
    account_number = fields.Char(string="Bank Account No.*", required=True, size=35)
    account_number_1 = fields.Char(String="Bank Account No First 16", compute='_taken_account_number_1', store=True)
    account_number_2 = fields.Char(String="Bank Account No Last", compute='_taken_account_number_2', store=True)
    swift_code = fields.Char(String="SWIFT Code", size=11)
    bank_street = fields.Char(string="Bank - Street*", required=True, size=35)
    bank_city = fields.Char(string="Bank - City*", required=True, size=35)
    bank_country = fields.Many2one('res.country', string="Bank - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    address_street = fields.Char(string="Address - Street *", required=True, size=35)
    address_city = fields.Char(string="Address - City *", required=True, size=35)
    address_district = fields.Char(string="Address - District *", required=True, size=35)
    address_pobox = fields.Char(string="Address - P.O. Box", size=35)
    address_postalcode = fields.Char(string="Address - Postal Code *", required=True, size=10)
    address_country = fields.Many2one('res.country', string="Address - Country Code *", required=True, domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    vat_number = fields.Char(string="VAT Number(Taiwan area supplier only)")
    payment_term = fields.Many2one('payment.term', string='Payment Term*', required=True)
    incoterm = fields.Many2one('incoterm', string='Incoterm*', required=True)
    destination = fields.Char(string="Destination*", required=True, size=28)
    currency = fields.Many2one('res.currency', string="Currency *", required=True)
    local_foreign = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Local or Foreign *')

    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")

    @api.depends('buyer_email')
    def _compute_buyer_id(self):
        for vendor in self:
            if vendor.buyer_email:
                buyer = self.env['res.partner'].search([('active', '=', True), ('email', '=', vendor.buyer_email)], limit=1)
                vendor.buyer_id = buyer.id

    @api.depends('plant')
    def _taken_vendor_account_group(self):
        for v in self:
            for account_group in self.env['iac.vendor.account.group'].search([]):
                if account_group.vendor_type == 'bvi':
                    v.vendor_account_group = account_group.account_group

    @api.depends('account_number')
    def _taken_account_number_1(self):
        for v in self:
            if v.account_number and len(v.account_number) >= 16:
                v.account_number_1 = v.account_number[0:16]
            else:
                v.account_number_1 = v.account_number

    @api.depends('account_number')
    def _taken_account_number_2(self):
        for v in self:
            if v.account_number and len(v.account_number) >= 16:
                v.account_number_2 = v.account_number[16:]
            else:
                v.account_number_2 = ''

    @api.constrains('name1_en')
    def _check_name1_en(self):
        for record in self:
            if utility.contain_zh(record.name1_en):
                raise ValidationError(_(u'Company Name 1(English)不能包含中文！/ Chinese character is not allowed in Company Name 1(English)!'))

    @api.constrains('name2_en')
    def _check_name2_en(self):
        for record in self:
            if utility.contain_zh(record.name2_en):
                raise ValidationError(_(u'Company Name 2(English)不能包含中文！/ Chinese character is not allowed in Company Name 2(English)!'))

    @api.constrains('short_name')
    def _check_short_name(self):
        for record in self:
            if utility.contain_zh(record.short_name):
                raise ValidationError(_(u'Supplier Short Name(Only English)不能包含中文！/ Chinese character is not allowed in Supplier Short Name(Only English)!'))

    @api.constrains('company_telephone1')
    def _check_company_telephone1(self):
        for record in self:
            if not utility.is_phone(record.company_telephone1):
                raise ValidationError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))

    @api.constrains('company_telephone2')
    def _check_company_telephone2(self):
        for record in self:
            if record.company_telephone2 and not utility.is_phone(record.company_telephone2):
                raise ValidationError(_(u'Company Tel. 2 必须填写有效的电话号码！/ Company Tel. 2 is invalid!'))

    @api.constrains('company_fax')
    def _check_company_fax(self):
        for record in self:
            if not utility.is_phone(record.company_fax):
                raise ValidationError(_(u'Company Fax 必须填写有效的传真号码！/ Company Fax is invalid!'))

    @api.constrains('sales_telephone')
    def _check_sales_telephone(self):
        for record in self:
            if not utility.is_phone(record.sales_telephone):
                raise ValidationError(_(u'Contact Office Tel. 必须填写有效的电话号码！/ Contact Office Tel. is invalid!'))

    @api.constrains('sales_email')
    def _check_sales_email(self):
        for record in self:
            if not utility.is_email(record.sales_email):
                raise ValidationError(_(u'Contact Email 必须填写有效的Email！/ Contact Email is invalid!'))

    @api.constrains('address_country')
    def _check_address_country(self):
        for record in self:
            country = self.env['res.country'].browse(record.address_country.id)
            if country.code == 'TW' and not record.vat_number:
                raise ValidationError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))

    @api.model
    def default_get(self, fields):
        result = super(IacBVIVendor, self).default_get(fields)
        if not self.env.user.partner_id.email:
            raise UserError(_(u'当前用户Email为空。无法自动获取Buyer Email，请联系管理员检查用户资料！'))
        else:
            result['buyer_email'] = self.env.user.partner_id.email

        return result

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name1_cn']
            if record['vendor_code']:
                name = record['vendor_code'] + ' ' + name
            res.append((record['id'], name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name1_cn', operator, name), ('vendor_code', operator, name)]
        vendor = self.search(domain + args, limit=limit)
        return vendor.name_get()

    @api.multi
    def button_to_sap(self):
        # 调用SAP接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_VENDOR_002_02", biz_object)
        if rpc_result:
            self.write({'state': 'done'})
            self.write({'state_msg': u'通知SAP成功'})

            # 创建BVI厂商
            vendor_reg_vals = {
                'vendor_code': self.vendor_code,
                'buyer_email': self.buyer_email.lower(),
                'name1_cn': self.name1_cn,
                'name2_cn': self.name2_cn,
                'name1_en': self.name1_en,
                'name2_en': self.name2_en,
                'company_telephone1': self.company_telephone1,
                'company_telephone2': self.company_telephone2,
                'company_fax': self.company_fax,
                'contact_person': self.sales_person,
                'short_name': self.short_name,
                'sales_email': self.sales_email,
                'sales_telephone': self.sales_telephone,
                'address_street': self.address_street,
                'address_city': self.address_city,
                'address_district': self.address_district,
                'address_pobox': self.address_pobox,
                'address_postalcode': self.address_postalcode,
                'address_country': self.address_country.id,
                'vat_number': self.vat_number,
                'currency': self.currency.id,
                'state': 'done',
                'other_emails': self.buyer_email.lower()
            }
            vendor_reg = self.env['iac.vendor.register'].sudo().create(vendor_reg_vals)

            vendor_vals = {
                'vendor_reg_id': vendor_reg.id,
                'plant': self.plant.id,
                'vendor_code': self.vendor_code,
                'name': self.name1_cn,
                'buyer_email': self.buyer_email.lower(),
                'payment_term': self.payment_term.id,
                'incoterm': self.incoterm.id,
                'destination': self.destination,
                'currency': self.currency.id,
                'local_foreign': self.local_foreign,
                'bank_name': self.bank_name,
                'branch_name': self.branch_name,
                'account_number': self.account_number,
                'swift_code': self.swift_code,
                'bank_street': self.bank_street,
                'bank_city': self.bank_city,
                'bank_country': self.bank_country.id,
                'vendor_type': 'bvi',
                'vendor_url': self.vendor_url,
                'vendor_account_group': self.vendor_account_group,
                'vendor_title': self.vendor_title,
                'bank_id': self.bank_id,
                'partner_bank_type': self.partner_bank_type,
                'state': 'done'
            }
            self.env['iac.vendor'].sudo().create(vendor_vals)

            try:
                # 给buyer发送邮件
                utility.send_to_email(self,self.id, 'oscg_vendor.vendor_bvi_sap_buyer_email')
            except:
                traceback.print_exc()
                return False
        else:
            self.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})

    @api.model
    def create(self,vals):
        if "vendor_code" in vals:
            vendor_rec=self.env["iac.vendor"].search([('vendor_code','=',vals["vendor_code"])],limit=1)
            if vendor_rec.exists():
                raise UserError('Vendor code %s has existed in vendor data')
            result=super(IacBVIVendor,self).create(vals)
            result._validate_record()
            return result
        else:
            result=super(IacBVIVendor,self).create(vals)
            result._validate_record()
            return result

    @api.multi
    def write(self,vals):
        result=super(IacBVIVendor,self).write(vals)

        #校验存储的数据
        for bvi_vendor in self:
            bvi_vendor._validate_record()
        return result

    def _validate_record(self):
        """
        进行数据校验，调用对象为记录对象
        :return:
        """
        #if self.name1_cn[0:3]!='BVI':
        #    raise UserError(u"Company Name 1(Chinese) must start with 'BVI'")
        #if self.name2_cn[0:3]!='BVI':
        #    raise UserError(u"Company Name 2(Chinese) must start with 'BVI'")
        #if self.name1_en[0:3]!='BVI':
        #    raise UserError(u"Company Name 1(English) must start with 'BVI'")
        #if self.name2_en[0:3]!='BVI':
        #    raise UserError(u"Company Name 2(English) must start with 'BVI'")
        #if self.vendor_code[0:3]!='BVI':
        #    raise UserError(u"BVI Vendor Code must start with 'BVI'")

        if self.address_country.code != 'TW' and self.vat_number!=False:
            raise UserError(_(u'非台湾不能填写VAT Number！/ VAT Number is required for none Taiwanese Vendor!'))
        if self.address_country.code == 'TW' and not self.vat_number:
            raise UserError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))

        domain=[('id','<>',self.id),'|','|','|',('name1_cn','=',self.name1_cn),('name2_cn','=',self.name2_cn),('name1_en','=',self.name1_en),('name2_en','=',self.name2_en)]
        bvi_vendor_rec=self.env["iac.bvi.vendor"].search(domain,limit=1)
        if bvi_vendor_rec.exists():
            raise UserError(u"Duplicated Company Name")
        #校验vendor_code
        domain=[('vendor_code','=',self.vendor_code),('id','<>',self.id)]
        bvi_vendor_rec=self.env["iac.bvi.vendor"].search(domain,limit=1)
        if bvi_vendor_rec.exists():
            raise UserError(u"Duplicated Vendor Code")

