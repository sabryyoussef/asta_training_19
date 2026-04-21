from odoo import api, fields, models


class NelcXapiConsoleSettings(models.Model):
    _name = 'nelc.xapi.console.settings'
    _description = 'NELC xAPI Console Settings'
    _order = 'id desc'

    name = fields.Char(default='Default NELC Settings', required=True)

    lrs_endpoint = fields.Char(string='LRS Endpoint', required=False)
    lrs_auth_header = fields.Char(string='LRS Authorization Header', required=False)
    platform_key = fields.Char(string='Platform Key', required=False)
    odoo_base_url = fields.Char(string='Odoo Base URL', required=False)
    platform_name_ar = fields.Char(string='Platform Name (ar-SA)')
    platform_name_en = fields.Char(string='Platform Name (en-US)')

    last_synced_at = fields.Datetime(readonly=True)
    last_applied_at = fields.Datetime(readonly=True)

    @api.model
    def action_open_singleton(self):
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({'name': 'Default NELC Settings'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'NELC xAPI Settings',
            'res_model': 'nelc.xapi.console.settings',
            'view_mode': 'form',
            'res_id': settings.id,
            'target': 'current',
        }

    def action_sync_from_parameters(self):
        icp = self.env['ir.config_parameter'].sudo()
        now = fields.Datetime.now()
        for rec in self:
            rec.write({
                'lrs_endpoint': icp.get_param('nelc.lrs.endpoint', ''),
                'lrs_auth_header': icp.get_param('nelc.lrs.auth_header', ''),
                'platform_key': icp.get_param('nelc.platform_key', ''),
                'odoo_base_url': icp.get_param('web.base.url', ''),
                'platform_name_ar': icp.get_param('nelc.platform.name.ar', ''),
                'platform_name_en': icp.get_param('nelc.platform.name.en', ''),
                'last_synced_at': now,
            })
        return True

    def action_apply_to_parameters(self):
        icp = self.env['ir.config_parameter'].sudo()
        now = fields.Datetime.now()
        for rec in self:
            icp.set_param('nelc.lrs.endpoint', rec.lrs_endpoint or '')
            icp.set_param('nelc.lrs.auth_header', rec.lrs_auth_header or '')
            icp.set_param('nelc.platform_key', rec.platform_key or '')
            if rec.odoo_base_url:
                icp.set_param('web.base.url', rec.odoo_base_url)
            icp.set_param('nelc.platform.name.ar', rec.platform_name_ar or '')
            icp.set_param('nelc.platform.name.en', rec.platform_name_en or '')
            rec.last_applied_at = now
        return True
