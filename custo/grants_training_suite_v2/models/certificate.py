# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Certificate(models.Model):
    _name = 'gr.certificate'
    _description = 'Grants Training Certificate'
    _order = 'issue_date desc'
    _inherit = ['mail.thread']

    # Basic Information
    name = fields.Char(
        string='Certificate Number',
        required=True,
        default=lambda self: _('New'),
        help='Unique certificate number'
    )
    
    # Certificate Details
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student receiving the certificate'
    )
    
    agent_id = fields.Many2one(
        'res.users',
        string='Assigned Agent',
        related='student_id.assigned_agent_id',
        store=True,
        help='Agent assigned to the student'
    )
    
    # Certificate Information
    certificate_type = fields.Selection([
        ('completion', 'Course Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('excellence', 'Excellence'),
        ('professional', 'Professional Development'),
        ('language', 'Language Proficiency'),
        ('technical', 'Technical Skills'),
        ('program_completion', 'Program Completion'),
        ('other', 'Other'),
    ], string='Certificate Type', required=True, tracking=True, help='Type of certificate')
    
    certificate_title = fields.Char(
        string='Certificate Title',
        required=True,
        help='Title of the certificate'
    )
    
    certificate_description = fields.Text(
        string='Certificate Description',
        help='Description of the certificate'
    )
    
    # Course Information
    course_name = fields.Char(
        string='Course Name',
        help='Name of the course for which certificate is issued'
    )
    
    course_duration = fields.Float(
        string='Course Duration (hours)',
        help='Duration of the course in hours'
    )
    
    completion_date = fields.Date(
        string='Course Completion Date',
        help='Date when the course was completed'
    )
    
    # Automation Integration
    automation_id = fields.Many2one(
        'gr.certificate.automation',
        string='Certificate Automation',
        help='Automation rule that generated this certificate'
    )
    
    training_program_id = fields.Many2one(
        'gr.training.program',
        string='Training Program',
        help='Training program this certificate is for'
    )
    
    # ===== Phase 5.1: Dynamic Template Integration =====
    template_id = fields.Many2one(
        'gr.certificate.template',
        string='Certificate Template',
        help='Template used to generate this certificate'
    )
    
    template_type = fields.Selection([
        ('program_completion', 'Program Completion'),
        ('course_completion', 'Course Completion'),
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('excellence', 'Excellence'),
        ('custom', 'Custom'),
    ], string='Template Type', help='Type of certificate template used')
    
    # Rendered Content
    rendered_header = fields.Html(
        string='Rendered Header',
        help='Rendered header content from template'
    )
    
    rendered_body = fields.Html(
        string='Rendered Body',
        help='Rendered body content from template'
    )
    
    rendered_footer = fields.Html(
        string='Rendered Footer',
        help='Rendered footer content from template'
    )
    
    # Issue Information
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        required=True,
        tracking=True,
        help='Date when certificate was issued'
    )
    
    issued_by_id = fields.Many2one(
        'res.users',
        string='Issued By',
        default=lambda self: self.env.user,
        tracking=True,
        help='User who issued the certificate'
    )
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('delivered', 'Delivered'),
        ('verified', 'Verified'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)
    
    # Validity Information
    valid_from = fields.Date(
        string='Valid From',
        default=fields.Date.today,
        help='Date from which certificate is valid'
    )
    
    valid_until = fields.Date(
        string='Valid Until',
        help='Date until which certificate is valid'
    )
    
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True,
        help='Whether the certificate is expired'
    )
    
    days_until_expiry = fields.Integer(
        string='Days Until Expiry',
        compute='_compute_days_until_expiry',
        store=True,
        help='Number of days until certificate expires'
    )
    
    # Performance Information
    final_grade = fields.Float(
        string='Final Grade',
        help='Final grade achieved in the course'
    )
    
    grade_percentage = fields.Float(
        string='Grade Percentage',
        help='Grade as percentage'
    )
    
    attendance_percentage = fields.Float(
        string='Attendance Percentage',
        help='Attendance percentage in the course'
    )
    
    # Certificate File
    certificate_file = fields.Binary(
        string='Certificate File',
        help='Digital certificate file'
    )
    
    certificate_filename = fields.Char(
        string='Certificate Filename',
        help='Name of the certificate file'
    )
    
    # Delivery Information
    delivery_date = fields.Date(
        string='Delivery Date',
        help='Date when certificate was delivered to student'
    )
    
    delivery_method = fields.Selection([
        ('email', 'Email'),
        ('postal', 'Postal Mail'),
        ('in_person', 'In Person'),
        ('digital', 'Digital Download'),
        ('other', 'Other'),
    ], string='Delivery Method', help='Method used to deliver the certificate')
    
    delivery_address = fields.Text(
        string='Delivery Address',
        help='Address where certificate was delivered'
    )
    
    # Additional Information
    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about the certificate'
    )
    
    # Verification Information
    verification_code = fields.Char(
        string='Verification Code',
        help='Unique code for certificate verification'
    )
    
    verification_url = fields.Char(
        string='Verification URL',
        help='URL for online certificate verification'
    )
    
    verified_date = fields.Date(
        string='Verified Date',
        help='Date when certificate was verified'
    )
    
    verified_by_id = fields.Many2one(
        'res.users',
        string='Verified By',
        help='User who verified the certificate'
    )
    
    # Computed Fields
    days_since_issue = fields.Integer(
        string='Days Since Issue',
        compute='_compute_days_since_issue',
        store=True,
        help='Number of days since certificate was issued'
    )
    
    is_valid = fields.Boolean(
        string='Is Valid',
        compute='_compute_is_valid',
        store=True,
        help='Whether the certificate is currently valid'
    )
    
    def _compute_is_expired(self):
        """Compute if certificate is expired."""
        for record in self:
            if record.valid_until:
                record.is_expired = fields.Date.today() > record.valid_until
            else:
                record.is_expired = False
    
    def _compute_days_until_expiry(self):
        """Compute days until expiry."""
        for record in self:
            if record.valid_until:
                delta = record.valid_until - fields.Date.today()
                record.days_until_expiry = delta.days
            else:
                record.days_until_expiry = 0
    
    def _compute_days_since_issue(self):
        """Compute days since issue."""
        for record in self:
            if record.issue_date:
                delta = fields.Date.today() - record.issue_date
                record.days_since_issue = delta.days
            else:
                record.days_since_issue = 0
    
    def _compute_is_valid(self):
        """Compute if certificate is valid."""
        for record in self:
            if record.state == 'verified' and not record.is_expired:
                record.is_valid = True
            else:
                record.is_valid = False
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and verification code."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gr.certificate') or _('New')
        
        # Generate verification code if not provided
        if not vals.get('verification_code'):
            import secrets
            vals['verification_code'] = secrets.token_hex(8).upper()
        
        # Set default validity period (2 years) if not provided
        if not vals.get('valid_until') and vals.get('issue_date'):
            issue_date = fields.Date.from_string(vals['issue_date'])
            vals['valid_until'] = issue_date + timedelta(days=730)  # 2 years
        elif not vals.get('valid_until'):
            vals['valid_until'] = fields.Date.today() + timedelta(days=730)
        
        certificate = super(Certificate, self).create(vals)
        
        # Log creation
        _logger.info('Certificate created: %s - Student: %s, Type: %s', 
                    certificate.name, certificate.student_id.name, certificate.certificate_type)
        
        return certificate
    
    def action_issue(self):
        """Action to issue the certificate."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft certificates can be issued.'))
        
        self.state = 'issued'
        self.issue_date = fields.Date.today()
        self.issued_by_id = self.env.user
        
        # Log issue
        _logger.info('Certificate issued: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Issued'),
                'message': _('Certificate has been issued.'),
                'type': 'success',
            }
        }
    
    def action_deliver(self):
        """Action to deliver the certificate."""
        self.ensure_one()
        
        if self.state != 'issued':
            raise UserError(_('Only issued certificates can be delivered.'))
        
        self.state = 'delivered'
        self.delivery_date = fields.Date.today()
        
        # Log delivery
        _logger.info('Certificate delivered: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Delivered'),
                'message': _('Certificate has been delivered.'),
                'type': 'success',
            }
        }
    
    def action_verify(self):
        """Action to verify the certificate."""
        self.ensure_one()
        
        if self.state not in ['issued', 'delivered']:
            raise UserError(_('Only issued or delivered certificates can be verified.'))
        
        self.state = 'verified'
        self.verified_date = fields.Date.today()
        self.verified_by_id = self.env.user
        
        # Log verification
        _logger.info('Certificate verified: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Verified'),
                'message': _('Certificate has been verified.'),
                'type': 'success',
            }
        }
    
    def action_revoke(self):
        """Action to revoke the certificate."""
        self.ensure_one()
        
        if self.state in ['revoked']:
            raise UserError(_('Certificate is already revoked.'))
        
        self.state = 'revoked'
        
        # Log revocation
        _logger.info('Certificate revoked: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Revoked'),
                'message': _('Certificate has been revoked.'),
                'type': 'warning',
            }
        }
    
    def action_expire(self):
        """Action to mark certificate as expired."""
        self.ensure_one()
        
        if self.state in ['revoked', 'expired']:
            raise UserError(_('Certificate is already revoked or expired.'))
        
        self.state = 'expired'
        
        # Log expiration
        _logger.info('Certificate expired: %s - Student: %s', 
                    self.name, self.student_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Certificate Expired'),
                'message': _('Certificate has been marked as expired.'),
                'type': 'warning',
            }
        }
    
    def action_reset(self):
        """Action to reset certificate to draft."""
        self.ensure_one()
        self.state = 'draft'
        self.issue_date = False
        self.issued_by_id = False
        self.delivery_date = False
        self.verified_date = False
        self.verified_by_id = False
        
        # Log reset
        _logger.info('Certificate reset: %s', self.name)
    
    @api.constrains('valid_until')
    def _check_valid_until(self):
        """Validate valid until date."""
        for record in self:
            if record.valid_until and record.valid_from and record.valid_until < record.valid_from:
                raise ValidationError(_('Valid until date cannot be before valid from date.'))
    
    @api.constrains('final_grade')
    def _check_final_grade(self):
        """Validate final grade."""
        for record in self:
            if record.final_grade and (record.final_grade < 0 or record.final_grade > 100):
                raise ValidationError(_('Final grade must be between 0 and 100.'))
    
    @api.constrains('attendance_percentage')
    def _check_attendance_percentage(self):
        """Validate attendance percentage."""
        for record in self:
            if record.attendance_percentage and (record.attendance_percentage < 0 or record.attendance_percentage > 100):
                raise ValidationError(_('Attendance percentage must be between 0 and 100.'))
    
    def name_get(self):
        """Custom name display for certificate records."""
        result = []
        for record in self:
            name = f"{record.name} - {record.certificate_title} ({record.student_id.name if record.student_id else 'No Student'})"
            result.append((record.id, name))
        return result
    
    # ===== Phase 5.1: Dynamic Template Methods =====
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Update template type when template is selected."""
        if self.template_id:
            self.template_type = self.template_id.template_type
    
    def render_certificate_content(self):
        """Render certificate content using the selected template."""
        self.ensure_one()
        
        if not self.template_id:
            raise UserError(_('No template selected for this certificate.'))
        
        # Prepare context data for template rendering
        context_data = {
            'student_name': self.student_id.name if self.student_id else 'Unknown Student',
            'program_name': self.training_program_id.name if self.training_program_id else self.certificate_title,
            'course_name': self.course_name or self.certificate_title,
            'issue_date': self.issue_date.strftime('%B %d, %Y') if self.issue_date else '',
            'certificate_number': self.name,
            'completion_date': self.completion_date.strftime('%B %d, %Y') if self.completion_date else '',
            'grade': str(self.grade_percentage) + '%' if hasattr(self, 'grade_percentage') and self.grade_percentage else 'N/A',
            'duration': str(self.course_duration) + ' hours' if self.course_duration else 'N/A',
            'instructor_name': self.issued_by_id.name if self.issued_by_id else 'N/A',
            'organization_name': 'Grants Training Organization',
        }
        
        # Render the template
        rendered = self.template_id.render_template(context_data)
        
        # Store rendered content
        self.rendered_header = rendered['header']
        self.rendered_body = rendered['body']
        self.rendered_footer = rendered['footer']
        
        return rendered
    
    def action_preview_certificate(self):
        """Preview the certificate with current template and data."""
        self.ensure_one()
        
        if not self.template_id:
            raise UserError(_('Please select a template first.'))
        
        # Render the content
        rendered = self.render_certificate_content()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificate Preview'),
            'res_model': 'gr.certificate.template.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.template_id.id,
                'default_header_content': rendered['header'],
                'default_body_content': rendered['body'],
                'default_footer_content': rendered['footer'],
                'default_context_data': rendered['context'],
            }
        }
    
    def action_generate_certificate_pdf(self):
        """Generate PDF certificate using the template."""
        self.ensure_one()
        
        if not self.template_id:
            raise UserError(_('Please select a template first.'))
        
        try:
            # Render the content
            rendered = self.render_certificate_content()
            
            # Generate PDF using report engine
            pdf_content = self._generate_certificate_pdf(rendered)
            
            # Update template usage count
            self.template_id.action_update_usage_count()
            
            # Store the PDF file
            self.certificate_file = pdf_content
            self.certificate_filename = f'certificate_{self.name}_{self.student_id.name.replace(" ", "_")}.pdf'
            
            _logger.info('Certificate PDF generated successfully for certificate: %s', self.name)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificate Generated'),
                    'message': _('Certificate PDF has been generated successfully.'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error('Error generating certificate PDF for %s: %s', self.name, str(e))
            raise UserError(_('Error generating certificate PDF: %s') % str(e))
    
    def _generate_certificate_pdf(self, rendered_content):
        """Generate PDF content from rendered certificate."""
        self.ensure_one()
        
        # Prepare the complete HTML content
        html_content = self._prepare_certificate_html(rendered_content)
        
        # Generate PDF using wkhtmltopdf
        try:
            pdf_content = self.env['ir.actions.report']._run_wkhtmltopdf(
                [html_content],
                landscape=False,
                specific_paperformat_args={
                    'command-line': '--page-size A4 --orientation Portrait --margin-top 1in --margin-bottom 1in --margin-left 1in --margin-right 1in'
                }
            )
            return pdf_content
        except Exception as e:
            _logger.error('Error in PDF generation: %s', str(e))
            raise UserError(_('PDF generation failed: %s') % str(e))
    
    def _prepare_certificate_html(self, rendered_content):
        """Prepare complete HTML content for PDF generation."""
        self.ensure_one()
        
        # Get template styling
        template = self.template_id
        
        # Build complete HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Certificate - {self.name}</title>
            <style>
                @page {{
                    size: {template.page_width}in {template.page_height}in;
                    margin: {template.margin_top}in {template.margin_right}in {template.margin_bottom}in {template.margin_left}in;
                }}
                body {{
                    font-family: {template.font_family}, sans-serif;
                    background-color: {template.background_color};
                    color: {template.text_color};
                    margin: 0;
                    padding: 0;
                    line-height: 1.6;
                }}
                .certificate-container {{
                    width: 100%;
                    height: 100%;
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .certificate-header {{
                    flex: 0 0 auto;
                }}
                .certificate-body {{
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .certificate-footer {{
                    flex: 0 0 auto;
                }}
                .accent {{
                    color: {template.accent_color};
                }}
                h1, h2, h3 {{
                    margin: 0;
                }}
                p {{
                    margin: 0;
                }}
            </style>
        </head>
        <body>
            <div class="certificate-container">
                <div class="certificate-header">
                    {rendered_content.get('header', '')}
                </div>
                <div class="certificate-body">
                    {rendered_content.get('body', '')}
                </div>
                <div class="certificate-footer">
                    {rendered_content.get('footer', '')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    # ===== Phase 5.2: Automated Certificate Generation =====
    
    def action_send_certificate_email(self):
        """Send certificate via email to student."""
        self.ensure_one()
        
        if not self.certificate_file:
            raise UserError(_('Please generate the certificate PDF first.'))
        
        if not self.student_id.email:
            raise UserError(_('Student email is required to send the certificate.'))
        
        try:
            # Prepare email content
            subject = _('Your Certificate: %s') % self.certificate_title
            body = _('''
Dear %s,

Congratulations! You have successfully completed the %s and earned your certificate.

Please find your certificate attached to this email.

Certificate Details:
- Certificate Number: %s
- Issue Date: %s
- Valid Until: %s

If you have any questions, please contact us.

Best regards,
Training Team
            ''') % (
                self.student_id.name,
                self.certificate_title,
                self.name,
                self.issue_date.strftime('%B %d, %Y') if self.issue_date else 'N/A',
                self.valid_until.strftime('%B %d, %Y') if self.valid_until else 'N/A'
            )
            
            # Create email
            mail_values = {
                'subject': subject,
                'body_html': body.replace('\n', '<br/>'),
                'email_to': self.student_id.email,
                'email_from': self.env.user.email or 'noreply@training.org',
                'auto_delete': True,
            }
            
            mail = self.env['mail.mail'].create(mail_values)
            
            # Attach certificate
            if self.certificate_file:
                attachment = self.env['ir.attachment'].create({
                    'name': self.certificate_filename,
                    'type': 'binary',
                    'datas': self.certificate_file,
                    'res_model': 'mail.mail',
                    'res_id': mail.id,
                    'mimetype': 'application/pdf',
                })
            
            # Send email
            mail.send()
            
            _logger.info('Certificate email sent to %s for certificate %s', self.student_id.email, self.name)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificate Sent'),
                    'message': _('Certificate has been sent to %s') % self.student_id.email,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error('Error sending certificate email: %s', str(e))
            raise UserError(_('Error sending certificate email: %s') % str(e))
    
    def action_download_certificate(self):
        """Download certificate PDF."""
        self.ensure_one()
        
        if not self.certificate_file:
            raise UserError(_('Certificate PDF has not been generated yet.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=gr.certificate&id={self.id}&field=certificate_file&filename_field=certificate_filename&download=true',
            'target': 'new',
        }
    
    @api.model
    def auto_generate_certificates_for_completed_students(self):
        """Automatically generate certificates for students who have completed training programs."""
        _logger.info('Starting automatic certificate generation for completed students')
        
        # Find students who have completed programs but don't have certificates
        completed_students = self._find_completed_students_without_certificates()
        
        certificates_created = 0
        errors = []
        
        for student_data in completed_students:
            try:
                certificate = self._create_certificate_for_student(student_data)
                if certificate:
                    certificates_created += 1
                    _logger.info('Created certificate %s for student %s', certificate.name, student_data['student'].name)
            except Exception as e:
                error_msg = f"Error creating certificate for {student_data['student'].name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
        
        _logger.info('Automatic certificate generation completed. Created %d certificates, %d errors', 
                    certificates_created, len(errors))
        
        return {
            'certificates_created': certificates_created,
            'errors': errors,
        }
    
    def _find_completed_students_without_certificates(self):
        """Find students who have completed programs but don't have certificates."""
        completed_students = []
        
        # Find students with completed progress trackers
        completed_trackers = self.env['gr.progress.tracker'].search([
            ('status', '=', 'completed'),
            ('completion_date', '!=', False),
        ])
        
        for tracker in completed_trackers:
            student = tracker.student_id
            course = tracker.course_integration_id
            
            # Enhanced success criteria validation
            if not self._validate_success_criteria(tracker, student, course):
                _logger.info('Student %s does not meet success criteria for course %s', 
                           student.name, course.name)
                continue
            
            # Check if student already has a certificate for this course
            existing_certificate = self.search([
                ('student_id', '=', student.id),
                ('course_name', '=', course.name),
                ('state', 'in', ['issued', 'delivered', 'verified']),
            ])
            
            if not existing_certificate:
                completed_students.append({
                    'student': student,
                    'course': course,
                    'tracker': tracker,
                })
        
        return completed_students
    
    def _validate_success_criteria(self, tracker, student, course):
        """Validate that student meets all success criteria for certificate generation."""
        success_criteria_met = True
        criteria_details = []
        
        # 1. Overall progress must meet completion threshold
        if tracker.overall_progress < course.completion_threshold:
            success_criteria_met = False
            criteria_details.append(f'Overall progress {tracker.overall_progress}% < required {course.completion_threshold}%')
        
        # 2. eLearning progress must meet minimum threshold (if applicable)
        if course.elearning_course_id and tracker.elearning_progress < course.min_elearning_progress:
            success_criteria_met = False
            criteria_details.append(f'eLearning progress {tracker.elearning_progress}% < required {course.min_elearning_progress}%')
        
        # 3. Student must have completed minimum required sessions (if applicable)
        if course.min_sessions_required and tracker.custom_sessions_completed < course.min_sessions_required:
            success_criteria_met = False
            criteria_details.append(f'Sessions completed {tracker.custom_sessions_completed} < required {course.min_sessions_required}')
        
        # 4. Student must have submitted minimum required homework (if applicable)
        if course.min_homework_required and tracker.homework_submissions < course.min_homework_required:
            success_criteria_met = False
            criteria_details.append(f'Homework submissions {tracker.homework_submissions} < required {course.min_homework_required}')
        
        # 5. Check if student has any outstanding issues or warnings
        if hasattr(student, 'has_warnings') and student.has_warnings:
            success_criteria_met = False
            criteria_details.append('Student has outstanding warnings or issues')
        
        # Log criteria validation results
        if success_criteria_met:
            _logger.info('Student %s meets all success criteria for course %s', student.name, course.name)
        else:
            _logger.warning('Student %s does not meet success criteria for course %s: %s', 
                          student.name, course.name, '; '.join(criteria_details))
        
        return success_criteria_met
    
    @api.model
    def get_certificate_eligibility_report(self):
        """Generate a comprehensive report of certificate eligibility for dashboard."""
        _logger.info('Generating certificate eligibility report for dashboard')
        
        # Get all completed students
        completed_trackers = self.env['gr.progress.tracker'].search([
            ('status', '=', 'completed'),
            ('completion_date', '!=', False),
        ])
        
        report_data = {
            'total_completed_students': len(completed_trackers),
            'eligible_for_certificates': 0,
            'not_eligible_for_certificates': 0,
            'already_have_certificates': 0,
            'detailed_breakdown': [],
            'success_criteria_summary': {
                'overall_progress_failures': 0,
                'elearning_progress_failures': 0,
                'sessions_failures': 0,
                'homework_failures': 0,
                'warnings_failures': 0,
            }
        }
        
        for tracker in completed_trackers:
            student = tracker.student_id
            course = tracker.course_integration_id
            
            # Check if already has certificate
            existing_certificate = self.search([
                ('student_id', '=', student.id),
                ('course_name', '=', course.name),
                ('state', 'in', ['issued', 'delivered', 'verified']),
            ])
            
            if existing_certificate:
                report_data['already_have_certificates'] += 1
                continue
            
            # Check success criteria
            criteria_met = True
            criteria_failures = []
            
            # Overall progress check
            if tracker.overall_progress < course.completion_threshold:
                criteria_met = False
                criteria_failures.append('overall_progress')
                report_data['success_criteria_summary']['overall_progress_failures'] += 1
            
            # eLearning progress check
            if course.elearning_course_id and tracker.elearning_progress < course.min_elearning_progress:
                criteria_met = False
                criteria_failures.append('elearning_progress')
                report_data['success_criteria_summary']['elearning_progress_failures'] += 1
            
            # Sessions check
            if course.min_sessions_required and tracker.custom_sessions_completed < course.min_sessions_required:
                criteria_met = False
                criteria_failures.append('sessions')
                report_data['success_criteria_summary']['sessions_failures'] += 1
            
            # Homework check
            if course.min_homework_required and tracker.homework_submissions < course.min_homework_required:
                criteria_met = False
                criteria_failures.append('homework')
                report_data['success_criteria_summary']['homework_failures'] += 1
            
            # Warnings check
            if hasattr(student, 'has_warnings') and student.has_warnings:
                criteria_met = False
                criteria_failures.append('warnings')
                report_data['success_criteria_summary']['warnings_failures'] += 1
            
            if criteria_met:
                report_data['eligible_for_certificates'] += 1
            else:
                report_data['not_eligible_for_certificates'] += 1
            
            # Add detailed breakdown
            report_data['detailed_breakdown'].append({
                'student_name': student.name,
                'course_name': course.name,
                'overall_progress': tracker.overall_progress,
                'elearning_progress': tracker.elearning_progress,
                'sessions_completed': tracker.custom_sessions_completed,
                'homework_submissions': tracker.homework_submissions,
                'completion_date': tracker.completion_date,
                'eligible': criteria_met,
                'criteria_failures': criteria_failures,
                'has_certificate': bool(existing_certificate),
            })
        
        _logger.info('Certificate eligibility report generated: %d eligible, %d not eligible, %d already have certificates',
                    report_data['eligible_for_certificates'], 
                    report_data['not_eligible_for_certificates'],
                    report_data['already_have_certificates'])
        
        return report_data
    
    def _create_certificate_for_student(self, student_data):
        """Create certificate for a completed student."""
        student = student_data['student']
        course = student_data['course']
        tracker = student_data['tracker']
        
        # Determine certificate type
        certificate_type = 'completion'
        if tracker.grade_percentage and tracker.grade_percentage >= 90:
            certificate_type = 'excellence'
        elif tracker.grade_percentage and tracker.grade_percentage >= 80:
            certificate_type = 'achievement'
        
        # Create certificate
        certificate_vals = {
            'student_id': student.id,
            'certificate_type': certificate_type,
            'certificate_title': f'{course.name} Completion Certificate',
            'course_name': course.name,
            'course_duration': course.duration_hours or 0,
            'completion_date': tracker.completion_date,
            'issue_date': fields.Date.today(),
            'issued_by_id': self.env.user.id,
            'final_grade': tracker.grade_percentage or 0,
            'attendance_percentage': tracker.attendance_percentage or 100,
            'certificate_description': f'Certificate of completion for {course.name}',
            'state': 'draft',
        }
        
        certificate = self.create(certificate_vals)
        
        # Apply default template
        if certificate_type == 'excellence':
            template_type = 'excellence'
        elif certificate_type == 'achievement':
            template_type = 'achievement'
        else:
            template_type = 'course_completion'
        
        default_template = self.env['gr.certificate.template'].get_default_template(template_type)
        if default_template:
            certificate.template_id = default_template
            certificate.render_certificate_content()
        
        return certificate
    
    def action_apply_default_template(self):
        """Apply the default template for this certificate type."""
        self.ensure_one()
        
        if not self.template_type:
            # Determine template type based on certificate type
            template_type_mapping = {
                'completion': 'program_completion',
                'achievement': 'achievement',
                'participation': 'participation',
                'excellence': 'excellence',
                'program_completion': 'program_completion',
            }
            self.template_type = template_type_mapping.get(self.certificate_type, 'program_completion')
        
        # Get default template
        default_template = self.env['gr.certificate.template'].get_default_template(self.template_type)
        
        if default_template:
            self.template_id = default_template
            self.render_certificate_content()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template Applied'),
                    'message': _('Default template has been applied and content rendered.'),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_('No default template found for type: %s') % self.template_type)
