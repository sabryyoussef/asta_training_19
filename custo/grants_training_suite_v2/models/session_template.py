# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SessionTemplate(models.Model):
    _name = 'gr.session.template'
    _description = 'Course Session Template'
    _order = 'name'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the session template'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of this session template'
    )
    
    # Template Configuration
    default_topic = fields.Char(
        string='Default Topic',
        help='Default topic for sessions created from this template'
    )
    
    default_objectives = fields.Text(
        string='Default Objectives',
        help='Default objectives for sessions created from this template'
    )
    
    default_duration = fields.Float(
        string='Default Duration (hours)',
        default=1.0,
        help='Default duration for sessions created from this template'
    )
    
    default_type = fields.Selection([
        ('online', 'Online'),
        ('in_person', 'In Person'),
        ('hybrid', 'Hybrid'),
    ], string='Default Session Type', default='online', help='Default session type')
    
    # Location Settings
    default_location = fields.Char(
        string='Default Location',
        help='Default location for in-person sessions'
    )
    
    default_meeting_link = fields.Char(
        string='Default Meeting Link',
        help='Default meeting link for online sessions'
    )
    
    # Template Settings
    auto_schedule = fields.Boolean(
        string='Auto Schedule',
        default=True,
        help='Automatically schedule sessions when created from this template'
    )
    
    default_schedule_days = fields.Integer(
        string='Default Schedule Days Ahead',
        default=7,
        help='How many days ahead to schedule sessions by default'
    )
    
    preferred_time_slots = fields.Text(
        string='Preferred Time Slots',
        help='Preferred time slots for scheduling (e.g., "9:00-10:00, 14:00-15:00")'
    )
    
    # Target Audience
    target_english_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('any', 'Any Level'),
    ], string='Target English Level', default='any', help='Target English level for this template')
    
    target_course_integration = fields.Many2one(
        'gr.course.integration',
        string='Target Course Integration',
        help='Specific course integration this template is designed for'
    )
    
    # Template Usage
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active and can be used'
    )
    
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        help='Number of times this template has been used'
    )
    
    last_used = fields.Datetime(
        string='Last Used',
        help='When this template was last used'
    )
    
    # Computed Fields
    sessions_created = fields.Integer(
        string='Sessions Created',
        compute='_compute_sessions_created',
        store=True,
        help='Number of sessions created using this template'
    )
    
    @api.depends('usage_count')
    def _compute_sessions_created(self):
        """Compute number of sessions created using this template."""
        for record in self:
            # This would be calculated based on actual session records
            # For now, we'll use the usage_count field
            record.sessions_created = record.usage_count
    
    def action_use_template(self):
        """Mark template as used and update statistics."""
        self.ensure_one()
        self.write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now()
        })
        return True
    
    def action_preview_template(self):
        """Preview how a session would look with this template."""
        self.ensure_one()
        
        preview_data = {
            'template_name': self.name,
            'topic': self.default_topic or 'Sample Topic',
            'objectives': self.default_objectives or 'Sample objectives',
            'duration': f"{self.default_duration} hours",
            'type': dict(self._fields['default_type'].selection)[self.default_type],
            'location': self.default_location or 'Not specified',
            'meeting_link': self.default_meeting_link or 'Not specified',
        }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Preview'),
                'message': _('Template "%s" preview:\nTopic: %s\nDuration: %s\nType: %s') % 
                          (self.name, preview_data['topic'], preview_data['duration'], preview_data['type']),
                'type': 'info',
                'sticky': True,
            }
        }
    
    @api.constrains('default_duration')
    def _check_default_duration(self):
        """Validate default duration."""
        for record in self:
            if record.default_duration <= 0:
                raise ValidationError(_('Default duration must be greater than 0.'))
            if record.default_duration > 8:
                raise ValidationError(_('Default duration cannot exceed 8 hours.'))
    
    @api.constrains('default_schedule_days')
    def _check_default_schedule_days(self):
        """Validate default schedule days."""
        for record in self:
            if record.default_schedule_days < 0:
                raise ValidationError(_('Default schedule days cannot be negative.'))
            if record.default_schedule_days > 365:
                raise ValidationError(_('Default schedule days cannot exceed 365.'))
    
    def name_get(self):
        """Custom name display for session template records."""
        result = []
        for record in self:
            name = f"{record.name}"
            if not record.is_active:
                name += " (Inactive)"
            result.append((record.id, name))
        return result
