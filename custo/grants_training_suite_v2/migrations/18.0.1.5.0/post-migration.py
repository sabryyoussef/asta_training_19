# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.5.0 - Notifications for Batch Completion/Errors."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.5.0 - Notifications')
    
    # Initialize notification fields for existing batches
    batches = env['gr.intake.batch'].search([])
    _logger.info('Found %d existing intake batches to update with notification fields', len(batches))
    
    for batch in batches:
        # Initialize notification fields with default values
        batch.write({
            'notification_sent': False,
            'notification_type': 'none',
            'notification_message': False,
            'notification_recipients': False,
            'notification_date': False,
            'email_notification_enabled': True,
            'in_app_notification_enabled': True,
        })
        
        # If batch is already processed, we could send a retrospective notification
        # but we'll leave that for manual action to avoid spam
        if batch.state == 'processed':
            _logger.info('Batch %s is already processed - notification fields initialized', batch.name)
        elif batch.state == 'error':
            _logger.info('Batch %s is in error state - notification fields initialized', batch.name)
    
    _logger.info('Finished updating intake batches with notification fields')
