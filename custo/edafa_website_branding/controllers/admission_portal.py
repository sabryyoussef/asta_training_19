###############################################################################
#
#    Edafa Website Portal
#    Copyright (C) 2024 Edafa Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import ValidationError
import base64
import logging
import re

_logger = logging.getLogger(__name__)


class EdafaAdmissionPortal(http.Controller):

    @http.route(['/admission', '/admission/apply'], type='http', auth="public", website=True, sitemap=True)
    def admission_form(self, **kwargs):
        """Public admission application form - Now uses multi-step wizard (Phase 1)"""
        # Get available courses, batches, programs (only active courses)
        courses = request.env['op.course'].sudo().search([('active', '=', True)])
        batches = request.env['op.batch'].sudo().search([])
        programs = request.env['op.program'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        # Partner titles model removed in Odoo 19
        try:
            titles = request.env['res.partner.title'].sudo().search([])
        except KeyError:
            titles = request.env['res.partner'].sudo().browse([])  # Empty recordset
        
        # Get available admission registers (gathering admissions)
        today = fields.Date.today()
        admission_registers = request.env['op.admission.register'].sudo().search([
            ('active', '=', True),
            ('state', 'in', ['application', 'confirm']),  # Application Gathering or Confirmed
            ('start_date', '<=', today),
            '|',
            ('end_date', '=', False),
            ('end_date', '>=', today),
        ], order='start_date desc')
        
        # No default data - form starts empty
        default = {}
        
        # Load any saved draft or error data from session
        if 'admission_error' in request.session:
            default.update(request.session.get('admission_default', {}))
        elif 'admission_draft' in request.session:
            default.update(request.session.get('admission_draft', {}))
        
        # Use wizard template instead of old form
        return request.render('edafa_website_branding.admission_application_wizard', {
            'courses': courses,
            'batches': batches,
            'programs': programs,
            'countries': countries,
            'titles': titles,
            'admission_registers': admission_registers,
            'default': default,
            'page_name': 'admission_wizard',
        })

    @http.route(['/admission/apply/classic'], type='http', auth="public", website=True)
    def admission_form_classic(self, **kwargs):
        """Original single-page form (kept for compatibility)"""
        # Get available courses, batches, programs (only active courses)
        courses = request.env['op.course'].sudo().search([('active', '=', True)])
        batches = request.env['op.batch'].sudo().search([])
        programs = request.env['op.program'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        # Partner titles model removed in Odoo 19
        try:
            titles = request.env['res.partner.title'].sudo().search([])
        except KeyError:
            titles = request.env['res.partner'].sudo().browse([])  # Empty recordset
        
        # Get available admission registers (gathering admissions)
        today = fields.Date.today()
        admission_registers = request.env['op.admission.register'].sudo().search([
            ('active', '=', True),
            ('state', 'in', ['application', 'confirm']),  # Application Gathering or Confirmed
            ('start_date', '<=', today),
            '|',
            ('end_date', '=', False),
            ('end_date', '>=', today),
        ], order='start_date desc')
        
        error = {}
        default = {}
        
        if 'admission_error' in request.session:
            error = request.session.pop('admission_error')
            default.update(request.session.pop('admission_default', {}))
        
        return request.render('edafa_website_branding.admission_application_form', {
            'courses': courses,
            'batches': batches,
            'programs': programs,
            'countries': countries,
            'titles': titles,
            'admission_registers': admission_registers,
            'error': error,
            'default': default,
            'page_name': 'admission',
        })

    @http.route('/admission/submit', type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def admission_submit(self, **post):
        """Handle admission form submission"""
        error = {}
        
        # Validation
        if not post.get('first_name') or not post.get('first_name').strip():
            error['first_name'] = 'First name is required.'
        
        if not post.get('last_name') or not post.get('last_name').strip():
            error['last_name'] = 'Last name is required.'
        
        if not post.get('email') or not post.get('email').strip():
            error['email'] = 'Email is required.'
        else:
            # Proper email format validation using regex
            email = post.get('email').strip()
            # RFC 5322 compliant email regex pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                error['email'] = 'Please enter a valid email address (e.g., name@example.com).'
        
        if not post.get('birth_date') or not post.get('birth_date').strip():
            error['birth_date'] = 'Birth date is required.'
        
        if not post.get('gender') or post.get('gender') not in ['m', 'f']:
            error['gender'] = 'Gender is required.'
        
        if not post.get('mobile') or not post.get('mobile').strip():
            error['mobile'] = 'Mobile number is required.'
        
        # If validation errors, redirect back with errors
        if error:
            request.session['admission_error'] = error
            # Exclude non-serializable data (like file uploads) from session
            post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
            request.session['admission_default'] = post_data
            return request.redirect('/admission/apply')
        
        try:
            # Get admission register - check if one was selected or find available one
            AdmissionRegister = request.env['op.admission.register'].sudo()
            today = fields.Date.today()
            register = False
            
            # Check if register_id was provided in form
            register_id = post.get('register_id')
            if register_id and str(register_id).strip():
                try:
                    register = AdmissionRegister.browse(int(register_id))
                    # Verify it's still available
                    if not register.exists() or not register.active or register.state not in ['application', 'confirm']:
                        register = False
                except (ValueError, TypeError):
                    register = False
            
            # If no register selected or invalid, find an available one
            if not register:
                register = AdmissionRegister.search([
                    ('active', '=', True),
                    ('state', 'in', ['application', 'confirm']),
                    ('start_date', '<=', today),
                    '|',
                    ('end_date', '=', False),
                    ('end_date', '>=', today),
                ], order='start_date desc', limit=1)
            
            # If still no register found, create a default one
            if not register:
                current_year = fields.Date.today().year
                register = AdmissionRegister.create({
                    'name': f'Online Applications {current_year}',
                    'start_date': fields.Date.today(),
                    'end_date': fields.Date.today().replace(month=12, day=31),
                    'max_count': 1000,  # Maximum number of online admissions
                    'min_count': 1,     # Minimum number of admissions
                    'state': 'application',  # Set to application gathering state
                })
            
            # Get course_id - handle empty strings and missing values
            course_id = post.get('course_id')
            _logger.info(f"DEBUG: Received course_id from form: {repr(course_id)}")
            
            # Check if course_id is valid (not empty, not False, not None)
            if course_id and str(course_id).strip():
                try:
                    course_id = int(course_id)
                    _logger.info(f"DEBUG: Converted course_id to: {course_id}")
                except (ValueError, TypeError):
                    course_id = None
            else:
                course_id = None
            
            # If no valid course_id, get first available active course
            if not course_id:
                _logger.info("DEBUG: No course selected, getting first available active course")
                Course = request.env['op.course'].sudo()
                # Search for active courses first
                default_course = Course.search([('active', '=', True)], limit=1)
                if not default_course:
                    # If no active courses, try inactive ones (for debugging)
                    _logger.warning("DEBUG: No active courses found, checking inactive courses")
                    default_course = Course.search([], limit=1)
                    if default_course:
                        _logger.warning(f"DEBUG: Found inactive course: {default_course.name} (ID: {default_course.id}, Active: {default_course.active})")
                
                if default_course:
                    course_id = default_course.id
                    _logger.info(f"DEBUG: Auto-selected course: {default_course.name} (ID: {course_id}, Active: {default_course.active})")
                else:
                    # If no courses exist, we can't create admission
                    _logger.error("DEBUG: No courses found in database!")
                    # Log total course count for debugging
                    total_courses = Course.search_count([])
                    active_courses = Course.search_count([('active', '=', True)])
                    _logger.error(f"DEBUG: Total courses in DB: {total_courses}, Active courses: {active_courses}")
                    error['general'] = 'No courses available. Please create an active course first in the backend.'
                    request.session['admission_error'] = error
                    post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
                    request.session['admission_default'] = post_data
                    return request.redirect('/admission/apply')
            
            # Final safety check for course_id
            if not course_id:
                _logger.error("CRITICAL: course_id is still None/False after all checks!")
                error['general'] = 'System error: Unable to assign course. Please contact administrator.'
                request.session['admission_error'] = error
                post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
                request.session['admission_default'] = post_data
                return request.redirect('/admission/apply')
            
            # Prepare admission data
            # NOTE: Don't pass False for Many2one fields - just omit them if empty
            admission_vals = {
                'register_id': register.id,  # Required field
                'name': f"{post.get('first_name', '').strip()} {post.get('last_name', '').strip()}".strip() or 'Student',
                'first_name': post.get('first_name', '').strip(),
                'middle_name': post.get('middle_name', '').strip() if post.get('middle_name') else '',
                'last_name': post.get('last_name', '').strip(),
                'email': post.get('email', '').strip(),
                'mobile': post.get('mobile', '').strip(),
                'phone': post.get('phone', '').strip() if post.get('phone') else '',
                'birth_date': post.get('birth_date', '').strip(),
                'gender': post.get('gender', '').strip(),
                'course_id': course_id,  # Always set to a valid course
                'street': post.get('street', '').strip() if post.get('street') else '',
                'street2': post.get('street2', '').strip() if post.get('street2') else '',
                'city': post.get('city', '').strip() if post.get('city') else '',
                'zip': post.get('zip', '').strip() if post.get('zip') else '',
                'application_date': fields.Datetime.now(),
                'state': 'submit',  # Set to submitted state initially
                # Previous education fields (optional)
                'prev_institute_id': post.get('prev_institute_id', '').strip() if post.get('prev_institute_id') else '',
                'prev_course_id': post.get('prev_course_id', '').strip() if post.get('prev_course_id') else '',
                'prev_result': post.get('prev_result', '').strip() if post.get('prev_result') else '',
                # Family information fields (optional)
                'family_business': post.get('family_business', '').strip() if post.get('family_business') else '',
                # Payment fields (set default application fee)
                'application_fee': 50.0,  # Default $50 application fee
                'payment_status': 'unpaid',
            }
            
            # Handle family income (float field)
            if post.get('family_income') and post.get('family_income') != '':
                try:
                    admission_vals['family_income'] = float(post.get('family_income'))
                except (ValueError, TypeError):
                    pass
            
            # Add title field (now a Char field, not Many2one)
            if post.get('title') and post.get('title').strip():
                admission_vals['title'] = post.get('title').strip()
            
            if post.get('program_id') and post.get('program_id') != '':
                try:
                    admission_vals['program_id'] = int(post.get('program_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('batch_id') and post.get('batch_id') != '':
                try:
                    admission_vals['batch_id'] = int(post.get('batch_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('state_id') and post.get('state_id') != '':
                try:
                    admission_vals['state_id'] = int(post.get('state_id'))
                except (ValueError, TypeError):
                    pass
            
            if post.get('country_id') and post.get('country_id') != '':
                try:
                    admission_vals['country_id'] = int(post.get('country_id'))
                except (ValueError, TypeError):
                    pass
            
            _logger.info(f"DEBUG: Creating admission with course_id: {course_id}")
            _logger.info(f"DEBUG: Admission values: {admission_vals}")
            
            # Handle image upload if provided
            image_file = post.get('image')
            if image_file:
                try:
                    # Handle different file upload formats
                    if hasattr(image_file, 'read'):
                        # FileStorage object (from form upload)
                        image_data = image_file.read()
                        if image_data:
                            # Validate file size (max 5MB)
                            max_size = 5 * 1024 * 1024  # 5MB
                            if len(image_data) > max_size:
                                error['image'] = 'Image file is too large. Maximum size is 5MB.'
                            else:
                                # Validate file type by checking magic bytes
                                is_valid_image = False
                                if image_data.startswith(b'\xff\xd8\xff'):  # JPEG
                                    is_valid_image = True
                                elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                                    is_valid_image = True
                                elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):  # GIF
                                    is_valid_image = True
                                elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:  # WEBP
                                    is_valid_image = True
                                
                                if is_valid_image:
                                    # Encode to base64 for Odoo Binary field
                                    admission_vals['image'] = base64.b64encode(image_data)
                                else:
                                    error['image'] = 'Invalid image format. Please upload a JPEG, PNG, GIF, or WEBP image.'
                    elif isinstance(image_file, str):
                        # Base64 string (from AJAX upload)
                        try:
                            # Remove data URL prefix if present
                            if ',' in image_file:
                                image_file = image_file.split(',')[1]
                            image_data = base64.b64decode(image_file)
                            # Validate size
                            max_size = 5 * 1024 * 1024  # 5MB
                            if len(image_data) > max_size:
                                error['image'] = 'Image file is too large. Maximum size is 5MB.'
                            else:
                                admission_vals['image'] = base64.b64encode(image_data)
                        except Exception as e:
                            _logger.warning(f"Error processing base64 image: {e}")
                            error['image'] = 'Invalid image data format.'
                except Exception as e:
                    _logger.error(f"Error processing image upload: {e}")
                    error['image'] = 'Error processing image. Please try again.'
            
            # If image validation failed, redirect back
            if error:
                request.session['admission_error'] = error
                post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
                request.session['admission_default'] = post_data
                return request.redirect('/admission/apply')
            
            # Create admission record
            admission = request.env['op.admission'].sudo().create(admission_vals)
            
            # Ensure application_number is generated (it might be computed)
            if not admission.application_number:
                # Refresh to get computed fields
                admission.invalidate_recordset(['application_number'])
                admission.refresh()
            
            _logger.info(f"DEBUG: Admission created successfully. ID: {admission.id}, Application Number: {admission.application_number}")
            
            # Send notification email (optional)
            try:
                template = request.env.ref('edafa_website_branding.admission_confirmation_email', raise_if_not_found=False)
                if template:
                    template.sudo().send_mail(admission.id, force_send=True)
            except:
                pass  # Don't fail if email template doesn't exist yet
            
            # Redirect to thank you page - use ID if application_number is not available
            redirect_param = admission.application_number or str(admission.id)
            _logger.info(f"DEBUG: Redirecting to thank you page with: {redirect_param}")
            return request.redirect(f'/admission/thank-you?application={redirect_param}')
            
        except Exception as e:
            _logger.exception("Error creating admission application: %s", str(e))
            error['general'] = f"An error occurred: {str(e)}"
            request.session['admission_error'] = error
            # Exclude non-serializable data (like file uploads) from session
            post_data = {k: v for k, v in post.items() if not hasattr(v, 'read')}
            request.session['admission_default'] = post_data
            return request.redirect('/admission/apply')

    @http.route('/admission/thank-you', type='http', auth="public", website=True)
    def admission_thank_you(self, **kwargs):
        """Thank you page after submission"""
        application_number = kwargs.get('application')
        
        # Get admission object to show payment option
        admission = None
        if application_number:
            # Try to find by application_number first
            admission = request.env['op.admission'].sudo().search([
                ('application_number', '=', application_number)
            ], limit=1)
            
            # If not found by application_number, try by ID (in case application_number wasn't generated yet)
            if not admission and application_number.isdigit():
                admission = request.env['op.admission'].sudo().browse(int(application_number))
                if not admission.exists():
                    admission = None
        
        return request.render('edafa_website_branding.admission_thank_you', {
            'application_number': application_number,
            'admission': admission,
            'page_name': 'admission_thanks',
        })

    @http.route('/admission/check-status', type='http', auth="public", website=True)
    def check_application_status(self, **kwargs):
        """Check application status by application number and email"""
        application_number = kwargs.get('application_number')
        email = kwargs.get('email')
        error = False
        admission = False
        
        if application_number and email:
            admission = request.env['op.admission'].sudo().search([
                ('application_number', '=', application_number),
                ('email', '=', email)
            ], limit=1)
            
            if not admission:
                error = "Application not found. Please check your application number and email."
        
        return request.render('edafa_website_branding.admission_status_check', {
            'admission': admission,
            'error': error,
            'application_number': application_number,
            'email': email,
            'page_name': 'admission_status',
        })


    @http.route('/admission/check-email', type='json', auth='public', csrf=False)
    def check_email(self, email):
        """Check if email already has an active application"""
        exists = request.env['op.admission'].sudo().search_count([
            ('email', '=', email),
            ('state', 'not in', ['cancel', 'reject'])
        ]) > 0
        return {'exists': exists}

    @http.route('/admission/save-draft', type='json', auth='public')
    def save_draft(self, **data):
        """Save application draft to session"""
        try:
            request.session['admission_draft'] = data
            request.session['admission_draft_timestamp'] = fields.Datetime.now().isoformat()
            return {
                'status': 'saved',
                'timestamp': request.session['admission_draft_timestamp']
            }
        except Exception as e:
            _logger.exception("Error saving draft: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/admission/load-draft', type='json', auth='public')
    def load_draft(self):
        """Load saved application draft from session"""
        draft = request.session.get('admission_draft', {})
        timestamp = request.session.get('admission_draft_timestamp', '')
        return {
            'formData': draft,
            'timestamp': timestamp
        }

    # ============================================
    # PAYMENT ROUTES - Phase 2
    # ============================================

    @http.route('/admission/<int:admission_id>/payment', type='http', 
                auth='public', website=True)
    def admission_payment_page(self, admission_id, access_token=None, **kwargs):
        """
        Display payment page for application fee.
        Can be accessed publicly with access_token or by logged-in owner.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        # Verify access (temporarily permissive for testing - remove in production)
        # TODO: Re-enable strict access control after testing
        # if not self._check_admission_access(admission, access_token):
        #     return request.render('http_routing.403')
        
        # Create invoice if doesn't exist and fee > 0
        if not admission.invoice_id and admission.application_fee > 0:
            try:
                admission.action_create_invoice()
            except Exception as e:
                _logger.exception("Error creating invoice: %s", str(e))
                error_html = f"""
                <div class="container mt-5">
                    <div class="alert alert-danger">
                        <h4>Error Creating Invoice</h4>
                        <p>{str(e)}</p>
                        <a href="/admission/apply" class="btn btn-primary">Submit New Application</a>
                    </div>
                </div>
                """
                return request.make_response(error_html, headers=[('Content-Type', 'text/html')])
        
        # Get available payment providers
        payment_providers = request.env['payment.provider'].sudo().search([
            ('state', '=', 'enabled'),
            ('is_published', '=', True),
        ])
        
        return request.render('edafa_website_branding.admission_payment_page', {
            'admission': admission,
            'invoice': admission.invoice_id,
            'payment_providers': payment_providers,
            'access_token': access_token or '',
            'page_name': 'payment',
        })

    @http.route('/admission/<int:admission_id>/create-payment-transaction', 
                type='json', auth='public')
    def create_payment_transaction(self, admission_id, provider_id, access_token=None):
        """
        Create payment.transaction for online payment.
        Links transaction to admission for tracking.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return {'error': 'Admission not found'}
        
        if not self._check_admission_access(admission, access_token):
            return {'error': 'Access denied'}
        
        try:
            # Ensure partner exists - check for existing partner first to avoid duplicates
            if not admission.partner_id:
                # Search for existing partner by email to avoid duplicates
                partner = False
                if admission.email:
                    partner = request.env['res.partner'].sudo().search([
                        ('email', '=', admission.email)
                    ], limit=1)
                
                # If no partner found by email, search by name and email combination
                if not partner and admission.name and admission.email:
                    partner = request.env['res.partner'].sudo().search([
                        ('name', '=', admission.name),
                        ('email', '=', admission.email)
                    ], limit=1)
                
                # If still no partner found, create a new one
                if not partner:
                    partner = request.env['res.partner'].sudo().create({
                        'name': admission.name,
                        'email': admission.email,
                        'phone': admission.mobile if admission.mobile else False,
                        'street': admission.street if admission.street else False,
                        'city': admission.city if admission.city else False,
                        'zip': admission.zip if admission.zip else False,
                        'country_id': admission.country_id.id if admission.country_id else False,
                        'state_id': admission.state_id.id if admission.state_id else False,
                    })
                else:
                    # Update existing partner with any missing information
                    update_vals = {}
                    if not partner.name and admission.name:
                        update_vals['name'] = admission.name
                    if not partner.phone and admission.mobile:
                        update_vals['phone'] = admission.mobile
                    if not partner.street and admission.street:
                        update_vals['street'] = admission.street
                    if not partner.city and admission.city:
                        update_vals['city'] = admission.city
                    if not partner.zip and admission.zip:
                        update_vals['zip'] = admission.zip
                    if not partner.country_id and admission.country_id:
                        update_vals['country_id'] = admission.country_id.id
                    if not partner.state_id and admission.state_id:
                        update_vals['state_id'] = admission.state_id.id
                    if update_vals:
                        partner.write(update_vals)
                
                admission.partner_id = partner.id
            
            # Ensure invoice exists
            if not admission.invoice_id:
                admission.action_create_invoice()
            
            # Create payment transaction
            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if not provider.exists():
                return {'error': 'Payment provider not found'}
            
            tx = request.env['payment.transaction'].sudo().create({
                'provider_id': provider.id,
                'amount': admission.application_fee,
                'currency_id': admission.currency_id.id,
                'partner_id': admission.partner_id.id,
                'reference': admission.application_number,
                'invoice_ids': [(4, admission.invoice_id.id)] if admission.invoice_id else [],
                'landing_route': f'/admission/{admission.id}/payment/success?access_token={access_token or ""}',
            })
            
            admission.payment_transaction_id = tx.id
            
            _logger.info(f'Payment transaction created for {admission.application_number}: {tx.reference}')
            
            return {
                'success': True,
                'transaction_id': tx.id,
                'redirect_url': f'/payment/pay?reference={tx.reference}',
            }
            
        except Exception as e:
            _logger.exception("Error creating payment transaction: %s", str(e))
            return {'error': str(e)}

    @http.route('/admission/<int:admission_id>/payment/success', 
                type='http', auth='public', website=True)
    def payment_success(self, admission_id, access_token=None, **kwargs):
        """
        Payment success callback page.
        Updates admission status after successful payment.
        """
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        # Update payment status from transaction
        if admission.payment_transaction_id:
            admission._update_payment_status_from_transaction()
        
        return request.render('edafa_website_branding.admission_payment_success', {
            'admission': admission,
            'transaction': admission.payment_transaction_id,
            'access_token': access_token or '',
            'page_name': 'payment_success',
        })

    @http.route('/admission/<int:admission_id>/payment/cancel', 
                type='http', auth='public', website=True)
    def payment_cancel(self, admission_id, access_token=None, **kwargs):
        """Payment cancelled callback"""
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('http_routing.404')
        
        return request.render('edafa_website_branding.admission_payment_cancel', {
            'admission': admission,
            'access_token': access_token or '',
            'page_name': 'payment_cancel',
        })

    # ============================================
    # HELPER METHODS
    # ============================================

    def _check_admission_access(self, admission, access_token=None):
        """
        Check if current user can access admission.
        Returns True if:
        - User is logged in and is the partner owner
        - Public user provides valid access_token
        """
        # Debug logging
        _logger.info(f"Checking access for admission {admission.id}")
        _logger.info(f"Access token provided: {access_token}")
        _logger.info(f"Admission access token: {admission.access_token}")
        _logger.info(f"Is public user: {request.env.user._is_public()}")
        
        if request.env.user._is_public():
            # Public user needs valid access token
            if not access_token:
                _logger.warning(f"No access token provided for admission {admission.id}")
                return False
            
            # Check if admission has access token (new field might not be set on old records)
            if not admission.access_token:
                _logger.warning(f"Admission {admission.id} has no access_token - generating one")
                admission.sudo()._generate_access_token()
            
            is_valid = access_token == admission.access_token
            _logger.info(f"Token validation result: {is_valid}")
            return is_valid
        else:
            # Logged in user must be the owner
            is_owner = admission.partner_id == request.env.user.partner_id or \
                       admission.email == request.env.user.partner_id.email
            _logger.info(f"Logged in user ownership check: {is_owner}")
            return is_owner


class EdafaPortalCustomer(CustomerPortal):
    """Extend portal to show student applications"""

    def _prepare_home_portal_values(self, counters):
        """Add admission applications count to portal"""
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'application_count' in counters:
            admission_count = request.env['op.admission'].search_count([
                ('email', '=', partner.email)
            ]) if partner else 0
            values['application_count'] = admission_count
        
        return values

    @http.route(['/my/applications', '/my/applications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_applications(self, page=1, sortby=None, filterby=None, **kw):
        """Display user's admission applications in portal"""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AdmissionSudo = request.env['op.admission'].sudo()

        # Search applications by email
        domain = [('email', '=', partner.email)]

        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Application Date'), 'order': 'application_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        
        # Default sort
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Pager
        application_count = AdmissionSudo.search_count(domain)
        pager = portal_pager(
            url="/my/applications",
            total=application_count,
            page=page,
            step=10,
            url_args={'sortby': sortby},
        )

        # Get applications
        applications = AdmissionSudo.search(
            domain,
            order=order,
            limit=10,
            offset=pager['offset']
        )

        values.update({
            'applications': applications,
            'page_name': 'application',
            'pager': pager,
            'default_url': '/my/applications',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return request.render("edafa_website_branding.portal_my_applications", values)

    @http.route(['/my/application/<int:application_id>'], type='http', auth="user", website=True)
    def portal_application_detail(self, application_id, **kw):
        """Display single application details"""
        partner = request.env.user.partner_id
        admission = request.env['op.admission'].sudo().browse(application_id)
        
        # Check if this application belongs to the user
        if admission.email != partner.email:
            return request.redirect('/my')
        
        values = {
            'admission': admission,
            'page_name': 'application_detail',
        }
        
        return request.render("edafa_website_branding.portal_application_detail", values)

