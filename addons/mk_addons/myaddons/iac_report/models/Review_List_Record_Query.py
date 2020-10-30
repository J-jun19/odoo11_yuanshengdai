# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacReviewListRecordQueryReportWizard(models.TransientModel):
    _name = 'v.review.list.record.wizard'