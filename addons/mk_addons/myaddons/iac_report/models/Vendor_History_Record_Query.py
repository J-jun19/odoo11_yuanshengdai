# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacVendorHistoryRecordQueryReportWizard(models.TransientModel):
    _name = 'v.vendor.history.record.wizard'