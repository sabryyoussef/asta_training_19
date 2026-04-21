{
    'name': 'NELC xAPI Console',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 15,
    'summary': 'Standalone console for NELC xAPI settings, manual tests, and logs',
    'description': """
NELC xAPI Console
=================
Standalone application module for managing NELC xAPI integration from Odoo UI.

Features:
- Dedicated settings form for NELC endpoint/auth/platform values
- One-click sync/apply with ir.config_parameter
- Manual statement test runner (registered/initialized/progressed/attempted/rated/earned)
- Event log list/form access from dedicated menu
    """,
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': [
        'base',
        'openeducat_admission',
        'nelc_xapi_admission',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/nelc_xapi_console_settings_views.xml',
        'views/nelc_xapi_manual_test_views.xml',
        'views/nelc_xapi_event_log_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
