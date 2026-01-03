# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class HomeworkGradeHistory(models.Model):
    _name = 'gr.homework.grade.history'
    _description = 'Homework Grade History'
    _order = 'change_date desc'
    _rec_name = 'display_name'

    # Basic Information
    homework_attempt_id = fields.Many2one(
        'gr.homework.attempt',
        string='Homework Attempt',
        required=True,
        ondelete='cascade',
        help='Homework attempt this grade change belongs to'
    )
    
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        related='homework_attempt_id.student_id',
        store=True,
        help='Student who submitted the homework'
    )
    
    homework_title = fields.Char(
        string='Homework Title',
        related='homework_attempt_id.homework_title',
        store=True,
        help='Title of the homework assignment'
    )
    
    # Grade Information
    old_grade = fields.Float(
        string='Previous Grade',
        required=True,
        help='Previous grade value'
    )
    
    new_grade = fields.Float(
        string='New Grade',
        required=True,
        help='New grade value'
    )
    
    grade_change = fields.Float(
        string='Grade Change',
        compute='_compute_grade_change',
        store=True,
        help='Difference between new and old grade'
    )
    
    grade_change_percentage = fields.Float(
        string='Change %',
        compute='_compute_grade_change_percentage',
        store=True,
        help='Percentage change in grade'
    )
    
    old_letter_grade = fields.Char(
        string='Previous Letter',
        compute='_compute_letter_grades',
        store=True,
        help='Previous letter grade'
    )
    
    new_letter_grade = fields.Char(
        string='New Letter',
        compute='_compute_letter_grades',
        store=True,
        help='New letter grade'
    )
    
    # Change Information
    change_date = fields.Datetime(
        string='Change Date',
        required=True,
        default=fields.Datetime.now,
        help='Date and time when the grade was changed'
    )
    
    changed_by_id = fields.Many2one(
        'res.users',
        string='Changed By',
        required=True,
        default=lambda self: self.env.user,
        help='User who made the grade change'
    )
    
    change_reason = fields.Char(
        string='Reason',
        help='Reason for the grade change'
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help='Display name for the grade history entry'
    )
    
    @api.depends('old_grade', 'new_grade')
    def _compute_grade_change(self):
        """Compute grade change amount."""
        for record in self:
            record.grade_change = record.new_grade - record.old_grade
    
    @api.depends('old_grade', 'new_grade', 'homework_attempt_id.max_grade')
    def _compute_grade_change_percentage(self):
        """Compute grade change percentage."""
        for record in self:
            if record.homework_attempt_id.max_grade > 0:
                old_percentage = (record.old_grade / record.homework_attempt_id.max_grade) * 100
                new_percentage = (record.new_grade / record.homework_attempt_id.max_grade) * 100
                record.grade_change_percentage = new_percentage - old_percentage
            else:
                record.grade_change_percentage = 0.0
    
    @api.depends('old_grade', 'new_grade', 'homework_attempt_id.max_grade')
    def _compute_letter_grades(self):
        """Compute letter grades for old and new grades."""
        for record in self:
            max_grade = record.homework_attempt_id.max_grade
            if max_grade > 0:
                # Calculate old letter grade
                old_percentage = (record.old_grade / max_grade) * 100
                record.old_letter_grade = record._get_letter_grade(old_percentage)
                
                # Calculate new letter grade
                new_percentage = (record.new_grade / max_grade) * 100
                record.new_letter_grade = record._get_letter_grade(new_percentage)
            else:
                record.old_letter_grade = 'N/A'
                record.new_letter_grade = 'N/A'
    
    def _get_letter_grade(self, percentage):
        """Get letter grade based on percentage."""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    @api.depends('homework_title', 'student_id', 'change_date')
    def _compute_display_name(self):
        """Compute display name for the grade history entry."""
        for record in self:
            if record.homework_title and record.student_id:
                record.display_name = f"{record.homework_title} - {record.student_id.name} ({record.change_date.strftime('%Y-%m-%d %H:%M')})"
            else:
                record.display_name = f"Grade History - {record.change_date.strftime('%Y-%m-%d %H:%M')}"
    
    def name_get(self):
        """Custom name display for grade history records."""
        result = []
        for record in self:
            name = f"{record.homework_title} - {record.student_id.name if record.student_id else 'Unknown'} ({record.change_date.strftime('%Y-%m-%d %H:%M')})"
            result.append((record.id, name))
        return result
