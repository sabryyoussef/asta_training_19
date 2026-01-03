# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.8.0 - Course Integration fixes and eLearning improvements."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.8.0 - Course Integration fixes')
    
    # Log course integration enhancements
    course_integrations = env['gr.course.integration'].search([])
    _logger.info('Found %d course integrations with enhanced enrollment functionality', len(course_integrations))
    
    for integration in course_integrations:
        _logger.info('Course integration: %s (Status: %s, Auto-enroll: %s)', 
                    integration.name, integration.status, integration.auto_enroll_eligible)
        
        # Log eLearning course integration
        if integration.elearning_course_id:
            _logger.info('  eLearning Course: %s', integration.elearning_course_id.name)
        else:
            _logger.info('  eLearning Course: Not linked')
    
    # Log training programs with course integrations
    training_programs = env['gr.training.program'].search([])
    _logger.info('Found %d training programs', len(training_programs))
    
    for program in training_programs:
        _logger.info('Training program: %s (Status: %s, Courses: %d)', 
                    program.name, program.status, len(program.course_integrations))
    
    # Log enrollment wizard enhancements
    _logger.info('Enrollment wizard enhanced to support both training programs and individual course integrations')
    
    # Check existing progress trackers (enrollments)
    progress_trackers = env['gr.progress.tracker'].search([])
    _logger.info('Found %d existing progress trackers (enrollments)', len(progress_trackers))
    
    # Log enrollment status distribution
    statuses = ['not_started', 'in_progress', 'completed', 'cancelled']
    for status in statuses:
        count = len(progress_trackers.filtered(lambda p: p.status == status))
        _logger.info('  Progress trackers with %s status: %d', status, count)
    
    # Log eLearning integration status
    elearning_courses = env['slide.channel'].search([])
    _logger.info('Found %d eLearning courses available for integration', len(elearning_courses))
    
    for course in elearning_courses[:5]:  # Log first 5 courses
        _logger.info('  eLearning Course: %s (Visibility: %s)', 
                    course.name, course.visibility)
    
    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.8.0 - Course Integration fixes')
    _logger.info('Enhanced course integration enrollment functionality is now available')
