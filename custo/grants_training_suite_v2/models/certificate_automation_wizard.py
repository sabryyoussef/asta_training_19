# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class CertificateAutomationWizard(models.Model):
    _name = 'gr.certificate.automation.wizard'
    _description = 'Certificate Automation Wizard'
    _rec_name = 'operation_type'

    # Operation Configuration
    operation_type = fields.Selection([
        ('auto_generate', 'Auto-Generate Certificates'),
        ('bulk_generate_pdf', 'Bulk Generate PDFs'),
        ('bulk_send_email', 'Bulk Send Emails'),
        ('bulk_download', 'Bulk Download'),
    ], string='Operation Type', required=True, default='auto_generate', help='Type of automation operation')
    
    # Selection Criteria
    certificate_type = fields.Selection([
        ('all', 'All Types'),
        ('completion', 'Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('excellence', 'Excellence'),
        ('program_completion', 'Program Completion'),
    ], string='Certificate Type Filter', default='all', help='Filter certificates by type')
    
    date_from = fields.Date(
        string='From Date',
        help='Filter certificates from this date'
    )
    
    date_to = fields.Date(
        string='To Date',
        help='Filter certificates to this date'
    )
    
    state_filter = fields.Selection([
        ('all', 'All States'),
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('delivered', 'Delivered'),
        ('verified', 'Verified'),
    ], string='State Filter', default='all', help='Filter certificates by state')
    
    # Email Configuration
    email_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        help='Email template to use for sending certificates'
    )
    
    email_subject = fields.Char(
        string='Email Subject',
        default='Your Certificate',
        help='Subject line for certificate emails'
    )
    
    email_body = fields.Html(
        string='Email Body',
        default='<p>Dear Student,</p><p>Please find your certificate attached.</p><p>Best regards,<br/>Training Team</p>',
        help='Email body content'
    )
    
    # Processing Options
    generate_pdf = fields.Boolean(
        string='Generate PDF',
        default=True,
        help='Generate PDF for certificates that don\'t have one'
    )
    
    send_email = fields.Boolean(
        string='Send Email',
        default=False,
        help='Send email to students after processing'
    )
    
    update_state = fields.Selection([
        ('no_change', 'No Change'),
        ('issued', 'Mark as Issued'),
        ('delivered', 'Mark as Delivered'),
    ], string='Update State', default='no_change', help='Update certificate state after processing')
    
    # Results
    processed_count = fields.Integer(
        string='Processed Count',
        readonly=True,
        help='Number of certificates processed'
    )
    
    success_count = fields.Integer(
        string='Success Count',
        readonly=True,
        help='Number of successful operations'
    )
    
    error_count = fields.Integer(
        string='Error Count',
        readonly=True,
        help='Number of errors encountered'
    )
    
    error_details = fields.Text(
        string='Error Details',
        readonly=True,
        help='Details of errors encountered'
    )
    
    operation_date = fields.Datetime(
        string='Operation Date',
        readonly=True,
        help='Date when the operation was performed'
    )
    
    # Computed Fields
    available_certificates_count = fields.Integer(
        string='Available Certificates',
        compute='_compute_available_certificates_count',
        help='Number of certificates matching the criteria'
    )
    
    @api.depends('certificate_type', 'date_from', 'date_to', 'state_filter')
    def _compute_available_certificates_count(self):
        """Compute the number of certificates matching the criteria."""
        for wizard in self:
            domain = self._get_certificate_domain()
            wizard.available_certificates_count = self.env['gr.certificate'].search_count(domain)
    
    def _get_certificate_domain(self):
        """Get domain for filtering certificates."""
        self.ensure_one()
        
        domain = []
        
        # Filter by certificate type
        if self.certificate_type != 'all':
            domain.append(('certificate_type', '=', self.certificate_type))
        
        # Filter by date range
        if self.date_from:
            domain.append(('issue_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('issue_date', '<=', self.date_to))
        
        # Filter by state
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        return domain
    
    def action_preview_certificates(self):
        """Preview certificates that will be processed."""
        self.ensure_one()
        
        domain = self._get_certificate_domain()
        certificates = self.env['gr.certificate'].search(domain, limit=10)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificates to Process (Preview)'),
            'res_model': 'gr.certificate',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_limit': 10},
        }
    
    def action_execute_automation(self):
        """Execute the automation operation."""
        self.ensure_one()
        
        if self.operation_type == 'auto_generate':
            return self._execute_auto_generate()
        elif self.operation_type == 'bulk_generate_pdf':
            return self._execute_bulk_generate_pdf()
        elif self.operation_type == 'bulk_send_email':
            return self._execute_bulk_send_email()
        elif self.operation_type == 'bulk_download':
            return self._execute_bulk_download()
        else:
            raise UserError(_('Unknown operation type: %s') % self.operation_type)
    
    def _execute_auto_generate(self):
        """Execute automatic certificate generation."""
        self.ensure_one()
        
        try:
            result = self.env['gr.certificate'].auto_generate_certificates_for_completed_students()
            
            self.processed_count = result['certificates_created']
            self.success_count = result['certificates_created']
            self.error_count = len(result['errors'])
            self.error_details = '\n'.join(result['errors']) if result['errors'] else ''
            self.operation_date = fields.Datetime.now()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Auto-Generation Complete'),
                    'message': _('Generated %d certificates. %d errors encountered.') % (self.success_count, self.error_count),
                    'type': 'success' if self.error_count == 0 else 'warning',
                }
            }
            
        except Exception as e:
            _logger.error('Error in auto-generation: %s', str(e))
            raise UserError(_('Error in auto-generation: %s') % str(e))
    
    def _execute_bulk_generate_pdf(self):
        """Execute bulk PDF generation."""
        self.ensure_one()
        
        domain = self._get_certificate_domain()
        certificates = self.env['gr.certificate'].search(domain)
        
        processed = 0
        success = 0
        errors = []
        
        for certificate in certificates:
            try:
                processed += 1
                
                if not certificate.certificate_file and certificate.template_id:
                    certificate.action_generate_certificate_pdf()
                    success += 1
                elif certificate.certificate_file:
                    success += 1  # Already has PDF
                else:
                    errors.append(f"Certificate {certificate.name}: No template selected")
                    
            except Exception as e:
                error_msg = f"Certificate {certificate.name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
        
        self.processed_count = processed
        self.success_count = success
        self.error_count = len(errors)
        self.error_details = '\n'.join(errors) if errors else ''
        self.operation_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk PDF Generation Complete'),
                'message': _('Processed %d certificates. %d successful, %d errors.') % (processed, success, len(errors)),
                'type': 'success' if len(errors) == 0 else 'warning',
            }
        }
    
    def _execute_bulk_send_email(self):
        """Execute bulk email sending."""
        self.ensure_one()
        
        domain = self._get_certificate_domain()
        certificates = self.env['gr.certificate'].search(domain)
        
        processed = 0
        success = 0
        errors = []
        
        for certificate in certificates:
            try:
                processed += 1
                
                if certificate.certificate_file and certificate.student_id.email:
                    certificate.action_send_certificate_email()
                    success += 1
                    
                    # Update state if requested
                    if self.update_state == 'delivered':
                        certificate.state = 'delivered'
                    elif self.update_state == 'issued':
                        certificate.state = 'issued'
                        
                elif not certificate.certificate_file:
                    errors.append(f"Certificate {certificate.name}: No PDF file")
                elif not certificate.student_id.email:
                    errors.append(f"Certificate {certificate.name}: Student has no email")
                    
            except Exception as e:
                error_msg = f"Certificate {certificate.name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
        
        self.processed_count = processed
        self.success_count = success
        self.error_count = len(errors)
        self.error_details = '\n'.join(errors) if errors else ''
        self.operation_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Email Sending Complete'),
                'message': _('Processed %d certificates. %d successful, %d errors.') % (processed, success, len(errors)),
                'type': 'success' if len(errors) == 0 else 'warning',
            }
        }
    
    def _execute_bulk_download(self):
        """Execute bulk download (redirect to certificate list)."""
        self.ensure_one()
        
        domain = self._get_certificate_domain()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificates for Download'),
            'res_model': 'gr.certificate',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_has_pdf': 1},
        }
    
    def action_generate_eligibility_report(self):
        """Generate certificate eligibility report for dashboard."""
        try:
            report_data = self.env['gr.certificate'].get_certificate_eligibility_report()
            
            # Create a formatted report message
            report_message = f"""
Certificate Eligibility Report:
===============================

Total Completed Students: {report_data['total_completed_students']}
Eligible for Certificates: {report_data['eligible_for_certificates']}
Not Eligible for Certificates: {report_data['not_eligible_for_certificates']}
Already Have Certificates: {report_data['already_have_certificates']}

Success Criteria Failures:
- Overall Progress Failures: {report_data['success_criteria_summary']['overall_progress_failures']}
- eLearning Progress Failures: {report_data['success_criteria_summary']['elearning_progress_failures']}
- Sessions Failures: {report_data['success_criteria_summary']['sessions_failures']}
- Homework Failures: {report_data['success_criteria_summary']['homework_failures']}
- Warnings Failures: {report_data['success_criteria_summary']['warnings_failures']}

Detailed breakdown available in logs.
            """
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Certificate Eligibility Report',
                    'message': report_message,
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error('Error generating eligibility report: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error generating eligibility report: {str(e)}',
                    'type': 'danger',
                }
            }
    
    def action_reset_wizard(self):
        """Reset wizard to initial state."""
        self.ensure_one()
        
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.error_details = ''
        self.operation_date = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Wizard Reset'),
                'message': _('Wizard has been reset to initial state.'),
                'type': 'info',
            }
        }
