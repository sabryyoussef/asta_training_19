###############################################################################
#
#    Edafa Website Branding
#    Copyright (C) 2024 Edafa Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import base64
from odoo import models, fields, api
from odoo.tools import file_open


class Website(models.Model):
    _inherit = 'website'

    def _default_logo(self):
        """Override default logo with Edafa branding"""
        try:
            with file_open('edafa_website_branding/static/src/img/edafa_logo.svg', 'rb') as f:
                return base64.b64encode(f.read())
        except:
            # Fallback to original logo if Edafa logo not found
            return super()._default_logo()
