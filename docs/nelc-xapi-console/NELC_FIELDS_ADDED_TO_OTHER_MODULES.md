# Fields Added to Other Modules by NELC xAPI Integration

This document explains all fields and methods added to **OTHER modules** by the nelc_xapi_console integration.

---

## 1. **op.admission** Model (in openeducat_admission module)

### Fields Added via `nelc_xapi_admission/models/op_admission_nelc.py`

The NELC xAPI module inherits from `op.admission` and adds **4 custom fields**:

| Field Name | Type | Properties | Purpose |
|---|---|---|---|
| `x_nelc_national_id` | Char (size 10) | `copy=False` | 10-digit national identity number (format: starts with 1, 2, or 4). Used as `actor.name` in xAPI statements sent to NELC LRS |
| `x_nelc_registered_sent` | Boolean | Default: False, `copy=False` | Flag: True once the "registered" xAPI statement has been successfully sent to NELC LRS |
| `x_nelc_registered_uuid` | Char | Readonly, `copy=False` | UUID returned by the NELC LRS on successful statement delivery |
| `x_nelc_registered_last_error` | Text | Readonly, `copy=False` | Error message from the most recent failed attempt to send the "registered" statement |

**File Location:**
- [custo/nelc_xapi_admission/models/op_admission_nelc.py](custo/nelc_xapi_admission/models/op_admission_nelc.py)

---

## 2. **edafa_website_branding** Module

### Fields Added to `op.admission` Model

The edafa_website_branding module already extends `op.admission` with payment and portal fields. The NELC integration **does NOT add new fields** to op.admission here, but **adds helper methods** to the portal controller.

**File Location:**
- [custo/edafa_website_branding/models/admission_extended.py](custo/edafa_website_branding/models/admission_extended.py)

**Existing fields managed by edafa_website_branding** (NOT added by NELC, but USED by NELC logic):
- `department_id` – Many2one to op.department
- `access_token` – Portal security token
- `payment_status` – Selection field (none/unpaid/partial/paid/refunded)
- `payment_date` – Datetime when payment completed
- `currency_id` – Currency for payment amounts

### Methods Added to Portal Controller

The NELC integration **adds 3 helper methods** to `EdafaAdmissionPortal` controller for xAPI event emission:

#### 1. `_compute_nelc_progress_scaled(self, admission)`
- **Type:** Helper method (private, prefixed with `_`)
- **Purpose:** Map admission workflow state to course progress value (0..1 scale)
- **Location:** [custo/edafa_website_branding/controllers/admission_portal.py:34-50](custo/edafa_website_branding/controllers/admission_portal.py#L34)
- **Logic:** 
  ```python
  draft → 0.0
  submit → 0.20
  pending → 0.35
  confirm → 0.50
  admission → 0.80
  done → 1.0
  ```
  - Additionally boosts progress to 0.60 if `payment_status == 'paid'`

#### 2. `_emit_nelc_initialized_non_blocking(self, admission)`
- **Type:** Helper method (private)
- **Purpose:** Send xAPI "initialized" statement without interrupting portal UX
- **Location:** [custo/edafa_website_branding/controllers/admission_portal.py:52-64](custo/edafa_website_branding/controllers/admission_portal.py#L52)
- **Behavior:** 
  - Calls `send_initialized_statement()` from nelc_xapi_admission service
  - Wrapped in try/except to prevent portal errors if xAPI send fails
  - Logs exceptions but doesn't raise them (non-blocking)

#### 3. `_emit_nelc_progressed_non_blocking(self, admission)`
- **Type:** Helper method (private)
- **Purpose:** Send xAPI "progressed" statement with current progress value
- **Location:** [custo/edafa_website_branding/controllers/admission_portal.py:66-79](custo/edafa_website_branding/controllers/admission_portal.py#L66)
- **Behavior:** 
  - Computes progress using `_compute_nelc_progress_scaled()`
  - Calls `send_progressed_statement(env, admission, progress_scaled)`
  - Non-blocking (catches exceptions, doesn't interrupt portal)

### Routes Enhanced with NELC Event Hooks

The following **existing routes** in EdafaAdmissionPortal are enhanced with NELC event emissions:

#### Route 1: `admission_thank_you` 
- **URL:** `/admission/thank-you` (after form submission)
- **Location:** [Line 564-590](custo/edafa_website_branding/controllers/admission_portal.py#L564)
- **xAPI Events Triggered:**
  - `_emit_nelc_initialized_non_blocking()` – First time learner enters the system
  - `_emit_nelc_progressed_non_blocking()` – Progress = 0.20 (submit state)
- **When Called:** After successful application form submission

#### Route 2: `check_application_status`
- **URL:** `/admission/status` (status page view)
- **Location:** [Line 594-631](custo/edafa_website_branding/controllers/admission_portal.py#L594)
- **xAPI Events Triggered:**
  - `_emit_nelc_progressed_non_blocking()` – Re-emitted when status changes
- **When Called:** When applicant views their application status
- **Safeguard:** Only emits if status actually changed (prevents duplicate sends)

#### Route 3: `payment_success`
- **URL:** `/admission/payment-success/<admission_id>` (after successful payment)
- **Location:** [Line 807-831](custo/edafa_website_branding/controllers/admission_portal.py#L807)
- **xAPI Events Triggered:**
  - `_emit_nelc_initialized_non_blocking()` – If not already sent
  - `_emit_nelc_progressed_non_blocking()` – Progress boosted to 0.60+ (payment completed)
- **When Called:** After payment gateway (Stripe/PayPal) confirms payment success

---

## 3. **openeducat_admission** Module (openeducat base module)

**No fields or methods added directly.**

The NELC integration:
- Inherits from `op.admission` model (non-invasive)
- Does NOT patch existing code
- Does NOT modify existing fields

---

## Summary Table: Fields by Module

| Module | Field Name | Type | Added By | Purpose |
|--------|-----------|------|----------|---------|
| **openeducat_admission** | | | | |
| | `x_nelc_national_id` | Char(10) | nelc_xapi_admission | Student national ID for xAPI actor |
| | `x_nelc_registered_sent` | Boolean | nelc_xapi_admission | Dedup: "registered" event already sent? |
| | `x_nelc_registered_uuid` | Char | nelc_xapi_admission | LRS response UUID |
| | `x_nelc_registered_last_error` | Text | nelc_xapi_admission | Last send failure message |
| **edafa_website_branding** | | | | |
| | *(no new fields)* | | | Uses existing portal fields (payment_status, etc.) |

---

## Summary Table: Methods by Module

| Module | Method Name | Type | Location | Purpose |
|--------|------------|------|----------|---------|
| **edafa_website_branding** | | | | |
| | `_compute_nelc_progress_scaled()` | Private helper | controllers/admission_portal.py:34 | Map state → progress (0..1) |
| | `_emit_nelc_initialized_non_blocking()` | Private helper | controllers/admission_portal.py:52 | Send "initialized" xAPI statement |
| | `_emit_nelc_progressed_non_blocking()` | Private helper | controllers/admission_portal.py:66 | Send "progressed" xAPI statement |
| | `admission_thank_you()` | Route handler | controllers/admission_portal.py:564 | Enhanced with NELC hooks |
| | `check_application_status()` | Route handler | controllers/admission_portal.py:594 | Enhanced with NELC hooks |
| | `payment_success()` | Route handler | controllers/admission_portal.py:807 | Enhanced with NELC hooks |

---

## Design Philosophy

### Why No Modification to openeducat_admission?

The NELC integration follows **Odoo best practices**:
- **Inheritance only** – No direct edits to openeducat_admission source
- **Custom fields** – Prefixed with `x_nelc_` (custom namespace)
- **Copy protection** – Fields marked `copy=False` to prevent pollution of duplicated records
- **Portable** – The module can be removed without breaking openeducat_admission

### Why Minimal Changes to edafa_website_branding?

The NELC integration:
- **Adds only helper methods** – No new database fields in edafa_website_branding
- **Reuses existing routes** – Existing portal flows remain unchanged
- **Non-blocking design** – xAPI failures do NOT interrupt user journey
- **Future-proof** – Controller inherits more gracefully via nelc_xapi_console

---

## Where Are These Used?

| Item | Used In | How |
|------|---------|-----|
| `x_nelc_national_id` | nelc_xapi_admission service | Extracted as `actor.name` in xAPI statements |
| `x_nelc_registered_sent` | nelc_xapi_admission dedup logic | Prevents "registered" statement from being sent twice |
| `_compute_nelc_progress_scaled()` | admission_thank_you, check_application_status, payment_success | Converts Odoo state to xAPI progress value (0..1) |
| `_emit_nelc_initialized_non_blocking()` | admission_thank_you, payment_success | Sends "initialized" statement when learner first engages |
| `_emit_nelc_progressed_non_blocking()` | All 3 routes: thank-you, status-check, payment-success | Sends "progressed" statement with current progress |

---

## How to Use These Fields in Your Code

### Accessing NELC Fields on Admission

```python
# In a model or controller:
admission = env['op.admission'].browse(admission_id)

# Read the national ID
national_id = admission.x_nelc_national_id

# Check if registered statement was sent
already_registered = admission.x_nelc_registered_sent

# Read the LRS response UUID
uuid = admission.x_nelc_registered_uuid

# Read the last error (if any)
error_msg = admission.x_nelc_registered_last_error
```

### Calling NELC Emission Methods

```python
# In a controller inheriting from EdafaAdmissionPortal:
admission = env['op.admission'].browse(admission_id)

# Compute progress for this admission
progress_scaled = self._compute_nelc_progress_scaled(admission)

# Emit initialized (non-blocking)
self._emit_nelc_initialized_non_blocking(admission)

# Emit progressed (non-blocking)
self._emit_nelc_progressed_non_blocking(admission)
```

---

## Configuration & Installation

No special configuration is required to use these fields.

**Installation Steps:**
1. Install `nelc_xapi_admission` module
2. Fields are automatically added to `op.admission` via inheritance
3. Install `edafa_website_branding` module (already exists in this project)
4. Helper methods are available in the portal controller
5. When admission records are viewed/edited, fields are available in forms/lists

**Viewing Fields in Odoo UI:**
- Go to **Admission → Admissions**
- Open any admission record
- Fields appear in the form under a "NELC xAPI" tab/section (if UI configured to show them)
- Or use SQL/backend API to read/write directly

---

## Gotchas & Best Practices

1. **`x_nelc_national_id` is required** for xAPI statements
   - If blank, statements will fail with validation error
   - Ensure it's populated before calling xAPI senders

2. **`x_nelc_registered_sent` is a one-way flag**
   - Once True, "registered" statement is never re-sent
   - Prevents duplicate "registered" events (dedup safety)

3. **Helper methods are non-blocking**
   - Failed xAPI sends do NOT interrupt the portal user experience
   - Errors are logged but exceptions are caught
   - Always safe to call in routes

4. **Progress values are state-based, not real-time**
   - Progress is computed from admission.state (workflow state)
   - Not from external tracking; Odoo state transitions define it

5. **No sensitive data in xAPI statements**
   - Only national ID and email are sent to NELC LRS
   - No passwords, payment details, or internal notes

---

## Files To Review

- [nelc_xapi_admission/models/op_admission_nelc.py](custo/nelc_xapi_admission/models/op_admission_nelc.py) – Field definitions
- [edafa_website_branding/controllers/admission_portal.py](custo/edafa_website_branding/controllers/admission_portal.py) – Helper methods & route hooks
- [edafa_website_branding/models/admission_extended.py](custo/edafa_website_branding/models/admission_extended.py) – Other admission fields (pre-existing)
