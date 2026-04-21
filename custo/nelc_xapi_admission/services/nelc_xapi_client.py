###############################################################################
#
#    NELC xAPI Admission Integration – HTTP client
#    Copyright (C) 2024 Edafa Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
###############################################################################
"""
nelc_xapi_client.py
===================
Backend-only service that builds and POSTs an xAPI statement to the NELC LRS.

Usage (from a controller or model method)::

    from odoo.addons.nelc_xapi_admission.services.nelc_xapi_client import (
        send_registered_statement,
    )
    result = send_registered_statement(env, admission_record)

The function returns a dict::

    {
        "success": True,
        "uuid": "<statement-uuid>",   # present on success
        "error": None,
    }
    # or on failure:
    {
        "success": False,
        "uuid": None,
        "error": "<short error message>",
    }

Configuration is read from ir.config_parameter (populated on module install
from environment variables – see data/nelc_config_init.xml and README.md).
"""

import datetime
import json
import logging
import re
import uuid as _uuid_mod

_logger = logging.getLogger(__name__)

_CONNECT_TIMEOUT = 10   # seconds
_READ_TIMEOUT = 30      # seconds

# --------------------------------------------------------------------------- #
#  HTML stripping utility                                                      #
# --------------------------------------------------------------------------- #

_HTML_TAG_RE = re.compile(r'<[^>]+>')
_WHITESPACE_RE = re.compile(r'\s+')


def _strip_html(text):
    """Remove HTML tags and collapse whitespace."""
    if not text:
        return ''
    text = _HTML_TAG_RE.sub(' ', text)
    text = _WHITESPACE_RE.sub(' ', text)
    return text.strip()


# --------------------------------------------------------------------------- #
#  Statement builder                                                           #
# --------------------------------------------------------------------------- #

def _build_registered_statement(env, admission):
    """
    Build an xAPI "registered" statement dict for the given admission record.

    :param env:       Odoo environment (for ir.config_parameter lookups)
    :param admission: op.admission record (must have x_nelc_national_id, email,
                      course_id populated)
    :returns:         dict suitable for JSON serialisation
    """
    ICP = env['ir.config_parameter'].sudo()
    platform_key = ICP.get_param('nelc.platform_key', 'odoo-platform')
    base_url = ICP.get_param('web.base.url', 'https://example.com').rstrip('/')

    national_id = (admission.x_nelc_national_id or '').strip()
    email = (admission.email or '').strip()

    # ------------------------------------------------------------------
    # Object ID: stable URL derived from the course
    # ------------------------------------------------------------------
    course = admission.course_id
    if course:
        course_slug = re.sub(r'[^a-zA-Z0-9_-]', '-', (course.name or str(course.id))).strip('-').lower()
        object_id = f"{base_url}/course/{course.id}-{course_slug}"
        course_name = course.name or ''
        course_desc = _strip_html(getattr(course, 'description', '') or '')
    else:
        object_id = f"{base_url}/admission/{admission.id}"
        course_name = ''
        course_desc = ''

    # ------------------------------------------------------------------
    # Timestamp (ISO 8601 UTC)
    # ------------------------------------------------------------------
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    # ------------------------------------------------------------------
    # Statement UUID (generated client-side for idempotency)
    # ------------------------------------------------------------------
    statement_uuid = str(_uuid_mod.uuid4())

    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': national_id,
            'mbox': f'mailto:{email}',
        },
        'verb': {
            'id': 'http://adlnet.gov/expapi/verbs/registered',
            'display': {'en-US': 'registered', 'ar-SA': 'سُجِّل'},
        },
        'object': {
            'objectType': 'Activity',
            'id': object_id,
            'definition': {
                'type': 'https://w3id.org/xapi/cmi5/activitytype/course',
                'name': {'ar-SA': course_name, 'en-US': course_name},
                'description': {'ar-SA': course_desc, 'en-US': course_desc},
            },
        },
        'context': {
            'platform': platform_key,
            'language': 'ar-SA',
            'extensions': {
                f'{base_url}/xapi/extensions/admission_id': admission.id,
            },
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


# --------------------------------------------------------------------------- #
#  HTTP sender                                                                 #
# --------------------------------------------------------------------------- #

def _post_statement(endpoint, auth_header, statement_dict):
    """
    POST a single xAPI statement to *endpoint*.

    Tries ``requests`` first; falls back to ``urllib`` if unavailable.
    Returns ``(success: bool, response_uuid: str|None, error_msg: str|None)``.
    """
    payload = json.dumps([statement_dict], ensure_ascii=False).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'X-Experience-API-Version': '1.0.3',
        'Authorization': auth_header,
    }

    try:
        import requests as _requests
        resp = _requests.post(
            endpoint,
            data=payload,
            headers=headers,
            timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT),
            verify=True,
        )
        resp.raise_for_status()
        # LRS returns a JSON array of statement UUIDs on success
        try:
            uuids = resp.json()
            response_uuid = uuids[0] if isinstance(uuids, list) and uuids else statement_dict.get('id')
        except Exception:
            response_uuid = statement_dict.get('id')
        return True, response_uuid, None

    except ImportError:
        # Fall back to urllib
        import urllib.request
        import urllib.error
        req = urllib.request.Request(endpoint, data=payload, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=_READ_TIMEOUT) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                try:
                    uuids = json.loads(body)
                    response_uuid = uuids[0] if isinstance(uuids, list) and uuids else statement_dict.get('id')
                except Exception:
                    response_uuid = statement_dict.get('id')
                return True, response_uuid, None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode('utf-8', errors='replace')[:300]
            return False, None, f'HTTP {exc.code}: {body}'
        except Exception as exc:
            return False, None, str(exc)[:300]

    except Exception as exc:
        return False, None, str(exc)[:300]


# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #

def send_registered_statement(env, admission):
    """
    Build and send the xAPI "registered" statement for *admission*.

    :param env:       Odoo environment
    :param admission: op.admission record
    :returns:         dict with keys ``success``, ``uuid``, ``error``
    """
    ICP = env['ir.config_parameter'].sudo()
    endpoint = ICP.get_param('nelc.lrs.endpoint', '').strip()
    auth_header = ICP.get_param('nelc.lrs.auth_header', '').strip()

    if not endpoint or not auth_header:
        msg = 'NELC LRS endpoint or auth header not configured (nelc.lrs.endpoint / nelc.lrs.auth_header)'
        _logger.warning('nelc_xapi: %s', msg)
        return {'success': False, 'uuid': None, 'error': msg}

    try:
        statement, stmt_uuid = _build_registered_statement(env, admission)
        _logger.info(
            'nelc_xapi: sending "registered" statement %s for admission %s',
            stmt_uuid, admission.id,
        )
        success, response_uuid, error_msg = _post_statement(endpoint, auth_header, statement)
        if success:
            _logger.info(
                'nelc_xapi: statement %s accepted by LRS (response uuid: %s)',
                stmt_uuid, response_uuid,
            )
            return {'success': True, 'uuid': response_uuid or stmt_uuid, 'error': None}
        else:
            _logger.error(
                'nelc_xapi: LRS rejected statement %s for admission %s – %s',
                stmt_uuid, admission.id, error_msg,
            )
            return {'success': False, 'uuid': None, 'error': error_msg}

    except Exception as exc:
        _logger.exception(
            'nelc_xapi: unexpected error building/sending statement for admission %s',
            admission.id,
        )
        return {'success': False, 'uuid': None, 'error': str(exc)[:300]}
