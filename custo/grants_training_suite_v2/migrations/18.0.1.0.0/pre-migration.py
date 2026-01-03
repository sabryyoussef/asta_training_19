# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Migrate existing student records to include Arabic and English name fields."""
    
    # Check if the new fields exist in the database
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'gr_student' 
        AND column_name IN ('name_arabic', 'name_english')
    """)
    
    existing_columns = [row[0] for row in cr.fetchall()]
    
    if 'name_arabic' not in existing_columns:
        _logger.info("Adding name_arabic column to gr_student table")
        cr.execute("ALTER TABLE gr_student ADD COLUMN name_arabic VARCHAR")
    
    if 'name_english' not in existing_columns:
        _logger.info("Adding name_english column to gr_student table")
        cr.execute("ALTER TABLE gr_student ADD COLUMN name_english VARCHAR")
    
    # Update existing records to populate the new fields
    # For existing records, we'll copy the 'name' field to both Arabic and English fields
    # This is a temporary solution - in a real scenario, you'd want to properly populate these fields
    cr.execute("""
        UPDATE gr_student 
        SET name_arabic = name, name_english = name 
        WHERE name_arabic IS NULL OR name_english IS NULL
    """)
    
    # Log the number of records updated
    cr.execute("SELECT COUNT(*) FROM gr_student")
    total_students = cr.fetchone()[0]
    
    _logger.info("Migration completed: %d student records updated with name fields", total_students)
    
    # Note: In a production environment, you would want to:
    # 1. Backup the database before running this migration
    # 2. Have a proper data mapping strategy for Arabic vs English names
    # 3. Validate the data after migration
    # 4. Have a rollback plan if needed
