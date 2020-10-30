# -*- coding: utf-8 -*-

from odoo import api
import odoo.modules.registry
from odoo.http import *
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.modules.registry import RegistryManager
import werkzeug
import base64
import time
import json
import logging
import types
from odoo.tools.safe_eval import safe_eval
from odoo import tools

_logger = logging.getLogger(__name__)

def no_token():
    rp = {'result': '', 'success': False, 'message':'invalid token!'}
    return json_response(rp)

def json_response(rp):
    headers = {"Access-Control-Allow-Origin": "*"}
    return werkzeug.wrappers.Response(json.dumps(rp, ensure_ascii=False), mimetype='application/json', headers=headers)

def isNumber(value):
    try:
        x = int(value)
    except TypeError:
        return False
    except ValueError:
        return False
    except Exception, e:
        return False
    else:
        return True

# 供应商注册
class VendorRegistor(http.Controller):
    db_password = {}
    db_tokens = {}

    def __init__(self):
        # 初始化webflow的登录密码,从配置文件中获取
        webflow_login_password_txt = tools.config.get("webflow_login_password")
        if webflow_login_password_txt == None:
            raise "webflow_login_password must set in openerp-server.conf file"

        webflow_db_list_txt = tools.config.get("webflow_db_list")
        if webflow_db_list_txt == None:
            raise "webflow_db_list must set in openerp-server.conf file"

        webflow_login_password = safe_eval(webflow_login_password_txt)
        webflow_db_list = safe_eval(webflow_db_list_txt)
        VendorRegistor.db_password = webflow_login_password
        VendorRegistor.db_tokens = webflow_db_list

    @http.route('/web/register', type='http', auth="none")
    def web_vendorRegistor(self, redirect=None, **kw):
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            result = request.env['iac.vendor.register'].generate_account(request.params['name'], request.params['email'], request.params['password'], request.params['buyeremail'])
            values['error'] = _(result)
        return request.render('oscg_vendor.iac_vendor_login', values)

    @route('/vendor/attachment/type', type="http", auth="none", csrf=False, methods=['GET'])
    def get_attachment_type(self, db_name=None, user_name=None, **kw):
        token = self.get_last_token(db_name, user_name)
        env = self.get_env(token)

        url = {}
        if not env:
            return no_token()
        try:
            type_list = env['iac.attachment.type'].search([])
            type_result = []
            for type in type_list:
                val = {
                    'id': type.id,
                    'name': type.name,
                    'description': type.description
                }
                type_result.append(val)
            url = {'file_type': type_result}
        except Exception, e:
            False, str(e)

        return json_response(url)

    @route('/vendor/attachment/upload', type="http", auth="none", csrf=False, methods=['POST', 'GET'])
    def upload_attachment(self, stage, vendor_reg_id, file_type_code, filename, file, description,
                          db_name=None, user_name=None, **kw):
        token = self.get_last_token(db_name, user_name)
        env = self.get_env(token)

        if not env:
            return no_token()
        try:
            # 参数校验
            error_str = ''
            value = re.compile('[0-9]')
            if stage not in ('F01', 'F02'):
                error_str = u'Stage不存在'
            elif not value.match(vendor_reg_id):
                error_str = u'vendor_reg_id值无效'
            else:
                vendor_reg_id = int(vendor_reg_id)  # unicode to int
                vendor_reg_obj = env['iac.vendor.register'].browse(vendor_reg_id)
                if not vendor_reg_obj:
                    error_str = u'Vendor不存在'
                else:
                    file_type_obj = env['iac.attachment.type'].search([('name', '=', file_type_code),
                                                                            ('active', '=', True)])
                    if not file_type_obj:
                        error_str = u'Doc type不存在'
            if error_str != '':
                url = {'file_url': error_str}
            else:
                config = env['ir.config_parameter'].search([('key', '=', 'web.server.url')], limit=1)
                str_file = str(file).replace(' ', '+')# 替换webflow发来的file中的空格为“+”号
                file_val = {'filename': filename,
                            'file': str_file
                            }
                if stage == 'F01':
                    attachment = env['iac.vendor.register.attachment'].search(
                        [('vendor_reg_id', '=', vendor_reg_id), ('type', '=', file_type_obj.id)], limit=1)
                    if not attachment:
                        file_val['directory'] = 1  # vendor目录
                        file_id = env['muk_dms.file'].create(file_val)
                        attachment_val = {'vendor_reg_id': vendor_reg_id,
                                          'type': file_type_obj.id,  # Vendor附件类型
                                          'file_id': file_id.id,
                                          'description': description
                                          }
                        attachment_id = env['iac.vendor.register.attachment'].create(attachment_val)
                        url = {'file_url': config.value + attachment_id.file_id.link_download,
                               'version': attachment_id.file_id.version}
                    elif not attachment.file_id:
                        file_val['directory'] = 1  # vendor目录
                        file_id = env['muk_dms.file'].create(file_val)
                        attachment_val = {'file_id': file_id.id,
                                          'description': description
                                          }
                        attachment.write(attachment_val)
                        url = {'file_url': config.value + attachment.file_id.link_download,
                               'version': attachment.file_id.version}
                    else:
                        attachment.file_id.write(file_val)
                        url = {'file_url': config.value + attachment.file_id.link_download,
                               'version': attachment.file_id.version}
                elif stage == 'F02':
                    attachment = env['iac.vendor.attachment'].search(
                        [('vendor_id', '=', vendor_reg_obj.vendor_id.id), ('type', '=', file_type_obj.id)], limit=1)
                    if not attachment:
                        file_val['directory'] = 2  # vendor目录
                        file_id = env['muk_dms.file'].create(file_val)
                        attachment_val = {'vendor_id': vendor_reg_obj.vendor_id.id,
                                          'type': file_type_obj.id,  # Vendor附件类型
                                          'file_id': file_id.id,
                                          'description': description
                                          }
                        attachment_id = env['iac.vendor.attachment'].create(attachment_val)
                        url = {'file_url': config.value + attachment_id.file_id.link_download,
                               'version': attachment_id.file_id.version}
                    elif not attachment.file_id:
                        file_val['directory'] = 2  # vendor目录
                        file_id = env['muk_dms.file'].create(file_val)
                        attachment_val = {'file_id': file_id.id,
                                          'description': description
                                          }
                        attachment.write(attachment_val)
                        url = {'file_url': config.value + attachment.file_id.link_download,
                               'version': attachment.file_id.version}
                    else:
                        attachment.file_id.write(file_val)
                        url = {'file_url': config.value + attachment.file_id.link_download,
                               'version': attachment.file_id.version}

        except Exception, e:
            False, str(e)
            url = {'file_url': str(e)}
        else:
            env.cr.commit()
            env.cr.close()

        return json_response(url)

    def get_last_token(self, db_name, user_name):
        if (db_name in self.db_tokens):
            token_list = self.db_tokens[db_name]
            if len(token_list) > 0:
                return token_list[len(token_list) - 1]
            else:
                # 获取登录密码来进行认证
                if (db_name in self.db_password):
                    db_password_dict = self.db_password[db_name]
                    if user_name not in db_password_dict:
                        # 抛出异常获取登录密码失败
                        return False
                        pass
                    password = db_password_dict[user_name]
                    token = self.get_token_by_pass(db_name, user_name, password)
                    self.db_tokens[db_name].append(token)
                    return token
                else:
                    # 抛出异常指定的数据库没有设定登录密码
                    return False

    # 验证token后返回Odoo的Env对象
    def get_env(self,token):
        try:
            a = 4 - len(token) % 4
            if a != 0:
                token += '==' if a == 2 else '='
            SERVER, db, login, uid, ts = base64.urlsafe_b64decode(str(token)).split(', ')
            if int(ts) + 60*60*24*7*10 < time.time():
                return False
            registry = RegistryManager.get(db)
            cr = registry.cursor()
            env = api.Environment(cr, int(uid), {})
        except Exception, e:
            return str(e)
        return env

    def get_token_by_pass(self,db_name,user_name,password):
        try:
            serv='http://www.oscg.cn'
            uid = http.request.session.authenticate(db_name, user_name, password)
        except Exception, e:
            rp = {'token': '', 'success': False, 'message': str(e)}
            return json_response(rp)
        if not uid:
            rp = {'token': '', 'success': False, 'message': 'you are unauthenticated'}
            return json_response(rp)
        token = base64.urlsafe_b64encode(', '.join([serv, db_name, user_name, str(uid), str(int(time.time()))]))
        return token