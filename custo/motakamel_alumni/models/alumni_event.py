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


class OpAlumniEvent(models.Model):
    _name = 'op.alumni.event'
    _description = 'Alumni Event'
    _inherit = ['mail.thread', 'website.published.mixin']
    _order = 'event_date desc'

    name = fields.Char('Event Name', required=True, tracking=True)
    event_number = fields.Char(
        'Event Number', 
        required=True, 
        readonly=True, 
        default=lambda self: _('New'),
        copy=False
    )
    
    # Event Details
    event_type = fields.Selection([
        ('reunion', 'Reunion'),
        ('networking', 'Networking'),
        ('seminar', 'Seminar/Workshop'),
        ('social', 'Social Gathering'),
        ('fundraiser', 'Fundraiser'),
        ('sports', 'Sports Event'),
        ('cultural', 'Cultural Event'),
        ('other', 'Other')
    ], 'Event Type', required=True, tracking=True)
    
    description = fields.Html('Description')
    
    # Date & Time
    event_date = fields.Datetime('Event Date', required=True, tracking=True)
    event_end_date = fields.Datetime('End Date', tracking=True)
    duration = fields.Float('Duration (hours)', compute='_compute_duration', store=True)
    
    # Venue
    venue = fields.Char('Venue', required=True)
    venue_address = fields.Text('Venue Address')
    is_online = fields.Boolean('Online Event')
    meeting_url = fields.Char('Meeting URL')
    
    # Registration
    registration_required = fields.Boolean('Registration Required', default=True)
    registration_deadline = fields.Date('Registration Deadline')
    max_attendees = fields.Integer('Maximum Attendees')
    
    # Fees
    is_paid = fields.Boolean('Paid Event')
    registration_fee = fields.Float('Registration Fee')
    currency_id = fields.Many2one('res.currency', 'Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Target Audience
    target_group_ids = fields.Many2many('op.alumni.group', string='Target Groups')
    target_graduation_years = fields.Char('Target Graduation Years', 
                                          help="e.g., 2020-2023")
    open_to_all = fields.Boolean('Open to All Alumni', default=True)
    
    # Registrations
    registration_ids = fields.One2many('op.alumni.event.registration', 'event_id', 'Registrations')
    registered_count = fields.Integer('Registered', compute='_compute_registration_stats', store=True)
    attended_count = fields.Integer('Attended', compute='_compute_registration_stats', store=True)
    
    # Organizer
    organizer_id = fields.Many2one('res.users', 'Organizer', default=lambda self: self.env.user)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('registration_open', 'Registration Open'),
        ('registration_closed', 'Registration Closed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True, required=True)
    
    active = fields.Boolean(default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('event_number', _('New')) == _('New'):
            vals['event_number'] = self.env['ir.sequence'].next_by_code('op.alumni.event') or _('New')
        return super(OpAlumniEvent, self).create(vals)
    
    @api.depends('event_date', 'event_end_date')
    def _compute_duration(self):
        for event in self:
            if event.event_date and event.event_end_date:
                delta = event.event_end_date - event.event_date
                event.duration = delta.total_seconds() / 3600
            else:
                event.duration = 0.0
    
    @api.depends('registration_ids', 'registration_ids.state')
    def _compute_registration_stats(self):
        for event in self:
            event.registered_count = len(event.registration_ids.filtered(
                lambda r: r.state in ['registered', 'attended']
            ))
            event.attended_count = len(event.registration_ids.filtered(
                lambda r: r.state == 'attended'
            ))
    
    def action_publish(self):
        """Publish event"""
        self.write({'state': 'published', 'is_published': True})
        return True
    
    def action_open_registration(self):
        """Open registration"""
        self.state = 'registration_open'
        return True
    
    def action_close_registration(self):
        """Close registration"""
        self.state = 'registration_closed'
        return True
    
    def action_start_event(self):
        """Mark event as in progress"""
        self.state = 'in_progress'
        return True
    
    def action_complete_event(self):
        """Mark event as completed"""
        self.state = 'completed'
        return True
    
    def action_cancel_event(self):
        """Cancel event"""
        self.state = 'cancelled'
        # Notify registered alumni
        return True
    
    def action_view_registrations(self):
        """View event registrations"""
        self.ensure_one()
        return {
            'name': _('Event Registrations'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni.event.registration',
            'view_mode': 'list,form',
            'domain': [('event_id', '=', self.id)],
            'context': {'default_event_id': self.id}
        }


class OpAlumniEventRegistration(models.Model):
    _name = 'op.alumni.event.registration'
    _description = 'Alumni Event Registration'
    _inherit = ['mail.thread']
    _order = 'registration_date desc'

    event_id = fields.Many2one('op.alumni.event', 'Event', required=True, ondelete='cascade')
    alumni_id = fields.Many2one('op.alumni', 'Alumni', required=True, tracking=True)
    
    registration_date = fields.Datetime('Registration Date', default=fields.Datetime.now, readonly=True)
    
    # Guest Information
    number_of_guests = fields.Integer('Number of Guests', default=0)
    guest_names = fields.Text('Guest Names')
    
    # Payment (if applicable)
    payment_required = fields.Boolean(related='event_id.is_paid', store=True)
    payment_amount = fields.Float(related='event_id.registration_fee', store=True)
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], 'Payment Status', default='pending', tracking=True)
    
    # Attendance
    attended = fields.Boolean('Attended', tracking=True)
    attendance_marked_date = fields.Datetime('Attendance Marked Date')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', tracking=True, required=True)
    
    # Notes
    special_requirements = fields.Text('Special Requirements')
    notes = fields.Text('Notes')
    
    _sql_constraints = [
        ('event_alumni_unique', 'unique(event_id, alumni_id)', 
         'Alumni already registered for this event!'),
    ]
    
    def action_confirm(self):
        """Confirm registration"""
        self.state = 'confirmed'
        # Send confirmation email
        return True
    
    def action_mark_attended(self):
        """Mark as attended"""
        self.write({
            'attended': True,
            'state': 'attended',
            'attendance_marked_date': fields.Datetime.now()
        })
        return True
    
    def action_cancel(self):
        """Cancel registration"""
        self.state = 'cancelled'
        return True

