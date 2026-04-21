# NELC Auto Validation Checklist - Implementation Plan

## Goal
Bring `nelc_xapi_admission` from MVP (registered only) to full compliance with NELC FutureX auto-validation requirements.

## Scope
This plan covers:
- Statement lifecycle coverage and sequence controls
- Course/object integrity rules
- Context/extensions policies
- Learner identity validation
- Assessment and scoring rules
- Certification statement rules
- Test and validation strategy

---

## Current Baseline (Today)
- Implemented: `registered` statement on admission submission.
- Implemented: National ID format validation (10 digits, starts with 1/2/4).
- Missing: all remaining lifecycle statements and most checklist rule enforcement.

---

## Progress Update (2026-04-21)

### Completed
- Phase 1 foundation implemented:
  - Event ledger model `nelc.xapi.event.log` with dedup key + sequence index.
  - SQL uniqueness for `statement_uuid` and `dedup_key`.
  - Generic sender with validation, dedup skip behavior, and send outcome persistence.
- Phase 2 partially implemented:
  - Implemented service builders/senders for: `registered`, `initialized`, `progressed`, `attempted`, `rated`, `earned`.
  - Sequence controls implemented:
    - `registered` required before `initialized`/`progressed`/`attempted`/`rated`/`earned`.
    - `registered` vs `initialized` timestamp collision handling (+1 second).
    - `progressed` monotonic increase enforcement and timestamp ordering.
    - `attempt-id` sequential increment enforcement.
  - Validation rules implemented:
    - National ID required in actor.
    - `progressed.score.scaled` in range 0..1.
    - `attempted.score.min` required and `success=true` when `raw>=min`.
    - `rated.score.scaled` in range 0..1 and textual `response` required.
    - `earned` certificate id/url distinct + public URL format (`http/https`).
- Initial controller wiring implemented:
  - `initialized` + `progressed` emitted from portal interaction points (thank you/payment success).
  - `progressed` emitted from status check flow.

### In Progress
- Phase 2 remaining lifecycle emitters and concrete wiring:
  - `watched`, `completed` (lesson/module/course), `attended`.
- Phase 3 object naming and parent relationship strict enforcement.
- Phase 4 mandatory registration extensions and official platform name payload.
- Phase 7 retry queue/cron and replay tooling.
- Phase 8 tests and staging validation artifacts.

### Pending (blocked on business mapping)
- Final end-to-end wiring for quiz attempts, rating actions, and certificate issuance events in production workflows.
- Definitive object ID naming map (`CR/MD/LSN/VD/QZ/CFT`) across your actual course structures.
- Official AR/EN platform names and mandatory registration extension sources.

---

## Phase 1 - Foundation and Data Model

### 1.1 Add xAPI event ledger model
Create a persistent model (example: `nelc.xapi.event.log`) with:
- learner identifier (national ID + email)
- course/activity identifiers
- verb
- object id/type
- statement uuid
- payload snapshot
- status (`pending`, `sent`, `failed`, `skipped_duplicate`)
- sent timestamp / error text
- dedup key and sequence index

### 1.2 Add uniqueness and dedup constraints
- Enforce no duplicate statement for same learner+course+verb+object+attempt where business rules require uniqueness.
- Add deterministic dedup key generation in service layer.

### 1.3 Add centralized statement service
Refactor sender into generic APIs:
- `build_statement(event_type, context)`
- `validate_statement(statement, event_type)`
- `send_statement(statement)`
- `record_event_outcome(...)`

Deliverable:
- Infrastructure ready for all verbs with auditable history.

---

## Phase 2 - Lifecycle Coverage and Sequence Rules

### 2.1 Implement missing verbs
Add emitters/builders for:
- `initialized`
- `watched`
- `completed` (lesson/module/course)
- `attended` (virtual classroom)
- `attempted`
- `progressed`
- `rated`
- `earned`

### 2.2 Sequence guardrails
- Ensure `registered` happens first.
- Prevent `registered` and `initialized` at identical timestamp for same journey.
- Prevent out-of-order terminal events (e.g., `earned` before completion path).

### 2.3 Journey completeness checks
Add check utility/report to verify per learner-course:
- full lifecycle expected by NELC
- no missing mandatory steps

Deliverable:
- Full statement coverage from `registered` through `earned`.

---

## Phase 3 - Object Integrity and Naming Rules

### 3.1 Object ID policy enforcement
Implement strict naming generator and validator:
- Format style: `.../course/CR001/module/MD003/lesson/123423`
- Stable IDs for course, module, lesson, video, quiz, certificate

### 3.2 Verb-object matrix validation
Enforce allowed mappings (examples):
- `watched` -> video
- `completed` (lesson) -> lesson
- `attempted` -> unit-test
- `attended` -> virtual classroom

### 3.3 Parent relationship integrity
- Ensure `contextActivities.parent` uses the course object where applicable.
- Ensure course id consistency across all statements in same journey.

### 3.4 Description/duration constraints
- Course description mandatory and non-empty in `registered`.
- No HTML tags in names/descriptions.
- Description must not equal name.
- Duration presence for course/lesson/video/virtual classroom when required.

Deliverable:
- Statements structurally aligned with NELC object rules.

---

## Phase 4 - Context and Extension Compliance

### 4.1 Registration-only extension policy
Implement rule set:
- registration statement includes all mandatory NELC extensions
- non-registration statements do not carry forbidden registration-only fields

### 4.2 Mandatory registration extensions
Populate and validate:
- `https://nelc.gov.sa/extensions/lms_url`
- `https://nelc.gov.sa/extensions/program_url`
- official platform names under:
  - `context.extensions.https://nelc.gov.sa/extensions/platform.name.ar-SA`
  - `context.extensions.https://nelc.gov.sa/extensions/platform.name.en-US`
- platform key consistency in all statements

### 4.3 Localization/language checks
- Enforce `context.language` alignment with localized fields.
- Ensure valid localization keys (`ar-SA`, `en-US`) and no misplaced values.

Deliverable:
- Context/extensions fully compliant with NELC profile expectations.

---

## Phase 5 - Assessments, Attempts, Ratings

### 5.1 Attempt sequencing
For each learner+quiz:
- maintain `attempt_id` counter
- increment by exactly 1 per new attempt
- include attempt id extension in attempted statements

### 5.2 Score and success validation
- Require `result.score.min` in attempts
- enforce `result.success = true` when `raw >= min`

### 5.3 Rating rules
- enforce score range 0..1 for scaled ratings
- require textual review response for `rated`

Deliverable:
- Assessment and scoring validations pass checklist.

---

## Phase 6 - Certificate Rules

### 6.1 Earned statement and certificate object
- Add earned event builder with learner-specific certificate instance object.

### 6.2 Distinct certificate fields
- Separate certificate ID from certificate public URL extension.
- Validate URL is publicly accessible (configurable check strategy).

Deliverable:
- Certification-related checklist items pass.

---

## Phase 7 - Reliability and Operations

### 7.1 Retry queue and cron
- move failed sends to retry queue
- controlled retries with backoff and max attempts

### 7.2 Monitoring and diagnostics
- dashboard/list views for sent/failed/duplicates/sequencing violations
- exportable validation report per learner journey

### 7.3 Safe reprocessing tools
- admin actions: replay event, mark duplicate, rebuild payload

Deliverable:
- Operationally robust integration for staging/production validation.

---

## Phase 8 - Tests and Validation Pack

### 8.1 Unit tests
- statement builders
- field/extension validators
- naming/verb-object matrix checks
- attempt increment rules

### 8.2 Integration tests
- end-to-end learner journey simulation
- duplicate prevention under repeated triggers
- monotonic progress validation

### 8.3 Staging test script
Create a checklist-driven script/playbook to run with new learner+new content and collect:
- HTTP status
- returned UUIDs
- sent statement timeline
- rule pass/fail report

Deliverable:
- Repeatable evidence package for NELC validation.

---

## Suggested Execution Order
1. Phase 1 (foundation)
2. Phase 2 (coverage + sequence)
3. Phase 3 (object integrity)
4. Phase 4 (context/extensions)
5. Phase 5 (assessment rules)
6. Phase 6 (certification)
7. Phase 7 (reliability)
8. Phase 8 (tests + evidence)

---

## Definition of Done
The module is considered compliant when:
- all mandatory statements are emitted for a full learner journey
- all checklist validations pass automatically
- no duplicates are produced for same logical activity
- progress remains monotonic
- attempt IDs increment correctly
- certificate statement includes distinct, valid public URL
- test suite and staging validation report both pass

---

## What I Need From You

1. Platform identity values (required)
- Official platform key value to enforce in all statements.
- Official platform names exactly as licensed by NELC:
  - `ar-SA`
  - `en-US`

2. Registration mandatory extensions mapping (required)
- Source fields for:
  - `https://nelc.gov.sa/extensions/lms_url`
  - `https://nelc.gov.sa/extensions/program_url`
  - any additional required learner/program metadata in your NELC contract.

3. Object ID convention decision (required)
- Confirm exact naming scheme for:
  - course, module, lesson, video, quiz, certificate IDs
- Confirm whether IDs must be external stable codes (e.g., `CR001`) or can use Odoo IDs.

4. Hook mapping approval (required)
- Confirm which module/flow is the source of truth for:
  - quiz attempts (likely `gr.homework.attempt`)
  - learner rating submission (exact model/route)
  - certificate issuance (likely `gr.certificate` creation path)
  - video watched completion and virtual classroom attendance.

5. Staging validation data (required for final sign-off)
- A dedicated test learner + test course journey for full lifecycle.
- NELC staging endpoint/auth credentials already configured in Odoo.
