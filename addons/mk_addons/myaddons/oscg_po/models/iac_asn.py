# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
import  traceback
import threading
import types

class IacPurchaseOrderAsn(models.Model):
    """
    用来规避记录规则的模型,不要附加记录规则
    """
    _name = "iac.purchase.order.asn"
    _inherit = "iac.purchase.order"
    _table="iac_purchase_order"
    order_line = fields.One2many("iac.purchase.order.line.asn", "order_id", string="PO Line Number")

class IacPurchaseOrderLineAsn(models.Model):
    """
    用来规避记录规则的模型,不要附加记录规则
    """
    _name = "iac.purchase.order.line.asn"
    _inherit = "iac.purchase.order.line"
    _table="iac_purchase_order_line"
    order_id = fields.Many2one('iac.purchase.order.asn', string="Purchase Order")
    new_asn_qty=fields.Integer(string='New Asn Qty',default=0)

class MaterialMasterPoLine(models.Model):
    """PO Change从表，同时是PO Line Delivery Change主表"""
    _name = "material.master.po.line"
    _inherit="material.master"
    _table="material_master"
    _description = "Material Mater In Po Line"
    _order = 'id desc'

class GoodsReceipts(models.Model):
    _inherit = "goods.receipts"
    _description = u"Goods Receipts"

    asn_id = fields.Many2one('iac.asn', string='ASN')
    asn_line_id = fields.Many2one('iac.asn.line', string='ASN Line')
    po_id = fields.Many2one('iac.purchase.order', string='PO Line')
    po_line_id = fields.Many2one('iac.purchase.order.line', string='PO Line')

#专用来避免iac.vendor 模型应用buyer_email筛选规则,专门用在asn相关表中
class IacVendorAsn(models.Model):
    _inherit="iac.vendor"
    _name='iac.vendor.asn'
    _table='iac_vendor'
    _description = u"Vendor Info"

class iacASN(models.Model):
    _name = 'iac.asn'
    _rec_name = 'asn_no'

    _sql_constraints = [
        ('iac_asn_asn_no_uniq', 'unique (asn_no)', "asn_no already exists !"),
    ]
    asn_no = fields.Char('ASN No',index=True)
    asn_date = fields.Date('ASN Date',default=fields.Date.today)
    asn_status = fields.Char('ASN Status')
    company_code = fields.Char('Company Code')
    plant_id = fields.Many2one('pur.org.data','Plant')
    buyer_erp_id = fields.Integer('Purchasing Group')
    vendor_id = fields.Many2one('iac.vendor.asn', string='Vendor')
    vendor_code=fields.Char(related="vendor_id.vendor_code",string='Supplier Code')
    vendor_name=fields.Char(related="vendor_id.name",string='Supplier Name')
    customer_currency = fields.Many2one('res.currency','Currency')
    customer_country = fields.Many2one('res.country','Country')

    total_cartons = fields.Float('Total Cartons')
    standard_carrier = fields.Char('Standard Carrier')
    packing_list_no = fields.Char('Packing List No')
    has_attachment = fields.Char('Has AttachMent')
    ship_from = fields.Char('Ship From')
    ship_from_country = fields.Char('Ship from Country')
    airbill_no = fields.Char('AirBill No')
    housebill_no = fields.Char('House Bill No')

    etd_date = fields.Date('ETD Date',default=fields.date.today())
    eta_date = fields.Date('ETA Date')
    delivery_days = fields.Integer('Delivery Days',default=1)
    ship_to = fields.Char('Ship To')

    transport_type = fields.Char('Trasnport Type')
    transport_id = fields.Integer('Transport ID')
    from_source = fields.Char('FromSource')
    source_id = fields.Integer('Source ID')
    line_ids = fields.One2many('iac.asn.line','asn_id','ASN Line')

    type = fields.Char('type')
    vendor_asn = fields.Char('VENDOR_ASN')
    state = fields.Selection([('draft','Draft'),
                              ('sap_ok','SAP OK'),
                              ('sap_fail','SAP Fail'),
                              ('odoo_cancel','ODOO Cancel'),
                              ],string='Status',default='draft')
    rpc_note = fields.Text('SAP RPC Note')
    storage_location = fields.Char('Storage location')
    pull_signal_id=fields.Char("Pull Singal Id From SAP")
    sap_flag=fields.Boolean("SAP Create Done",default=False)
    create_mode = fields.Selection([('buyer_create','Buyer Create'),('vendor_create','Vendor Create'),('auto_create','System Auto Create')],default="buyer_create")

    #数据迁移所使用的字段
    plant_code=fields.Char(string="Plant",index=True)
    vendor_code_sap=fields.Char(string="vendor Code",index=True)
    buyer_code=fields.Char(string="Buyer Code",index=True)
    customer_country_name=fields.Char(string="Customer Conuntry Name",index=True)
    customer_currency_name=fields.Char(string="Customer Currency Name",index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID")

    @api.model
    def get_query_sql(self,args,offset=0,limit=None,order=None):
        query = self._where_calc(args)
        self._apply_ir_rules(query, 'read')
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or 'where 1=1'
        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''

        new_where_clause_params=[]
        for param_val in where_clause_params:
            if type(param_val) is types.StringType:
                param_val='\''+param_val+'\''
                new_where_clause_params.append(param_val)
            else:

                new_where_clause_params.append(param_val)
        where_str=where_str%tuple(new_where_clause_params)

        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + order_by + limit_str + offset_str
        return from_clause,where_str,order_by,limit_str,offset_str

"""
    @api.model
    def search_count(self, args):
        #result=super(iacASN,self).search_count(args)

        from_clause,where_str,order_by,limit_str,offset_str=self.get_query_sql(args)
        main_query_str = 'SELECT count(*) FROM ' + from_clause + where_str
        from_clause_sub,where_str_sub,order_by_sub,limit_str_sub,offset_str_sub=self.env["iac.asn.line"].get_query_sql([])
        query_str_sub = 'SELECT "%s".id FROM '%self._table+ from_clause_sub + where_str_sub
        main_query_str+=' and exists ('
        main_query_str+=query_str_sub
        main_query_str+=' and "iac_asn_line"."asn_id"="iac_asn"."id"'+')'

        self.env.cr.execute(main_query_str)
        result_count=self.env.cr.fetchall()
        result=result_count[0][0]

        return result

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):


        #result=super(iacASN,self).search(args, offset, limit, order, count)

        from_clause,where_str,order_by,limit_str,offset_str=self.get_query_sql(args, offset, limit, order)
        main_query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str
        from_clause_sub,where_str_sub,order_by_sub,limit_str_sub,offset_str_sub=self.env["iac.asn.line"].get_query_sql([])
        query_str_sub = 'SELECT "%s".id FROM ' % self.env["iac.asn.line"]._table + from_clause_sub + where_str_sub
        main_query_str+=' and exists ('
        main_query_str+=query_str_sub
        main_query_str+=' and "iac_asn_line"."asn_id"="iac_asn"."id"'+')'+order_by+limit_str+offset_str

        self.env.cr.execute(main_query_str)
        result_ids=self.env.cr.fetchall()
        id_list=[]
        for asn_id in result_ids:
            id_list.append(asn_id[0])
        result=self.browse(id_list)

        return result
"""

class iacASNLine(models.Model):
    _name = 'iac.asn.line'
    _order='asn_line_no asc'
    asn_id = fields.Many2one('iac.asn','ASN')
    asn_line_no = fields.Integer('ASN Line No',index=True)
    po_id = fields.Many2one('iac.purchase.order.asn','PO')
    po_line_id = fields.Many2one('iac.purchase.order.line.asn','PO Line')
    part_id = fields.Many2one('material.master.po.line','Part No')
    part_desc=fields.Char(related='part_id.part_description',string='Part Description')
    asn_qty = fields.Float('ASN QTY',digits=(18,4))
    qty_per_carton = fields.Integer('QTY per Carton')
    packing_note = fields.Char('Packing Note')
    gr_status = fields.Char('GR Status')
    gross_weight = fields.Float('Gross Weight')
    net_weight = fields.Float('Net Weight')
    amount = fields.Float('Amount',precision=(18, 2))
    invoice_no = fields.Char('Invoice No')
    origin_country = fields.Many2one("res.country",string='Original Country')

    max_qty = fields.Integer('Max QTY',compute='_compute_max_qty')
    REDUCE_QTY = fields.Char('REDUCE_QTY')
    rpc_note = fields.Text('SAP RPC Note')
    storage_location = fields.Char('Storage location')
    plant_code = fields.Char('Plant')
    vendor_asn=fields.Char("Vendor Asn")
    vendor_asn_item=fields.Char("Vendor Asn Item")

    gr_line_ids=fields.One2many('goods.receipts','asn_line_id',string='GR Line List')#当前asn入料信息列表
    on_road_qty = fields.Float(string="In Transit ASN Quantity", compute='_taken_on_road_qty')
    gr_qty = fields.Float(string="GR Quantity", compute='_taken_gr_qty')

    asn_no=fields.Char('ASN No',index=True)
    vendor_id=fields.Many2one('iac.vendor.asn',string="Vendor Info")
    plant_id=fields.Many2one('pur.org.data',string="Plant Info")
    buyer_id = fields.Many2one('buyer.code', string="Buyer Code Info", index=True)
    buyer_erp_id = fields.Char(string="Purchasing Group", index=True)

    #数据迁移所使用的字段
    plant_code=fields.Char(string="Plant",index=True)
    vendor_code_sap=fields.Char(string="vendor Code",index=True)
    buyer_code=fields.Char(string="Buyer Code",index=True)
    asn_no_sap=fields.Char(string="asn code",index=True)
    po_code=fields.Char(string="PO Code",index=True)
    part_no=fields.Char(string="Part No",index=True)
    po_line_code=fields.Char(string="PO Line Code",index=True)
    sap_key=fields.Char(string="SAP KEY")
    sap_log_id=fields.Char(string="SAP LOG ID",index=True)
    miss_flag=fields.Integer(string="Miss Flag")

    #为数据权限配置增加的字段
    source_code=fields.Char(string="Source Code",index=True)
    cancel_qty = fields.Float('New ASN QTY',digits=(18,4))

    #废弃字段
    document_line_erp_id = fields.Char(string='document_line_erp_id')

    @api.one
    def _taken_gr_qty(self):
        """
        从gr表中获取相应的入料汇总数据
        :return:
        """
        gr_qty_sum=0
        for gr_line in self.gr_line_ids:
            gr_qty_sum=gr_qty_sum+gr_line.qty_received
        self.gr_qty=gr_qty_sum

    @api.one
    @api.depends('asn_qty','gr_qty')
    def _taken_on_road_qty(self):
        """
        从ASN表中获取相应的asn汇总数据
        :return:
        """
        self.on_road_qty=self.asn_qty-self.gr_qty


    @api.multi
    @api.depends('asn_qty','part_id')
    def _compute_max_qty(self):
        for r in self:
            domain=[('vendor_id','=',r.vendor_id.id),('plant_id','=',r.plant_id.id),('part_id','=',r.part_id.id),('state','=','done')]
            max_qty_rec=self.env['asn.maxqty'].search(domain,limit=1)
            r.max_qty = max_qty_rec.remained_qty

    @api.model
    def get_query_sql(self,args,offset=0,limit=None,order=None):
        query = self._where_calc(args)
        self._apply_ir_rules(query, 'read')
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or 'where 1=1'
        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''

        new_where_clause_params=[]
        for param_val in where_clause_params:
            if type(param_val) is types.StringType:
                param_val='\''+param_val+'\''
                new_where_clause_params.append(param_val)
            else:

                new_where_clause_params.append(param_val)
        where_str=where_str%tuple(new_where_clause_params)


        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + order_by + limit_str + offset_str
        return from_clause,where_str,order_by,limit_str,offset_str