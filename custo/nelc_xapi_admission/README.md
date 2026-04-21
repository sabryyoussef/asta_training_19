# NELC xAPI Admission Module

## Overview

This Odoo 19 add-on sends an xAPI **"registered"** statement to the
**NELC Learning Record Store (LRS)** immediately after a student's admission
record is created via the portal wizard.

### What it does

| Step | Action |
|------|--------|
| Student fills admission wizard Step 1 | Enters a **National ID** (10 digits, starts with 1/2/4) |
| Student submits the wizard | `op.admission` record is created |
| Backend trigger | `send_registered_statement()` is called |
| On success | `x_nelc_registered_sent = True`, UUID stored in `x_nelc_registered_uuid` |
| On failure | Error stored in `x_nelc_registered_last_error`; student flow is **not** blocked |

---

## Configuration on Odoo.sh

Set the following **environment variables** in the Odoo.sh project settings
(Project → Settings → Environment Variables):

| Variable | Description |
|----------|-------------|
| `NELC_LRS_ENDPOINT` | Full HTTPS URL of the NELC LRS statements endpoint |
| `NELC_LRS_AUTH_HEADER` | Complete `Authorization` header value, e.g. `Basic base64...` or `Bearer token` |
| `NELC_PLATFORM_KEY` | Platform key assigned by NELC (e.g. `MGMT-003`) |
| `ODOO_BASE_URL` | Public base URL for this Odoo instance (optional; e.g. `https://myinstitution.odoo.com`) |

Odoo.sh maps environment variables into the container at startup.  The module
reads them via `ir.config_parameter` keys populated by the post-install hook
in `hooks.py` (or you can set them manually in
**Settings → Technical → Parameters → System Parameters**):

| ir.config_parameter key | Env var |
|-------------------------|---------|
| `nelc.lrs.endpoint` | `NELC_LRS_ENDPOINT` |
| `nelc.lrs.auth_header` | `NELC_LRS_AUTH_HEADER` |
| `nelc.platform_key` | `NELC_PLATFORM_KEY` |
| `web.base.url` | `ODOO_BASE_URL` (only if provided) |

> **Security note:** Never commit real credentials to source control.
> Use `.env.example` as a template and keep `.env` in `.gitignore`.

---

## Module structure

```
custo/nelc_xapi_admission/
├── __manifest__.py
├── __init__.py
├── data/
│   └── nelc_config_init.xml       # default (empty) ir.config_parameter records
├── models/
│   ├── __init__.py
│   └── op_admission_nelc.py       # inherit op.admission, add NELC fields
├── services/
│   ├── __init__.py
│   └── nelc_xapi_client.py        # build + POST xAPI statement
└── README.md
```

---

## Fields added to `op.admission`

| Field | Type | Description |
|-------|------|-------------|
| `x_nelc_national_id` | Char(10) | Student national ID (actor.name) |
| `x_nelc_registered_sent` | Boolean | True once statement was accepted by LRS |
| `x_nelc_registered_uuid` | Char | UUID returned by LRS on success |
| `x_nelc_registered_last_error` | Text | Last error from a failed send attempt |

---

## xAPI Statement structure

```json
{
  "id": "<client-generated-uuid>",
  "actor": {
    "objectType": "Agent",
    "name": "<national_id>",
    "mbox": "mailto:<student_email>"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/registered",
    "display": { "en-US": "registered", "ar-SA": "سُجِّل" }
  },
  "object": {
    "objectType": "Activity",
    "id": "https://<base_url>/course/<id>-<slug>",
    "definition": {
      "type": "https://w3id.org/xapi/cmi5/activitytype/course",
      "name": { "ar-SA": "...", "en-US": "..." },
      "description": { "ar-SA": "...", "en-US": "..." }
    }
  },
  "context": {
    "platform": "<platform_key>",
    "language": "ar-SA"
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

## Logging

All activity is logged under the `nelc_xapi_admission.services.nelc_xapi_client`
logger.  Check the Odoo log for lines prefixed with `nelc_xapi:`.
