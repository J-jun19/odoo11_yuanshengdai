# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.odoo_env import odoo_env


class UpdateExpirationIsoState(models.Model):
    _name = 'update.expiration.iso.state'

    @odoo_env
    @api.model
    def job_update_expiraton_iso_state_job(self):
        self._cr.execute("""update iac_vendor_register_attachment ivra set state = 'inactive' from 
                           (select id,sub_group from iac_attachment_type)iat
                           where ivra."type" = iat.id
                           and iat.sub_group = 'iso'
                           and (ivra.expiration_date < CURRENT_DATE)
                           and ivra.state = 'active'
                           """)
