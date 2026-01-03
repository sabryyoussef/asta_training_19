# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

class CertificateTemplate(models.Model):
    _name = 'gr.certificate.template'
    _description = 'Certificate Template'
    _order = 'name'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the certificate template'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of the certificate template'
    )
    
    # Template Configuration
    template_type = fields.Selection([
        ('program_completion', 'Program Completion'),
        ('course_completion', 'Course Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('excellence', 'Excellence'),
        ('custom', 'Custom'),
    ], string='Template Type', required=True, default='program_completion', help='Type of certificate template')
    
    # Template Content
    header_content = fields.Html(
        string='Header Content',
        default='<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px;">CERTIFICATE OF COMPLETION</div>',
        help='HTML content for the certificate header'
    )
    
    body_content = fields.Html(
        string='Body Content',
        default='<div style="text-align: center; font-size: 16px; line-height: 1.6;">This certifies that<br/><strong>{student_name}</strong><br/>has successfully completed the<br/><strong>{program_name}</strong><br/>training program.</div>',
        help='HTML content for the certificate body (use placeholders like {student_name}, {program_name})'
    )
    
    footer_content = fields.Html(
        string='Footer Content',
        default='<div style="text-align: center; font-size: 12px; margin-top: 30px;"><p>Issued on: {issue_date}</p><p>Certificate Number: {certificate_number}</p></div>',
        help='HTML content for the certificate footer'
    )
    
    # Styling and Layout
    background_color = fields.Char(
        string='Background Color',
        default='#ffffff',
        help='Background color for the certificate (hex code)'
    )
    
    text_color = fields.Char(
        string='Text Color',
        default='#000000',
        help='Primary text color for the certificate (hex code)'
    )
    
    accent_color = fields.Char(
        string='Accent Color',
        default='#007bff',
        help='Accent color for highlights (hex code)'
    )
    
    font_family = fields.Selection([
        ('Arial', 'Arial'),
        ('Times New Roman', 'Times New Roman'),
        ('Helvetica', 'Helvetica'),
        ('Georgia', 'Georgia'),
        ('Verdana', 'Verdana'),
        ('Courier New', 'Courier New'),
    ], string='Font Family', default='Arial', help='Font family for the certificate')
    
    # Layout Configuration
    page_width = fields.Float(
        string='Page Width (inches)',
        default=8.5,
        help='Width of the certificate page in inches'
    )
    
    page_height = fields.Float(
        string='Page Height (inches)',
        default=11.0,
        help='Height of the certificate page in inches'
    )
    
    margin_top = fields.Float(
        string='Top Margin (inches)',
        default=1.0,
        help='Top margin in inches'
    )
    
    margin_bottom = fields.Float(
        string='Bottom Margin (inches)',
        default=1.0,
        help='Bottom margin in inches'
    )
    
    margin_left = fields.Float(
        string='Left Margin (inches)',
        default=1.0,
        help='Left margin in inches'
    )
    
    margin_right = fields.Float(
        string='Right Margin (inches)',
        default=1.0,
        help='Right margin in inches'
    )
    
    # Logo and Images
    logo_image = fields.Binary(
        string='Logo Image',
        help='Logo image for the certificate'
    )
    
    logo_filename = fields.Char(
        string='Logo Filename',
        help='Filename of the logo image'
    )
    
    logo_position = fields.Selection([
        ('top_left', 'Top Left'),
        ('top_center', 'Top Center'),
        ('top_right', 'Top Right'),
        ('bottom_left', 'Bottom Left'),
        ('bottom_center', 'Bottom Center'),
        ('bottom_right', 'Bottom Right'),
    ], string='Logo Position', default='top_center', help='Position of the logo on the certificate')
    
    # Signature Configuration
    signature_image = fields.Binary(
        string='Signature Image',
        help='Signature image for the certificate'
    )
    
    signature_filename = fields.Char(
        string='Signature Filename',
        help='Filename of the signature image'
    )
    
    signature_position = fields.Selection([
        ('bottom_left', 'Bottom Left'),
        ('bottom_center', 'Bottom Center'),
        ('bottom_right', 'Bottom Right'),
    ], string='Signature Position', default='bottom_right', help='Position of the signature on the certificate')
    
    signature_text = fields.Char(
        string='Signature Text',
        default='Program Director',
        help='Text below the signature'
    )
    
    # Template Status
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this template is active and can be used'
    )
    
    is_default = fields.Boolean(
        string='Default Template',
        default=False,
        help='Whether this is the default template for its type'
    )
    
    # Usage Tracking
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        help='Number of times this template has been used'
    )
    
    last_used_date = fields.Datetime(
        string='Last Used',
        help='Date when this template was last used'
    )
    
    # Related Certificates
    certificate_ids = fields.One2many(
        'gr.certificate',
        'template_id',
        string='Certificates',
        help='Certificates generated using this template'
    )
    
    certificate_count = fields.Integer(
        string='Certificate Count',
        compute='_compute_certificate_count',
        store=True,
        help='Number of certificates generated using this template'
    )
    
    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        """Compute the number of certificates using this template."""
        for template in self:
            template.certificate_count = len(template.certificate_ids)
    
    @api.constrains('is_default', 'template_type')
    def _check_default_template(self):
        """Ensure only one default template per type."""
        for template in self:
            if template.is_default:
                existing_default = self.search([
                    ('template_type', '=', template.template_type),
                    ('is_default', '=', True),
                    ('id', '!=', template.id)
                ])
                if existing_default:
                    raise ValidationError(_('Only one default template is allowed per template type.'))
    
    @api.model
    def get_default_template(self, template_type):
        """Get the default template for a given type."""
        template = self.search([
            ('template_type', '=', template_type),
            ('is_default', '=', True),
            ('active', '=', True)
        ], limit=1)
        
        if not template:
            # Fallback to any active template of the same type
            template = self.search([
                ('template_type', '=', template_type),
                ('active', '=', True)
            ], limit=1)
        
        return template
    
    def render_template(self, context_data):
        """Render the template with provided context data."""
        self.ensure_one()
        
        # Prepare the context data with defaults
        context = {
            'student_name': context_data.get('student_name', 'Unknown Student'),
            'program_name': context_data.get('program_name', 'Training Program'),
            'course_name': context_data.get('course_name', 'Course'),
            'issue_date': context_data.get('issue_date', datetime.now().strftime('%B %d, %Y')),
            'certificate_number': context_data.get('certificate_number', 'N/A'),
            'completion_date': context_data.get('completion_date', datetime.now().strftime('%B %d, %Y')),
            'grade': context_data.get('grade', 'N/A'),
            'duration': context_data.get('duration', 'N/A'),
            'instructor_name': context_data.get('instructor_name', 'N/A'),
            'organization_name': context_data.get('organization_name', 'Training Organization'),
        }
        
        # Render header content
        header = self.header_content.format(**context) if self.header_content else ''
        
        # Render body content
        body = self.body_content.format(**context) if self.body_content else ''
        
        # Render footer content
        footer = self.footer_content.format(**context) if self.footer_content else ''
        
        return {
            'header': header,
            'body': body,
            'footer': footer,
            'context': context
        }
    
    def action_preview_template(self):
        """Preview the template with sample data."""
        self.ensure_one()
        
        sample_context = {
            'student_name': 'John Doe',
            'program_name': 'Sample Training Program',
            'course_name': 'Sample Course',
            'issue_date': datetime.now().strftime('%B %d, %Y'),
            'certificate_number': 'CERT-001',
            'completion_date': datetime.now().strftime('%B %d, %Y'),
            'grade': 'A+',
            'duration': '40 hours',
            'instructor_name': 'Dr. Smith',
            'organization_name': 'Training Organization',
        }
        
        rendered = self.render_template(sample_context)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Template Preview'),
            'res_model': 'gr.certificate.template.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_header_content': rendered['header'],
                'default_body_content': rendered['body'],
                'default_footer_content': rendered['footer'],
                'default_context_data': sample_context,
            }
        }
    
    def action_duplicate_template(self):
        """Duplicate this template."""
        self.ensure_one()
        
        copy_vals = {
            'name': f"{self.name} (Copy)",
            'is_default': False,  # Don't duplicate default status
        }
        
        new_template = self.copy(copy_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificate Template'),
            'res_model': 'gr.certificate.template',
            'res_id': new_template.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_update_usage_count(self):
        """Update usage count and last used date."""
        self.ensure_one()
        self.usage_count += 1
        self.last_used_date = fields.Datetime.now()
    
    def name_get(self):
        """Custom name display for certificate template records."""
        result = []
        for record in self:
            name = record.name
            if record.is_default:
                name = f"{name} (Default)"
            result.append((record.id, name))
        return result
