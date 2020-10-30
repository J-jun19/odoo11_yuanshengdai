# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
# from lxml import etree


class ConfirmVersion(models.Model):
    """    tconfirm_version檔, 用來記錄每個採購release出去的版本號
        """
    _name = 'iac.tconfirm.version'
    _description = "tConfirm version"
    _order = 'id desc, version'

    raw_id = fields.Many2one('iac.traw.data', string="raw data id",index=True)
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code", index=True)
    version = fields.Char(string="version", required=True) # buyer release出去的版本號
    fpversion = fields.Char(string="fpversion", required=True)
    division_id = fields.Many2one('division.code', string='Division Info',index=True)
    vendor_id = fields.Many2one('iac.vendor', string="Vendor id",index=True)
    material_id = fields.Many2one('material.master', 'Material', index=True)
    # status = fields.Char(string="status")  # status 有效 # T: true有效,F:  false無效, O: old 舊版
    status = fields.Selection([
        ('T', ''),  # T: true有效
        ('F', '無效'),  # F:  false 無效
        ('O', '舊版')  # O: old 舊版
    ], string='Status', readonly=True, index=True, copy=False)
    vendor_code = fields.Char(string="Vendor_code", related="vendor_id.vendor_code")
    material_code = fields.Char(string='Material_code', related='material_id.part_no')
    division_code = fields.Char(string='Division_code', related='division_id.division')

    # 紀錄 "调用SAP接口"是否成功的欄位____s
    state = fields.Selection([
        ('pending', 'Pending'),  # 等待拋轉中
        ('fp error', 'FP Error'),  # 通知FP失敗
        ('finished', 'Finished'),  # 更新FP成功
    ], string='Status', readonly=True, index=True, copy=False, default='pending', track_visibility='onchange')
    state_msg = fields.Char()
    # 紀錄 "调用SAP接口"是否成功的欄位____e

    group_id = fields.Many2one('iac.tconfirm.version.group')  # 20180702 laura add  for整批拋FP
    edi_version = fields.Char(string="edi_version" )  # EDI 830 用  version 20180704 laura add
    storage_location_id = fields.Many2one('iac.storage.location.address', string='Storage Location')  # 181211 ning add


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        tree_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'iac_forecast_release_to_vendor.view_confirm_version_list')
        res = super(ConfirmVersion, self).fields_view_get(view_id=tree_view_id,view_type=view_type,
                                                          toolbar=toolbar,submenu=submenu)

        label_value="Status"

        res['arch'] = res['arch'].replace('<field name="status" string="status" ',
                                          '<field name="status" string="%s" ')% (label_value)

        return res

class ConfirmVersionTemp(models.Model):

    _name = 'iac.tconfirm.version.temp'
    _description = "tConfirm version temp table"
    _order = 'id desc, version'

    _inherit = ['iac.tconfirm.version']
