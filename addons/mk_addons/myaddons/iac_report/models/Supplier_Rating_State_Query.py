# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacSupplierRatingStateQueryReportWizard(models.TransientModel):
    _name = 'v.supplier.rating.state.wizard'