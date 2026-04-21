# NELC xAPI Console - Developer Documentation

## 1. Purpose
`nelc_xapi_console` is a standalone backend application module that centralizes:
- NELC xAPI configuration
- manual xAPI event testing
- integration log visibility
- portal-flow integration using inheritance (without patching source files in other modules)

This module is designed for portability across repositories.

## 2. Design Goals
- Keep all NELC operational UI in one module (menus, forms, lists, actions).
- Avoid direct source edits in other modules by using model/controller inheritance.
- Reuse existing sender/service in `nelc_xapi_admission`.
- Provide auditable execution history through `nelc.xapi.event.log`.

## 3. Dependencies
Defined in `__manifest__.py`:
- `base`
- `openeducat_admission`
- `edafa_website_branding`
- `nelc_xapi_admission`

Why:
- `openeducat_admission`: provides `op.admission`.
- `edafa_website_branding`: provides portal controller routes inherited by this module.
- `nelc_xapi_admission`: provides sender service and event log model.

## 4. Module Structure
- `__manifest__.py`: app metadata, dependencies, data files.
- `models/nelc_xapi_console_settings.py`: settings UI model and sync/apply actions.
- `models/nelc_xapi_manual_test.py`: manual test model and event dispatch action.
- `controllers/admission_portal_inherit.py`: inherited portal route hooks.
- `views/*`: list/form/search views and menu entries.
- `security/ir.model.access.csv`: access control for console models.
- `data/sequence_data.xml`: sequence for manual test records.

## 5. Data Models

### 5.1 `nelc.xapi.console.settings`
Purpose:
- Stores editable operational settings in a form.
- Syncs with and applies values to `ir.config_parameter`.

Primary fields:
- `lrs_endpoint`
- `lrs_auth_header`
- `platform_key`
- `odoo_base_url`
- `platform_name_ar`
- `platform_name_en`
- `last_synced_at`
- `last_applied_at`

Methods:
- `action_sync_from_parameters()`: reads current parameter values.
- `action_apply_to_parameters()`: writes current form values to parameters.

Config keys used:
- `nelc.lrs.endpoint`
- `nelc.lrs.auth_header`
- `nelc.platform_key`
- `web.base.url`
- `nelc.platform.name.ar`
- `nelc.platform.name.en`

### 5.2 `nelc.xapi.manual.test`
Purpose:
- Lets admins create and execute manual xAPI test sends against an admission.

Supported `event_type` values:
- `registered`
- `initialized`
- `progressed`
- `attempted`
- `rated`
- `earned`

Execution:
- `action_send_test()` routes to the relevant sender in `nelc_xapi_admission.services.nelc_xapi_client`.
- Writes execution status, UUID, timestamp, and error message.
- Attempts to link the generated/sent ledger row in `nelc.xapi.event.log`.

## 6. Controller Inheritance (No Source Patching)
File: `controllers/admission_portal_inherit.py`

Class: `NelcXapiConsolePortalIntegration(EdafaAdmissionPortal)`

Inherited routes:
- `admission_thank_you`
- `check_application_status`
- `payment_success`

Behavior:
- Calls `super()` to preserve original portal behavior.
- Adds non-blocking NELC emits from this module via inherited hooks.
- Emits `initialized` and/or `progressed` when conditions are met.
- Uses `x_nelc_registered_sent` as prerequisite.

This allows behavior injection from one module without editing `edafa_website_branding` source in the target repo.

## 7. Menus and Views
App root menu:
- `NELC xAPI Console`

Submenus:
- `Settings`
- `Manual Tests`
- `Event Logs`

Provided UI artifacts:
- Settings list/form
- Manual test list/form
- Event log list/form/search

## 8. Installation
1. Copy module folder `custo/nelc_xapi_console` to target repository.
2. Ensure dependency modules exist in that repository:
   - `nelc_xapi_admission`
   - `edafa_website_branding`
   - `openeducat_admission`
3. Update Apps List.
4. Install `NELC xAPI Console`.

## 9. Configuration and Operation
1. Open app: `NELC xAPI Console` -> `Settings`.
2. Configure endpoint/auth/platform/base URL.
3. Click `Apply To Parameters`.
4. Open `Manual Tests` and create test records by event type.
5. Click `Send Test Event`.
6. Validate outcomes in `Event Logs`.

## 10. Porting to Another Repo (Single-Module Integration Pattern)
If you do not want to patch other modules directly:
- Keep all integration logic in this module via inheritance.
- Do not edit `edafa_website_branding` source; use inherited routes in this module.
- Keep `nelc_xapi_admission` as service dependency for sender and log persistence.

If target repo has a different portal controller class or route names:
- Replace `EdafaAdmissionPortal` import in `controllers/admission_portal_inherit.py`.
- Override the equivalent route methods and keep `super()` behavior.

## 11. Known Constraints
- This module is backend app UI. It is not a public website UI.
- `attempted`, `rated`, and `earned` are currently manually executable from UI; production auto-hooking depends on available business events in target modules.
- Event sequencing and dedup are enforced by `nelc_xapi_admission` service/ledger.

## 12. Extension Guide
Typical extension points:
- Add new event type support in `nelc.xapi.manual.test` selection and sender map.
- Add extra config fields to `nelc.xapi.console.settings` and sync/apply methods.
- Add dashboards/graphs using `nelc.xapi.event.log` grouped by status/event type.
- Add scheduled actions (cron) for replay/retry workflows in a future enhancement.

## 13. Acceptance Checklist
- Module installs without patching dependency module source.
- App menu appears with Settings/Manual Tests/Event Logs.
- Settings apply to `ir.config_parameter` successfully.
- Manual test send creates or links `nelc.xapi.event.log` entries.
- Inherited portal hooks execute without breaking existing routes.
