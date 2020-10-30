# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from datetime import datetime, timedelta
from odoo import fields
from odoo import tools
from odoo.http import request
from odoo import SUPERUSER_ID
import time
import traceback
import logging
import utility
conf_obj=tools.config
_logger = logging.getLogger(__name__)

class IacVendorRegister(models.Model):
    """
    Vendor基本资料
    """
    _name = "iac.vendor.register"
    _description = "Vendor Register"
    _rec_name = 'name1_cn'
    _order = 'id desc'

    name = fields.Char(string="Name", related="name1_cn", index=True)
    name1_cn = fields.Char(string="Company Name 1(Chinese)*", size=35, index=True)
    name2_cn = fields.Char(string="Company Name 2(Chinese)*", size=35)
    name1_en = fields.Char(string="Company Name 1(English)*", size=35)
    name2_en = fields.Char(string="Company Name 2(English)*", size=35)
    short_name = fields.Char(string="Supplier Short Name(Only English)*", size=10)
    mother_name_en = fields.Char(string="Mother Company Name(English)*")
    mother_name_cn = fields.Char(string="Mother Company Name(Chinese)*")
    mother_address_en = fields.Char(string="Mother Company Address(English)*")
    mother_address_cn = fields.Char(string="Mother Company Address(Chinese)*")
    capital = fields.Float(string="Capital(USD)")
    employee_number = fields.Char(string="Number of Employee*", size=7)
    conglomerate = fields.Char(string="Major Conglomerate")
    shareholders = fields.Char(string="Major Shareholders & Shares")
    company_telephone1 = fields.Char(string="Company Tel. 1 *", size=16)
    company_telephone2 = fields.Char(string="Company Tel. 2", size=16)
    company_fax = fields.Char(string="Company Fax *", size=31)
    iso_certificate = fields.Many2many('iac.attachment.type', string='ISO Certificate *',
                                       domain=[('sub_group', '=', 'iso')])
    buyer_email = fields.Char(string="Buyer email *", index=True)
    buyer_id = fields.Many2one('res.partner', compute='_compute_buyer_id')
    web_site = fields.Char(string="Company Web Site")
    license_number = fields.Char(string="Company License No. *")
    duns_number = fields.Char(string="DUNS Number", size=4)
    vat_number = fields.Char(string="VAT Number(Taiwan area supplier only)", size=20)
    contact_person = fields.Char(string="Contact Person *")
    sales_telephone = fields.Char(string="Contact Office Tel. *", size=16)
    sales_mobile = fields.Char(string="Contact Mobile Phone *")
    sales_email = fields.Char(string="Contact email *")
    address_street = fields.Char(string="Address - Street *", size=35)
    address_city = fields.Char(string="Address - City *", size=35)
    address_district = fields.Char(string="Address - District *", size=35)
    address_pobox = fields.Char(string="Address - P.O. Box", size=35)
    address_postalcode = fields.Char(string="Address - Postal Code *", size=10)
    address_country = fields.Many2one('res.country', string="Address - Country Code *", domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])
    currency = fields.Many2one('res.currency', string="Currency *")
    factory_count = fields.Integer(string="Factory Number")
    supplier_type = fields.Selection(
        string='Supplier Type *', selection='_selection_supplier_type')
    supplier_category = fields.Selection(
        string='Supplier Category *', selection='_selection_supplier_category')
    attachment_ids = fields.One2many("iac.vendor.register.attachment", "vendor_reg_id", string="Attachment Lines")
    product_ids = fields.One2many("iac.vendor.product", "vendor_reg_id", string="Product Lines")
    factory_ids = fields.One2many("iac.vendor.factory", "vendor_reg_id", string="Factory Lines")
    state = fields.Selection([
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('submit', 'Submit'),  # vendor编辑好提交buyer review
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),  # webflow拒绝或抽单
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'),  # 表单取消
        ('block', 'Block'),  # 锁定状态
        ('deleted', 'Deleted')  # 删除状态
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)
    webflow_number = fields.Char(string="Webflow Number", readonly=True)
    user_id = fields.Many2one('res.users', string="User", index=True)
    vendor_code = fields.Char(string="Vendor Code", readonly=True, index=True)
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor", index=True)

    # Buyer Approve New Registration
    reason_one = fields.Many2one('iac.vendor.reason', string='Vendor Apply Reason One')
    material_use_range = fields.Char(string='Material Use Range')
    corporation_description = fields.Char(string='Corporation Description')
    supplier_description = fields.Char(string='Supplier Description')

    # QS approve file
    material_ids = fields.One2many("iac.vendor.material", "vendor_reg_id", string="Material Lines *")

    # Buyer Select BU/BG and QM Leader
    use_project = fields.Char(string="Use Project *")
    project_status = fields.Char(string="Project Status")
    apply_reason = fields.Many2many('iac.vendor.reason', string='Vendor Apply Reason *')
    applyfile_id = fields.Many2one('muk_dms.file', string="Attachment File *")  # 客户指定时的佐证文件
    apply_memo = fields.Text(string="Apply Memo *")

    is_scene = fields.Selection([('Y', 'Yes'), ('N', 'No')], string="Suggest Local Approve *", default="Y")  # 是否建议现地评鉴
    is_outerbuy = fields.Selection([('Y', 'Yes'), ('N', 'No')], string="Is Foreign *", default="Y")  # 是否外购

    delivery_hours = fields.Float(string="Estimate Hours")  # 预估车程
    bu_leaders = fields.Many2many('res.partner', string='Select BU Leader to Notify *')
    qm_leaders = fields.Many2many('res.partner', string='Select QM Leader to Notify *')
    cm_roles = fields.Many2many('res.partner', string='Select CM Role to Send Mail *')
    comment = fields.Text(string="Comment")

    other_emails = fields.Text(string="Email Notice Recipients", required=True, help=u"请使用半角分号(;)分割email")
    reject_reason = fields.Text(string="Reject Reason")

    plant_id = fields.Many2one('pur.org.data', string="Plant *")

    def _valid_record(self):
        """
        校验数据正确性,新建或者更新记录后调用这个方法进行数据校验
        :return:
        """
        #if self.name1_en!=False and utility.contain_zh(self.name1_en):
        #    raise UserError(_(u'Company Name 1(English)不能包含中文！'))
        #if self.name2_en!=False and utility.contain_zh(self.name2_en):
        #    raise UserError(_(u'Company Name 2(English)不能包含中文！'))
        #if self.short_name!=False and utility.contain_zh(self.short_name):
        #    raise UserError(_(u'Supplier Short Name(Only English)不能包含中文！'))
        #if self.mother_name_en!= False and utility.contain_zh(self.mother_name_en):
        #    raise UserError(_(u'Mother Company Name(English)不能包含中文！'))
        #if self.mother_address_en!=False and utility.contain_zh(self.mother_address_en):
        #    raise UserError(_(u'Mother Company Address(English)不能包含中文！'))
        if self.company_telephone1!=False and not utility.is_phone(self.company_telephone1):
            raise UserError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))
        if self.company_telephone2!= False and not utility.is_phone(self.company_telephone2):
            raise UserError(_(u'Company Tel. 2 必须填写有效的电话号码！/ Company Tel. 2 is invalid!'))
        if self.company_fax!=False and not utility.is_phone(self.company_fax):
            raise UserError(_(u'Company Fax 必须填写有效的传真号码！/ Company Fax is invalid!'))
        if self.sales_telephone!= False and not utility.is_phone(self.sales_telephone):
            raise UserError(_(u'Contact Office Tel. 必须填写有效的电话号码！/ Contact Office Tel. is invalid!'))
        if self.sales_mobile!= False and not utility.is_phone(self.sales_mobile):
            raise UserError(_(u'Contact Mobile Phone 必须填写有效的电话号码！/ Contact Mobile Phone is invalid!'))
        if self.sales_email!= False and not utility.is_email(self.sales_email):
            raise UserError(_(u'Contact Email 必须填写有效的Email！/ Contact Email is invalid!'))

        if self.address_country!= False:
            country = self.env['res.country'].browse(self.address_country)
            if self.vat_number==False and self.address_country.code=='TW':
                raise UserError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))
            if self.address_country.code != 'TW' and self.vat_number!=False:
                raise UserError(_(u'非台湾不能填写VAT Number！/ VAT Number is required for none Taiwanese Vendor!'))


        if "no_check_short_name" not in  self._context and self.short_name!=False:
            vendor_register = self.env['iac.vendor.register'].search([('state', '!=', 'cancel'), ('short_name', '=', self.short_name),('id','!=',self.id)], limit=1)
            if vendor_register.exists():
                raise UserError(_(u'Supplier Short Name已经存在，请修改！/ Supplier Short Name exists!'))

    @api.model
    def create(self,values):
        if "buyer_email" in values:
            buyer_email=values["buyer_email"]
            values["buyer_email"]=buyer_email.lower()
        result=super(IacVendorRegister,self).create(values)
        if not conf_obj.get('import_data_mode'):
            result._valid_record()
        return result

    @api.multi
    def write(self, values):
        #conf_obj
        #if not tools.config.get('import_data_mode'):
        #    self._valid_record()

            #校验功能已经转移到_valid_record()方法中,暂时保留老版本
            #if values.get('name1_en', False) and utility.contain_zh(values['name1_en']):
            #    raise UserError(_(u'Company Name 1(English)不能包含中文！'))
            #if values.get('name2_en', False) and utility.contain_zh(values['name2_en']):
            #    raise UserError(_(u'Company Name 2(English)不能包含中文！'))
            #if values.get('short_name', False) and utility.contain_zh(values['short_name']):
            #    raise UserError(_(u'Supplier Short Name(Only English)不能包含中文！'))
            #if values.get('mother_name_en', False) and utility.contain_zh(values['mother_name_en']):
            #    raise UserError(_(u'Mother Company Name(English)不能包含中文！'))
            #if values.get('mother_address_en', False) and utility.contain_zh(values['mother_address_en']):
            #    raise UserError(_(u'Mother Company Address(English)不能包含中文！'))
            #if values.get('company_telephone1', False) and not utility.is_phone(values['company_telephone1']):
            #    raise UserError(_(u'Company Tel. 1 必须填写有效的电话号码！'))
            #if values.get('company_telephone2', False) and not utility.is_phone(values['company_telephone2']):
            #    raise UserError(_(u'Company Tel. 2 必须填写有效的电话号码！'))
            #if values.get('company_fax', False) and not utility.is_phone(values['company_fax']):
            #    raise UserError(_(u'Company Fax 必须填写有效的传真号码！'))
            #if values.get('sales_telephone', False) and not utility.is_phone(values['sales_telephone']):
            #    raise UserError(_(u'Contact Office Tel. 必须填写有效的电话号码！'))
            #if values.get('sales_mobile', False) and not utility.is_phone(values['sales_mobile']):
            #    raise UserError(_(u'Contact Mobile Phone 必须填写有效的电话号码！'))
            #if values.get('sales_email', False) and not utility.is_email(values['sales_email']):
            #    raise UserError(_(u'Contact Email 必须填写有效的Email！'))
#
            #if values.get('short_name', False):
            #    vendor_register = self.env['iac.vendor.register'].search([('state', '!=', 'cancel'), ('short_name', '=', values['short_name']),('id','!=',self.id)], limit=1)
            #    if vendor_register:
            #        raise UserError(_(u'Supplier Short Name已经存在，请修改！'))
            #if values.get('address_country', False):
            #    country = self.env['res.country'].browse(values['address_country'])
            #    vat_number = values.get('vat_number', False)
            #    if not vat_number:
            #        vat_number = self.vat_number
            #    if country.code == 'TW' and not vat_number:
            #        raise UserError(_(u'台湾必须填写VAT Number！'))
        if "buyer_email" in values:
            buyer_email=values["buyer_email"]
            values["buyer_email"]=buyer_email.lower()
        vendor = super(IacVendorRegister, self).write(values)
        if not conf_obj.get('import_data_mode'):
            self._valid_record()
        return vendor

    @api.multi
    def name_get(self):
        res = []
        for vendor in self:
            name = vendor.name1_cn
            if vendor.vendor_code:
                name = "%s (%s)" % (vendor.vendor_code, name)

            res += [(vendor.id, name)]
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain += ['|', ('vendor_code', operator, name), ('name1_cn', operator, name)]
        vendor = self.search(domain + args, limit=limit)
        return vendor.name_get()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # 根据角色过滤数据
        if self.env.user.id != SUPERUSER_ID:
            if self.env.user.has_group('oscg_vendor.IAC_vendor_groups'):
                if self.env.user.vendor_id:
                    args += [('vendor_id', '=', self.env.user.vendor_id.id)]
            elif self.env.user.has_group('oscg_vendor.IAC_buyer_groups'):
                args += [('buyer_email', '=', self.env.user.partner_id.email)]

        return super(IacVendorRegister, self).search(args, offset, limit, order, count=count)

    @api.model
    def _selection_supplier_type(self):
        res_type = []
        type_list = self.env['ir.config_parameter'].search([('key', 'like', 'supplier_type_')])
        for item in type_list:
            res_type.append((item.key[14:], _(item.value)))

        return res_type

    @api.model
    def _selection_supplier_category(self):
        res_category = []
        category_list = self.env['ir.config_parameter'].search([('key', 'like', 'supplier_category_')])
        for item in category_list:
            res_category.append((item.key[18:], _(item.value)))

        return res_category

    @api.depends('buyer_email')
    def _compute_buyer_id(self):
        for vendor in self:
            if vendor.buyer_email:
                buyer = self.env['res.partner'].search([('active', '=', True), ('email', '=', vendor.buyer_email)], limit=1)
                vendor.buyer_id = buyer.id

    @api.multi
    def button_registe(self):
        """
        vendor提交MM审核，用户输入校验
        """
        # 必填项校验
        if not self.name1_cn:
            raise UserError(_(u'Company Name 1(Chinese)不能为空！/ Company Name 1(Chinese) is required!'))
        if not self.name1_en:
            raise UserError(_(u'Company Name 1(English)不能为空！/ Company Name 1(English) is required!'))
        if not self.short_name:
            raise UserError(_(u'Supplier Short Name(Only English)不能为空！/ Supplier Short Name(Only English) is required!'))
        if not self.mother_name_en:
            raise UserError(_(u'Mother Company Name(English)不能为空！/ Mother Company Name(English) is required!'))
        if not self.mother_name_cn:
            raise UserError(_(u'Mother Company Name(Chinese)不能为空！/ Mother Company Name(Chinese) is required!'))
        if not self.mother_address_en:
            raise UserError(_(u'Mother Company Address(English)不能为空！/ Mother Company Address(English) is required!'))
        if not self.mother_address_cn:
            raise UserError(_(u'Mother Company Address(Chinese)不能为空！/ Mother Company Address(Chinese) is required!'))
        if not utility.is_digital(self.employee_number):
            raise UserError(_(u'Number of Employee不能为空且必须填写正整数！/ Number of Employee is required and has to be positive integer.'))
        if not utility.is_phone(self.company_telephone1):
            raise UserError(_(u'Company Tel. 1 不能为空且必须填写有效的电话号码！/ Company Tel. 1 is required and has to be valid!'))
        if not self.company_fax:
            raise UserError(_(u'Company Fax不能为空！/ Company Fax is required!'))
        if not self.iso_certificate:
            raise UserError(_(u'ISO Certificate不能为空！/ ISO Certificate is required!'))
        if not utility.is_email(self.buyer_email):
            raise UserError(_(u'Buyer email不能为空且必须是有效的email！'))
        # 校验buyer email
        buyer_flag = False
        for user in self.env.ref('oscg_vendor.IAC_buyer_groups').users:
            if self.buyer_email == user.email:
                buyer_flag = True
        if not buyer_flag:
            raise UserError(_(u"Buyer Email不存在，请核实后重新输入！"))
        if not self.license_number:
            raise UserError(_(u'Company License No.不能为空！/ Company License No. is required!'))
        if not self.contact_person:
            raise UserError(_(u'Contact Person不能为空！/ Contact Person is required!'))
        if not self.sales_telephone:
            raise UserError(_(u'Sales Office Tel.不能为空！/ Sales Office Tel. is required!'))
        if not self.sales_mobile:
            raise UserError(_(u'Contact Mobile Phone 不能为空！/ Contact Mobile Phone is required!'))
        if not utility.is_email(self.sales_email):
            raise UserError(_(u'Contact email不能为空且必须是有效的email！/ Contact email is required and has to be valid eamil address!'))
        if not self.address_street:
            raise UserError(_(u'Address - Street不能为空！/ Address-Street is required!'))
        if not self.address_city:
            raise UserError(_(u'Address - City不能为空！/ Address-City is required!'))
        if not self.address_district:
            raise UserError(_(u'Address - District不能为空！/ Address-District is required!'))
        if not self.address_postalcode:
            raise UserError(_(u'Address - Postal Code不能为空！/ Address-Postal Code is required!'))
        if not self.address_country:
            raise UserError(_(u'Address - Country Code不能为空！/ Address-Country Code is required!'))
        if not self.currency:
            raise UserError(_(u'Currency不能为空！/ Currency is required!'))
        if not self.supplier_type:
            raise UserError(_(u'Supplier Type不能为空！/ Supplier Type is required!'))
        if not self.supplier_category:
            raise UserError(_(u'Supplier Category不能为空！/ Supplier Category is required!'))
        if not self.product_ids:
            raise UserError(_(u'Product Lines不能为空！/ Product Lines are required!'))
        for product in self.product_ids:
            if not product.product_type or not product.product_class or not product.brand_name or not product.major_customer:
                raise UserError(_(u'Product Lines 明细项不能为空！/ Product Lines are required!'))
        for factory in self.factory_ids:
            if not factory.factory_type or not factory.factory_name:
                raise UserError(_(u'Factory Lines 明细项不能为空！/ Factory Lines is required!'))
        for attachment in self.attachment_ids:
            if not attachment.type:
                raise UserError(_(u'Attachment Lines 明细项不能为空！/ Attachment Lines are required!'))

        # 上传文档校验
        attachment_list = self.env['iac.attachment.config'].search([('model_obj', '=', 'vendor'), ('is_displayed', '=', True)])
        for attachment in attachment_list:
            if attachment.is_required:
                is_upload = False
                if self.attachment_ids:
                    for file in self.attachment_ids:
                        if file.type.name == attachment.type.name and file.file_id:
                            is_upload = True
                if not is_upload:
                    raise UserError(_(u'%s文件必须上传！') % (attachment.type.name))

        # 业务逻辑校验
        if self.address_country.code == 'CN' and len(self.address_postalcode) != 6:
            raise UserError(_(u'中国的邮编必须为6位数字！'))
        if self.address_country.code == 'US' and len(self.address_postalcode) not in (5, 10):
            raise UserError(_(u'美国的邮编必须为5位或10位数字！/ US Postal Code is 5 or 10 digits.'))

        if self.address_country.code == 'TW' and not self.vat_number:
            raise UserError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))

        # 校验通过，更新vendor register状态
        if self.state == 'draft':
            self.write({'state': 'submit'})

        # 给buyer发送邮件
        try:
            #utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_buyer_email')
            title = _("Tips for %s") % self.name1_cn
            return self.env['warning_box'].info(title=title, message=u"提交成功，请等待Buyer审核！")
        except:
            traceback.print_exc()
            return False

    def test_send_email(self):
        utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_buyer_email')
        return True

    @api.multi
    def button_reject(self):
        """
        buyer拒绝vendor的注册申请
        """
        if self.state == 'submit':
            self.write({'state': 'draft'})

            try:
                if self.env.user in self.env.ref('oscg_vendor.IAC_buyer_groups').users:
                    # buyer拒绝，给vendor发送邮件
                    utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_buyer_reject_email')
                #废弃代码,没有相应菜单不可能执行
                #if self.env.user in self.env.ref('oscg_vendor.IAC_qs_groups').users:
                #    # QS拒绝给vendor发送邮件
                #    utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_qs_reject_email')
            except:
                traceback.print_exc()
                return False

    @api.multi
    def button_cancel(self):
        """
        buyer取消vendor的注册申请
        """
        if self.state == 'submit':
            self.write({'state': 'cancel'})

    @api.multi
    def button_to_approve(self):
        """
        buyer同意vendor的注册申请，补充资料后送签webflow（供应商一阶段签核）
        """

        # 上传文档对应的审核人和失效时间校验
        config_list = self.env['iac.attachment.config'].search([('model_obj', '=', 'vendor'), ('is_displayed', '=', True)])
        for config in config_list:
            if config.is_required:
                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        if attachment.type.name == config.type.name and attachment.file_id:
                            if attachment.type.special_approved and not attachment.approver_id:
                                raise UserError(_(u'%s 审核人不能为空！' % (attachment.type.name)))

        # buyer补充的资料校验
        if not self.material_ids:
            raise UserError(_(u'Vendor的Division Code不能为空！'))
        if not self.use_project:
            raise UserError(_(u'应用的Project不能为空！'))
        if not self.apply_reason:
            raise UserError(_(u'申请原因不能为空！'))
        # 申请原因是客户指定时，必须上传佐证材料
        for reason in self.apply_reason:
            if reason.id == self.env.ref('oscg_vendor.iac_vendor_reason_customer').id:
                if not self.applyfile_id:
                    raise UserError(_(u'申请原因是客户指定时佐证文档不能为空！'))
        if not self.apply_memo:
            raise UserError(_(u'申请原因说明不能为空！'))
        if not self.is_scene:
            raise UserError(_(u'建议是否现地评鉴不能为空！'))
        if not self.is_outerbuy:
            raise UserError(_(u'是否属外购不能为空！'))

        # 调用webflow接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F01_B", biz_object)

        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签成功'})
            message = u'送签成功'
        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.name1_cn
        return self.env['warning_box'].info(title=title, message=message)

    def generate_account(self, name, email, password, buyer_email):
        """
        Vendor注册，生成register 资料
        """

        cryptor = AES.new('keyskeyskeyskeys', AES.MODE_CBC, 'keyskeyskeyskeys')
        expire_date_str = tools.config.get("expire_datetime")# 系统授权过期日期
        expire_date = cryptor.decrypt(a2b_hex(expire_date_str)).rstrip('\0')
        if fields.Datetime.from_string(expire_date) > datetime.now():
            # 用户输入校验
            # 校验Email
            email = email.lower()  # 转成小写
            buyer_email = buyer_email.lower()
            if not utility.is_email(email):
                return u"Email格式有误，请重新输入！"
            if not utility.is_email(buyer_email):
                return u"Buyer Email格式有误，请重新输入！"
            if not utility.checkPassword(password):
                #return u"密码长度必须大于6位，且包含大小写字母、数字和特殊字符"
                return u"Use 6 or more characters with a mix of letters, numbers & symbols for your password."

            # 校验buyer email
            buyer_flag = False
            buyer_users = self.env.ref('oscg_vendor.IAC_buyer_groups').users
            for user in buyer_users:
                if buyer_email == user.email:
                    buyer_flag = True
                    break
            if not buyer_flag:
                return u"Buyer Email不存在，请核实后重新输入！/ Buyer Email doesn't exist!"

            # 检查是否已经存在
            user_ids = self.env['res.users'].sudo().search([('name', '=', name), ('email', '=', email)])
            if user_ids:
                return u"注册信息已经存在，请勿重复注册！"

            # 使用序列生产login
            login = self.env['ir.sequence'].next_by_code('supplier.company.user')
            user_vals = {
                'name': name,
                'login': login,
                'password': password,
                'password_date': fields.Date.today(),
                'share': True
            }
            vendor_user = self.env['res.users'].sudo().create(user_vals)
            # 修改user对应的partner的email地址
            vendor_user.partner_id.write({'email': email, 'supplier': True})
            # 将当前Vendor user加入Vendor用户组
            vendor_group = self.env.ref('oscg_vendor.IAC_vendor_groups')
            if vendor_group:
                group_vals = {'groups_id': [(4, vendor_group.id)]}
                vendor_user.write(group_vals)

            # 必传附件和可选附件
            attachment_ids = []
            attachment_list = self.env['iac.attachment.config'].search(
                [('model_obj', '=', 'vendor'), ('is_displayed', '=', True)])
            for attachment in attachment_list:
                attachment_ids.append((0, 0, {'type': attachment.type.id, 'group': 'basic'}))

            # 生成register资料
            vendor_reg_vals = {
                'user_id': vendor_user.id,
                'other_emails': email,
                'buyer_email': buyer_email,
                'attachment_ids': attachment_ids
            }
            vendor_reg_rec=self.create(vendor_reg_vals)

            # 给user发送邮件
            try:
                utility.send_to_email(self, vendor_reg_rec.id, 'oscg_vendor.vendor_register_supplier_email')
            except:
                traceback.print_exc()
                return False

            return u"新用户注册成功，请注意查收邮件，以新账号登录系统！\n Please check your mailbox and use new account name to login."
        else:
            return "System Error!"

    def vendor_register_callback(self, context=None):
        """
        回调函数说明
        供应商注册第一步审核完成
        模型为 iac.vendor.register
        context={"approve_status": True,"data":{"id":1376,"vendor_property":"Own Parts",}}

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
                    vendor_reg = self.browse(int(context.get("data").get("id")))
                    if not vendor_reg.exists():
                        proc_result = False
                        proc_ex.append("iac_vendor_register with id %s is not exists!" %(context.get("data").get("id"),))
                        _logger("iac_vendor_register with id %s is not exists!" %(context.get("data").get("id"),))
                        return proc_result, proc_ex

                    vendor_reg.write({'state': 'done', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # F01审核通过就创建vendor资料
                    attachment_ids = []
                    attachment_list = self.env['iac.attachment.config'].search(
                        [('model_obj', '=', 'vendor_bank'), ('is_displayed', '=', True)])
                    for attachment in attachment_list:
                        attachment_ids.append((0, 0, {'type': attachment.type.id, 'group': 'bank'}))

                    vendor_code = ''
                    if vendor_reg.supplier_type == 'Agent':
                        vendor_code = 'TMP' + self.env['ir.sequence'].next_by_code('supplier.vendor.code')
                    elif vendor_reg.supplier_type == 'Manufacturer':
                        vendor_code = 'MAN' + self.env['ir.sequence'].next_by_code('supplier.vendor.code')
                    vendor_vals = {
                        'user_id': vendor_reg.user_id.id,
                        'vendor_reg_id': context.get("data").get("id"),
                        'buyer_email': vendor_reg.buyer_email.lower(),
                        'name': vendor_reg.name1_cn,
                        'currency': vendor_reg.currency.id,
                        'created_by': vendor_reg.user_id.login,
                        'creation_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'vendor_property': context.get("data").get("vendor_property"),
                        'attachment_ids': attachment_ids,
                        'vendor_type': 'normal',
                        'vendor_code': vendor_code
                    }
                    vendor = self.env['iac.vendor'].create(vendor_vals)
                    vendor_reg.write({'vendor_id': vendor.id})

                    # 更新vendor.material
                    material_list = self.env['iac.vendor.material'].search([('vendor_reg_id', '=', vendor_reg.id)])
                    for material in material_list:
                        material.write({'vendor_id': vendor.id})

                    # 通知相关负责人建立GV,SC,PLM
                    utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_gsp_buyer_email')
                else:
                    vendor_reg = self.browse(context.get("data").get("id"))
                    vendor_reg.write({'state': 'unapproved', 'state_msg': u'webflow(%s)签核未通过' % context["rpc_callback_data"]["EFormNO"]})

                proc_result = True
                return proc_result, proc_ex
        except:
            ex_string = traceback.format_exc()
            proc_result = False
            proc_ex.append(ex_string)
            traceback.print_exc()
            return proc_result, proc_ex

class IacAttachment(models.Model):
    """
    Iac附件
    """

    _name = "iac.attachment"
    _description = u"Iac Attachment"

    file_id = fields.Many2one('muk_dms.file', string="Attachment File",index=True)
    description = fields.Char(string='Description')
    type = fields.Many2one('iac.attachment.type', string="Attachment Type", readonly=True)
    time_sensitive = fields.Boolean(related='type.time_sensitive', string='Time Sensitive')
#    group = fields.Selection([('basic', 'Basic'), ('bank', 'Bank')], string="Group", default="basic")# basic：基本资料的附件；bank：银行资料的附件
    group = fields.Selection(string='Group', selection='_selection_subgroup', required=True, default="basic")# basic：基本资料的附件；bank：银行资料的附件
    upload_date = fields.Date(string="Upload Date")  # 上传日期
    expiration_date = fields.Date(string="Expiration Date")# 失效日期
    state = fields.Selection([
        ('upload', 'Upload'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='upload')
    active = fields.Boolean(string="Active", default=True)
    memo = fields.Text(string='Memo')

    @api.multi
    def unlink(self):
        raise UserError(_(u'不能删除文档！'))

    @api.model
    def _selection_subgroup(self):
        res_type = []
        group_list = self.env['ir.config_parameter'].search([('key', 'like', 'doc_config_group_')])
        for item in group_list:
            res_type.append((item.key[17:], _(item.value)))

        return res_type

class IacVendorRegisterAttachment(models.Model):
    """vendor注册资料附件"""
    _name = "iac.vendor.register.attachment"
    _inherit = "iac.attachment"

    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Register", readonly=True)
    approver_id = fields.Many2one('res.users', string='Approve User')
    is_file_reviewer =fields.Boolean('Is File Reviewer',compute='_compute_is_file_reviewer')

    @api.one
    def _compute_is_file_reviewer(self):
        file_group = self.env.ref('oscg_vendor.IAC_qs_groups')
        if self.env.user.id in file_group.users.ids:
            self.is_file_reviewer=True
        else:
            self.is_file_reviewer=False


    @api.model
    def create(self, values):
        if values.get('file_id', False):
            # 给approver发送邮件
            utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_qs_attachment_email')
        result = super(IacVendorRegisterAttachment, self).create(values)

        buyer_group = self.env.ref('oscg_vendor.IAC_buyer_groups')
        #如果当前操作员是buyer ,需要校验文件是否指定审核人
        if self.env.user.id in buyer_group.users.ids:
            if result.type.special_approved==True and (not result.approver_id.exists()):
                raise UserError("Special Approved File Type Must specific Approve User")
        return result

    @api.multi
    def write(self, values):
        result = super(IacVendorRegisterAttachment, self).write(values)
        # 给approver发送邮件
        if values.get('file_id', False):
            utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_qs_attachment_email')
        buyer_group = self.env.ref('oscg_vendor.IAC_buyer_groups')
        #如果当前操作员是buyer ,需要校验文件是否指定审核人
        if self.env.user.id in buyer_group.users.ids:
            if self.type.special_approved==True and (not self.approver_id.exists()):
                raise UserError("Special Approved File Type Must specific Approve User")
        return result


class IacVendorAttachment(models.Model):
    """vendor银行资料附件"""
    _name = "iac.vendor.attachment"
    _inherit = "iac.attachment"

    vendor_id = fields.Many2one("iac.vendor", String="Vendor", readonly=True)
    approver_id = fields.Many2one('res.users', string='Approve User')


    @api.model
    def create(self, values):
        try:
            # 给approver发送邮件
            if values.get('file_id', False):
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_qs_attachment_email')
            result = super(IacVendorAttachment, self).create(values)
            return result
        except:
            traceback.print_exc()
            return False

    @api.multi
    def write(self, values):
        try:
            # 给approver发送邮件
            if values.get('file_id', False):
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_qs_attachment_email')
            result = super(IacVendorAttachment, self).write(values)
            return result
        except:
            traceback.print_exc()
            return False

class IacVendorChangeAttachment(models.Model):
    """vendor change银行资料附件"""
    _name = "iac.vendor.change.attachment"
    _inherit = "iac.vendor.attachment"
    _table="iac_vendor_attachment"

    type = fields.Many2one('iac.attachment.type', string="Attachment Type", readonly=True)
    change_id = fields.Many2one("iac.vendor.change.basic", String="Vendor Change Bank Info")
    approver_id = fields.Many2one('res.users', string='Approve User')

    @api.model
    def create(self,value):
        result=super(IacVendorChangeAttachment,self).create(value)
        if result.change_id.exists():
            update_vals={"vendor_id":result.change_id.vendor_reg_id.vendor_id.id}
            super(IacVendorChangeAttachment,self).write(update_vals)
        return result




class IacVendorAttachmentWizard(models.TransientModel):
    """Vendor Attachment向导"""
    _name = 'iac.vendor.attachment.wizard'

    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor")
    state = fields.Selection([
        ('upload', 'Upload'),
        ('active', 'Activate'),
        ('inactive', 'Inactivate')
    ], string='Status', default='upload', require=True)

    @api.multi
    def search_vendor_attachments(self):
        result = []
        for wizard in self:
            domain = []
            if wizard.vendor_id:
                domain += [('vendor_id', '=', wizard.vendor_id.id)]
            if wizard.state:
                domain += [('state', '=', wizard.state)]
            result = self.env['iac.vendor.attachment'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor Attachment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iac.vendor.attachment'
        }
        return action

class IacVendorRegisterAttachmentWizard(models.TransientModel):
    """Vendor Register Attachment向导"""
    _name = 'iac.vendor.register.attachment.wizard'

    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Register")
    state = fields.Selection([
        ('upload', 'Upload'),
        ('active', 'Activate'),
        ('inactive', 'Inactivate')
    ], string='Status', default='upload', require=True)

    @api.multi
    def search_vendor_attachments(self):
        result = []
        for wizard in self:
            domain = []
            if wizard.vendor_reg_id:
                domain += [('vendor_reg_id', '=', wizard.vendor_reg_id.id)]
            if wizard.state:
                domain += [('state', '=', wizard.state)]
            result = self.env['iac.vendor.register.attachment'].search(domain)

        action = {
            'domain': [('id', 'in', [x.id for x in result])],
            'name': _('Vendor Register Attachment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iac.vendor.register.attachment'
        }
        return action

class IacVendorCodeWizard(models.TransientModel):
    """Select Vendor向导"""
    _name = 'iac.select.vendor.wizard'

    plant_code = fields.Char(string="Current Plant Code")
    vendor_code = fields.Char(string="Current Vendor Code")
    plant_id = fields.Many2one('pur.org.data', string="Plant", required=True)
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor Code", required=True)

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.env.user.plant_id:
            plant_code = "%s(%s)" % (self.env.user.plant_id.plant_name_cn, self.env.user.plant_id.plant_code)
            self.plant_code = plant_code
        if self.env.user.vendor_id:
            if self.env.user.vendor_id.vendor_code:
                vendor_code = "%s(%s)" % (self.env.user.vendor_id.name, self.env.user.vendor_id.vendor_code)
            else:
                vendor_code = self.env.user.vendor_id.name
            self.vendor_code = vendor_code

        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_id': [('state', '=', 'done')]}}

    @api.multi
    def select_vendor_code(self):
        request.session['session_plant_id'] = self.plant_id.id
        request.session['session_vendor_id'] = self.vendor_id.id
        return self.env['warning_box'].info(title="Select Vendor", message=u"Vendor Code设置成功！")

class IacVendorProduct(models.Model):
    _name="iac.vendor.product"
    _description=u"product_line"

    vendor_id = fields.Many2one("iac.vendor", String="vendor")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="vendor register")
    product_name = fields.Char(String="Product Name")
    #product_type = fields.Many2one('material.group', string="Product Type*", domain=[('material_group', 'ilike', 'R-')])
    product_type = fields.Many2one('material.group', string="Product Type*")
    product_class = fields.Many2one('plm.subclass', string='Sub Class*')
    brand_name = fields.Char(String="Brand Name*")
    capacity_month = fields.Char(String="Capacity by month")
    major_customer = fields.Char(String="Major Customer*")
    material_group_name = fields.Char(string="Material Group Name", compute='_taken_material_group')

    @api.one
    def _taken_material_group(self):
        """
        累计当前记录对应的asn数量
        :return:
        """
        if self.product_type.exists():
            self.material_group_name=self.product_type.material_group
        else:
            self.material_group_name=False

    @api.onchange('product_type')
    def onchange_product_type(self):
        res = {}
        if self.product_type.exists():
            res['domain'] = {'product_class': [('material_group', '=', self.product_type.material_group)]}
        return res
        if self.product_type.exists():
            self.product_class=False

class IacVendorFactory(models.Model):
    _name="iac.vendor.factory"
    _description = u"factory_line"

    vendor_id = fields.Many2one("iac.vendor", String="Vendor")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="vendor register")

    factory_type = fields.Selection([("NORMAL",u"NORMAL"),("FOUNDRY",u"FOUNDRY"),("PACKAGING",u"PACKAGING"),("TESTING",u"TESTING")],String="Type")
    factory_name = fields.Char(string="Name")
    factory_location = fields.Char(String="Location")
    factory_address = fields.Char(String="Address")
    main_flag = fields.Boolean(String="Main_Flag")
    ur_flag = fields.Boolean(String="UR Flag")
    relation = fields.Selection([("Self-Owned",u"Self-Owned"),("Joint-Venture",u"Joint-Venture"),("Outsourcing",u"Outsourcing")], string="Relation")
    qa_contact = fields.Char(String="QA Contact")
    qa_tel = fields.Char(String="QA Tel")
    qa_email = fields.Char(String="QA Email")

class IacVendorMaterial(models.Model):
    """
    Buyer补充填写的资料
    """
    _name="iac.vendor.material"
    _description = u"Vendor Material"

    vendor_id = fields.Many2one("iac.vendor", String="Vendor")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="vendor register")
    division_code = fields.Many2one('division.code', string="Division Code*")
    project = fields.Char(string="Project*")
    material_group = fields.Many2one('material.group', string="Material Group*", domain=[('material_group', 'ilike', 'R-')])
