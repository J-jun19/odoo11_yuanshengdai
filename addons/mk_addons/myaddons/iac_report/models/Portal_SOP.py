# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools.translate import _


class IacPortalSOPWizard(models.TransientModel):
    _name = 'v.portal.sop.wizard'