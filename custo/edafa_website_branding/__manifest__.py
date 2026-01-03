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

{
    'name': 'Edafa Website Portal',
    'version': '19.0.1.2.0',
    'license': 'LGPL-3',
    'category': 'Website',
    'sequence': 1,
    'summary': 'Edafa website branding and student admission portal with multi-step wizard',
    'complexity': "easy",
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': [
        'base',
        'website',
        'portal',
        'openeducat_core',
        'openeducat_admission',
        'payment',  # For payment.transaction integration
        'account',  # For account.move (invoices)
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_security.xml',
        'data/website_data.xml',
        'data/website_menu.xml',
        'data/payment_data.xml',
        'views/admission_portal_templates.xml',
        'views/admission_wizard_templates.xml',
        'views/admission_thank_you_template.xml',
        'views/my_applications_template.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        # Frontend assets (loaded on website/portal pages)
        'web.assets_frontend': [
            'edafa_website_branding/static/src/css/admission_portal.css',
            'edafa_website_branding/static/src/css/wizard.css',
            'edafa_website_branding/static/src/js/admission_form.js',
            'edafa_website_branding/static/src/js/application_wizard.js',
        ],
    },
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
