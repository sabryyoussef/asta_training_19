# 🔌 Edafa Admission Portal - API Documentation

**Module:** `edafa_website_branding`  
**Version:** 18.0.1.2  
**Last Updated:** November 3, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [HTTP Routes](#http-routes)
3. [JSON-RPC Endpoints](#json-rpc-endpoints)
4. [JavaScript API](#javascript-api)
5. [Models & Methods](#models--methods)
6. [Integration Examples](#integration-examples)

---

## 🎯 Overview

This document provides complete API reference for the Edafa Admission Portal, including all routes, endpoints, methods, and integration points.

### Base URL

```
Development: http://localhost:8025
Production: https://your-domain.com
```

### Authentication

- **Public Routes:** No authentication required
- **Portal Routes:** User authentication required
- **JSON-RPC:** Public access with CSRF exemption where noted

---

## 🌐 HTTP Routes

### 1. Admission Wizard (Main Form)

#### `GET /admission/apply`

**Description:** Display multi-step admission wizard

**Authentication:** Public

**Parameters:** None

**Returns:** HTML page with 5-step wizard

**Example:**
```bash
curl http://localhost:8025/admission/apply
```

**Template:** `edafa_website_branding.admission_application_wizard`

**Context Variables:**
```python
{
    'courses': recordset,      # op.course records
    'batches': recordset,      # op.batch records
    'programs': recordset,     # op.program records
    'countries': recordset,    # res.country records
    'titles': recordset,       # res.partner.title records
    'default': dict,           # Demo data for testing
    'page_name': 'admission_wizard'
}
```

---

### 2. Classic Form (Legacy)

#### `GET /admission/apply/classic`

**Description:** Original single-page form (backward compatibility)

**Authentication:** Public

**Parameters:** None

**Returns:** HTML page with single-page form

**Template:** `edafa_website_branding.admission_application_form`

---

### 3. Form Submission

#### `POST /admission/submit`

**Description:** Submit admission application

**Authentication:** Public

**Method:** POST

**Content-Type:** `multipart/form-data`

**CSRF:** Required

**Parameters:**
```python
{
    # Required
    'first_name': str,
    'last_name': str,
    'email': str,
    'birth_date': date,
    'gender': str,  # 'm', 'f', 'o'
    'mobile': str,
    
    # Optional
    'title': int,  # res.partner.title ID
    'middle_name': str,
    'phone': str,
    'image': file,  # Binary file upload
    'street': str,
    'street2': str,
    'city': str,
    'zip': str,
    'country_id': int,  # res.country ID
    'state_id': int,  # res.country.state ID
    'program_id': int,  # op.program ID
    'course_id': int,  # op.course ID
    'batch_id': int,  # op.batch ID
    'prev_institute_id': str,
    'prev_course_id': str,
    'prev_result': str,
    'family_business': str,
    'family_income': float,
    'csrf_token': str  # Required
}
```

**Success Response:**
```
HTTP 302 Redirect
Location: /admission/thank-you?application=APP/2025/001
```

**Error Response:**
```
HTTP 302 Redirect
Location: /admission/apply
Session: admission_error dict with error messages
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8025/admission/submit \
  -F "first_name=Ahmed" \
  -F "last_name=Hassan" \
  -F "email=ahmed@example.com" \
  -F "birth_date=2000-01-15" \
  -F "gender=m" \
  -F "mobile=+966599214084" \
  -F "csrf_token=YOUR_TOKEN"
```

---

### 4. Thank You Page

#### `GET /admission/thank-you`

**Description:** Confirmation page after successful submission

**Authentication:** Public

**Parameters:**
- `application` (string): Application number

**Example:**
```
GET /admission/thank-you?application=APP/2025/001
```

---

### 5. Status Checker

#### `GET /admission/check-status`

**Description:** Check application status

**Authentication:** Public

**Parameters:**
- `application_number` (string): Application number
- `email` (string): Applicant email

**Example:**
```
GET /admission/check-status?application_number=APP/2025/001&email=test@example.com
```

**Returns:** HTML page with application details or error message

---

### 6. Portal - My Applications

#### `GET /my/applications`

**Description:** List user's applications (portal)

**Authentication:** User (logged in)

**Parameters:**
- `page` (int): Page number (default: 1)
- `sortby` (string): Sort field ('date', 'name', 'state')

**Example:**
```
GET /my/applications?page=1&sortby=date
```

---

### 7. Portal - Application Detail

#### `GET /my/application/<int:application_id>`

**Description:** View single application details

**Authentication:** User (logged in)

**Parameters:**
- `application_id` (int): Application ID

**Security:** User can only view their own applications (email match)

**Example:**
```
GET /my/application/42
```

---

## 🔄 JSON-RPC Endpoints

### 1. Check Email Duplicate

#### `POST /admission/check-email`

**Description:** Check if email already has active application

**Type:** JSON-RPC

**Authentication:** Public

**CSRF:** Disabled (csrf=False)

**Request:**
```javascript
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "email": "ahmed@example.com"
    },
    "id": 1
}
```

**Response:**
```javascript
{
    "jsonrpc": "2.0",
    "result": {
        "exists": true  // or false
    },
    "id": 1
}
```

**JavaScript Example:**
```javascript
const result = await jsonrpc('/admission/check-email', {
    email: 'ahmed@example.com'
});
console.log(result.exists);  // true or false
```

**Use Case:** Real-time email validation in wizard Step 1

---

### 2. Save Draft

#### `POST /admission/save-draft`

**Description:** Save application draft to session

**Type:** JSON-RPC

**Authentication:** Public

**CSRF:** Enabled

**Request:**
```javascript
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "first_name": "Ahmed",
        "last_name": "Hassan",
        "email": "ahmed@example.com",
        // ... all form fields
    },
    "id": 1
}
```

**Response:**
```javascript
{
    "jsonrpc": "2.0",
    "result": {
        "status": "saved",
        "timestamp": "2025-11-03T23:15:30"
    },
    "id": 1
}
```

**JavaScript Example:**
```javascript
const result = await jsonrpc('/admission/save-draft', {
    first_name: 'Ahmed',
    last_name: 'Hassan',
    // ... all fields
});
if (result.status === 'saved') {
    showMessage('Draft saved!');
}
```

**Use Case:** Auto-save feature (every 30 seconds)

---

### 3. Load Draft

#### `POST /admission/load-draft`

**Description:** Load saved draft from session

**Type:** JSON-RPC

**Authentication:** Public

**CSRF:** Enabled

**Request:**
```javascript
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
}
```

**Response:**
```javascript
{
    "jsonrpc": "2.0",
    "result": {
        "formData": {
            "first_name": "Ahmed",
            "last_name": "Hassan",
            // ... saved fields
        },
        "timestamp": "2025-11-03T23:15:30"
    },
    "id": 1
}
```

**JavaScript Example:**
```javascript
const result = await jsonrpc('/admission/load-draft', {});
if (result.formData) {
    restoreFormData(result.formData);
    alert('Draft from ' + result.timestamp + ' restored!');
}
```

**Use Case:** Restore draft when user returns to wizard

---

## 💻 JavaScript API

### ApplicationWizard Widget

**Selector:** `.admission-wizard`

**Public Methods:**

#### `showStep(stepNumber)`

Navigate to specific step.

**Parameters:**
- `stepNumber` (int): Step to display (1-5)

**Example:**
```javascript
const wizard = document.querySelector('.admission-wizard').__wizard__;
wizard.showStep(3);  // Jump to step 3
```

---

#### `next()`

Advance to next step after validation.

**Returns:** `boolean` (true if advanced, false if validation failed)

**Example:**
```javascript
wizard.next();
```

---

#### `previous()`

Go back to previous step.

**Example:**
```javascript
wizard.previous();
```

---

#### `validateStep(stepNumber)`

Validate specific step fields.

**Parameters:**
- `stepNumber` (int): Step to validate (1-5)

**Returns:** `boolean` (true if valid, false if errors)

**Example:**
```javascript
if (wizard.validateStep(1)) {
    console.log('Step 1 is valid!');
}
```

---

#### `populateReview()`

Populate review summary on step 5.

**Example:**
```javascript
wizard.populateReview();
```

---

### Inline Wizard Controller

**Global Object:** `window.wizard` (available in template)

**Properties:**
```javascript
{
    currentStep: 1,      // Current step number
    totalSteps: 5,       // Total number of steps
}
```

**Methods:**
```javascript
wizard.showStep(stepNum)     // Navigate to step
wizard.next()                 // Next step
wizard.previous()             // Previous step
wizard.validateStep(stepNum)  // Validate step
wizard.populateReview()       // Fill review summary
```

---

## 📦 Models & Methods

### OpAdmission Model Extension

**Model:** `op.admission`  
**Inherit:** `mail.thread`, `mail.activity.mixin`

**Fields Added by Portal:**

None (portal uses existing fields)

**Methods Available:**

#### Search Applications by Email

```python
# Python
admissions = env['op.admission'].sudo().search([
    ('email', '=', 'user@example.com')
])
```

```xml
<!-- XML-RPC -->
<methodCall>
  <methodName>execute</methodName>
  <params>
    <param><string>database</string></param>
    <param><int>uid</int></param>
    <param><string>password</string></param>
    <param><string>op.admission</string></param>
    <param><string>search_read</string></param>
    <param>
      <array>
        <data>
          <value><array><data>
            <value><array><data>
              <value><string>email</string></value>
              <value><string>=</string></value>
              <value><string>user@example.com</string></value>
            </data></array></value>
          </data></array></value>
        </data>
      </array>
    </param>
  </params>
</methodCall>
```

---

## 🔗 Integration Examples

### External System Integration

#### Submit Application via API

```python
import xmlrpc.client

# Connect to Odoo
url = 'http://localhost:8025'
db = 'your_database'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Create admission
admission_vals = {
    'register_id': 1,  # Must exist
    'first_name': 'Ahmed',
    'last_name': 'Hassan',
    'email': 'ahmed@example.com',
    'birth_date': '2000-01-15',
    'gender': 'm',
    'mobile': '+966599214084',
    'state': 'submit',
}

admission_id = models.execute_kw(
    db, uid, password,
    'op.admission', 'create',
    [admission_vals]
)

print(f'Created admission ID: {admission_id}')
```

---

### JavaScript Integration

#### Embed in External Website

```html
<!-- On external website -->
<iframe 
    src="http://your-odoo-domain.com/admission/apply" 
    width="100%" 
    height="800px"
    frameborder="0">
</iframe>
```

#### AJAX Submission

```javascript
// Submit application via AJAX
async function submitApplication(formData) {
    const response = await fetch('/admission/submit', {
        method: 'POST',
        body: new FormData(document.getElementById('admissionForm')),
    });
    
    if (response.redirected) {
        window.location.href = response.url;
    }
}
```

---

### Webhook Integration

#### Notify External System on Submission

```python
# In models/admission_extended.py
import requests

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    @api.model
    def create(self, vals):
        admission = super().create(vals)
        
        # Send webhook to external system
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('admission_webhook_url')
        if webhook_url:
            try:
                requests.post(webhook_url, json={
                    'event': 'admission.created',
                    'application_number': admission.application_number,
                    'email': admission.email,
                    'name': admission.name,
                    'course': admission.course_id.name,
                    'timestamp': fields.Datetime.now().isoformat(),
                })
            except Exception as e:
                _logger.error(f'Webhook error: {e}')
        
        return admission
```

---

## 📊 Response Codes

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | Success | Page loaded successfully |
| 302 | Redirect | After form submission |
| 400 | Bad Request | Invalid data sent |
| 403 | Forbidden | CSRF token missing/invalid |
| 404 | Not Found | Route doesn't exist |
| 500 | Server Error | Internal error (check logs) |

### Application States

| State | Code | Description |
|-------|------|-------------|
| draft | `'draft'` | Not submitted yet |
| submit | `'submit'` | Submitted from portal |
| confirm | `'confirm'` | Confirmed by admin |
| admission | `'admission'` | Admitted |
| reject | `'reject'` | Rejected |
| pending | `'pending'` | Awaiting information |
| cancel | `'cancel'` | Cancelled |

---

## 🔒 Security

### CSRF Protection

All POST routes require CSRF token:

```html
<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
```

**Exceptions:**
- `/admission/check-email` (JSON-RPC, read-only)

### Access Control

**Public Access:**
```python
# Can create admissions
auth='public'
request.env['op.admission'].sudo().create(vals)
```

**Portal Access:**
```python
# Can only view own applications
auth='user'
admissions = request.env['op.admission'].search([
    ('email', '=', request.env.user.partner_id.email)
])
```

---

## 📝 Data Models

### Application Data Structure

```python
{
    'id': 42,
    'application_number': 'APP/2025/001',
    'register_id': 1,
    'name': 'Ahmed Hassan Mohamed',
    'first_name': 'Ahmed',
    'middle_name': 'Hassan',
    'last_name': 'Mohamed',
    'title': 1,  # Mr.
    'email': 'ahmed@example.com',
    'mobile': '+966599214084',
    'phone': '',
    'birth_date': '2000-01-15',
    'gender': 'm',
    'image': b'base64_encoded_image...',
    'street': '123 Tahrir Street',
    'street2': 'Apt 5B',
    'city': 'Cairo',
    'zip': '11511',
    'country_id': 64,  # Egypt
    'state_id': 892,  # Cairo
    'program_id': False,
    'course_id': 5,  # Computer Science
    'batch_id': 12,  # Batch A
    'prev_institute_id': 'Cairo Secondary School',
    'prev_course_id': 'High School Diploma',
    'prev_result': '85%',
    'family_business': 'Self-employed',
    'family_income': 50000.0,
    'application_date': '2025-11-03 23:15:30',
    'admission_date': False,
    'state': 'submit',
    'partner_id': False,
    'student_id': False,
}
```

---

## 🛠️ Customization API

### Add Custom Validation

```javascript
// In your custom module's JS
odoo.define('your_module.custom_validation', function (require) {
    'use strict';
    
    const wizard = document.querySelector('.admission-wizard').__wizard__;
    
    // Override validation
    const originalValidate = wizard.validateStep;
    wizard.validateStep = function(stepNum) {
        // Run original validation
        if (!originalValidate.call(this, stepNum)) {
            return false;
        }
        
        // Add custom validation
        if (stepNum === 3) {
            const course = document.getElementById('course_id').value;
            if (!course) {
                alert('Please select a course');
                return false;
            }
        }
        
        return true;
    };
});
```

### Add Custom Step

```xml
<!-- Add step 6 to template -->
<div class="wizard-step" data-step="6">
    <div class="step-header">
        <h3>Additional Information</h3>
    </div>
    <!-- Your custom fields -->
</div>
```

```javascript
// Update total steps
wizard.totalSteps = 6;
```

---

## 📚 Code Examples

### Python: Create Application Programmatically

```python
# In Odoo shell or custom module
admission = env['op.admission'].sudo().create({
    'register_id': env['op.admission.register'].search([], limit=1).id,
    'name': 'Ahmed Hassan Mohamed',
    'first_name': 'Ahmed',
    'middle_name': 'Hassan',
    'last_name': 'Mohamed',
    'email': 'ahmed@example.com',
    'mobile': '+966599214084',
    'birth_date': '2000-01-15',
    'gender': 'm',
    'state': 'submit',
})
print(f'Created: {admission.application_number}')
```

### Python: Query Applications

```python
# Get all submitted applications
submitted = env['op.admission'].search([
    ('state', '=', 'submit'),
    ('application_date', '>=', '2025-11-01')
])

# Group by course
from collections import Counter
courses = Counter(submitted.mapped('course_id.name'))
print(courses.most_common(5))
```

### JavaScript: Listen to Wizard Events

```javascript
// Custom event listener
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admissionWizardForm');
    
    // Listen for step changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                const step = mutation.target.dataset.step;
                if (mutation.target.classList.contains('active')) {
                    console.log('Entered step:', step);
                    // Your custom logic
                }
            }
        });
    });
    
    // Observe all wizard steps
    document.querySelectorAll('.wizard-step').forEach(step => {
        observer.observe(step, { attributes: true });
    });
});
```

---

## 🔧 Error Handling

### Common Error Codes

```python
# In controller
try:
    admission = request.env['op.admission'].sudo().create(admission_vals)
except ValidationError as e:
    # Field validation failed
    return {'error': str(e)}
except AccessError as e:
    # Permission denied
    return {'error': 'Access denied'}
except Exception as e:
    # General error
    _logger.exception("Error creating admission")
    return {'error': 'System error occurred'}
```

### Error Response Format

```javascript
{
    "error": {
        "code": 400,
        "message": "Validation Error",
        "data": {
            "field": "email",
            "reason": "Invalid format"
        }
    }
}
```

---

## 📊 Rate Limiting (Future)

### Planned Rate Limits

```
Public API:
- 10 requests/minute per IP
- 100 requests/hour per IP

Authenticated API:
- 60 requests/minute
- 1000 requests/hour
```

**Implementation:**
```python
from odoo.addons.base.models.ir_http import IrHttp

class IrHttpCustom(IrHttp):
    @classmethod
    def _check_rate_limit(cls, ip_address):
        # Rate limiting logic
        pass
```

---

## 🎯 Best Practices

### For Developers

1. **Always Use sudo() for Public Access**
   ```python
   request.env['op.admission'].sudo().create(vals)
   ```

2. **Validate Input Server-Side**
   ```python
   if not vals.get('email'):
       raise ValidationError(_('Email is required'))
   ```

3. **Handle Errors Gracefully**
   ```python
   try:
       admission = create_admission(vals)
   except Exception as e:
       _logger.exception("Admission creation failed")
       return error_page()
   ```

4. **Log Important Events**
   ```python
   _logger.info(f'Application created: {admission.application_number}')
   ```

5. **Use Transactions**
   ```python
   with self.env.cr.savepoint():
       # Database operations
   ```

---

## 📞 Support

### API Support

- **Email:** dev@edafa.org
- **GitHub Issues:** Create issue with "API" label
- **Documentation:** This file + Enhancement Plan

### Report Issues

Include:
- API endpoint used
- Request parameters
- Response received
- Expected behavior
- Odoo version
- Module version

---

**Document Version:** 1.0  
**API Version:** 18.0.1.2  
**Last Updated:** November 3, 2025

