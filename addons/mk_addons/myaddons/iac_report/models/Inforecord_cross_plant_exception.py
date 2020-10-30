# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class InforecordCrossPlantExceptionSpot(models.Model):
    _name = "v.inforecord.cross.plant.exception.spot"
    _description = "Inforecord Cross Plant Exception Spot"
    _auto = False
    _order = "id desc"

    webflow_number = fields.Char('Webflow 單號')
    approve_date_web = fields.Date('Info Record 建立日期')
    new_plant = fields.Char('廠區')
    new_vendor = fields.Char('廠商代碼')
    new_vendor_name = fields.Char('廠商名稱')
    material = fields.Char('料號')
    material_desc = fields.Char('Desc')
    new_buyer_code = fields.Char('採購代碼')
    new_buyer_name = fields.Char('採購名稱')
    new_currency = fields.Char('幣別')
    new_price = fields.Float('Info Record價格', digits=(18, 6))
    new_division = fields.Char('Division Code')
    new_division_desc = fields.Char('Division Name')
    new_valid_from = fields.Date('生效日期')
    new_valid_to = fields.Date('失效日期')
    diff = fields.Char('高價/低價')
    old_plant = fields.Char('廠區')
    old_vendor = fields.Char('廠商代碼')
    old_vendor_name = fields.Char('廠商名稱')
    old_currency = fields.Char('幣別')
    old_price = fields.Float('RFQ價格', digits=(18, 6))
    old_division = fields.Char('Division Code')
    old_division_desc = fields.Char('Division Name')
    cost_up_reason_id = fields.Char('高於其他原因說明代碼（AS）')
    cost_up_reason_desc = fields.Char('高於其他原因說明（AS）')
    old_buyer_code = fields.Char('採購代碼')
    old_buyer_name = fields.Char('採購名稱')
    old_valid_from = fields.Date('生效日期')
    old_valid_to = fields.Date('失效日期')
    data_type = fields.Char('Data Type')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_inforecord_cross_plant_exception_spot')
        self._cr.execute("""CREATE OR REPLACE VIEW public.v_inforecord_cross_plant_exception_spot AS
               select row_number()over()as id,* from
	           (select 
               r.webflow_number as webflow_number,
               r.approve_date_web as approve_date_web,
               pod.plant_code as new_plant,
               v.vendor_code as new_vendor,
               v."name" as new_vendor_name,
               mm.part_no as material,
               md.part_description as material_desc,
               r.buyer_code as new_buyer_code,
               bc.buyer_name as new_buyer_name,
               rc."name" as new_currency,
               r.input_price as new_price,
               dc.division as new_division,
               dc.division_description as new_division_desc,
               r.valid_from as new_valid_from,
               r.valid_to as new_valid_to,
               rno.price_compare as diff,
               pod1.plant_code as old_plant,
               v1.vendor_code as old_vendor,
               v1."name" as old_vendor_name,
               rc1."name" as old_currency,
               r1.input_price as old_price,
               dc1.division as old_division,
               dc1.division_description as old_division_desc,
               r.cost_up_reason_id as cost_up_reason_id,
               rcur.description as cost_up_reason_desc,
               r.buyer_code as old_buyer_code,
               bc1.buyer_name as old_buyer_name,
               r1.valid_from as old_valid_from,
               r1.valid_to as old_valid_to,
               '新旧单价对比' as data_type
               from iac_rfq_new_vs_old rno
         inner join iac_rfq r on r.id = rno.current_rfq_id
         inner join iac_rfq r1 on r1.id = rno.old_rfq_id
         inner join iac_vendor v on v.id = r.vendor_id
         inner join pur_org_data pod on pod.id = r.plant_id
         inner join material_master mm on mm.id = r.part_id
         inner join material_description md on md.part_no = mm.part_no and md.plant_code = mm.plant_code   
         inner join buyer_code bc on bc.id = r.buyer_code     
         inner join res_currency rc on rc.id = r.currency_id
         inner join division_code dc on dc.id = r.division_id
         inner join division_code dc1 on dc1.id = r1.division_id
         inner join iac_vendor v1 on v1.id = r1.vendor_id
         inner join pur_org_data pod1 on pod1.id = r1.plant_id
         inner join res_currency rc1 on rc1.id = r1.currency_id
         inner join buyer_code bc1 on bc1.id = r1.buyer_code
         inner join iac_rfq_cost_up_reason rcur on rcur.id = r.cost_up_reason_id
         where rno.new_flag = 'Y'                       
           and (rno.id,rno.current_rfq_id,rno.old_rfq_id) 
               in (select max(id),max(current_rfq_id),max(old_rfq_id) 
                     from iac_rfq_new_vs_old rno1
                      where rno1.current_rfq_id = rno.current_rfq_id and rno1.old_rfq_id = rno.old_rfq_id
                   )                  
           and r.valid_from <= cast(now() as date) and r.valid_to >= cast(now() as date)
           and r1.valid_from <= cast(now() as date) and r1.valid_to >= cast(now() as date)
           and r.approve_date_web is not null
           and abs(rno.ratio) > 0.03
           union           
        select distinct 
               r.webflow_number as webflow_number,
               r.approve_date_web as approve_date_web,
               pod.plant_code as new_plant,
               v.vendor_code as new_vendor,
               v."name" as new_vendor_name,
               mm.part_no as material,
               md.part_description as material_desc,
               r.buyer_code as new_buyer_code,
               bc.buyer_name as new_buyer_name,
               rc."name" as new_currency,
               r.input_price as new_price,
               dc.division as new_division,
               dc.division_description as new_division_desc,
               r.valid_from as new_valid_from,
               r.valid_to as new_valid_to,
               case 
                 when (r.input_price - r1.input_price) >0 then 'up'
                 when (r.input_price - r1.input_price) <0 then 'down'
                 when (r.input_price - r1.input_price) = 0 then 'nochange'
               end as diff,
               pod1.plant_code as old_plant,
               v1.vendor_code as old_vendor,
               v1."name" as old_vendor_name,
               rc1."name" as old_currency,
               r1.input_price as old_price,
               dc1.division as old_division,
               dc1.division_description as old_division_desc,
               r.cost_up_reason_id as cost_up_reason_id,
               rcur.description as cost_up_reason_desc,
               r.buyer_code as old_buyer_code,
               bc1.buyer_name as old_buyer_name,
               r1.valid_from as old_valid_from,
               r1.valid_to as old_valid_to,
               '第一笔单价是现货商' as data_type 
               from iac_rfq_new_vs_old rno
         inner join iac_rfq r on r.id = rno.current_rfq_id
         inner join iac_vendor v on v.id = r.vendor_id
         inner join pur_org_data pod on pod.id = r.plant_id
         inner join material_master mm on mm.part_no = r.part_code
         inner join material_description md on md.part_no = mm.part_no and md.plant_code = mm.plant_code   
         inner join buyer_code bc on bc.id = r.buyer_code     
         inner join res_currency rc on rc.id = r.currency_id
         inner join division_code dc on dc.id = r.division_id        
         inner join iac_rfq_cost_up_reason rcur on rcur.id = r.cost_up_reason_id
         inner join (select id,vendor_id,part_id,plant_id,currency_id,buyer_code,input_price,division_id,valid_from,valid_to 
                     from iac_rfq ir1
                     where (ir1.vendor_id,ir1.part_id,id
                           ) in 
                    (select vs.id,mm1.id,min(rs.id) from   material_master mm1 
                                                    inner join iac_rfq rs on rs.part_id = mm1.id
                                                    inner join iac_vendor vs on vs.id = rs.vendor_id
                                                    inner join iac_vendor_account_group ivag on ivag.account_group = vs.vendor_account_group
                     where exists (select 1 from iac_rfq_new_vs_old irnvo 
                                            inner join iac_rfq ir on ir.id = irnvo.current_rfq_id
                                            inner join material_master mms on mms.id = ir.part_id 
                                   where mms.part_no = mm1.part_no 
                                  )
          and rs.valid_from <= cast(now() as date)    
          and ivag.vendor_type = 'spot'
          and rs.state = 'sap_ok'          
          group by vs.id,mm1.id
                    )
                    )r1 on r1.part_id = r.part_id 
         inner join division_code dc1 on dc1.id = r1.division_id
         inner join iac_vendor v1 on v1.id = r1.vendor_id
         inner join pur_org_data pod1 on pod1.id = r1.plant_id
         inner join res_currency rc1 on rc1.id = r1.currency_id
         inner join buyer_code bc1 on bc1.id = r1.buyer_code        
         where r.approve_date_web is not null    
         union           
        select distinct
               r.webflow_number as webflow_number,
               r.approve_date_web as approve_date_web,
               pod.plant_code as new_plant,
               v.vendor_code as new_vendor,
               v."name" as new_vendor_name,
               mm.part_no as material,
               md.part_description as material_desc,
               r.buyer_code as new_buyer_code,
               bc.buyer_name as new_buyer_name,
               rc."name" as new_currency,
               r.input_price as new_price,
               dc.division as new_division,
               dc.division_description as new_division_desc,
               r.valid_from as new_valid_from,
               r.valid_to as new_valid_to,
               case 
                 when (r.input_price - r1.input_price) >0 then 'up'
                 when (r.input_price - r1.input_price) <0 then 'down'
                 when (r.input_price - r1.input_price) = 0 then 'nochange'
               end as diff,
               pod1.plant_code as old_plant,
               v1.vendor_code as old_vendor,
               v1."name" as old_vendor_name,
               rc1."name" as old_currency,
               r1.input_price as old_price,
               dc1.division as old_division,
               dc1.division_description as old_division_desc,
               r.cost_up_reason_id as cost_up_reason_id,
               rcur.description as cost_up_reason_desc,
               r.buyer_code as old_buyer_code,
               bc1.buyer_name as old_buyer_name,
               r1.valid_from as old_valid_from,
               r1.valid_to as old_valid_to,
               '现货商相关' as data_type 
               from iac_rfq_new_vs_old rno
         inner join iac_rfq r on r.id = rno.current_rfq_id
         inner join iac_vendor v on v.id = r.vendor_id
         inner join pur_org_data pod on pod.id = r.plant_id
         inner join material_master mm on mm.part_no = r.part_code
         inner join material_description md on md.part_no = mm.part_no and md.plant_code = mm.plant_code   
         inner join buyer_code bc on bc.id = r.buyer_code     
         inner join res_currency rc on rc.id = r.currency_id
         inner join division_code dc on dc.id = r.division_id
         inner join iac_rfq_spot_last r1 on  r1.part_id = r.part_id and r1.vendor_id = r.vendor_id
         inner join division_code dc1 on dc1.id = r1.division_id
         inner join iac_vendor v1 on v1.id = r1.vendor_id
         inner join pur_org_data pod1 on pod1.id = r1.plant_id
         inner join res_currency rc1 on rc1.id = r1.currency_id
         inner join buyer_code bc1 on bc1.id = r1.buyer_code
         inner join iac_rfq_cost_up_reason rcur on rcur.id = r.cost_up_reason_id
         where r.approve_date_web is not null) t
              """)


class InforecordCrossPlantException(models.Model):
    _name = "v.inforecord.cross.plant.exception"
    _description = "Inforecord Cross Plant Exception"
    _auto = False
    _order = "id desc"

    webflow_number = fields.Char('Webflow 單號')
    approve_date_web = fields.Date('Info Record 建立日期')
    new_plant = fields.Char('廠區')
    new_vendor = fields.Char('廠商代碼')
    new_vendor_name = fields.Char('廠商名稱')
    material = fields.Char('料號')
    material_desc = fields.Char('Desc')
    new_buyer_code = fields.Char('採購代碼')
    new_buyer_name = fields.Char('採購名稱')
    new_currency = fields.Char('幣別')
    new_price = fields.Float('Info Record價格', digits=(18, 6))
    new_division = fields.Char('Division Code')
    new_division_desc = fields.Char('Division Name')
    new_valid_from = fields.Date('生效日期')
    new_valid_to = fields.Date('失效日期')
    diff = fields.Char('高價/低價')
    old_plant = fields.Char('廠區')
    old_vendor = fields.Char('廠商代碼')
    old_vendor_name = fields.Char('廠商名稱')
    old_currency = fields.Char('幣別')
    old_price = fields.Float('RFQ價格', digits=(18, 6))
    old_division = fields.Char('Division Code')
    old_division_desc = fields.Char('Division Name')
    cost_up_reason_id = fields.Char('高於其他原因說明代碼（AS）')
    cost_up_reason_desc = fields.Char('高於其他原因說明（AS）')
    old_buyer_code = fields.Char('採購代碼')
    old_buyer_name = fields.Char('採購名稱')
    old_valid_from = fields.Date('生效日期')
    old_valid_to = fields.Date('失效日期')
    data_type = fields.Char('Data Type')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'v_inforecord_cross_plant_exception')
        self._cr.execute("""CREATE OR REPLACE VIEW public.v_inforecord_cross_plant_exception AS
               select rno.id,
               r.webflow_number as webflow_number,
               r.approve_date_web as approve_date_web,
               pod.plant_code as new_plant,
               v.vendor_code as new_vendor,
               v."name" as new_vendor_name,
               mm.part_no as material,
               md.part_description as material_desc,
               r.buyer_code as new_buyer_code,
               bc.buyer_name as new_buyer_name,
               rc."name" as new_currency,
               r.input_price as new_price,
               dc.division as new_division,
               dc.division_description as new_division_desc,
               r.valid_from as new_valid_from,
               r.valid_to as new_valid_to,
               rno.price_compare as diff,
               pod1.plant_code as old_plant,
               v1.vendor_code as old_vendor,
               v1."name" as old_vendor_name,
               rc1."name" as old_currency,
               r1.input_price as old_price,
               dc1.division as old_division,
               dc1.division_description as old_division_desc,
               r.cost_up_reason_id as cost_up_reason_id,
               rcur.description as cost_up_reason_desc,
               r.buyer_code as old_buyer_code,
               bc1.buyer_name as old_buyer_name,
               r1.valid_from as old_valid_from,
               r1.valid_to as old_valid_to,
               '新旧单价对比' as data_type
               from iac_rfq_new_vs_old rno
         inner join iac_rfq r on r.id = rno.current_rfq_id
         inner join iac_rfq r1 on r1.id = rno.old_rfq_id
         inner join iac_vendor v on v.id = r.vendor_id
         inner join pur_org_data pod on pod.id = r.plant_id
         inner join material_master mm on mm.id = r.part_id
         inner join material_description md on md.part_no = mm.part_no and md.plant_code = mm.plant_code
         inner join buyer_code bc on bc.id = r.buyer_code
         inner join res_currency rc on rc.id = r.currency_id
         inner join division_code dc on dc.id = r.division_id
         inner join division_code dc1 on dc1.id = r1.division_id
         inner join iac_vendor v1 on v1.id = r1.vendor_id
         inner join pur_org_data pod1 on pod1.id = r1.plant_id
         inner join res_currency rc1 on rc1.id = r1.currency_id
         inner join buyer_code bc1 on bc1.id = r1.buyer_code
         inner join iac_rfq_cost_up_reason rcur on rcur.id = r.cost_up_reason_id
         where rno.new_flag = 'Y'
           and (rno.id,rno.current_rfq_id,rno.old_rfq_id)
               in (select max(id),max(current_rfq_id),max(old_rfq_id)
                     from iac_rfq_new_vs_old rno1
                      where rno1.current_rfq_id = rno.current_rfq_id and rno1.old_rfq_id = rno.old_rfq_id
                   )
           and r.valid_from <= cast(now() as date) and r.valid_to >= cast(now() as date)
           and r1.valid_from <= cast(now() as date) and r1.valid_to >= cast(now() as date)
           and r.approve_date_web is not null
           and abs(rno.ratio) > 0.03
           """)


class InforecordCrossPlantExceptionWizard(models.TransientModel):
    _name = 'inforecord.cross.plant.exception.wizard'

    new_plant = fields.Many2one('pur.org.data', string="Plant",
                                domain=lambda self: [('id', 'in', self.env.user.plant_id_list)], index=True)
    new_vendor = fields.Many2one('iac.vendor', string="Vendor", index=True)
    cost_up_reason_id = fields.Many2one('iac.rfq.cost.up.reason', string="Cost Up Reason", index=True)
    one_or_many_material = fields.Selection([('one_material_code', '單顆材料查詢'), ('many_material_code', '多顆材料查詢')]
                                            , string=u"選擇查詢材料方式")
    part_id = fields.Char(string="查询单颗材料，至少输入前4码 Material")
    many_material = fields.Text(string="查询多颗材料 Material")
    approve_date_from = fields.Date(string="签核日期 Begin *")
    approve_date_to = fields.Date(string="签核日期 End *")
    vendor_spot = fields.Boolean(string="顯示現貨商價格")

    @api.onchange('one_or_many_material')
    def _onchange_part_id(self):
        if self.one_or_many_material == 'one_material_code':
            self.many_material = False
        if self.one_or_many_material == 'many_material_code':
            self.part_id = False

    # @api.onchange('one_or_many_material')
    # def _onchange_plant_id_part_id(self):
    #     self.part_id = False
    #     if self.one_or_many_material:
    #         return {'domain': {'part_id': [('one_or_many_material', '=', self.one_or_many_material)]}}

    @api.multi
    def search_inforecord_cross_plant_exception(self):
        self.ensure_one()
        # result = []
        domain = []
        action_type = 0
        for wizard in self:
            if wizard.new_plant:
                domain += [('new_plant', '=', wizard.new_plant.plant_code)]
            if wizard.new_vendor:
                domain += [('new_vendor', '=', wizard.new_vendor.vendor_code)]
            if wizard.part_id:
                domain += [('material', 'ilike', wizard.part_id)]
            if wizard.many_material:
                part_no_list = wizard.many_material.split('\n')
                domain += [('material', 'in', part_no_list)]
            if wizard.approve_date_from:
                domain += [('approve_date_web', '>=', wizard.approve_date_from)]
            if wizard.approve_date_to:
                domain += [('approve_date_web', '<=', wizard.approve_date_to)]
            if wizard.vendor_spot == True:
                action_type = 1
                result = self.env['v.inforecord.cross.plant.exception.spot'].search(domain)
            elif wizard.vendor_spot == False:
                result = self.env['v.inforecord.cross.plant.exception'].search(domain)

        if action_type == 1:
            action = {
                'domain': [('id', 'in', [x.id for x in result])],
                'name': _('Info Record Cross Plant Exception Spot'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'v.inforecord.cross.plant.exception.spot'
            }
            return action
        else:
            action = {
                'domain': [('id', 'in', [x.id for x in result])],
                'name': _('Info Record Cross Plant Exception'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'v.inforecord.cross.plant.exception'
            }
            return action
