# -*- coding:utf-8 -*-

from odoo import fields, models, api


class IacAsnAutoCreateLog(models.Model):
    _name = 'iac.asn.auto.create.log'

    asn_id = fields.Integer()
    ori_state = fields.Char()
    new_state = fields.Char()
    action = fields.Char()
    message = fields.Char()
    begin_time = fields.Datetime()
    end_time = fields.Datetime()
    flag = fields.Char()

    @api.model
    def insert_log(self, asn_id, state, action, message, begin_time, end_time, table_name, log_id):
        # domain = [('id', '=', log_id)]
        log_header = self.browse(log_id)
        if not log_header:
            vals = {
                'asn_id': asn_id,
                'ori_state': state,
                'new_state': state,
                'action': action,
                'message': message,
                'begin_time': begin_time,
                'end_time': begin_time,
                'flag': table_name
            }
            new_log = self.create(vals)
            return new_log.id
        else:
            vals = {
                # 'id': log_id,
                # 'asn_id': asn_id,
                'new_state': state,
                # 'action': action,
                'message': message,
                # 'begin_time': begin_time,
                'end_time': end_time,
                # 'flag': table_name
            }
            log_header.write(vals)
            return log_header.id


class IacAsnLineAutoCreateLog(models.Model):
    _name = 'iac.asn.line.auto.create.log'

    asn_line_id = fields.Integer()
    ori_state = fields.Char()
    new_state = fields.Char()
    action = fields.Char()
    message = fields.Char()
    begin_time = fields.Datetime()
    end_time = fields.Datetime()
    flag = fields.Char()

    @api.model
    def insert_log(self, asn_line_id, state, action, message, begin_time, end_time, table_name, log_line_id):

        # domain = [('id', '=', log_line_id)]
        log_line = self.browse(log_line_id)
        if not log_line:
            vals = {
                'asn_line_id': asn_line_id,
                'ori_state': state,
                'new_state': state,
                'action': action,
                'message': message,
                'begin_time': begin_time,
                'end_time': begin_time,
                'flag': table_name
            }
            new_log_line = self.create(vals)
            return new_log_line.id
        else:
            vals = {
                # 'asn_line_id': asn_line_id,
                'new_state': state,
                # 'action': action,
                'message': message,
                # 'begin_time': begin_time,
                'end_time': end_time,
                # 'flag': table_name
            }
            log_line.write(vals)
            return log_line.id
