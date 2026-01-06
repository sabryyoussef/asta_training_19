##############################################################################
#
#    Edafa Inc
#    Copyright (C) 2009-TODAY Edafa Inc(<https://www.edafa.org>).
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
##############################################################################

from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpAdmission(models.Model):
    _name = "op.admission"
    _inherit = ['mail.thread']
    _rec_name = "application_number"
    _description = "Admission"
    _order = 'id DESC'

    name = fields.Char(
        'Name', required=True, translate=True)
    first_name = fields.Char(
        'First Name', required=True, translate=True)
    middle_name = fields.Char(
        'Middle Name', translate=True)
    last_name = fields.Char(
        'Last Name', required=True, translate=True)
    title = fields.Char(
        'Title')
    application_number = fields.Char(
        'Application Number', size=16, copy=False,
        readonly=True, store=True)
    admission_date = fields.Date(
        'Admission Date', copy=False)
    application_date = fields.Datetime(
        'Application Date', required=True, copy=False,
        default=lambda self: fields.Datetime.now())
    birth_date = fields.Date(
        'Birth Date', required=True)
    course_id = fields.Many2one(
        'op.course', 'Course', required=False)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', required=False)
    street = fields.Char(
        'Street', size=256)
    street2 = fields.Char(
        'Street2', size=256)
    phone = fields.Char(
        'Phone', size=16)
    mobile = fields.Char(
        'Mobile', size=16)
    email = fields.Char(
        'Email', size=256, required=True)
    city = fields.Char('City', size=64)
    zip = fields.Char('Zip', size=8)
    state_id = fields.Many2one(
        'res.country.state', 'States', domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one(
        'res.country', 'Country')
    fees = fields.Float('Fees')
    image = fields.Image('image')
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted'),
         ('confirm', 'Confirmed'), ('admission', 'Admission Confirm'),
         ('reject', 'Rejected'), ('pending', 'Pending'),
         ('cancel', 'Cancelled'), ('done', 'Done')],
        'State', default='draft', tracking=True)
    due_date = fields.Date('Due Date')
    prev_institute_id = fields.Char('Previous Institute')
    prev_course_id = fields.Char('Previous Course')
    prev_result = fields.Char(
        'Previous Result', size=256)
    family_business = fields.Char(
        'Family Business', size=256)
    family_income = fields.Float(
        'Family Income')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')],
        string='Gender',
        required=True)
    student_id = fields.Many2one(
        'op.student', 'Student')
    nbr = fields.Integer('No of Admission', readonly=True)
    register_id = fields.Many2one(
        'op.admission.register', 'Admission Register', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    is_student = fields.Boolean('Is Already Student')
    fees_term_id = fields.Many2one('op.fees.terms', 'Fees Term')
    active = fields.Boolean(default=True)
    discount = fields.Float(string='Discount (%)',
                            digits='Discount', default=0.0)

    fees_start_date = fields.Date('Fees Start Date')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    program_id = fields.Many2one('op.program', string="Program", tracking=True)
    course_ids = fields.Many2many('op.course', string='Courses',
                                  compute='_compute_course_ids')

    _sql_constraints = [
        ('unique_application_number',
         'unique(application_number)',
         'Application Number must be unique per Application!'),
    ]

    @api.depends('register_id')
    def _compute_course_ids(self):
        for data in self:
            if data.register_id:
                if data.register_id.admission_base == 'program':
                    course_list = []
                    for rec in data.register_id.admission_fees_line_ids:
                        course_list.append(rec.course_id.id) if rec.course_id.id not in course_list else None  # noqa
                    data.course_ids = [(6, 0, course_list)]
                else:
                    data.course_id = data.register_id.course_id.id
                    data.course_ids = [(6, 0, [data.register_id.course_id.id])]
            else:
                data.course_ids = [(6, 0, [])]

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.first_name) + " " + str(
                self.last_name
            )
        else:
            self.name = str(self.first_name) + " " + str(
                self.middle_name) + " " + str(self.last_name)

    @api.onchange('student_id', 'is_student')
    def onchange_student(self):
        _logger.info("DEBUG: onchange_student called - UPDATED VERSION with .browse()")
        if self.is_student and self.student_id:
            sd = self.student_id
            # Assign Many2one fields properly - never use False
            # Title is a Char field, not Many2one, and res.partner.title was removed in Odoo 19
            try:
                self.title = sd.title if sd.title else False
            except (KeyError, AttributeError):
                # Fallback if title doesn't exist on student
                self.title = False
            # Basic fields that should exist on student
            self.first_name = getattr(sd, 'first_name', False) or False
            self.middle_name = getattr(sd, 'middle_name', False) or False
            self.last_name = getattr(sd, 'last_name', False) or False
            self.birth_date = getattr(sd, 'birth_date', False) or False
            self.gender = getattr(sd, 'gender', False) or False
            
            # Image field - check both student and partner
            partner = sd.partner_id if sd.partner_id else False
            self.image = getattr(sd, 'image_1920', False) or (getattr(partner, 'image_1920', False) if partner else False) or False
            
            # Address and contact fields - check both student and partner (use getattr for safety)
            self.street = getattr(sd, 'street', False) or (getattr(partner, 'street', False) if partner else False) or False
            self.street2 = getattr(sd, 'street2', False) or (getattr(partner, 'street2', False) if partner else False) or False
            self.phone = getattr(sd, 'phone', False) or (getattr(partner, 'phone', False) if partner else False) or False
            # Mobile might not exist on res.partner, so use getattr safely
            self.mobile = getattr(sd, 'mobile', False) or (getattr(partner, 'mobile', False) if partner else False) or False
            self.email = getattr(sd, 'email', False) or (getattr(partner, 'email', False) if partner else False) or False
            self.zip = getattr(sd, 'zip', False) or (getattr(partner, 'zip', False) if partner else False) or False
            self.city = getattr(sd, 'city', False) or (getattr(partner, 'city', False) if partner else False) or False
            # Many2one fields - ensure we always assign a recordset, never False
            # Use safe assignment to avoid boolean False being assigned
            try:
                self.country_id = sd.country_id if (sd.country_id and sd.country_id.id) else self.env['res.country'].browse()
            except (AttributeError, TypeError):
                self.country_id = self.env['res.country'].browse()
            
            try:
                self.state_id = sd.state_id if (sd.state_id and sd.state_id.id) else self.env['res.country.state'].browse()
            except (AttributeError, TypeError):
                self.state_id = self.env['res.country.state'].browse()
            
            try:
                self.partner_id = sd.partner_id if (sd.partner_id and sd.partner_id.id) else self.env['res.partner'].browse()
            except (AttributeError, TypeError):
                self.partner_id = self.env['res.partner'].browse()
        else:
            # Clear all fields - use browse() for Many2one fields
            # Title is a Char field, not Many2one, and res.partner.title was removed in Odoo 19
            self.title = False
            self.birth_date = False
            self.gender = False
            self.image = False
            self.street = False
            self.street2 = False
            self.phone = False
            self.mobile = False
            self.zip = False
            self.city = False
            self.country_id = self.env['res.country'].browse()
            self.state_id = self.env['res.country.state'].browse()
            self.partner_id = self.env['res.partner'].browse()

    @api.onchange('register_id')
    def onchange_register(self):
        if not self.register_id:
            return
            
        if self.register_id.admission_base == 'course':
            if self.course_id and self.course_id.program_id:
                self.program_id = self.course_id.program_id
            if self.register_id.product_id:
                self.fees = self.register_id.product_id.lst_price
            if self.register_id.company_id:
                self.company_id = self.register_id.company_id
        else:
            if self.register_id.program_id:
                self.program_id = self.register_id.program_id
            else:
                self.program_id = self.env['op.program'].browse()

    @api.onchange('course_id')
    def onchange_course(self):
        # Always clear batch when course changes
        self.batch_id = self.env['op.batch'].browse()
        
        if not self.course_id:
            # If no course selected, clear related fields
            self.fees_term_id = self.env['op.fees.terms'].browse()
            self.program_id = self.env['op.program'].browse()
            return
        
        # Handle fees based on admission type
        if self.register_id and self.register_id.admission_base == 'program':
            for rec in self.register_id.admission_fees_line_ids:
                if rec.course_id and rec.course_id.id == self.course_id.id:
                    if rec.course_fees_product_id:
                        self.fees = rec.course_fees_product_id.lst_price
        
        # Set program_id from course
        if self.course_id.program_id:
            self.program_id = self.course_id.program_id
        else:
            self.program_id = self.env['op.program'].browse()
        
        # Set fees_term_id from course
        if self.course_id.fees_term_id:
            self.fees_term_id = self.course_id.fees_term_id
        else:
            self.fees_term_id = self.env['op.fees.terms'].browse()

    @api.constrains('register_id', 'application_date')
    def _check_admission_register(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.register_id.start_date)
            end_date = fields.Date.from_string(rec.register_id.end_date)
            application_date = fields.Date.from_string(rec.application_date)
            if application_date < start_date or application_date > end_date:
                raise ValidationError(_(
                    "Application Date should be between Start Date & End Date of Admission Register."))  # noqa

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))
            elif record and record.birth_date:
                today_date = fields.Date.today()
                day = (today_date - record.birth_date).days
                years = day // 365
                if years < self.register_id.minimum_age_criteria:
                    raise ValidationError(_(
                        "Not Eligible for Admission minimum "
                        "required age is :"
                        " %s " % self.register_id.minimum_age_criteria))

    @api.constrains('name')
    def create_sequence(self):
        if not self.application_number:
            self.application_number = self.env['ir.sequence'].next_by_code(
                'op.admission') or '/'

    def submit_form(self):
        self.state = 'submit'

    def admission_confirm(self):
        self.state = 'admission'

    def confirm_in_progress(self):
        for record in self:
            record.state = 'confirm'

    def get_student_vals(self):
        enable_create_student_user = self.env['ir.config_parameter'].get_param(
            'openeducat_admission.enable_create_student_user')
        for student in self:
            # Ensure partner exists before creating student to avoid duplicates
            # Check if admission already has a partner_id
            partner = student.partner_id
            if not partner:
                # Search for existing partner by email to avoid duplicates
                if student.email:
                    partner = self.env['res.partner'].sudo().search([
                        ('email', '=', student.email)
                    ], limit=1)
                
                # If no partner found by email, search by name and email combination
                if not partner and student.name and student.email:
                    partner = self.env['res.partner'].sudo().search([
                        ('name', '=', student.name),
                        ('email', '=', student.email)
                    ], limit=1)
                
                # If still no partner found, create a new one
                if not partner:
                    partner = self.env['res.partner'].sudo().create({
                        'name': student.name,
                        'email': student.email if student.email else False,
                        'phone': student.phone if student.phone else False,
                        'street': student.street if student.street else False,
                        'street2': student.street2 if student.street2 else False,
                        'city': student.city if student.city else False,
                        'zip': student.zip if student.zip else False,
                    })
                    # Add Many2one fields only if they exist
                    if student.country_id:
                        partner.country_id = student.country_id.id
                    if student.state_id:
                        partner.state_id = student.state_id.id
                    if student.image:
                        partner.image_1920 = student.image
                else:
                    # Update existing partner with any missing information
                    update_vals = {}
                    if not partner.name and student.name:
                        update_vals['name'] = student.name
                    if not partner.phone and student.phone:
                        update_vals['phone'] = student.phone
                    if not partner.street and student.street:
                        update_vals['street'] = student.street
                    if not partner.city and student.city:
                        update_vals['city'] = student.city
                    if not partner.zip and student.zip:
                        update_vals['zip'] = student.zip
                    if not partner.country_id and student.country_id:
                        update_vals['country_id'] = student.country_id.id
                    if not partner.state_id and student.state_id:
                        update_vals['state_id'] = student.state_id.id
                    if update_vals:
                        partner.write(update_vals)
                
                # Update admission with the partner
                student.partner_id = partner.id
            
            student_user = False
            if enable_create_student_user:
                # Check if user already exists for this partner or email to avoid duplicates
                existing_user = False
                if partner:
                    # First check if partner already has a user
                    existing_user = self.env['res.users'].sudo().search([
                        ('partner_id', '=', partner.id)
                    ], limit=1)
                
                if not existing_user and student.email:
                    # Check if user exists with this email/login
                    existing_user = self.env['res.users'].sudo().search([
                        ('login', '=', student.email)
                    ], limit=1)
                
                if existing_user:
                    # Use existing user instead of creating duplicate
                    student_user = existing_user
                    _logger.info(f"Using existing user for student {student.name}: {existing_user.login}")
                    
                    # Ensure the existing user has portal group if not already assigned
                    portal_group = self.env.ref('base.group_portal', raise_if_not_found=False)
                    if portal_group and student_user:
                        try:
                            current_users = portal_group.users
                            if student_user not in current_users:
                                # Ensure user is portal, not internal
                                portal_group.write({'users': [(4, student_user.id)]})
                                _logger.info(f"Assigned portal group to existing user {student_user.id}")
                        except Exception as e:
                            _logger.error(f"Could not assign portal group to existing user {student_user.id}: {e}")
                else:
                    # Create user first without groups_id (Odoo 19 compatibility)
                    portal_group = self.env.ref('base.group_portal', raise_if_not_found=False)
                    user_vals = {
                        'name': student.name,
                        'login': student.email if student.email else student.application_number,  # noqa
                        'image_1920': self.image or False,
                        'is_student': True,
                        'partner_id': partner.id,  # Use existing partner to avoid duplicates
                    }
                    if self.company_id:
                        user_vals['company_id'] = self.company_id.id
                    
                    student_user = self.env['res.users'].create(user_vals)
                    _logger.info(f"Created new user for student {student.name}: {student_user.login}")
                    
                    # Assign portal group after creation (Odoo 19 compatibility)
                    # Use group.users instead of user.groups_id (inverse relationship)
                    if portal_group and student_user:
                        try:
                            # In Odoo 19, groups_id is not writable on res.users
                            # Use group's users field (inverse relationship) with write() method
                            current_users = portal_group.users
                            if student_user not in current_users:
                                # Add user to group using Many2many command (4 = add to existing)
                                portal_group.write({'users': [(4, student_user.id)]})
                        except Exception as e:
                            _logger.error(f"Could not assign portal group to user {student_user.id}: {e}")
                            # Continue without group assignment - user can be assigned manually later
                            # This is not critical - the user can still be created and assigned groups manually
            # Prepare partner details (res.partner doesn't have 'mobile' field in standard Odoo)
            # Only include fields that exist on res.partner
            partner_details = {
                'name': student.name,
                'phone': student.phone if student.phone else False,
                'email': student.email if student.email else False,
                'street': student.street if student.street else False,
                'street2': student.street2 if student.street2 else False,
                'city': student.city if student.city else False,
                'zip': student.zip if student.zip else False,
            }
            # Add Many2one fields only if they exist
            if student.country_id:
                partner_details['country_id'] = student.country_id.id
            if student.state_id:
                partner_details['state_id'] = student.state_id.id
            if student.image:
                partner_details['image_1920'] = student.image
            
            # Write to partner if user was created
            if enable_create_student_user and student_user and student_user.partner_id:
                try:
                    student_user.partner_id.write(partner_details)
                except Exception as e:
                    _logger.warning(f"Could not update partner details: {e}")
            
            # Prepare student details
            # Note: op.student inherits from res.partner via _inherits, so contact info goes to partner
            # Mobile field doesn't exist on op.student or res.partner in standard Odoo 19
            details = {
                'name': student.name,
                'phone': student.phone if student.phone else False,
                'email': student.email if student.email else False,
                'street': student.street if student.street else False,
                'street2': student.street2 if student.street2 else False,
                'city': student.city if student.city else False,
                'zip': student.zip if student.zip else False,
            }
            # Add Many2one fields only if they exist
            if student.country_id:
                details['country_id'] = student.country_id.id
            if student.state_id:
                details['state_id'] = student.state_id.id
            if student.image:
                details['image_1920'] = student.image
            # Generate registration number (gr_no) if not already set
            # Use application number if available, otherwise generate from sequence
            gr_no = False
            if student.application_number and student.application_number != '/':
                # Use application number as registration number
                gr_no = student.application_number
            else:
                # Try to generate from sequence, or use a default format
                try:
                    # Try to get sequence for student registration
                    sequence = self.env['ir.sequence'].search([
                        ('code', '=', 'op.student.registration')
                    ], limit=1)
                    if sequence:
                        gr_no = sequence.next_by_id()
                    else:
                        # Fallback: generate based on year and ID
                        current_year = fields.Date.today().year
                        # Use a simple format: YEAR-XXXX
                        last_student = self.env['op.student'].search([
                            ('gr_no', 'like', f'{current_year}-%')
                        ], order='gr_no desc', limit=1)
                        if last_student and last_student.gr_no:
                            try:
                                last_num = int(last_student.gr_no.split('-')[-1])
                                gr_no = f'{current_year}-{str(last_num + 1).zfill(4)}'
                            except (ValueError, IndexError):
                                gr_no = f'{current_year}-0001'
                        else:
                            gr_no = f'{current_year}-0001'
                except Exception as e:
                    _logger.warning(f"Could not generate registration number: {e}")
                    # Use application number as fallback
                    gr_no = student.application_number or False
            
            details.update({
                # Note: op.student doesn't have a 'title' field, so we don't include it
                'partner_id': partner.id,  # Use existing partner to avoid duplicates
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'birth_date': student.birth_date,
                'gender': student.gender if student.gender else False,
                'image_1920': student.image or False,
                'gr_no': gr_no,  # Set registration number
                'course_detail_ids': [[0, False, {
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                    'academic_years_id':
                        student.register_id.academic_years_id.id or False,
                    'academic_term_id':
                        student.register_id.academic_term_id.id or False,
                    'fees_term_id': student.fees_term_id.id,
                    'fees_start_date': student.fees_start_date,
                    'product_id': student.register_id.product_id.id,
                }]],
                'user_id': student_user.id if student_user else False,
                'company_id': self.company_id.id
            })
            return details

    def enroll_student(self):
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))
            if not record.student_id:
                vals = record.get_student_vals()
                if vals:
                    record.student_id = student_id = self.env[
                        'op.student'].create(vals).id
                    record.partner_id = record.student_id.partner_id.id \
                        if record else False
                    
                    # Automatically create portal user access for the enrolled student
                    if record.student_id and not record.student_id.user_id:
                        record.student_id.create_student_user()

            else:
                student_id = record.student_id.id
                record.student_id.write({
                    'course_detail_ids': [[0, False, {
                        'course_id':
                            record.course_id and record.course_id.id or False,
                        'batch_id':
                            record.batch_id and record.batch_id.id or False,
                        'fees_term_id': record.fees_term_id.id,
                        'fees_start_date': record.fees_start_date,
                        'product_id': record.register_id.product_id.id,
                    }]],
                })
                
                # Also create portal user for existing student if not already created
                if record.student_id and not record.student_id.user_id:
                    record.student_id.create_student_user()
            if record.fees_term_id.fees_terms in ['fixed_days', 'fixed_date']:
                val = []
                product_id = record.register_id.product_id.id
                for line in record.fees_term_id.line_ids:
                    no_days = line.due_days
                    per_amount = line.value
                    amount = (per_amount * record.fees) / 100
                    dict_val = {
                        'fees_line_id': line.id,
                        'amount': amount,
                        'fees_factor': per_amount,
                        'product_id': product_id,
                        'discount': record.discount or record.fees_term_id.discount,
                        'state': 'draft',
                        'course_id': record.course_id and record.course_id.id or False,
                        'batch_id': record.batch_id and record.batch_id.id or False,
                    }
                    if line.due_date:
                        date = line.due_date
                        dict_val.update({
                            'date': date
                        })
                    elif self.fees_start_date:
                        date = self.fees_start_date + relativedelta(
                            days=no_days)
                        dict_val.update({
                            'date': date,
                        })
                    else:
                        date_now = (datetime.today() + relativedelta(
                            days=no_days)).date()
                        dict_val.update({
                            'date': date_now,
                        })
                    val.append([0, False, dict_val])
                record.student_id.write({
                    'fees_detail_ids': val
                })
            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
                'student_id': student_id,
                'is_student': True,
            })
            reg_id = self.env['op.subject.registration'].create({
                'student_id': student_id,
                'batch_id': record.batch_id.id,
                'course_id': record.course_id.id,
                'min_unit_load': record.course_id.min_unit_load or 0.0,
                'max_unit_load': record.course_id.max_unit_load or 0.0,
                'state': 'draft',
            })
            reg_id.get_subjects()

    def confirm_rejected(self):
        self.state = 'reject'

    def confirm_pending(self):
        self.state = 'pending'

    def confirm_to_draft(self):
        self.state = 'draft'

    def confirm_cancel(self):
        self.state = 'cancel'
        if self.is_student and self.student_id.fees_detail_ids:
            self.student_id.fees_detail_ids.state = 'cancel'

    def payment_process(self):
        self.state = 'fees_paid'

    def open_student(self):
        form_view = self.env.ref('openeducat_core.view_op_student_form')
        tree_view = self.env.ref('openeducat_core.view_op_student_tree')
        value = {
            'domain': str([('id', '=', self.student_id.id)]),
            'view_type': 'form',
            'view_mode': 'list, form',
            'res_model': 'op.student',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'list')],
            'type': 'ir.actions.act_window',
            'res_id': self.student_id.id,
            'target': 'current',
            'nodestroy': True
        }
        self.state = 'done'
        return value

    def create_invoice(self):
        """ Create invoice for fee payment process of student """

        # Check for existing partner to avoid duplicates
        partner_id = self.partner_id
        if not partner_id:
            # Search for existing partner by email
            if self.email:
                partner_id = self.env['res.partner'].search([
                    ('email', '=', self.email)
                ], limit=1)
            
            # If no partner found, create a new one
            if not partner_id:
                partner_id = self.env['res.partner'].create({'name': self.name})
            else:
                # Update partner name if needed
                if not partner_id.name or partner_id.name != self.name:
                    partner_id.write({'name': self.name})
                # Update admission with the partner
                self.partner_id = partner_id.id
        account_id = False
        product = self.register_id.product_id
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                   You may have to install a chart of account from Accounting \
                   app, settings menu.') % (product.name,))
        if self.fees <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        amount = self.fees
        name = product.name
        invoice = self.env['account.invoice'].create({
            'name': self.name,
            'origin': self.application_number,
            'move_type': 'out_invoice',
            'reference': False,
            'account_id': partner_id.property_account_receivable_id.id,
            'partner_id': partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': self.application_number,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.register_id.product_id.uom_id.id,
                'product_id': product.id,
            })],
        })
        invoice.compute_taxes()
        form_view = self.env.ref('account.invoice_form')
        tree_view = self.env.ref('account.invoice_tree')
        value = {
            'domain': str([('id', '=', invoice.id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'list')],
            'type': 'ir.actions.act_window',
            'res_id': invoice.id,
            'target': 'current',
            'nodestroy': True
        }
        self.partner_id = partner_id
        self.state = 'payment_process'
        return value

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Admission'),
            'template': '/openeducat_admission/static/xls/op_admission.xls'
        }]


class OpStudentCourseInherit(models.Model):
    _inherit = "op.student.course"

    product_id = fields.Many2one(
        'product.product', 'Course Fees',
        domain=[('type', '=', 'service')], tracking=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_create_student_user = fields.Boolean(
        config_parameter='openeducat_admission.enable_create_student_user',
        string='Create Student User')
