# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Assignment(models.Model):
    _name = 'gr.assignment'
    _description = 'Grants Training Assignment'
    _order = 'create_date desc'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Assignment Reference',
        required=True,
        default=lambda self: _('New'),
        help='Unique reference for this assignment'
    )
    
    # Assignment Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student being assigned'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        required=True,
        tracking=True,
        help='Agent assigned to the student'
    )
    
    # Assignment Information
    assignment_date = fields.Datetime(
        string='Assignment Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='Date when the assignment was made'
    )
    
    assigned_by_id = fields.Many2one(
        'res.users',
        string='Assigned By',
        default=lambda self: self.env.user,
        tracking=True,
        help='User who made the assignment'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('contacted', 'Contacted'),
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Contact Information
    first_contact_date = fields.Datetime(
        string='First Contact Date',
        help='Date when agent first contacted the student'
    )
    
    last_contact_date = fields.Datetime(
        string='Last Contact Date',
        help='Date of last contact with the student'
    )
    
    contact_attempts = fields.Integer(
        string='Contact Attempts',
        default=0,
        help='Number of contact attempts made'
    )
    
    # Assignment Notes
    assignment_notes = fields.Text(
        string='Assignment Notes',
        help='Notes about the assignment'
    )
    
    contact_notes = fields.Text(
        string='Contact Notes',
        help='Notes from agent contacts with student'
    )
    
    # Performance Metrics
    response_time = fields.Float(
        string='Response Time (hours)',
        compute='_compute_response_time',
        store=True,
        help='Time taken to first contact after assignment'
    )
    
    enrollment_time = fields.Float(
        string='Enrollment Time (hours)',
        compute='_compute_enrollment_time',
        store=True,
        help='Time taken from assignment to enrollment'
    )
    
    completion_time = fields.Float(
        string='Completion Time (hours)',
        compute='_compute_completion_time',
        store=True,
        help='Time taken from assignment to completion'
    )
    
    # Computed Fields
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='Whether the assignment is overdue for contact'
    )
    
    days_since_assignment = fields.Integer(
        string='Days Since Assignment',
        compute='_compute_days_since_assignment',
        store=True,
        help='Number of days since assignment was made'
    )
    
    def _compute_response_time(self):
        """Compute response time from assignment to first contact."""
        for record in self:
            if record.assignment_date and record.first_contact_date:
                delta = record.first_contact_date - record.assignment_date
                record.response_time = delta.total_seconds() / 3600  # Convert to hours
            else:
                record.response_time = 0.0
    
    def _compute_enrollment_time(self):
        """Compute enrollment time from assignment to enrollment."""
        for record in self:
            if record.assignment_date and record.state in ['enrolled', 'in_progress', 'completed']:
                # Find when state changed to enrolled
                # For now, we'll use a simple calculation
                # In a real implementation, you might track state changes
                record.enrollment_time = 0.0  # TODO: Implement proper tracking
            else:
                record.enrollment_time = 0.0
    
    def _compute_completion_time(self):
        """Compute completion time from assignment to completion."""
        for record in self:
            if record.assignment_date and record.state == 'completed':
                # Find when state changed to completed
                # For now, we'll use a simple calculation
                # In a real implementation, you might track state changes
                record.completion_time = 0.0  # TODO: Implement proper tracking
            else:
                record.completion_time = 0.0
    
    def _compute_is_overdue(self):
        """Compute if assignment is overdue for contact."""
        for record in self:
            if record.assignment_date and not record.first_contact_date:
                # Check if more than 24 hours have passed
                delta = fields.Datetime.now() - record.assignment_date
                record.is_overdue = delta.total_seconds() > 86400  # 24 hours
            else:
                record.is_overdue = False
    
    def _compute_days_since_assignment(self):
        """Compute days since assignment."""
        for record in self:
            if record.assignment_date:
                delta = fields.Datetime.now() - record.assignment_date
                record.days_since_assignment = delta.days
            else:
                record.days_since_assignment = 0
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and initial state."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.assignment') or _('New')
        
        assignment = super(Assignment, self).create(vals)
        
        # Update student's assignment information
        if assignment.student_id:
            assignment.student_id.assigned_agent_id = assignment.agent_id
            assignment.student_id.assignment_date = assignment.assignment_date
            assignment.student_id.state = 'assigned'
        
        # Log creation
        _logger.info('Assignment created: %s - Student: %s, Agent: %s', 
                    assignment.name, assignment.student_id.name, assignment.agent_id.name)
        
        return assignment
    
    def write(self, vals):
        """Override write to update student information when assignment changes."""
        result = super(Assignment, self).write(vals)
        
        # Update student information if assignment changes
        for record in self:
            if 'agent_id' in vals and record.student_id:
                record.student_id.assigned_agent_id = record.agent_id
            if 'assignment_date' in vals and record.student_id:
                record.student_id.assignment_date = record.assignment_date
        
        return result
    
    def action_assign(self):
        """Action to confirm the assignment."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft assignments can be confirmed.'))
        
        self.state = 'assigned'
        
        # Log assignment
        _logger.info('Assignment confirmed: %s - Student: %s, Agent: %s', 
                    self.name, self.student_id.name, self.agent_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Assignment Confirmed'),
                'message': _('Student has been assigned to agent %s.') % self.agent_id.name,
                'type': 'success',
            }
        }
    
    def action_mark_contacted(self):
        """Action to mark student as contacted."""
        self.ensure_one()
        
        if self.state not in ['assigned', 'contacted']:
            raise UserError(_('Student must be assigned first.'))
        
        if not self.first_contact_date:
            self.first_contact_date = fields.Datetime.now()
        
        self.last_contact_date = fields.Datetime.now()
        self.contact_attempts += 1
        self.state = 'contacted'
        
        # Update student state
        if self.student_id:
            self.student_id.first_contact_date = self.first_contact_date
            self.student_id.state = 'contacted'
        
        # Log contact
        _logger.info('Student contacted: %s by agent %s', 
                    self.student_id.name, self.agent_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Student Contacted'),
                'message': _('Student has been marked as contacted.'),
                'type': 'success',
            }
        }
    
    def action_enroll(self):
        """Action to enroll student."""
        self.ensure_one()
        
        if self.state != 'contacted':
            raise UserError(_('Student must be contacted first.'))
        
        self.state = 'enrolled'
        
        # Update student state
        if self.student_id:
            self.student_id.state = 'enrolled'
        
        # Log enrollment
        _logger.info('Student enrolled: %s', self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Student Enrolled'),
                'message': _('Student has been enrolled.'),
                'type': 'success',
            }
        }
    
    def action_start_course(self):
        """Action to start course for student."""
        self.ensure_one()
        
        if self.state != 'enrolled':
            raise UserError(_('Student must be enrolled first.'))
        
        self.state = 'in_progress'
        
        # Update student state
        if self.student_id:
            self.student_id.state = 'in_progress'
        
        # Log course start
        _logger.info('Course started for student: %s', self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Course Started'),
                'message': _('Course has been started for the student.'),
                'type': 'success',
            }
        }
    
    def action_complete(self):
        """Action to mark assignment as completed."""
        self.ensure_one()
        
        if self.state != 'in_progress':
            raise UserError(_('Student must be in progress first.'))
        
        self.state = 'completed'
        
        # Update student state
        if self.student_id:
            self.student_id.state = 'completed'
        
        # Log completion
        _logger.info('Assignment completed: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Assignment Completed'),
                'message': _('Assignment has been completed.'),
                'type': 'success',
            }
        }
    
    def action_cancel(self):
        """Action to cancel the assignment."""
        self.ensure_one()
        
        if self.state in ['completed']:
            raise UserError(_('Completed assignments cannot be cancelled.'))
        
        self.state = 'cancelled'
        
        # Reset student assignment
        if self.student_id:
            self.student_id.assigned_agent_id = False
            self.student_id.assignment_date = False
            self.student_id.first_contact_date = False
            self.student_id.state = 'eligible'
        
        # Log cancellation
        _logger.info('Assignment cancelled: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Assignment Cancelled'),
                'message': _('Assignment has been cancelled.'),
                'type': 'warning',
            }
        }
    
    def action_reset(self):
        """Action to reset assignment to draft."""
        self.ensure_one()
        self.state = 'draft'
        self.first_contact_date = False
        self.last_contact_date = False
        self.contact_attempts = 0
        
        # Log reset
        _logger.info('Assignment reset: %s', self.name)
    
    @api.constrains('student_id', 'agent_id')
    def _check_unique_assignment(self):
        """Ensure student is not assigned to multiple agents."""
        for record in self:
            if record.student_id and record.agent_id:
                existing = self.search([
                    ('student_id', '=', record.student_id.id),
                    ('agent_id', '=', record.agent_id.id),
                    ('state', 'not in', ['cancelled', 'completed']),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('This student is already assigned to this agent.'))
    
    @api.constrains('assignment_date')
    def _check_assignment_date(self):
        """Validate assignment date."""
        for record in self:
            if record.assignment_date and record.assignment_date > fields.Datetime.now():
                raise ValidationError(_('Assignment date cannot be in the future.'))
    
    def name_get(self):
        """Custom name display for assignment records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.student_id.name if record.student_id else 'No Student'}"
            result.append((record.id, name))
        return result
