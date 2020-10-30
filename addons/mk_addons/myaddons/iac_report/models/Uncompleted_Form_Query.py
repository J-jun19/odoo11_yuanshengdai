# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacUncompletedFormQueryReportWizard(models.TransientModel):
    _name = 'v.uncompleted.form.wizard'