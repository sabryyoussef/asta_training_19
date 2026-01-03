# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.12.0 - Automated Certificate Generation."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.12.0 - Automated Certificate Generation')

    # Create email template for certificate notifications if it doesn't exist
    existing_template = env['mail.template'].search([
        ('name', '=', 'Certificate Notification'),
        ('model', '=', 'gr.certificate'),
    ], limit=1)

    if not existing_template:
        template_vals = {
            'name': 'Certificate Notification',
            'model_id': env.ref('grants_training_suite_v2.model_gr_certificate').id,
            'subject': 'Your Certificate: {{ object.certificate_title }}',
            'body_html': '''
<div style="margin: 0px; padding: 0px;">
    <p>Dear {{ object.student_id.name }},</p>
    <p>Congratulations! You have successfully completed the <strong>{{ object.certificate_title }}</strong> and earned your certificate.</p>
    <p>Please find your certificate attached to this email.</p>
    
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="color: #2c3e50; margin-top: 0;">Certificate Details:</h3>
        <ul style="margin: 0; padding-left: 20px;">
            <li><strong>Certificate Number:</strong> {{ object.name }}</li>
            <li><strong>Issue Date:</strong> {{ object.issue_date }}</li>
            <li><strong>Valid Until:</strong> {{ object.valid_until or 'No expiration' }}</li>
            <li><strong>Course:</strong> {{ object.course_name }}</li>
        </ul>
    </div>
    
    <p>If you have any questions about your certificate, please contact us.</p>
    <p>Best regards,<br/>Training Team</p>
</div>
            ''',
            'auto_delete': True,
        }
        
        new_template = env['mail.template'].create(template_vals)
        _logger.info('Created certificate notification email template (ID: %s)', new_template.id)
    else:
        _logger.info('Certificate notification email template already exists (ID: %s)', existing_template.id)

    # Create a scheduled action for automatic certificate generation (disabled by default)
    existing_cron = env['ir.cron'].search([
        ('name', '=', 'Auto-Generate Certificates'),
        ('model_id', '=', env.ref('grants_training_suite_v2.model_gr_certificate').id),
    ], limit=1)

    if not existing_cron:
        cron_vals = {
            'name': 'Auto-Generate Certificates',
            'model_id': env.ref('grants_training_suite_v2.model_gr_certificate').id,
            'state': 'code',
            'code': 'model.auto_generate_certificates_for_completed_students()',
            'interval_number': 1,
            'interval_type': 'days',
            'active': False,  # Disabled by default, can be enabled manually
        }
        
        new_cron = env['ir.cron'].create(cron_vals)
        _logger.info('Created automatic certificate generation cron job (ID: %s) - DISABLED by default', new_cron.id)
    else:
        _logger.info('Automatic certificate generation cron job already exists (ID: %s)', existing_cron.id)

    # Update existing certificates to ensure they have proper template integration
    certificates_without_templates = env['gr.certificate'].search([
        ('template_id', '=', False),
        ('state', 'in', ['draft', 'issued', 'delivered', 'verified']),
    ])
    
    _logger.info('Found %d certificates without templates to update', len(certificates_without_templates))
    
    for certificate in certificates_without_templates:
        try:
            # Apply default template based on certificate type
            template_type_mapping = {
                'completion': 'course_completion',
                'achievement': 'achievement',
                'participation': 'participation',
                'excellence': 'excellence',
                'program_completion': 'program_completion',
            }
            
            template_type = template_type_mapping.get(certificate.certificate_type, 'course_completion')
            default_template = env['gr.certificate.template'].get_default_template(template_type)
            
            if default_template:
                certificate.template_id = default_template
                certificate.template_type = template_type
                _logger.info('Applied template %s to certificate %s', default_template.name, certificate.name)
            
        except Exception as e:
            _logger.error('Error updating certificate %s: %s', certificate.name, str(e))

    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.12.0.')
