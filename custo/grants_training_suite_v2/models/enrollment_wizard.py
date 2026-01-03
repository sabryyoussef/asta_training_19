# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class EnrollmentWizard(models.Model):
    _name = 'gr.enrollment.wizard'
    _description = 'Student Enrollment Wizard for Training Programs'
    _inherit = ['mail.thread']

    # Wizard Configuration
    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        help='Training program to enroll students in'
    )
    
    course_integration_id = fields.Many2one(
        'gr.course.integration',
        string='Course Integration',
        help='Individual course integration to enroll students in'
    )
    
    enrollment_type = fields.Selection([
        ('direct_enroll', 'Direct Enroll'),
        ('invite_only', 'Send Invitation Only'),
        ('invite_and_enroll', 'Send Invitation & Auto-Enroll'),
    ], string='Enrollment Type', default='direct_enroll', required=True,
       help='Type of enrollment to perform')
    
    # Student Selection
    student_selection_type = fields.Selection([
        ('all_eligible', 'All Eligible Students'),
        ('selected_students', 'Selected Students'),
        ('filtered_students', 'Filtered Students'),
    ], string='Student Selection', default='all_eligible', required=True,
       help='How to select students for enrollment')
    
    selected_student_ids = fields.Many2many(
        'gr.student',
        string='Selected Students',
        help='Students selected for enrollment'
    )
    
    # Filtering Options
    filter_by_english_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('any', 'Any Level'),
    ], string='Filter by English Level', default='any',
       help='Filter students by English proficiency level')
    
    filter_by_state = fields.Selection([
        ('eligible', 'Eligible Only'),
        ('assigned_to_agent', 'Assigned to Agent Only'),
        ('both', 'Both Eligible & Assigned'),
    ], string='Filter by State', default='both',
       help='Filter students by their current state')
    
    filter_by_course_preference = fields.Boolean(
        string='Match Course Preferences',
        default=True,
        help='Only include students who have matching course preferences'
    )
    
    # Enrollment Settings
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
        help='Send notification to students about enrollment'
    )
    
    notification_message = fields.Text(
        string='Custom Notification Message',
        help='Custom message to include in the notification'
    )
    
    auto_assign_agent = fields.Boolean(
        string='Auto-Assign Agent',
        default=True,
        help='Automatically assign an agent if student doesn\'t have one'
    )
    
    # Results Tracking
    enrollment_summary = fields.Text(
        string='Enrollment Summary',
        readonly=True,
        help='Summary of enrollment results'
    )
    
    enrolled_count = fields.Integer(
        string='Students Enrolled',
        readonly=True,
        default=0
    )
    
    invited_count = fields.Integer(
        string='Students Invited',
        readonly=True,
        default=0
    )
    
    error_count = fields.Integer(
        string='Errors',
        readonly=True,
        default=0
    )
    
    enrollment_date = fields.Datetime(
        string='Enrollment Date',
        readonly=True,
        default=fields.Datetime.now
    )
    
    # Computed Fields
    available_students = fields.Many2many(
        'gr.student',
        string='Available Students',
        compute='_compute_available_students',
        help='Students available for enrollment based on filters'
    )
    
    available_students_count = fields.Integer(
        string='Available Students Count',
        compute='_compute_available_students_count',
        help='Number of students available for enrollment'
    )
    
    @api.depends('training_program_id', 'course_integration_id', 'filter_by_english_level', 'filter_by_state', 
                 'filter_by_course_preference')
    def _compute_available_students(self):
        """Compute available students based on filters."""
        for wizard in self:
            if not wizard.training_program_id and not wizard.course_integration_id:
                wizard.available_students = False
                continue
            
            # Base domain
            domain = []
            
            # Filter by state
            if wizard.filter_by_state == 'eligible':
                domain.append(('state', '=', 'eligible'))
            elif wizard.filter_by_state == 'assigned_to_agent':
                domain.append(('state', '=', 'assigned_to_agent'))
            else:  # both
                domain.append(('state', 'in', ['eligible', 'assigned_to_agent']))
            
            # Filter by English level
            if wizard.filter_by_english_level != 'any':
                domain.append(('english_level', '=', wizard.filter_by_english_level))
            
            # Filter by course preference if enabled
            if wizard.filter_by_course_preference:
                if wizard.training_program_id and wizard.training_program_id.course_integrations:
                    course_ids = wizard.training_program_id.course_integrations.ids
                    domain.append(('preferred_course_integration_id', 'in', course_ids))
                elif wizard.course_integration_id:
                    domain.append(('preferred_course_integration_id', '=', wizard.course_integration_id.id))
            
            # Get students
            students = self.env['gr.student'].search(domain)
            wizard.available_students = students
    
    @api.depends('available_students')
    def _compute_available_students_count(self):
        """Compute count of available students."""
        for wizard in self:
            wizard.available_students_count = len(wizard.available_students)
    
    @api.onchange('student_selection_type')
    def _onchange_student_selection_type(self):
        """Update selected students when selection type changes."""
        if self.student_selection_type == 'all_eligible':
            self.selected_student_ids = self.available_students
        elif self.student_selection_type == 'filtered_students':
            self.selected_student_ids = self.available_students
        else:
            self.selected_student_ids = False
    
    @api.onchange('available_students')
    def _onchange_available_students(self):
        """Update selected students when available students change."""
        if self.student_selection_type in ['all_eligible', 'filtered_students']:
            self.selected_student_ids = self.available_students
    
    def action_preview_enrollment(self):
        """Preview enrollment without actually enrolling students."""
        self.ensure_one()
        
        if not self.training_program_id and not self.course_integration_id:
            raise UserError(_('Please select a training program or course integration.'))
        
        students_to_enroll = self._get_students_to_enroll()
        
        if not students_to_enroll:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Students Found'),
                    'message': _('No students match the selected criteria.'),
                    'type': 'warning',
                }
            }
        
        # Create preview message
        target_name = self.training_program_id.name if self.training_program_id else self.course_integration_id.name
        preview_message = _('Enrollment Preview for %s:\n\n') % target_name
        preview_message += _('Students to %s: %d\n') % (
            'enroll' if self.enrollment_type == 'direct_enroll' else 'invite', 
            len(students_to_enroll)
        )
        preview_message += _('Enrollment Type: %s\n') % dict(self._fields['enrollment_type'].selection)[self.enrollment_type]
        preview_message += _('Send Notification: %s\n\n') % ('Yes' if self.send_notification else 'No')
        
        preview_message += _('Students:\n')
        for student in students_to_enroll:
            preview_message += f'- {student.name} ({student.email})\n'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Enrollment Preview'),
                'message': preview_message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_proceed_with_enrollment(self):
        """Proceed with the enrollment process."""
        self.ensure_one()
        
        if not self.training_program_id and not self.course_integration_id:
            raise UserError(_('Please select a training program or course integration.'))
        
        students_to_enroll = self._get_students_to_enroll()
        
        if not students_to_enroll:
            raise UserError(_('No students match the selected criteria.'))
        
        try:
            enrolled_count = 0
            invited_count = 0
            errors = []
            enrollment_start = fields.Datetime.now()
            
            for student in students_to_enroll:
                try:
                    if self.enrollment_type in ['direct_enroll', 'invite_and_enroll']:
                        # Direct enrollment
                        self._enroll_student_in_program(student)
                        enrolled_count += 1
                    
                    if self.enrollment_type in ['invite_only', 'invite_and_enroll']:
                        # Send invitation
                        self._send_enrollment_invitation(student)
                        invited_count += 1
                    
                    # Log the action
                    self._log_enrollment_action(student)
                    
                except Exception as e:
                    error_msg = f'Error processing student {student.name}: {str(e)}'
                    errors.append(error_msg)
                    _logger.error(error_msg)
            
            # Update wizard with results
            self.write({
                'enrolled_count': enrolled_count,
                'invited_count': invited_count,
                'error_count': len(errors),
                'enrollment_date': enrollment_start,
                'enrollment_summary': self._generate_enrollment_summary(students_to_enroll, enrolled_count, invited_count, errors)
            })
            
            # Show success message
            success_message = _('Enrollment completed successfully!\n')
            success_message += _('Enrolled: %d students\n') % enrolled_count
            if self.enrollment_type in ['invite_only', 'invite_and_enroll']:
                success_message += _('Invited: %d students\n') % invited_count
            if errors:
                success_message += _('Errors: %d\n') % len(errors)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Enrollment Complete'),
                    'message': success_message,
                    'type': 'warning' if errors else 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error('Error during enrollment: %s', str(e))
            raise UserError(_('Error during enrollment: %s') % str(e))
    
    def _get_students_to_enroll(self):
        """Get students to enroll based on wizard settings."""
        if self.student_selection_type == 'selected_students':
            return self.selected_student_ids
        else:
            return self.available_students
    
    def _enroll_student_in_program(self, student):
        """Enroll a student in the training program or individual course."""
        if self.training_program_id:
            # Enroll in training program (all courses)
            existing_enrollments = self.env['gr.progress.tracker'].search([
                ('student_id', '=', student.id),
                ('course_integration_id', 'in', self.training_program_id.course_integrations.ids)
            ])
            
            if existing_enrollments:
                _logger.info('Student %s already enrolled in some courses of program %s', 
                            student.name, self.training_program_id.name)
                return
            
            # Enroll in all active courses
            enrolled_courses = []
            for course in self.training_program_id.course_integrations:
                if course.status == 'active':
                    # Create progress tracker
                    self.env['gr.progress.tracker'].create({
                        'student_id': student.id,
                        'course_integration_id': course.id,
                        'status': 'not_started'
                    })
                    enrolled_courses.append(course.name)
            
            _logger.info('Enrolled student %s in program %s (courses: %s)', 
                        student.name, self.training_program_id.name, ', '.join(enrolled_courses))
        
        elif self.course_integration_id:
            # Enroll in individual course
            existing_tracker = self.env['gr.progress.tracker'].search([
                ('student_id', '=', student.id),
                ('course_integration_id', '=', self.course_integration_id.id)
            ])
            
            if existing_tracker:
                _logger.info('Student %s already enrolled in course %s', 
                            student.name, self.course_integration_id.name)
                return
            
            # Create progress tracker
            self.env['gr.progress.tracker'].create({
                'student_id': student.id,
                'course_integration_id': self.course_integration_id.id,
                'status': 'not_started'
            })
            
            _logger.info('Enrolled student %s in course %s', 
                        student.name, self.course_integration_id.name)
    
    def _send_enrollment_invitation(self, student):
        """Send enrollment invitation to student."""
        # Create notification
        target_name = self.training_program_id.name if self.training_program_id else self.course_integration_id.name
        target_type = 'Training Program' if self.training_program_id else 'Course'
        
        subject = _('%s Invitation: %s') % (target_type, target_name)
        message = _('Dear %s,\n\n') % student.name
        message += _('You have been invited to join the %s: %s\n\n') % (target_type.lower(), target_name)
        
        if self.notification_message:
            message += self.notification_message + '\n\n'
        else:
            message += _('This program will help you improve your English skills and achieve your learning goals.\n\n')
        
        message += _('%s Details:\n') % target_type
        if self.training_program_id:
            message += _('- Program: %s\n') % self.training_program_id.name
            message += _('- Description: %s\n') % (self.training_program_id.description or 'Not specified')
            message += _('- Duration: %s weeks\n') % (self.training_program_id.duration_weeks or 'Not specified')
            
            if self.training_program_id.course_integrations:
                message += _('- Courses included:\n')
                for course in self.training_program_id.course_integrations:
                    message += f'  * {course.name}\n'
        else:
            message += _('- Course: %s\n') % self.course_integration_id.name
            message += _('- eLearning Course: %s\n') % (self.course_integration_id.elearning_course_id.name if self.course_integration_id.elearning_course_id else 'Not specified')
        
        message += _('\nWe look forward to your participation!\n\nBest regards,\nTraining Team')
        
        # Send notification (in-app notification)
        self.env['mail.message'].create({
            'model': 'gr.student',
            'res_id': student.id,
            'subject': subject,
            'body': message,
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
        })
        
        target_name = self.training_program_id.name if self.training_program_id else self.course_integration_id.name
        _logger.info('Sent enrollment invitation to student %s for %s', 
                    student.name, target_name)
    
    def _log_enrollment_action(self, student):
        """Log the enrollment action for tracking."""
        action_type = 'enrollment'
        if self.enrollment_type == 'invite_only':
            action_type = 'invitation'
        elif self.enrollment_type == 'invite_and_enroll':
            action_type = 'enrollment_and_invitation'
        
        # Create activity log entry
        target_name = self.training_program_id.name if self.training_program_id else self.course_integration_id.name
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': _('Student %s - %s') % (action_type.title(), student.name),
            'note': _('Student %s %s in %s via wizard') % (
                student.name, action_type, target_name),
            'model': 'gr.student',
            'res_id': student.id,
            'user_id': self.env.user.id,
        })
    
    def _generate_enrollment_summary(self, students, enrolled_count, invited_count, errors):
        """Generate enrollment summary."""
        target_name = self.training_program_id.name if self.training_program_id else self.course_integration_id.name
        target_type = 'Program' if self.training_program_id else 'Course'
        summary_lines = [
            f"Enrollment Summary for {target_type}: {target_name}",
            f"Date: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Enrollment Type: {dict(self._fields['enrollment_type'].selection)[self.enrollment_type]}",
            f"Students Processed: {len(students)}",
            f"Students Enrolled: {enrolled_count}",
            f"Students Invited: {invited_count}",
            f"Errors: {len(errors)}",
            ""
        ]
        
        if students:
            summary_lines.append("Processed Students:")
            for student in students:
                summary_lines.append(f"  - {student.name} ({student.email})")
            summary_lines.append("")
        
        if errors:
            summary_lines.append("Errors:")
            for error in errors:
                summary_lines.append(f"  - {error}")
        
        return '\n'.join(summary_lines)
    
    def action_reset_wizard(self):
        """Reset wizard to initial state."""
        self.write({
            'selected_student_ids': False,
            'enrollment_summary': False,
            'enrolled_count': 0,
            'invited_count': 0,
            'error_count': 0,
            'enrollment_date': False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Wizard Reset'),
                'message': _('Enrollment wizard has been reset.'),
                'type': 'info',
            }
        }
