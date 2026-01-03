# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Student(models.Model):
    _name = 'gr.student'
    _description = 'Grants Training Student'
    _order = 'create_date desc'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Full Name',
        required=True,
        tracking=True,
        help='Student full name'
    )
    
    name_arabic = fields.Char(
        string='Student Name (Arabic)',
        required=True,
        tracking=True,
        help='Student name in Arabic'
    )
    
    name_english = fields.Char(
        string='Student Name (English)',
        required=True,
        tracking=True,
        help='Student name in English'
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True,
        help='Student email address'
    )
    
    phone = fields.Char(
        string='Phone',
        tracking=True,
        help='Student phone number'
    )
    
    # Personal Information
    birth_date = fields.Date(
        string='Birth Date',
        tracking=True,
        help='Student birth date'
    )
    
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        help='Student age calculated from birth date'
    )
    
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', tracking=True)
    
    nationality = fields.Char(
        string='Nationality',
        help='Student nationality'
    )
    
    # Language Information
    native_language = fields.Char(
        string='Native Language',
        help='Student native language'
    )
    
    english_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('upper_intermediate', 'Upper Intermediate'),
        ('advanced', 'Advanced'),
        ('proficient', 'Proficient'),
    ], string='English Level', tracking=True, help='Student English proficiency level')
    
    # Eligibility Information
    has_certificate = fields.Boolean(
        string='Has Certificate',
        default=False,
        tracking=True,
        help='Does the student have a required certificate?'
    )
    
    certificate_type = fields.Char(
        string='Certificate Type',
        help='Type of certificate the student has'
    )
    
    certificate_date = fields.Date(
        string='Certificate Date',
        help='Date when certificate was obtained'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('eligible', 'Eligible'),
        ('assigned', 'Assigned to Agent'),
        ('contacted', 'Contacted'),
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('certified', 'Certified'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    
    # Intake Information
    intake_batch_id = fields.Many2one(
        'gr.intake.batch',
        string='Intake Batch',
        help='Batch from which this student was imported'
    )
    
    intake_date = fields.Datetime(
        string='Intake Date',
        default=fields.Datetime.now,
        help='Date when student was added to the system'
    )
    
    # Assignment Information
    assigned_agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        tracking=True,
        help='Agent assigned to this student'
    )
    
    assignment_date = fields.Datetime(
        string='Assignment Date',
        help='Date when student was assigned to an agent'
    )
    
    first_contact_date = fields.Datetime(
        string='First Contact Date',
        help='Date when agent first contacted the student'
    )
    
    # Course Information
    course_session_ids = fields.One2many(
        'gr.course.session',
        'student_id',
        string='Course Sessions',
        help='Course sessions this student is enrolled in'
    )
    
    # Course Selection
    preferred_course_integration_id = fields.Many2one(
        'gr.course.integration',
        string='Preferred Course',
        help='Course integration the student prefers to be enrolled in'
    )
    
    enrollment_type = fields.Selection([
        ('auto', 'Auto Enroll'),
        ('manual', 'Manual Enroll'),
        ('import', 'Import Enrollment'),
    ], string='Enrollment Type', default='auto', tracking=True,
       help='Type of enrollment for this student')
    
    # Assessment Information
    homework_attempt_ids = fields.One2many(
        'gr.homework.attempt',
        'student_id',
        string='Homework Attempts',
        help='Homework attempts by this student'
    )
    
    # Certificate Information
    certificate_ids = fields.One2many(
        'gr.certificate',
        'student_id',
        string='Certificates',
        help='Certificates earned by this student'
    )
    
    # eLearning Integration
    elearning_enrollments = fields.One2many(
        'slide.channel.partner',
        'partner_id',
        string='eLearning Enrollments',
        domain=[('partner_id', '=', 'id')],
        help='eLearning course enrollments'
    )
    
    elearning_progress = fields.Float(
        string='eLearning Progress (%)',
        compute='_compute_elearning_progress',
        store=True,
        help='Overall eLearning progress percentage'
    )
    
    completed_courses = fields.Integer(
        string='Completed Courses',
        compute='_compute_completed_courses',
        store=True,
        help='Number of completed eLearning courses'
    )
    
    # Integration status
    integration_status = fields.Selection([
        ('not_integrated', 'Not Integrated'),
        ('enrolled', 'Enrolled in eLearning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('certified', 'Certified')
    ], string='Integration Status', default='not_integrated', tracking=True)
    
    # Progress tracking
    progress_trackers = fields.One2many(
        'gr.progress.tracker',
        'student_id',
        string='Progress Trackers',
        help='Progress tracking records for integrated courses'
    )
    
    # Computed Fields
    total_sessions = fields.Integer(
        string='Total Sessions',
        compute='_compute_total_sessions',
        store=True,
        help='Total number of course sessions'
    )
    
    completed_sessions = fields.Integer(
        string='Completed Sessions',
        compute='_compute_completed_sessions',
        store=True,
        help='Number of completed sessions'
    )
    
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress_percentage',
        store=True,
        help='Course completion percentage'
    )
    
    # Eligibility Assessment
    is_eligible = fields.Boolean(
        string='Is Eligible',
        compute='_compute_eligibility',
        store=True,
        help='Whether student meets eligibility criteria'
    )
    
    eligibility_reason = fields.Text(
        string='Eligibility Reason',
        compute='_compute_eligibility',
        store=True,
        help='Reason for eligibility or rejection'
    )
    
    @api.depends('birth_date')
    def _compute_age(self):
        """Compute age from birth date."""
        today = date.today()
        for record in self:
            if record.birth_date:
                age = today.year - record.birth_date.year
                if today.month < record.birth_date.month or \
                   (today.month == record.birth_date.month and today.day < record.birth_date.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0
    
    @api.depends('course_session_ids')
    def _compute_total_sessions(self):
        """Compute total number of course sessions."""
        for record in self:
            record.total_sessions = len(record.course_session_ids)
    
    @api.depends('course_session_ids', 'course_session_ids.state')
    def _compute_completed_sessions(self):
        """Compute number of completed sessions."""
        for record in self:
            record.completed_sessions = len(record.course_session_ids.filtered(lambda s: s.state == 'completed'))
    
    @api.depends('elearning_enrollments', 'elearning_enrollments.completion')
    def _compute_elearning_progress(self):
        """Compute overall eLearning progress."""
        for record in self:
            if record.elearning_enrollments:
                total_progress = sum(enrollment.completion for enrollment in record.elearning_enrollments)
                record.elearning_progress = total_progress / len(record.elearning_enrollments)
            else:
                record.elearning_progress = 0.0
    
    @api.depends('elearning_enrollments', 'elearning_enrollments.completion')
    def _compute_completed_courses(self):
        """Compute number of completed eLearning courses."""
        for record in self:
            record.completed_courses = len(record.elearning_enrollments.filtered(lambda e: e.completion >= 100.0))
    
    def action_auto_enroll_eligible_courses(self):
        """Auto-enroll student in eligible eLearning courses."""
        self.ensure_one()
        
        if not self.is_eligible:
            raise UserError(_('Student is not eligible for enrollment. Please check eligibility criteria.'))
        
        # Find active course integrations with auto-enrollment enabled
        domain = [
            ('status', '=', 'active'),
            ('auto_enroll_eligible', '=', True)
        ]
        
        # If student has a preferred course, prioritize it
        if self.preferred_course_integration_id and self.preferred_course_integration_id.status == 'active':
            if self.preferred_course_integration_id.auto_enroll_eligible:
                course_integrations = self.preferred_course_integration_id
            else:
                # Preferred course exists but not auto-enroll eligible, show message
                raise UserError(_('Your preferred course "%s" is not available for auto-enrollment. Please use manual enrollment.') % self.preferred_course_integration_id.name)
        else:
            course_integrations = self.env['gr.course.integration'].search(domain)
        
        enrollments_created = 0
        for integration in course_integrations:
            # Check if student is already enrolled
            existing_enrollment = self.env['slide.channel.partner'].search([
                ('partner_id', '=', self.id),
                ('channel_id', '=', integration.elearning_course_id.id)
            ])
            
            if not existing_enrollment:
                try:
                    # Create eLearning enrollment
                    enrollment = self.env['slide.channel.partner'].create({
                        'partner_id': self.id,
                        'channel_id': integration.elearning_course_id.id,
                        'enroll_date': fields.Datetime.now(),
                    })
                    
                    # Create progress tracker
                    self.env['gr.progress.tracker'].create({
                        'student_id': self.id,
                        'course_integration_id': integration.id,
                        'elearning_enrollment_id': enrollment.id,
                        'status': 'not_started',
                    })
                    
                    enrollments_created += 1
                    _logger.info('Auto-enrolled student %s in course %s', self.name, integration.elearning_course_id.name)
                    
                except Exception as e:
                    _logger.error('Failed to auto-enroll student %s in course %s: %s', 
                                self.name, integration.elearning_course_id.name, str(e))
                    continue
        
        if enrollments_created > 0:
            # Update integration status
            self.integration_status = 'enrolled'
            message = _('Auto-enrolled in %d eLearning courses') % enrollments_created
            self.message_post(body=message)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Enrollment Successful'),
                    'message': message,
                    'type': 'success',
                }
            }
        else:
            # Provide more helpful error message
            if self.preferred_course_integration_id:
                message = _('No eligible courses found for auto-enrollment. Your preferred course "%s" is not available for auto-enrollment. Please use manual enrollment or contact your agent.') % self.preferred_course_integration_id.name
            else:
                message = _('No eligible courses found for auto-enrollment. Please ensure there are active course integrations with auto-enrollment enabled. Contact your administrator if this issue persists.')
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Enrollments'),
                    'message': message,
                    'type': 'warning',
                }
            }
    
    def action_manual_enroll_course(self):
        """Manual enrollment in specific eLearning course."""
        self.ensure_one()
        
        # Check if there are active course integrations
        active_integrations = self.env['gr.course.integration'].search([('status', '=', 'active')])
        
        if not active_integrations:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Courses Available'),
                    'message': _('No active course integrations found. Please contact your administrator to set up available courses.'),
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Course for Enrollment'),
            'res_model': 'gr.course.integration',
            'view_mode': 'list,form',
            'domain': [('status', '=', 'active')],
            'context': {
                'default_student_id': self.id,
                'student_id': self.id,
                'search_default_active': 1,
            },
            'target': 'new',
        }
    
    def action_sync_elearning_progress(self):
        """Synchronize eLearning progress from external system."""
        self.ensure_one()
        
        if not self.elearning_enrollments:
            raise UserError(_('Student has no eLearning enrollments to sync.'))
        
        sync_count = 0
        for enrollment in self.elearning_enrollments:
            # Update progress tracker if exists
            progress_tracker = self.env['gr.progress.tracker'].search([
                ('student_id', '=', self.id),
                ('elearning_enrollment_id', '=', enrollment.id)
            ])
            
            if progress_tracker:
                old_progress = progress_tracker.elearning_progress
                progress_tracker.action_sync_with_elearning()
                if old_progress != progress_tracker.elearning_progress:
                    sync_count += 1
        
        if sync_count > 0:
            message = _('Synchronized progress for %d enrollments') % sync_count
            self.message_post(body=message)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': message,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Updates'),
                    'message': _('All enrollments are already up to date.'),
                    'type': 'info',
                }
            }
    
    @api.depends('total_sessions', 'completed_sessions')
    def _compute_progress_percentage(self):
        """Compute course progress percentage."""
        for record in self:
            if record.total_sessions > 0:
                record.progress_percentage = (record.completed_sessions / record.total_sessions) * 100
            else:
                record.progress_percentage = 0.0
    
    @api.depends('age', 'english_level', 'has_certificate')
    def _compute_eligibility(self):
        """Compute eligibility based on criteria."""
        for record in self:
            reasons = []
            eligible = True
            
            # Age requirement (18-65)
            if record.age < 18:
                eligible = False
                reasons.append('Age must be at least 18 years')
            elif record.age > 65:
                eligible = False
                reasons.append('Age must be 65 years or less')
            
            # English level requirement (at least intermediate)
            if record.english_level in ['beginner', 'elementary']:
                eligible = False
                reasons.append('English level must be at least intermediate')
            
            # Certificate requirement
            if not record.has_certificate:
                eligible = False
                reasons.append('Required certificate is missing')
            
            record.is_eligible = eligible
            if eligible:
                record.eligibility_reason = 'Student meets all eligibility criteria'
            else:
                record.eligibility_reason = '; '.join(reasons)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set intake date and assess eligibility."""
        students = super(Student, self).create(vals_list)
        
        # Assess eligibility after creation
        for student in students:
            student._assess_eligibility()
            # Log creation
            _logger.info('Student created: %s (%s)', student.name, student.email)
        
        return students
    
    def write(self, vals):
        """Override write to reassess eligibility if relevant fields change."""
        result = super(Student, self).write(vals)
        
        # Reassess eligibility if relevant fields changed
        relevant_fields = ['age', 'english_level', 'has_certificate', 'birth_date']
        if any(field in vals for field in relevant_fields):
            for record in self:
                record._assess_eligibility()
        
        return result
    
    def _assess_eligibility(self):
        """Assess student eligibility and update state."""
        self.ensure_one()
        
        if self.is_eligible:
            if self.state == 'draft':
                self.state = 'eligible'
                _logger.info('Student %s marked as eligible', self.name)
        else:
            if self.state in ['draft', 'eligible']:
                self.state = 'rejected'
                _logger.info('Student %s marked as rejected: %s', self.name, self.eligibility_reason)
    
    def action_assign_agent(self):
        """Action to assign an agent to the student."""
        self.ensure_one()
        
        if self.state != 'eligible':
            raise UserError(_('Only eligible students can be assigned to agents.'))
        
        # Find available agent (round-robin assignment)
        agent_group = self.env.ref('grants_training_suite_v2.group_agent', raise_if_not_found=False)
        if not agent_group:
            raise UserError(_('Agent group not found. Please contact system administrator.'))
        
        available_agents = self.env['res.users'].search([
            ('groups_id', 'in', [agent_group.id]),
            ('active', '=', True)
        ])
        
        if not available_agents:
            raise UserError(_('No available agents found.'))
        
        # Simple round-robin assignment (can be improved)
        agent = available_agents[0]
        
        self.assigned_agent_id = agent
        self.assignment_date = fields.Datetime.now()
        self.state = 'assigned'
        
        # Log assignment
        _logger.info('Student %s assigned to agent %s', self.name, agent.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Agent Assigned'),
                'message': _('Student has been assigned to agent %s.') % agent.name,
                'type': 'success',
            }
        }
    
    def action_mark_contacted(self):
        """Action to mark student as contacted by agent."""
        self.ensure_one()
        
        if self.state != 'assigned':
            raise UserError(_('Student must be assigned to an agent first.'))
        
        self.first_contact_date = fields.Datetime.now()
        self.state = 'contacted'
        
        # Log contact
        _logger.info('Student %s marked as contacted by agent %s', self.name, self.assigned_agent_id.name)
        
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
        """Action to enroll student in a course."""
        self.ensure_one()
        
        if self.state != 'contacted':
            raise UserError(_('Student must be contacted first before enrollment.'))
        
        self.state = 'enrolled'
        
        # Log enrollment
        _logger.info('Student %s enrolled in course', self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Student Enrolled'),
                'message': _('Student has been enrolled in the course.'),
                'type': 'success',
            }
        }
    
    def action_start_course(self):
        """Action to start the course for the student."""
        self.ensure_one()
        
        if self.state != 'enrolled':
            raise UserError(_('Student must be enrolled first.'))
        
        self.state = 'in_progress'
        
        # Log course start
        _logger.info('Student %s started the course', self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Course Started'),
                'message': _('Student has started the course.'),
                'type': 'success',
            }
        }
    
    def action_complete_course(self):
        """Action to mark course as completed."""
        self.ensure_one()
        
        if self.state != 'in_progress':
            raise UserError(_('Student must be in progress first.'))
        
        self.state = 'completed'
        
        # Log completion
        _logger.info('Student %s completed the course', self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Course Completed'),
                'message': _('Student has completed the course.'),
                'type': 'success',
            }
        }
    
    def action_issue_certificate(self):
        """Action to issue certificate to student."""
        self.ensure_one()
        
        if self.state != 'completed':
            raise UserError(_('Student must complete the course first.'))
        
        self.state = 'certified'
        
        # Log certification
        _logger.info('Student %s received certificate', self.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Issued'),
                'message': _('Certificate has been issued to the student.'),
                'type': 'success',
            }
        }
    
    def action_reset(self):
        """Action to reset student to draft state."""
        self.ensure_one()
        self.state = 'draft'
        self.assigned_agent_id = False
        self.assignment_date = False
        self.first_contact_date = False
        
        # Log reset
        _logger.info('Student %s reset to draft state', self.name)
    
    @api.constrains('email')
    def _check_email(self):
        """Validate email format."""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(_('Please enter a valid email address.'))
    
    @api.constrains('age')
    def _check_age(self):
        """Validate age range."""
        for record in self:
            if record.age and (record.age < 0 or record.age > 100):
                raise ValidationError(_('Age must be between 0 and 100 years.'))
