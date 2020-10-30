# -*- coding: utf-8 -*-

from odoo import models,fields,api
import datetime
from odoo.exceptions import UserError

class CustomsPassPortList(models.Model):
    _name = 'iac.customs.pass.port.list'
    _inherit = 'iac.customs.pass.port.header'
    _table = 'iac_customs_pass_port_header'

    sas_header_list_ids = fields.One2many('iac.asn.customs.sas.search.data','pass_port_id')


class CustomsPassPortListWizard(models.TransientModel):
    _name = 'iac.customs.pass.port.list.wizard'

    plant_id = fields.Many2one('pur.org.data',string='Plant *')
    vendor_id = fields.Many2one('iac.vendor',string='Vendor Code')
    part_id = fields.Many2one('material.master',string='Material')
    pass_port_no = fields.Char('核放单编号')
    rlt_no = fields.Char('关联出入库单')
    pass_port_typecd = fields.Selection([('1', u'先入区后报关'),
                                         ('2', u'一线一体化进出区'),
                                         ('3', u'二线进出区'),
                                         ('4', u'非报关进出区'),
                                         ('5', u'卡口登记货物'),
                                         ('6', u'空车进出区'), ], string=u'核放单类型')
    state = fields.Selection([("wait_lg_approve", u"待关务确认"),
                              ("lg_approved", u'关务核准'),
                              ("lg_reject", u"关务拒绝"),
                              ("interface_submit_success", u"推送海关系统成功"),
                              ("interface_submit_fail", u"推送海关系统失败"),
                              ('to_cancel', u'作废中'),
                              ('cancel', u'厂商取消'),
                              ("done", "done")], string=u"状态")

    def _get_today(self):
        return (datetime.datetime.now()).strftime('%Y-%m-%d')

    def _get_one_month_ago(self):
        return (datetime.datetime.now()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    valid_from = fields.Date('From Date *',default=_get_one_month_ago)
    valid_to = fields.Date('To Date *',default=_get_today)


    @api.multi
    def search_pass_port_list(self):
        domain = []
        for wizard in self:
            if wizard.plant_id:
                domain+=[('plant_id','=',wizard.plant_id.id)]
            if wizard.vendor_id:
                domain+=[('vendor_id','=',wizard.vendor_id.id)]
            else:
                for item in self.env.user.groups_id:
                    if item.name == 'External vendor':
                        raise UserError('操作人员为厂商时,vendor code必填')
            # if wizard.part_id:
            #     domain+=[('plant_id','=',wizard.plant_id.id)]
            if wizard.pass_port_no:
                domain+=[('pass_port_no','=',wizard.pass_port_no)]
            # if wizard.rlt_no:
            #     domain+=[('rlt_no','=',wizard.rlt_no)]
            if wizard.pass_port_typecd:
                domain+=[('pass_port_typecd','=',wizard.pass_port_typecd)]
            if wizard.state:
                domain+=[('state','=',wizard.state)]
            if wizard.valid_from:
                domain+=[('create_date','>=',wizard.valid_from)]
            if wizard.valid_to:
                domain+=[('create_date','<=',wizard.valid_to)]
            result = self.env['iac.customs.pass.port.list'].search(domain)

        action = {
            'domain':[('id','in',[x.id for x in result])],
            'name':'Customs Pass Port List',
            'type':'ir.actions.act_window',
            'view_mode':'tree,form',
            'res_model':'iac.customs.pass.port.list'
        }
        return action


