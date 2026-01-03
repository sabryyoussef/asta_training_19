# 👨‍💻 Edafa Admission Portal - Developer Guide

**Module:** `edafa_website_branding`  
**Version:** 18.0.1.2  
**Last Updated:** November 3, 2025

---

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Extending the Wizard](#extending-the-wizard)
4. [Customization Examples](#customization-examples)
5. [Testing](#testing)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)

---

## 🚀 Development Setup

### Environment Setup

```bash
# 1. Clone repository
git clone git@github.com:sabryyoussef/motakamel_training_academy.git
cd motakamel_training_academy

# 2. Checkout feature branch
git checkout feature/edafa-admission-portal

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Odoo
# Edit odoo.conf with your settings

# 5. Start development server
python3 odoo-bin -c odoo.conf -d edu_demo --dev=all
```

### Development Tools

**Recommended:**
- PyCharm Professional (Odoo plugin)
- VS Code with Python extension
- Browser DevTools (Chrome/Firefox)
- Git for version control

**Odoo Dev Mode:**
```
# Enable developer mode
Navigate to Settings → Activate Developer Mode
```

---

## 🏗️ Architecture Overview

### Module Structure

```
edafa_website_branding/
├── controllers/
│   └── admission_portal.py       # HTTP/JSON-RPC routes
├── models/
│   └── website.py                 # Model extensions
├── static/
│   ├── src/
│   │   ├── css/
│   │   │   ├── admission_portal.css  # Original form styles
│   │   │   └── wizard.css            # Wizard styles
│   │   └── js/
│   │       ├── admission_form.js     # Original form logic
│   │       └── application_wizard.js # Wizard logic (OWL widget)
│   └── doc/
│       └── application_portal_enhancement/
│           ├── PORTAL_ENHANCEMENT_PLAN.md
│           ├── USER_GUIDE.md
│           ├── ADMIN_GUIDE.md
│           ├── API_DOCUMENTATION.md
│           ├── DEVELOPER_GUIDE.md
│           └── README.md
├── views/
│   ├── admission_portal_templates.xml      # Original form
│   ├── admission_wizard_templates.xml       # 5-step wizard
│   ├── admission_thank_you_template.xml
│   └── my_applications_template.xml
├── data/
│   ├── website_data.xml
│   └── website_menu.xml
└── __manifest__.py
```

### Technology Stack

**Backend:**
- Python 3.10+
- Odoo 18 Framework
- PostgreSQL 13+

**Frontend:**
- QWeb Templates
- Vanilla JavaScript (inline + OWL widget)
- Bootstrap 5
- Font Awesome icons

**APIs:**
- HTTP Routes (Odoo controllers)
- JSON-RPC endpoints
- ORM (Odoo models)

---

## 🔧 Extending the Wizard

### Adding a New Step

#### Step 1: Update Template

```xml
<!-- In admission_wizard_templates.xml -->

<!-- Add to progress indicator -->
<div class="step" data-step="6">
    <div class="step-icon">6</div>
    <div class="step-label">Documents</div>
</div>

<!-- Add step content -->
<div class="wizard-step" data-step="6">
    <div class="step-header">
        <h3>Upload Documents</h3>
        <p>Attach required certificates</p>
    </div>
    
    <div class="mb-3">
        <label for="id_document">ID Document</label>
        <input type="file" name="id_document" id="id_document" class="form-control-file"/>
    </div>
    
    <div class="mb-3">
        <label for="certificates">Certificates</label>
        <input type="file" name="certificates" id="certificates" class="form-control-file" multiple=""/>
    </div>
</div>
```

#### Step 2: Update JavaScript

```javascript
// In template inline script
const wizard = {
    currentStep: 1,
    totalSteps: 6,  // Changed from 5 to 6
    
    // ... rest of wizard code
};
```

#### Step 3: Update Controller (if needed)

```python
# Handle file uploads in admission_submit
if post.get('id_document'):
    file = post.get('id_document')
    admission_vals['id_document'] = base64.b64encode(file.read())
```

---

### Adding Custom Validation

#### Client-Side Validation

```javascript
// Add to wizard inline script after existing code
wizard.validateStep = function(stepNum) {
    // Call original validation first
    const isValid = this.validateStepOriginal(stepNum);
    if (!isValid) return false;
    
    // Add custom validation for step 3
    if (stepNum === 3) {
        const course = document.getElementById('course_id').value;
        const program = document.getElementById('program_id').value;
        
        // Require course selection
        if (!course) {
            alert('Please select a course to continue');
            document.getElementById('course_id').classList.add('is-invalid');
            return false;
        }
        
        // Validate course belongs to program (if program selected)
        if (program && course) {
            // AJAX call to verify relationship
            // Implementation left as exercise
        }
    }
    
    return true;
};

// Save original
wizard.validateStepOriginal = wizard.validateStep;
```

#### Server-Side Validation

```python
# In controllers/admission_portal.py
def admission_submit(self, **post):
    error = {}
    
    # Custom validation
    if post.get('family_income'):
        try:
            income = float(post.get('family_income'))
            if income < 0:
                error['family_income'] = 'Income cannot be negative'
        except ValueError:
            error['family_income'] = 'Invalid income value'
    
    if error:
        request.session['admission_error'] = error
        return request.redirect('/admission/apply')
    
    # Continue with submission
    # ...
```

---

## 💡 Customization Examples

### Example 1: Add Conditional Fields

**Requirement:** Show "Previous Degree" field only for Graduate programs

```javascript
// Add to wizard inline script
document.getElementById('program_id').addEventListener('change', function() {
    const programName = this.options[this.selectedIndex].text.toLowerCase();
    const degreeField = document.getElementById('previous_degree_section');
    
    if (programName.includes('graduate') || programName.includes('master')) {
        degreeField.style.display = 'block';
        document.getElementById('previous_degree').required = true;
    } else {
        degreeField.style.display = 'none';
        document.getElementById('previous_degree').required = false;
    }
});
```

---

### Example 2: Add Auto-Complete for City

**Requirement:** Suggest cities as user types

```xml
<!-- Add to template -->
<input type="text" name="city" id="city" class="form-control" list="city-suggestions"/>
<datalist id="city-suggestions">
    <option value="Cairo"/>
    <option value="Alexandria"/>
    <option value="Giza"/>
    <!-- More options -->
</datalist>
```

**Or use AJAX:**
```javascript
document.getElementById('city').addEventListener('input', async function() {
    const query = this.value;
    if (query.length < 2) return;
    
    const cities = await jsonrpc('/admission/suggest-cities', { query: query });
    // Display suggestions
});
```

---

### Example 3: Add Payment Step

**Step 1: Add Payment Step to Template**
```xml
<div class="wizard-step" data-step="5">
    <div class="step-header">
        <h3>Application Fee Payment</h3>
        <p>Pay application fee to continue</p>
    </div>
    
    <div id="payment-element"></div>
    <button type="button" id="pay-button">Pay Now</button>
</div>
```

**Step 2: Integrate Stripe**
```javascript
// Load Stripe.js
const stripe = Stripe('pk_test_YOUR_KEY');
const elements = stripe.elements();
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

document.getElementById('pay-button').addEventListener('click', async function() {
    const {error, paymentIntent} = await stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: 'http://localhost:8025/admission/payment-success',
        },
    });
    
    if (error) {
        showError(error.message);
    }
});
```

---

### Example 4: Add Email Verification

**Requirement:** Send verification code to email before allowing submission

**Backend:**
```python
import random
import string

@http.route('/admission/send-verification', type='json', auth='public')
def send_verification(self, email):
    """Send verification code to email"""
    code = ''.join(random.choices(string.digits, k=6))
    request.session[f'verification_{email}'] = code
    
    # Send email with code
    # ... email sending logic ...
    
    return {'status': 'sent'}

@http.route('/admission/verify-code', type='json', auth='public')
def verify_code(self, email, code):
    """Verify the code"""
    stored_code = request.session.get(f'verification_{email}')
    return {'valid': code == stored_code}
```

**Frontend:**
```javascript
// In wizard, before allowing submission
async function verifyEmail(email) {
    await jsonrpc('/admission/send-verification', {email: email});
    const userCode = prompt('Enter verification code sent to your email:');
    const result = await jsonrpc('/admission/verify-code', {email: email, code: userCode});
    return result.valid;
}
```

---

### Example 5: Add Analytics Tracking

**Google Analytics:**
```javascript
// Track step completion
wizard.showStep = function(stepNum) {
    // Original showStep logic
    // ...
    
    // Track with GA
    if (typeof gtag !== 'undefined') {
        gtag('event', 'step_complete', {
            'event_category': 'Application',
            'event_label': 'Step ' + stepNum,
            'value': stepNum
        });
    }
};
```

**Custom Analytics:**
```javascript
// Track to backend
function trackEvent(eventName, eventData) {
    jsonrpc('/admission/track-event', {
        event: eventName,
        data: eventData,
        timestamp: new Date().toISOString()
    });
}

// Usage
trackEvent('step_completed', {step: 2, time_spent: 45});
```

---

## 🧪 Testing

### Unit Testing (Python)

```python
# tests/test_admission_portal.py
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestAdmissionPortal(HttpCase):
    
    def test_admission_wizard_loads(self):
        """Test wizard page loads correctly"""
        response = self.url_open('/admission/apply')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'wizard-progress', response.content)
    
    def test_email_duplicate_check(self):
        """Test email duplicate detection"""
        # Create admission with test email
        self.env['op.admission'].create({
            'register_id': self.register.id,
            'name': 'Test User',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'birth_date': '2000-01-01',
            'gender': 'm',
            'mobile': '1234567890',
            'state': 'submit',
        })
        
        # Check duplicate
        result = self.url_open('/admission/check-email', 
                               data={'email': 'test@example.com'})
        self.assertTrue(result.json()['exists'])
    
    def test_application_submission(self):
        """Test full application submission"""
        data = {
            'first_name': 'Ahmed',
            'last_name': 'Hassan',
            'email': 'ahmed@test.com',
            'birth_date': '2000-01-15',
            'gender': 'm',
            'mobile': '+966599214084',
        }
        
        response = self.url_open('/admission/submit', data=data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify admission created
        admission = self.env['op.admission'].search([
            ('email', '=', 'ahmed@test.com')
        ])
        self.assertTrue(admission)
```

### JavaScript Testing

```javascript
// tests/test_wizard.js
QUnit.module('Admission Wizard');

QUnit.test('Wizard initializes correctly', function(assert) {
    const wizard = {currentStep: 1, totalSteps: 5};
    assert.equal(wizard.currentStep, 1, 'Starts at step 1');
    assert.equal(wizard.totalSteps, 5, 'Has 5 steps');
});

QUnit.test('Next button advances step', function(assert) {
    wizard.next();
    assert.equal(wizard.currentStep, 2, 'Advanced to step 2');
});

QUnit.test('Validation blocks invalid step', function(assert) {
    // Clear required field
    document.getElementById('email').value = '';
    const isValid = wizard.validateStep(1);
    assert.false(isValid, 'Step 1 invalid without email');
});
```

### End-to-End Testing (Playwright)

```javascript
// tests/e2e/admission_wizard.spec.js
import { test, expect } from '@playwright/test';

test('Complete application flow', async ({ page }) => {
    // Navigate to wizard
    await page.goto('http://localhost:8025/admission/apply');
    
    // Step 1: Personal Info
    await expect(page.locator('.step.active').first()).toHaveText('1');
    await page.fill('#first_name', 'Ahmed');
    await page.fill('#last_name', 'Hassan');
    await page.fill('#email', 'test@example.com');
    await page.fill('#birth_date', '2000-01-15');
    await page.selectOption('#gender', 'm');
    await page.fill('#mobile', '+966599214084');
    await page.click('.btn-wizard-next');
    
    // Step 2: Address
    await expect(page.locator('.step.active').first()).toHaveText('2');
    await page.fill('#city', 'Cairo');
    await page.click('.btn-wizard-next');
    
    // Step 3: Academic
    await expect(page.locator('.step.active').first()).toHaveText('3');
    await page.selectOption('#course_id', {index: 1});
    await page.click('.btn-wizard-next');
    
    // Step 4: Background
    await page.click('.btn-wizard-next');
    
    // Step 5: Review & Submit
    await expect(page.locator('.step.active').first()).toHaveText('5');
    await page.check('#terms_accepted');
    await page.click('.btn-wizard-submit');
    
    // Verify redirect to thank you page
    await expect(page).toHaveURL(/\/admission\/thank-you/);
});
```

---

## 🎨 Customization Examples

### Add Custom Field

**1. Add to Backend Model**
```python
# models/admission_extended.py
from odoo import fields, models

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    nationality = fields.Many2one('res.country', string='Nationality')
    passport_number = fields.Char(string='Passport Number', size=20)
```

**2. Add to Security**
```csv
# security/ir.model.access.csv
# Add if creating new model, not needed for field additions
```

**3. Add to Template**
```xml
<!-- In wizard step 1 -->
<div class="mb-3">
    <label for="nationality">Nationality</label>
    <select name="nationality" id="nationality" class="form-control">
        <option value="">Select Nationality...</option>
        <t t-foreach="countries" t-as="country">
            <option t-att-value="country.id">
                <t t-esc="country.name"/>
            </option>
        </t>
    </select>
</div>
```

**4. Add to Controller**
```python
# In admission_submit method
if post.get('nationality'):
    try:
        admission_vals['nationality'] = int(post.get('nationality'))
    except (ValueError, TypeError):
        pass
```

**5. Add to Review Step**
```xml
<div class="review-field">
    <div class="review-field-label">Nationality:</div>
    <div class="review-field-value" id="review-nationality"></div>
</div>
```

```javascript
// In populateReview
wizard.populateReview = function() {
    // ... existing code ...
    document.getElementById('review-nationality').textContent = 
        getSelect('nationality');
};
```

---

### Create Custom Validation Rule

**Example: Require course for certain programs**

```javascript
// Add after wizard definition
wizard.customValidations = {
    step3: function() {
        const program = document.getElementById('program_id').value;
        const course = document.getElementById('course_id').value;
        
        if (program && !course) {
            document.getElementById('course_id').classList.add('is-invalid');
            alert('Course is required when program is selected');
            return false;
        }
        
        return true;
    }
};

// Hook into validateStep
const originalValidate = wizard.validateStep;
wizard.validateStep = function(stepNum) {
    if (!originalValidate.call(this, stepNum)) {
        return false;
    }
    
    const customValidator = this.customValidations['step' + stepNum];
    if (customValidator) {
        return customValidator();
    }
    
    return true;
};
```

---

### Add Server-Side Validation

```python
# models/admission_extended.py
from odoo import api, models
from odoo.exceptions import ValidationError

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    @api.constrains('email', 'mobile')
    def _check_duplicate_contact(self):
        for record in self:
            # Check for duplicate email in active applications
            duplicate = self.search([
                ('id', '!=', record.id),
                ('email', '=', record.email),
                ('state', 'not in', ['cancel', 'reject'])
            ])
            if duplicate:
                raise ValidationError(
                    f'Email {record.email} already has an active application'
                )
    
    @api.constrains('birth_date')
    def _check_minimum_age(self):
        from datetime import date
        for record in self:
            if record.birth_date:
                today = date.today()
                age = (today - record.birth_date).days / 365.25
                if age < 16:
                    raise ValidationError(
                        'Applicant must be at least 16 years old'
                    )
```

---

## 📝 Common Patterns

### Pattern 1: AJAX Field Population

**Use Case:** Load states when country changes

```javascript
document.getElementById('country_id').addEventListener('change', async function() {
    const countryId = this.value;
    if (!countryId) return;
    
    const states = await jsonrpc('/web/dataset/call_kw', {
        model: 'res.country.state',
        method: 'search_read',
        args: [],
        kwargs: {
            domain: [['country_id', '=', parseInt(countryId)]],
            fields: ['id', 'name'],
        }
    });
    
    const stateSelect = document.getElementById('state_id');
    stateSelect.innerHTML = '<option value="">Select State...</option>';
    states.forEach(state => {
        stateSelect.innerHTML += `<option value="${state.id}">${state.name}</option>`;
    });
});
```

---

### Pattern 2: File Upload with Preview

```javascript
document.getElementById('image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate
    if (file.size > 5 * 1024 * 1024) {
        alert('File too large (max 5MB)');
        this.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = document.createElement('img');
        img.src = event.target.result;
        img.style.maxWidth = '200px';
        document.getElementById('image-preview').innerHTML = '';
        document.getElementById('image-preview').appendChild(img);
    };
    reader.readAsDataURL(file);
});
```

---

### Pattern 3: Progress Persistence

```javascript
// Save progress to localStorage
function saveProgress() {
    const formData = new FormData(document.getElementById('admissionWizardForm'));
    const data = Object.fromEntries(formData.entries());
    
    localStorage.setItem('admission_progress', JSON.stringify({
        step: wizard.currentStep,
        data: data,
        timestamp: new Date().toISOString()
    }));
}

// Load progress
function loadProgress() {
    const saved = localStorage.getItem('admission_progress');
    if (!saved) return;
    
    const progress = JSON.parse(saved);
    
    // Restore form data
    Object.keys(progress.data).forEach(key => {
        const field = document.querySelector(`[name="${key}"]`);
        if (field) field.value = progress.data[key];
    });
    
    // Jump to saved step
    wizard.showStep(progress.step);
}
```

---

## 🔍 Debugging

### Enable Debug Mode

```python
# In controller
import logging
_logger = logging.getLogger(__name__)

def admission_submit(self, **post):
    _logger.debug('Received submission: %s', post)
    # ... rest of code
```

### Browser DevTools

```javascript
// Add to wizard for debugging
wizard.debug = function() {
    console.log('Current Step:', this.currentStep);
    console.log('Form Data:', this.formData);
    console.log('Validation Cache:', this.validationCache);
};

// Call in console
wizard.debug();
```

### Performance Profiling

```python
import time

def admission_submit(self, **post):
    start = time.time()
    
    # ... processing ...
    
    duration = time.time() - start
    _logger.info(f'Submission processed in {duration:.2f}s')
```

---

## 📚 Best Practices

### Code Style

**Python:**
- Follow PEP 8
- Use descriptive variable names
- Add docstrings to all methods
- Use type hints where possible

```python
def create_admission(self, vals: dict) -> int:
    """
    Create admission record from portal submission
    
    Args:
        vals (dict): Admission field values
    
    Returns:
        int: Created admission ID
    
    Raises:
        ValidationError: If validation fails
    """
    # Implementation
```

**JavaScript:**
- Use ESLint with Odoo rules
- Comment complex logic
- Use const/let (no var)
- Handle errors gracefully

```javascript
/**
 * Validate email format and check for duplicates
 * @param {string} email - Email address to validate
 * @returns {Promise<boolean>} True if valid and unique
 */
async function validateEmail(email) {
    // Implementation
}
```

### Security

1. **Always Validate Server-Side**
   - Don't trust client validation
   - Validate all input
   - Sanitize data

2. **Use CSRF Tokens**
   - All POST forms must have CSRF token
   - Exempt read-only JSON-RPC carefully

3. **Limit Public Access**
   - Only allow creating admissions
   - No delete/write for public
   - Use sudo() carefully

4. **Rate Limiting**
   - Prevent spam submissions
   - Limit AJAX requests
   - Block suspicious IPs

### Performance

1. **Optimize Queries**
   ```python
   # Bad
   for course in courses:
       batches = course.batch_ids  # N+1 query
   
   # Good
   courses_with_batches = courses.with_context(prefetch_fields=['batch_ids'])
   ```

2. **Cache Static Data**
   ```python
   @tools.ormcache('country_id')
   def get_states(self, country_id):
       return self.env['res.country.state'].search([
           ('country_id', '=', country_id)
       ])
   ```

3. **Lazy Load Assets**
   ```xml
   <!-- Load only when needed -->
   <script src="/static/src/js/wizard.js" defer="defer"></script>
   ```

---

## 🎓 Learning Resources

### Odoo Development

- **Official Docs:** https://www.odoo.com/documentation/18.0/developer/
- **OWL Framework:** https://github.com/odoo/owl
- **Community:** https://www.odoo.com/forum

### Web Development

- **Bootstrap 5:** https://getbootstrap.com/docs/5.0/
- **JavaScript:** https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **QWeb:** Odoo template engine docs

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**For Module Version:** 18.0.1.2

