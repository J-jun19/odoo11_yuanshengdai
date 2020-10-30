# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)

def odoo_env(func,**kwargs):
    def __decorator(self,**kwargs):    #add parameter receive the user information
        db_name = self.env.registry.db_name
        db = odoo.sql_db.db_connect(db_name)
        threading.current_thread().dbname = db_name
        cr = db.cursor()
        with api.Environment.manage():
            try:
                env=api.Environment(cr, self.env.uid, {})
                self.env=env
                func(self,**kwargs)

            except:
                traceback.print_exc()
        cr.commit()
        cr.close()

    return __decorator
# 定时任务
class IacMailTask(models.TransientModel):
    _name = 'iac.mail.task'
    _description = 'Mail Task Utils'
    @odoo_env
    def _send_mail(self,**kwargs):
        template_id=kwargs.get("template_id")
        object_id=kwargs.get("object_id")
        try:
            template = self.env.ref(template_id)
            user_admin=self.env["res.users"].browse(SUPERUSER_ID)
            context={
                "system_email":user_admin.email
            }
            template.with_context(context).send_mail(object_id, force_send=True)
        except:
            traceback.print_exc()


    @api.model
    def add_mail_task(self,**kwargs):
        mail_send_thread = threading.Thread(target=self._send_mail, kwargs=kwargs)
        mail_send_thread.start()
