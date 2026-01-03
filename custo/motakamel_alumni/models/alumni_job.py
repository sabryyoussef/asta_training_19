# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class OpAlumniJob(models.Model):
    _name = 'op.alumni.job'
    _description = 'Alumni Job Posting'
    _inherit = ['mail.thread', 'website.published.mixin']
    _order = 'create_date desc'

    name = fields.Char('Job Title', required=True, tracking=True)
    job_number = fields.Char(
        'Job Number', 
        required=True, 
        readonly=True, 
        default=lambda self: _('New'),
        copy=False
    )
    
    # Company Information
    company_name = fields.Char('Company Name', required=True, tracking=True)
    company_website = fields.Char('Company Website')
    company_description = fields.Text('About Company')
    
    # Job Details
    description = fields.Html('Job Description', required=True)
    responsibilities = fields.Html('Key Responsibilities')
    requirements = fields.Html('Requirements')
    
    # Job Type
    job_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance')
    ], 'Job Type', required=True, tracking=True)
    
    # Experience
    experience_required = fields.Selection([
        ('fresher', 'Fresher'),
        ('0-2', '0-2 years'),
        ('2-5', '2-5 years'),
        ('5-10', '5-10 years'),
        ('10+', '10+ years')
    ], 'Experience Required', required=True)
    
    # Location
    location = fields.Char('Job Location', required=True)
    is_remote = fields.Boolean('Remote Work Available')
    
    # Salary
    salary_range = fields.Char('Salary Range')
    currency_id = fields.Many2one('res.currency', 'Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Skills
    skills_required = fields.Text('Skills Required')
    
    # Application
    application_deadline = fields.Date('Application Deadline', tracking=True)
    application_email = fields.Char('Application Email')
    application_url = fields.Char('Application URL')
    application_instructions = fields.Text('Application Instructions')
    
    # Posted By
    posted_by = fields.Many2one('op.alumni', 'Posted By', required=True, 
                                default=lambda self: self._get_default_alumni())
    posted_date = fields.Date('Posted Date', default=fields.Date.today, readonly=True)
    
    # Applications
    application_ids = fields.One2many('op.alumni.job.application', 'job_id', 'Applications')
    application_count = fields.Integer('Applications', compute='_compute_application_count')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('filled', 'Position Filled')
    ], 'Status', default='draft', tracking=True, required=True)
    
    active = fields.Boolean(default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('job_number', _('New')) == _('New'):
            vals['job_number'] = self.env['ir.sequence'].next_by_code('op.alumni.job') or _('New')
        return super(OpAlumniJob, self).create(vals)
    
    def _get_default_alumni(self):
        """Get alumni record for current user"""
        if self.env.user:
            alumni = self.env['op.alumni'].search([('user_id', '=', self.env.user.id)], limit=1)
            return alumni.id if alumni else False
        return False
    
    @api.depends('application_ids')
    def _compute_application_count(self):
        for job in self:
            job.application_count = len(job.application_ids)
    
    def action_publish(self):
        """Publish job"""
        self.write({'state': 'published', 'is_published': True})
        return True
    
    def action_close(self):
        """Close job posting"""
        self.state = 'closed'
        return True
    
    def action_mark_filled(self):
        """Mark position as filled"""
        self.state = 'filled'
        return True
    
    def action_view_applications(self):
        """View job applications"""
        self.ensure_one()
        return {
            'name': _('Job Applications'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni.job.application',
            'view_mode': 'list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id}
        }


class OpAlumniJobApplication(models.Model):
    _name = 'op.alumni.job.application'
    _description = 'Alumni Job Application'
    _inherit = ['mail.thread']
    _order = 'application_date desc'

    job_id = fields.Many2one('op.alumni.job', 'Job', required=True, ondelete='cascade')
    applicant_id = fields.Many2one('op.alumni', 'Applicant')
    
    # Applicant Details (if not alumni)
    applicant_name = fields.Char('Name', required=True)
    applicant_email = fields.Char('Email', required=True)
    applicant_phone = fields.Char('Phone')
    
    # Application
    application_date = fields.Date('Application Date', default=fields.Date.today, readonly=True)
    cover_letter = fields.Text('Cover Letter')
    resume = fields.Binary('Resume/CV', attachment=True)
    resume_filename = fields.Char('Resume Filename')
    
    # Status
    state = fields.Selection([
        ('applied', 'Applied'),
        ('screening', 'Under Screening'),
        ('interview', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn')
    ], 'Status', default='applied', tracking=True, required=True)
    
    # Notes
    notes = fields.Text('Notes')
    
    _sql_constraints = [
        ('job_applicant_unique', 'unique(job_id, applicant_email)', 
         'You have already applied for this job!'),
    ]

