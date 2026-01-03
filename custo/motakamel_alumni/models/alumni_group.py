# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _


class OpAlumniGroup(models.Model):
    _name = 'op.alumni.group'
    _description = 'Alumni Group'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char('Group Name', required=True, tracking=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    
    # Group Type
    group_type = fields.Selection([
        ('batch', 'Batch/Year'),
        ('course', 'Course'),
        ('department', 'Department'),
        ('interest', 'Interest Based'),
        ('location', 'Location Based'),
        ('professional', 'Professional Network'),
        ('other', 'Other')
    ], 'Group Type', required=True, default='batch', tracking=True)
    
    # Academic Reference
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one('op.batch', 'Batch')
    graduation_year = fields.Char('Graduation Year')
    
    # Members
    alumni_ids = fields.Many2many(
        'op.alumni', 
        'alumni_group_rel', 
        'group_id', 
        'alumni_id', 
        'Members'
    )
    member_count = fields.Integer('Total Members', compute='_compute_member_count', store=True)
    
    # Group Admin
    admin_ids = fields.Many2many(
        'op.alumni', 
        'alumni_group_admin_rel', 
        'group_id', 
        'alumni_id', 
        'Group Admins'
    )
    
    # Contact Info
    email = fields.Char('Group Email')
    website = fields.Char('Website')
    
    # Status
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Group Code must be unique!'),
    ]
    
    @api.depends('alumni_ids')
    def _compute_member_count(self):
        for group in self:
            group.member_count = len(group.alumni_ids)
    
    def action_view_members(self):
        """View group members"""
        self.ensure_one()
        return {
            'name': _('Group Members'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.alumni',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.alumni_ids.ids)],
        }

