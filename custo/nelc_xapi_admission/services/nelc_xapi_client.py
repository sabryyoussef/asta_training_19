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
import hashlib
import uuid as _uuid_mod

from odoo import fields

_logger = logging.getLogger(__name__)

_CONNECT_TIMEOUT = 10   # seconds
_READ_TIMEOUT = 30      # seconds

# --------------------------------------------------------------------------- #
#  HTML stripping utility                                                      #
# --------------------------------------------------------------------------- #

_HTML_TAG_RE = re.compile(r'<[^>]+>')
_WHITESPACE_RE = re.compile(r'\s+')

_EVENT_VERB_MAP = {
    'registered': 'http://adlnet.gov/expapi/verbs/registered',
    'initialized': 'http://adlnet.gov/expapi/verbs/initialized',
    'progressed': 'http://adlnet.gov/expapi/verbs/progressed',
    'attempted': 'http://adlnet.gov/expapi/verbs/attempted',
    'rated': 'http://id.tincanapi.com/verb/rated',
    'earned': 'http://id.tincanapi.com/verb/earned',
}


def _strip_html(text):
    """Remove HTML tags and collapse whitespace."""
    if not text:
        return ''
    text = _HTML_TAG_RE.sub(' ', text)
    text = _WHITESPACE_RE.sub(' ', text)
    return text.strip()


def _utc_now_iso8601():
    """Return current UTC timestamp in xAPI format with ms precision."""
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def _parse_xapi_timestamp(timestamp_text):
    """Parse xAPI timestamp text; returns aware UTC datetime or None."""
    if not timestamp_text:
        return None
    try:
        return datetime.datetime.strptime(timestamp_text, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def _format_xapi_timestamp(dt_utc):
    """Format datetime into xAPI timestamp with ms precision."""
    if not dt_utc:
        return _utc_now_iso8601()
    if not dt_utc.tzinfo:
        dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
    dt_utc = dt_utc.astimezone(datetime.timezone.utc)
    return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def _build_course_activity_metadata(env, admission):
    """Build common actor/object/context fragments for course-level statements."""
    ICP = env['ir.config_parameter'].sudo()
    platform_key = ICP.get_param('nelc.platform_key', 'odoo-platform')
    base_url = ICP.get_param('web.base.url', 'https://example.com').rstrip('/')

    national_id = (admission.x_nelc_national_id or '').strip()
    email = (admission.email or '').strip()

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

    return {
        'platform_key': platform_key,
        'base_url': base_url,
        'national_id': national_id,
        'email': email,
        'object_id': object_id,
        'course_name': course_name,
        'course_desc': course_desc,
    }


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
    meta = _build_course_activity_metadata(env, admission)

    # ------------------------------------------------------------------
    # Timestamp (ISO 8601 UTC)
    # ------------------------------------------------------------------
    timestamp = _utc_now_iso8601()

    # ------------------------------------------------------------------
    # Statement UUID (generated client-side for idempotency)
    # ------------------------------------------------------------------
    statement_uuid = str(_uuid_mod.uuid4())

    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://adlnet.gov/expapi/verbs/registered',
            'display': {'en-US': 'registered', 'ar-SA': 'سُجِّل'},
        },
        'object': {
            'objectType': 'Activity',
            'id': meta['object_id'],
            'definition': {
                'type': 'https://w3id.org/xapi/cmi5/activitytype/course',
                'name': {'ar-SA': meta['course_name'], 'en-US': meta['course_name']},
                'description': {'ar-SA': meta['course_desc'], 'en-US': meta['course_desc']},
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
            'extensions': {
                f"{meta['base_url']}/xapi/extensions/admission_id": admission.id,
            },
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_initialized_statement(env, admission, event_data=None):
    """Build a course-level initialized statement for the given admission."""
    meta = _build_course_activity_metadata(env, admission)
    timestamp = _utc_now_iso8601()
    statement_uuid = str(_uuid_mod.uuid4())
    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://adlnet.gov/expapi/verbs/initialized',
            'display': {'en-US': 'initialized', 'ar-SA': 'بدأ'},
        },
        'object': {
            'objectType': 'Activity',
            'id': meta['object_id'],
            'definition': {
                'type': 'https://w3id.org/xapi/cmi5/activitytype/course',
                'name': {'ar-SA': meta['course_name'], 'en-US': meta['course_name']},
                'description': {'ar-SA': '', 'en-US': ''},
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_progressed_statement(env, admission, event_data=None):
    """Build a course-level progressed statement with scaled progress."""
    event_data = event_data or {}
    meta = _build_course_activity_metadata(env, admission)
    timestamp = _utc_now_iso8601()
    statement_uuid = str(_uuid_mod.uuid4())
    progress_scaled = event_data.get('progress_scaled', 0.0)
    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://adlnet.gov/expapi/verbs/progressed',
            'display': {'en-US': 'progressed', 'ar-SA': 'تقدم'},
        },
        'object': {
            'objectType': 'Activity',
            'id': meta['object_id'],
            'definition': {
                'type': 'https://w3id.org/xapi/cmi5/activitytype/course',
                'name': {'ar-SA': meta['course_name'], 'en-US': meta['course_name']},
                'description': {'ar-SA': '', 'en-US': ''},
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
        },
        'result': {
            'score': {
                'scaled': progress_scaled,
            },
            'completion': True,
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_attempted_statement(env, admission, event_data=None):
    """Build a unit-test attempted statement with incremental attempt-id."""
    event_data = event_data or {}
    meta = _build_course_activity_metadata(env, admission)
    timestamp = _utc_now_iso8601()
    statement_uuid = str(_uuid_mod.uuid4())

    quiz_key = str(event_data.get('quiz_key') or event_data.get('quiz_id') or '').strip() or 'unknown-quiz'
    object_id = str(event_data.get('object_id') or '').strip()
    if not object_id:
        object_id = f"{meta['object_id']}/quiz/{quiz_key}"

    score_raw = event_data.get('score_raw', 0)
    score_min = event_data.get('score_min')
    score_max = event_data.get('score_max')
    attempt_id = event_data.get('attempt_id')
    if attempt_id is None:
        attempt_id = _next_attempt_id(env, admission, object_id)

    success = event_data.get('success')
    try:
        raw_num = float(score_raw)
        min_num = float(score_min) if score_min is not None else None
    except Exception:
        raw_num = None
        min_num = None
    if success is None and raw_num is not None and min_num is not None:
        success = raw_num >= min_num

    result_score = {
        'raw': score_raw,
    }
    if score_min is not None:
        result_score['min'] = score_min
    if score_max is not None:
        result_score['max'] = score_max

    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://adlnet.gov/expapi/verbs/attempted',
            'display': {'en-US': 'attempted', 'ar-SA': 'حاول'},
        },
        'object': {
            'objectType': 'Activity',
            'id': object_id,
            'definition': {
                'type': 'http://id.tincanapi.com/activitytype/unit-test',
                'name': {
                    'ar-SA': str(event_data.get('object_name_ar') or event_data.get('object_name') or quiz_key),
                    'en-US': str(event_data.get('object_name') or quiz_key),
                },
                'description': {
                    'ar-SA': str(event_data.get('object_description_ar') or event_data.get('object_description') or ''),
                    'en-US': str(event_data.get('object_description') or ''),
                },
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
            'extensions': {
                'http://id.tincanapi.com/extension/attempt-id': int(attempt_id),
            },
        },
        'result': {
            'score': result_score,
            'success': bool(success) if success is not None else False,
            'completion': bool(event_data.get('completion', False)),
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_rated_statement(env, admission, event_data=None):
    """Build a course-level rated statement with textual response."""
    event_data = event_data or {}
    meta = _build_course_activity_metadata(env, admission)
    timestamp = _utc_now_iso8601()
    statement_uuid = str(_uuid_mod.uuid4())

    object_id = str(event_data.get('object_id') or meta['object_id']).strip()
    score_scaled = event_data.get('score_scaled', 0.0)
    score_raw = event_data.get('score_raw', 0)
    score_min = event_data.get('score_min', 0)
    score_max = event_data.get('score_max', 5)
    response_text = str(event_data.get('response') or '').strip()

    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://id.tincanapi.com/verb/rated',
            'display': {'en-US': 'rated', 'ar-SA': 'قيّم'},
        },
        'object': {
            'objectType': 'Activity',
            'id': object_id,
            'definition': {
                'type': 'https://w3id.org/xapi/cmi5/activitytype/course',
                'name': {'ar-SA': meta['course_name'], 'en-US': meta['course_name']},
                'description': {'ar-SA': '', 'en-US': ''},
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
        },
        'result': {
            'score': {
                'scaled': score_scaled,
                'raw': score_raw,
                'min': score_min,
                'max': score_max,
            },
            'response': response_text,
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_earned_statement(env, admission, event_data=None):
    """Build learner certificate earned statement with public certificate URL."""
    event_data = event_data or {}
    meta = _build_course_activity_metadata(env, admission)
    timestamp = _utc_now_iso8601()
    statement_uuid = str(_uuid_mod.uuid4())

    certificate_id = str(event_data.get('certificate_id') or '').strip()
    certificate_url = str(event_data.get('certificate_url') or '').strip()
    object_id = str(event_data.get('object_id') or '').strip()
    if not object_id:
        object_id = f"{meta['object_id']}/certificate/{certificate_id or 'unknown'}"

    statement = {
        'id': statement_uuid,
        'actor': {
            'objectType': 'Agent',
            'name': meta['national_id'],
            'mbox': f"mailto:{meta['email']}",
        },
        'verb': {
            'id': 'http://id.tincanapi.com/verb/earned',
            'display': {'en-US': 'earned', 'ar-SA': 'نال'},
        },
        'object': {
            'objectType': 'Activity',
            'id': object_id,
            'definition': {
                'type': 'https://www.opigno.org/en/tincan_registry/activity_type/certificate',
                'name': {
                    'ar-SA': str(event_data.get('certificate_name_ar') or event_data.get('certificate_name') or 'Certificate'),
                    'en-US': str(event_data.get('certificate_name') or 'Certificate'),
                },
            },
        },
        'context': {
            'platform': meta['platform_key'],
            'language': 'ar-SA',
            'extensions': {
                'http://id.tincanapi.com/extension/jws-certificate-location': certificate_url,
                'https://nelc.gov.sa/extensions/certificate_id': certificate_id,
            },
        },
        'timestamp': timestamp,
    }
    return statement, statement_uuid


def _build_statement(event_type, env, source_record, event_data=None):
    """Build xAPI statement for the requested event type."""
    if event_type == 'registered':
        return _build_registered_statement(env, source_record)
    if event_type == 'initialized':
        return _build_initialized_statement(env, source_record, event_data=event_data)
    if event_type == 'progressed':
        return _build_progressed_statement(env, source_record, event_data=event_data)
    if event_type == 'attempted':
        return _build_attempted_statement(env, source_record, event_data=event_data)
    if event_type == 'rated':
        return _build_rated_statement(env, source_record, event_data=event_data)
    if event_type == 'earned':
        return _build_earned_statement(env, source_record, event_data=event_data)
    raise NotImplementedError(f'Unsupported event type: {event_type}')


def _validate_statement(statement_dict, event_type):
    """Perform minimal structural validation before send."""
    required_keys = ('id', 'actor', 'verb', 'object', 'context', 'timestamp')
    missing_keys = [key for key in required_keys if key not in statement_dict]
    if missing_keys:
        return False, f'Missing required statement keys: {", ".join(missing_keys)}'

    verb_id = (statement_dict.get('verb') or {}).get('id', '')
    expected_verb = _EVENT_VERB_MAP.get(event_type, '')
    if expected_verb and verb_id != expected_verb:
        return False, f'Verb mismatch for event {event_type}: got {verb_id}'

    actor = statement_dict.get('actor') or {}
    if not (actor.get('name') or '').strip():
        return False, 'actor.name is required'

    object_id = ((statement_dict.get('object') or {}).get('id') or '').strip()
    if not object_id:
        return False, 'object.id is required'

    if event_type == 'progressed':
        score = (((statement_dict.get('result') or {}).get('score') or {}).get('scaled'))
        try:
            score = float(score)
        except Exception:
            return False, 'progressed result.score.scaled must be numeric'
        if score < 0.0 or score > 1.0:
            return False, 'progressed result.score.scaled must be between 0 and 1'

    if event_type == 'attempted':
        score = ((statement_dict.get('result') or {}).get('score') or {})
        if 'min' not in score:
            return False, 'attempted result.score.min is required'

        try:
            raw_score = float(score.get('raw'))
            min_score = float(score.get('min'))
        except Exception:
            return False, 'attempted score.raw and score.min must be numeric'

        success = bool((statement_dict.get('result') or {}).get('success'))
        if raw_score >= min_score and not success:
            return False, 'attempted result.success must be true when score.raw >= score.min'

        attempt_id = (((statement_dict.get('context') or {}).get('extensions') or {}).get(
            'http://id.tincanapi.com/extension/attempt-id'
        ))
        try:
            attempt_id = int(attempt_id)
        except Exception:
            return False, 'attempted context extension attempt-id must be an integer'
        if attempt_id < 1:
            return False, 'attempted context extension attempt-id must be >= 1'

    if event_type == 'rated':
        score = ((statement_dict.get('result') or {}).get('score') or {})
        try:
            scaled = float(score.get('scaled'))
        except Exception:
            return False, 'rated result.score.scaled must be numeric'
        if scaled < 0.0 or scaled > 1.0:
            return False, 'rated result.score.scaled must be between 0 and 1'
        response_text = str((statement_dict.get('result') or {}).get('response') or '').strip()
        if not response_text:
            return False, 'rated result.response is required'

    if event_type == 'earned':
        ext = ((statement_dict.get('context') or {}).get('extensions') or {})
        certificate_url = str(ext.get('http://id.tincanapi.com/extension/jws-certificate-location') or '').strip()
        certificate_id = str(ext.get('https://nelc.gov.sa/extensions/certificate_id') or '').strip()
        if not certificate_id:
            return False, 'earned certificate_id extension is required'
        if not certificate_url:
            return False, 'earned certificate URL extension is required'
        if certificate_url == certificate_id:
            return False, 'earned certificate_id and certificate_url must be distinct values'
        if not (certificate_url.startswith('http://') or certificate_url.startswith('https://')):
            return False, 'earned certificate URL must be publicly accessible http/https link'

    return True, None


def _build_dedup_key(event_type, statement_dict, source_record):
    """Build deterministic key used to prevent duplicate sends."""
    actor_name = (((statement_dict.get('actor') or {}).get('name')) or '').strip()
    object_id = (((statement_dict.get('object') or {}).get('id')) or '').strip()
    admission_id = getattr(source_record, 'id', '')
    course_id = getattr(getattr(source_record, 'course_id', None), 'id', '')
    progress_scaled = (((statement_dict.get('result') or {}).get('score') or {}).get('scaled'))
    attempt_id = (((statement_dict.get('context') or {}).get('extensions') or {}).get(
        'http://id.tincanapi.com/extension/attempt-id'
    ))
    key_material = '|'.join([
        str(event_type or ''),
        str(actor_name),
        str(object_id),
        str(admission_id),
        str(course_id),
        str(progress_scaled if progress_scaled is not None else ''),
        str(attempt_id if attempt_id is not None else ''),
    ])
    return hashlib.sha256(key_material.encode('utf-8')).hexdigest()


def _get_sent_event_log(env, source_record, event_type):
    """Get latest sent event log for source + event type."""
    return env['nelc.xapi.event.log'].sudo().search([
        ('admission_id', '=', source_record.id),
        ('event_type', '=', event_type),
        ('status', '=', 'sent'),
    ], limit=1, order='id desc')


def _extract_progress_scaled_from_payload(payload_json):
    """Extract result.score.scaled from stored payload, returns float or None."""
    try:
        payload = json.loads(payload_json or '{}')
    except Exception:
        return None

    scaled = (((payload.get('result') or {}).get('score') or {}).get('scaled'))
    try:
        return float(scaled)
    except Exception:
        return None


def _get_latest_sent_progress_log(env, source_record):
    """Get latest sent progressed event for this admission."""
    return env['nelc.xapi.event.log'].sudo().search([
        ('admission_id', '=', source_record.id),
        ('event_type', '=', 'progressed'),
        ('status', '=', 'sent'),
    ], limit=1, order='id desc')


def _extract_attempt_id_from_payload(payload_json):
    """Extract attempt-id extension from stored payload, returns int or None."""
    try:
        payload = json.loads(payload_json or '{}')
    except Exception:
        return None

    attempt_id = (((payload.get('context') or {}).get('extensions') or {}).get(
        'http://id.tincanapi.com/extension/attempt-id'
    ))
    try:
        return int(attempt_id)
    except Exception:
        return None


def _get_latest_sent_attempted_log(env, source_record, object_id):
    """Get latest sent attempted event for this admission and quiz object id."""
    return env['nelc.xapi.event.log'].sudo().search([
        ('admission_id', '=', source_record.id),
        ('event_type', '=', 'attempted'),
        ('object_id', '=', object_id),
        ('status', '=', 'sent'),
    ], limit=1, order='id desc')


def _next_attempt_id(env, source_record, object_id):
    """Return next sequential attempt id for a quiz object in an admission journey."""
    latest_attempt = _get_latest_sent_attempted_log(env, source_record, object_id)
    if not latest_attempt:
        return 1
    previous_attempt_id = _extract_attempt_id_from_payload(latest_attempt.payload_json)
    return int((previous_attempt_id or 0) + 1)


def _enforce_sequence_rules(env, event_type, source_record, statement_dict):
    """Ensure sequence requirements are enforced before send."""
    if event_type not in ('initialized', 'progressed', 'attempted', 'rated', 'earned'):
        return True, None

    registered_log = _get_sent_event_log(env, source_record, 'registered')
    if not registered_log:
        return False, 'registered statement must be sent before initialized/progressed events'

    if event_type == 'initialized':
        try:
            reg_payload = json.loads(registered_log.payload_json or '{}')
        except Exception:
            reg_payload = {}
        reg_ts = _parse_xapi_timestamp(reg_payload.get('timestamp'))
        init_ts = _parse_xapi_timestamp(statement_dict.get('timestamp'))
        if reg_ts and init_ts and reg_ts.replace(microsecond=0) == init_ts.replace(microsecond=0):
            statement_dict['timestamp'] = _format_xapi_timestamp(reg_ts + datetime.timedelta(seconds=1))

    if event_type == 'progressed':
        latest_progress_log = _get_latest_sent_progress_log(env, source_record)
        if latest_progress_log:
            previous_scaled = _extract_progress_scaled_from_payload(latest_progress_log.payload_json)
            current_scaled = (((statement_dict.get('result') or {}).get('score') or {}).get('scaled'))
            try:
                current_scaled = float(current_scaled)
            except Exception:
                current_scaled = None

            if previous_scaled is not None and current_scaled is not None and current_scaled <= previous_scaled:
                return (
                    False,
                    (
                        'progressed score must increase monotonically '
                        f'(previous={previous_scaled}, current={current_scaled})'
                    ),
                )

            try:
                previous_payload = json.loads(latest_progress_log.payload_json or '{}')
            except Exception:
                previous_payload = {}
            previous_ts = _parse_xapi_timestamp(previous_payload.get('timestamp'))
            current_ts = _parse_xapi_timestamp(statement_dict.get('timestamp'))
            if previous_ts and current_ts and current_ts <= previous_ts:
                statement_dict['timestamp'] = _format_xapi_timestamp(previous_ts + datetime.timedelta(seconds=1))

    if event_type == 'attempted':
        object_id = ((statement_dict.get('object') or {}).get('id') or '').strip()
        previous_attempt = _get_latest_sent_attempted_log(env, source_record, object_id)
        current_attempt_id = _extract_attempt_id_from_payload(json.dumps(statement_dict, ensure_ascii=False))
        if current_attempt_id is None:
            return False, 'attempted event must include valid attempt-id extension'

        if previous_attempt:
            previous_attempt_id = _extract_attempt_id_from_payload(previous_attempt.payload_json)
            expected_next = int((previous_attempt_id or 0) + 1)
            if current_attempt_id != expected_next:
                return (
                    False,
                    (
                        'attempt-id must increment sequentially by 1 '
                        f'(previous={previous_attempt_id}, current={current_attempt_id})'
                    ),
                )

    return True, None


def _get_lrs_config(env):
    """Read LRS endpoint and auth header from config params."""
    ICP = env['ir.config_parameter'].sudo()
    endpoint = ICP.get_param('nelc.lrs.endpoint', '').strip()
    auth_header = ICP.get_param('nelc.lrs.auth_header', '').strip()
    return endpoint, auth_header


def _create_event_log(env, event_type, source_record, statement_dict, dedup_key, sequence_index=0):
    """Create a pending ledger record for this xAPI event."""
    admission = source_record
    course = getattr(source_record, 'course_id', None)
    actor = statement_dict.get('actor') or {}
    event_log_vals = {
        'event_type': event_type,
        'verb_iri': ((statement_dict.get('verb') or {}).get('id') or '').strip(),
        'admission_id': getattr(admission, 'id', False),
        'course_id': getattr(course, 'id', False),
        'learner_national_id': (actor.get('name') or '').strip(),
        'learner_email': ((actor.get('mbox') or '').replace('mailto:', '').strip()),
        'object_id': ((statement_dict.get('object') or {}).get('id') or '').strip(),
        'object_type': ((statement_dict.get('object') or {}).get('objectType') or '').strip(),
        'statement_uuid': (statement_dict.get('id') or '').strip(),
        'dedup_key': dedup_key,
        'sequence_index': int(sequence_index or 0),
        'payload_json': json.dumps(statement_dict, ensure_ascii=False),
        'status': 'pending',
    }
    return env['nelc.xapi.event.log'].sudo().create(event_log_vals)


def _next_sequence_index(env, source_record):
    """Return next sequence index for events linked to this admission."""
    last_event = env['nelc.xapi.event.log'].sudo().search([
        ('admission_id', '=', source_record.id),
    ], limit=1, order='sequence_index desc, id desc')
    return int((last_event.sequence_index or 0) + 1) if last_event else 1


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


def send_event_statement(env, event_type, source_record, event_data=None):
    """Generic event sender with dedup + audit log persistence."""
    endpoint, auth_header = _get_lrs_config(env)
    if not endpoint or not auth_header:
        msg = 'NELC LRS endpoint or auth header not configured (nelc.lrs.endpoint / nelc.lrs.auth_header)'
        _logger.warning('nelc_xapi: %s', msg)
        return {'success': False, 'uuid': None, 'error': msg}

    try:
        statement, stmt_uuid = _build_statement(event_type, env, source_record, event_data=event_data)

        sequence_ok, sequence_error = _enforce_sequence_rules(env, event_type, source_record, statement)
        if not sequence_ok:
            _logger.warning('nelc_xapi: sequence violation for %s on source %s - %s', event_type, source_record.id, sequence_error)
            return {'success': False, 'uuid': None, 'error': sequence_error}

        is_valid, validation_error = _validate_statement(statement, event_type)
        if not is_valid:
            _logger.error('nelc_xapi: invalid %s statement for source %s - %s', event_type, source_record.id, validation_error)
            return {'success': False, 'uuid': None, 'error': validation_error}

        dedup_key = _build_dedup_key(event_type, statement, source_record)
        existing = env['nelc.xapi.event.log'].sudo().search([('dedup_key', '=', dedup_key)], limit=1)
        if existing:
            if existing.status in ('pending', 'sent', 'skipped_duplicate'):
                _logger.info(
                    'nelc_xapi: duplicate %s statement skipped for source %s (dedup=%s)',
                    event_type, source_record.id, dedup_key,
                )
                if existing.status != 'skipped_duplicate':
                    existing.write({'status': 'skipped_duplicate'})
                return {
                    'success': True,
                    'uuid': existing.response_uuid or existing.statement_uuid,
                    'error': None,
                    'skipped_duplicate': True,
                }

        event_log = _create_event_log(
            env,
            event_type,
            source_record,
            statement,
            dedup_key,
            sequence_index=_next_sequence_index(env, source_record),
        )
        _logger.info(
            'nelc_xapi: sending "%s" statement %s for source %s',
            event_type, stmt_uuid, source_record.id,
        )

        success, response_uuid, error_msg = _post_statement(endpoint, auth_header, statement)
        if success:
            event_log.write({
                'status': 'sent',
                'response_uuid': (response_uuid or stmt_uuid),
                'sent_at': fields.Datetime.now(),
                'error_message': False,
            })
            _logger.info(
                'nelc_xapi: statement %s accepted by LRS (response uuid: %s)',
                stmt_uuid, response_uuid,
            )
            return {'success': True, 'uuid': response_uuid or stmt_uuid, 'error': None}

        event_log.write({
            'status': 'failed',
            'response_uuid': False,
            'error_message': error_msg,
        })
        _logger.error(
            'nelc_xapi: LRS rejected statement %s for source %s - %s',
            stmt_uuid, source_record.id, error_msg,
        )
        return {'success': False, 'uuid': None, 'error': error_msg}

    except NotImplementedError as exc:
        _logger.warning('nelc_xapi: %s', str(exc))
        return {'success': False, 'uuid': None, 'error': str(exc)}
    except Exception as exc:
        _logger.exception(
            'nelc_xapi: unexpected error building/sending %s statement for source %s',
            event_type, source_record.id,
        )
        return {'success': False, 'uuid': None, 'error': str(exc)[:300]}


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
    return send_event_statement(env, 'registered', admission)


def send_initialized_statement(env, admission):
    """Build and send the xAPI initialized statement for *admission*."""
    return send_event_statement(env, 'initialized', admission)


def send_progressed_statement(env, admission, progress_scaled):
    """Build and send the xAPI progressed statement for *admission*."""
    return send_event_statement(env, 'progressed', admission, event_data={'progress_scaled': progress_scaled})


def send_attempted_statement(
    env,
    admission,
    quiz_key,
    score_raw,
    score_min,
    score_max=None,
    success=None,
    completion=False,
    object_id=None,
    object_name=None,
    object_description=None,
):
    """Build and send the xAPI attempted statement for a quiz attempt."""
    event_data = {
        'quiz_key': quiz_key,
        'score_raw': score_raw,
        'score_min': score_min,
        'score_max': score_max,
        'success': success,
        'completion': completion,
        'object_id': object_id,
        'object_name': object_name,
        'object_description': object_description,
    }
    return send_event_statement(env, 'attempted', admission, event_data=event_data)


def send_rated_statement(
    env,
    admission,
    score_scaled,
    response,
    score_raw=0,
    score_min=0,
    score_max=5,
    object_id=None,
):
    """Build and send the xAPI rated statement for a course/content rating."""
    event_data = {
        'score_scaled': score_scaled,
        'score_raw': score_raw,
        'score_min': score_min,
        'score_max': score_max,
        'response': response,
        'object_id': object_id,
    }
    return send_event_statement(env, 'rated', admission, event_data=event_data)


def send_earned_statement(
    env,
    admission,
    certificate_id,
    certificate_url,
    certificate_name,
    object_id=None,
):
    """Build and send the xAPI earned statement for learner certificate issuance."""
    event_data = {
        'certificate_id': certificate_id,
        'certificate_url': certificate_url,
        'certificate_name': certificate_name,
        'object_id': object_id,
    }
    return send_event_statement(env, 'earned', admission, event_data=event_data)
