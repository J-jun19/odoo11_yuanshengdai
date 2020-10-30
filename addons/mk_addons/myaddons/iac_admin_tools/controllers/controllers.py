# -*- coding: utf-8 -*-
from odoo import http

# class IacAdminTools(http.Controller):
#     @http.route('/iac_admin_tools/iac_admin_tools/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iac_admin_tools/iac_admin_tools/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iac_admin_tools.listing', {
#             'root': '/iac_admin_tools/iac_admin_tools',
#             'objects': http.request.env['iac_admin_tools.iac_admin_tools'].search([]),
#         })

#     @http.route('/iac_admin_tools/iac_admin_tools/objects/<model("iac_admin_tools.iac_admin_tools"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iac_admin_tools.object', {
#             'object': obj
#         })