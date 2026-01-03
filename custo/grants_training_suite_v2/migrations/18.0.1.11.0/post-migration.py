# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for version 18.0.1.11.0 - Dynamic Certificate Templates."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info('Starting post-migration script for grants_training_suite_v2 v18.0.1.11.0 - Dynamic Certificate Templates')

    # Create default certificate templates if they don't exist
    template_types = [
        ('program_completion', 'Program Completion Certificate'),
        ('course_completion', 'Course Completion Certificate'),
        ('achievement', 'Achievement Certificate'),
        ('participation', 'Participation Certificate'),
        ('excellence', 'Excellence Certificate'),
        ('custom', 'Custom Certificate'),
    ]

    for template_type, template_name in template_types:
        existing_template = env['gr.certificate.template'].search([
            ('template_type', '=', template_type),
            ('is_default', '=', True)
        ], limit=1)

        if not existing_template:
            # Create default template
            template_vals = {
                'name': template_name,
                'template_type': template_type,
                'description': f'Default template for {template_type.replace("_", " ").title()} certificates',
                'is_default': True,
                'active': True,
            }

            # Add specific content based on template type
            if template_type == 'program_completion':
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #2c3e50;">CERTIFICATE OF PROGRAM COMPLETION</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #3498db; margin: 20px 0;">{student_name}</h2>
                        <p>has successfully completed the</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{program_name}</h3>
                        <p>training program</p>
                        <p>Duration: {duration}</p>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #3498db; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })
            elif template_type == 'course_completion':
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #2c3e50;">CERTIFICATE OF COURSE COMPLETION</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #3498db; margin: 20px 0;">{student_name}</h2>
                        <p>has successfully completed the course</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{course_name}</h3>
                        <p>Duration: {duration}</p>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #3498db; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })
            elif template_type == 'achievement':
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #e74c3c;">ACHIEVEMENT CERTIFICATE</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #e74c3c; margin: 20px 0;">{student_name}</h2>
                        <p>has demonstrated outstanding achievement in</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{program_name}</h3>
                        <p>Grade: {grade}</p>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #e74c3c; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })
            elif template_type == 'participation':
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #27ae60;">CERTIFICATE OF PARTICIPATION</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #27ae60; margin: 20px 0;">{student_name}</h2>
                        <p>has participated in</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{program_name}</h3>
                        <p>Duration: {duration}</p>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #27ae60; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })
            elif template_type == 'excellence':
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #f39c12;">CERTIFICATE OF EXCELLENCE</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #f39c12; margin: 20px 0;">{student_name}</h2>
                        <p>has demonstrated excellence in</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{program_name}</h3>
                        <p>Grade: {grade}</p>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #f39c12; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })
            else:  # custom
                template_vals.update({
                    'header_content': '<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #9b59b6;">CUSTOM CERTIFICATE</div>',
                    'body_content': '''<div style="text-align: center; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                        <p>This certifies that</p>
                        <h2 style="color: #9b59b6; margin: 20px 0;">{student_name}</p>
                        <p>has successfully completed</p>
                        <h3 style="color: #2c3e50; margin: 20px 0;">{program_name}</h3>
                        <p>Completion Date: {completion_date}</p>
                    </div>''',
                    'footer_content': '''<div style="text-align: center; font-size: 12px; margin-top: 40px; border-top: 2px solid #9b59b6; padding-top: 20px;">
                        <p>Certificate Number: {certificate_number}</p>
                        <p>Issued on: {issue_date}</p>
                        <p>{organization_name}</p>
                    </div>''',
                })

            new_template = env['gr.certificate.template'].create(template_vals)
            _logger.info('Created default certificate template: %s (ID: %s)', template_name, new_template.id)

    _logger.info('Finished post-migration script for grants_training_suite_v2 v18.0.1.11.0.')
