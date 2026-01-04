###############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
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

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpStudentCourse(models.Model):
    _name = "op.student.course"
    _description = "Student Course Details"
    _inherit = "mail.thread"
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', 'Student',
                                 ondelete="cascade", tracking=True)
    course_id = fields.Many2one('op.course', 'Course', required=True, tracking=True)
    batch_id = fields.Many2one('op.batch', 'Batch', tracking=True)
    roll_number = fields.Char('Roll Number', tracking=True)
    subject_ids = fields.Many2many('op.subject', string='Subjects')
    academic_years_id = fields.Many2one('op.academic.year', 'Academic Year')
    academic_term_id = fields.Many2one('op.academic.term', 'Terms')
    state = fields.Selection([('running', 'Running'),
                              ('finished', 'Finished')],
                             string="Status", default="running")

    _sql_constraints = [
        ('unique_name_roll_number_id',
         'unique(roll_number,course_id,batch_id,student_id)',
         'Roll Number & Student must be unique per Batch!'),
        ('unique_name_roll_number_course_id',
         'unique(roll_number,course_id,batch_id)',
         'Roll Number must be unique per Batch!'),
        ('unique_name_roll_number_student_id',
         'unique(student_id,course_id,batch_id)',
         'Student must be unique per Batch!'),
    ]

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Student Course Details'),
            'template': '/openeducat_core/static/xls/op_student_course.xls'
        }]


class OpStudent(models.Model):
    _name = "op.student"
    _description = "Student"
    _inherit = ['mail.thread']
    _inherits = {"res.partner": "partner_id"}

    first_name = fields.Char('First Name',  translate=True)
    middle_name = fields.Char('Middle Name', translate=True)
    last_name = fields.Char('Last Name', translate=True)
    birth_date = fields.Date('Birth Date')
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=True, default='m')
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    user_id = fields.Many2one('res.users', 'User', ondelete="cascade")
    gr_no = fields.Char("Registration Number", size=20)
    category_id = fields.Many2one('op.category', 'Category')
    course_detail_ids = fields.One2many('op.student.course', 'student_id',
                                        'Course Details',
                                        tracking=True)
    active = fields.Boolean(default=True)
    certificate_number = fields.Char(
        string='Certificate No.',
        readonly=True,
        copy=False,)

    _sql_constraints = [(
        'unique_gr_no',
        'unique(gr_no)',
        'Registration Number must be unique per student!'
    )]

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name_1(self):
        fname = self.first_name or ""
        mname = self.middle_name or ""
        lname = self.last_name or ""

        if fname or mname or lname:
            self.name = " ".join(filter(None, [fname, mname, lname]))
        else:
            self.name = "New"

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Students'),
            'template': '/openeducat_core/static/xls/op_student.xls'
        }]

    def create_student_user(self):
        """Create portal user for student with Odoo 19 compatibility"""
        portal_group = self.env.ref("base.group_portal", raise_if_not_found=False)
        users_res = self.env['res.users']
        
        for record in self:
            if not record.user_id and record.email:
                # Create user without groups_id (Odoo 19 compatibility)
                user_vals = {
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'login': record.email,
                    'is_student': True,
                    'tz': self._context.get('tz'),
                }
                
                try:
                    user_id = users_res.create(user_vals)
                    record.user_id = user_id
                    
                    # Assign portal group after user creation (Odoo 19 compatibility)
                    if portal_group and user_id:
                        try:
                            # Use group's users field (inverse relationship)
                            portal_group.write({'users': [(4, user_id.id)]})
                            _logger.info(f"Portal access created for student: {record.name} (ID: {record.id})")
                        except Exception as e:
                            _logger.error(f"Could not assign portal group to user {user_id.id}: {e}")
                            # Continue - user can be assigned groups manually later
                    
                    # Send password reset email to allow student to set their password
                    if user_id:
                        try:
                            user_id.action_reset_password()
                            _logger.info(f"Password reset email sent to: {record.email}")
                        except Exception as e:
                            _logger.warning(f"Could not send password reset email to {record.email}: {e}")
                            
                except Exception as e:
                    _logger.error(f"Could not create portal user for student {record.name}: {e}")
                    raise ValidationError(_(f"Could not create portal access for {record.name}. Error: {str(e)}"))
            elif not record.email:
                _logger.warning(f"Cannot create portal user for student {record.name} (ID: {record.id}): No email address")

