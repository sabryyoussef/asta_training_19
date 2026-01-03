# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CourseIntegration(models.Model):
    _name = 'gr.course.integration'
    _description = 'Course Integration between eLearning and Training Suite'
    _order = 'name'

    name = fields.Char(
        string='Integration Name',
        required=True,
        help='Name of the course integration'
    )
    
    # eLearning Course
    elearning_course_id = fields.Many2one(
        'slide.channel',
        string='eLearning Course',
        required=True,
        help='The eLearning course to integrate with'
    )
    
    # Training Program
    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        help='The training program this course belongs to'
    )
    
    # Integration Settings
    auto_enroll_eligible = fields.Boolean(
        string='Auto-enroll Eligible Students',
        default=True,
        help='Automatically enroll eligible students in this course'
    )
    
    completion_threshold = fields.Float(
        string='Completion Threshold (%)',
        default=100.0,
        help='Percentage required to consider course completed'
    )
    
    # Enhanced success criteria for certificate generation
    min_sessions_required = fields.Integer(
        string='Minimum Sessions Required',
        default=0,
        help='Minimum number of custom training sessions required for certificate'
    )
    
    min_homework_required = fields.Integer(
        string='Minimum Homework Required',
        default=0,
        help='Minimum number of homework submissions required for certificate'
    )
    
    min_elearning_progress = fields.Float(
        string='Minimum eLearning Progress (%)',
        default=80.0,
        help='Minimum eLearning progress percentage required for certificate'
    )
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    
    # Statistics
    enrolled_students = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_students',
        store=True
    )
    
    completed_students = fields.Integer(
        string='Completed Students',
        compute='_compute_completed_students',
        store=True
    )
    
    # Progress tracking
    progress_trackers = fields.One2many(
        'gr.progress.tracker',
        'course_integration_id',
        string='Progress Trackers'
    )
    
    # Computed fields
    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_completion_rate',
        store=True
    )
    
    @api.depends('progress_trackers')
    def _compute_enrolled_students(self):
        """Compute number of enrolled students."""
        for record in self:
            record.enrolled_students = len(record.progress_trackers)
    
    @api.depends('progress_trackers', 'progress_trackers.status')
    def _compute_completed_students(self):
        """Compute number of completed students."""
        for record in self:
            record.completed_students = len(record.progress_trackers.filtered(
                lambda p: p.status == 'completed'
            ))
    
    @api.depends('enrolled_students', 'completed_students')
    def _compute_completion_rate(self):
        """Compute completion rate percentage."""
        for record in self:
            if record.enrolled_students > 0:
                record.completion_rate = (record.completed_students / record.enrolled_students) * 100
            else:
                record.completion_rate = 0.0
    
    @api.constrains('completion_threshold')
    def _check_completion_threshold(self):
        """Validate completion threshold."""
        for record in self:
            if record.completion_threshold < 0 or record.completion_threshold > 100:
                raise ValidationError(_('Completion threshold must be between 0 and 100.'))
    
    def action_activate(self):
        """Activate the course integration."""
        for record in self:
            if record.status == 'draft':
                record.status = 'active'
                _logger.info('Course integration activated: %s', record.name)
    
    def action_archive(self):
        """Archive the course integration."""
        for record in self:
            if record.status == 'active':
                record.status = 'archived'
                _logger.info('Course integration archived: %s', record.name)
    
    def action_enroll_eligible_students(self):
        """Open enrollment wizard for eligible students."""
        for record in self:
            if record.status != 'active':
                raise UserError(_('Only active course integrations can enroll students.'))
            
            # Create enrollment wizard specifically for this course
            wizard = self.env['gr.enrollment.wizard'].create({
                'training_program_id': False,  # No training program for individual course enrollment
                'enrollment_type': 'direct_enroll',
                'student_selection_type': 'all_eligible',
                'filter_by_state': 'both',
                'filter_by_english_level': 'any',
                'filter_by_course_preference': True,
                'send_notification': True,
                'auto_assign_agent': True,
            })
            
            return {
                'name': _('Enroll Students in %s') % record.name,
                'type': 'ir.actions.act_window',
                'res_model': 'gr.enrollment.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_course_integration_id': record.id,
                    'course_integration_mode': True,
                }
            }
    
    def action_enroll_with_wizard(self):
        """Open enrollment wizard with advanced options for this course."""
        for record in self:
            if record.status != 'active':
                raise UserError(_('Only active course integrations can enroll students.'))
            
            # Create enrollment wizard with advanced options
            wizard = self.env['gr.enrollment.wizard'].create({
                'training_program_id': False,  # No training program for individual course enrollment
                'enrollment_type': 'direct_enroll',
                'student_selection_type': 'filtered_students',
                'filter_by_state': 'both',
                'filter_by_english_level': 'any',
                'filter_by_course_preference': True,
                'send_notification': True,
                'auto_assign_agent': True,
            })
            
            return {
                'name': _('Advanced Student Enrollment - %s') % record.name,
                'type': 'ir.actions.act_window',
                'res_model': 'gr.enrollment.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_course_integration_id': record.id,
                    'course_integration_mode': True,
                }
            }
    
    def name_get(self):
        """Custom name display."""
        result = []
        for record in self:
            name = f"{record.name} ({record.elearning_course_id.name})"
            result.append((record.id, name))
        return result
