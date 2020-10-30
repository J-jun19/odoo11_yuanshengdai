# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
from lxml import etree


class ConfirmVersion(models.Model):
    # 目的：iac_column_title 檔,  tile 的動態標題
    _name = 'iac.tcolumn.title'
    _description = "column title"
    _order = 'fpversion desc'

    division = fields.Char(string='division')
    flag = fields.Char(string='flag')
    fpversion = fields.Char(string='fpversion')
    plant = fields.Char(string='plant')
    vendor_code = fields.Char(string='vendor_code')
    vendor_name = fields.Char(string='vendor_name')
    buyer_code = fields.Char(string='buyer_code')
    po = fields.Char(string='po')
    pr = fields.Char(string='pr')
    quota = fields.Char(string='quota')
    remark = fields.Char(string='remark')
    round_value = fields.Char(string='round_value')
    stock = fields.Char(string='stock')
    intransit_qty = fields.Char(string='intransit_qty')
    leadtime = fields.Char(string='leadtime')
    material = fields.Char(string='material')
    max_surplus_qty = fields.Char(string='max_surplus_qty')
    mfgpn_info = fields.Char(string='mfgpn_info')
    mquota_flag = fields.Char(string='mquota_flag')
    open_po = fields.Char(string='open_po')
    creation_date = fields.Char(string='creation_date')
    custpn_info = fields.Char(string='custpn_info')
    description = fields.Char(string='description')
    alt_flag = fields.Char(string='alt_flag')
    alt_grp = fields.Char(string='alt_grp')
    b001 = fields.Char(string='b001')
    b002 = fields.Char(string='b002')
    b004 = fields.Char(string='b004')
    b005 = fields.Char(string='b005')
    b012 = fields.Char(string='b012')
    b017b = fields.Char(string='b017b')
    b902q = fields.Char(string='b902q')
    b902s = fields.Char(string='b902s')
    qty_m1 = fields.Char(string='qty_m1')
    qty_m2 = fields.Char(string='qty_m2')
    qty_m3 = fields.Char(string='qty_m3')
    qty_m4 = fields.Char(string='qty_m4')
    qty_m5 = fields.Char(string='qty_m5')
    qty_m6 = fields.Char(string='qty_m6')
    qty_m7 = fields.Char(string='qty_m7')
    qty_m8 = fields.Char(string='qty_m8')
    qty_m9 = fields.Char(string='qty_m9')
    qty_w1 = fields.Char(string='qty_w1')
    qty_w1_r = fields.Char(string='qty_w1_r')
    qty_w10 = fields.Char(string='qty_w10')
    qty_w11 = fields.Char(string='qty_w11')
    qty_w12 = fields.Char(string='qty_w12')
    qty_w13 = fields.Char(string='qty_w13')
    qty_w2 = fields.Char(string='qty_w2')
    qty_w3 = fields.Char(string='qty_w3')
    qty_w4 = fields.Char(string='qty_w4')
    qty_w5 = fields.Char(string='qty_w5')
    qty_w6 = fields.Char(string='qty_w6')
    qty_w7 = fields.Char(string='qty_w7')
    qty_w8 = fields.Char(string='qty_w8')
    qty_w9 = fields.Char(string='qty_w9')
    sap_log_id = fields.Char(string="Sap log Info", index=True)
    sap_temp_id = fields.Integer(string="Sap Temp Info", index=True)
    storage_location = fields.Char()


    # 參考 : https://git.vauxoo.com/vauxoo-dev/odoo/commit/21db945b887688d651bd2520a7be21034fdc1485
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(ConfirmVersion, self).fields_view_get(view_id, view_type,toolbar=toolbar, submenu=submenu)
        asset_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        doc = etree.XML(result['arch'])

        if doc.xpath("//field[@name='fpversion']"):
            node = doc.xpath("//field[@name='fpversion']")[0]
            node.set('string', 'tt fpversion tt')

        if doc.xpath("//field[@name='qty_m1']"):
            node = doc.xpath("//field[@name='qty_m1']")[0]
            node.set('string', 'tt qty_m1 tt')

        # if doc.xpath("//field[@name='method_end']"):
        #     node = doc.xpath("//field[@name='method_end']")
        #     node.set('invisible', '1')

        result['arch'] = etree.tostring(doc)
        return result

