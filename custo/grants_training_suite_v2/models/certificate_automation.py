# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class CertificateAutomation(models.Model):
    _name = 'gr.certificate.automation'
    _description = 'Automated Certificate Generation System'
    _order = 'create_date desc'

    name = fields.Char(
        string='Certificate Automation Name',
        required=True
    )

    # Certificate Configuration
    certificate_template_name = fields.Char(
        string='Certificate Template Name',
        default='Program Completion Certificate',
        required=True,
        help='Name of the certificate template to use'
    )
    
    certificate_template_content = fields.Text(
        string='Certificate Template Content',
        default='This certifies that {student_name} has successfully completed the {program_name} training program.',
        help='Template content for the certificate (use {student_name}, {program_name} placeholders)'
    )

    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        required=True
    )

    # Automation Rules
    auto_generate = fields.Boolean(
        string='Auto Generate Certificates',
        default=True,
        help='Automatically generate certificates when conditions are met'
    )

    completion_threshold = fields.Float(
        string='Completion Threshold (%)',
        default=100.0,
        help='Minimum completion percentage required for certificate generation'
    )

    require_all_courses = fields.Boolean(
        string='Require All Courses',
        default=True,
        help='Require completion of all courses in the program'
    )

    require_elearning_completion = fields.Boolean(
        string='Require eLearning Completion',
        default=True,
        help='Require eLearning course completion for certificate'
    )

    require_custom_assessment = fields.Boolean(
        string='Require Custom Assessment',
        default=False,
        help='Require custom assessment completion for certificate'
    )

    # Validation Rules
    min_attendance_percentage = fields.Float(
        string='Minimum Attendance %',
        default=80.0,
        help='Minimum attendance percentage required'
    )

    require_homework_submission = fields.Boolean(
        string='Require Homework Submission',
        default=False,
        help='Require homework submission for certificate'
    )

    # Timing Rules
    generation_delay_hours = fields.Integer(
        string='Generation Delay (Hours)',
        default=0,
        help='Delay certificate generation by specified hours after completion'
    )

    # Status and Tracking
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived')
    ], string='Status', default='draft')

    generated_certificates_count = fields.Integer(
        string='Generated Certificates',
        compute='_compute_certificate_stats',
        store=True
    )

    pending_verifications_count = fields.Integer(
        string='Pending Verifications',
        compute='_compute_certificate_stats',
        store=True
    )

    failed_generations_count = fields.Integer(
        string='Failed Generations',
        compute='_compute_certificate_stats',
        store=True
    )

    last_generation_date = fields.Datetime(
        string='Last Generation Date'
    )

    # Generated Certificates
    generated_certificates = fields.One2many(
        'gr.certificate',
        'automation_id',
        string='Generated Certificates'
    )

    @api.depends('generated_certificates')
    def _compute_certificate_stats(self):
        """Compute certificate generation statistics."""
        for automation in self:
            certificates = automation.generated_certificates
            
            automation.generated_certificates_count = len(certificates)
            automation.pending_verifications_count = len(certificates.filtered(lambda c: c.status == 'pending'))
            automation.failed_generations_count = len(certificates.filtered(lambda c: c.status == 'failed'))

    def action_activate_automation(self):
        """Activate the certificate automation."""
        self.status = 'active'
        _logger.info('Certificate automation activated: %s', self.name)

    def action_pause_automation(self):
        """Pause the certificate automation."""
        self.status = 'paused'
        _logger.info('Certificate automation paused: %s', self.name)

    def action_archive_automation(self):
        """Archive the certificate automation."""
        self.status = 'archived'
        _logger.info('Certificate automation archived: %s', self.name)

    @api.model
    def process_automatic_certificates(self):
        """Process automatic certificate generation for all active automations."""
        _logger.info('Starting automatic certificate generation process...')
        
        active_automations = self.search([('status', '=', 'active'), ('auto_generate', '=', True)])
        
        total_generated = 0
        
        for automation in active_automations:
            try:
                generated_count = automation._generate_certificates_for_program()
                total_generated += generated_count
                automation.last_generation_date = fields.Datetime.now()
                
            except Exception as e:
                _logger.error('Failed to process automation %s: %s', automation.name, str(e))
                continue
        
        _logger.info('Automatic certificate generation completed. Generated %d certificates.', total_generated)
        return total_generated

    def _generate_certificates_for_program(self):
        """Generate certificates for students who meet the program requirements."""
        generated_count = 0
        
        # Get all students in the training program
        program_students = self._get_eligible_students()
        
        for student in program_students:
            try:
                if self._validate_certificate_eligibility(student):
                    certificate = self._create_certificate_for_student(student)
                    if certificate:
                        generated_count += 1
                        
            except Exception as e:
                _logger.error('Failed to generate certificate for student %s: %s', student.name, str(e))
                continue
        
        return generated_count

    def _get_eligible_students(self):
        """Get students eligible for certificate generation."""
        # Get students with progress trackers for this program
        trackers = self.env['gr.progress.tracker'].search([
            ('course_integration_id.training_program_id', '=', self.training_program_id.id)
        ])
        
        # Get unique students from trackers
        student_ids = list(set(tracker.student_id.id for tracker in trackers))
        return self.env['gr.student'].browse(student_ids)

    def _validate_certificate_eligibility(self, student):
        """Validate if student is eligible for certificate generation."""
        # Check if certificate already exists
        existing_certificate = self.env['gr.certificate'].search([
            ('student_id', '=', student.id),
            ('automation_id', '=', self.id)
        ])
        
        if existing_certificate:
            return False
        
        # Check completion threshold
        if student.elearning_progress < self.completion_threshold:
            return False
        
        # Check if all courses are required and completed
        if self.require_all_courses:
            program_courses = self.env['gr.course.integration'].search([
                ('training_program_id', '=', self.training_program_id.id)
            ])
            
            student_trackers = self.env['gr.progress.tracker'].search([
                ('student_id', '=', student.id),
                ('course_integration_id', 'in', program_courses.ids)
            ])
            
            if len(student_trackers) < len(program_courses):
                return False
            
            # Check if all courses are completed
            for tracker in student_trackers:
                if tracker.status != 'completed':
                    return False
        
        # Check eLearning completion requirement
        if self.require_elearning_completion:
            if student.integration_status not in ['completed', 'certified']:
                return False
        
        # Check custom assessment requirement
        if self.require_custom_assessment:
            # This would depend on your custom assessment implementation
            # For now, we'll assume it's satisfied if student has completed courses
            pass
        
        # Check attendance requirement
        if self.min_attendance_percentage > 0:
            # This would depend on your attendance tracking implementation
            # For now, we'll assume it's satisfied if student has good progress
            if student.elearning_progress < self.min_attendance_percentage:
                return False
        
        # Check homework submission requirement
        if self.require_homework_submission:
            # Check if student has submitted required homework
            homework_attempts = self.env['gr.homework.attempt'].search([
                ('student_id', '=', student.id),
                ('status', '=', 'submitted')
            ])
            
            if not homework_attempts:
                return False
        
        return True

    def _create_certificate_for_student(self, student):
        """Create certificate for eligible student."""
        try:
            # Check generation delay
            if self.generation_delay_hours > 0:
                delay_time = datetime.now() - timedelta(hours=self.generation_delay_hours)
                if student.completion_date and student.completion_date > delay_time:
                    # Still within delay period, skip generation
                    return None
            
            # Create the certificate
            certificate = self.env['gr.certificate'].create({
                'name': f'Certificate - {student.name} - {self.training_program_id.name}',
                'student_id': student.id,
                'training_program_id': self.training_program_id.id,
                'automation_id': self.id,
                'completion_date': fields.Date.today(),
                'state': 'pending',
                'certificate_type': 'program_completion',
                'certificate_title': self.certificate_template_name,
                'issued_by_id': self.env.user.id,
                'notes': f'Automatically generated by {self.name}'
            })
            
            # Generate certificate content
            certificate._generate_certificate_content()
            
            # Update student status
            if student.integration_status != 'certified':
                student.integration_status = 'certified'
            
            # Create notification
            self._create_certificate_notification(student, certificate)
            
            _logger.info('Certificate generated for student: %s', student.name)
            return certificate
            
        except Exception as e:
            _logger.error('Failed to create certificate for student %s: %s', student.name, str(e))
            return None

    def _create_certificate_notification(self, student, certificate):
        """Create notification for certificate generation."""
        try:
            self.env['gr.progress.notification'].create({
                'name': f'Certificate Generated - {student.name}',
                'student_id': student.id,
                'notification_type': 'achievement',
                'milestone_type': 'custom',
                'message': f'Congratulations! A certificate has been generated for {student.name} for completing {self.training_program_id.name}.',
                'recipient_user_id': student.assigned_agent_id.user_id.id if student.assigned_agent_id else None,
                'recipient_email': student.email,
                'priority': 'normal',
                'auto_generated': True,
                'trigger_condition': 'Certificate automation triggered',
                'status': 'draft'
            }).action_send_notification()
            
        except Exception as e:
            _logger.error('Failed to create certificate notification: %s', str(e))

    def action_test_automation(self):
        """Test the automation rules without generating certificates."""
        self.ensure_one()
        
        eligible_students = self._get_eligible_students()
        eligible_count = 0
        
        for student in eligible_students:
            if self._validate_certificate_eligibility(student):
                eligible_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test Results',
                'message': f'Found {eligible_count} eligible students out of {len(eligible_students)} total students.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_manual_certificates(self):
        """Manually trigger certificate generation for eligible students."""
        self.ensure_one()
        
        generated_count = self._generate_certificates_for_program()
        self.last_generation_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Manual Generation Complete',
                'message': f'Generated {generated_count} certificates.',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def cleanup_failed_certificates(self):
        """Clean up failed certificate generations."""
        _logger.info('Cleaning up failed certificate generations...')
        
        failed_certificates = self.env['gr.certificate'].search([
            ('status', '=', 'failed'),
            ('create_date', '<', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'))
        ])
        
        cleaned_count = 0
        for certificate in failed_certificates:
            try:
                certificate.unlink()
                cleaned_count += 1
            except Exception as e:
                _logger.error('Failed to clean up certificate %s: %s', certificate.name, str(e))
        
        _logger.info('Cleaned up %d failed certificates', cleaned_count)
        return cleaned_count
