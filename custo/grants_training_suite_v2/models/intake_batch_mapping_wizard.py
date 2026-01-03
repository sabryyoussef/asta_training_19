# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IntakeBatchMappingWizard(models.TransientModel):
    _name = 'gr.intake.batch.mapping.wizard'
    _description = 'Intake Batch Column Mapping Wizard'

    intake_batch_id = fields.Many2one(
        'gr.intake.batch',
        string='Intake Batch',
        required=True
    )
    
    available_columns = fields.Text(
        string='Available Columns',
        help='JSON string containing the detected columns from the uploaded file'
    )
    
    preview_data = fields.Text(
        string='Preview Data',
        help='JSON string containing sample data for preview'
    )
    
    column_mapping = fields.Text(
        string='Column Mapping',
        help='JSON string containing the mapping between file columns and student fields'
    )
    
    # Dynamic fields for mapping interface - using Char fields instead of Selection
    name_mapping = fields.Char(
        string='Student Name (English)',
        help='Map to student name field'
    )
    
    name_arabic_mapping = fields.Char(
        string='Student Name (Arabic)',
        help='Map to Arabic name field'
    )
    
    name_english_mapping = fields.Char(
        string='Student Name (English) - Alternative',
        help='Map to alternative English name field'
    )
    
    email_mapping = fields.Char(
        string='Email Address',
        help='Map to email field'
    )
    
    phone_mapping = fields.Char(
        string='Phone Number',
        help='Map to phone field'
    )
    
    birth_date_mapping = fields.Char(
        string='Birth Date',
        help='Map to birth date field'
    )
    
    gender_mapping = fields.Char(
        string='Gender',
        help='Map to gender field'
    )
    
    nationality_mapping = fields.Char(
        string='Nationality',
        help='Map to nationality field'
    )
    
    native_language_mapping = fields.Char(
        string='Native Language',
        help='Map to native language field'
    )
    
    english_level_mapping = fields.Char(
        string='English Level',
        help='Map to English level field'
    )
    
    has_certificate_mapping = fields.Char(
        string='Has Certificate',
        help='Map to certificate field'
    )
    
    certificate_type_mapping = fields.Char(
        string='Certificate Type',
        help='Map to certificate type field'
    )
    
    certificate_date_mapping = fields.Char(
        string='Certificate Date',
        help='Map to certificate date field'
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values from context."""
        defaults = super().default_get(fields_list)
        
        # Get data from context
        intake_batch_id = self.env.context.get('default_intake_batch_id')
        available_columns = self.env.context.get('default_available_columns', '[]')
        preview_data = self.env.context.get('default_preview_data', '[]')
        column_mapping = self.env.context.get('default_column_mapping', '{}')
        
        if intake_batch_id:
            defaults['intake_batch_id'] = intake_batch_id
        if available_columns:
            defaults['available_columns'] = available_columns
        if preview_data:
            defaults['preview_data'] = preview_data
        if column_mapping:
            defaults['column_mapping'] = column_mapping
            
        return defaults

    @api.onchange('available_columns')
    def _onchange_available_columns(self):
        """Update available columns when they change."""
        if not self.available_columns:
            return
        
        try:
            columns = json.loads(self.available_columns)
            # Store available columns for validation
            self.available_columns_list = columns
                
        except (json.JSONDecodeError, TypeError) as e:
            _logger.error('Error parsing available columns: %s', str(e))

    @api.model
    def create(self, vals):
        """Override create to set up mapping fields."""
        record = super().create(vals)
        record._setup_mapping_fields()
        return record

    def _setup_mapping_fields(self):
        """Set up the mapping fields with auto-detected values."""
        if not self.available_columns:
            return
        
        try:
            columns = json.loads(self.available_columns)
            
            # Apply auto-detected mapping if available
            auto_mapping = {}
            if self.column_mapping:
                try:
                    auto_mapping = json.loads(self.column_mapping)
                except json.JSONDecodeError:
                    pass
            
            # Map auto-detected values to field mappings
            mapping_fields = {
                'name': 'name_mapping',
                'name_arabic': 'name_arabic_mapping',
                'name_english': 'name_english_mapping',
                'email': 'email_mapping',
                'phone': 'phone_mapping',
                'birth_date': 'birth_date_mapping',
                'gender': 'gender_mapping',
                'nationality': 'nationality_mapping',
                'native_language': 'native_language_mapping',
                'english_level': 'english_level_mapping',
                'has_certificate': 'has_certificate_mapping',
                'certificate_type': 'certificate_type_mapping',
                'certificate_date': 'certificate_date_mapping'
            }
            
            update_vals = {}
            for field, mapping_field in mapping_fields.items():
                update_vals[mapping_field] = auto_mapping.get(field, '')
            
            self.write(update_vals)
            
        except (json.JSONDecodeError, TypeError) as e:
            _logger.error('Error setting up mapping fields: %s', str(e))

    def action_save_mapping(self):
        """Save the column mapping and proceed."""
        self.ensure_one()
        
        # Get available columns for validation
        available_columns = []
        if self.available_columns:
            try:
                available_columns = json.loads(self.available_columns)
            except json.JSONDecodeError:
                raise UserError(_('Invalid available columns data.'))
        
        # Build mapping dictionary
        mapping = {}
        mapping_fields = {
            'name': self.name_mapping,
            'name_arabic': self.name_arabic_mapping,
            'name_english': self.name_english_mapping,
            'email': self.email_mapping,
            'phone': self.phone_mapping,
            'birth_date': self.birth_date_mapping,
            'gender': self.gender_mapping,
            'nationality': self.nationality_mapping,
            'native_language': self.native_language_mapping,
            'english_level': self.english_level_mapping,
            'has_certificate': self.has_certificate_mapping,
            'certificate_type': self.certificate_type_mapping,
            'certificate_date': self.certificate_date_mapping
        }
        
        # Only include mapped fields (skip empty mappings)
        for field, column in mapping_fields.items():
            if column:
                # Validate that the column exists in available columns
                if column not in available_columns:
                    field_labels = {
                        'name': 'Student Name (English)',
                        'name_arabic': 'Student Name (Arabic)',
                        'name_english': 'Student Name (English) - Alternative',
                        'email': 'Email Address',
                        'phone': 'Phone Number',
                        'birth_date': 'Birth Date',
                        'gender': 'Gender',
                        'nationality': 'Nationality',
                        'native_language': 'Native Language',
                        'english_level': 'English Level',
                        'has_certificate': 'Has Certificate',
                        'certificate_type': 'Certificate Type',
                        'certificate_date': 'Certificate Date'
                    }
                    raise UserError(_('Column "%s" not found in file for %s. Available columns: %s') % 
                                  (column, field_labels[field], ', '.join(available_columns)))
                mapping[field] = column
        
        # Validate required fields
        required_fields = ['name', 'name_arabic', 'name_english', 'email']
        missing_fields = [field for field in required_fields if field not in mapping]
        
        if missing_fields:
            field_labels = {
                'name': 'Student Name (English)',
                'name_arabic': 'Student Name (Arabic)',
                'name_english': 'Student Name (English) - Alternative',
                'email': 'Email Address'
            }
            missing_labels = [field_labels[field] for field in missing_fields]
            raise UserError(_('Please map the following required fields: %s') % ', '.join(missing_labels))
        
        # Save mapping to intake batch
        mapping_json = json.dumps(mapping)
        self.intake_batch_id.action_save_column_mapping(mapping_json)
        
        return {'type': 'ir.actions.act_window_close'}

    def action_preview_mapping(self):
        """Preview the mapping results."""
        self.ensure_one()
        
        if not self.preview_data:
            raise UserError(_('No preview data available.'))
        
        try:
            preview_records = json.loads(self.preview_data)
            if not preview_records:
                raise UserError(_('No preview records found.'))
            
            # Build mapping dictionary
            mapping = {}
            mapping_fields = {
                'name': self.name_mapping,
                'name_arabic': self.name_arabic_mapping,
                'name_english': self.name_english_mapping,
                'email': self.email_mapping,
                'phone': self.phone_mapping,
                'birth_date': self.birth_date_mapping,
                'gender': self.gender_mapping,
                'nationality': self.nationality_mapping,
                'native_language': self.native_language_mapping,
                'english_level': self.english_level_mapping,
                'has_certificate': self.has_certificate_mapping,
                'certificate_type': self.certificate_type_mapping,
                'certificate_date': self.certificate_date_mapping
            }
            
            # Apply mapping to preview records
            mapped_preview = []
            for record in preview_records[:3]:  # Show first 3 records
                mapped_record = {}
                for field, column in mapping_fields.items():
                    if column and column in record:
                        mapped_record[field] = record[column]
                mapped_preview.append(mapped_record)
            
            # Return preview action
            return {
                'type': 'ir.actions.act_window',
                'name': _('Mapping Preview'),
                'res_model': 'gr.intake.batch.mapping.wizard',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'context': {
                    'default_intake_batch_id': self.intake_batch_id.id,
                    'default_available_columns': self.available_columns,
                    'default_preview_data': self.preview_data,
                    'default_column_mapping': json.dumps(mapping),
                    'show_preview': True,
                    'mapped_preview': json.dumps(mapped_preview)
                }
            }
            
        except Exception as e:
            raise UserError(_('Error generating preview: %s') % str(e))
