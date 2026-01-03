# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.3.0 - Progress Tracking."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.3.0 - Progress Tracking')
    
    # Initialize progress tracking fields for existing batches
    batches = env['gr.intake.batch'].search([])
    _logger.info('Found %d existing intake batches to update with progress tracking', len(batches))
    
    for batch in batches:
        # Set progress fields based on current state
        if batch.state == 'draft':
            batch.upload_progress = 'pending'
            batch.mapping_progress = 'pending'
            batch.validation_progress = 'pending'
            batch.processing_progress = 'pending'
        elif batch.state == 'uploaded':
            batch.upload_progress = 'completed'
            batch.mapping_progress = 'pending'
            batch.validation_progress = 'pending'
            batch.processing_progress = 'pending'
        elif batch.state == 'mapping':
            batch.upload_progress = 'completed'
            batch.mapping_progress = 'completed'
            batch.validation_progress = 'pending'
            batch.processing_progress = 'pending'
        elif batch.state == 'validated':
            batch.upload_progress = 'completed'
            batch.mapping_progress = 'completed'
            batch.validation_progress = 'completed'
            batch.processing_progress = 'pending'
        elif batch.state == 'processed':
            batch.upload_progress = 'completed'
            batch.mapping_progress = 'completed'
            batch.validation_progress = 'completed'
            batch.processing_progress = 'completed'
        elif batch.state == 'error':
            # Set appropriate failed progress based on context
            batch.upload_progress = 'completed'  # Assume upload succeeded if we have data
            batch.mapping_progress = 'completed' if batch.column_mapping else 'pending'
            batch.validation_progress = 'failed'
            batch.processing_progress = 'pending'
        
        _logger.info('Updated batch %s (ID: %s) with progress tracking', batch.name, batch.id)
    
    _logger.info('Finished updating intake batches with progress tracking')
