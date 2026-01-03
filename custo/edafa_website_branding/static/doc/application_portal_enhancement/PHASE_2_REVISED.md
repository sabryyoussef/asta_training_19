# 🚀 Phase 2 Implementation Plan - REVISED & CLARIFIED

**Module:** `edafa_website_branding`  
**Phase:** 2 of 4  
**Duration:** 2 weeks (80 hours)  
**Priority:** 🔴 High  
**Date:** November 3, 2025  
**Last Updated:** November 4, 2025

---

## 📊 PROGRESS SUMMARY

### ✅ Completed Today (November 3-4, 2025)

**Step 1: Extended Admission Model** ✅
- Added payment fields to `op.admission` via inheritance
- Fields: `access_token`, `application_fee`, `payment_status`, `payment_transaction_id`, `invoice_id`
- Added methods: `_generate_access_token()`, `action_create_invoice()`, `_update_payment_status_from_transaction()`

**Step 2: Created Payment Routes** ✅
- `/admission/<id>/payment` - Payment page with provider selection
- `/admission/<id>/create-payment-transaction` - Transaction creation
- `/admission/<id>/payment/success` - Success callback
- `/admission/<id>/payment/cancel` - Cancel/failed callback
- Helper method: `_check_admission_access()` for security

**Step 3: Created Payment Templates** ✅
- `admission_payment_page` - Main payment page
- `admission_payment_success` - Success page with animated checkmark
- `admission_payment_cancel` - Cancel page with retry option

**Step 3.5: Integrated Payment in User Flow** ✅
- Added payment button to thank you page
- Set default `application_fee = $50.00` for new applications
- Yellow alert box highlighting payment requirement
- Seamless flow from submission → payment

**Testing Infrastructure** ✅
- Created `demo_data.xml` with test admissions
- Created `payment_data.xml` with default product
- Added comprehensive `TESTING_GUIDE.md`
- Debug logging for troubleshooting

---

## 🎯 What's Left To Do

### ⬜ Step 4: Conditional Fields (Next Session)
- Program → Course filtering with AJAX
- Course → Batch filtering
- Dynamic course fee display
- Show/hide fields based on selections

### ⬜ Step 5: Email Notifications
- Payment confirmation emails
- Application status update emails
- Email templates

### ⬜ Step 6: Full Integration Testing
- End-to-end payment flow with Stripe test mode
- Email delivery testing
- Error handling verification
- Mobile responsiveness testing

---

## 📋 What We're Building

### Scope (REVISED)

✅ **Payment Integration** (48 hours) - IN PROGRESS (70% DONE)
- ✅ Application fee management
- ✅ Invoice generation
- ✅ Integration with Odoo payment providers
- ✅ Payment status tracking
- ✅ Payment UI pages (main, success, cancel)
- ✅ Thank you page integration
- ⬜ Email notifications
- ⬜ Full end-to-end testing with live gateway

✅ **Conditional Fields** (32 hours) - NOT STARTED
- Dynamic field show/hide
- Program → Course filtering
- Course → Batch filtering
- Course fee display
- Smart field requirements

❌ **Document Upload** - REMOVED
- Deferred to separate document management module
- Will be added later per user's deliverable requirements

---

## 💳 PAYMENT GATEWAY - Complete Explanation

### Where Does Payment Live in Odoo?

#### Option A: Odoo Built-in Payment Providers (RECOMMENDED)

**Location:** Odoo Core Modules

```bash
# These are ALREADY in Odoo core, just need to install/enable:

odoo/addons/payment/              # Payment framework (always installed)
odoo/addons/payment_stripe/       # Stripe gateway (install from Apps)
odoo/addons/payment_paypal/       # PayPal gateway (install from Apps)
odoo/addons/payment_authorize/    # Authorize.net (install from Apps)
```

**How to Use:**

**Step 1: Install Payment Provider (One-time setup)**
```
Settings → Apps → Remove "Apps" filter → Search "Stripe"
→ Click "Install" on "Payment Provider: Stripe"
```

**Step 2: Configure (One-time setup)**
```
Website → Configuration → Payment Providers → Stripe
→ Enable: ✓
→ Publishable Key: pk_test_xxxxx (from Stripe dashboard)
→ Secret Key: sk_test_xxxxx (from Stripe dashboard)
→ Save
```

**Step 3: Use in Code (What we'll implement)**
```python
# In YOUR module (edafa_website_branding)
# Create payment transaction
tx = request.env['payment.transaction'].sudo().create({
    'provider_id': stripe_provider.id,  # Get enabled Stripe provider
    'amount': admission.application_fee,
    'currency_id': admission.currency_id.id,
    'reference': admission.application_number,
    'partner_id': admission.partner_id.id,
})

# Redirect user to Odoo's payment page (handles everything)
return request.redirect(f'/payment/pay?reference={tx.reference}')
```

**Benefits:**
- ✅ **No payment code to write** - Odoo handles it
- ✅ **PCI compliant** - Card data never touches your server
- ✅ **Multi-gateway** - Stripe, PayPal, etc. same code
- ✅ **Automatic reconciliation** - Payments auto-linked
- ✅ **3D Secure support** - Built-in
- ✅ **Webhooks handled** - Stripe → Odoo automatic

**This is what we'll use!**

---

#### Option B: Custom Integration (NOT RECOMMENDED - Complex)

Only if you need special gateway not supported by Odoo.

**We won't do this** - unnecessary complexity!

---

### What Goes in YOUR Module (edafa_website_branding)

**Your module only adds:**

1. **Payment fields** to `op.admission` model:
   ```python
   application_fee = fields.Monetary('Application Fee')
   payment_status = fields.Selection([...])
   payment_transaction_id = fields.Many2one('payment.transaction')
   ```

2. **Routes** to trigger payment:
   ```python
   @http.route('/admission/<id>/pay')
   def initiate_payment(self, admission_id):
       # Create payment.transaction
       # Redirect to Odoo payment page
   ```

3. **UI** to show payment option:
   ```xml
   <a href="/admission/123/pay">Pay Application Fee</a>
   ```

**That's it!** Odoo payment modules do the heavy lifting.

---

## 📝 Implementation Plan (REVISED - NO DOCUMENTS)

### Phase 2.1: Payment Integration (48 hours)

#### Step 1: Extend Admission Model (8 hours)

**File:** `models/admission_extended.py` (New)

```python
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    # Payment fields
    application_fee = fields.Monetary('Application Fee', 
                                     currency_field='currency_id',
                                     help="Fee for application processing")
    payment_status = fields.Selection([
        ('none', 'No Payment Required'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Payment Status', default='none', tracking=True)
    
    payment_transaction_id = fields.Many2one('payment.transaction', 
                                            string='Payment Transaction',
                                            readonly=True)
    invoice_id = fields.Many2one('account.move', 'Application Invoice',
                                 readonly=True)
    currency_id = fields.Many2one('res.currency', 
                                  compute='_compute_currency_id',
                                  store=True)
    payment_date = fields.Datetime('Payment Date', readonly=True)
    payment_reference = fields.Char('Payment Reference', readonly=True)
    
    @api.depends('company_id')
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = record.company_id.currency_id or \
                                self.env.company.currency_id
    
    @api.onchange('course_id', 'register_id')
    def _onchange_application_fee(self):
        """Auto-set application fee from register or course"""
        if self.register_id and self.register_id.product_id:
            self.application_fee = self.register_id.product_id.lst_price
        elif self.course_id and hasattr(self.course_id, 'application_fee'):
            self.application_fee = self.course_id.application_fee
        else:
            self.application_fee = 0.0
    
    def action_create_invoice(self):
        """Create invoice for application fee (like openeducat_fees pattern)"""
        self.ensure_one()
        
        if self.invoice_id:
            raise ValidationError(_('Invoice already exists'))
        
        if not self.application_fee or self.application_fee <= 0:
            return False
        
        # Get or create application fee product
        product = self.env.ref('edafa_website_branding.product_application_fee',
                              raise_if_not_found=False)
        if not product:
            # Create default product
            product = self.env['product.product'].sudo().create({
                'name': 'Application Processing Fee',
                'type': 'service',
                'list_price': 50.0,
                'invoice_policy': 'order',
            })
        
        # Get partner or create one
        partner = self.partner_id
        if not partner:
            partner = self.env['res.partner'].sudo().create({
                'name': self.name,
                'email': self.email,
                'phone': self.mobile,
            })
            self.partner_id = partner.id
        
        # Create invoice (following openeducat_fees/models/student.py pattern)
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Application Fee - {self.application_number}',
                'product_id': product.id,
                'quantity': 1.0,
                'price_unit': self.application_fee,
            })],
        })
        
        self.invoice_id = invoice.id
        self.payment_status = 'unpaid'
        
        return invoice
```

**Step 2: Add Payment Routes (8 hours)**

**File:** `controllers/admission_portal.py`

Add these methods to existing `EdafaAdmissionPortal` class:

```python
@http.route('/admission/<int:admission_id>/payment', type='http', 
            auth='public', website=True)
def admission_payment_page(self, admission_id, access_token=None, **kwargs):
    """Display payment page for application fee"""
    admission = request.env['op.admission'].sudo().browse(admission_id)
    
    if not admission.exists():
        return request.render('website.404')
    
    # Verify access (either public with token, or owner)
    if not self._check_admission_access(admission, access_token):
        return request.render('website.403')
    
    # Create invoice if doesn't exist and fee > 0
    if not admission.invoice_id and admission.application_fee > 0:
        admission.action_create_invoice()
    
    # Get available payment providers
    providers = request.env['payment.provider'].sudo().search([
        ('state', '=', 'enabled'),
        ('is_published', '=', True),
    ])
    
    return request.render('edafa_website_branding.admission_payment_page', {
        'admission': admission,
        'invoice': admission.invoice_id,
        'providers': providers,
        'access_token': access_token,
        'page_name': 'payment',
    })

@http.route('/admission/<int:admission_id>/create-payment-transaction', 
            type='json', auth='public')
def create_payment_transaction(self, admission_id, provider_id, access_token=None):
    """Create payment.transaction for online payment"""
    admission = request.env['op.admission'].sudo().browse(admission_id)
    
    if not admission.exists() or not self._check_admission_access(admission, access_token):
        return {'error': 'Access denied'}
    
    # Ensure partner exists
    if not admission.partner_id:
        partner = request.env['res.partner'].sudo().create({
            'name': admission.name,
            'email': admission.email,
            'phone': admission.mobile,
        })
        admission.partner_id = partner.id
    
    # Create payment transaction
    tx = request.env['payment.transaction'].sudo().create({
        'provider_id': int(provider_id),
        'amount': admission.application_fee,
        'currency_id': admission.currency_id.id,
        'partner_id': admission.partner_id.id,
        'reference': admission.application_number,
        'landing_route': f'/admission/{admission.id}/payment/success',
    })
    
    admission.payment_transaction_id = tx.id
    
    return {
        'success': True,
        'transaction_id': tx.id,
        'redirect_url': f'/payment/pay?reference={tx.reference}',
    }

@http.route('/admission/<int:admission_id>/payment/success', 
            type='http', auth='public', website=True)
def payment_success(self, admission_id, **kwargs):
    """Payment success callback"""
    admission = request.env['op.admission'].sudo().browse(admission_id)
    
    if admission.exists() and admission.payment_transaction_id:
        tx = admission.payment_transaction_id
        
        # Check if payment is successful
        if tx.state == 'done':
            admission.write({
                'payment_status': 'paid',
                'payment_date': fields.Datetime.now(),
                'payment_reference': tx.reference,
                'state': 'confirm',  # Auto-confirm after payment
            })
    
    return request.render('edafa_website_branding.payment_success_page', {
        'admission': admission,
        'transaction': admission.payment_transaction_id,
    })

def _check_admission_access(self, admission, access_token=None):
    """Check if user can access admission (owner or has token)"""
    if request.env.user._is_public():
        # Public user needs access token
        return access_token and admission.access_token == access_token
    else:
        # Logged in user must be owner
        return admission.partner_id == request.env.user.partner_id
```

**Step 3: Update Thank You Page to Show Payment Link (2 hours)**

**File:** `views/admission_thank_you_template.xml`

Add after application number display:

```xml
<!-- Payment Section -->
<div t-if="admission.application_fee > 0" class="alert alert-warning my-4">
    <h4><i class="fa fa-credit-card"></i> Application Fee Payment</h4>
    <p><strong>Amount Due:</strong> 
        <span t-esc="admission.application_fee" 
              t-options="{'widget': 'monetary', 'display_currency': admission.currency_id}"/>
    </p>
    
    <t t-if="admission.payment_status == 'unpaid'">
        <p>Please complete payment to process your application.</p>
        <a t-attf-href="/admission/#{admission.id}/payment?access_token=#{admission.access_token}"
           class="btn btn-primary btn-lg">
            <i class="fa fa-credit-card"></i> Pay Now
        </a>
    </t>
    <t t-elif="admission.payment_status == 'paid'">
        <p class="text-success"><i class="fa fa-check-circle"></i> Payment Received - Thank you!</p>
    </t>
</div>
```

**Step 4: Create Payment Page Template (6 hours)**

**File:** `views/payment_templates.xml` (New)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <template id="admission_payment_page" name="Application Fee Payment">
        <t t-call="website.layout">
            <div class="container mt-5 mb-5">
                <div class="row">
                    <div class="col-md-8 offset-md-2">
                        
                        <!-- Application Summary -->
                        <div class="card mb-4">
                            <div class="card-header bg-success text-white">
                                <h4><i class="fa fa-graduation-cap"></i> Application Summary</h4>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-6">
                                        <p><strong>Application Number:</strong><br/>
                                           <span class="text-primary" t-esc="admission.application_number"/></p>
                                        <p><strong>Applicant:</strong><br/>
                                           <t t-esc="admission.name"/></p>
                                    </div>
                                    <div class="col-6">
                                        <p><strong>Course:</strong><br/>
                                           <t t-esc="admission.course_id.name"/></p>
                                        <p><strong>Application Date:</strong><br/>
                                           <span t-field="admission.application_date"/></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Payment Section -->
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h4><i class="fa fa-credit-card"></i> Payment Required</h4>
                            </div>
                            <div class="card-body">
                                
                                <!-- Amount -->
                                <div class="text-center mb-4">
                                    <h2>Amount Due</h2>
                                    <h1 class="text-success">
                                        <span t-esc="admission.application_fee"
                                              t-options="{'widget': 'monetary', 'display_currency': admission.currency_id}"/>
                                    </h1>
                                </div>
                                
                                <!-- Payment Status -->
                                <t t-if="admission.payment_status == 'paid'">
                                    <div class="alert alert-success text-center">
                                        <i class="fa fa-check-circle fa-3x mb-3"></i>
                                        <h4>Payment Received!</h4>
                                        <p>Your application is being processed.</p>
                                        <a href="/my/applications" class="btn btn-primary">
                                            View My Applications
                                        </a>
                                    </div>
                                </t>
                                
                                <t t-else="">
                                    <!-- Payment Methods -->
                                    <h5 class="mb-3">Choose Payment Method:</h5>
                                    
                                    <!-- Online Payment -->
                                    <t t-if="providers">
                                        <div class="card mb-3">
                                            <div class="card-body">
                                                <h6><i class="fa fa-credit-card"></i> Pay Online (Credit/Debit Card)</h6>
                                                <p class="text-muted">Secure payment powered by Stripe/PayPal</p>
                                                
                                                <t t-foreach="providers" t-as="provider">
                                                    <button class="btn btn-primary btn-lg mr-2 pay-online-btn"
                                                            t-att-data-provider-id="provider.id"
                                                            t-att-data-admission-id="admission.id"
                                                            t-att-data-access-token="access_token">
                                                        <i class="fa fa-lock"></i> Pay with <t t-esc="provider.name"/>
                                                    </button>
                                                </t>
                                            </div>
                                        </div>
                                    </t>
                                    
                                    <!-- Bank Transfer / Manual Payment -->
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <h6><i class="fa fa-university"></i> Bank Transfer / Cash</h6>
                                            <p class="text-muted">Download invoice and pay manually</p>
                                            
                                            <t t-if="invoice">
                                                <a t-attf-href="/my/invoices/#{invoice.id}" 
                                                   class="btn btn-secondary">
                                                    <i class="fa fa-download"></i> Download Invoice
                                                </a>
                                            </t>
                                            <t t-else="">
                                                <p class="text-info">Invoice will be generated by admissions staff.</p>
                                            </t>
                                        </div>
                                    </div>
                                </t>
                                
                            </div>
                        </div>
                        
                    </div>
                </div>
            </div>
            
            <!-- Inline payment JavaScript -->
            <script type="text/javascript">
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('.pay-online-btn').forEach(btn => {
                        btn.addEventListener('click', async function() {
                            const providerId = this.dataset.providerId;
                            const admissionId = this.dataset.admissionId;
                            const accessToken = this.dataset.accessToken;
                            
                            this.disabled = true;
                            this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing...';
                            
                            try {
                                // Create payment transaction via AJAX
                                const response = await fetch('/admission/' + admissionId + '/create-payment-transaction', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                        jsonrpc: '2.0',
                                        method: 'call',
                                        params: {
                                            provider_id: providerId,
                                            access_token: accessToken
                                        }
                                    })
                                });
                                
                                const data = await response.json();
                                
                                if (data.result && data.result.redirect_url) {
                                    // Redirect to Odoo's payment page
                                    window.location.href = data.result.redirect_url;
                                } else {
                                    alert('Error creating payment: ' + (data.result.error || 'Unknown error'));
                                    this.disabled = false;
                                    this.innerHTML = '<i class="fa fa-lock"></i> Pay Online';
                                }
                            } catch (error) {
                                console.error('Payment error:', error);
                                alert('Payment system error. Please try again or use bank transfer.');
                                this.disabled = false;
                                this.innerHTML = '<i class="fa fa-lock"></i> Pay Online';
                            }
                        });
                    });
                });
            </script>
        </t>
    </template>
    
    <!-- Payment Success Page -->
    <template id="payment_success_page" name="Payment Success">
        <t t-call="website.layout">
            <div class="container mt-5 mb-5 text-center">
                <div class="card shadow-lg">
                    <div class="card-body p-5">
                        <i class="fa fa-check-circle fa-5x text-success mb-4"></i>
                        <h1 class="text-success">Payment Successful!</h1>
                        <p class="lead">Thank you for your payment.</p>
                        
                        <div class="alert alert-info my-4">
                            <h4>Transaction Details</h4>
                            <p><strong>Application:</strong> <t t-esc="admission.application_number"/></p>
                            <p><strong>Amount Paid:</strong> 
                               <span t-esc="admission.application_fee"
                                     t-options="{'widget': 'monetary', 'display_currency': admission.currency_id}"/>
                            </p>
                            <p><strong>Reference:</strong> <t t-esc="transaction.reference"/></p>
                        </div>
                        
                        <div class="mt-4">
                            <a href="/my/applications" class="btn btn-primary btn-lg">
                                <i class="fa fa-list"></i> View My Applications
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </template>
    
</odoo>
```

**Step 3: Add Access Token to Admission (4 hours)**

**Update:** `models/admission_extended.py`

```python
import secrets

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    access_token = fields.Char('Access Token', readonly=True, copy=False)
    
    @api.model
    def create(self, vals):
        # Generate access token for public access
        if not vals.get('access_token'):
            vals['access_token'] = secrets.token_urlsafe(32)
        return super().create(vals)
```

**Step 4: Update Thank You Page with Payment Link (2 hours)**

Already shown above in Step 3.

---

### Phase 2.2: Conditional Fields (32 hours)

#### Step 1: Add Filtering Endpoints (8 hours)

**File:** `controllers/admission_portal.py`

```python
@http.route('/admission/api/courses-by-program', type='json', auth='public')
def get_courses_by_program(self, program_id):
    """Get courses filtered by program"""
    if not program_id:
        courses = request.env['op.course'].sudo().search([])
    else:
        courses = request.env['op.course'].sudo().search([
            ('program_id', '=', int(program_id)),
            ('active', '=', True)
        ])
    
    return [{
        'id': c.id,
        'name': c.name,
        'code': c.code,
    } for c in courses]

@http.route('/admission/api/batches-by-course', type='json', auth='public')
def get_batches_by_course(self, course_id):
    """Get batches filtered by course"""
    batches = request.env['op.batch'].sudo().search([
        ('course_id', '=', int(course_id)),
        ('active', '=', True)
    ])
    
    return [{
        'id': b.id,
        'name': b.name,
        'code': b.code,
    } for b in batches]

@http.route('/admission/api/course-details', type='json', auth='public')
def get_course_details(self, course_id):
    """Get course details including fee"""
    course = request.env['op.course'].sudo().browse(int(course_id))
    
    if not course.exists():
        return {'error': 'Course not found'}
    
    # Get application fee from admission register
    register = request.env['op.admission.register'].sudo().search([
        ('course_id', '=', course.id),
        ('state', '=', 'confirm')
    ], limit=1)
    
    fee = 0
    if register and register.product_id:
        fee = register.product_id.lst_price
    
    return {
        'id': course.id,
        'name': course.name,
        'code': course.code,
        'program_id': course.program_id.id if course.program_id else False,
        'program_name': course.program_id.name if course.program_id else '',
        'application_fee': fee,
        'currency_symbol': request.env.company.currency_id.symbol,
    }
```

#### Step 2: Add Conditional Logic to Wizard (16 hours)

**File:** `views/admission_wizard_templates.xml`

Add to inline JavaScript after existing wizard object:

```javascript
// ========================================
// CONDITIONAL FIELDS LOGIC
// ========================================

wizard.setupConditionalFields = function() {
    console.log('Setting up conditional fields...');
    
    // 1. Program → Course Filtering
    const programSelect = document.getElementById('program_id');
    const courseSelect = document.getElementById('course_id');
    
    if (programSelect) {
        programSelect.addEventListener('change', async function() {
            const programId = this.value;
            
            // Show loading
            courseSelect.disabled = true;
            courseSelect.innerHTML = '<option value="">Loading courses...</option>';
            
            try {
                // Fetch courses for this program
                const response = await fetch('/admission/api/courses-by-program', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {program_id: programId || null}
                    })
                });
                
                const data = await response.json();
                const courses = data.result;
                
                // Populate course dropdown
                courseSelect.innerHTML = '<option value="">Select Course...</option>';
                courses.forEach(course => {
                    const option = document.createElement('option');
                    option.value = course.id;
                    option.textContent = course.name;
                    courseSelect.appendChild(option);
                });
                
                courseSelect.disabled = false;
                
            } catch (error) {
                console.error('Error loading courses:', error);
                courseSelect.innerHTML = '<option value="">Error loading courses</option>';
            }
        });
    }
    
    // 2. Course → Batch Filtering & Fee Display
    if (courseSelect) {
        courseSelect.addEventListener('change', async function() {
            const courseId = this.value;
            const batchSelect = document.getElementById('batch_id');
            
            if (!courseId) {
                batchSelect.innerHTML = '<option value="">Select Batch...</option>';
                hideFeeNotification();
                return;
            }
            
            // Show loading
            batchSelect.disabled = true;
            batchSelect.innerHTML = '<option value="">Loading batches...</option>';
            
            try {
                // Fetch batches
                const batchResponse = await fetch('/admission/api/batches-by-course', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {course_id: courseId}
                    })
                });
                
                const batchData = await batchResponse.json();
                const batches = batchData.result;
                
                // Populate batch dropdown
                batchSelect.innerHTML = '<option value="">Select Batch...</option>';
                batches.forEach(batch => {
                    const option = document.createElement('option');
                    option.value = batch.id;
                    option.textContent = batch.name;
                    batchSelect.appendChild(option);
                });
                
                batchSelect.disabled = false;
                
                // Fetch and display course details (including fee)
                const detailResponse = await fetch('/admission/api/course-details', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {course_id: courseId}
                    })
                });
                
                const detailData = await detailResponse.json();
                const details = detailData.result;
                
                // Show application fee if exists
                if (details.application_fee && details.application_fee > 0) {
                    showFeeNotification(details.application_fee, details.currency_symbol);
                } else {
                    showFeeNotification(0, details.currency_symbol);
                }
                
            } catch (error) {
                console.error('Error loading course details:', error);
                batchSelect.innerHTML = '<option value="">Error loading batches</option>';
            }
        });
    }
    
    // 3. Graduate Programs → Require Previous Education
    if (programSelect) {
        programSelect.addEventListener('change', function() {
            const programName = this.options[this.selectedIndex]?.text.toLowerCase() || '';
            const prevInstituteField = document.getElementById('prev_institute_id');
            const prevInstituteLabel = document.querySelector('label[for="prev_institute_id"]');
            const fieldGroup = document.querySelector('.field-group');
            
            // Check if graduate/master program
            const isGraduate = programName.includes('graduate') || 
                             programName.includes('master') || 
                             programName.includes('phd') || 
                             programName.includes('doctorate');
            
            if (isGraduate && prevInstituteField) {
                // Make previous education required
                prevInstituteField.required = true;
                if (prevInstituteLabel && !prevInstituteLabel.classList.contains('required')) {
                    prevInstituteLabel.classList.add('required');
                }
                if (fieldGroup) {
                    fieldGroup.classList.add('border-warning');
                }
                
                // Show notification
                showGraduateProgramNotice();
            } else if (prevInstituteField) {
                // Make optional
                prevInstituteField.required = false;
                if (prevInstituteLabel) {
                    prevInstituteLabel.classList.remove('required');
                }
                if (fieldGroup) {
                    fieldGroup.classList.remove('border-warning');
                }
                
                hideGraduateProgramNotice();
            }
        });
    }
};

// Helper functions
function showFeeNotification(amount, currency) {
    let notification = document.getElementById('fee-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'fee-notification';
        notification.className = 'alert alert-info mt-3';
        document.querySelector('.wizard-step[data-step="3"]').appendChild(notification);
    }
    
    if (amount > 0) {
        notification.innerHTML = `
            <i class="fa fa-info-circle"></i> 
            <strong>Application Fee:</strong> ${currency}${amount.toFixed(2)}
            <br/><small>Payment will be required after submission</small>
        `;
        notification.style.display = 'block';
    } else {
        notification.innerHTML = `
            <i class="fa fa-check-circle"></i> 
            <strong>No application fee for this course</strong>
        `;
        notification.style.display = 'block';
    }
}

function hideFeeNotification() {
    const notification = document.getElementById('fee-notification');
    if (notification) notification.style.display = 'none';
}

function showGraduateProgramNotice() {
    let notice = document.getElementById('graduate-notice');
    if (!notice) {
        notice = document.createElement('div');
        notice.id = 'graduate-notice';
        notice.className = 'alert alert-warning mt-3';
        const fieldGroup = document.querySelector('.field-group');
        if (fieldGroup) fieldGroup.appendChild(notice);
    }
    notice.innerHTML = `
        <i class="fa fa-exclamation-triangle"></i>
        <strong>Graduate Program Selected:</strong> Previous education information is required.
    `;
    notice.style.display = 'block';
}

function hideGraduateProgramNotice() {
    const notice = document.getElementById('graduate-notice');
    if (notice) notice.style.display = 'none';
}

// Initialize conditional fields after wizard loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (typeof wizard !== 'undefined') {
            wizard.setupConditionalFields();
        }
    }, 500);
});
```

---

## 📊 Revised Implementation Summary

### What We're Building (Phase 2 - REVISED)

✅ **Payment Integration** (48 hours)
1. Extend `op.admission` with payment fields
2. Create invoice generation method (using openeducat_fees pattern)
3. Integrate with Odoo payment providers (Stripe/PayPal from core)
4. Add payment page in portal
5. Add payment success/failure handling
6. Update thank you page with payment link

✅ **Conditional Fields** (32 hours)
1. Program → Course filtering (AJAX)
2. Course → Batch filtering (AJAX)
3. Course → Fee amount display
4. Graduate programs → require previous education
5. Low income → scholarship notification

❌ **Document Upload** - REMOVED (will be in separate module)

---

## 🗂️ Files to Create

**Backend Models:**
1. `models/admission_extended.py` - Payment fields, invoice method

**Controllers:**
2. `controllers/admission_portal.py` (modify) - Payment routes, filtering APIs

**Views:**
3. `views/payment_templates.xml` - Payment page, success page

**Data:**
4. `data/payment_data.xml` - Application fee product

---

## ✅ Revised Checklist

### Payment Integration
- [ ] Add payment fields to op.admission model
- [ ] Add access_token field for public access
- [ ] Implement action_create_invoice() method
- [ ] Add /admission/<id>/payment route
- [ ] Add /admission/<id>/create-payment-transaction route
- [ ] Add /admission/<id>/payment/success route
- [ ] Create payment page template
- [ ] Create payment success template
- [ ] Update thank you page with payment link
- [ ] Create application fee product (data)
- [ ] Test invoice creation
- [ ] Test with manual payment (bank transfer)
- [ ] Test with Stripe (requires Stripe module installed)

### Conditional Fields
- [ ] Add program → course filtering endpoint
- [ ] Add course → batch filtering endpoint
- [ ] Add course details endpoint (with fee)
- [ ] Add conditional logic to wizard JavaScript
- [ ] Implement program change handler
- [ ] Implement course change handler
- [ ] Add fee notification display
- [ ] Add graduate program notice
- [ ] Test all filtering
- [ ] Test on different programs/courses

---

## ⏱️ Revised Time Estimates

| Task | Hours | 
|------|-------|
| Payment model extension | 8h |
| Payment routes | 8h |
| Payment UI templates | 6h |
| Invoice integration | 4h |
| Payment provider integration | 8h |
| Testing payment flow | 14h |
| **Payment Subtotal** | **48h** |
| | |
| Filtering endpoints | 8h |
| Conditional JavaScript | 16h |
| Testing conditional logic | 8h |
| **Conditional Subtotal** | **32h** |
| | |
| **TOTAL Phase 2** | **80h (2 weeks)** |

---

## 💡 Payment Gateway Setup (Admin Task - Not Code)

**After we implement the code, admin needs to:**

```
Step 1: Install Stripe Module
  Settings → Apps → Remove "Apps" filter → Search "Stripe"
  → Install "Payment Provider: Stripe"

Step 2: Get Stripe API Keys
  - Go to stripe.com → Create account
  - Get Publishable Key (pk_test_xxxx)
  - Get Secret Key (sk_test_xxxx)

Step 3: Configure in Odoo
  Website → Configuration → Payment Providers → Stripe
  → State: Enabled
  → Published: ✓
  → Publishable Key: pk_test_xxxxx
  → Secret Key: sk_test_xxxxx
  → Save

Step 4: Test
  - Submit application with fee
  - Click "Pay Online"
  - Should redirect to Stripe payment form
  - Complete test payment
  - Verify payment recorded in Odoo
```

**That's it! No custom payment module needed.**

---

**Ready to implement revised Phase 2?** 🚀

