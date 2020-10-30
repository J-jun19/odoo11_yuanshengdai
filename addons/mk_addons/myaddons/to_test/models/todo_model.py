# -*- coding: utf-8 -*-
from odoo import models, fields,api
class TodoTask(models.Model):
    _name = 'todo.task'
    _description = "To-do Task"
    name = fields.Char('Description', required=True)
    is_done = fields.Boolean('Done')
    active = fields.Boolean('Active?', default=True)

    @api.multi
    def do_toggle_done(self):
        for task in self:
            task.is_done = not task.is_done
        return True

    @api.multi
    def do_clear_done(self):
        dones = self.search([('is_done','=',True)])
        dones.write({'active':False})
        return True

class TodoTask(models.Model):
    _inherit = 'todo.task'

    user_id = fields.Many2one('res.users', string='Responsible')
    date_deadline = fields.Date('Deadline')
    name = fields.Char(help="what need to be done?")

    @api.multi
    def do_toggle_done(self):
        print 2
        return super(TodoTask,self).do_toggle_done()