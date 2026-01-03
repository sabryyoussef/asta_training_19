# 🚀 Phase 2 Implementation Plan - Advanced Features (REVISED)

**Module:** `edafa_website_branding`  
**Phase:** 2 of 4  
**Duration:** 2 weeks (80 hours)  
**Priority:** 🔴 High  
**Created:** November 3, 2025  
**Revised:** November 3, 2025

---

## 📋 Overview

Implement advanced features for the admission portal based on **existing patterns found in the codebase**:
1. ~~**Document Upload**~~ ❌ **REMOVED** - Will be handled by separate deliverable/document module
2. **Payment Integration** ✅ (using Odoo's built-in payment providers + existing `account.move`)
3. **Conditional Fields** ✅ (based on existing `@api.onchange` patterns)

**Note:** Document upload functionality will be implemented later as part of a separate document management module for deliverables and required documents.

---

## 🔍 Codebase Analysis - Existing Patterns

### Pattern 1: Invoice/Payment System (openeducat_fees)

**Found in:** `openeducat_fees/models/student.py`

```python
def get_invoice(self):
    """Create invoice for fee payment process"""
    inv_obj = self.env['account.move']
    # Creates account.move (invoice)
    # Links invoice_id to fee record
    # Returns invoice for payment
```

**Key Insights:**
- ✅ Invoice system already exists (`account.move`)
- ✅ Payment workflow: create invoice → record payment
- ✅ Integration with Odoo Accounting module
- ⚠️ No online payment gateway (Stripe/PayPal) integration yet

**Recommendation:**  
Build on existing invoice system, add Stripe/PayPal for online payment

---

### Pattern 2: Conditional Logic (openeducat_admission)

**Found in:** `openeducat_admission/models/admission.py`

```python
@api.onchange('course_id')
def onchange_course(self):
    # Auto-populate fees_term_id from course
    if self.course_id.fees_term_id:
        self.fees_term_id = self.course_id.fees_term_id
    
    # Auto-set program from course
    if self.course_id.program_id:
        self.program_id = self.course_id.program_id
```

**Found in:** `openeducat_admission/views/admission_register_view.xml`

```xml
<field name="course_id" 
       invisible="admission_base != 'course'"
       required="admission_base == 'course'"/>
<field name="program_id" 
       invisible="admission_base != 'program'"
       required="admission_base == 'program'"/>
```

**Key Insights:**
- ✅ `invisible` attribute for show/hide logic
- ✅ Dynamic `required` based on conditions
- ✅ `@api.onchange` for field dependencies
- ⚠️ XML-based (backend), need JavaScript for portal

**Recommendation:**  
Translate XML `invisible` logic to JavaScript for portal

---

### Pattern 3: Document Management ~~(REMOVED FROM PHASE 2)~~

**Status:** ❌ **Deferred to separate module**

**Reason:**  
User has indicated a separate document upload module will be created for deliverables and required documents. This will be implemented later as part of that dedicated module.

**When implementing later:**
- Refer to `openeducat_admission/static/doc/04_WORKFLOWS.md`
- Use planned `op.admission.document` model structure
- Integrate with admission workflow

**For Phase 2:** We skip document upload and focus on **Payment + Conditional Fields only**

---

## 📝 Implementation Plan (REVISED)

### ❌ Phase 2.1: Document Upload - REMOVED

**Status:** Deferred to separate document management module

**What we're NOT doing in Phase 2:**
- ~~Document upload functionality~~
- ~~Document verification workflow~~
- ~~Document types and validation~~

**Why:** User has a separate plan for comprehensive document management module

---

### ✅ Phase 2.1: Payment Integration (48 hours) - PRIORITY 1

#### Understanding Payment in Odoo

**Where Payment Providers Live:**

```
Odoo Core Modules (Already Installed):
├── odoo/addons/payment/              # Payment framework (BASE)
├── odoo/addons/payment_stripe/       # Stripe integration
├── odoo/addons/payment_paypal/       # PayPal integration
└── odoo/addons/account/              # Invoicing system

Your Module (edafa_website_branding):
├── models/admission_extended.py      # Add payment fields to admission
├── controllers/admission_portal.py   # Payment routes
└── views/payment_templates.xml       # Payment UI
```

**How It Works:**

```
1. User submits application → op.admission created
2. System creates account.move (invoice) for application fee
3. Portal shows payment options:
   a) Download invoice → pay manually → admin marks paid
   b) Pay online → Odoo payment provider → auto-reconciled
4. Payment recorded → admission.payment_status = 'paid'
5. Auto-confirm admission after payment
```

**What You Configure (not code):**
1. Install `payment_stripe` module (Odoo Apps)
2. Configure Stripe API keys (Website → Payment Providers)
3. Done! Payment works automatically

**What We Code:**
1. Add payment fields to `op.admission` model
2. Create invoice using existing `account.move` pattern
3. Add payment page in portal
4. Link payment transaction to admission

---

#### Backend Implementation (24 hours)

**Step 1: Extend Admission Model with Payment Fields**

**File:** `models/admission_document.py` (New)

```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import base64

class OpDocumentType(models.Model):
    """Document types for admission"""
    _name = 'op.document.type'
    _description = 'Admission Document Type'
    _order = 'sequence, name'
    
    name = fields.Char('Document Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    required = fields.Boolean('Required', default=False)
    max_size_mb = fields.Integer('Max Size (MB)', default=10)
    allowed_extensions = fields.Char('Allowed Extensions', 
                                     default='pdf,jpg,jpeg,png',
                                     help='Comma-separated list')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True)
    description = fields.Text('Description')

class OpAdmissionDocument(models.Model):
    """Documents attached to admission application"""
    _name = 'op.admission.document'
    _description = 'Admission Document'
    _order = 'create_date desc'
    
    admission_id = fields.Many2one('op.admission', 'Admission', 
                                   required=True, ondelete='cascade')
    document_type_id = fields.Many2one('op.document.type', 'Document Type', 
                                       required=True)
    document = fields.Binary('Document File', required=True, attachment=True)
    filename = fields.Char('File Name', required=True)
    filesize = fields.Integer('File Size (bytes)', compute='_compute_filesize', store=True)
    mimetype = fields.Char('MIME Type')
    
    state = fields.Selection([
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending', tracking=True)
    
    verified_by = fields.Many2one('res.users', 'Verified By', readonly=True)
    verified_date = fields.Datetime('Verification Date', readonly=True)
    rejection_reason = fields.Text('Rejection Reason')
    notes = fields.Text('Notes')
    
    @api.depends('document')
    def _compute_filesize(self):
        for record in self:
            if record.document:
                record.filesize = len(base64.b64decode(record.document))
            else:
                record.filesize = 0
    
    @api.constrains('document', 'document_type_id')
    def _check_file_size(self):
        for record in self:
            if record.filesize:
                max_size = record.document_type_id.max_size_mb * 1024 * 1024
                if record.filesize > max_size:
                    raise ValidationError(
                        f'File size ({record.filesize / 1024 / 1024:.1f}MB) exceeds maximum '
                        f'allowed size ({record.document_type_id.max_size_mb}MB)'
                    )
    
    def action_verify(self):
        """Mark document as verified"""
        self.write({
            'state': 'verified',
            'verified_by': self.env.user.id,
            'verified_date': fields.Datetime.now(),
        })
    
    def action_reject(self):
        """Mark document as rejected"""
        self.write({'state': 'rejected'})
```

**Step 2: Extend Admission Model**

**File:** `models/admission_extended.py` (New)

```python
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    # Document management
    document_ids = fields.One2many('op.admission.document', 'admission_id', 
                                   string='Documents')
    document_count = fields.Integer('Document Count', 
                                    compute='_compute_document_count')
    required_documents_complete = fields.Boolean('Documents Complete',
                                                 compute='_compute_documents_complete')
    
    # Payment management  
    application_fee = fields.Monetary('Application Fee', 
                                     currency_field='currency_id')
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Payment Status', default='unpaid', tracking=True)
    payment_reference = fields.Char('Payment Reference')
    payment_date = fields.Datetime('Payment Date')
    invoice_id = fields.Many2one('account.move', 'Application Invoice')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id')
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('document_ids', 'document_ids.state')
    def _compute_documents_complete(self):
        for record in self:
            required_types = self.env['op.document.type'].search([
                ('required', '=', True)
            ])
            if not required_types:
                record.required_documents_complete = True
                continue
            
            verified_types = record.document_ids.filtered(
                lambda d: d.state == 'verified'
            ).mapped('document_type_id')
            
            record.required_documents_complete = all(
                req_type in verified_types for req_type in required_types
            )
    
    @api.depends('company_id')
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = record.company_id.currency_id or \
                                self.env.company.currency_id
    
    def action_create_application_invoice(self):
        """Create invoice for application fee (like openeducat_fees pattern)"""
        self.ensure_one()
        
        if self.invoice_id:
            raise ValidationError(_('Invoice already exists for this application'))
        
        if not self.application_fee or self.application_fee <= 0:
            raise ValidationError(_('Application fee must be greater than zero'))
        
        # Get application fee product
        product = self.env.ref('edafa_website_branding.product_application_fee', 
                              raise_if_not_found=False)
        if not product:
            raise ValidationError(
                _('Application fee product not configured. '
                  'Contact administrator.')
            )
        
        # Create invoice (following openeducat_fees pattern)
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id if self.partner_id else \
                         self.env.user.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Application Fee - {self.application_number}',
                'product_id': product.id,
                'quantity': 1.0,
                'price_unit': self.application_fee,
                'account_id': product.property_account_income_id.id,
            })],
        })
        
        self.invoice_id = invoice.id
        self.payment_status = 'unpaid'
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Application Fee Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
```

**Step 3: Create Security & Access**

**File:** `security/ir.model.access.csv`

Add lines:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_op_document_type_public,op.document.type public,model_op_document_type,base.group_public,1,0,0,0
access_op_admission_document_public,op.admission.document public,model_op_admission_document,base.group_public,1,0,1,0
access_op_admission_document_user,op.admission.document user,model_op_admission_document,base.group_user,1,1,1,1
access_op_document_type_user,op.document.type user,model_op_document_type,base.group_user,1,1,1,1
```

**Step 4: Create Initial Data**

**File:** `data/document_types.xml` (New)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- Document Types -->
        <record id="document_type_photo" model="op.document.type">
            <field name="name">Passport Photo</field>
            <field name="code">photo</field>
            <field name="required" eval="True"/>
            <field name="max_size_mb">5</field>
            <field name="allowed_extensions">jpg,jpeg,png</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="document_type_id" model="op.document.type">
            <field name="name">ID Document / Passport</field>
            <field name="code">id_document</field>
            <field name="required" eval="True"/>
            <field name="max_size_mb">10</field>
            <field name="allowed_extensions">pdf,jpg,jpeg,png</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="document_type_certificate" model="op.document.type">
            <field name="name">Academic Certificates</field>
            <field name="code">certificates</field>
            <field name="required" eval="False"/>
            <field name="max_size_mb">20</field>
            <field name="allowed_extensions">pdf</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="document_type_transcript" model="op.document.type">
            <field name="name">Academic Transcripts</field>
            <field name="code">transcript</field>
            <field name="required" eval="False"/>
            <field name="max_size_mb">20</field>
            <field name="allowed_extensions">pdf</field>
            <field name="sequence">40</field>
        </record>
        
        <!-- Application Fee Product -->
        <record id="product_application_fee" model="product.product">
            <field name="name">Application Fee</field>
            <field name="type">service</field>
            <field name="list_price">50.00</field>
            <field name="categ_id" ref="product.product_category_all"/>
            <field name="invoice_policy">order</field>
        </record>
        
    </data>
</odoo>
```

#### Portal Implementation (16 hours)

**Step 5: Add Document Upload Route**

**File:** `controllers/admission_portal.py`

```python
import json

@http.route('/admission/upload-document', type='http', auth='public', 
            methods=['POST'], csrf=True)
def upload_document(self, **post):
    """Handle document upload from portal"""
    try:
        file = post.get('file')
        document_type_id = post.get('document_type_id')
        session_key = post.get('session_key', 'temp_documents')
        
        if not file or not hasattr(file, 'read'):
            return json.dumps({'error': 'No file provided'})
        
        # Read and validate file
        file_data = file.read()
        file_name = file.filename
        file_size = len(file_data)
        
        # Get document type for validation
        doc_type = request.env['op.document.type'].sudo().browse(
            int(document_type_id)
        )
        
        # Validate file size
        max_size = doc_type.max_size_mb * 1024 * 1024
        if file_size > max_size:
            return json.dumps({
                'error': f'File too large. Maximum {doc_type.max_size_mb}MB allowed'
            })
        
        # Validate file extension
        ext = file_name.split('.')[-1].lower()
        allowed = doc_type.allowed_extensions.split(',')
        if ext not in allowed:
            return json.dumps({
                'error': f'Invalid file type. Allowed: {doc_type.allowed_extensions}'
            })
        
        # Store in session temporarily (will attach to admission on submit)
        temp_docs = request.session.get(session_key, [])
        temp_docs.append({
            'document_type_id': int(document_type_id),
            'document': base64.b64encode(file_data).decode(),
            'filename': file_name,
            'filesize': file_size,
        })
        request.session[session_key] = temp_docs
        
        return json.dumps({
            'success': True,
            'filename': file_name,
            'filesize': file_size,
            'document_type': doc_type.name,
        })
        
    except Exception as e:
        _logger.exception("Document upload error")
        return json.dumps({'error': str(e)})

@http.route('/admission/delete-temp-document', type='json', auth='public')
def delete_temp_document(self, index, session_key='temp_documents'):
    """Delete temporary document before submission"""
    try:
        temp_docs = request.session.get(session_key, [])
        if 0 <= index < len(temp_docs):
            temp_docs.pop(index)
            request.session[session_key] = temp_docs
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}
```

**Step 6: Update Submission to Handle Documents**

**Modify:** `controllers/admission_portal.py` → `admission_submit()`

```python
def admission_submit(self, **post):
    # ... existing code to create admission ...
    
    admission = request.env['op.admission'].sudo().create(admission_vals)
    
    # Attach uploaded documents
    temp_docs = request.session.get('temp_documents', [])
    for doc_data in temp_docs:
        request.env['op.admission.document'].sudo().create({
            'admission_id': admission.id,
            'document_type_id': doc_data['document_type_id'],
            'document': doc_data['document'],
            'filename': doc_data['filename'],
            'state': 'pending',
        })
    
    # Clear temp documents from session
    request.session.pop('temp_documents', None)
    
    # ... rest of submission code ...
```

**Step 7: Add Document Upload UI to Wizard**

**File:** `views/admission_wizard_templates.xml`

Add new step 4.5 (between Background and Review):

```xml
<!-- Step 4.5: Document Upload -->
<div class="wizard-step" data-step="5">
    <div class="step-header">
        <h3>Upload Documents</h3>
        <p>Upload required documents to complete your application</p>
    </div>
    
    <t t-foreach="document_types" t-as="doc_type">
        <div class="document-upload-section mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5>
                    <t t-esc="doc_type.name"/>
                    <span t-if="doc_type.required" class="text-danger">*</span>
                    <span t-else="" class="text-muted">(Optional)</span>
                </h5>
                <small class="text-muted">
                    Max <t t-esc="doc_type.max_size_mb"/>MB | 
                    <t t-esc="doc_type.allowed_extensions.upper()"/>
                </small>
            </div>
            
            <div class="upload-area" 
                 t-att-data-document-type="doc_type.id"
                 t-att-data-required="doc_type.required">
                <input type="file" 
                       t-att-id="'doc_' + str(doc_type.id)"
                       class="document-input"
                       t-att-accept="'.' + doc_type.allowed_extensions.replace(',', ',.')"/>
                <div class="upload-placeholder">
                    <i class="fa fa-cloud-upload fa-3x"></i>
                    <p>Drag & drop file here or click to browse</p>
                    <p class="text-muted"><small><t t-esc="doc_type.description"/></small></p>
                </div>
                <div class="upload-preview" style="display: none;">
                    <div class="file-info">
                        <i class="fa fa-file-pdf-o fa-2x"></i>
                        <div class="file-details">
                            <div class="file-name"></div>
                            <div class="file-size text-muted"></div>
                        </div>
                        <button type="button" class="btn btn-sm btn-danger delete-file">
                            <i class="fa fa-trash"></i>
                        </button>
                    </div>
                    <div class="upload-progress" style="display: none;">
                        <div class="progress">
                            <div class="progress-bar" role="progressbar"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</div>
```

**Step 8: Add Document Upload JavaScript**

**File:** `static/src/js/document_uploader.js` (New)

```javascript
/** @odoo-module **/

// Simple document uploader
document.addEventListener('DOMContentLoaded', function() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        const input = area.querySelector('.document-input');
        const placeholder = area.querySelector('.upload-placeholder');
        const preview = area.querySelector('.upload-preview');
        
        // Click to upload
        placeholder.addEventListener('click', () => input.click());
        
        // Drag & drop
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('drag-over');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('drag-over');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length) {
                input.files = files;
                handleFileUpload(input, area);
            }
        });
        
        // File input change
        input.addEventListener('change', () => {
            handleFileUpload(input, area);
        });
        
        // Delete button
        const deleteBtn = area.querySelector('.delete-file');
        deleteBtn.addEventListener('click', () => {
            input.value = '';
            placeholder.style.display = 'block';
            preview.style.display = 'none';
        });
    });
    
    async function handleFileUpload(input, area) {
        const file = input.files[0];
        if (!file) return;
        
        const documentTypeId = area.dataset.documentType;
        const placeholder = area.querySelector('.upload-placeholder');
        const preview = area.querySelector('.upload-preview');
        const progressBar = preview.querySelector('.progress-bar');
        const progressContainer = preview.querySelector('.upload-progress');
        
        // Show preview
        placeholder.style.display = 'none';
        preview.style.display = 'block';
        progressContainer.style.display = 'block';
        
        // Update file info
        preview.querySelector('.file-name').textContent = file.name;
        preview.querySelector('.file-size').textContent = 
            formatFileSize(file.size);
        
        // Upload file
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type_id', documentTypeId);
        formData.append('session_key', 'temp_documents');
        
        try {
            const xhr = new XMLHttpRequest();
            
            // Progress tracking
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressBar.style.width = percent + '%';
                    progressBar.textContent = Math.round(percent) + '%';
                }
            });
            
            xhr.addEventListener('load', () => {
                progressContainer.style.display = 'none';
                const response = JSON.parse(xhr.responseText);
                
                if (response.success) {
                    area.classList.add('upload-success');
                } else {
                    alert('Upload failed: ' + response.error);
                    input.value = '';
                    placeholder.style.display = 'block';
                    preview.style.display = 'none';
                }
            });
            
            xhr.open('POST', '/admission/upload-document');
            xhr.send(formData);
            
        } catch (error) {
            console.error('Upload error:', error);
            alert('Upload failed. Please try again.');
        }
    }
    
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1024 / 1024).toFixed(1) + ' MB';
    }
});
```

---

### Phase 2.2: Payment Integration (48 hours)

#### Backend Implementation (32 hours)

**Step 1: Install Stripe Module** (Optional - if not using Odoo's built-in)

For simple integration, use Odoo's existing `account.move` invoice + manual payment.

**Step 2: Add Payment Routes**

**File:** `controllers/payment_handler.py` (New)

```python
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class AdmissionPaymentController(http.Controller):
    
    @http.route('/admission/payment/<int:admission_id>', type='http', 
                auth='public', website=True)
    def admission_payment_page(self, admission_id, **kwargs):
        """Display payment page for application fee"""
        admission = request.env['op.admission'].sudo().browse(admission_id)
        
        if not admission.exists():
            return request.render('website.404')
        
        # Create invoice if not exists
        if not admission.invoice_id and admission.application_fee > 0:
            admission.action_create_application_invoice()
        
        return request.render('edafa_website_branding.admission_payment_page', {
            'admission': admission,
            'invoice': admission.invoice_id,
            'page_name': 'payment',
        })
    
    @http.route('/admission/payment/success', type='http', 
                auth='public', website=True)
    def payment_success(self, **kwargs):
        """Payment success callback"""
        payment_intent_id = kwargs.get('payment_intent')
        admission_id = kwargs.get('admission_id')
        
        if admission_id:
            admission = request.env['op.admission'].sudo().browse(int(admission_id))
            admission.write({
                'payment_status': 'paid',
                'payment_reference': payment_intent_id,
                'payment_date': fields.Datetime.now(),
                'state': 'confirm',  # Auto-confirm after payment
            })
        
        return request.render('edafa_website_branding.payment_success', {
            'admission_id': admission_id,
        })
```

**Step 3: Add Payment UI**

**File:** `views/payment_templates.xml` (New)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <template id="admission_payment_page" name="Application Fee Payment">
        <t t-call="website.layout">
            <div class="container mt-5 mb-5">
                <div class="row">
                    <div class="col-md-8 offset-md-2">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h4><i class="fa fa-credit-card"></i> Application Fee Payment</h4>
                            </div>
                            <div class="card-body">
                                <h5>Application: <t t-esc="admission.application_number"/></h5>
                                <p><strong>Applicant:</strong> <t t-esc="admission.name"/></p>
                                <p><strong>Course:</strong> <t t-esc="admission.course_id.name"/></p>
                                
                                <div class="alert alert-info">
                                    <h4>Amount Due: <span t-esc="admission.application_fee" 
                                                          t-options="{'widget': 'monetary', 'display_currency': admission.currency_id}"/></h4>
                                </div>
                                
                                <!-- Payment Options -->
                                <div class="payment-methods">
                                    <h5>Select Payment Method:</h5>
                                    
                                    <!-- Option 1: Manual/Bank Transfer -->
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <h6><i class="fa fa-university"></i> Bank Transfer</h6>
                                            <p>Download invoice and pay via bank transfer</p>
                                            <a t-if="invoice" t-attf-href="/my/invoices/#{invoice.id}" 
                                               class="btn btn-secondary">
                                                <i class="fa fa-download"></i> Download Invoice
                                            </a>
                                        </div>
                                    </div>
                                    
                                    <!-- Option 2: Online Payment (Future - Stripe) -->
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <h6><i class="fa fa-credit-card"></i> Credit/Debit Card</h6>
                                            <p class="text-muted">Coming soon - Stripe integration</p>
                                            <button class="btn btn-primary" disabled="">
                                                <i class="fa fa-lock"></i> Pay Online (Coming Soon)
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </template>
    
</odoo>
```

---

### Phase 2.3: Conditional Fields (32 hours)

#### Implementation Based on Existing Patterns

**Step 1: Analyze Conditional Requirements**

From existing `@api.onchange` patterns:
```python
# When course changes → update program, fees_term, batch
# When program changes → filter courses  
# When register changes → update fees
```

**Frontend Equivalent:**
```javascript
// When course selected → load related batches
// When course selected → show course-specific fields
// When program selected → filter courses by program
```

**Step 2: Add Conditional Logic to Wizard**

**File:** Inline JavaScript in `admission_wizard_templates.xml`

```javascript
// Add to wizard object after existing code

wizard.setupConditionalFields = function() {
    // 1. Program → Course filtering
    document.getElementById('program_id').addEventListener('change', function() {
        const programId = this.value;
        const courseSelect = document.getElementById('course_id');
        
        if (!programId) {
            // Show all courses
            courseSelect.querySelectorAll('option').forEach(opt => {
                if (opt.value) opt.style.display = 'block';
            });
            return;
        }
        
        // Filter courses by program (AJAX call)
        fetch('/admission/get-courses-by-program?program_id=' + programId)
            .then(r => r.json())
            .then(courses => {
                courseSelect.innerHTML = '<option value="">Select Course...</option>';
                courses.forEach(course => {
                    courseSelect.innerHTML += 
                        `<option value="${course.id}">${course.name}</option>`;
                });
            });
    });
    
    // 2. Course → Batch filtering & fee display
    document.getElementById('course_id').addEventListener('change', function() {
        const courseId = this.value;
        const batchSelect = document.getElementById('batch_id');
        
        if (!courseId) {
            batchSelect.innerHTML = '<option value="">Select Batch...</option>';
            return;
        }
        
        // Load batches for course (AJAX)
        fetch('/admission/get-batches-by-course?course_id=' + courseId)
            .then(r => r.json())
            .then(batches => {
                batchSelect.innerHTML = '<option value="">Select Batch...</option>';
                batches.forEach(batch => {
                    batchSelect.innerHTML += 
                        `<option value="${batch.id}">${batch.name}</option>`;
                });
            });
        
        // Load and display application fee (AJAX)
        fetch('/admission/get-course-fee?course_id=' + courseId)
            .then(r => r.json())
            .then(data => {
                if (data.fee > 0) {
                    showFeeNotification(data.fee, data.currency);
                }
            });
    });
    
    // 3. Graduate programs → require previous degree
    document.getElementById('program_id').addEventListener('change', function() {
        const programName = this.options[this.selectedIndex].text.toLowerCase();
        const prevEduSection = document.querySelector('.field-group');
        const prevInstituteField = document.getElementById('prev_institute_id');
        
        if (programName.includes('graduate') || programName.includes('master') || 
            programName.includes('phd') || programName.includes('doctorate')) {
            // Make previous education required
            prevInstituteField.required = true;
            prevEduSection.classList.add('required-section');
            
            // Add visual indicator
            const label = document.querySelector('label[for="prev_institute_id"]');
            if (!label.classList.contains('required')) {
                label.classList.add('required');
            }
        } else {
            // Make optional
            prevInstituteField.required = false;
            prevEduSection.classList.remove('required-section');
        }
    });
    
    // 4. Family income → show scholarship info
    document.getElementById('family_income').addEventListener('blur', function() {
        const income = parseFloat(this.value);
        if (!isNaN(income) && income < 30000) {
            showScholarshipNotification();
        }
    });
};

// Call setup after wizard loads
wizard.setupConditionalFields();
```

**Step 3: Add Backend Endpoints for Filtering**

**File:** `controllers/admission_portal.py`

```python
@http.route('/admission/get-courses-by-program', type='json', auth='public')
def get_courses_by_program(self, program_id):
    """Get courses filtered by program"""
    courses = request.env['op.course'].sudo().search([
        ('program_id', '=', int(program_id))
    ])
    return [{
        'id': c.id,
        'name': c.name,
        'code': c.code,
    } for c in courses]

@http.route('/admission/get-batches-by-course', type='json', auth='public')
def get_batches_by_course(self, course_id):
    """Get batches filtered by course"""
    batches = request.env['op.batch'].sudo().search([
        ('course_id', '=', int(course_id))
    ])
    return [{
        'id': b.id,
        'name': b.name,
        'code': b.code,
    } for b in batches]

@http.route('/admission/get-course-fee', type='json', auth='public')
def get_course_fee(self, course_id):
    """Get application fee for course"""
    course = request.env['op.course'].sudo().browse(int(course_id))
    
    # Get fee from admission register or default
    register = request.env['op.admission.register'].sudo().search([
        ('course_id', '=', int(course_id)),
        ('state', '=', 'confirm')
    ], limit=1)
    
    fee = 0
    if register and register.product_id:
        fee = register.product_id.lst_price
    
    return {
        'fee': fee,
        'currency': request.env.company.currency_id.symbol,
    }
```

---

## 📊 Implementation Summary

### Files to Create

**Backend:**
1. `models/admission_document.py` - Document models
2. `models/admission_extended.py` - Payment & document fields
3. `controllers/payment_handler.py` - Payment routes
4. `data/document_types.xml` - Document type seed data
5. `views/payment_templates.xml` - Payment UI

**Frontend:**
6. `static/src/js/document_uploader.js` - Upload functionality
7. `static/src/css/document_upload.css` - Upload UI styles

### Files to Modify

1. `controllers/admission_portal.py` - Add filtering endpoints
2. `views/admission_wizard_templates.xml` - Add document upload step
3. `__manifest__.py` - Register new models, data, assets
4. `models/__init__.py` - Import new models
5. `controllers/__init__.py` - Import payment controller

### Database Changes

**New Tables:**
- `op_document_type` (4 records initially)
- `op_admission_document` (user uploads)

**Modified Tables:**
- `op_admission` (add payment fields, document count)

---

## ✅ Implementation Checklist

### Phase 2.1: Document Upload
- [ ] Create `op.document.type` model
- [ ] Create `op.admission.document` model
- [ ] Add document fields to `op.admission`
- [ ] Create document type data (4 types)
- [ ] Add `/admission/upload-document` route
- [ ] Update `/admission/submit` to handle documents
- [ ] Add document upload step to wizard template
- [ ] Create document uploader JavaScript
- [ ] Add drag & drop CSS styling
- [ ] Test upload functionality
- [ ] Test file size/type validation
- [ ] Test document viewing in backend

### Phase 2.2: Payment Integration
- [ ] Add payment fields to `op.admission`
- [ ] Create application fee product
- [ ] Implement `action_create_application_invoice()`
- [ ] Add payment routes (payment page, success)
- [ ] Create payment page template
- [ ] Add payment link to thank you page
- [ ] Test invoice creation
- [ ] Test manual payment recording
- [ ] (Optional) Integrate Stripe API

### Phase 2.3: Conditional Fields
- [ ] Add `setupConditionalFields()` to wizard
- [ ] Implement program → course filtering
- [ ] Implement course → batch filtering
- [ ] Add course fee display
- [ ] Add graduate program → require previous education
- [ ] Add low income → scholarship notification
- [ ] Create filtering endpoints (3 routes)
- [ ] Test all conditional logic
- [ ] Test on different programs/courses

---

## 🎯 Success Criteria

**Document Upload:**
- ✅ Users can upload up to 4 document types
- ✅ Drag & drop works
- ✅ File size/type validated
- ✅ Progress bar shows during upload
- ✅ Documents attached to admission record
- ✅ Admins can verify/reject documents

**Payment Integration:**
- ✅ Application fee displayed based on course
- ✅ Invoice created automatically
- ✅ Payment page accessible
- ✅ Manual payment can be recorded
- ✅ Payment status tracked

**Conditional Fields:**
- ✅ Course list filters by program selection
- ✅ Batch list filters by course selection
- ✅ Fee amount shows when course selected
- ✅ Graduate programs require previous education
- ✅ Low income shows scholarship info

---

## ⏱️ Time Estimates

| Task | Hours | Dependencies |
|------|-------|--------------|
| Document models (backend) | 16h | None |
| Document upload (frontend) | 12h | Document models |
| Document routes & handling | 12h | Document models |
| Payment models & logic | 16h | None |
| Payment UI & templates | 8h | Payment models |
| Payment routes | 8h | Payment models |
| Conditional field logic | 16h | None |
| Filter endpoints | 8h | None |
| Testing & debugging | 24h | All above |
| **Total** | **120h** | **3 weeks** |

---

**Ready to implement? Let me know and I'll start building Phase 2!** 🚀

