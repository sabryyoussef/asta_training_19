# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_create_alumni_portal = fields.Boolean(
        'Auto Create Alumni Portal',
        config_parameter='motakamel_alumni.auto_create_alumni_portal',
        help="Automatically create portal access for alumni"
    )
    
    alumni_portal_access_days = fields.Integer(
        'Portal Access Days',
        config_parameter='motakamel_alumni.alumni_portal_access_days',
        default=365,
        help="Number of days alumni can access portal (0 for unlimited)"
    )

