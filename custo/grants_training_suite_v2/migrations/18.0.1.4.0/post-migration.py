# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.4.0 - Failed Records Management."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.4.0 - Failed Records Management')
    
    # Initialize failed records fields for existing batches
    batches = env['gr.intake.batch'].search([])
    _logger.info('Found %d existing intake batches to update with failed records management', len(batches))
    
    for batch in batches:
        # Initialize failed records fields
        if not hasattr(batch, 'failed_records_data'):
            batch.failed_records_data = False
        
        # If batch has errors, try to populate failed records data
        if batch.state == 'error' and batch.validation_errors:
            # Create basic failed records structure for existing error batches
            try:
                import json
                failed_data = {
                    'failed_records': [],
                    'total_failed': batch.error_records or 0,
                    'validation_timestamp': batch.validation_date.isoformat() if batch.validation_date else '',
                    'batch_id': batch.id,
                    'batch_name': batch.name,
                    'migration_note': 'Migrated from existing validation errors'
                }
                batch.failed_records_data = json.dumps(failed_data, indent=2)
                _logger.info('Initialized failed records data for batch %s (ID: %s)', batch.name, batch.id)
            except Exception as e:
                _logger.warning('Could not initialize failed records data for batch %s: %s', batch.name, str(e))
    
    _logger.info('Finished updating intake batches with failed records management')
