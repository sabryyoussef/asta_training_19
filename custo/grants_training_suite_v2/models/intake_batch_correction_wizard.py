# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class IntakeBatchCorrectionWizard(models.TransientModel):
    _name = 'gr.intake.batch.correction.wizard'
    _description = 'Intake Batch Correction Wizard'
    
    # Basic Fields
    intake_batch_id = fields.Many2one(
        'gr.intake.batch',
        string='Intake Batch',
        required=True,
        readonly=True
    )
    
    batch_name = fields.Char(
        string='Batch Name',
        related='intake_batch_id.name',
        readonly=True
    )
    
    # Failed Records Data
    failed_records_data = fields.Text(
        string='Failed Records Data',
        related='intake_batch_id.failed_records_data',
        readonly=True
    )
    
    failed_records_count = fields.Integer(
        string='Failed Records Count',
        related='intake_batch_id.failed_records_count',
        readonly=True
    )
    
    # Correction Data
    corrected_records = fields.Text(
        string='Corrected Records',
        help='JSON string containing corrected records data'
    )
    
    # Status Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('correcting', 'Correcting'),
        ('corrected', 'Corrected'),
        ('processed', 'Processed'),
    ], string='Status', default='draft')
    
    # Computed Fields
    failed_records_list = fields.Text(
        string='Failed Records List',
        compute='_compute_failed_records_list',
        store=True
    )
    
    corrected_records_count = fields.Integer(
        string='Corrected Records Count',
        compute='_compute_corrected_records_count',
        store=True
    )
    
    @api.depends('failed_records_data')
    def _compute_failed_records_list(self):
        """Compute formatted list of failed records for display."""
        for wizard in self:
            if wizard.failed_records_data:
                try:
                    failed_data = json.loads(wizard.failed_records_data)
                    failed_records = failed_data.get('failed_records', [])
                    
                    formatted_list = []
                    for record in failed_records:
                        row_num = record.get('row_number', 0)
                        errors = record.get('errors', [])
                        warnings = record.get('warnings', [])
                        
                        formatted_list.append(f"Row {row_num}:")
                        for error in errors:
                            formatted_list.append(f"  ❌ {error}")
                        for warning in warnings:
                            formatted_list.append(f"  ⚠️ {warning}")
                        formatted_list.append("")
                    
                    wizard.failed_records_list = '\n'.join(formatted_list)
                except (json.JSONDecodeError, TypeError):
                    wizard.failed_records_list = "Error parsing failed records data."
            else:
                wizard.failed_records_list = "No failed records found."
    
    @api.depends('corrected_records')
    def _compute_corrected_records_count(self):
        """Compute the number of corrected records."""
        for wizard in self:
            if wizard.corrected_records:
                try:
                    corrected_data = json.loads(wizard.corrected_records)
                    corrected_records = corrected_data.get('corrected_records', [])
                    wizard.corrected_records_count = len(corrected_records)
                except (json.JSONDecodeError, TypeError):
                    wizard.corrected_records_count = 0
            else:
                wizard.corrected_records_count = 0
    
    @api.model
    def create(self, vals):
        """Override create to load failed records data."""
        wizard = super(IntakeBatchCorrectionWizard, self).create(vals)
        wizard._load_failed_records()
        return wizard
    
    def _load_failed_records(self):
        """Load failed records data from the intake batch."""
        self.ensure_one()
        
        if not self.intake_batch_id or not self.intake_batch_id.failed_records_data:
            return
        
        # Initialize corrected records with failed records data
        try:
            failed_data = json.loads(self.intake_batch_id.failed_records_data)
            failed_records = failed_data.get('failed_records', [])
            
            # Create initial corrected records structure
            corrected_data = {
                'corrected_records': [],
                'original_failed_count': len(failed_records),
                'correction_timestamp': fields.Datetime.now().isoformat(),
                'batch_id': self.intake_batch_id.id,
                'batch_name': self.intake_batch_id.name
            }
            
            # Initialize corrected records with original data
            for record in failed_records:
                corrected_record = {
                    'row_number': record.get('row_number'),
                    'data': record.get('data', {}).copy(),
                    'original_errors': record.get('errors', []),
                    'original_warnings': record.get('warnings', []),
                    'corrections_made': [],
                    'status': 'needs_correction'
                }
                corrected_data['corrected_records'].append(corrected_record)
            
            self.corrected_records = json.dumps(corrected_data, indent=2)
            self.state = 'correcting'
            
        except (json.JSONDecodeError, TypeError) as e:
            raise UserError(_('Error loading failed records data: %s') % str(e))
    
    def action_correct_record(self, row_number, corrected_data):
        """Correct a specific record."""
        self.ensure_one()
        
        if not self.corrected_records:
            raise UserError(_('No corrected records data found.'))
        
        try:
            corrected_json = json.loads(self.corrected_records)
            corrected_records = corrected_json.get('corrected_records', [])
            
            # Find the record to correct
            for record in corrected_records:
                if record.get('row_number') == row_number:
                    # Update the record data
                    record['data'].update(corrected_data)
                    record['corrections_made'].append({
                        'field': list(corrected_data.keys())[0],
                        'old_value': record['data'].get(list(corrected_data.keys())[0]),
                        'new_value': list(corrected_data.values())[0],
                        'timestamp': fields.Datetime.now().isoformat()
                    })
                    record['status'] = 'corrected'
                    break
            
            # Save updated data
            self.corrected_records = json.dumps(corrected_json, indent=2)
            
            return True
            
        except (json.JSONDecodeError, TypeError) as e:
            raise UserError(_('Error correcting record: %s') % str(e))
    
    def action_validate_corrected_records(self):
        """Validate the corrected records."""
        self.ensure_one()
        
        if not self.corrected_records:
            raise UserError(_('No corrected records found.'))
        
        try:
            corrected_json = json.loads(self.corrected_records)
            corrected_records = corrected_json.get('corrected_records', [])
            
            validation_errors = []
            
            for record in corrected_records:
                if record.get('status') == 'corrected':
                    # Validate the corrected record
                    record_errors = self._validate_single_record(record['data'])
                    if record_errors:
                        validation_errors.extend([f"Row {record.get('row_number')}: {error}" for error in record_errors])
            
            if validation_errors:
                raise UserError(_('Validation failed for corrected records:\n%s') % '\n'.join(validation_errors))
            
            self.state = 'corrected'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Records Validated'),
                    'message': _('All corrected records passed validation. Ready for processing.'),
                    'type': 'success',
                }
            }
            
        except (json.JSONDecodeError, TypeError) as e:
            raise UserError(_('Error validating corrected records: %s') % str(e))
    
    def _validate_single_record(self, record_data):
        """Validate a single record."""
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'name_arabic', 'name_english', 'email']
        for field in required_fields:
            if not record_data.get(field) or str(record_data.get(field)).strip() == '':
                errors.append(f'Missing required field "{field}"')
        
        # Email validation
        email = record_data.get('email', '').strip()
        if email and ('@' not in email or '.' not in email.split('@')[-1]):
            errors.append(f'Invalid email format "{email}"')
        
        # Date validation
        birth_date = record_data.get('birth_date', '').strip()
        if birth_date:
            try:
                from datetime import datetime
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                errors.append(f'Invalid date format for birth_date "{birth_date}". Use YYYY-MM-DD format.')
        
        return errors
    
    def action_process_corrected_records(self):
        """Process the corrected records."""
        self.ensure_one()
        
        if self.state != 'corrected':
            raise UserError(_('Please validate the corrected records first.'))
        
        # Call the intake batch's reprocessing method
        return self.intake_batch_id.action_reprocess_failed_records()
    
    def action_skip_record(self, row_number):
        """Skip a record (mark as skipped)."""
        self.ensure_one()
        
        if not self.corrected_records:
            raise UserError(_('No corrected records data found.'))
        
        try:
            corrected_json = json.loads(self.corrected_records)
            corrected_records = corrected_json.get('corrected_records', [])
            
            # Find the record to skip
            for record in corrected_records:
                if record.get('row_number') == row_number:
                    record['status'] = 'skipped'
                    record['corrections_made'].append({
                        'action': 'skipped',
                        'timestamp': fields.Datetime.now().isoformat()
                    })
                    break
            
            # Save updated data
            self.corrected_records = json.dumps(corrected_json, indent=2)
            
            return True
            
        except (json.JSONDecodeError, TypeError) as e:
            raise UserError(_('Error skipping record: %s') % str(e))
