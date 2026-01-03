# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GrantStudentMapping(models.Model):
    _inherit = 'gr.student'
    
    openeducat_student_id = fields.Many2one(
        'op.student',
        string='Linked OpenEduCat Student',
        help='Optional link to corresponding OpenEduCat student record'
    )
    
    is_mapped_to_openeducat = fields.Boolean(
        compute='_compute_is_mapped',
        string='Mapped to OpenEduCat',
        store=True
    )
    
    @api.depends('openeducat_student_id')
    def _compute_is_mapped(self):
        for record in self:
            record.is_mapped_to_openeducat = bool(record.openeducat_student_id)


class OpenEducatStudentMapping(models.Model):
    _inherit = 'op.student'
    
    grant_training_student_id = fields.Many2one(
        'gr.student',
        string='Linked Grant Training Student',
        help='Optional link to corresponding grant training student record'
    )
    
    is_mapped_to_grants = fields.Boolean(
        compute='_compute_is_mapped',
        string='Mapped to Grant Training',
        store=True
    )
    
    @api.depends('grant_training_student_id')
    def _compute_is_mapped(self):
        for record in self:
            record.is_mapped_to_grants = bool(record.grant_training_student_id)
