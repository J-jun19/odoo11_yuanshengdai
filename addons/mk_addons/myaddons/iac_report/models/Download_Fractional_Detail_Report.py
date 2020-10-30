# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacDownloadFractionalDetailReportWizard(models.TransientModel):
    _name = 'v.download.fractional.report.wizard'