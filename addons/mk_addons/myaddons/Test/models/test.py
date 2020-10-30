# -*- coding: utf-8 -*-

import json
import xlwt
import time,base64
# import datetime
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from xlsxwriter.workbook import Workbook
from xlrd import open_workbook
from odoo import models, fields, api,odoo_env
import psycopg2
import logging
import xlsxwriter
from dateutil.relativedelta import relativedelta
from StringIO import StringIO
import pdb
import pdfminer
from datetime import datetime, timedelta
import traceback
import sys
import re
from odoo.odoo_env import odoo_env
sys.path.append('D:\work\GOdoo10_IAC\myaddons\iac_vendor_evaluation')



_logger = logging.getLogger(__name__)

class TestByNing(models.Model):

    _name = 'test.by.ning'

    test = fields.Char()

class IacTest1(models.Model):

    _name = 'iac.test.one'

    # test_one_id = fields.One2many('iac.test.two','test_two_id')
    one1_id = fields.Many2one('iac.test.one1')
    two_line_ids = fields.One2many('iac.test.two','test_two_id')
    qty = fields.Float()
    test_char = fields.Char()

    # @api.depends('two_line_ids','two_line_ids.qty')
    # def _get_total_qty(self):
    #     print 1

    @api.multi
    def test_one(self):

        for i in range(5):
            self.env['iac.asn'].create()
        print '\u4eba\u751f\u82e6\u77ed\uff0cpy\u662f\u5cb8'
        print u'\u4eba\u751f\u82e6\u77ed\uff0cpy\u662f\u5cb8'
        score_part_category_ids = []
        part_category_line_ids = []
        vals = {
            'test_char':'2'
        }
        part_category_line_ids.append((0, 0, vals))


        # val = {
        #     'test_one_id':part_category_line_ids
        # }
        # self.env['iac.test.one'].create(vals)

class IacTest2(models.Model):
    _name = 'iac.test.two'

    test_two_id = fields.Many2one('iac.test.one')
    test_char = fields.Char()
    qty = fields.Float()



class IacTest(models.Model):
    """mm下载rfq,选择查询条件进行下载：
    """
    _name = 'iac.test.one1'
    # _inherits = {'muk_dms.file': 'file_id'}

    # directory = fields.Many2one('muk_dms.directory', default=4,string="Directory", required=True)
    # file_id = fields.Many2one('muk_dms.file', string='File Info', required=True, ondelete='cascade', index=True)
    # order_id = fields.Many2one('iac.purchase.order', string='Order Info', index=True)
    vendor = fields.Char('Vendor',compute='_get_vendor')
    one1_line_ids = fields.One2many('iac.test.one','one1_id')
    material = fields.Char('Part')
    qty = fields.Char()
    total_amount = fields.Float(compute='_get_total_qty')
    state = fields.Selection([
        ('finished', 'Finished'),
        ('draft', 'Draft'),  # vendor自己编辑保存的状态
        ('approved', 'Approved'),  # webflow送簽成功

        ('cancel','Cancelled'),# 更新FP成功
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    active = fields.Boolean()
    check = fields.Selection([('YES','yes'),('NO','no')],string='yes/no')
    test_date = fields.Datetime()


    @odoo_env
    @api.model
    def test_by_ning(self):
        for a in self.browse(1):
            a.write({'test_date':datetime.now()})
        self.env.cr.execute("""delete from public.iac_test_one where id=8""")

    def my_function(self):
        print('2223333')
        return {
            'warning': {
                'title': '提示',
                'message': '知道🌶啦！'
            }
        }

    @api.multi
    def _get_vendor(self):
        for v in self:
            v.vendor = '123345'

    @api.multi
    def change_active(self):
        self.env.cr.execute("""SELECT iv.vendor_code,ivr.name1_cn FROM "public"."iac_vendor" iv
INNER JOIN iac_vendor_register ivr on ivr.vendor_id=iv.id; """)
        for a in self.env.cr.dictfetchall():
            print a['vendor_code']
        for item in self:
            item.active = not item.active

        return True

    @api.model
    def clear_all_active(self):
        print 1
        # obj = self.search([('active','=',True)])
        # obj.write({'active':False})
        return True

    def write(self, vals):
        print 222
        result = super(IacTest,self).write(vals)
        return result

    @api.depends('one1_line_ids','one1_line_ids.qty')
    def _get_total_qty(self):
        # print 111
        print self
        for record in self:
            for line in record.one1_line_ids:
                record.total_amount+=line.qty

    @api.onchange('filename')
    def change_directory(self):
        print self.file
        po_dir_rec = self.env["muk_dms.directory"].search([('name', '=', 'po_attachment')], order='id desc', limit=1)
        if not po_dir_rec.exists():
            raise UserError("Dir 'po_attachment' has not found")
        self.directory=po_dir_rec.id

    @api.multi
    def btn_to_approve(self):
        self.state = 'approved'

    @api.multi
    def btn_to_finish(self):
        self.state = 'finished'

    @api.multi
    def btn_to_cancel(self):
        self.state = 'cancel'

    @api.multi
    def btn_to_draft(self):
        self.state = 'draft'

    def button1(self, select_ids):
        print 2  # 选中的订单id

    @api.multi
    def submit_review(self):
        """
        批量提交审核
        :return:
        """
        print 222

    def insert(self,**kwargs):
        print kwargs.get('value')
        print kwargs.get('hello')
    @api.multi
    def test_one(self):
        """
        MM下载自己归属的rfq,这些rfq是AS先前上传的
        :return:
        """
        # _request_stack = werkzeug.local.LocalStack()
        # request = _request_stack()
        # request.env['ir.http'].session_info()
        # print fields.Datetime.to_string(datetime.today())
        print self.env.user.groups_id
        self._cr.execute("""select * from res_currency where name=%s""",('USD123',))
        print self.env.cr.dictfetchall()
        str = datetime.strftime((datetime.strptime('2020-09-05','%Y-%m-%d')).replace(day=1),'%Y-%m-%d')
        print str,type(str)
        asn = self.env['iac.asn.line.buy.sell'].search([('asn_id','=',None)],limit=1)
        print asn.id
        vals = {}
        str = '12344,2334,453'
        vals[str] = 123
        if str in vals.keys():
            vals[str] = vals[str]+222
        print vals
        for key in vals.keys():
            print key
            print key.split(',')[0]
        kwargs = {
            'value':123,
            'hello':1
        }
        self.insert(**kwargs)
        print self.env['iac.smart.po.recover'].search([('order_id','!=',None)])
        a = b'\xe6\x95\xb0\xe6\x8d\xae\xe4\xbc\xa0\xe5\x85\xa5\xe6\x9c\x89\xe8\xaf\xaf'
        print a.decode()



        print 1
        print re.findall(r'[\w-]+', '-asd')
        print re.findall(r'[\w]+', '-asd')
        a = '{:.5f}'.format(40.8/510000)
        vals = {
            'qty':a
        }
        self.env['iac.test.one1'].create(vals)
        self.env.cr.commit()
        print  40.8/510000
        print 37.4 / 350000
        a = {'a':1,'b':2,'c':3}
        if 'd' in a:
            print 1
        print self.env['iac.vendor.fcst.setting'].search([('begin_date', '=', '2019-12-18'),('end_date','=','2019-12-24'),('restart_flag','=',False)])
        print 26/26
        print 26%26
        print ord('A')
        print ord('a')
        print chr(100)
        print (datetime.strptime('2019-12-24','%Y-%m-%d')-datetime.strptime('2019-12-20','%Y-%m-%d')).days
        print (datetime.now()+timedelta(days=30)).strftime('%Y%m%d')
        error_msg = "    raise UserError(u'拥有卡控规则的情况下,没有配置最大可交量:" \
                    "vendor_code 是 ( %s );part_no 是 ( %s )' % (vendor_code, part_no,)) " \
                    "(u'拥有卡控规则的情况下,没有配置最大可交量:vendor_code " \
                    "是 ( 0000231710 );part_no 是 ( 6018A0132601 )', None)".split('UserError:')[0]

        try:
            print 3/0
        except:
            print 1
            l_err_msg = error_msg
            try:
                error_msg = error_msg.split('UserError:')[1]
            except:
                error_msg = l_err_msg
            print error_msg
        print '%'+(datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')+'%'
        self._cr.execute("""select max(id) from iac_job_func_call_log where sap_log_id like %s""",('%'+(datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')+'%',))
        result = self.env.cr.dictfetchone()
        print result['max']
        if result:
            self._cr.execute("""delete from iac_job_func_call_log where id = %s""",(result['max'],))
        if '1' == None:
            print 1
        if '1' == '':
            print 1
        if None in ('B','',None):
            print 3
        self.env.cr.execute("""
                select current_class from iac_supplier_company where company_no='SC002552'
            """)
        result = self.env.cr.dictfetchone()
        print result['current_class'],result['current_class'] == ''
        print sys.path
        try:
            print 3/0
        except:
            print 1
        self.env.cr.execute("select plant from iac_vendor where vendor_code=%s",('0000470305',))
        result = self.env.cr.dictfetchall()
        if result:
            for plant in result:
                print plant['plant'],type(plant['plant'])
        else:
            print 1
        print (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        try:
            date = self.env['iac.customs.sas.header'].browse(228).lg_approve_time
        except:
            print traceback.format_exc()
            # raise UserError(traceback.format_exc())

        vendor_ids=[]
        for vendor_id in self.env['iac.vendor'].search([]):
            vendor_ids.append(vendor_id.id)
        print [(6, 0, vendor_ids)]
        str = '112asdffgdadfasdfa'
        print str[:4]
        print type((datetime.now()).strftime('%Y-%m-%d'))
        print datetime.now()
        print (datetime.now()).strftime('%Y-%m-%d')>'2019-1-7 10:00:00.211223'
        print '11.0'.isdigit()
        # print self.directory
        fp = open('d:\\11.pdf', 'rb')

        print fp


#         print str((datetime.datetime.now()-datetime.timedelta(days=60)).strftime('%Y-%m-%d'))
#         self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw','wang.ningg@iac.com.tw','zhang.pei-wu@iac.com.tw','test subject',['name','email','vendor','po']
# ,[['ning','123','380010','2121'],['ning','1','380','1212'],['ning111','123','123455','1212'],['a','1','112233','1212']],'vendor scoring')

        # workbook = xlsxwriter.Workbook('d://hello.xlsx')
        # worksheet = workbook.add_worksheet()
        # worksheet.write('A1', 48)
        # worksheet.write('A2', 51)
        # worksheet.write_formula(2, 0, '=A1 - A2')
        #
        # format1 = workbook.add_format({'font_color': 'red','border':True})
        # worksheet.conditional_format('A1:A3', {'type': 'cell',
        #                                        'criteria': '<',
        #                                        'value': 0,
        #                                        'format': format1})
        # workbook.close()


class test_model(models.Model):
    _name = 'test.model'
    name = fields.Char(string='Value')

    @api.multi
    def call_up_wizard(self):
      return {
            'name': 'Are you sure?',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
             }

class wizard(models.TransientModel):
    _name = 'wizard'

    yes_no = fields.Char(default='Do you want to proceed?')

    @api.multi
    def yes(self):
        pass
       # sure continue!

    @api.multi
    def no(self):
        pass # don't do anything stupid

