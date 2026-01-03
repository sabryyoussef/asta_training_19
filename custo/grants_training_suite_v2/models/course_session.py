# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class CourseSession(models.Model):
    _name = 'gr.course.session'
    _description = 'Grants Training Course Session'
    _order = 'session_date desc'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Session Name',
        required=True,
        default='New Session',
        help='Name of the course session'
    )
    
    # Session Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student attending the session'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        related='student_id.assigned_agent_id',
        store=True,
        help='Agent assigned to the student'
    )
    
    # Session Information
    session_date = fields.Datetime(
        string='Session Date',
        required=True,
        tracking=True,
        help='Date and time of the session'
    )
    
    session_duration = fields.Float(
        string='Duration (hours)',
        default=1.0,
        help='Duration of the session in hours'
    )
    
    session_type = fields.Selection([
        ('online', 'Online'),
        ('in_person', 'In Person'),
        ('hybrid', 'Hybrid'),
    ], string='Session Type', default='online', tracking=True, help='Type of session')
    
    # Location Information
    location = fields.Char(
        string='Location',
        help='Location of the session (for in-person sessions)'
    )
    
    meeting_link = fields.Char(
        string='Meeting Link',
        help='Online meeting link (for online sessions)'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ], string='Status', default='scheduled', tracking=True)
    
    # Attendance Information
    attendance_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ], string='Attendance', help='Student attendance status')
    
    check_in_time = fields.Datetime(
        string='Check-in Time',
        help='Time when student checked in'
    )
    
    check_out_time = fields.Datetime(
        string='Check-out Time',
        help='Time when student checked out'
    )
    
    # Session Content
    session_topic = fields.Char(
        string='Session Topic',
        help='Main topic covered in this session'
    )
    
    session_objectives = fields.Text(
        string='Session Objectives',
        help='Learning objectives for this session'
    )
    
    session_notes = fields.Text(
        string='Session Notes',
        help='Notes from the session'
    )
    
    # Progress Tracking
    progress_percentage = fields.Float(
        string='Progress (%)',
        help='Progress made in this session (0-100)'
    )
    
    homework_assigned = fields.Text(
        string='Homework Assigned',
        help='Homework assigned during this session'
    )
    
    homework_due_date = fields.Datetime(
        string='Homework Due Date',
        help='Due date for assigned homework'
    )
    
    # Performance Metrics
    student_engagement = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], string='Student Engagement', help='Student engagement level during session')
    
    session_rating = fields.Selection([
        ('5', 'Excellent (5)'),
        ('4', 'Good (4)'),
        ('3', 'Average (3)'),
        ('2', 'Poor (2)'),
        ('1', 'Very Poor (1)'),
    ], string='Session Rating', help='Overall session rating')
    
    # Computed Fields
    is_upcoming = fields.Boolean(
        string='Is Upcoming',
        compute='_compute_is_upcoming',
        store=True,
        help='Whether the session is upcoming'
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='Whether the session is overdue'
    )
    
    days_until_session = fields.Integer(
        string='Days Until Session',
        compute='_compute_days_until_session',
        store=True,
        help='Number of days until the session'
    )
    
    actual_duration = fields.Float(
        string='Actual Duration (hours)',
        compute='_compute_actual_duration',
        store=True,
        help='Actual duration of the session'
    )
    
    def _compute_is_upcoming(self):
        """Compute if session is upcoming."""
        for record in self:
            if record.session_date and record.state == 'scheduled':
                record.is_upcoming = record.session_date > fields.Datetime.now()
            else:
                record.is_upcoming = False
    
    def _compute_is_overdue(self):
        """Compute if session is overdue."""
        for record in self:
            if record.session_date and record.state == 'scheduled':
                record.is_overdue = fields.Datetime.now() > record.session_date
            else:
                record.is_overdue = False
    
    def _compute_days_until_session(self):
        """Compute days until session."""
        for record in self:
            if record.session_date:
                delta = record.session_date - fields.Datetime.now()
                record.days_until_session = delta.days
            else:
                record.days_until_session = 0
    
    def _compute_actual_duration(self):
        """Compute actual session duration."""
        for record in self:
            if record.check_in_time and record.check_out_time:
                delta = record.check_out_time - record.check_in_time
                record.actual_duration = delta.total_seconds() / 3600  # Convert to hours
            else:
                record.actual_duration = 0.0
    
    @api.onchange('student_id', 'session_date')
    def _onchange_suggest_name(self):
        """Suggest session name when student or date changes."""
        if self.student_id and self.session_date:
            try:
                date_str = self.session_date.strftime('%Y-%m-%d %H:%M')
                suggested_name = f"Session - {self.student_id.name} - {date_str}"
                if not self.name or self.name == 'New Session':
                    self.name = suggested_name
            except:
                if not self.name or self.name == 'New Session':
                    self.name = f"Session - {self.student_id.name}"
    
    @api.model
    def create(self, vals):
        """Override create to set default values."""
        # Generate session name if not provided
        if not vals.get('name') or vals.get('name') == 'New':
            student_name = vals.get('student_id') and self.env['gr.student'].browse(vals['student_id']).name or 'Student'
            session_date = vals.get('session_date')
            if session_date:
                try:
                    date_obj = fields.Datetime.from_string(session_date)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                    vals['name'] = f"Session - {student_name} - {date_str}"
                except:
                    vals['name'] = f"Session - {student_name}"
            else:
                vals['name'] = f"Session - {student_name}"
        
        course_session = super(CourseSession, self).create(vals)
        
        # Log creation
        _logger.info('Course session created: %s - Student: %s, Date: %s', 
                    course_session.name, course_session.student_id.name, course_session.session_date)
        
        return course_session
    
    def action_start_session(self):
        """Action to start the session."""
        self.ensure_one()
        
        if self.state != 'scheduled':
            raise UserError(_('Only scheduled sessions can be started.'))
        
        self.state = 'in_progress'
        self.check_in_time = fields.Datetime.now()
        
        # Log session start
        _logger.info('Course session started: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Session Started'),
                'message': _('Course session has been started.'),
                'type': 'success',
            }
        }
    
    def action_complete_session(self):
        """Action to complete the session."""
        self.ensure_one()
        
        if self.state != 'in_progress':
            raise UserError(_('Only sessions in progress can be completed.'))
        
        self.state = 'completed'
        self.check_out_time = fields.Datetime.now()
        self.attendance_status = 'present'
        
        # Log session completion
        _logger.info('Course session completed: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Session Completed'),
                'message': _('Course session has been completed.'),
                'type': 'success',
            }
        }
    
    def action_mark_no_show(self):
        """Action to mark student as no show."""
        self.ensure_one()
        
        if self.state not in ['scheduled', 'in_progress']:
            raise UserError(_('Only scheduled or in-progress sessions can be marked as no show.'))
        
        self.state = 'no_show'
        self.attendance_status = 'absent'
        
        # Log no show
        _logger.info('Student no show: %s - Session: %s', 
                    self.student_id.name, self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('No Show Marked'),
                'message': _('Student has been marked as no show.'),
                'type': 'warning',
            }
        }
    
    def action_cancel_session(self):
        """Action to cancel the session."""
        self.ensure_one()
        
        if self.state in ['completed']:
            raise UserError(_('Completed sessions cannot be cancelled.'))
        
        self.state = 'cancelled'
        
        # Log cancellation
        _logger.info('Course session cancelled: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Session Cancelled'),
                'message': _('Course session has been cancelled.'),
                'type': 'warning',
            }
        }
    
    def action_reschedule(self):
        """Action to reschedule the session."""
        self.ensure_one()
        
        if self.state not in ['scheduled', 'cancelled']:
            raise UserError(_('Only scheduled or cancelled sessions can be rescheduled.'))
        
        self.state = 'scheduled'
        self.attendance_status = False
        self.check_in_time = False
        self.check_out_time = False
        
        # Log reschedule
        _logger.info('Course session rescheduled: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Session Rescheduled'),
                'message': _('Course session has been rescheduled.'),
                'type': 'info',
            }
        }
    
    @api.constrains('session_date')
    def _check_session_date(self):
        """Validate session date."""
        for record in self:
            if record.session_date and record.session_date < fields.Datetime.now() - timedelta(days=1):
                raise ValidationError(_('Session date cannot be more than 1 day in the past.'))
    
    @api.constrains('session_duration')
    def _check_session_duration(self):
        """Validate session duration."""
        for record in self:
            if record.session_duration <= 0:
                raise ValidationError(_('Session duration must be greater than 0.'))
            if record.session_duration > 8:
                raise ValidationError(_('Session duration cannot exceed 8 hours.'))
    
    @api.constrains('progress_percentage')
    def _check_progress_percentage(self):
        """Validate progress percentage."""
        for record in self:
            if record.progress_percentage < 0 or record.progress_percentage > 100:
                raise ValidationError(_('Progress percentage must be between 0 and 100.'))
    
    def name_get(self):
        """Custom name display for course session records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.student_id.name if record.student_id else 'No Student'} ({record.session_date.strftime('%Y-%m-%d %H:%M') if record.session_date else 'No Date'})"
            result.append((record.id, name))
        return result
