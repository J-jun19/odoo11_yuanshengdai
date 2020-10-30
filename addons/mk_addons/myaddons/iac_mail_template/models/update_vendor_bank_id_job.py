# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.odoo_env import odoo_env


class UpdateVendorBankIdJob(models.Model):
    _name = 'update.vendor.bank.id.job'

    @odoo_env
    @api.model
    def job_update_vendor_bank_id_job(self):
        self._cr.execute("""update iac_vendor v set bank_id = vb.id
                             from
                            (select vendor_code, id from vendor_bank ) vb
                             where vb.vendor_code = v.vendor_code
                             and v.bank_id is null""")
