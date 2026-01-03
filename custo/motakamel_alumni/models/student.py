# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _


class OpStudent(models.Model):
    _inherit = 'op.student'

    is_alumni = fields.Boolean('Is Alumni', default=False, tracking=True)
    alumni_id = fields.Many2one('op.alumni', 'Alumni Record', readonly=True)
    
    def action_convert_to_alumni(self):
        """Convert student to alumni"""
        return {
            'name': _('Convert to Alumni'),
            'type': 'ir.actions.act_window',
            'res_model': 'convert.to.alumni.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_student_ids': [(6, 0, self.ids)],
            }
        }

