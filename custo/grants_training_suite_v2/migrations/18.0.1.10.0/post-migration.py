# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.10.0 - Phase 4.2 Grade Calculation Improvements."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.10.0 - Phase 4.2 Grade Calculation Improvements')

    # Initialize grade history for existing homework attempts with grades
    homework_attempts = env['gr.homework.attempt'].search([('grade', '>', 0)])
    _logger.info('Found %d homework attempts with grades to initialize grade history.', len(homework_attempts))

    for attempt in homework_attempts:
        # Create initial grade history entry
        env['gr.homework.grade.history'].create({
            'homework_attempt_id': attempt.id,
            'old_grade': 0.0,
            'new_grade': attempt.grade,
            'change_date': attempt.create_date or fields.Datetime.now(),
            'changed_by_id': attempt.create_uid.id if attempt.create_uid else env.user.id,
            'change_reason': 'Initial grade (migrated from existing data)',
        })
        _logger.info('Created initial grade history for homework attempt %s (ID: %s)', attempt.name, attempt.id)

    _logger.info('Phase 4.2 Grade Calculation Improvements migration completed successfully')
    _logger.info('New features available:')
    _logger.info('- Enhanced grade validation with improved rules')
    _logger.info('- Automatic grade history tracking for all grade changes')
    _logger.info('- Grade history model with detailed change tracking')
    _logger.info('- Enhanced homework attempt views with grade history')
    _logger.info('- Auto-update Grade % when Grade is entered')
    _logger.info('- Comprehensive grade change audit trail')
    
    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.10.0.')
