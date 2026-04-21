###############################################################################
#
#    NELC xAPI Admission Integration
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

{
    'name': 'NELC xAPI Admission Integration',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 10,
    'summary': 'Send xAPI "registered" statements to the NELC LRS upon admission submission',
    'description': """
NELC xAPI Admission MVP
=======================
Sends an xAPI "registered" statement to the NELC Learning Record Store (LRS)
immediately after a student's admission record is created.

Features:
- National ID field captured on admission wizard (10-digit, starts with 1/2/4)
- NELC tracking fields on op.admission (sent flag, UUID, last error)
- Backend-only HTTP client using Python requests / urllib
- Credentials managed via environment variables → ir.config_parameter
- Non-blocking: failures are logged but do not interrupt the student flow

Configuration:
Set the following environment variables on Odoo.sh (or copy .env.example):
  NELC_LRS_ENDPOINT   – HTTPS URL of the NELC LRS statements endpoint
  NELC_LRS_AUTH_HEADER – Full Authorization header value (e.g. "Basic xxx")
  NELC_PLATFORM_KEY   – Platform identifier assigned by NELC
  ODOO_BASE_URL        – Public base URL of this Odoo instance (optional)
    """,
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': [
        'base',
        'website',
        'portal',
        'openeducat_core',
        'openeducat_admission',
        'edafa_website_branding',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/nelc_config_init.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
}
