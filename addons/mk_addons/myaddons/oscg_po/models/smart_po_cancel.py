# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class IacSmartPoCancel(models.Model):
    _name = 'iac.smart.po.cancel'
    _order = 'vendor_code,order_code desc,order_line_code'

    order_id = fields.Many2one('iac.purchase.order')
    order_code = fields.Char()
    order_line_id = fields.Many2one('iac.purchase.order.line')
    order_line_code = fields.Char()
    storage_location_id = fields.Many2one('iac.storage.location.address')
    storage_location = fields.Char()
    odoo_storage_location = fields.Char(related='order_line_id.storage_location',string='Storage location')
    po_date = fields.Date(string='PO date')
    vendor_id = fields.Many2one('iac.vendor')
    vendor_code = fields.Char()
    vendor_name = fields.Char(related='vendor_id.name')
    division_id = fields.Many2one('division.code')
    division_code = fields.Char()
    part_id = fields.Many2one('material.master')
    part_no = fields.Char()
    purchasing_group = fields.Char(string='Purchasing group')
    odoo_buyer_code = fields.Char(related='order_id.buyer_erp_id',string='Purchasing group')
    description = fields.Char(related='part_id.part_description')
    plant_id = fields.Many2one('pur.org.data')
    plant_code = fields.Char(string='Plant')
    fp_open_po_quantity = fields.Float()
    odoo_open_po = fields.Float(compute='_get_open_po_qty',string='Odoo open PO')
    suggested_cancel_quantity = fields.Float()
    round_value = fields.Integer(string='Round value(MOQ)')
    cancel_quantity = fields.Float()
    delivery_date = fields.Date()
    new_price = fields.Float()
    odoo_price = fields.Float(related='order_line_id.price')
    odoo_price_unit = fields.Integer(related='order_line_id.price_unit')
    intransit_asn_quantity = fields.Float()
    odoo_intransit_asn_quantity = fields.Float(compute='_get_intransit_asn_quantity',string='Odoo intransit ASN quantity')
    original_quantity = fields.Float()
    odoo_original_quantity = fields.Float(related='order_line_id.line_history_id.quantity')
    po_change_id = fields.Many2one('iac.purchase.order.change')
    po_line_change_id = fields.Many2one('iac.purchase.order.line.change')
    is_used = fields.Boolean(default=False)
    state = fields.Selection([('current', 'Current'), ('history', 'History')])
    sap_log_id = fields.Char()
    po_state = fields.Selection(related='order_id.state')
    exception_flag = fields.Boolean(default=False)  #如果存在po在change中，flag标记为True

    @api.multi
    def write(self, vals):
        if vals.get('cancel_quantity',False)<0:
            raise exceptions.ValidationError('PO:'+self.order_code+',item:'+self.order_line_code+',part no:'+self.part_no+'cancel数量不能小于0')
        result = super(IacSmartPoCancel,self).write(vals)
        return result

    @api.multi
    def _get_intransit_asn_quantity(self):
        for po in self:
            asn_count, gr_count, open_count = self.get_count(
                po.order_id.id, po.order_line_id.id, po.part_id.id)
            po.odoo_intransit_asn_quantity = asn_count

    @api.multi
    def _get_open_po_qty(self):
        for po in self:
            asn_count, gr_count, open_count = self.get_count(
                po.order_id.id, po.order_line_id.id, po.part_id.id)
            po.odoo_open_po = open_count

    #根据order id,order line id以及part id获取asn数，gr数和open po数
    def get_count(self,order_id,order_line_id,part_id):
        self.env.cr.execute("""select * from public.proc_po_part_info(%s,%s,%s)""",
                            (order_id, order_line_id, part_id))
        for count in self.env.cr.dictfetchall():
            asn_count = count['o_asn_count']
            gr_count = count['o_gr_count']
            open_count = count['o_open_count']

        return asn_count,gr_count,open_count

    @api.multi
    def _validate_po_cancel(self):
        for po in self:
            if po.exception_flag == True:
                raise exceptions.ValidationError('PO:'+po.order_code+',item:'+po.order_line_code+'在资料导入过程中存在po change,无法作cancel')
            if po.po_state not in ['pending', 'unapproved', 'vendor_confirmed', 'vendor_exception',
                                   'wait_vendor_confirm']:
                raise exceptions.ValidationError(
                    'PO:' + po.order_code + ',item:' + po.order_line_code + '在操作期间状态改变为' + po.po_state + ',不可以做po change,请刷新页面重新载入')
            if po.is_used == True:
                raise exceptions.ValidationError('PO:' + po.order_code + ',item:' + po.order_line_code + '已经做过cancel')
            asn_count, gr_count, open_count = self.get_count(po.order_id.id,po.order_line_id.id,po.part_id.id)
            # 获取cancel之后该po line的数量
            new_qty = po.order_line_id.quantity-po.cancel_quantity
            if new_qty < asn_count:
                raise exceptions.ValidationError('PO:'+po.order_code+',item:'+po.order_line_code+',part no:'+po.part_no+'cancel之后的数量不能小于在途数！')
            # FP过来的cancel数字要小于等于OpenPO数
            if po.cancel_quantity > open_count:
                raise exceptions.ValidationError('PO:'+po.order_code+',item:'+po.order_line_code+',part no:'+po.part_no+'cancel数量不能大于open po数！')
            if po.cancel_quantity > po.order_line_id.quantity:
                raise exceptions.ValidationError('PO:'+po.order_code+',item:'+po.order_line_code+',part no:'+po.part_no+'cancel数量不能大于po总数！')


    @api.multi
    def cancel_po(self):
        self._cr.execute("  select count(*) as job_count  from ep_temp_master.extractlog "
                         "  where extractname in ( select extractname from ep_temp_master.extractgroup "
                         "                                        where extractgroup = 'SMART_PO_CANCEL' ) "
                         "      and extractstatus = 'ODOO_PROCESS'   ")
        for job in self.env.cr.dictfetchall():
            if job['job_count'] and job['job_count'] > 0:
                raise exceptions.ValidationError(' 正在轉資料 ,請勿操作 ! ')
        # 对po做校验
        self._validate_po_cancel()
        # 对选中po做去重操作
        po_list = []
        po_change_list = []
        for po in self:
            if po.order_id not in po_list:
                po_list.append(po.order_id)

        # 每个po调用一次创建po change的方法
        for po_obj in po_list:
            po_obj.button_to_change()

        # 将cancel的数量写到产生的po change对应的line上
        for smart_po in self:
            # 根据order id以及order line id找到新产生的po change line
            change_line_obj = self.env['iac.purchase.order.line.change'].search(
                [('order_id', '=', smart_po.order_id.id), ('order_line_id', '=', smart_po.order_line_id.id)],
                order='id desc', limit=1)
            if smart_po.cancel_quantity < smart_po.order_line_id.quantity:
                change_line_obj.write({'new_qty': smart_po.order_line_id.quantity-smart_po.cancel_quantity})
            else:
                change_line_obj.write({'odoo_deletion_flag': True})
            smart_po.write({'po_change_id': change_line_obj.change_id.id, 'po_line_change_id': change_line_obj.id,
                            'is_used': True})
        # 对po change做去重操作
        for po_change in self:
            if po_change.po_change_id not in po_change_list:
                po_change_list.append(po_change.po_change_id)

        # 每个po change调用送签方法
        for po_change_obj in po_change_list:
            po_change_obj.button_to_approve()

        return self.env['warning_box'].info(title='提示', message='PO Cancel成功！')
