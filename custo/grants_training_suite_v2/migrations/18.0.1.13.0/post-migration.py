# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.13.0 - Certificate Validation and Verification."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.13.0 - Certificate Validation and Verification')

    # Initialize new success criteria fields for existing course integrations
    course_integrations = env['gr.course.integration'].search([])
    _logger.info('Found %d existing course integrations to update with success criteria fields.', len(course_integrations))

    for course in course_integrations:
        # Set default values for new fields if they don't exist or are 0
        updates = {}
        
        if not hasattr(course, 'min_sessions_required') or not course.min_sessions_required:
            updates['min_sessions_required'] = 0  # Default to 0 (no minimum requirement)
        
        if not hasattr(course, 'min_homework_required') or not course.min_homework_required:
            updates['min_homework_required'] = 0  # Default to 0 (no minimum requirement)
        
        if not hasattr(course, 'min_elearning_progress') or not course.min_elearning_progress:
            updates['min_elearning_progress'] = 80.0  # Default to 80% minimum eLearning progress
        
        # Update the course with new field values
        if updates:
            course.write(updates)
            _logger.info('Updated course integration %s (ID: %s) with success criteria fields: %s', 
                        course.name, course.id, updates)

    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.13.0.')

    # Test the new certificate eligibility report functionality
    try:
        _logger.info('Testing certificate eligibility report functionality...')
        report_data = env['gr.certificate'].get_certificate_eligibility_report()
        _logger.info('Certificate eligibility report test successful. Found %d completed students.', 
                    report_data['total_completed_students'])
    except Exception as e:
        _logger.error('Error testing certificate eligibility report: %s', str(e))
