# -*- coding: utf-8 -*-
from odoo import http, api, SUPERUSER_ID

from odoo.http import request
import werkzeug.utils

# from CorpApi import *
from odoo import registry as registry_get
import logging
_logger = logging.getLogger(__name__)

# class WechatLoginOdoo(http.Controller):
#     @http.route('/wechat_login_odoo/wechat_login_odoo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wechat_login_odoo/wechat_login_odoo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wechat_login_odoo.listing', {
#             'root': '/wechat_login_odoo/wechat_login_odoo',
#             'objects': http.request.env['wechat_login_odoo.wechat_login_odoo'].search([]),
#         })

#     @http.route('/wechat_login_odoo/wechat_login_odoo/objects/<model("wechat_login_odoo.wechat_login_odoo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wechat_login_odoo.object', {
#             'object': obj
#         })


class Wechat(http.Controller):
    @http.route('/wechat/open/', auth='public')
    def open_wechat(self):
        """
        企业微信oauth_url
        1.构造独立窗口登录二维码
            https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid=CORPID&agentid=AGENTID&redirect_uri=REDIRECT_URI&state=STATE

        """
        dbname = request.session.db
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                # 设置odoo运行环境
                env = api.Environment(cr, SUPERUSER_ID, {})
                config = env['wechat.corp.config'].sudo().browse(1)[0]
                if config:
                    # 获取url参数
                    corp_id = config.corp_id
                    agent_id = config.agent_id
                    redirect_url = config.redirect_url
                    state = config.state
                    # 获取服务器域名
                    host = request.httprequest.environ.get('HTTP_HOST', '')
                    # 拼接获取企业微信code参数的url
                    # url = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid=%s&agentid=%s&redirect_uri=%s&state=%s'\
                    #       % (corp_id, agent_id, redirect_url, state)

                    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=http://%s/wechat/wechat&response_type=code&scope=SCOPE&connect_redirect=1#wechat_redirect'%(corp_id,host)


                return self.set_cookie_and_redirect(url)

            except Exception as e:
                _logger.exception("open: %s" % str(e))
                url = "/web/login?oauth_error=2"

    def set_cookie_and_redirect(self, redirect_url):
        """ 跳转url """
        redirect = werkzeug.utils.redirect(redirect_url, 303)
        redirect.autocorrect_location_header = False


