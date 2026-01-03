# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

{
    'name': 'Motakamel Alumni Management',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 15,
    'summary': 'Manage Alumni Records and Engagement',
    'complexity': "easy",
    'author': 'Motakamel Training Academy',
    'website': 'https://www.motakamel.com',
    'depends': [
        'openeducat_core',
        'website',
        'portal',
        'mail',
    ],
    'data': [
        # Security
        'security/alumni_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/alumni_sequence.xml',
        'data/alumni_data.xml',
        
        # Views
        'views/alumni_view.xml',
        # 'views/alumni_group_view.xml',  # TODO: Create
        # 'views/alumni_event_view.xml',  # TODO: Create
        # 'views/alumni_job_view.xml',  # TODO: Create
        # 'views/alumni_portal_templates.xml',  # TODO: Create
        # 'views/alumni_website_templates.xml',  # TODO: Create
        
        # Reports (TODO: Create these files)
        # 'report/alumni_report.xml',
        # 'report/alumni_card_template.xml',
        
        # Wizards (TODO: Create these files)
        # 'wizard/convert_to_alumni_wizard_view.xml',
        # 'wizard/alumni_bulk_email_wizard_view.xml',
        
        # Menus
        'menus/alumni_menu.xml',
    ],
    'demo': [
        # 'demo/alumni_demo.xml',  # TODO: Create demo data
    ],
    'assets': {
        'web.assets_backend': [
            'motakamel_alumni/static/src/css/alumni.css',
            'motakamel_alumni/static/src/js/alumni_dashboard.js',
        ],
        'web.assets_frontend': [
            'motakamel_alumni/static/src/css/alumni_portal.css',
        ],
    },
    # 'images': [
    #     # TODO: Uncomment when banner image is created
    #     # 'static/description/motakamel_alumni_banner.jpg',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

