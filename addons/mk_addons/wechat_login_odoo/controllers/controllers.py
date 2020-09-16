# -*- coding: utf-8 -*-
from odoo import http

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