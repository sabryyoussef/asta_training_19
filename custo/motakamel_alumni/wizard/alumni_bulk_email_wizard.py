# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<https://www.openeducat.org>).
#
##############################################################################

from odoo import models, fields, api, _


class AlumniBulkEmailWizard(models.TransientModel):
    _name = 'alumni.bulk.email.wizard'
    _description = 'Alumni Bulk Email Wizard'

    alumni_ids = fields.Many2many('op.alumni', string='Alumni', required=True)
    subject = fields.Char('Subject', required=True)
    body = fields.Html('Message', required=True)
    
    def action_send_email(self):
        """Send bulk email to selected alumni"""
        self.ensure_one()
        
        mail_template = self.env['mail.template'].create({
            'name': 'Alumni Bulk Email',
            'model_id': self.env['ir.model']._get('op.alumni').id,
            'subject': self.subject,
            'body_html': self.body,
            'email_from': self.env.user.email or self.env.company.email,
        })
        
        for alumni in self.alumni_ids:
            if alumni.email:
                mail_template.send_mail(alumni.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Emails sent successfully to %s alumni') % len(self.alumni_ids),
                'type': 'success',
                'sticky': False,
            }
        }

