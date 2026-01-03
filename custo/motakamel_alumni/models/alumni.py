# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class OpAlumni(models.Model):
    _name = 'op.alumni'
    _description = 'Alumni'
    _inherit = ['mail.thread', 'website.published.mixin']
    _rec_name = 'name'
    _order = 'graduation_date desc, id desc'

    # Basic Information
    name = fields.Char('Name', required=True, tracking=True, compute='_compute_name', store=True)
    first_name = fields.Char('First Name', required=True, tracking=True)
    middle_name = fields.Char('Middle Name', translate=True)
    last_name = fields.Char('Last Name', required=True, tracking=True)
    
    alumni_number = fields.Char(
        'Alumni Number', 
        required=True, 
        readonly=True, 
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    
    # Student Reference
    student_id = fields.Many2one(
        'op.student', 
        'Student Record', 
        ondelete='restrict',
        tracking=True,
        help="Original student record"
    )
    
    # Personal Information
    image = fields.Binary('Photo', attachment=True)
    email = fields.Char('Email', required=True, tracking=True)
    phone = fields.Char('Phone', tracking=True)
    mobile = fields.Char('Mobile', tracking=True)
    
    birth_date = fields.Date('Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], 'Gender', tracking=True)
    
    # Address
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    zip = fields.Char('ZIP')
    
    # Academic Information
    course_id = fields.Many2one('op.course', 'Course', required=True, tracking=True)
    batch_id = fields.Many2one('op.batch', 'Batch', tracking=True)
    program_id = fields.Many2one('op.program', 'Program', tracking=True)
    
    admission_date = fields.Date('Admission Date')
    graduation_date = fields.Date('Graduation Date', required=True, tracking=True)
    graduation_year = fields.Char('Graduation Year', compute='_compute_graduation_year', store=True)
    
    grade = fields.Selection([
        ('distinction', 'Distinction'),
        ('first_class', 'First Class'),
        ('second_class', 'Second Class'),
        ('pass', 'Pass')
    ], 'Grade/Division', tracking=True)
    
    cgpa = fields.Float('CGPA', digits=(3, 2))
    percentage = fields.Float('Percentage', digits=(5, 2))
    
    # Professional Information
    current_company = fields.Char('Current Company', tracking=True)
    current_designation = fields.Char('Current Designation', tracking=True)
    industry = fields.Char('Industry')
    work_experience_years = fields.Integer('Years of Experience')
    
    linkedin_url = fields.Char('LinkedIn Profile')
    website = fields.Char('Personal Website')
    
    # Alumni Group
    group_ids = fields.Many2many(
        'op.alumni.group', 
        'alumni_group_rel', 
        'alumni_id', 
        'group_id', 
        'Alumni Groups'
    )
    
    # Events
    event_registration_ids = fields.One2many(
        'op.alumni.event.registration', 
        'alumni_id', 
        'Event Registrations'
    )
    event_count = fields.Integer('Events Attended', compute='_compute_event_count')
    
    # Jobs Posted
    job_ids = fields.One2many('op.alumni.job', 'posted_by', 'Jobs Posted')
    job_count = fields.Integer('Jobs Posted', compute='_compute_job_count')
    
    # Engagement
    last_contact_date = fields.Date('Last Contact Date')
    willing_to_mentor = fields.Boolean('Willing to Mentor', default=False)
    willing_to_recruit = fields.Boolean('Willing to Recruit', default=False)
    
    # Portal Access
    user_id = fields.Many2one('res.users', 'Portal User', ondelete='restrict')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], 'Status', default='draft', tracking=True, required=True)
    
    active = fields.Boolean(default=True)
    
    # Notes
    notes = fields.Text('Notes')
    achievements = fields.Text('Notable Achievements')
    
    _sql_constraints = [
        ('alumni_number_unique', 'unique(alumni_number)', 'Alumni Number must be unique!'),
        ('email_unique', 'unique(email)', 'Email must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('alumni_number', _('New')) == _('New'):
            vals['alumni_number'] = self.env['ir.sequence'].next_by_code('op.alumni') or _('New')
        return super(OpAlumni, self).create(vals)
    
    @api.depends('first_name', 'middle_name', 'last_name')
    def _compute_name(self):
        for alumni in self:
            name_parts = [alumni.first_name or '']
            if alumni.middle_name:
                name_parts.append(alumni.middle_name)
            if alumni.last_name:
                name_parts.append(alumni.last_name)
            alumni.name = ' '.join(name_parts).strip()
    
    @api.depends('graduation_date')
    def _compute_graduation_year(self):
        for alumni in self:
            if alumni.graduation_date:
                alumni.graduation_year = str(alumni.graduation_date.year)
            else:
                alumni.graduation_year = ''
    
    @api.depends('event_registration_ids')
    def _compute_event_count(self):
        for alumni in self:
            alumni.event_count = len(alumni.event_registration_ids.filtered(
                lambda r: r.state == 'attended'
            ))
    
    @api.depends('job_ids')
    def _compute_job_count(self):
        for alumni in self:
            alumni.job_count = len(alumni.job_ids)
    
    def action_activate(self):
        """Activate alumni record"""
        self.write({'state': 'active'})
        return True
    
    def action_deactivate(self):
        """Deactivate alumni record"""
        self.write({'state': 'inactive'})
        return True
    
    def action_create_portal_user(self):
        """Create portal user for alumni"""
        self.ensure_one()
        if self.user_id:
            raise ValidationError(_('Portal user already exists for this alumni!'))
        
        # Create portal user
        portal_group = self.env.ref('base.group_portal')
        user_vals = {
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'groups_id': [(6, 0, [portal_group.id])],
            'partner_id': self._create_partner().id,
        }
        user = self.env['res.users'].create(user_vals)
        self.user_id = user.id
        
        # Send invitation email
        user.action_reset_password()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Portal user created successfully. Invitation email sent.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _create_partner(self):
        """Create partner record for alumni"""
        partner_vals = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'zip': self.zip,
            'is_company': False,
            'customer_rank': 0,
            'supplier_rank': 0,
        }
        return self.env['res.partner'].create(partner_vals)
    
    def action_view_events(self):
        """View alumni events"""
        self.ensure_one()
        return {
            'name': _('Alumni Events'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni.event.registration',
            'view_mode': 'list,form',
            'domain': [('alumni_id', '=', self.id)],
            'context': {'default_alumni_id': self.id}
        }
    
    def action_view_jobs(self):
        """View jobs posted by alumni"""
        self.ensure_one()
        return {
            'name': _('Jobs Posted'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni.job',
            'view_mode': 'list,form',
            'domain': [('posted_by', '=', self.id)],
            'context': {'default_posted_by': self.id}
        }
    
    def action_send_email(self):
        """Send email to alumni"""
        self.ensure_one()
        template = self.env.ref('motakamel_alumni.email_template_alumni_general', 
                               raise_if_not_found=False)
        if template:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_model': 'op.alumni',
                    'default_res_id': self.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id if template else False,
                }
            }

