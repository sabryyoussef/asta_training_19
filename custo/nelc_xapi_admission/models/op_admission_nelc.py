###############################################################################
#
#    NELC xAPI Admission Integration – op.admission extension
#    Copyright (C) 2024 Edafa Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
###############################################################################

from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)


class OpAdmissionNelc(models.Model):
    """
    Extends op.admission with NELC xAPI tracking fields.

    Fields added:
      x_nelc_national_id           – Student national ID sent as actor.name
      x_nelc_registered_sent       – True once the "registered" statement has
                                      been successfully delivered to the LRS
      x_nelc_registered_uuid       – UUID returned by the LRS on success
      x_nelc_registered_last_error – Last error message from a failed attempt
    """
    _inherit = 'op.admission'

    x_nelc_national_id = fields.Char(
        string='National ID (NELC)',
        size=10,
        copy=False,
        help="10-digit national identity number (starts with 1, 2, or 4). "
             "Used as actor.name in NELC xAPI statements.",
    )

    x_nelc_registered_sent = fields.Boolean(
        string='NELC Registered Sent',
        default=False,
        copy=False,
        help="True once the xAPI 'registered' statement was successfully sent "
             "to the NELC LRS for this admission record.",
    )

    x_nelc_registered_uuid = fields.Char(
        string='NELC Registered UUID',
        readonly=True,
        copy=False,
        help="Statement UUID returned by the NELC LRS after a successful send.",
    )

    x_nelc_registered_last_error = fields.Text(
        string='NELC Registered Last Error',
        readonly=True,
        copy=False,
        help="Concise error message from the most recent failed attempt to "
             "send the xAPI 'registered' statement.",
    )
