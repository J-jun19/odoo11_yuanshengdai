# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
import time,base64
import traceback
from StringIO import StringIO
import xlwt
import psycopg2
import logging
from odoo.osv.osv import osv
import os
import datetime


_logger = logging.getLogger(__name__)

class CountryOrigin(models.Model):
    _name = 'iac.country.origin'

    plant = fields.Many2one('pur.org.data',string='Plant')
    buyer_code = fields.Char(string='Buyer Code',compute='_get_buyer_code')
    vendor = fields.Many2one('iac.vendor',string='Vendor Code')
    material = fields.Many2one('material.master',string='Material',index=True)
    country_id = fields.Text(string='Country')
    city = fields.Char()
    remark = fields.Char()
    update_by = fields.Many2one('res.users',string='Updated By',readonly=True)
    update_on = fields.Datetime(string='Updated On',readonly=True)
    division = fields.Char(related='material.division')


    def _get_buyer_code(self):

        for item in self:
            buyer_code = self.env['material.master.asn'].browse(item.material.id).buyer_code_id.buyer_erp_id
            item.buyer_code = buyer_code

    @api.model
    def create(self, values):
        values['update_on'] = fields.datetime.now()
        values['update_by'] = self._uid
        change = super(CountryOrigin, self).create(values)

        return change

    @api.multi
    def write(self, values):
        values['update_on'] = fields.datetime.now()
        values['update_by'] = self._uid
        change = super(CountryOrigin, self).write(values)

        return change


class IacCountryOriginReportWizard(models.TransientModel):
    _name = 'country.origin.report.wizard'

    @property
    def buyer_id_list_origin(self):
        record = 0

        for item in self.env.user.groups_id:
            if item.name == 'Buyer Manager':
                record = 1
                break
        if record == 0:
            self.env.cr.execute("select buyer_code_id from res_partner_buyer_code_line where partner_id=%s",
                                (self.env.user.partner_id.id,))
            buyer_ids = self.env.cr.fetchall()
            buyer_id_list_origin = []
            for buyer_id in buyer_ids:
                buyer_id_list_origin += list(buyer_id)
            return buyer_id_list_origin
        if record == 1:
            self.env.cr.execute("select distinct(buyer_code_id) from res_partner_buyer_code_line")
            buyer_ids = self.env.cr.fetchall()
            buyer_id_list_origin = []
            for buyer_id in buyer_ids:
                buyer_id_list_origin += list(buyer_id)
            return buyer_id_list_origin


    @property
    def material_id_list(self):
        record_manager = 0
        record_buyer = 0
        record_vendor = 0
        for item in self.env.user.groups_id:
            if item.name == 'Buyer Manager':
                record_manager = 1
                break
            if item.name == 'Buyer':
                record_buyer = 1
                continue
            if item.name == 'External vendor':
                record_vendor = 1
                break
        if record_buyer == 1 and record_manager == 0:

            material_id_list = []
            for item in self.env['material.master'].search([('buyer_code_id','in',self.env.user.buyer_id_list)]):
                material_id_list.append(item.id)
            return material_id_list
        elif record_manager == 1:
            self.env.cr.execute("select id from material_master")
            material_ids = self.env.cr.fetchall()
            material_id_list = []
            for material_id in material_ids:
                material_id_list += list(material_id)
            return material_id_list
        elif record_vendor == 1:
            material_id_list = []
            # print self.env.user.vendor_ids.ids
            for item in self.env['iac.country.origin'].search([('vendor', 'in', self.env.user.vendor_ids.ids)]):
                material_id_list.append(item.material.id)
            return material_id_list
        else:
            material_id_list = []
            return material_id_list

    plant = fields.Many2one('pur.org.data', string='Plant',domain=lambda self:[('id','in',self.env.user.plant_id_list)])
    buyer = fields.Many2one('buyer.code', string='Buyer Code',domain=lambda self:[('id','in',self.buyer_id_list_origin)])
    vendor = fields.Many2one('iac.vendor', string='Vendor Code')
    material = fields.Many2one('material.master', string='Material',domain=lambda self:[('id','in',self.material_id_list)])
    country_id = fields.Text(string='Country')
    city = fields.Text()
    open_po = fields.Boolean(string='Open PO')
    stock = fields.Boolean(string='Stock')


    @api.multi
    def search_country_origin_report(self):
        # print self.buyer_id_list_origin
        self.ensure_one()
        # self._cr.execute("delete from payment_info_report")
        result = []
        record_manager = 0
        record_buyer = 0
        record_vendor = 0
        vendor_id_list = []
        buyer_id_list = []
        buyer_code_list = []
        material_id_list = []
        for item in self.env.user.groups_id:
            if item.name == 'Buyer Manager':
                record_manager = 1
                break
            if item.name == 'Buyer':
                record_buyer = 1
                continue
            if item.name == 'External vendor':
                record_vendor = 1
                break


        for wizard in self:
            domain = []
            if wizard.plant:
                domain += [('plant', '=', wizard.plant.id)]
            if wizard.buyer:
                domain += [('buyer_code', '=', wizard.buyer.buyer_erp_id)]
            else:
                if record_buyer==1 and record_manager !=1:
                    for item in self.env.user.buyer_id_list:
                        # vendor_code = self.env['iac.vendor'].search([('id', '=', item.id)]).vendor_code
                        buyer_code = self.env['buyer.code'].browse(item).buyer_erp_id
                        buyer_code_list.append(buyer_code)
                        buyer_id_list.append(item)
                    domain += [('buyer_code', 'in', buyer_code_list)]
            if wizard.vendor:
                domain += [('vendor', '=', wizard.vendor.id)]
            else:
                if record_vendor == 1:
                    for item in self.env.user.vendor_ids:
                        # vendor_code = self.env['iac.vendor'].search([('id', '=', item.id)]).vendor_code
                        vendor_id_list.append(item.id)
                    domain += [('vendor', 'in', vendor_id_list)]
            if wizard.material:
                domain += [('material', '=', wizard.material.id)]
            else:
                if record_vendor == 1:
                    for item in self.material_id_list:
                        material_id_list.append(item)
                    domain += [('material', 'in', material_id_list)]
                if record_buyer == 1 and record_manager !=1:
                    for item in self.material_id_list:
                        material_id_list.append(item)
                    domain += [('material', 'in', material_id_list)]
            if wizard.country_id:
                domain += [('country_id', '=', wizard.country_id)]
            if wizard.city:
                domain += [('city', '=', wizard.city)]
            if wizard.open_po:
                open_po_list = []
                self._cr.execute(" select max(fpversion) from iac_traw_data" )
                for item in self.env.cr.dictfetchall():
                    max_fpversion = item['max']
                if record_buyer == 1 and record_manager != 1:
                    if wizard.buyer:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('buyer_id','=',wizard.buyer.id),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                    else:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('buyer_id','in',buyer_id_list),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                if record_vendor == 1:
                    if wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('vendor_id','=',wizard.vendor.id),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                    else:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('vendor_id','in',vendor_id_list),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                if record_manager == 1:
                    if wizard.buyer and wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('buyer_id','=',wizard.buyer.id),
                                         ('vendor_id','=',wizard.vendor.id),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                    if wizard.buyer and not wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('buyer_id','=',wizard.buyer.id),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                    if not wizard.buyer and wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),
                                         ('vendor_id','=',wizard.vendor.id),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)
                    if not wizard.buyer and not wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                        [('fpversion','=',max_fpversion),'|',
                                         ('open_po','>',0),('intransit_qty','>',0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor','=',vendor_id),
                                    ('material','=',material_id)])
                                if country_origin:
                                    open_po_list.append(country_origin.id)

                domain += [('id', 'in', open_po_list)]

            if wizard.stock:
                stock_list = []
                self._cr.execute(" select max(fpversion) from iac_traw_data")
                for item in self.env.cr.dictfetchall():
                    max_fpversion = item['max']
                if record_buyer ==1 and record_manager !=1:
                    if wizard.buyer:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('buyer_id', '=', wizard.buyer.id),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                    else:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('buyer_id', 'in', buyer_id_list),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)

                if record_vendor == 1:
                    if wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('vendor_id', '=', wizard.vendor.id),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                    else:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('vendor_id', 'in', vendor_id_list),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)

                if record_manager == 1:
                    if wizard.buyer and wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('vendor_id','=',wizard.vendor.id),
                                 ('buyer_id','=',wizard.buyer.id),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                    if wizard.buyer and not wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('buyer_id','=',wizard.buyer.id),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                    if not wizard.buyer and wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('vendor_id','=',wizard.vendor.id),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                    if not wizard.buyer and not wizard.vendor:
                        for item in self.env['iac.traw.data'].search(
                                [('fpversion', '=', max_fpversion),
                                 ('stock', '>', 0)]):
                            vendor_id = item.vendor_id.id
                            material_id = item.material_id.id
                            if vendor_id and material_id:
                                country_origin = self.env['iac.country.origin'].search(
                                    [('vendor', '=', vendor_id),
                                     ('material', '=', material_id)])
                                if country_origin:
                                    stock_list.append(country_origin.id)
                domain += [('id', 'in', stock_list)]
            # print wizard.city

            result = self.env['iac.country.origin'].search(domain)
            final_result = []
            for item in result:
                if wizard.buyer:
                    buyer_code_id = self.env['material.master.asn'].browse(item.material.id).buyer_code_id.id
                    # buyer_code_id = self.env['material.master'].browse(item.material.id).buyer_code_id
                    if wizard.buyer.id == buyer_code_id:
                        final_result.append(item)
                else:
                    final_result = result


        action = {
            'domain': [('id', 'in', [x.id for x in final_result])],
            'name': _('Country Origin'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'iac.country.origin'
        }
        return action



