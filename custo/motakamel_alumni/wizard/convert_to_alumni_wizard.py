# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConvertToAlumniWizard(models.TransientModel):
    _name = 'convert.to.alumni.wizard'
    _description = 'Convert Student to Alumni Wizard'

    student_ids = fields.Many2many('op.student', string='Students', required=True)
    graduation_date = fields.Date('Graduation Date', required=True, default=fields.Date.today)
    grade = fields.Selection([
        ('distinction', 'Distinction'),
        ('first_class', 'First Class'),
        ('second_class', 'Second Class'),
        ('pass', 'Pass')
    ], 'Grade/Division')
    cgpa = fields.Float('CGPA', digits=(3, 2))
    percentage = fields.Float('Percentage', digits=(5, 2))
    create_portal_user = fields.Boolean('Create Portal User', default=True)
    
    def action_convert(self):
        """Convert selected students to alumni"""
        self.ensure_one()
        
        alumni_records = []
        for student in self.student_ids:
            # Check if already alumni
            if student.is_alumni:
                raise ValidationError(_('Student %s is already converted to alumni!') % student.name)
            
            # Create alumni record
            alumni_vals = {
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'mobile': student.mobile,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'image': student.image_1920,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'state_id': student.state_id.id,
                'country_id': student.country_id.id,
                'zip': student.zip,
                'course_id': student.course_detail_ids[0].course_id.id if student.course_detail_ids else False,
                'batch_id': student.course_detail_ids[0].batch_id.id if student.course_detail_ids else False,
                'admission_date': student.admission_date,
                'graduation_date': self.graduation_date,
                'grade': self.grade,
                'cgpa': self.cgpa,
                'percentage': self.percentage,
                'student_id': student.id,
                'state': 'active',
            }
            
            alumni = self.env['op.alumni'].create(alumni_vals)
            alumni_records.append(alumni.id)
            
            # Update student record
            student.write({
                'is_alumni': True,
                'alumni_id': alumni.id,
            })
            
            # Create portal user if requested
            if self.create_portal_user:
                try:
                    alumni.action_create_portal_user()
                except Exception as e:
                    # Log error but continue
                    pass
        
        # Return action to view created alumni
        return {
            'name': _('Alumni Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni',
            'view_mode': 'list,form',
            'domain': [('id', 'in', alumni_records)],
            'context': {'create': False},
        }

