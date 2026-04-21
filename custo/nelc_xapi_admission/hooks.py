###############################################################################
#
#    NELC xAPI Admission Integration – post-install / post-upgrade hooks
#    Copyright (C) 2024 Edafa Inc.
#
###############################################################################
"""
hooks.py
========
Reads NELC-related environment variables and writes them into
ir.config_parameter so that the rest of the module can use
env['ir.config_parameter'].get_param(...) without needing direct OS access.

Mapping
-------
  NELC_LRS_ENDPOINT   → nelc.lrs.endpoint
  NELC_LRS_AUTH_HEADER → nelc.lrs.auth_header
  NELC_PLATFORM_KEY   → nelc.platform_key
  ODOO_BASE_URL        → web.base.url  (only if non-empty)
"""

import logging
import os

_logger = logging.getLogger(__name__)

_ENV_PARAM_MAP = {
    'NELC_LRS_ENDPOINT': 'nelc.lrs.endpoint',
    'NELC_LRS_AUTH_HEADER': 'nelc.lrs.auth_header',
    'NELC_PLATFORM_KEY': 'nelc.platform_key',
}


def post_init_hook(env):
    """Populate ir.config_parameter from environment variables."""
    ICP = env['ir.config_parameter'].sudo()

    for env_var, param_key in _ENV_PARAM_MAP.items():
        value = os.environ.get(env_var, '').strip()
        if value:
            ICP.set_param(param_key, value)
            _logger.info('nelc_xapi: set %s from env var %s', param_key, env_var)
        else:
            _logger.debug(
                'nelc_xapi: env var %s not set; leaving %s unchanged',
                env_var, param_key,
            )

    # web.base.url: only override if ODOO_BASE_URL is explicitly provided
    odoo_base_url = os.environ.get('ODOO_BASE_URL', '').strip()
    if odoo_base_url:
        ICP.set_param('web.base.url', odoo_base_url)
        _logger.info('nelc_xapi: set web.base.url from env var ODOO_BASE_URL')
