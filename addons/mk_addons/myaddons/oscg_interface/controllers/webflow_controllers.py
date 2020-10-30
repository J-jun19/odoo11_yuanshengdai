# -*- coding: utf-8 -*-

from odoo import api, http, SUPERUSER_ID, _
from odoo.modules.registry import RegistryManager
from odoo.http import Root
import werkzeug
import base64
import time
import json
import logging
from odoo.tools.safe_eval import safe_eval
from odoo import tools
import socket
import traceback
import types
_logger = logging.getLogger(__name__)


###############################
#
# Odoo iac Restful API Method.
#
###############################

def no_token():
    rp = {'result': '', 'success': False, 'message':'invalid token!'}
    return json_response(rp)

def json_response(rp):
    headers = {"Access-Control-Allow-Origin": "*"}
    return werkzeug.wrappers.Response(json.dumps(rp, ensure_ascii=False), mimetype='application/json', headers=headers)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def get_base64_val(str_val):
    try:
        encode_str=str_val.replace(" ","+")
        result_str=base64.decodestring(encode_str)
    except:
        err_msg="Error Decode Base64,String Text is  %s " %(str_val,)
        err_msg+=traceback.format_exc()
        raise Exception(err_msg)
    return result_str

def get_json_base64(dic_json):
    result_dict={}
    for key in dic_json:
        if isinstance(dic_json[key],dict):#如果dic_json[key]依旧是字典类型
            #print("****key--：%s value--: %s"%(key,dic_json[key]))
            sub_dict=get_json_base64(dic_json[key])
            result_dict[key] = sub_dict
        elif isinstance(dic_json[key],list):
            value_list=[]
            for item_val in dic_json[key]:
                if isinstance(item_val,dict):
                    #构成数组的元素是dict那么递归调用
                    sub_dict=get_json_base64(item_val)
                    value_list.append(sub_dict)
                else:
                    #构成数组的元素是普通值
                    value_list.append(get_base64_val(item_val))
            result_dict[key] = value_list
        else:
            result_dict[key] = get_base64_val(dic_json[key])
    return result_dict

# 获取token
class OdooRestfulApi(http.Controller):

    db_password={"iac_test_db":{"admin":"admin123"}}
    db_tokens={"iac_test_db":[]}


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


    def get_last_token(self,db_name,user_name):
        if (db_name in OdooRestfulApi.db_tokens):
            token_list=OdooRestfulApi.db_tokens[db_name]
            if len(token_list)>0:
                return token_list[len(token_list)-1]
            else:
                #获取登录密码来进行认证
                if (db_name in OdooRestfulApi.db_password):
                    db_password_dict=OdooRestfulApi.db_password[db_name]
                    if user_name not in db_password_dict:
                        #抛出异常获取登录密码失败
                        return False
                        pass
                    password=db_password_dict[user_name]
                    token=self.get_token_by_pass(db_name,user_name,password)
                    OdooRestfulApi.db_tokens[db_name].append(token)
                    return token
                else:
                    #抛出异常指定的数据库没有设定登录密码
                    return False


    # 调用模型的方法
    @http.route([
        '/webflow/<string:db_name>/<string:model>/call/<string:method>/<string:user_name>',
        ], auth='none', type='http', csrf=False, methods=['POST', 'GET'])
    def call_method(self,db_name=None, model=None, method=None, user_name=None,success=True, message='', **kw):
        if "data" not in kw:
            response_json={"status":"false","message":"must call with form key name ( data )", "id": ""}
            return json_response(response_json)

        token=self.get_last_token(db_name,user_name)
        env=self.get_env(token)

        exception_list=[]
        if not env:
            return no_token()
        try:
            #result = eval('env[model].'+method)(kw)
            script_context={}
            rpc_call_json={}
            encoded_json=json.loads(kw["data"])
            rpc_call_json=get_json_base64(encoded_json)

            context={}
            context.update(rpc_call_json)
            context["tokens"]=OdooRestfulApi.db_tokens[db_name]

            script_context["env"]=env
            script_context["context"]=context
            eval_script="env[\"%s\"].sudo().%s(context)"%(model,method)
            result=safe_eval(eval_script,script_context)
        except Exception, e:
            #result=traceback.format_exc()
            err_msg=traceback.format_exc()
            str_ip=get_host_ip()
            result="Exception raise at machine %s;"%(str_ip,)
            result+=err_msg
            traceback.print_exc()
            #解析json出现异常的情况下,尝试写入文件
            fileObject = open('//odoo-files//webflow_text//webflow_error.txt', 'w')
            fileObject.write(kw["data"])
            fileObject.close()

        env.cr.commit()
        env.cr.close()
        return json_response(result)

#初始化webflow的登录密码,从配置文件中获取
conf_obj=tools.config
webflow_login_password_txt=conf_obj.get("webflow_login_password")
if webflow_login_password_txt==None:
    raise "webflow_login_password must set in openerp-server.conf file"

webflow_db_list_txt=conf_obj.get("webflow_db_list")
if webflow_db_list_txt==None:
    raise "webflow_db_list must set in openerp-server.conf file"

webflow_login_password = safe_eval(webflow_login_password_txt)
webflow_db_list = safe_eval(webflow_db_list_txt)
OdooRestfulApi.db_password=webflow_login_password
OdooRestfulApi.db_tokens=webflow_db_list

