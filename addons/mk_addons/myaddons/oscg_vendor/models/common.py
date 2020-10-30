# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from datetime import datetime, timedelta
from odoo import exceptions
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.http import request
import logging
import traceback
from odoo.addons.muk_dms.models import muk_dms_base as base
_logger = logging.getLogger(__name__)

class AttachmentType(models.Model):
    """
    附件的类型定义，同时用在Vendor选择自己拥有的ISO文件
    """
    _name = "iac.attachment.type"
    _description = u"Attachment Type"

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    sub_group = fields.Selection(string='Sub Group', selection='_selection_subgroup')
    special_approved = fields.Boolean(string='Special Approved', default=False)
    time_sensitive = fields.Boolean(string='Time Sensitive', default=False)
    approver_ids = fields.Many2many('res.users', string="Approver", domain=[('share', '=', False)])
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Attachment Type name already exists !"),
    ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name']
            if record['description']:
                name = name + ' ' + record['description']
            res.append((record['id'], name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('description', operator, name)]
        result = self.search(domain + args, limit=limit)
        return result.name_get()

    @api.model
    def _selection_subgroup(self):
        res_type = []
        group_list = self.env['ir.config_parameter'].search([('key', 'like', 'document_subgroup_')])
        for item in group_list:
            res_type.append((item.key[18:], _(item.value)))

        return res_type

class AttachmentConfig(models.Model):
    """
    模型对应的附件配置
    """
    _name = "iac.attachment.config"
    _description = u"Attachment Config"
    _order = "sequence"

#    model_obj = fields.Selection([('vendor', 'Vendor'), ('vendor_bank', 'Vendor Bank')], string='Model Object', required=True)
    model_obj = fields.Selection(string='Model Object', selection='_selection_subgroup', required=True)
    type = fields.Many2one('iac.attachment.type', string="Attachment Type", domain=[('active', '=', True)])
    is_required = fields.Boolean(string='Is Required', default=False)
    is_displayed = fields.Boolean(string='Is Displayed', default=True)
    sequence = fields.Integer(string="Sequence")

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(model_obj, type)',
         "model and type must be unique."),
    ]

    @api.model
    def _selection_subgroup(self):
        res_type = []
        group_list = self.env['ir.config_parameter'].search([('key', 'like', 'doc_config_model_obj_')])
        for item in group_list:
            res_type.append((item.key[21:], _(item.value)))

        return res_type

class VendorRegisteReason(models.Model):
    """
    buyer选择vendor registe申请原因
    """
    _name = "iac.vendor.reason"
    _description = u"Apply Reason"

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Apply reason name already exists !"),
    ]

class IacVendorQVL(models.Model):
    """
    新厂商注册评分作业
    """
    _name = "iac.vendor.qvl"
    _description = u"QVL Score Information"

    name = fields.Char(string="Name", required=True)
    stage = fields.Char(string="Stage", required=True)
    rate = fields.Float('Rate', required=True, digits=(7, 2))
    line_ids = fields.One2many("iac.vendor.qvl.line", "qvl_id", string="QVL Score Information Lines")

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for record in self:
            total = sum([x.top_score for x in record.line_ids])
            if record.rate * 100 != total:
                raise ValidationError(u"QVL单项的分数之和必须与QVL权重相符！")

    @api.constrains('rate')
    def _check_rate(self):
        for record in self:
            total = sum([x.rate for x in self.search([])])
            if total > 1:
                raise ValidationError(u"QVL所有项目的rate必须等于1！")

class IacVendorQVLLine(models.Model):
    """
    新厂商注册评分作业明细
    """
    _name = "iac.vendor.qvl.line"
    _description = u"QVL Score Information Line"
    _order = "qvl_id, sequence"

    qvl_id = fields.Many2one('iac.vendor.qvl')
    item = fields.Char(string="Item", required=True)
    sequence = fields.Integer(string="Sequence")
    description_en = fields.Char(string="Description EN", required=True)
    description_cn = fields.Char(string="Description CN", required=True)
    top_score = fields.Float(string="Top Score", required=True, digits=(7, 2))

class ResCountry(models.Model):
    _inherit = "res.country"

    code = fields.Char(string='Country Code', size=3,
                       help='The ISO country code in two chars. \nYou can use this field for quick search.')
    sh_import = fields.Selection([
        ('Y', 'Yes'),
        ('N', 'No')], string="SH import")
    show_in_list = fields.Selection([
        ('Y', 'Yes'),
        ('N', 'No')], string="Show in list")

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            res.append((record['id'], name))
        return res

class ResUsers(models.Model):
    _inherit = "res.users"

    vendor_reg_ids = fields.One2many('iac.vendor.register', 'user_id', string="Vendor Registration")
    vendor_ids = fields.One2many('iac.vendor', 'user_id', string="Vendor")
    plant_id = fields.Many2one('pur.org.data', string="Current Plant", compute="_compute_plant_id")  # 用户登录后选择的plant
    vendor_id = fields.Many2one('iac.vendor.vendor', string="Current Vendor", compute="_compute_vendor_id")# 用户登录后选择的vendor
    vendor_code = fields.Char(string="Vendor Code", related="vendor_id.vendor_code", readonly=True)
    password_date = fields.Date('Password Date', readonly=True, default=fields.Date.today)# 密码设置时间
    expired_date = fields.Date('Expiration Date', readonly=True, compute="_compute_expired_date")  # 用户密码过期日期
    agent_user_ids = fields.One2many('iac.agent.users', 'principal_user_id', string="Agent Users")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}

        # 根据attachment type approver过滤数据
        if context.get('filter_user_by_attachment_type'):# attachment approver
            args += [('active', '=', True)]
            attachment_type_id = self.env['iac.attachment.type'].browse(context.get('attachment_type_id'))
            if attachment_type_id:
                args += [('id', 'in', attachment_type_id.approver_ids.ids)]

        # 根据登录user的plant过滤user
        if context.get('filter_user_by_user_plant'):
            int_partner_ids = []
            for plant_id in self.env.user.partner_id.plant_ids:
                self.env.cr.execute("select partner_id from partner_plant_rel where plant_id=%s", (plant_id.id,))
                for partner_id in self.env.cr.fetchall():
                    int_partner_ids.append(partner_id)
            if int_partner_ids:
                args += [('partner_id', 'in', int_partner_ids)]

        return super(ResUsers, self).search(args, offset, limit, order, count=count)

    def _compute_plant_id(self):
        for v in self:
            if request.session:
                v.plant_id = request.session.get('session_plant_id', False)

    def _compute_vendor_id(self):
        for v in self:
            if request.session:
                v.vendor_id = request.session.get('session_vendor_id', False)

    @api.depends('password_date')
    def _compute_expired_date(self):
        # 计算密码过期日期
        expiration_days = self.env['ir.config_parameter'].get_param('password.expiration.days', False)
        if not expiration_days:
            expiration_days = 356
        for user in self:
            user.expired_date = fields.Datetime.from_string(user.password_date) + timedelta(days=int(expiration_days))

    @property
    def buyer_id_list(self):
        self.env.cr.execute("select buyer_code_id from res_partner_buyer_code_line where partner_id=%s",(self.partner_id.id,))
        buyer_ids=self.env.cr.fetchall()
        buyer_id_list=[]
        for buyer_id in buyer_ids:
            buyer_id_list+=list(buyer_id)
        return buyer_id_list

    @property
    def plant_id_list(self):
        self.env.cr.execute("select plant_id from partner_plant_rel where partner_id=%s",(self.partner_id.id,))
        plant_ids=self.env.cr.fetchall()
        plant_id_list=[]
        for plant_id in plant_ids:
            plant_id_list+=list(plant_id)
        #针对登录账户是vendor的情况下
        for vendor_id in self.vendor_ids:
            if vendor_id.plant.id not in plant_id_list:
                plant_id_list.append(vendor_id.plant.id)
        return plant_id_list

    @property
    def division_id_list(self):
        self.env.cr.execute("select division_code_id from partner_division_rel where partner_id=%s",(self.partner_id.id,))
        division_ids=self.env.cr.fetchall()
        division_id_list=[]
        for division_id in division_ids:
            division_id_list+=list(division_id)
        return division_id_list

    @property
    def source_code_list(self):
        self.env.cr.execute("select sc.source_code from source_code sc                                         " \
                            "where exists(                                                                     " \
                            "select 1 from res_partner_source_code_line rpsc where rpsc.source_code_id=sc.id   " \
                            " and rpsc.partner_id=%s                                                               " \
                            ")                                                                                 ",
                            (self.partner_id.id,))
        source_code_ids=self.env.cr.fetchall()
        source_code_list=[]
        for source_code in source_code_ids:
            source_code_list+=list(source_code)
        return source_code_list

    @property
    def buyer_vendor_id_list(self):
        """
        获取当前buyer对应的vendor_id
        """
        self.env.cr.execute("select id from iac_vendor where buyer_email=%s",(self.partner_id.email,))
        vendor_ids=self.env.cr.fetchall()
        vendor_id_list=[]
        for vendor_id in vendor_ids:
            vendor_id_list+=list(vendor_id)
        return vendor_id_list

    @property
    def buyer_vendor_reg_id_list(self):
        """
        获取当前buyer对应的vendor_id
        """
        self.env.cr.execute("select id from iac_vendor_register where buyer_email=%s",(self.partner_id.email,))
        vendor_reg_ids=self.env.cr.fetchall()
        vendor_reg_id_list=[]
        for vendor_reg_id in vendor_reg_ids:
            vendor_reg_id_list+=list(vendor_reg_id)
        return vendor_reg_id_list

    @property
    def file_type_id_list(self):
        """
        获取当前user管理的文件类型id
        """
        self.env.cr.execute("select iac_attachment_type_id from iac_attachment_type_res_users_rel where res_users_id=%s",(self.ids[0],))
        file_type_ids=self.env.cr.fetchall()
        file_type_id_list=[]
        for file_type_id in file_type_ids:
            file_type_id_list+=list(file_type_id)
        return file_type_id_list


class IacAgentUsers(models.Model):
    """
    实现代理人机制
    规则：1.只能设置一层代理关系，设置后立即生效，超期日期为expired_date当天（包含expired_date）
          2.委托人在同一有效时间范围内只能设置一个代理人
          3.委托人可以主动取消代理关系，代理关系逾期后系统自动取消
          4.代理人可以切换到委托人工作空间，如果要切换到自己的工作空间需要重新登录
    """
    _name = "iac.agent.users"

    principal_user_id = fields.Many2one('res.users', string='Principal User', readonly=True)# 委托人、被代理人
    agent_user_id = fields.Many2one('res.users', string='Agent User', required=True, domain=[('share', '=', False)])# 代理人
    expired_date = fields.Date(string="Expired Date", required=True)
    password_str=fields.Char(string="Password")#明文密码

    @api.model
    def create(self, values):
        if self.env.uid == SUPERUSER_ID:
            raise UserError(_(u'超级管理员不可以设置代理人。'))
        cur_time=datetime.now().strftime("%Y-%m-%d")
        if values.get('expired_date', False) and values['expired_date'] < cur_time:
            raise exceptions.Warning(u'过期日期必须大于等于当前日期！')
        count = self.search_count([('principal_user_id', '=', self.env.uid), ('expired_date', '>=', fields.Date.today())])
        if count > 0:
            raise exceptions.Warning(u'在当前有效期内您已经设置过代理人！')

        #校验输入的密码是否正确,如果密码不正确就阻挡密码数据的录入
        #if "password_str" in values:
        #    try:
        #        db_name=self.env.cr.dbname
        #        uid=self.env.uid
        #        password_str=values["password_str"]
        #        self.env["res.users"].check(db_name,uid,password_str)
        #    except:
        #        traceback.print_exc()
        #        raise UserError("Password is not correct!")

        values['principal_user_id'] = self.env.uid
        result = super(IacAgentUsers, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if values.get('expired_date', False) and fields.Datetime.from_string(values['expired_date']) < datetime.today():
            raise exceptions.Warning(u'过期日期必须大于当前日期！')
        count = self.search_count([('principal_user_id', '=', self.env.uid), ('expired_date', '>', fields.Date.today()),('id','not in',self.ids)])
        if count > 0:
            raise exceptions.Warning(u'在当前有效期内您已经设置过代理人！')

        # 如果修改代理人则将原代理关系记录代理历史
        if values.get('agent_user_id', False):
            val_history = {
                'principal_user_id': self.principal_user_id,
                'agent_user_id': self.agent_user_id,
                'start_date': self.write_date,
                'expired_date': fields.Date.today()
            }
            self.env['iac.agent.users.history'].create(val_history)

        ##校验输入的密码是否正确,如果密码不正确就阻挡密码数据的录入
        #if "password_str" in values:
        #    try:
        #        db_name=self.env.cr.dbname
        #        uid=self.env.uid
        #        password_str=values["password_str"]
        #        self.env["res.users"].check(db_name,uid,password_str)
        #    except:
        #        traceback.print_exc()
        #        raise UserError("Password is not correct!")

        values['principal_user_id'] = self.env.uid
        result = super(IacAgentUsers, self).write(values)
        return result

    @api.multi
    def unlink(self):
        val_history = {
            'principal_user_id': self.principal_user_id.id,
            'agent_user_id': self.agent_user_id.id,
            'start_date': self.write_date,
            'expired_date': fields.Date.today()
        }
        self.env['iac.agent.users.history'].create(val_history)
        return super(IacAgentUsers, self).unlink()

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.agent_user_id.login
            res.append((record['id'], name))
        return res

class IacAgentUsersHistory(models.Model):
    _name = "iac.agent.users.history"

    principal_user_id = fields.Many2one('res.users', string='Principal User', readonly=True)# 委托人、被代理人
    agent_user_id = fields.Many2one('res.users', string='Agent User', readonly=True)# 代理人
    start_date = fields.Date(string="Start Date", readonly=True)
    expired_date = fields.Date(string="Expired Date", readonly=True)

class IacAgentUsersWizard(models.TransientModel):
    """设置当前工作人"""
    _name = 'iac.agent.users.wizard'

    work_user_name = fields.Char(string='Current Work User')# 当前工作空间
    principal_user_id = fields.Selection(string='Principal User', selection='selection_principal_user')  # 委托人、被代理人

    @api.onchange('principal_user_id')
    def _onchange_principal_user_id(self):
        for v in self:
            v.work_user_name = self.env.user.login

    @api.model
    def selection_principal_user(self):
        user_list = []
        agents = self.env['iac.agent.users'].sudo().search([('agent_user_id', '=', self.env.uid), ('expired_date', '>=', fields.Datetime.to_string(datetime.now()))])
        for item in agents:
            user_list.append((item.id,item.principal_user_id.name))
        return user_list

    @api.multi
    def set_work_user(self):
        if self.env.uid == SUPERUSER_ID:
            raise UserError(_(u'超级管理员不可以执行该操作。'))

        self.ensure_one()
        for wizard in self:
            if wizard.principal_user_id:# 切换到委托人工作空间
                agent_user_rec = self.env['iac.agent.users'].sudo().browse(int(wizard.principal_user_id))
                #request.session.login_principal(user_id.login, user_id.id)
                #request.session.authenticate(db='IAC_DB',login=user_id.login,password='INC063472*&^678',uid=4108)

                db_name=self.env.cr.dbname
                new_user_login=agent_user_rec.principal_user_id.login
                new_user_password=agent_user_rec.principal_user_id.password
                new_user_uid=agent_user_rec.principal_user_id.id
                #明文密码没有保存
                if new_user_password==False:
                    raise UserError("Switch workspace fail,Principal none encrypted password has not saved!")

                #验证代理密码是否有效
                try:
                    self.env["res.users"].check(db_name,new_user_uid,new_user_password)
                except:
                    traceback.print_exc()
                    raise UserError("Switch workspace fail,Principal password is not correct!")

                #开始切换登录账号
                request.session.authenticate(db_name,new_user_login,new_user_password,uid=new_user_uid)
                #request.session.authenticate(self.env.cr.dbname,login=user_id.login,password='INC063472*&^678',uid=user_id.uid)
                return self.env['warning_box'].info(title=u"设置成功", message=u"切换工作空间成功，请刷新页面！")

class ResPartnerBuyerCodeLine(models.Model):
    _name = "res.partner.buyer.code.line"

    partner_id = fields.Many2one('res.partner', string="Partner")
    buyer_code_id = fields.Many2one('buyer.code', string="Buyer Code", required=True, domain=[('is_bind', '=', False)])

    @api.model
    def create(self, values):
        result = super(ResPartnerBuyerCodeLine, self).create(values)
        result.buyer_code_id.is_bind = True
        return result

    @api.multi
    def unlink(self):
        #self.buyer_code_id.is_bind = False
        for partner_line in self:
            partner_line.buyer_code_id.write({"is_bind":False})
        result = super(ResPartnerBuyerCodeLine, self).unlink()
        return result

class ResPartnerSourceCodeLine(models.Model):
    _name = "res.partner.source.code.line"

    partner_id = fields.Many2one('res.partner', string="Partner")
    source_code_id = fields.Many2one('source.code', string="Buyer Code", required=True, domain=[('is_bind', '=', False)])

    @api.model
    def create(self, values):
        result = super(ResPartnerSourceCodeLine, self).create(values)
        result.source_code_id.is_bind = True
        return result

    @api.multi
    def unlink(self):
        for partner_line in self:
            #partner_line.source_code_id.is_bind = False
            partner_line.source_code_id.write({"is_bind":False})
        result = super(ResPartnerSourceCodeLine, self).unlink()
        return result

class ResPartnerIacStorageLocationLine(models.Model):
    _name = "res.partner.iac.storage.location.line"

    partner_id = fields.Many2one('res.partner', string="Partner")
    storage_location_id = fields.Many2one('iac.storage.location.address', string="Location Address", required=True)

    @api.model
    def create(self, values):
        result = super(ResPartnerIacStorageLocationLine, self).create(values)
        result.storage_location_id.is_bind = True
        return result

    # @api.multi
    # def unlink(self):
    #     for partner_line in self:
    #         partner_line.storage_location_id.write({"is_bind":False})
    #     result = super(ResPartnerIacStorageLocationLine,self).unlink()
    #     return result


class ResPartner(models.Model):
    _inherit = "res.partner"

    plant_ids = fields.Many2many('pur.org.data', 'partner_plant_rel', 'partner_id', 'plant_id', string="Plant")
    # location_ids = fields.Many2one('iac.storage.location.address', 'partner_location_rel', 'partner_id', 'location_id')
    buyer_code_ids = fields.One2many("res.partner.buyer.code.line", 'partner_id', string="Buyer Code")# 被选择后不能再被其他partner选择
    source_code_ids = fields.One2many("res.partner.source.code.line", 'partner_id', string="Source Code")# 被选择后不能再被其他partner选择
    storage_location_ids = fields.One2many("res.partner.iac.storage.location.line", 'partner_id', string="Location Address")
    division_code_ids = fields.Many2many("division.code", 'partner_division_rel', 'partner_id', 'division_code_id', string="Division Code")# 被选择后不能再被其他partner选择
    in_cm_group = fields.Boolean(string="In CM Group", compute="_compute_in_cm_group")# 用于控制division_code_ids是否可见
    in_as_group = fields.Boolean(string="In AS Group", compute="_compute_in_as_group")# 用于控制source_code_ids是否可见
    in_scm_user_group = fields.Boolean(string="In SCM User Group", compute="_compute_in_scm_user_group", search='_search_scm_user')
    in_qm_user_group = fields.Boolean(string="In QM User Group", compute="_compute_in_qm_user_group", search='_search_qm_user')
    employee_code = fields.Char(string="Employee Code")


    @api.multi
    def _compute_in_cm_group(self):
        in_cm_group = False
        cm_group = self.env.ref('oscg_vendor.IAC_CM_groups')
        for partner in self:
            for user in cm_group.users:
                if partner.id == user.partner_id.id:
                    in_cm_group = True
                    break
            partner.in_cm_group = in_cm_group

    @api.multi
    def _compute_in_as_group(self):
        in_as_group = False
        as_group = self.env.ref('oscg_vendor.IAC_AS_groups')
        for partner in self:
            for user in as_group.users:
                if partner.id == user.partner_id.id:
                    in_as_group = True
                    break
            partner.in_as_group = in_as_group

    @api.multi
    def _compute_in_scm_user_group(self):
        in_cm_group = False
        user_group = self.env.ref('oscg_vendor.group_scm_user')
        for partner in self:
            for user in user_group.users:
                if partner.id == user.partner_id.id:
                    in_cm_group = True
                    break
            partner.in_cm_group = in_cm_group

    @api.multi
    def _compute_in_qm_user_group(self):
        in_cm_group = False
        user_group = self.env.ref('oscg_vendor.group_qm_user')
        for partner in self:
            for user in user_group.users:
                if partner.id == user.partner_id.id:
                    in_cm_group = True
                    break
            partner.in_cm_group = in_cm_group

    @api.multi
    def _search_scm_user(self, operator, value):
        ids = []
        user_group = self.env.ref('oscg_vendor.group_scm_user')
        for user in user_group.users:
           ids.append(user.partner_id.id)
        return [('id', 'in', ids)]

    @api.multi
    def _search_qm_user(self, operator, value):
        ids = []
        user_group = self.env.ref('oscg_vendor.group_qm_user')
        for user in user_group.users:
           ids.append(user.partner_id.id)
        return [('id', 'in', ids)]

    @api.constrains('plant_ids')
    def _check_plant_ids(self):
        in_vendor_group = False
        vendor_group = self.env.ref('oscg_vendor.IAC_vendor_groups')
        for record in self:
            for user in vendor_group.users:
                if record.id == user.partner_id.id:
                    in_vendor_group = True
                    break
            if in_vendor_group:
                if not self.plant_ids:
                    raise ValidationError(u"请选择Plant！")

    @api.model
    def create(self, values):
        if values.get('email', False):
            values['email'] = values['email'].lower()
        result = super(ResPartner, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if values.get('email', False):
            values['email'] = values['email'].lower()
        result = super(ResPartner, self).write(values)
        return result

    @api.onchange('plant_ids')
    def _onchange_plant_ids(self):
        res = {'domain': []}
        if self.plant_ids:
            domain = [('plant_id', 'in', self.plant_ids.ids)]

            res['domain'] = {'buyer_code': domain}
        return res

class ResCurrency(models.Model):
    _inherit = "res.currency"

    decimal_setting = fields.Integer(string="Decimal Setting")
    description = fields.Char(string="Description")

class VendorAccountGroup(models.Model):
    _name = 'iac.vendor.account.group'

    vendor_type = fields.Selection([
        ('normal', 'Normal'),
        ('spot', 'Spot'),
        ('mold', 'Mold'),
        ('bvi', 'BVI'),
    ], default='normal', required=True, string="Vendor Type *")
    plant_id = fields.Many2one('pur.org.data', string="Plant")
    local_foreign = fields.Selection([("local", "Local"), ("foreign", "Foreign")], string="Local or Foreign")
    account_group = fields.Char(string="Account Group *", required=True)
    comment = fields.Char(string="Comment")


#muk_dms.file

class MukDmsFile(base.DMSModel):
    _inherit = 'muk_dms.file'
    @api.multi
    def write(self, values):
        result = super(MukDmsFile, self).write(values)
        #附件对象是否存在vendor 或者vendor_reg 文档中
        #只有在上传文件的情况下更新状态信息
        if "file" in values:
            domain=[('file_id','in',self.ids)]
            vendor_reg_attachments=self.env["iac.vendor.register.attachment"].search(domain)
            if vendor_reg_attachments.exists():
                vendor_reg_attachments.write({"state":"upload"})
            vendor_attachments=self.env["iac.vendor.attachment"].search(domain)
            if vendor_attachments.exists():
                vendor_attachments.write({"state":"upload"})
        return result