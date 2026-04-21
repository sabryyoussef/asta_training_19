import logging

from odoo import http
from odoo.http import request

from odoo.addons.edafa_website_branding.controllers.admission_portal import EdafaAdmissionPortal

_logger = logging.getLogger(__name__)


class NelcXapiConsolePortalIntegration(EdafaAdmissionPortal):
    """Attach NELC xAPI hooks via controller inheritance (no source patching required)."""

    def _compute_nelc_progress_scaled(self, admission):
        state_to_progress = {
            'draft': 0.0,
            'submit': 0.20,
            'pending': 0.35,
            'confirm': 0.50,
            'admission': 0.80,
            'done': 1.0,
        }
        progress_scaled = state_to_progress.get(admission.state, 0.0)
        if getattr(admission, 'payment_status', '') == 'paid':
            progress_scaled = max(progress_scaled, 0.60)
        return progress_scaled

    def _emit_nelc_initialized_non_blocking(self, admission):
        try:
            from odoo.addons.nelc_xapi_admission.services.nelc_xapi_client import send_initialized_statement

            send_initialized_statement(request.env, admission)
        except Exception:
            _logger.exception(
                "NELC xAPI Console: failed to send 'initialized' for admission %s",
                admission.id,
            )

    def _emit_nelc_progressed_non_blocking(self, admission):
        try:
            from odoo.addons.nelc_xapi_admission.services.nelc_xapi_client import send_progressed_statement

            progress_scaled = self._compute_nelc_progress_scaled(admission)
            send_progressed_statement(request.env, admission, progress_scaled)
        except Exception:
            _logger.exception(
                "NELC xAPI Console: failed to send 'progressed' for admission %s",
                admission.id,
            )

    def _find_admission_by_application_number(self, application_number):
        if not application_number:
            return request.env['op.admission'].sudo().browse([])

        admission = request.env['op.admission'].sudo().search([
            ('application_number', '=', application_number)
        ], limit=1)

        if not admission and str(application_number).isdigit():
            by_id = request.env['op.admission'].sudo().browse(int(application_number))
            if by_id.exists():
                admission = by_id

        return admission

    @http.route()
    def admission_thank_you(self, **kwargs):
        response = super().admission_thank_you(**kwargs)
        application_number = kwargs.get('application')
        admission = self._find_admission_by_application_number(application_number)
        if admission and getattr(admission, 'x_nelc_registered_sent', False):
            self._emit_nelc_initialized_non_blocking(admission)
            self._emit_nelc_progressed_non_blocking(admission)
        return response

    @http.route()
    def check_application_status(self, **kwargs):
        response = super().check_application_status(**kwargs)
        application_number = kwargs.get('application_number')
        email = kwargs.get('email')
        if application_number and email:
            admission = request.env['op.admission'].sudo().search([
                ('application_number', '=', application_number),
                ('email', '=', email),
            ], limit=1)
            if admission and getattr(admission, 'x_nelc_registered_sent', False):
                self._emit_nelc_progressed_non_blocking(admission)
        return response

    @http.route()
    def payment_success(self, admission_id, access_token=None, **kwargs):
        response = super().payment_success(admission_id, access_token=access_token, **kwargs)
        admission = request.env['op.admission'].sudo().browse(admission_id)
        if admission.exists() and getattr(admission, 'x_nelc_registered_sent', False):
            self._emit_nelc_initialized_non_blocking(admission)
            self._emit_nelc_progressed_non_blocking(admission)
        return response
