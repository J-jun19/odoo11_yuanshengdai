# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from odoo import SUPERUSER_ID
from odoo.http import request
import traceback
import time, base64
import logging
import utility
from datetime import datetime
import psycopg2
import os.path
import json
_logger = logging.getLogger(__name__)

class IacVendor(models.Model):
    """
    Vendor主档
    """
    _name = "iac.vendor"
    _description = "Vendor"
    _rec_name = 'vendor_code'
    _order = 'id desc, name'

    _sql_constraints = [
        ('iac_vendor_vendor_code_uniq', 'unique (vendor_code)', "vendor_code already exists !"),
    ]
    name = fields.Char(string="Name", index=True)
    user_id = fields.Many2one('res.users', string="Login", index=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Vendor Register", index=True)
    buyer_email = fields.Char(string="Buyer email", index=True)
    buyer_id = fields.Many2one('res.partner', compute='_compute_buyer_id')
    vendor_code = fields.Char(string="Vendor Code", readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('submit', 'Submit'),  # vendor编辑好提交buyer review
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),  # webflow拒绝或抽单
        ('to sap', 'To SAP'),  # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'),  # 表单取消
        ('block', 'Block'),  # 锁定状态
        ('deleted', 'Deleted')  # 删除状态
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message")
    webflow_number = fields.Char(string="Webflow Number", readonly=True)
    current_class = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('DW', 'DW'),
    ], default='C', string="Class", related='supplier_company_id.current_class', copy=False)  # 评核等级
    class_date = fields.Date('Class Date', related='supplier_company_id.class_date', readonly=True, copy=False)  # 评核日期，每次评核生效时更新该字段
    score_snapshot = fields.Char(string='Score Snapshot', related='supplier_company_id.score_snapshot', readonly=True, copy=False)  # 评核快照号
    vendor_site_id = fields.Char(string="vendor_site_id")
    vendor_site_id_1 = fields.Char(string="vendor_site_id_1")
    vendor_quality_rating = fields.Char(string="vendor_quality_rating")
    vendor_delivery_rating = fields.Char(string="vendor_delivery_rating")
    vendor_type = fields.Selection([
        ('normal', 'Normal'),
        ('spot', 'Spot'),
        ('mold', 'Mold'),
        ('bvi', 'BVI'),
    ], default='normal', string="Vendor Type")
    vendor_default_id = fields.Char(string="vendor_default_id")
    parent_id = fields.Many2one('res.partner', string="Parent")
    erp_system_id = fields.Char(string="erp_system_id")
    z_terms_code = fields.Char(string="z_terms_code")
    ship_code = fields.Char(string="ship_code")

    z_buyer_erp_id = fields.Char(string="z_buyer_erp_id")
    sort_field = fields.Char(string="sort_field")
    purchasing_block = fields.Char(string="purchasing_block")
    vat_reg_no = fields.Char(string="vat_reg_no")
    language_key = fields.Char(string="language_key")
    payment_block = fields.Char(string="payment_block")
    z_eval_receipt_stlmt = fields.Char(string="z_eval_receipt_stlmt")
    z_confirmation_control = fields.Char(string="z_confirmation_control")
    creation_date = fields.Datetime(string="creation_date")
    created_by = fields.Char(string="created_by")
    last_update_date = fields.Char(string="last_update_date")
    last_updated_by = fields.Char(string="last_updated_by")
    last_asn_no = fields.Char(string="last_asn_no")
    vmi_enabled = fields.Char(string="vmi_enabled")
    vmi_due_in_weeks = fields.Char(string="VMI Due In Weeks")
    si_flag = fields.Char(string="si_flag")
    last_si_no = fields.Char(string="last_si_no")
    global_vendor_code = fields.Char(string="global_vendor_code", readonly=True)
    order_currency = fields.Char(string="order_currency", related="currency.name")
    vendor_group = fields.Char(string="vendor_group")
    vendor_title = fields.Char(string="vendor_title")
    sh_import_flag = fields.Char(string="sh_import_flag")
    vendor_url = fields.Char(string="vendor_url", size=132)
    supplier_company_id = fields.Many2one('iac.supplier.company', String="Supplier Company")
    supplier_type = fields.Char(string="Supplier Type", compute='_taken_supplier_type')
    show_in = fields.Char(string="show_in")
    real_online = fields.Char(string="real_online")
    vendor_sap_status = fields.Char(string="vendor_sap_status")
    last_asn_no_sec = fields.Char(string="last_asn_no_sec")
    spotflag = fields.Char(string="spotflag")

    # Bank信息
    bank_name = fields.Char(string="Bank Name*", size=60)
    branch_name = fields.Char(string="Bank Branch Name*", size=40)
    account_number = fields.Char(string="Bank Account No.*", size=35)
    account_number_1 = fields.Char(string="Bank Account No First 16", compute='_taken_account_number_1')
    account_number_2 = fields.Char(string="Bank Account No Last", compute='_taken_account_number_2')
    swift_code = fields.Char(string="SWIFT Code*", size=11)
    transfer_number = fields.Char(string="Bank Transfer Number(TaiwanSupplier Must Specify)")
    bank_street = fields.Char(string="Bank - Street*", size=35)
    bank_city = fields.Char(string="Bank - City*", size=35)
    bank_country = fields.Many2one('res.country', string="Bank - Country Code *", domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])
    attachment_ids = fields.One2many("iac.vendor.attachment", "vendor_id", string="Attachment Lines")

    # Buyer approved supplier bank information and input basic data
    rma_terms = fields.Selection(string="RMA Terms *", selection='_selection_rmaterms')
    it_level = fields.Selection(string="Vendor IT Support Level *", selection='_selection_itlevel')
    plant = fields.Many2one('pur.org.data', string="Plant *")
    payment_term = fields.Many2one('payment.term', string='Payment Term*')
    incoterm = fields.Many2one('incoterm', string='Incoterm*')
    destination = fields.Char(string="Destination*")
    reason = fields.Text(string="Reason*")
    vmi_supplier = fields.Selection([("yes", "Yes"), ("no", "No")], string="VMI Supplier*")
    vmi_due = fields.Char(string="VMI Due In Week*")
    si_supplier = fields.Selection([("yes", "Yes"), ("no", "No")], string="SI Supplier*")
    import_required = fields.Selection([("yes", "Yes"), ("no", "No")], string="Import Data Required*")
    local_foreign = fields.Selection([("local", "Local"), ("foreign", "Foreign")], string="Local or Foreign*")
    purchase_contract = fields.Many2one('muk_dms.file', string="Purchase Contract*")
    probity_agreement = fields.Many2one('muk_dms.file', string="Probity Agreement*")
    finance = fields.Many2one('res.partner', string="Finance")

    # 其他从Register带过来的字段
    currency = fields.Many2one('res.currency', string="Currency *")

    bank_id = fields.Many2one('vendor.bank', string="Bank Info From SAP")
    sap_vendor_id = fields.Many2one('vendor', string="Vendor Info From SAP")
    vendor_account_group = fields.Char(string='Vendor Account Group', compute="_taken_vendor_account_group", store=True,
                                       size=4)
    sap_vendor_cert_id = fields.Many2one('vendor.certified', string="Vendor Certified Info From SAP")
    partner_bank_type = fields.Char(string='Partner Bank Type', size=4)

    vendor_property = fields.Selection([("Own Parts", "Own Parts"), ("AVAP", "AVAP"), ("Buy and Sell", "Buy and Sell")],
                                       string="Vendor Property")

    # 废弃的字段 incoterm 和 destination 已经存在
    z_fob = fields.Char(string="z_fob")
    z_fob2 = fields.Char(string="z_fob2")
    is_bind = fields.Boolean(string="Is Bind", default=False, readonly=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record['name']:
                name = record['name']
            else:
                name = ''
            if record['vendor_code']:
                name = record['vendor_code'] + ' ' + name
            res.append((record['id'], name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain += ['|', ('vendor_code', operator, name), ('name', operator, name)]
        vendors = self.search(domain + args, limit=limit)
        return vendors.name_get()

    @api.depends('supplier_company_id')
    def _taken_supplier_type(self):
        """
        从supplier company查supplier_type
        """
        supplier_type = False
        for r in self:
            if r.supplier_company_id:
                supplier_type = r.supplier_company_id.supplier_type
        return supplier_type

    @api.depends('vendor_type', 'plant', 'local_foreign')
    def _taken_vendor_account_group(self):
        for v in self:
            for account_group in self.env['iac.vendor.account.group'].search([]):
                if v.vendor_type == 'normal' and account_group.vendor_type == v.vendor_type \
                        and account_group.plant_id.id == v.plant.id and account_group.local_foreign == v.local_foreign:
                        v.vendor_account_group = account_group.account_group
                elif v.vendor_type == 'spot' and account_group.vendor_type == v.vendor_type \
                        and account_group.plant_id.id == v.plant.id and account_group.local_foreign == v.local_foreign:
                    v.vendor_account_group = account_group.account_group
                elif v.vendor_type == 'mold' and account_group.vendor_type == v.vendor_type \
                        and account_group.plant_id.id == v.plant.id:
                    v.vendor_account_group = account_group.account_group
                elif v.vendor_type == 'bvi' and account_group.vendor_type == v.vendor_type:
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

    @api.depends('buyer_email')
    def _compute_buyer_id(self):
        for vendor in self:
            if vendor.buyer_email:
                buyer = self.env['res.partner'].search([('active', '=', True), ('email', '=', vendor.buyer_email)], limit=1)
                vendor.buyer_id = buyer.id

    @api.model
    def _selection_rmaterms(self):
        res_type = []
        term_list = self.env['ir.config_parameter'].search([('key', 'like', 'rmaterms_')])
        for item in term_list:
            res_type.append((item.key[9:], _(item.value)))

        return res_type

    @api.model
    def _selection_itlevel(self):
        res_type = []
        level_list = self.env['ir.config_parameter'].search([('key', 'like', 'itlevel_')])
        for item in level_list:
            res_type.append((item.key[8:], _(item.value)))

        return res_type

    @api.multi
    def button_submit(self):
        """
        vendor填写bank info 后提交
        """

        # 必填项校验
        if not self.bank_name:
            raise UserError(_(u'Bank Name不能为空！/ Bank Name is required!'))
        if not self.branch_name:
            raise UserError(_(u'Bank Branch Name不能为空！/ Bank Branch Name is required!'))
        if not self.account_number:
            raise UserError(_(u'Bank Account No.不能为空！/ Bank Account No. is required!'))
        if not self.bank_street:
            raise UserError(_(u'Bank - Street不能为空！/ Bank-Street is required!'))
        if not self.bank_city:
            raise UserError(_(u'Bank - City不能为空！/ Bank-City is required!'))
        if not self.bank_country:
            raise UserError(_(u'Bank - Country Code不能为空！/ Bank-Country Code is required!'))

        # 上传文档校验
        attachment_list = self.env['iac.attachment.config'].search([('model_obj', '=', 'vendor_bank'), ('is_displayed', '=', True)])
        for attachment in attachment_list:
            if attachment.is_required:
                is_upload = False
                for file in self.attachment_ids:
                    if file.type.name == attachment.type.name and file.file_id:
                        is_upload = True
                if not is_upload:
                    raise UserError(_(u'%s文件必须上传！') % (attachment.type.name))

        # 校验通过，更新vendor状态
        if self.state == 'draft':
            self.write({'state': 'submit'})

        try:
            # 给buyer发送邮件
            utility.send_to_email(self, self.id, 'oscg_vendor.vendor_bank_email')

            title = _("Tips for %s") % self.name
            return self.env['warning_box'].info(title=title, message=u'提交成功！')
        except:
            traceback.print_exc()
            return False

    @api.multi
    def button_reject(self):
        """
        buyer拒绝vendor的bank info
        """

        if self.state == 'submit':
            self.write({'state': 'draft', 'state_msg': 'buyer拒绝'})

    @api.multi
    def button_to_approve(self):
        """
        Buyer approved supplier bank information（供应商二阶段签核）
        """

        # buyer补充的资料校验
        if not self.rma_terms:
            raise UserError(_(u'RMA Terms不能为空！/ RMA Terms are required!'))
        if not self.it_level:
            raise UserError(_(u'IT Support Level不能为空！'))
        if not self.plant:
            raise UserError(_(u'Plant不能为空！/ Plant is required!'))
        if not self.payment_term:
            raise UserError(_(u'Payment Term不能为空！/ Payment Term is required!'))
        if not self.incoterm:
            raise UserError(_(u'Incoterm不能为空！'))
        if not self.destination:
            raise UserError(_(u'Destination不能为空！/ Destination is required!'))
        if not self.reason:
            raise UserError(_(u'Reason不能为空！/ Reason is required!'))
        if not self.vmi_supplier:
            raise UserError(_(u'VMI Supplier不能为空！'))
        if not self.vmi_due:
            raise UserError(_(u'VMI Due In Week不能为空！'))
        if not self.si_supplier:
            raise UserError(_(u'SI Supplier不能为空！/ SI Supplier is required!'))
        if not self.import_required:
            raise UserError(_(u'Import Data Required不能为空！'))
        if not self.local_foreign:
            raise UserError(_(u'Ship Destination不能为空！/ Ship Destination is required!'))
        #if not self.purchase_contract:
        #    raise UserError(_(u'Purchase Contract不能为空！'))
        #if not self.probity_agreement:
        #    raise UserError(_(u'Probity Agreement不能为空！'))
        if not self.vendor_reg_id.material_ids:
            raise UserError(_(u'Vendor的Division Code不能为空！'))

        # 调用webflow接口
        biz_object = {
            "id": self.vendor_reg_id.id,
            "biz_object_id": self.vendor_reg_id.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F02_B", biz_object)

        message = ''
        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签成功'})
            message = u'送签成功'
        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.name
        return self.env['warning_box'].info(title=title, message=message)

    def vendor_be_normal_callback(self, context=None):
        """
        回调函数说明
        供应商提供银行资料后审核通过变更为正常状态
        模型为 iac.vendor
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
                    vendor = self.browse(context.get("data").get("id"))
                    vendor.write({'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 补充vendor register的plant_id
                    vendor.vendor_reg_id.write({'plant_id': vendor.plant.id})

                    # 调用SAP接口
                    if self.button_to_sap(context.get("data").get("id")):
                        proc_result = True
                        return proc_result, proc_ex
                    else:
                        proc_result = True
                        proc_ex.append(u'通知SAP失败')
                        return proc_result, proc_ex
                else:
                    vendor = self.browse(context.get("data").get("id"))
                    vendor.write({'state': 'unapproved', 'state_msg': u'webflow(%s)签核未通过' % context["rpc_callback_data"]["EFormNO"]})

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
            vendor = self
        else:
            vendor = self.browse(object_id)

        try:
            # 调用SAP接口
            biz_object = {
                "id": vendor.id,
                "biz_object_id": vendor.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_VENDOR_001", biz_object)
            if rpc_result:
                vendor.write({'state': 'done',
                              'state_msg': u'通知SAP成功',
                              'vendor_code': rpc_json_data['vendor_code']})
                vendor.vendor_reg_id.vendor_code = rpc_json_data['vendor_code']

                # 给厂商和buyer发邮件
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_sap_supplier_email')
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_register_sap_buyer_email')

                return True
            else:
                vendor.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})

                return False
        except:
            traceback.print_exc()
            vendor.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
            return False

class IacVendorVendor(models.Model):
    """
    继承iac.vendor模型，增加search方法
    """
    _name = "iac.vendor.vendor"
    _description = "VendorVendor"
    _inherit = 'iac.vendor'
    _table = 'iac_vendor'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        # 根据角色过滤数据
        if self.env.user.id != SUPERUSER_ID:
            if self.env.user.has_group('oscg_vendor.IAC_vendor_groups'):
                if self.env.user.vendor_id:
                    if not context.get('do_not_filter_vendor_by_vendor_id'):
                        args += [('id', '=', self.env.user.vendor_id.id)]
            elif self.env.user.has_group('oscg_vendor.IAC_buyer_groups'):
                if not context.get('do_not_filter_vendor_by_buyer_email'):  # vendor copy 不过滤，其他场景过滤
                    args += [('buyer_email', '=', self.env.user.partner_id.email)]

        return super(IacVendor, self).search(args, offset, limit, order, count=count)

class IacSupplierCompany(models.Model):
    _name = "iac.supplier.company"
    _description = u"supplier company"
    _order = 'id desc'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "company name already exists !"),
    ]

    company_no = fields.Char(string="Company No", readonly=True, index=True)
    name = fields.Char(string="Company name*", required=True, index=True)
    company_name2 = fields.Char(string="Company name2")
    vat_no = fields.Char(string="Vat No")
    supplier_type = fields.Selection(string='Supplier Company Type *', selection='_selection_supplier_type', required=True)
    line_ids = fields.One2many("iac.supplier.company.line", 'supplier_company_id', required=True, string="Vendors")
    comment = fields.Text(string="Comments")
    current_class = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('DW', 'DW')], default='C', readonly=True)
    class_date = fields.Date('Class Date', readonly=True, copy=False)# 评核日期，每次评核生效时更新该字段
    score_snapshot = fields.Char(string='Score Snapshot', readonly=True, copy=False)# 评核快照号
    state_msg=fields.Text(string='State Message')
    state=fields.Selection([('draft','Draft'),('done','Done'),('sap_error','SAP Error')],string="Status")
    is_bind = fields.Boolean(string="Is GV Bind", default=False, readonly=True)

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for supplier in self:
            name = supplier.company_no + ' ' + supplier.name
            result.append((supplier.id, name))
        return result

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError(u"请选择Vendor！")

    @api.model
    def create(self, vals):
        if (not vals.get('company_no', False)):
            vals['company_no'] = self.env['ir.sequence'].next_by_code('supplier.company.code')

        return super(IacSupplierCompany, self).create(vals)

    @api.model
    def _selection_supplier_type(self):
        res_type = []
        type_list = self.env['ir.config_parameter'].search([('key', 'like', 'supplier_company_type_')])
        for item in type_list:
            res_type.append((item.key[22:], _(item.value)))

        return res_type

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('company_no', operator, name)]
        objects = self.search(domain + args, limit=limit)
        return objects.name_get()

class IacSupplierCompanyLine(models.Model):
    _name = "iac.supplier.company.line"

    supplier_company_id = fields.Many2one('iac.supplier.company', string="Supplier Company")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", required=True, domain=[('is_bind', '=', False)])
    vendor_code = fields.Char(string="Vendor Code", related="vendor_id.vendor_code", readonly=True)
    vendor_name = fields.Char(string="Vendor Name", related="vendor_id.name", readonly=True)
    state_msg=fields.Text(string='State Message')
    state=fields.Selection([('draft','Draft'),('done','Done'),('sap_error','SAP Error')],string="Status")

    @api.model
    def create(self, values):
        result = super(IacSupplierCompanyLine, self).create(values)
        result.vendor_id.is_bind = True
        result.vendor_id.supplier_company_id = result.supplier_company_id.id
        return result

    @api.multi
    def unlink(self):
        self.vendor_id.is_bind = False
        self.vendor_id.supplier_company_id = False
        result = super(IacSupplierCompanyLine, self).unlink()
        return result

class IacGlobalVendor(models.Model):
    _name = "iac.global.vendor"
    _description = u"Global Vendor"
    _order = 'id desc'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "company name already exists !"),
    ]

    global_vendor_code = fields.Char(string="Global Vendor", readonly=True)
    name = fields.Char(string="Global Vendor Name*", required=True, index=True)
    global_name2 = fields.Char(string="Global Vendor Name2")
    global_address = fields.Char(string="Global Address")
    global_address2 = fields.Char(string="Global Address2")
    line_ids = fields.One2many('iac.global.vendor.line', 'global_vendor_id', string='Supplier Company', required=True)
    supplier_type = fields.Char(string="Supplier Type", readonly=True)
    comment = fields.Text(string="Comments")
    is_manufacturer = fields.Boolean(string="Is Manufacturer", compute="_compute_is_manufacturer",
                                     search="_search_is_manufacturer")
    is_used = fields.Boolean(string="Is Used", default=False)

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError(u"请选择Supplier！")

    @api.model
    def create(self, values):
        if (not values.get('global_vendor_code', False)):
            values['global_vendor_code'] = self.env['ir.sequence'].next_by_code('global.vendor.code')

        # 去重supplier
        line_ids = set()
        list_line_ids = []
        if values.get('line_ids', False):
            for line_id in values.get('line_ids', False):
                line_ids.add(line_id[2]['supplier_company_id'])
            for item in line_ids:
                list_line_ids.append([0, False, {'supplier_company_id': item}])
            values['line_ids'] = list_line_ids

        return super(IacGlobalVendor, self).create(values)

    @api.multi
    def write(self, values):
        # 去重supplier
        line_ids = set()  # 新添加去重
        list_line_add_ids = []  # 新添加
        list_line_reserve_ids = []  # 保留
        list_line_remove_ids = []  # 删除
        if values.get('line_ids', False):
            for line_id in values.get('line_ids', False):
                if line_id[0] == 0:  # 新添加
                    line_ids.add(line_id[2]['supplier_company_id'])
                elif line_id[0] == 4:  # 保留
                    list_line_reserve_ids.append(line_id)
                elif line_id[0] == 2:  # 删除
                    list_line_remove_ids.append(line_id)
            int_list_line_reserve_ids = [self.env['iac.global.vendor.line'].browse(x[1]).supplier_company_id.id for x in
                                         list_line_reserve_ids]
            for item in line_ids:
                if item not in int_list_line_reserve_ids:
                    list_line_add_ids.append([0, False, {'supplier_company_id': item}])
            values['line_ids'] = list_line_reserve_ids + list_line_add_ids + list_line_remove_ids

        result = super(IacGlobalVendor, self).write(values)
        return result

    @api.depends('line_ids.supplier_company_id')
    def _compute_is_manufacturer(self):
        flag = False
        for global_vendor in self:
            for line_supplier in global_vendor.line_ids:
                for line_vendor in line_supplier.supplier_company_id.line_ids:
                    if line_vendor.vendor_id.vendor_reg_id and line_vendor.vendor_id.vendor_reg_id.supplier_type == 'Manufacturer':
                        flag = True
                        break
            global_vendor.is_manufacturer = flag

    @api.multi
    def _search_is_manufacturer(self, operator, value):
        ids = []
        self.env.cr.execute("""
                    select a.id 
                    from iac_global_vendor a, iac_global_vendor_line b, iac_supplier_company c, 
                         iac_supplier_company_line d, iac_vendor_register e
                    where a.id = b.global_vendor_id
                    and b.supplier_company_id = c.id
                    and c.id = d.supplier_company_id
                    and d.vendor_id = e.vendor_id
                    and e.supplier_type = 'Manufacturer'
                """)
        gv_ids = self.env.cr.dictfetchall()
        for gv in gv_ids:
            ids.append(gv['id'])

        return [('id', 'in', ids)]

class IacGlobalVendorLine(models.Model):
    _name = "iac.global.vendor.line"

    global_vendor_id = fields.Many2one('iac.global.vendor', string="Global Vendor")
    supplier_company_id = fields.Many2one('iac.supplier.company', string="Supplier Company", required=True, domain=[('is_bind', '=', False)])
    company_no = fields.Char(related="supplier_company_id.company_no", string="Company No", readonly=True)
    company_name = fields.Char(related="supplier_company_id.name", string="Company Name", readonly=True)

    @api.model
    def create(self, values):
        result = super(IacGlobalVendorLine, self).create(values)
        result.supplier_company_id.is_bind = True
        return result

    @api.multi
    def unlink(self):
        self.supplier_company_id.is_bind = False
        result = super(IacGlobalVendorLine, self).unlink()
        return result

class IacVendorPlm(models.Model):
    _name = "iac.vendor.plm"
    _description = u"IAC Vendor Plm"

    name = fields.Char(string="PLM Name", required=True, index=True)
    global_vendor_id = fields.Many2one('iac.global.vendor', string="Global Vendor", required=True )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.model
    def create(self, values):
        result = super(IacVendorPlm, self).create(values)
        domain=[('name','=',result.name),('id','!=',result.id)]
        search_result=self.env["iac.vendor.plm"].search(domain,limit=1)
        if search_result.exists():
            raise UserError("PLM Name must be unique")
        super(IacVendorPlm,result).write({"state":"draft"})

        result.global_vendor_id.write({"is_used":True})
        #result.global_vendor_id.is_used = True
        #result.state = 'done'
        return result

class IacVendorCopy(models.Model):
    """
    Vendor Copy
    """
    _name = "iac.vendor.copy"
    _order = "id desc"

    ori_vendor_id = fields.Many2one('iac.vendor', string="Copy Vendor", required=True, domain=[('state', 'in', ['done', 'block']), ('vendor_type', '=', 'normal')], index=True)
    ori_company_name = fields.Char(related="ori_vendor_id.name", string="Company Name")
    ori_local_foreign = fields.Selection([("local", "Local"), ("foreign", "Foreign")], related="ori_vendor_id.local_foreign", string="Local or Foreign")
    ori_currency = fields.Many2one('res.currency', related="ori_vendor_id.currency", string="Currency")
    ori_plant = fields.Many2one('pur.org.data', related="ori_vendor_id.plant", string="Plant", index=True)
    ori_payment_term = fields.Many2one('payment.term', related="ori_vendor_id.payment_term", string="Payment Term")
    ori_incoterm = fields.Many2one('incoterm', related="ori_vendor_id.incoterm", string="Incoterm")
    ori_destination = fields.Char(related="ori_vendor_id.destination", String="Destination")

    new_vendor_id = fields.Many2one('iac.vendor.vendor', string="New Vendor")
    plant = fields.Many2one('pur.org.data', string="Plant *", required=True, index=True)
    currency = fields.Many2one('res.currency', string="Currency *", required=True)
    buyer_email = fields.Char(string="Buyer Email *", readonly=True, required=True)
    payment_term = fields.Many2one('payment.term', string='Payment Term*', required=True)
    incoterm = fields.Many2one('incoterm', string='Incoterm*', required=True)
    destination = fields.Char(string="Destination*", required=True)
    local_foreign = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Local or Foreign *', required=True)
    copy_reason = fields.Text(string="Copy Reason *", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('callback_error', 'Call Back Error'),  # webflow回调处理过程中出现异常
        ('unapproved', 'Unapproved'),# webflow拒绝或抽单
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled') # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)
    webflow_number = fields.Char(string="Webflow Number", readonly=True)
    context_str=fields.Text(string="Context Info")

    @api.model
    def default_get(self, fields):
        result = super(IacVendorCopy, self).default_get(fields)
        result['buyer_email'] = self.env.user.email
        return result

    @api.model
    def create(self, values):
        # 检查copy的vendor各内容都一样的单子
        same_count = self.sudo().search_count([('plant', '=', values.get('plant', False)), ('currency', '=', values.get('currency', False)),
                                      ('buyer_email', '=', values.get('buyer_email', False)), ('payment_term', '=', values.get('payment_term', False)),
                                      ('incoterm', '=', values.get('incoterm', False)), ('destination', '=', values.get('destination', False)),
                                      ('local_foreign', '=', values.get('local_foreign', False)), ('state', '=', 'draft')])
        if same_count > 0:
            raise UserError(_(u'Vendor Copy 新厂商栏位都一样的单子已经存在，不能保存！'))

        result = super(IacVendorCopy, self).create(values)
        return result

    @api.onchange('ori_vendor_id')
    def _onchange_ori_vendor_id(self):
        if self.sudo().ori_vendor_id:
            vars = {
                'currency': self.sudo().ori_vendor_id.currency.id,
                'payment_term': self.sudo().ori_vendor_id.payment_term.id,
                'incoterm': self.sudo().ori_vendor_id.incoterm.id,
                'destination': self.sudo().ori_vendor_id.destination,
                'local_foreign': self.sudo().ori_vendor_id.local_foreign
            }
            self.update(vars)
        return {}

    @api.multi
    def button_to_approve(self):
        # 用户输入校验
        if not utility.is_email(self.buyer_email):
            raise UserError(_(u'Buyer Email必须输入有效的Email！/ Buyer Email is invalid!'))

        # 校验buyer email
        buyer_flag = False
        for user in self.env.ref('oscg_vendor.IAC_buyer_groups').users:
            if self.buyer_email == user.email:
                buyer_flag = True
        if not buyer_flag:
            raise UserError(_(u'Buyer Email不存在，请核实后重新输入！/ Buyer Email doesn\'t exist!'))

        # 检查是否有修改
        change_flag = False
        if self.sudo().ori_vendor_id.currency.id != self.currency.id:
            change_flag = True
        if self.sudo().ori_vendor_id.buyer_email != self.buyer_email:
            change_flag = True
        if self.sudo().ori_vendor_id.payment_term.id != self.payment_term.id:
            change_flag = True
        if self.sudo().ori_vendor_id.incoterm.id != self.incoterm.id:
            change_flag = True
        if self.sudo().ori_vendor_id.destination != self.destination:
            change_flag = True
        if self.sudo().ori_vendor_id.local_foreign != self.local_foreign:
            change_flag = True
        if not change_flag:
            raise UserError(_(u'栏位跟复制原Vendor栏位一样，不能复制！'))

        # 检查copy的vendor各内容都一样的，还在流程中的单子
        same_count = self.search_count([('plant', '=', self.plant.id), ('currency', '=', self.currency.id),
                                      ('buyer_email', '=', self.buyer_email), ('payment_term', '=', self.payment_term.id),
                                      ('incoterm', '=', self.incoterm.id), ('destination', '=', self.destination),
                                      ('local_foreign', '=', self.local_foreign), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error', 'done'))])
        if same_count > 0:
            raise UserError(_(u'Vendor Copy 新厂商栏位都一样的单子已经存在，不能送签！'))

        #if self.sudo().ori_vendor_id.plant.plant_code == 'CP21' and self.plant.plant_code == 'CP21' \
        #        and self.sudo().ori_vendor_id.local_foreign != self.local_foreign:
        #    raise UserError(_(u'Copy CP21 到 CP21 的是 Local Foreign 不能修改！'))

        if not self.sudo().ori_vendor_id.vendor_reg_id.material_ids:
            # 如果division_code没有，就默认一个
            vendor_reg_val = {
                'material_ids': [(0, 0, {'division_code': 99999})]
            }
            self.sudo().ori_vendor_id.vendor_reg_id.write(vendor_reg_val)

        # 调用webflow接口
        biz_object = {
            "vendor_copy_id": self.id,
            "copied_vendor_id": self.sudo().ori_vendor_id.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F03_B", biz_object)
        message = ''
        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签成功'})
            message = u'送签成功'
        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.sudo().ori_vendor_id.name
        return self.env['warning_box'].info(title=title, message=message)

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    def vendor_copy_callback(self,context=None):
        """
        回调函数说明
        供应商复制审核完成
        模型为iac.vendor.copy
        context={"approve_status": True,"data":{"id":1376,}}


        返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
        :param context:
        :return:
        """
        proc_result = False
        proc_ex = []
        model_obj=None
        try:

            # 校验接口入参
            if not context["approve_status"] or not context.get("data") or not context.get("data").get("id"):
                proc_result = False
                proc_ex.append(u"接口调用参数异常")
                _logger(u"接口调用参数异常")
                return proc_result, proc_ex
            else:
                model_obj = self.browse(context.get("data").get("id"))
                if not model_obj.exists():
                    proc_result=False
                    proc_ex.append(u"接口调用参数异常,目标id %s 在 vendor copy 中不存在"%(context.get("data").get("id"),))
                    return proc_result, proc_ex

                #保存调用参数入口现场
                update_vals={
                    "context_str":json.dumps(context),
                    "webflow_number":context["rpc_callback_data"]["EFormNO"],
                }
                webflow_number=context["rpc_callback_data"]["EFormNO"],
                model_obj.write({"context_str":json.dumps(context)})
                self.env.cr.commit()

                #根据返回状态信息进行相应处理
                if context["approve_status"] and context["rpc_callback_data"]["FormStatus"] == "C":
                    model_obj.write({'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 生成Vendor Register
                    new_vendor_reg_vals = {
                        'plant_id': model_obj.plant.id,
                        'currency': model_obj.currency.id,
                        'buyer_email': model_obj.buyer_email.lower(),
                        'vendor_code': '',
                        'state': 'done',
                        'state_msg': '',
                        "webflow_number":webflow_number,
                    }
                    new_vendor_reg_vals = model_obj.ori_vendor_id.vendor_reg_id.copy_data(new_vendor_reg_vals)[0]
                    product_ids = []
                    for product_id in model_obj.ori_vendor_id.vendor_reg_id.product_ids:
                        product_val = {
                            'product_name': product_id.product_name,
                            'product_type': product_id.product_type.id,
                            'product_class': product_id.product_class.id,
                            'brand_name': product_id.brand_name,
                            'capacity_month': product_id.capacity_month,
                            'major_customer': product_id.major_customer
                        }
                        product_ids.append((0, 0, product_val))
                    new_vendor_reg_vals['product_ids'] = product_ids
                    factory_ids = []
                    for factory_id in model_obj.ori_vendor_id.vendor_reg_id.factory_ids:
                        factory_val = {
                            'factory_type': factory_id.factory_type,
                            'factory_name': factory_id.factory_name,
                            'factory_location': factory_id.factory_location,
                            'factory_address': factory_id.factory_address,
                            'main_flag': factory_id.main_flag,
                            'ur_flag': factory_id.ur_flag,
                            'relation': factory_id.relation,
                            'qa_contact': factory_id.qa_contact,
                            'qa_tel': factory_id.qa_tel,
                            'qa_email': factory_id.qa_email
                        }
                        factory_ids.append((0, 0, factory_val))
                    new_vendor_reg_vals['factory_ids'] = factory_ids
                    attachment_ids = []

                    #更新vendor_reg附件信息,复制附件(复制文件并且生成相应的数据),并且更新当前处理vendor附件列表
                    for ori_attachment in model_obj.ori_vendor_id.vendor_reg_id.attachment_ids:
                        #复制附件的文件和数据
                        if not ori_attachment.file_id.exists():
                            continue
                        #复制文件的时候,可能会出现文件链接无效的情况,捕捉异常
                        try:
                            new_file_id=ori_attachment.file_id.copy()
                            attachment_val = {
                                'type': ori_attachment.type.id,
                                'file_id': new_file_id.id,
                                'description': ori_attachment.description,
                                'group': ori_attachment.group,
                                'expiration_date': ori_attachment.expiration_date,
                                'memo': ori_attachment.memo,
                                'approver_id': ori_attachment.approver_id.id
                            }
                            attachment_ids.append((0, 0, attachment_val))
                        except:
                            sys_error=traceback.format_exc()
                            user_error="Copy File Failed,File id is %s ,File Name is %s "%(ori_attachment.file_id.id,ori_attachment.file_id.filename)
                            raise UserError(user_error)

                    new_vendor_reg_vals['attachment_ids'] = attachment_ids
                    material_ids = []
                    for division in model_obj.ori_vendor_id.vendor_reg_id.material_ids:
                        division_val = {
                            'division_code': division.division_code.id,
                            'project': division.project,
                            'material_group': division.material_group.id
                        }
                        material_ids.append((0, 0, division_val))
                    new_vendor_reg_vals['material_ids'] = material_ids
                    new_vendor_reg_obj = self.env['iac.vendor.register'].with_context({"no_check_short_name":True}).create(new_vendor_reg_vals)
                    #补充缺少的附件栏位信息
                    new_vendor_reg_obj.fill_blank_attachment()

                    # 生成Vendor
                    new_vendor_vals = {
                        'plant': model_obj.plant.id,
                        'currency': model_obj.currency.id,
                        'buyer_email': model_obj.buyer_email.lower(),
                        'payment_term': model_obj.payment_term.id,
                        'incoterm': model_obj.incoterm.id,
                        'destination': model_obj.destination,
                        'reason': model_obj.copy_reason,
                        'local_foreign': model_obj.local_foreign,
                        'vendor_code': '',
                        'state': 'to sap',
                        'vendor_type': 'normal',
                        'state_msg': '',
                        "webflow_number":webflow_number,
                    }

                    if model_obj.ori_vendor_id.supplier_company_id.exists():
                        new_vendor_vals["supplier_company_id"]=model_obj.ori_vendor_id.supplier_company_id.id

                    new_vendor_vals = model_obj.ori_vendor_id.copy_data(new_vendor_vals)[0]
                    attachment_ids = []
                    #更新vendor附件信息,复制附件(复制文件并且生成相应的数据),并且更新当前处理vendor附件列表
                    for ori_attachment in model_obj.ori_vendor_id.attachment_ids:
                        #复制附件的文件和数据
                        if not ori_attachment.file_id.exists():
                            continue
                        try:
                            new_file_id=ori_attachment.file_id.copy()
                            attachment_val = {
                                'type': ori_attachment.type.id,
                                'file_id': new_file_id.id,
                                'description': ori_attachment.description,
                                'group': ori_attachment.group,
                                'expiration_date': ori_attachment.expiration_date,
                                'memo': ori_attachment.memo,
                                'approver_id': ori_attachment.approver_id.id
                            }
                            attachment_ids.append((0, 0, attachment_val))
                        except:
                            sys_error=traceback.format_exc()
                            user_error="Copy File Failed,File id is %s ,File Name is %s "%(ori_attachment.file_id.id,ori_attachment.file_id.filename)
                            raise UserError(user_error)
                    new_vendor_vals['attachment_ids'] = attachment_ids

                    new_vendor_vals["vendor_reg_id"]= new_vendor_reg_obj.id
                    new_vendor_vals["supplier_company_id"]=model_obj.ori_vendor_id.supplier_company_id.id
                    self.env.cr.execute("select last_value+1 from iac_vendor_id_seq")
                    pg_result=self.env.cr.fetchall()
                    temp_vendor_code="TMP_CODE_%s"%(pg_result[0][0],)
                    new_vendor_vals["vendor_code"]=temp_vendor_code
                    new_vendor_obj = self.env['iac.vendor'].create(new_vendor_vals)

                    #补充缺少的附件栏位信息
                    new_vendor_obj.fill_blank_attachment()

                    #放置当前vendor 到supplier_company_line中
                    #iac.supplier.company.line
                    if model_obj.ori_vendor_id.supplier_company_id.exists():
                        sc_domain=[('supplier_company_id','=',model_obj.ori_vendor_id.supplier_company_id.id)]
                        sc_domain+=[('vendor_id','=',new_vendor_obj.id)]
                        sc_lines=self.env["iac.supplier.company.line"].sudo().search(sc_domain)
                        if not sc_lines.exists():
                            sc_line_vals={
                                "supplier_company_id":model_obj.ori_vendor_id.supplier_company_id.id,
                                "vendor_id":new_vendor_obj.id,
                            }
                            self.env["iac.supplier.company.line"].sudo().create(sc_line_vals)


                    new_vendor_reg_obj.write({'vendor_id': new_vendor_obj.id})
                    model_obj.write({'new_vendor_reg_id': new_vendor_reg_obj.id, 'new_vendor_id': new_vendor_obj.id})
                    # 更新vendor.material
                    for material in new_vendor_reg_obj.material_ids:
                        material.write({'vendor_id': new_vendor_obj.id})

                    # 调用SAP接口
                    if model_obj.send_to_sap():
                        proc_result = True
                        return proc_result, proc_ex
                    else:
                        proc_result = True
                        proc_ex.append(u'通知SAP失败')
                        return proc_result, proc_ex
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

            #异常处理操作,回滚已经进行的数据写入操作
            self.env.cr.rollback()
            update_vals={
                "state":"callback_error",
                "state_msg":proc_ex,
            }
            model_obj.write(update_vals)

            #不向webflow返回异常信息,代码发生异常odoo自行记录状态和异常信息
            proc_result=True
            proc_ex=[]
            return proc_result, proc_ex

    def send_to_sap(self):
        """
        只能被vendor_copy记录对象调用,单笔记录发送到SAP系统
        """
        vendor = self.new_vendor_id

        try:
            if vendor.state in ('to sap', 'sap error'):
                # 调用SAP接口
                biz_object = {
                    "id": vendor.id,
                    "biz_object_id": vendor.id
                }
                rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                    "iac.interface.rpc"].invoke_web_call_with_log(
                    "ODOO_VENDOR_001", biz_object)
                if rpc_result:
                    #修改vendor_reg 状态
                    vendor_code= rpc_json_data['vendor_code']
                    vendor_reg_vals={
                        'state':'done',
                        'vendor_code':vendor_code,
                        'state_msg': u'通知SAP成功'
                    }
                    vendor_2=self.env["iac.vendor"].browse(vendor.id)
                    if vendor_2.vendor_reg_id.exists():
                        vendor.vendor_reg_id.write(vendor_reg_vals)
                    else:
                        raise UserError("Vendor  %s has no Vendor Register Info"%(vendor_code))

                    # 修改vendor状态
                    vendor.write({'state': 'done',
                                  'state_msg': u'通知SAP成功',
                                  'vendor_code': rpc_json_data['vendor_code']})
                    # 修改vendor copy单子状态
                    self.write({'state': 'done',
                                  'state_msg': u'通知SAP成功'})
                    return True
                else:
                    # 修改vendor状态
                    vendor.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
                    #修改vendor_reg状态
                    vendor_reg_vals={
                        'state':'sap error',
                        'state_msg': u'通知SAP失败,接口日志id为 %s ; 异常信息为 %s' %(log_line_id,exception_log)
                    }
                    vendor.vendor_reg_id.write(vendor_reg_vals)
                    # 修改vendor copy单子状态
                    self.write({'state': 'sap error',
                                 'state_msg': u'通知SAP失败,接口日志id为 %s ; 异常信息为 %s' %(log_line_id,exception_log)
                    })
                    return False
            else:
                self.write({'state': 'done'})
                return True
        except:
            traceback.print_exc()
            vendor.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
            return False


    def button_to_sap(self):
        """
        只能被vendor_copy记录对象调用
        从浏览器端点击按钮触发
        如果状态为sap_error或者 to sap 那么直接调用接口ODOO_VENDOR_001接口同步数据给SAP即可
        如果状态为callback_error 需要重新调用callback函数进行业务处理，生成相应的业务数据后再调用ODOO_VENDOR_001接口
        """
        if self.state in ['to sap', 'sap error']:
            self.send_to_sap()
        elif self.state in ['callback_error']:
            context=json.loads(self.context_str)
            self.sudo().vendor_copy_callback(context)


class IacVendorBlock(models.Model):
    """
    Vendor Block or Unblock
    """
    _name = "iac.vendor.block"
    _order = "id desc"

    plant_id = fields.Many2one('pur.org.data', string="Plant *", index=True)
    material_ids = fields.One2many("iac.vendor.material", "vendor_reg_id", string="Material Lines")
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Vendor *", domain=[('state', 'in', ['done', 'block'])],
                                required=True, index=True)
    is_block = fields.Selection([
        ('block', 'Block'),
        ('unblock', 'Unblock'),
    ], string="Block or Unblock")
    comment = fields.Text(string="Comment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),# webflow拒绝或抽单
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)
    webflow_number = fields.Char(string="Webflow Number", readonly=True)

    @api.model
    def create(self, values):
        vendor_block_ids = self.sudo().search([('vendor_id', '=', values['vendor_id']), ('is_block', '=', values['is_block']), ('state', '=', 'draft')])
        if vendor_block_ids:
            raise ValidationError(_(u'Vendor已经有draft状态单子，请edit并送件！'))

        if values['vendor_id']:
            vendor_id = self.env['iac.vendor'].sudo().browse(values['vendor_id'])
            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].sudo().search(
                [('vendor_id', '=', vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能创建！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].sudo().search(
                [('vendor_reg_id', '=', vendor_id.vendor_reg_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].sudo().search([('vendor_id', '=', vendor_id.id), (
            'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))

        result = super(IacVendorBlock, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if values.get('vendor_id', False):
            vendor_id = self.env['iac.vendor'].sudo().browse(values['vendor_id'])
            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].sudo().search(
                [('vendor_id', '=', vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能修改！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].sudo().search(
                [('vendor_reg_id', '=', vendor_id.vendor_reg_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].sudo().search([('vendor_id', '=', vendor_id.id), (
                'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))

        return super(IacVendorBlock, self).write(values)

    @api.constrains('vendor_id')
    def _check_vendor_id(self):
        for record in self:
            if record.is_block == 'block' and record.vendor_id.state != 'done':
                raise ValidationError(_(u'Vendor不是done状态，不能做block操作！'))
            elif record.is_block == 'unblock' and record.vendor_id.state != 'block':
                raise ValidationError(_(u'Vendor不是block状态，不能做unblock操作！'))
            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = record.env['iac.vendor.block'].search([('vendor_id', '=', record.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise ValidationError(_(u'Vendor已经有block/unblock流程中的单子！'))
            change_basic_ids = record.env['iac.vendor.change.basic'].search([('vendor_reg_id', '=', record.vendor_id.vendor_reg_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise ValidationError(_(u'Vendor已经有change流程中的单子！'))
            change_terms_ids = record.env['iac.vendor.change.terms'].search([('vendor_id', '=', record.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise ValidationError(_(u'Vendor已经有change流程中的单子！'))

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', 'in', ('done', 'block'))]}}
        else:
            return {'domain': {'vendor_id': [('state', 'in', ('done', 'block'))]}}

    @api.multi
    def button_to_approve(self):
        # vendor 状态判断
        if self.is_block == 'block' and self.vendor_id.state != 'done':
            raise UserError(_(u'Vendor不是done状态，不能做block操作！'))
        elif self.is_block == 'unblock' and self.vendor_id.state != 'block':
            raise UserError(_(u'Vendor不是block状态，不能做unblock操作！'))

        # vendor block/unblock/change流程中的不能送签表单
        vendor_block_ids = self.env['iac.vendor.block'].search([('id', '!=', self.id), ('vendor_id', '=', self.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if vendor_block_ids:
            raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能送签！'))
        change_basic_ids = self.env['iac.vendor.change.basic'].search([('vendor_reg_id', '=', self.vendor_id.vendor_reg_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_basic_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))
        change_terms_ids = self.env['iac.vendor.change.terms'].search([('vendor_id', '=', self.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_terms_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))

        if not self.vendor_id.vendor_reg_id.material_ids:
            # 如果division_code没有，就默认一个
            vendor_reg_val = {
                'material_ids': [(0, 0, {'division_code': 99999})]
            }
            self.vendor_id.vendor_reg_id.write(vendor_reg_val)

        # 调用webflow接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F04_B_2", biz_object)

        message = ''
        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签成功'})
            message = u'送签成功'
        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.vendor_id.name
        return self.env['warning_box'].info(title=title, message=message)

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    def vendor_block_unblock_callback(self,context=None):
        """
        回调函数说明
        供应商状态变更审核完成
        模型为 iac.vendor.block
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
                    model_obj.write({'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 调用SAP接口
                    if self.button_to_sap(context.get("data").get("id")):
                        proc_result = True
                        return proc_result, proc_ex
                    else:
                        proc_result = True
                        proc_ex.append(u'通知SAP失败')
                        return proc_result, proc_ex
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

        try:
            biz_object = {
                "id": model_obj.id,
                "block_map": {
                    "block": "0",
                    "unblock": "1"
                },
                "biz_object_id": model_obj.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_VENDOR_004", biz_object)
            if rpc_result:
                model_obj.write({'state': 'done', 'state_msg': u'通知SAP成功'})

                # 更新vendor状态
                if model_obj.is_block == 'block':
                    model_obj.vendor_id.write({'state': 'block'})
                    model_obj.vendor_id.vendor_reg_id.write({'state': 'block'})
                else:
                    model_obj.vendor_id.write({'state': 'done'})
                    model_obj.vendor_id.vendor_reg_id.write({'state': 'done'})

                # 通知相关人员厂商修改成功
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_block_sap_buyer_email')

                return True
            else:
                model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
                return False
        except:
            traceback.print_exc()
            model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
            return False

class IacVendorChangeBasic(models.Model):
    """
    Vendor Change Basic Bank info
    """
    _name = "iac.vendor.change.basic"
    _order = "id desc"

    plant_id = fields.Many2one('pur.org.data', string="Plant *")
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Change Vendor", domain=[('state', '=', 'done')],
                                    required=True, index=True)

    # 基本信息
    name1_cn = fields.Char(string="Company Name 1(Chinese)*")
    name2_cn = fields.Char(string="Company Name 2(Chinese)*")
    name1_en = fields.Char(string="Company Name 1(English)*")
    name2_en = fields.Char(string="Company Name 2(English)*")
    short_name = fields.Char(string="Supplier Short Name(Only English)*")
    contact_person = fields.Char(string="Contact Person *")
    company_telephone1 = fields.Char(string="Company Tel. 1 *")
    company_telephone2 = fields.Char(string="Company Tel. 2")
    company_fax = fields.Char(string="Company Fax *")
    buyer_email = fields.Char(string="Buyer email *")
    sales_email = fields.Char(string="Contact email *")
    vat_number = fields.Char(string="VAT Number(Taiwan area supplier only)")
    address_street = fields.Char(string="Address - Street *")
    address_city = fields.Char(string="Address - City *")
    address_district = fields.Char(string="Address - District *")
    address_pobox = fields.Char(string="Address - P.O. Box")
    address_postalcode = fields.Char(string="Address - Postal Code *")
    address_country = fields.Many2one('res.country', string="Address - Country Code *", domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])
    currency = fields.Many2one('res.currency', string="Currency *")

    # 银行信息
    bank_name = fields.Char(string="Bank Name*")
    branch_name = fields.Char(string="Bank Branch Name")
    account_number = fields.Char(string="Bank Account No.*")
    account_number_1 = fields.Char(string="Bank Account No First 16", compute='_taken_account_number_1')
    account_number_2 = fields.Char(string="Bank Account No Last", compute='_taken_account_number_2')
    swift_code = fields.Char(string="SWIFT Code*")
    transfer_number = fields.Char(string="Bank Transfer Number(TaiwanSupplier Must Specify)")
    bank_street = fields.Char(string="Bank - Street*")
    bank_city = fields.Char(string="Bank - City*")
    bank_country = fields.Many2one('res.country', string="Bank - Country Code *", domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])
    attachment_ids = fields.One2many("iac.vendor.change.attachment", "change_id", string="Attachment Lines")

    state = fields.Selection([
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('submit', 'Submit'),  # vendor编辑好提交buyer review
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),# webflow拒绝或抽单
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)
    webflow_number = fields.Char(string="Webflow Number", readonly=True)
    effective_date = fields.Datetime(string="Effective Date*")# 新资料生效日期
    finance = fields.Many2one('res.partner', string="Finance")# 财务审核人

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_reg_id': ['&', ('plant_id', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_reg_id': [('state', '=', 'done')]}}

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

    @api.onchange('vendor_reg_id')
    def _onchange_vendor_reg_id(self):
        if self.vendor_reg_id:
            basic_vars = {
                'name1_cn': self.vendor_reg_id.name1_cn,
                'name2_cn': self.vendor_reg_id.name2_cn,
                'name1_en': self.vendor_reg_id.name1_en,
                'name2_en': self.vendor_reg_id.name2_en,
                'short_name': self.vendor_reg_id.short_name,
                'contact_person': self.vendor_reg_id.contact_person,
                'company_telephone1': self.vendor_reg_id.company_telephone1,
                'company_fax': self.vendor_reg_id.company_fax,
                'buyer_email': self.vendor_reg_id.buyer_email,
                'sales_email': self.vendor_reg_id.sales_email,
                'vat_number': self.vendor_reg_id.vat_number,
                'address_street': self.vendor_reg_id.address_street,
                'address_city': self.vendor_reg_id.address_city,
                'address_district': self.vendor_reg_id.address_district,
                'address_pobox': self.vendor_reg_id.address_pobox,
                'address_postalcode': self.vendor_reg_id.address_postalcode,
                'address_country': self.vendor_reg_id.address_country.id,
                'currency': self.vendor_reg_id.currency.id
            }
            self.update(basic_vars)

            # Attachment 列出Vendor Bank Attachment
            attachment_ids = []
            for attachment in self.vendor_reg_id.vendor_id.attachment_ids:
                change_attachment=self.env["iac.vendor.change.attachment"].browse(attachment.id)
                if not change_attachment.change_id.exists():
                    change_attachment_vals={
                        "change_id":self._origin.id
                    }
                    change_attachment.write(change_attachment_vals)
                attachment_ids.append((4, attachment.id))
                #attachment_ids.append((0, 0, {'vendor_id':self.vendor_reg_id.vendor_id.id,'type': attachment.type.id, 'group': 'bank','file_id':attachment.file_id.id}))

            bank_vars = {
                'bank_name': self.vendor_reg_id.vendor_id.bank_name,
                'branch_name': self.vendor_reg_id.vendor_id.branch_name,
                'account_number': self.vendor_reg_id.vendor_id.account_number,
                'swift_code': self.vendor_reg_id.vendor_id.swift_code,
                'transfer_number': self.vendor_reg_id.vendor_id.transfer_number,
                'bank_street': self.vendor_reg_id.vendor_id.bank_street,
                'bank_city': self.vendor_reg_id.vendor_id.bank_city,
                'bank_country': self.vendor_reg_id.vendor_id.bank_country.id,
                'attachment_ids': attachment_ids
            }
            self.update(bank_vars)

        return {}

    @api.model
    def create(self, values):
        if values['vendor_reg_id']:
            vendor_reg_id = self.env['iac.vendor.register'].sudo().browse(values['vendor_reg_id'])
            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].sudo().search([('vendor_id', '=', vendor_reg_id.vendor_id.id), (
            'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能创建！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].sudo().search(
                [('id', '!=', self.id), ('vendor_reg_id', '=', vendor_reg_id.id),
                 ('state', 'in', ('draft','to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].sudo().search(
                [('vendor_id', '=', vendor_reg_id.vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))

            values['short_name'] = vendor_reg_id.short_name
            values['currency'] = vendor_reg_id.currency.id
        else:
            raise UserError(_(u'请选择Vendor！/ Please select Vendor!'))
        if "attachment_ids" in values:
            attachment_ids=values["attachment_ids"]
            values.pop("attachment_ids")
        vendor_change_rec=super(IacVendorChangeBasic, self).create(values)

        #更新change_id到相应的字段
        for attachment_item in attachment_ids:
            attachment_rec=self.env["iac.vendor.change.attachment"].browse(attachment_item[1])
            attachment_rec.write({"change_id":vendor_change_rec.id})

        return vendor_change_rec

    @api.multi
    def write(self, values):
        if values.get('vendor_reg_id', False):
            vendor_reg_id = self.env['iac.vendor.register'].sudo().browse(values.get('vendor_reg_id', False))

            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].sudo().search([('vendor_id', '=', vendor_reg_id.vendor_id.id), (
                'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能修改！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].sudo().search(
                [('id', '!=', self.id), ('vendor_reg_id', '=', vendor_reg_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].sudo().search(
                [('vendor_id', '=', vendor_reg_id.vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))

        return super(IacVendorChangeBasic, self).write(values)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # 根据角色过滤数据
        if self.env.user.id != SUPERUSER_ID:
            if self.env.user in self.env.ref('oscg_vendor.IAC_vendor_groups').users:
                if self.env.user.vendor_id:
                    args += [('vendor_reg_id', '=', self.env.user.vendor_id.vendor_reg_id.id)]

        return super(IacVendorChangeBasic, self).search(args, offset, limit, order, count=count)

    @api.multi
    def button_confirm(self):
        # 必填项校验
        #if not self.name1_cn:
        #    raise UserError(_(u'Company Name 1(Chinese)不能为空！/ Company Name 1(Chinese) is required!'))
        #if not self.name1_en or utility.contain_zh(self.name1_en):
        #    raise UserError(_(u'Company Name 1(English)不能为空且不能包含中文！/ Company Name 1(English) is required and Chinese character is not allowed!'))
        #if not self.name2_cn:
        #    raise UserError(_(u'Company Name 2(Chinese)不能为空！/ Company Name 2(Chinese) is required!'))
        #if not self.name2_en or utility.contain_zh(self.name2_en):
        #    raise UserError(_(u'Company Name 2(English)不能为空且不能包含中文！'))
        #if not self.short_name or utility.contain_zh(self.short_name):
        #    raise UserError(_(u'Supplier Short Name(Only English)不能为空且不能包含中文！/ Supplier Short Name(Only English) is required and Chinese character is not allowed!'))
        if not self.contact_person:
            raise UserError(_(u'Contact Person不能为空！/ Contact Person is required!'))
        if not self.company_telephone1 or not utility.is_phone(self.company_telephone1):
            raise UserError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))
        if not self.company_fax or not utility.is_phone(self.company_fax):
            raise UserError(_(u'Company Fax必须填写有效的FAX！/ Company Fax is invalid!'))
        if not self.buyer_email or not utility.is_email(self.buyer_email):
            raise UserError(_(u'Buyer email必须填写有效的Email！'))
        # 校验buyer email
        buyer_flag = False
        for user in self.env.ref('oscg_vendor.IAC_buyer_groups').users:
            if self.buyer_email == user.email:
                buyer_flag = True
        if not buyer_flag:
            raise UserError(_(u'Buyer Email不存在，请核实后重新输入！/ Buyer Email doesn\'t exist!'))

        if not self.sales_email or not utility.is_email(self.sales_email):
            raise UserError(_(u'Contact email必须填写有效Email！/ Contact email is invalid!'))
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
        if not self.bank_name:
            raise UserError(_(u'Bank Name不能为空！/ Bank Name is required!'))
        if not self.branch_name:
            raise UserError(_(u'Bank Branch Name不能为空！/ Bank Branch Name is required!'))
        if not self.account_number:
            raise UserError(_(u'Bank Account No.不能为空！/ Bank Account No. is required!'))
        if not self.swift_code:
            raise UserError(_(u'SWIFT Code不能为空！/ SWIFT Code is required!'))
        if not self.bank_city:
            raise UserError(_(u'Bank City不能为空！/ Bank City is required!'))
        if self.address_country.code != 'TW' and self.vat_number!=False:
            raise UserError(_(u'非台湾不能填写VAT Number！/ VAT Number is required for none Taiwanese Vendor!'))
        if self.address_country.code == 'TW' and not self.vat_number:
            raise UserError(_(u'台湾必须填写VAT Number！/ VAT Number is required for Taiwanese Vendor!'))
        if self.address_country.code == 'TW' and not self.transfer_number:
            raise UserError(_(u'Bank Transfer Number(TaiwanSupplier Must Specify)不能为空！'))
        if not self.bank_street:
            raise UserError(_(u'Bank - Street不能为空！/ Bank-Street is required!'))
        if not self.bank_country:
            raise UserError(_(u'Bank - Country Code不能为空！/ Bank-Country Code is required!'))
        # 检查附件
        if self.vendor_reg_id.vendor_id.vendor_type in ["normal"]:
            if not self.attachment_ids:
                raise UserError(_(u'Attachment必须上传！/ Attachment is required to upload!'))
            else:

                for attachment_id in self.attachment_ids:
                    if (not attachment_id.file_id) :
                        domain=[('type','=',attachment_id.type.id)]
                        domain+=[('is_required','=',True)]
                        config_rec=self.env["iac.attachment.config"].search(domain,limit=1)
                        if config_rec.exists():
                            raise UserError(_(u'Attachment必须上传！/ Attachment type is %s')%(attachment_id.type.name,))

        change_flag = False
        if self.vendor_reg_id.name1_cn != self.name1_cn:
            change_flag = True
        if self.vendor_reg_id.name1_en != self.name1_en:
            change_flag = True
        if self.vendor_reg_id.name2_cn != self.name2_cn:
            change_flag = True
        if self.vendor_reg_id.name2_en != self.name2_en:
            change_flag = True
        if self.vendor_reg_id.short_name != self.short_name:
            change_flag = True
        if self.vendor_reg_id.contact_person != self.contact_person:
            change_flag = True
        if self.vendor_reg_id.company_telephone1 != self.company_telephone1:
            change_flag = True
        if self.vendor_reg_id.company_fax != self.company_fax:
            change_flag = True
        if self.vendor_reg_id.buyer_email != self.buyer_email:
            change_flag = True
        if self.vendor_reg_id.sales_email != self.sales_email:
            change_flag = True
        if self.vendor_reg_id.address_street != self.address_street:
            change_flag = True
        if self.vendor_reg_id.address_city != self.address_city:
            change_flag = True
        if self.vendor_reg_id.address_district != self.address_district:
            change_flag = True
        if self.vendor_reg_id.address_postalcode != self.address_postalcode:
            change_flag = True
        if self.vendor_reg_id.address_country != self.address_country.id:
            change_flag = True
        if self.vendor_reg_id.currency != self.currency.id:
            change_flag = True
        if self.vendor_reg_id.vendor_id.bank_name != self.bank_name:
            change_flag = True
        if self.vendor_reg_id.vendor_id.branch_name != self.branch_name:
            change_flag = True
        if self.vendor_reg_id.vendor_id.account_number != self.account_number:
            change_flag = True
        if self.vendor_reg_id.vendor_id.swift_code != self.swift_code:
            change_flag = True
        if self.vendor_reg_id.vendor_id.transfer_number != self.transfer_number:
            change_flag = True
        if self.vendor_reg_id.vendor_id.bank_street != self.bank_street:
            change_flag = True
        if self.vendor_reg_id.vendor_id.bank_country.id != self.bank_country:
            change_flag = True
        if not change_flag:
            raise UserError(_(u'栏位都未修改不能保存！'))

        if self.state == 'draft':
            self.write({'state': 'submit'})
            try:
                # 给buyer和supplier分别发邮件
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_change_basic_email_vendor')
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_change_basic_email_buyer')
            except:
                traceback.print_exc()
                return False

        return True

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    @api.multi
    def button_reject(self):
        if self.state == 'submit':
            self.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        # vendor block/unblock/change流程中的不能送签表单
        vendor_block_ids = self.env['iac.vendor.block'].search([('vendor_id', '=', self.vendor_reg_id.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if vendor_block_ids:
            raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能送签！'))
        change_basic_ids = self.env['iac.vendor.change.basic'].search([('id', '!=', self.id), ('vendor_reg_id', '=', self.vendor_reg_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_basic_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))
        change_terms_ids = self.env['iac.vendor.change.terms'].search([('vendor_id', '=', self.vendor_reg_id.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_terms_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))




        #查询得到缺少的附件栏位信息
        self.env.cr.execute("""
            SELECT
                iac.\"type\" \"attachment_type_id\",
                iat.\"name\",
                iat.description,
                iac.model_obj attachment_cate,
                iac.is_required,
                iac.is_displayed,
                iac.\"sequence\"
            FROM
                iac_attachment_config iac,
                iac_attachment_type iat
            WHERE
                iac.\"type\" = iat. ID
            AND iac.model_obj = 'vendor_bank'
            AND NOT EXISTS (
                SELECT
                    1
                FROM
                    iac_vendor_attachment iva
                WHERE
                    iva.change_id = %s
                AND iva.\"type\" = iac.\"type\"
            )
            ORDER BY
                iac.model_obj,
                iac.\"sequence\"
        """,(self.id,))

        pg_result=self.env.cr.fetchall()
        #遍历全部缺少的栏位进行补充操作,缺少必须的文件会提示错误信息
        for attachment_type_id,attachment_type_name,attachment_type_desc,attachment_type_cate,\
            is_required,is_displayed,sequence in pg_result:
            if is_required:
                raise UserError(_(u'%s文件必须上传！') % (attachment_type_name,))

        # 检查附件,检查是否指定了签核人
        if self.vendor_reg_id.vendor_id.vendor_type in ["normal"]:
            if self.attachment_ids:
                for attachment_id in self.attachment_ids:
                    if (attachment_id.type.special_approved==True) and (not attachment_id.approver_id.exists()):
                        raise UserError(_(u'Attachment type is %s must set a approver !')%(attachment_id.type.name,))
            else:
                raise UserError(_(u'Attachment必须上传！/ Attachment is required to upload!'))

        if not self.vendor_reg_id.material_ids:
            # 如果division_code没有，就默认一个
            vendor_reg_val = {
                'material_ids': [(0, 0, {'division_code': 99999})]
            }
            self.vendor_reg_id.write(vendor_reg_val)

        # 调用webflow接口
        effective_date = time.strftime('%Y/%m/%d %H:%M:%S', time.strptime(self.effective_date, '%Y-%m-%d %H:%M:%S'))
        biz_object = {
            "vendor_change_id": self.id,
            "vendor_register_id": self.vendor_reg_id.id,
            "biz_object_id": self.id,
            "effectvie_date": effective_date
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F04_B_1", biz_object)

        message = ''
        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签成功'})
            message = u'送签成功'

        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.name1_cn
        return self.env['warning_box'].info(title=title, message=message)

    def vendor_change_basic_callback(self, context=None):
        """
        回调函数说明
        供应商修改基本资料审核完成
        模型为iac.vendor.change.basic
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
                    model_obj.write({'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 定时任务会调用SAP接口，这里直接返回
                    self.cron_vendor_change_basic()
                    proc_result = True
                    return proc_result, proc_ex
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
        if model_obj.effective_date and fields.Datetime.from_string(model_obj.effective_date) <= datetime.today():
            biz_object = {
                "id": model_obj.id,
                "biz_object_id": model_obj.id
            }
            rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                "iac.interface.rpc"].invoke_web_call_with_log(
                "ODOO_VENDOR_003", biz_object)
            if rpc_result:
                model_obj.write({'state': 'done', 'state_msg': u'通知SAP成功'})

                # 更新vendor_reg basic资料、vendor bank资料
                basic_vars = {
                    'name1_cn': model_obj.name1_cn,
                    'name2_cn': model_obj.name2_cn,
                    'name1_en': model_obj.name1_en,
                    'name2_en': model_obj.name2_en,
                    'contact_person': model_obj.contact_person,
                    'company_telephone1': model_obj.company_telephone1,
                    'company_fax': model_obj.company_fax,
                    'buyer_email': model_obj.buyer_email,
                    'sales_email': model_obj.sales_email,
                    'vat_number': model_obj.vat_number,
                    'address_street': model_obj.address_street,
                    'address_city': model_obj.address_city,
                    'address_district': model_obj.address_district,
                    'address_pobox': model_obj.address_pobox,
                    'address_postalcode': model_obj.address_postalcode,
                    'address_country': model_obj.address_country.id
                }
                model_obj.vendor_reg_id.write(basic_vars)

                bank_vars = {
                    'bank_name': model_obj.bank_name,
                    'branch_name': model_obj.branch_name,
                    'account_number': model_obj.account_number,
                    'swift_code': model_obj.swift_code,
                    'transfer_number': model_obj.transfer_number,
                    'bank_street': model_obj.bank_street,
                    'bank_country': model_obj.bank_country.id
                }
                model_obj.vendor_reg_id.vendor_id.write(bank_vars)

                # Bank Attachment 用change时上传的Attachment更新Vendor Bank Info
                try:
                    for attachment_id in model_obj.vendor_reg_id.vendor_id.attachment_ids:
                        for doc_id in model_obj.attachment_ids:
                            if attachment_id.type.id == doc_id.type.id:
                                if doc_id.file_id:
                                    attachment_id.write({"file_id":doc_id.file_id})
                                    #attachment_id.file_id.write({'directory': doc_id.file_id.directory.id, 'filename': doc_id.file_id.filename,
                                    #                         'file': doc_id.file_id.file, 'file_extension': doc_id.file_id.file_extension})
                except:
                    traceback.print_exc()
                    error_info=traceback.format_exc()
                    raise UserError("Fail to update Vendor Register Attachment,system err info is %s" %(error_info,))

                # Vendor/Buyer change基本资料修改SAP成功之后给buyer发邮件
                utility.send_to_email(self, self.id, 'oscg_vendor.vendor_change_basic_sap_email_buyer')
                return True
            else:
                model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
                return False
        else:
            model_obj.write({'state_msg': u'未到生效日期，未通知SAP'})
            return False


    def cron_vendor_change_basic(self):
        _logger.debug(u'定时任务启动，开始Vendor Change Basic生效日期...')

        for change in self.env['iac.vendor.change.basic'].search([('state', '=', 'to sap'),
                                                                  ('effective_date', '<=', fields.Datetime.to_string(datetime.today()))]):
            self.button_to_sap(change.id)

class IacVendorChangeMaster(models.Model):
    """
    Vendor Change Master
    """
    _name = "iac.vendor.change.master"
    _order = "id desc"

    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Change Vendor", domain=[('state', '=', 'done')], index=True)

    # Vendor Master Data
    rma_terms = fields.Selection(string="RMA Terms *", selection='_selection_rmaterms')
    it_level = fields.Selection(string="Vendor IT Support Level *", selection='_selection_itlevel')
    vmi_supplier = fields.Selection([("yes", "Yes"), ("no", "No")], string="VMI Supplier*")
    vmi_due = fields.Char(string="VMI Due In Week*")
    si_supplier = fields.Selection([("yes", "Yes"), ("no", "No")], string="SI Supplier*")
    import_required = fields.Selection([("yes", "Yes"), ("no", "No")], string="Import Data Required*")

    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('done', 'Done'),  # 已完成状态
        ('cancel', 'Cancelled')  # 已取消状态
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)

    @api.model
    def _selection_itlevel(self):
        res_type = []
        level_list = self.env['ir.config_parameter'].search([('key', 'like', 'itlevel_')])
        for item in level_list:
            res_type.append((item.key[8:], _(item.value)))

        return res_type

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_id': [('state', '=', 'done')]}}

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            vars = {
                'rma_terms': self.vendor_id.rma_terms,
                'it_level': self.vendor_id.it_level,
                'vmi_supplier': self.vendor_id.vmi_supplier,
                'vmi_due': self.vendor_id.vmi_due,
                'si_supplier': self.vendor_id.si_supplier,
                'import_required': self.vendor_id.import_required
            }
            self.update(vars)

        return {}

    @api.multi
    def button_confirm(self):
        # 校验用户输入
        if not self.rma_terms:
            raise UserError(_(u'RMA Terms不能为空！/ RMA Terms are required!'))
        if not self.it_level:
            raise UserError(_(u'Vendor IT Support Level不能为空！'))
        if not self.vmi_supplier:
            raise UserError(_(u'VMI Supplier不能为空！'))
        if not self.vmi_due:
            raise UserError(_(u'VMI Due In Week不能为空！'))
        if not self.si_supplier:
            raise UserError(_(u'SI Supplier不能为空！/ SI Supplier is required!'))
        if not self.import_required:
            raise UserError(_(u'Import Data Required不能为空！'))

        change_flag = False
        if self.rma_terms != self.vendor_id.rma_terms:
            change_flag = True
        if self.it_level != self.vendor_id.it_level:
            change_flag = True
        if self.vmi_supplier != self.vendor_id.vmi_supplier:
            change_flag = True
        if self.vmi_due != self.vendor_id.vmi_due:
            change_flag = True
        if self.si_supplier != self.vendor_id.si_supplier:
            change_flag = True
        if self.import_required != self.vendor_id.import_required:
            change_flag = True
        if not change_flag:
            raise UserError(_(u'栏位都未修改不能提交！'))

        # 无需签核直接变更vendor
        vals = {
            'rma_terms': self.rma_terms,
            'it_level': self.it_level,
            'vmi_supplier': self.vmi_supplier,
            'vmi_due': self.vmi_due,
            'si_supplier': self.si_supplier,
            'import_required': self.import_required
        }
        self.vendor_id.write(vals)
        self.write({'state': 'done', 'state_msg': u'修改成功'})

        return self.env['warning_box'].info(title=u"提示信息", message=u"修改成功！")

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    @api.model
    def _selection_rmaterms(self):
        res_type = []
        term_list = self.env['ir.config_parameter'].search([('key', 'like', 'rmaterms_')])
        for item in term_list:
            res_type.append((item.key[9:], _(item.value)))

        return res_type

    @api.model
    def _selection_itlevel(self):
        res_type = []
        level_list = self.env['ir.config_parameter'].search([('key', 'like', 'itlevel_')])
        for item in level_list:
            res_type.append((item.key[8:], _(item.value)))

        return res_type

class IacVendorChangeTerms(models.Model):
    """
    Vendor Change Terms
    """
    _name = "iac.vendor.change.terms"
    _order = "id desc"

    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Change Vendor", domain=[('state', '=', 'done')],
                                required=True, index=True)

    # Payment Terms and Incoterms
    payment_term = fields.Many2one('payment.term', string='Payment Term*')
    incoterm = fields.Many2one('incoterm', string='Incoterm*')
    destination = fields.Char(string="Destination*")
    change_reason = fields.Text(string="Change Reason*")
    contract_file = fields.Many2one('muk_dms.file', string="Sub Contract File")
    file_description = fields.Char(string="Contract File Description")  # 文件描述信息
    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('to approve', 'To Approve'),  # buyer review后提交webflow签核，送签
        ('unapproved', 'Unapproved'),# webflow拒绝或抽单
        ('to sap', 'To SAP'), # webflow签核通过，call sap
        ('sap error', 'SAP Error'),  # CALL SAP失败
        ('done', 'Done'),  # 已正常完成
        ('cancel', 'Cancelled'), # 表单取消
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)
    webflow_number = fields.Char(string="Webflow Number", readonly=True)
    effective_date = fields.Date(string="Effective Date*")  # 新资料生效日期

    ori_payment_term = fields.Many2one('payment.term', string='Ori Payment Term*')
    ori_incoterm = fields.Many2one('incoterm', string='Ori Incoterm*')
    ori_destination = fields.Char(string="Ori Destination*")

    @api.model
    def create(self, values):
        if values['vendor_id']:
            vendor_id = self.env['iac.vendor'].sudo().browse(values['vendor_id'])
            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].sudo().search([('vendor_id', '=', vendor_id.id), (
                'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能创建！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].sudo().search(
                [('id', '!=', self.id), ('vendor_reg_id', '=', vendor_id.vendor_reg_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].sudo().search(
                [('vendor_id', '=', vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能创建！'))
        else:
            raise UserError(_(u'请选择Vendor！/ Please select Vendor!'))

        create_result=super(IacVendorChangeTerms, self).create(values)
        update_vals={
            "ori_incoterm":create_result.vendor_id.incoterm.id,
            "ori_payment_term":create_result.vendor_id.payment_term.id,
            "ori_destination":create_result.vendor_id.destination,
        }
        super(IacVendorChangeTerms, create_result).write(update_vals)
        return create_result


    @api.multi
    def write(self, values):
        if values.get('vendor_id', False):
            vendor_id = self.env['iac.vendor'].browse(values.get('vendor_id', False))

            # vendor block/unblock/change流程中的不能送签表单
            vendor_block_ids = self.env['iac.vendor.block'].search([('vendor_id', '=', vendor_id.id), (
                'state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if vendor_block_ids:
                raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能修改！'))
            change_basic_ids = self.env['iac.vendor.change.basic'].search(
                [('id', '!=', self.id), ('vendor_reg_id', '=', vendor_id.vendor_reg_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_basic_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))
            change_terms_ids = self.env['iac.vendor.change.terms'].search(
                [('vendor_id', '=', vendor_id.id),
                 ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
            if change_terms_ids:
                raise UserError(_(u'Vendor已经有change流程中的单子，不能修改！'))

        return super(IacVendorChangeTerms, self).write(values)

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_id': [('state', '=', 'done')]}}

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            vars = {
                'payment_term': self.vendor_id.payment_term.id,
                'incoterm': self.vendor_id.incoterm.id,
                'destination': self.vendor_id.destination,
                'file_description': self.file_description
            }
            self.update(vars)

        return {}

    @api.multi
    def button_to_approve(self):
        # 校验用户输入
        if not self.payment_term:
            raise UserError(_(u'Payment Term不能为空！/ Payment Term is required!'))
        if not self.incoterm:
            raise UserError(_(u'Incoterm不能为空！'))
        if not self.destination:
            raise UserError(_(u'Destination不能为空！/ Destination is required!'))
        if not self.change_reason:
            raise UserError(_(u'Change Reason不能为空！/ Change Reason is required!'))
        if not self.contract_file:
            raise UserError(_(u'Sub Contract File不能为空！'))

        # 未修改payment_term/incoterm/destination不能送签
        if self.payment_term == self.vendor_id.payment_term and self.incoterm == self.vendor_id.incoterm and self.destination == self.vendor_id.destination:
            raise UserError(_(u'Payment term、Incoterm, Destination没有发生任何改变，不能送签！'))

        # vendor block/unblock/change流程中的不能送签表单
        vendor_block_ids = self.env['iac.vendor.block'].search([('vendor_id', '=', self.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if vendor_block_ids:
            raise UserError(_(u'Vendor已经有block/unblock流程中的单子，不能送签！'))
        change_basic_ids = self.env['iac.vendor.change.basic'].search([('vendor_reg_id', '=', self.vendor_id.vendor_reg_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_basic_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))
        change_terms_ids = self.env['iac.vendor.change.terms'].search([('id', '!=', self.id), ('vendor_id', '=', self.vendor_id.id), ('state', 'in', ('to approve', 'unapproved', 'to sap', 'sap error'))])
        if change_terms_ids:
            raise UserError(_(u'Vendor已经有change流程中的单子，不能送签！'))

        if not self.vendor_id.vendor_reg_id.material_ids:
            # 如果division_code没有，就默认一个
            vendor_reg_val = {
                'material_ids': [(0, 0, {'division_code': 99999})]
            }
            self.vendor_id.vendor_reg_id.write(vendor_reg_val)

        # 调用webflow接口
        biz_object = {
            "id": self.id,
            "biz_object_id": self.id,
            "file_description": self.file_description
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env["iac.interface.rpc"].invoke_web_call_with_log(
            "F04_B_3", biz_object)

        message = ''
        if rpc_result:
            self.write({'state': 'to approve', 'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'webflow送签成功'})
            message = u'送签成功'
        else:
            self.write({'webflow_number': rpc_json_data.get('EFormNO'), 'state_msg': u'webflow送签失败'})
            message = u'送签失败'

        title = _("Tips for %s") % self.vendor_id.name
        return self.env['warning_box'].info(title=title, message=message)

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

    def vendor_change_payment_incoterm_callback(self, context=None):
        """
        回调函数说明
        采购员修改支付信息审核完成
        模型为 iac.vendor.change.terms
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
                    model_obj.write({'state': 'to sap', 'state_msg': u'webflow(%s)签核通过' % context["rpc_callback_data"]["EFormNO"]})

                    # 定时任务会调用SAP接口，这里直接返回
                    self.cron_vendor_change_terms()
                    proc_result = True
                    return proc_result, proc_ex
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

        try:
            # 调用SAP接口
            if model_obj.effective_date and fields.Datetime.from_string(model_obj.effective_date) <= datetime.today():
                biz_object = {
                    "id": model_obj.id,
                    "biz_object_id": model_obj.id
                }
                rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                    "iac.interface.rpc"].invoke_web_call_with_log(
                    "ODOO_VENDOR_003_02", biz_object)
                if rpc_result:
                    model_obj.write({'state': 'done', 'state_msg': u'通知SAP成功'})

                    # 更新vendor资料
                    vars = {
                        'payment_term': model_obj.payment_term.id,
                        'incoterm': model_obj.incoterm.id,
                        'destination': model_obj.destination,
                        #'purchase_contract': model_obj.contract_file.id
                    }
                    model_obj.vendor_id.write(vars)
                    # 更新IAC VENDOR ATTACHMENT資料
                    att_type = self.env['iac.attachment.type'].search([('name', '=', 'A16')])
                    if att_type:
                        iac_vendor_att = self.env['iac.vendor.attachment'].search([
                                                                            ('vendor_id', '=', model_obj.vendor_id.id),
                                                                            ('type', '=', att_type.id)
                                                                        ])
                        if iac_vendor_att:
                            vars1 = {
                                'file_id': model_obj.contract_file.id
                            }
                            iac_vendor_att.write(vars1)
                    return True
                else:
                    model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
                    return False
            else:
                model_obj.write({'state_msg': u'未到生效日期，未通知SAP'})
                return False
        except:
            traceback.print_exc()
            model_obj.write({'state': 'sap error', 'state_msg': u'通知SAP失败'})
            return False

    def cron_vendor_change_terms(self):
        _logger.debug(u'定时任务启动，开始Vendor Change Terms生效日期...')

        for change in self.env['iac.vendor.change.terms'].search([('state', '=', 'to sap'),
                                                                  ('effective_date', '<=', fields.Datetime.to_string(datetime.today()))]):
            self.button_to_sap(change.id)

class IacVendorChangeManufacture(models.Model):
    """
    Vendor Change Manufacture
    """
    _name = "iac.vendor.change.manufacture"
    _order = "id desc"

    plant_id = fields.Many2one('pur.org.data', string="Plant", index=True)
    vendor_reg_id = fields.Many2one('iac.vendor.register', string="Change Vendor", domain=[('state', '=', 'done')], index=True)

    # 基本信息中manufacture
    name1_cn = fields.Char(string="Company Name 1(Chinese)*")
    name1_en = fields.Char(string="Company Name 1(English)*")
    short_name = fields.Char(string="Supplier Short Name(Only English)*")
    contact_person = fields.Char(string="Contact Person *")
    company_telephone1 = fields.Char(string="Company Tel. 1 *")
    company_fax = fields.Char(string="Company Fax *")
    sales_email = fields.Char(string="Contact email *")
    address_street = fields.Char(string="Address - Street *")
    address_city = fields.Char(string="Address - City *")
    address_district = fields.Char(string="Address - District *")
    address_postalcode = fields.Char(string="Address - Postal Code *")
    address_country = fields.Many2one('res.country', string="Address - Country Code *", domain=['&', ('show_in_list', '=', 'Y'), ('sh_import', '=', 'N')])

    state = fields.Selection([
        ('draft', 'Draft'),  # buyer自己编辑保存的状态
        ('done', 'Done'),  # 已完成状态
        ('cancel', 'Cancelled')  # 已取消状态
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    state_msg = fields.Char(string="Status Message", readonly=True)

    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.plant_id:
            return {'domain': {'vendor_reg_id': ['&', ('plant', '=', self.plant_id.id),
                                             ('state', '=', 'done')]}}
        else:
            return {'domain': {'vendor_reg_id': [('state', '=', 'done')]}}

    @api.onchange('vendor_reg_id')
    def _onchange_vendor_reg_id(self):
        if self.vendor_reg_id:
            vars = {
                'name1_cn': self.vendor_reg_id.name1_cn,
                'name1_en': self.vendor_reg_id.name1_en,
                'short_name': self.vendor_reg_id.short_name,
                'contact_person': self.vendor_reg_id.contact_person,
                'company_telephone1': self.vendor_reg_id.company_telephone1,
                'company_fax': self.vendor_reg_id.company_fax,
                'sales_email': self.vendor_reg_id.sales_email,
                'address_street': self.vendor_reg_id.address_street,
                'address_city': self.vendor_reg_id.address_city,
                'address_district': self.vendor_reg_id.address_district,
                'address_postalcode': self.vendor_reg_id.address_postalcode,
                'address_country': self.vendor_reg_id.address_country.id
            }
            self.update(vars)

        return {}

    @api.multi
    def button_confirm(self):
        # 校验用户输入
        if not self.name1_cn:
            raise UserError(_(u'Company Name 1(Chinese)不能为空！/ Company Name 1(Chinese) is required!'))
        if not self.name1_en or utility.contain_zh(self.name1_en):
            raise UserError(_(u'Company Name 1(English)不能为空且不能包含中文！/ Company Name 1(English) is required and Chinese character is not allowed!'))
        if not self.short_name or utility.contain_zh(self.short_name):
            raise UserError(_(u'Supplier Short Name(Only English)不能为空且不能包含中文！/ Supplier Short Name(Only English) is required and Chinese character is not allowed!'))
        if not self.contact_person:
            raise UserError(_(u'Contact Person不能为空！/ Contact Person is required!'))
        if not self.company_telephone1 or not utility.is_phone(self.company_telephone1):
            raise UserError(_(u'Company Tel. 1 必须填写有效的电话号码！/ Company Tel. 1 is invalid!'))
        if not self.company_fax or not utility.is_phone(self.company_fax):
            raise UserError(_(u'Company Fax必须填写有效的FAX！/ Company Fax is invalid!'))
        if not self.sales_email or not utility.is_email(self.sales_email):
            raise UserError(_(u'Contact email必须填写有效Email！/ Contact email is invalid!'))
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

        # 无需签核直接变更vendor
        vals = {
            'name1_cn': self.name1_cn,
            'name1_en': self.name1_en,
            'short_name': self.short_name,
            'contact_person': self.contact_person,
            'company_telephone1': self.company_telephone1,
            'company_fax': self.company_fax,
            'sales_email': self.sales_email,
            'address_street': self.address_street,
            'address_city': self.address_city,
            'address_district': self.address_district,
            'address_postalcode': self.address_postalcode,
            'address_country': self.address_country.id
        }
        self.vendor_reg_id.write(vals)

        if self.state == 'draft':
            self.write({'state': 'done'})

        title = _("Tips for %s") % self.name1_cn
        return self.env['warning_box'].info(title=title, message=u'提交成功！')

    @api.multi
    def button_cancel(self):
        if self.state == 'draft':
            self.write({'state': 'cancel'})

class MailMessage(models.Model):
    """
    继承mail.message，增加发送给所有Vendor用户组的设置
    """
    _inherit = "mail.message"

    white_id = fields.Many2one('mail.message.white', string="White List", domain=[('active', '=', True)])
    is_all = fields.Boolean(string="Is all", default=False)
    file_id = fields.Many2one('muk_dms.file', string="Attachment File", index=True)

    @api.onchange('white_id')
    def _onchange_white_id(self):
        partner_ids = []
        self.partner_ids = []
        # 白名单
        vendor_group = self.env.ref('oscg_vendor.IAC_vendor_groups')
        if vendor_group:
            for item in self.white_id.line_ids:
                if item.vendor_id.user_id in vendor_group.users:
                    partner_ids.append(item.vendor_id.user_id.partner_id.id)
        self.partner_ids = partner_ids

    @api.onchange('is_all')
    def _onchange_is_all(self):
        partner_ids = []
        if self.is_all:# 全选
            self.partner_ids = []
            vendor_group = self.env.ref('oscg_vendor.IAC_vendor_groups')
            if vendor_group:
                partner_list = self.env['res.partner'].search([('active', '=', True), ('supplier', '=', True)])
                for item in partner_list:
                    if item.user_id in vendor_group.users:
                        partner_ids.append(item.id)
            self.partner_ids = partner_ids
        else:# 使用白名单
            if self.white_id:
                # 白名单
                vendor_group = self.env.ref('oscg_vendor.IAC_vendor_groups')
                if vendor_group:
                    for item in self.white_id.line_ids:
                        if item.vendor_id.user_id in vendor_group.users:
                            partner_ids.append(item.vendor_id.user_id.partner_id.id)
                self.partner_ids = partner_ids

class MailMessageWhite(models.Model):
    """
    Vendor公告白名单
    """
    _name = "mail.message.white"
    _description = "Vendor Message White list"
    _order = 'id desc'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    line_ids = fields.One2many('mail.message.white.line', 'white_id', string="White Lines")
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, values):
        # 白名单去重vendor code
        line_ids = set()
        list_line_ids = []
        if values.get('line_ids', False):
            for line_id in values.get('line_ids', False):
                line_ids.add(line_id[2]['vendor_id'])
            for item in line_ids:
                list_line_ids.append([0, False, {'vendor_id': item}])
            values['line_ids'] = list_line_ids
        result = super(MailMessageWhite, self).create(values)
        return result

    @api.multi
    def write(self, values):
        # 白名单去重vendor code
        line_ids = set()# 新添加去重
        list_line_add_ids = []# 新添加
        list_line_reserve_ids = []# 保留
        list_line_remove_ids = []# 删除
        if values.get('line_ids', False):
            for line_id in values.get('line_ids', False):
                if line_id[0] == 0:# 新添加
                    line_ids.add(line_id[2]['vendor_id'])
                elif line_id[0] == 4:# 保留
                    list_line_reserve_ids.append(line_id)
                elif line_id[0] == 2:# 删除
                    list_line_remove_ids.append(line_id)
            int_list_line_reserve_ids = [self.env['mail.message.white.line'].browse(x[1]).vendor_id.id for x in list_line_reserve_ids]
            for item in line_ids:
                if item not in int_list_line_reserve_ids:
                    list_line_add_ids.append([0, False, {'vendor_id': item}])
            values['line_ids'] = list_line_reserve_ids + list_line_add_ids + list_line_remove_ids

        result = super(MailMessageWhite, self).write(values)
        return result

class MailMessageWhiteLine(models.Model):
    """
    Vendor 公告白名单 Line
    """
    _name = "mail.message.white.line"
    _description = "Vendor Message White Line"

    white_id = fields.Many2one('mail.message.white', string="White Name")
    vendor_id = fields.Many2one('iac.vendor', string="Vendor", required=True, index=True)
    vendor_code = fields.Char(related="vendor_id.vendor_code", string="Vendor Code", readonly=True, index=True)
    vendor_name = fields.Char(related="vendor_id.name", string="Vendor Name", readonly=True)

class MailMessageWhiteUpload(models.TransientModel):
    _name = 'mail.message.white.upload'
    _inherit = 'base_import.import'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.file = base64.decodestring(self.file)

        # 判断文件类型
        file_extend = os.path.splitext(self.file_name)[1]
        if file_extend not in ('.xls', '.xlsx'):
            raise ValidationError(_(u'导入文件类型不是Excle格式，请使用导入模板编辑后重新导入！'))

        def _do_import(fields, options, Flag):
            result = self.do(fields, options, Flag)
            return result

        options = {u'datetime_format': u'', u'date_format': u'%Y-%m-%d', u'keep_matches': False, u'encoding': u'utf-8', u'fields': [], u'quoting': u'"', u'headers': True, u'separator': u',', u'float_thousand_separator': u',', u'float_decimal_separator': u'.', u'advanced': False}

        fields = ['vendor_code']
        result = _do_import(fields, options, False)

        if result['messages']:
            message = u'导入白名单完成，但有以下Vendor Code不存在或是非正常状态：%s' % result['messages']
            return self.env['warning_box'].info(title="message", message=message)
        else:
            action = {
                'name': _('White List'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.message.white',  # 跳转模型名称
                'res_id': result['white_id'],  # 跳转模型id
            }
            return action

    @api.multi
    def do(self, fields, options, dryrun=False):
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')
        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)
        except ValueError, error:
            return [{
                'type': 'error',
                'message': unicode(error),
                'record': False,
            }]
        _logger.info('importing %d rows...', len(data))

        # 拼装主从结构的白名单
        no_vendor_list = set()
        line_ids = []
        int_line_ids = set()
        for line in data:
            # 补齐10位vendor code
            vendor = self.env['iac.vendor'].search([('vendor_code', '=', line[0].zfill(10)), ('state', 'in', ('done', 'block'))], limit=1)
            if vendor:
                int_line_ids.add(vendor.id)
            else:
                no_vendor_list.add(line[0])
        for item in int_line_ids:
            line_ids.append((0, 0, {'vendor_id': item}))
        white_list = {
            'name': self.name,
            'description': self.description,
            'line_ids': line_ids
        }
        white_id = self.env['mail.message.white'].create(white_list)
        _logger.info('done')

        # If transaction aborted, RELEASE SAVEPOINT is going to raise
        # an InternalError (ROLLBACK should work, maybe). Ignore that.
        # TODO: to handle multiple errors, create savepoint around
        #       write and release it in case of write error (after
        #       adding error to errors array) => can keep on trying to
        #       import stuff, and rollback at the end if there is any
        #       error in the results.
        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
            else:
                self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        if no_vendor_list:
            messages = ','.join(list(no_vendor_list))
        else:
            messages = ''
        return {'messages': messages, 'white_id': white_id.id}