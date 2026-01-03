###############################################################################
#
#    Motakamel Odoo Dashboard
#    Copyright (C) 2024 Motakamel Inc.
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
    'name': 'Motakamel Workflow Dashboard',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 1,
    'summary': 'Workflow-based dashboard for Edafa modules',
    'complexity': "easy",
    'author': 'Motakamel Inc',
    'website': 'https://www.motakamel.org',
           'depends': [
               'base',
               'web',
               'openeducat_core',
               'openeducat_activity',
               'openeducat_admission',
               'openeducat_assignment',
               'openeducat_attendance',
               'openeducat_classroom',
               'openeducat_exam',
               'openeducat_facility',
               'openeducat_fees',
               'openeducat_library',
               'openeducat_parent',
               'openeducat_timetable',
               'grants_training_suite_v2',
           ],
    'data': [
        'security/ir.model.access.csv',
        'data/workflow_data.xml',
        'views/workflow_dashboard_view.xml',
        'views/workflow_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'motakamel_dashboard/static/src/css/workflow_diagram.css',
            'motakamel_dashboard/static/src/js/bootstrap_console_tap.js',
            'motakamel_dashboard/static/src/css/workflow_dashboard.css',
        ],
    },
    'demo': [],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
