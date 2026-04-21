###############################################################################
#
#    NELC xAPI Admission Integration - event ledger
#    Copyright (C) 2024 Edafa Inc.
#
###############################################################################

from odoo import fields, models


class NelcXapiEventLog(models.Model):
    """Persistent ledger for xAPI event deduplication and audit."""

    _name = 'nelc.xapi.event.log'
    _description = 'NELC xAPI Event Log'
    _order = 'id desc'

    event_type = fields.Char(required=True, index=True)
    verb_iri = fields.Char(required=True)

    admission_id = fields.Many2one('op.admission', string='Admission', index=True, ondelete='set null')
    course_id = fields.Many2one('op.course', string='Course', index=True, ondelete='set null')

    learner_national_id = fields.Char(string='Learner National ID', index=True)
    learner_email = fields.Char(string='Learner Email', index=True)

    object_id = fields.Char(required=True, index=True)
    object_type = fields.Char(required=True)

    statement_uuid = fields.Char(required=True, index=True)
    response_uuid = fields.Char(index=True)
    dedup_key = fields.Char(required=True, index=True)
    sequence_index = fields.Integer(default=0, index=True)

    payload_json = fields.Text(required=True)

    status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('skipped_duplicate', 'Skipped Duplicate'),
        ],
        default='pending',
        required=True,
        index=True,
    )
    sent_at = fields.Datetime()
    error_message = fields.Text()

    _sql_constraints = [
        ('nelc_xapi_event_log_statement_uuid_uniq', 'unique(statement_uuid)', 'Statement UUID must be unique.'),
        ('nelc_xapi_event_log_dedup_key_uniq', 'unique(dedup_key)', 'Duplicate xAPI event is not allowed.'),
    ]
