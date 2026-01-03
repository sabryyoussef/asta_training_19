##############################################################################
#
#    Edafa Inc
#    Copyright (C) 2009-TODAY Edafa Inc(<https://www.edafa.org>).
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
##############################################################################

{
    'name': "Edafa Admission",
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 3,
    'summary': "Manage Admissions""",
    'complexity': "easy",
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': [
        'openeducat_core',
        'openeducat_fees'
    ],
    'data': [
        'security/op_admission_security.xml',
        'security/ir.model.access.csv',
        'data/admission_sequence.xml',
        'data/parameter_data.xml',
        'views/admission_register_view.xml',
        'views/admission_view.xml',
        'report/report_admission_analysis.xml',
        'report/report_menu.xml',
        'wizard/admission_analysis_wizard_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        # Commented out due to missing openeducat_core.op_course_* references
        # These load before CSV courses are imported
        # 'demo/admission_register_demo.xml',
        # 'demo/admission_demo.xml',
    ],
    'test': [],
    'images': [
        'static/description/openeducat-admission_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
