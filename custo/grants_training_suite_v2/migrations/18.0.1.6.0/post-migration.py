# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.6.0 - Session Automation."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.6.0 - Session Automation')
    
    # Initialize session automation fields for existing batches
    batches = env['gr.intake.batch'].search([])
    _logger.info('Found %d existing intake batches to update with session automation fields', len(batches))
    
    for batch in batches:
        # Initialize session automation fields with default values
        batch.write({
            'auto_create_sessions': False,
            'session_creation_enabled': True,
            'sessions_created_count': 0,
            'sessions_scheduled_count': 0,
            'session_creation_date': False,
            'session_creation_errors': False,
            'session_template_id': False,
            'default_session_duration': 1.0,
            'default_session_type': 'online',
            'session_creation_summary': False,
        })
        
        _logger.info('Updated batch %s with session automation fields', batch.name)
    
    # Create default session templates
    _logger.info('Creating default session templates')
    
    # Template 1: Initial Assessment
    initial_template = env['gr.session.template'].create({
        'name': 'Initial Assessment Session',
        'description': 'Template for initial assessment and goal setting sessions',
        'default_topic': 'Initial Assessment and Goal Setting',
        'default_objectives': 'Assess student\'s current skill level\nReview learning goals and expectations\nEstablish communication preferences\nCreate personalized learning plan',
        'default_duration': 1.0,
        'default_type': 'online',
        'target_english_level': 'any',
        'auto_schedule': True,
        'default_schedule_days': 7,
        'is_active': True,
    })
    _logger.info('Created initial assessment template: %s', initial_template.name)
    
    # Template 2: Beginner Level Session
    beginner_template = env['gr.session.template'].create({
        'name': 'Beginner Level Session',
        'description': 'Template for beginner-level English sessions',
        'default_topic': 'Basic English Communication',
        'default_objectives': 'Introduce basic vocabulary\nPractice simple conversations\nBuild confidence in speaking\nReview fundamental grammar',
        'default_duration': 1.0,
        'default_type': 'online',
        'target_english_level': 'beginner',
        'auto_schedule': True,
        'default_schedule_days': 7,
        'is_active': True,
    })
    _logger.info('Created beginner template: %s', beginner_template.name)
    
    # Template 3: Intermediate Level Session
    intermediate_template = env['gr.session.template'].create({
        'name': 'Intermediate Level Session',
        'description': 'Template for intermediate-level English sessions',
        'default_topic': 'Intermediate English Practice',
        'default_objectives': 'Practice complex conversations\nImprove fluency and accuracy\nExpand vocabulary range\nWork on pronunciation',
        'default_duration': 1.5,
        'default_type': 'online',
        'target_english_level': 'intermediate',
        'auto_schedule': True,
        'default_schedule_days': 7,
        'is_active': True,
    })
    _logger.info('Created intermediate template: %s', intermediate_template.name)
    
    # Template 4: Advanced Level Session
    advanced_template = env['gr.session.template'].create({
        'name': 'Advanced Level Session',
        'description': 'Template for advanced-level English sessions',
        'default_topic': 'Advanced English Mastery',
        'default_objectives': 'Master complex language structures\nPractice professional communication\nEnhance critical thinking skills\nPrepare for certification',
        'default_duration': 2.0,
        'default_type': 'online',
        'target_english_level': 'advanced',
        'auto_schedule': True,
        'default_schedule_days': 7,
        'is_active': True,
    })
    _logger.info('Created advanced template: %s', advanced_template.name)
    
    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.6.0 - Session Automation')
