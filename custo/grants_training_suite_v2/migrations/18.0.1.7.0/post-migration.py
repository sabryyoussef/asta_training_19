# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.7.0 - Training Programs Improvements."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.7.0 - Training Programs Improvements')
    
    # Log that enrollment wizard model has been created
    _logger.info('Enrollment wizard model created with enhanced student enrollment functionality')
    
    # Check if any existing training programs need to be updated
    training_programs = env['gr.training.program'].search([])
    _logger.info('Found %d existing training programs', len(training_programs))
    
    for program in training_programs:
        _logger.info('Training program: %s (Status: %s)', program.name, program.status)
        
        # Log course integrations for each program
        if program.course_integrations:
            _logger.info('  Course integrations:')
            for course in program.course_integrations:
                _logger.info('    - %s (Status: %s, Auto-enroll: %s)', 
                           course.name, course.status, course.auto_enroll_eligible)
    
    # Check existing students for enrollment eligibility
    eligible_students = env['gr.student'].search([
        ('state', 'in', ['eligible', 'assigned_to_agent'])
    ])
    _logger.info('Found %d eligible students for enrollment', len(eligible_students))
    
    # Log student distribution by English level
    for level in ['beginner', 'intermediate', 'advanced']:
        count = len(eligible_students.filtered(lambda s: s.english_level == level))
        _logger.info('  Students with %s English level: %d', level, count)
    
    # Check existing progress trackers (enrollments)
    progress_trackers = env['gr.progress.tracker'].search([])
    _logger.info('Found %d existing progress trackers (enrollments)', len(progress_trackers))
    
    # Log enrollment status distribution
    statuses = ['not_started', 'in_progress', 'completed', 'cancelled']
    for status in statuses:
        count = len(progress_trackers.filtered(lambda p: p.status == status))
        _logger.info('  Progress trackers with %s status: %d', status, count)
    
    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.7.0 - Training Programs Improvements')
    _logger.info('Enhanced enrollment functionality is now available with the new enrollment wizard')
