from odoo import api, fields, models


class NelcXapiManualTest(models.Model):
    _name = 'nelc.xapi.manual.test'
    _description = 'NELC xAPI Manual Test'
    _order = 'id desc'

    name = fields.Char(default='New', required=True, copy=False)

    admission_id = fields.Many2one('op.admission', string='Admission', required=True)
    event_type = fields.Selection(
        [
            ('registered', 'Registered'),
            ('initialized', 'Initialized'),
            ('progressed', 'Progressed'),
            ('attempted', 'Attempted'),
            ('rated', 'Rated'),
            ('earned', 'Earned'),
        ],
        required=True,
        default='registered',
    )

    progress_scaled = fields.Float()

    quiz_key = fields.Char()
    score_raw = fields.Float()
    score_min = fields.Float()
    score_max = fields.Float(default=100.0)

    rating_scaled = fields.Float()
    rating_response = fields.Text()

    certificate_id = fields.Char()
    certificate_url = fields.Char()
    certificate_name = fields.Char()

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='draft',
        required=True,
    )
    result_uuid = fields.Char(readonly=True)
    error_message = fields.Text(readonly=True)
    executed_at = fields.Datetime(readonly=True)

    event_log_id = fields.Many2one('nelc.xapi.event.log', string='Event Log', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('nelc.xapi.manual.test') or 'New'
        return super().create(vals_list)

    def action_send_test(self):
        from odoo.addons.nelc_xapi_admission.services.nelc_xapi_client import (
            send_attempted_statement,
            send_earned_statement,
            send_event_statement,
            send_progressed_statement,
            send_rated_statement,
        )

        for rec in self:
            result = {'success': False, 'uuid': None, 'error': 'Unknown error'}

            if rec.event_type in ('registered', 'initialized'):
                result = send_event_statement(self.env, rec.event_type, rec.admission_id)
            elif rec.event_type == 'progressed':
                result = send_progressed_statement(self.env, rec.admission_id, rec.progress_scaled)
            elif rec.event_type == 'attempted':
                result = send_attempted_statement(
                    self.env,
                    rec.admission_id,
                    quiz_key=rec.quiz_key or 'manual-quiz',
                    score_raw=rec.score_raw,
                    score_min=rec.score_min,
                    score_max=rec.score_max,
                )
            elif rec.event_type == 'rated':
                result = send_rated_statement(
                    self.env,
                    rec.admission_id,
                    score_scaled=rec.rating_scaled,
                    response=rec.rating_response or '',
                    score_raw=rec.rating_scaled * 5.0,
                    score_min=0,
                    score_max=5,
                )
            elif rec.event_type == 'earned':
                result = send_earned_statement(
                    self.env,
                    rec.admission_id,
                    certificate_id=rec.certificate_id or 'manual-certificate-id',
                    certificate_url=rec.certificate_url or 'https://example.com/certificate/manual',
                    certificate_name=rec.certificate_name or 'Manual Certificate',
                )

            status = 'success' if result.get('success') else 'failed'
            result_uuid = result.get('uuid') or False
            error_message = result.get('error') or False

            event_log = False
            if result_uuid:
                event_log = self.env['nelc.xapi.event.log'].sudo().search([
                    ('statement_uuid', '=', result_uuid),
                ], limit=1)
                if not event_log:
                    event_log = self.env['nelc.xapi.event.log'].sudo().search([
                        ('response_uuid', '=', result_uuid),
                    ], limit=1)

            rec.write({
                'status': status,
                'result_uuid': result_uuid,
                'error_message': error_message,
                'executed_at': fields.Datetime.now(),
                'event_log_id': event_log.id if event_log else False,
            })

        return True
