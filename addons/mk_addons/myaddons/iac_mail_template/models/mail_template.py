# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import datetime
from odoo.odoo_env import odoo_env
import traceback


class IacMailTemplate(models.Model):


    _name = 'iac.email.pool'

    category = fields.Char()
    mail_body = fields.Char()
    mail_subject = fields.Char()
    mail_from = fields.Char()
    mail_to = fields.Char()
    mail_cc = fields.Char()
    state = fields.Char()
    create_date = fields.Datetime()
    create_by = fields.Many2one('res.users')
    send_date = fields.Datetime()


    # 发邮件排队的方法
    def button_to_mail(self,mail_from,mail_to,mail_cc,subject,title,body,category):
        # print self.id
        vals = {}
        str_row = ''
        str_col = ''
        str_body = ''
        str_header = ''
        str_header_row = ''
        # print mail_from,mail_to,mail_cc,subject,title,body,category
        for item in range(len(body)):
            if len(body[item]) == len(title):
                continue
            else:
                raise exceptions.ValidationError('数据传入有误')

        body.insert(0, title)

        for m in range(len(body[0])):
            str_header += '<td>' + body[0][m] + '</td>'
        str_header_row = '<tr bgcolor="#DDDDDD">' \
                      +str_header+ \
                      '</tr>'
        for i in range(len(body)):
            str_col = ''
            for j in range(len(body[0])):
                if i>=1:
                    str_col += '<td>' + body[i][j] + '</td>'

            if str_col != '':
                str_row +='<tr>' +str_col+ '</tr>'
        str_body = '<table border="1" width="100%" cellspacing="0" cellpadding="0">' \
                   +str_header_row+str_row+ \
                   '</table>'
        vals['mail_body'] = str_body
        vals['mail_from'] = mail_from
        vals['mail_to'] = mail_to
        vals['mail_cc'] = mail_cc
        vals['mail_subject'] = subject
        vals['category'] = category
        vals['state'] = 'i'

        # if self.id:
        #     email_id = self.env['iac.email.pool'].browse(self.id)
        #     email_id.write(vals)
        # else:
        email_id = self.env['iac.email.pool'].create(vals)
        email_id.env.cr.commit()
        self._cr.execute("delete from  iac_email_pool where mail_body is null")
        self.env.cr.commit()
        # raise exceptions.ValidationError('已进入队列')



    # 发送邮件的Job
    @odoo_env
    @api.model
    def job_mail_template(self):
        """
        根据公告的频率发送邮件
        :return:
        """
        # 初始状态为i 失败状态为f 成功状态为s
        self._cr.execute("SELECT id FROM iac_email_pool where state='i' order by id LIMIT 50")
        for item in self.env.cr.dictfetchall():

            try:
                mail_task_vals = {
                    "object_id": item['id'],
                    "template_id": "iac_mail_template.evaluation_email"
                }

                # print '*127: ', mail_task_vals
                self.env["iac.mail.task"].add_mail_task(**mail_task_vals)
                vals = {}
                email_id = self.env['iac.email.pool'].browse(item['id'])
                vals['state'] = 's'
                email_id.write(vals)
                email_id.env.cr.commit()
            except:
                vals = {}
                email_id = self.env['iac.email.pool'].browse(item['id'])
                vals['state'] = 'f'
                email_id.write(vals)
                email_id.env.cr.commit()
                traceback.print_exc()

        return True


    # 评鉴筛选排队的Job
    @odoo_env
    @api.model
    def job_evaluation_mail(self):
        """
        根据公告的频率发送邮件
        :return:
        """

        scm_list = []
        qm_list = []

        self._cr.execute("select distinct sc_code,sc_name,scm_user_login,part_category,create_date from v_vendor_evaluation_detail where item_status = 'scoring' and score_group = 'SCM' order by scm_user_login, SC_CODE")
        for item in self.env.cr.dictfetchall():
            # print item['scm_user_login']
            if item['scm_user_login'] not in scm_list:
                scm_list.append(item['scm_user_login'])

        self._cr.execute(
            "select distinct sc_code,sc_name,scm_qm_login,part_category,create_date from v_vendor_evaluation_detail where item_status = 'scoring' and score_group = 'QM' order by scm_qm_login, SC_CODE")
        for item in self.env.cr.dictfetchall():
            # print item['scm_user_login']
            if item['scm_qm_login'] not in qm_list:
                qm_list.append(item['scm_qm_login'])
        for i in range(len(scm_list)):
            # print scm_list[i]
            scm_detail_list = []
            scm_detail_total = []
            partner_id = self.env['res.users'].search([('login','=',scm_list[i])]).partner_id.id
            email = self.env['res.partner'].search([('id','=',partner_id)]).email
            self._cr.execute(
                "select distinct sc_code,sc_name,scm_user_login,part_category,create_date from v_vendor_evaluation_detail where item_status = %s and score_group = %s and scm_user_login = %s order by scm_user_login, SC_CODE",('scoring','SCM',scm_list[i]))
            for item in self.env.cr.dictfetchall():
                # print item
                scm_detail_list = [item['sc_code'],item['sc_name'],item['part_category'],item['create_date']]
                scm_detail_total.append(scm_detail_list)
            self.button_to_mail('iac-ep_support@iac.com.tw',email,'','[系統通知] 如下厂商需要您去评核',['sc_code','sc_name','part_category','create_date'],scm_detail_total,'vendor evaluation alter')

        for i in range(len(qm_list)):
            # print scm_list[i]
            qm_detail_list = []
            qm_detail_total = []
            partner_id = self.env['res.users'].search([('login','=',qm_list[i])]).partner_id.id
            email = self.env['res.partner'].search([('id','=',partner_id)]).email
            self._cr.execute(
                "select distinct sc_code,sc_name,scm_qm_login,part_category,create_date from v_vendor_evaluation_detail where item_status = %s and score_group = %s and scm_qm_login = %s order by scm_qm_login, SC_CODE",('scoring','QM',qm_list[i]))
            for item in self.env.cr.dictfetchall():
                # print item
                qm_detail_list = [item['sc_code'],item['sc_name'],item['part_category'],item['create_date']]
                qm_detail_total.append(qm_detail_list)
            self.button_to_mail('iac-ep_support@iac.com.tw',email,'','[系統通知] 如下厂商需要您去评核',['sc_code','sc_name','part_category','create_date'],qm_detail_total,'vendor evaluation alter')
        return True




