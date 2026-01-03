# Portal Integration Documentation

## Overview

This document provides comprehensive information about the portal integration in the OpenEduCat Admission module, explaining how students can apply online, track their applications, and interact with the admission system through the Odoo web portal.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Portal Architecture](#portal-architecture)
3. [Student Portal Access](#student-portal-access)
4. [Online Application Process](#online-application-process)
5. [Portal Features](#portal-features)
6. [Portal Controllers](#portal-controllers)
7. [Portal Templates](#portal-templates)
8. [Security & Access Control](#security--access-control)
9. [Portal Customization](#portal-customization)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Portal Integration?

Portal integration enables students to interact with the admission system through a web-based interface without requiring full Odoo backend access. Students can:

- Submit admission applications online
- Upload required documents
- Track application status in real-time
- Communicate with admission staff
- Make online payments
- Download admission letters and receipts

### Benefits

**For Students:**
- 24/7 access to application system
- Convenient online submission
- Real-time status tracking
- Reduced paperwork
- Faster processing

**For Institution:**
- Reduced manual data entry
- Better data accuracy
- Automated workflows
- Improved applicant experience
- Cost savings

---

## Portal Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│           Student Browser                    │
└──────────────────┬──────────────────────────┘
                   │ HTTPS
┌──────────────────▼──────────────────────────┐
│         Odoo Portal Frontend                 │
│  ┌────────────────────────────────────┐    │
│  │  Portal Templates (QWeb)           │    │
│  │  - Application Form                │    │
│  │  - Document Upload                 │    │
│  │  - Status Dashboard                │    │
│  └────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      Portal Controllers (Python)             │
│  ┌────────────────────────────────────┐    │
│  │  AdmissionPortal Controller        │    │
│  │  - Route Handlers                  │    │
│  │  - Request Processing              │    │
│  │  - Response Rendering              │    │
│  └────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Odoo Backend (ORM)                   │
│  ┌────────────────────────────────────┐    │
│  │  op.admission Model                │    │
│  │  - Business Logic                  │    │
│  │  - Validation                      │    │
│  │  - Data Persistence                │    │
│  └────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           PostgreSQL Database                │
└──────────────────────────────────────────────┘
```

### Data Flow

1. **Student Request** → Portal frontend
2. **Portal Frontend** → Portal controller
3. **Portal Controller** → Odoo ORM (models)
4. **Odoo ORM** → Database
5. **Database** → Odoo ORM
6. **Odoo ORM** → Portal controller
7. **Portal Controller** → Portal template
8. **Portal Template** → Student browser

---

## Student Portal Access

### Creating Portal Access

#### Method 1: Automatic (During Admission)

When an admission is processed, the system can automatically create a portal user:

```python
# In op.admission model
enable_create_student_user = self.env['ir.config_parameter'].get_param(
    'openeducat_admission.enable_create_student_user')

if enable_create_student_user:
    student_user = self.env['res.users'].create({
        'name': student.name,
        'login': student.email,
        'is_student': True,
        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
    })
```

**Configuration:**
- Navigate to: Settings → General Settings → Admission
- Enable: "Create Student User"

#### Method 2: Manual Portal Access Grant

1. Navigate to the admission record
2. Click on the partner (Contact)
3. Click "Grant Portal Access"
4. System sends invitation email

#### Method 3: Self-Registration (Website)

If website module is installed:
1. Student visits registration page
2. Fills registration form
3. Receives confirmation email
4. Activates account via email link

### Portal Login

**URL**: `https://your-domain.com/web/login`

**Credentials:**
- **Username**: Email address or application number
- **Password**: Set during registration or sent via email

### Password Management

**Reset Password:**
1. Click "Reset Password" on login page
2. Enter email address
3. Receive reset link via email
4. Set new password

---

## Online Application Process

### Step-by-Step Application Flow

#### Step 1: Access Portal

```
URL: https://your-domain.com/my/admissions
```

Student logs in and sees their admission dashboard.

#### Step 2: Start New Application

1. Click "Apply for Admission" button
2. Select admission register (program/course)
3. System validates eligibility criteria

#### Step 3: Fill Personal Information

**Required Fields:**
- Title (Mr., Ms., etc.)
- First Name
- Middle Name (optional)
- Last Name
- Date of Birth
- Gender
- Email
- Phone/Mobile

**Address Information:**
- Street Address
- City
- State/Province
- Country
- Postal Code

#### Step 4: Educational Background

- Previous Institution
- Previous Course/Program
- Previous Result/Grade
- Graduation Year

#### Step 5: Family Information

- Family Business
- Family Income
- Emergency Contact Details
- Guardian Information (if minor)

#### Step 6: Program/Course Selection

- Select Program (if program-based admission)
- Select Course
- Select Batch (if available)
- View fee information

#### Step 7: Document Upload

Upload required documents:
- Passport-size photograph
- Identity proof (ID card, passport)
- Birth certificate
- Academic certificates
- Previous transcripts
- Other required documents

**Document Requirements:**
- Format: PDF, JPG, PNG
- Maximum size: 5MB per file
- Clear and readable scans

#### Step 8: Review and Submit

1. Review all entered information
2. Preview application
3. Accept terms and conditions
4. Submit application

#### Step 9: Confirmation

- Receive application number
- Get confirmation email
- View application status

---

## Portal Features

### 1. Admission Dashboard

**URL**: `/my/admissions`

**Features:**
- List of all applications
- Application status indicators
- Quick actions (view, edit, cancel)
- Filter and search capabilities
- Application statistics

**Status Indicators:**
```python
STATE_COLORS = {
    'draft': 'info',      # Blue
    'submit': 'primary',  # Dark blue
    'confirm': 'warning', # Yellow
    'admission': 'success', # Green
    'done': 'success',    # Green
    'reject': 'danger',   # Red
    'cancel': 'secondary' # Gray
}
```

### 2. Application Detail View

**URL**: `/my/admission/<admission_id>`

**Sections:**

#### Personal Information Tab
- View all personal details
- Edit if in draft state
- View submission history

#### Documents Tab
- List of uploaded documents
- Document verification status
- Upload additional documents
- Download uploaded documents

#### Status Timeline
- Visual timeline of application progress
- State change history
- Timestamps for each state
- Comments from reviewers

#### Communication Center
- Message thread (chatter)
- Send messages to admission staff
- Receive notifications
- View communication history

#### Payment Information
- Fee amount
- Payment status
- Payment due date
- Make payment button
- Payment history

### 3. Document Management

**Upload Documents:**
```html
<form enctype="multipart/form-data">
    <input type="file" name="document" accept=".pdf,.jpg,.png"/>
    <select name="document_type_id">
        <option value="1">Photograph</option>
        <option value="2">ID Proof</option>
        <option value="3">Academic Certificate</option>
    </select>
    <button type="submit">Upload</button>
</form>
```

**Document Status:**
- 🟡 Pending Verification
- 🟢 Verified
- 🔴 Rejected (with reason)

### 4. Application Tracking

**Real-time Status Updates:**
- Email notifications on state changes
- In-portal notification badges
- SMS alerts (if configured)

**Status Descriptions:**

| Status | Description | Next Action |
|--------|-------------|-------------|
| Draft | Application not submitted | Complete and submit |
| Submitted | Under review | Wait for verification |
| Document Verification | Documents being checked | Upload missing docs |
| Confirmed | Admission approved | Make payment |
| Admission | Ready for enrollment | Wait for enrollment |
| Done | Enrolled as student | Access student portal |
| Rejected | Application not approved | View rejection reason |

### 5. Payment Processing

**Payment Flow:**
1. View fee amount
2. Click "Make Payment"
3. Choose payment method
4. Complete payment
5. Receive payment confirmation
6. Download receipt

**Payment Methods:**
- Online payment gateway (Stripe, PayPal)
- Bank transfer (with reference number)
- Cash payment at office (generate voucher)

---

## Portal Controllers

### Controller Structure

```python
# controllers/portal.py
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo.exceptions import AccessError, MissingError

class AdmissionPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        """Add admission count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        if 'admission_count' in counters:
            admission_count = request.env['op.admission'].search_count([])
            values['admission_count'] = admission_count
        return values
    
    @http.route(['/my/admissions', '/my/admissions/page/<int:page>'], 
                type='http', auth="user", website=True)
    def portal_my_admissions(self, page=1, date_begin=None, date_end=None, 
                             sortby=None, filterby=None, **kw):
        """List all admissions for current user"""
        values = self._prepare_portal_layout_values()
        Admission = request.env['op.admission']
        
        domain = []
        
        # Search and filter logic
        searchbar_sortings = {
            'date': {'label': 'Application Date', 'order': 'application_date desc'},
            'name': {'label': 'Name', 'order': 'name'},
            'state': {'label': 'Status', 'order': 'state'},
        }
        
        searchbar_filters = {
            'all': {'label': 'All', 'domain': []},
            'draft': {'label': 'Draft', 'domain': [('state', '=', 'draft')]},
            'submitted': {'label': 'Submitted', 'domain': [('state', '=', 'submit')]},
            'done': {'label': 'Enrolled', 'domain': [('state', '=', 'done')]},
        }
        
        # Default sort and filter
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'
        
        order = searchbar_sortings[sortby]['order']
        domain += searchbar_filters[filterby]['domain']
        
        # Count for pager
        admission_count = Admission.search_count(domain)
        
        # Pager
        pager_values = pager(
            url="/my/admissions",
            total=admission_count,
            page=page,
            step=self._items_per_page,
            url_args={'sortby': sortby, 'filterby': filterby},
        )
        
        # Get admissions
        admissions = Admission.search(
            domain, 
            order=order, 
            limit=self._items_per_page, 
            offset=pager_values['offset']
        )
        
        values.update({
            'admissions': admissions,
            'page_name': 'admission',
            'pager': pager_values,
            'default_url': '/my/admissions',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
        })
        
        return request.render("openeducat_admission.portal_my_admissions", values)
    
    @http.route(['/my/admission/<int:admission_id>'], 
                type='http', auth="user", website=True)
    def portal_admission_detail(self, admission_id, access_token=None, **kw):
        """View admission details"""
        try:
            admission_sudo = self._document_check_access(
                'op.admission', admission_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'admission': admission_sudo,
            'page_name': 'admission',
        }
        
        return request.render("openeducat_admission.portal_admission_detail", values)
    
    @http.route(['/my/admission/apply'], 
                type='http', auth="user", website=True)
    def portal_admission_apply(self, **kw):
        """Create new admission application"""
        values = {}
        
        # Get active admission registers
        registers = request.env['op.admission.register'].search([
            ('state', 'in', ['application', 'admission']),
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today()),
        ])
        
        values.update({
            'registers': registers,
            'page_name': 'admission_apply',
        })
        
        return request.render("openeducat_admission.portal_admission_apply", values)
    
    @http.route(['/my/admission/apply/submit'], 
                type='http', auth="user", website=True, methods=['POST'])
    def portal_admission_submit(self, **post):
        """Submit admission application"""
        Admission = request.env['op.admission']
        
        # Prepare values
        values = {
            'name': post.get('name'),
            'first_name': post.get('first_name'),
            'middle_name': post.get('middle_name'),
            'last_name': post.get('last_name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'mobile': post.get('mobile'),
            'birth_date': post.get('birth_date'),
            'gender': post.get('gender'),
            'register_id': int(post.get('register_id')),
            'course_id': int(post.get('course_id')) if post.get('course_id') else False,
            'state': 'draft',
        }
        
        # Create admission
        admission = Admission.create(values)
        
        return request.redirect('/my/admission/%s' % admission.id)
    
    @http.route(['/my/admission/<int:admission_id>/upload'], 
                type='http', auth="user", website=True, methods=['POST'])
    def portal_admission_upload_document(self, admission_id, **post):
        """Upload document for admission"""
        admission = request.env['op.admission'].browse(admission_id)
        
        # Check access
        if not admission.exists() or admission.partner_id != request.env.user.partner_id:
            return request.redirect('/my')
        
        # Handle file upload
        document_file = post.get('document')
        document_type_id = int(post.get('document_type_id'))
        
        if document_file:
            request.env['op.admission.document'].create({
                'admission_id': admission_id,
                'document_type_id': document_type_id,
                'document': base64.b64encode(document_file.read()),
                'filename': document_file.filename,
                'state': 'pending',
            })
        
        return request.redirect('/my/admission/%s' % admission_id)
```

### Route Definitions

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/my/admissions` | GET | user | List admissions |
| `/my/admission/<id>` | GET | user | View admission |
| `/my/admission/apply` | GET | user | Application form |
| `/my/admission/apply/submit` | POST | user | Submit application |
| `/my/admission/<id>/upload` | POST | user | Upload document |
| `/my/admission/<id>/cancel` | POST | user | Cancel application |

---

## Portal Templates

### Template Structure

```xml
<!-- views/portal_templates.xml -->
<odoo>
    <!-- Admission List Template -->
    <template id="portal_my_admissions" name="My Admissions">
        <t t-call="portal.portal_layout">
            <t t-set="breadcrumbs_searchbar" t-value="True"/>
            
            <t t-call="portal.portal_searchbar">
                <t t-set="title">Admissions</t>
            </t>
            
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h3>My Admission Applications</h3>
                        
                        <t t-if="not admissions">
                            <div class="alert alert-info">
                                No admission applications found.
                                <a href="/my/admission/apply" class="btn btn-primary">
                                    Apply Now
                                </a>
                            </div>
                        </t>
                        
                        <t t-if="admissions">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Application #</th>
                                        <th>Name</th>
                                        <th>Program/Course</th>
                                        <th>Date</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <t t-foreach="admissions" t-as="admission">
                                        <tr>
                                            <td>
                                                <a t-attf-href="/my/admission/#{admission.id}">
                                                    <t t-esc="admission.application_number"/>
                                                </a>
                                            </td>
                                            <td><t t-esc="admission.name"/></td>
                                            <td><t t-esc="admission.course_id.name"/></td>
                                            <td><t t-esc="admission.application_date"/></td>
                                            <td>
                                                <span t-attf-class="badge badge-{{admission.state}}">
                                                    <t t-esc="admission.state"/>
                                                </span>
                                            </td>
                                            <td>
                                                <a t-attf-href="/my/admission/#{admission.id}" 
                                                   class="btn btn-sm btn-primary">
                                                    View
                                                </a>
                                            </td>
                                        </tr>
                                    </t>
                                </tbody>
                            </table>
                            
                            <!-- Pager -->
                            <div t-if="pager" class="o_portal_pager text-center">
                                <t t-call="portal.pager"/>
                            </div>
                        </t>
                    </div>
                </div>
            </div>
        </t>
    </template>
    
    <!-- Admission Detail Template -->
    <template id="portal_admission_detail" name="Admission Detail">
        <t t-call="portal.portal_layout">
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h3>
                            Admission Application: 
                            <t t-esc="admission.application_number"/>
                        </h3>
                        
                        <!-- Status Badge -->
                        <div class="mb-3">
                            <span t-attf-class="badge badge-{{admission.state}}">
                                <t t-esc="admission.state"/>
                            </span>
                        </div>
                        
                        <!-- Tabs -->
                        <ul class="nav nav-tabs" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link active" data-toggle="tab" href="#details">
                                    Details
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-toggle="tab" href="#documents">
                                    Documents
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-toggle="tab" href="#timeline">
                                    Timeline
                                </a>
                            </li>
                        </ul>
                        
                        <!-- Tab Content -->
                        <div class="tab-content mt-3">
                            <!-- Details Tab -->
                            <div id="details" class="tab-pane active">
                                <h4>Personal Information</h4>
                                <table class="table">
                                    <tr>
                                        <th>Name:</th>
                                        <td><t t-esc="admission.name"/></td>
                                    </tr>
                                    <tr>
                                        <th>Email:</th>
                                        <td><t t-esc="admission.email"/></td>
                                    </tr>
                                    <tr>
                                        <th>Phone:</th>
                                        <td><t t-esc="admission.phone"/></td>
                                    </tr>
                                    <tr>
                                        <th>Date of Birth:</th>
                                        <td><t t-esc="admission.birth_date"/></td>
                                    </tr>
                                </table>
                                
                                <h4>Program Information</h4>
                                <table class="table">
                                    <tr>
                                        <th>Program:</th>
                                        <td><t t-esc="admission.program_id.name"/></td>
                                    </tr>
                                    <tr>
                                        <th>Course:</th>
                                        <td><t t-esc="admission.course_id.name"/></td>
                                    </tr>
                                    <tr>
                                        <th>Fees:</th>
                                        <td><t t-esc="admission.fees"/></td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Documents Tab -->
                            <div id="documents" class="tab-pane">
                                <h4>Uploaded Documents</h4>
                                
                                <!-- Upload Form -->
                                <form method="post" 
                                      t-attf-action="/my/admission/#{admission.id}/upload"
                                      enctype="multipart/form-data">
                                    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
                                    
                                    <div class="form-group">
                                        <label>Document Type</label>
                                        <select name="document_type_id" class="form-control" required="1">
                                            <option value="">Select...</option>
                                            <!-- Document types -->
                                        </select>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label>File</label>
                                        <input type="file" name="document" class="form-control" required="1"/>
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary">
                                        Upload Document
                                    </button>
                                </form>
                                
                                <!-- Document List -->
                                <table class="table mt-3">
                                    <thead>
                                        <tr>
                                            <th>Document Type</th>
                                            <th>Filename</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <t t-foreach="admission.document_ids" t-as="doc">
                                            <tr>
                                                <td><t t-esc="doc.document_type_id.name"/></td>
                                                <td><t t-esc="doc.filename"/></td>
                                                <td>
                                                    <span t-attf-class="badge badge-{{doc.state}}">
                                                        <t t-esc="doc.state"/>
                                                    </span>
                                                </td>
                                                <td>
                                                    <a t-attf-href="/web/content/#{doc.id}/document/#{doc.filename}"
                                                       class="btn btn-sm btn-primary">
                                                        Download
                                                    </a>
                                                </td>
                                            </tr>
                                        </t>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Timeline Tab -->
                            <div id="timeline" class="tab-pane">
                                <h4>Application Timeline</h4>
                                <!-- Timeline visualization -->
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

## Security & Access Control

### Record Rules

```xml
<!-- security/portal_security.xml -->
<odoo>
    <data noupdate="1">
        <!-- Portal user can only see their own admissions -->
        <record id="admission_portal_rule" model="ir.rule">
            <field name="name">Portal User: Own Admissions</field>
            <field name="model_id" ref="model_op_admission"/>
            <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>
    </data>
</odoo>
```

### Field-level Security

```python
# Only allow editing in draft state
@api.onchange('state')
def _check_portal_edit_permission(self):
    if self.env.user.has_group('base.group_portal'):
        if self.state not in ['draft', 'submit']:
            # Make fields readonly
            pass
```

### CSRF Protection

All POST requests must include CSRF token:
```html
<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
```

---

## Portal Customization

### Adding Custom Fields to Portal Form

1. **Add field to model**
```python
custom_field = fields.Char('Custom Field')
```

2. **Add to portal template**
```xml
<div class="form-group">
    <label for="custom_field">Custom Field</label>
    <input type="text" name="custom_field" class="form-control"/>
</div>
```

3. **Handle in controller**
```python
values['custom_field'] = post.get('custom_field')
```

### Custom Portal Dashboard Widget

```xml
<template id="portal_admission_widget">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-body">
                <h5>My Applications</h5>
                <p class="text-muted">
                    <t t-esc="admission_count"/> applications
                </p>
                <a href="/my/admissions" class="btn btn-primary">
                    View All
                </a>
            </div>
        </div>
    </div>
</template>
```

---

## Troubleshooting

### Common Issues

**Issue: Portal user cannot see admissions**
- **Cause**: Missing partner_id link
- **Solution**: Ensure admission.partner_id is set correctly

**Issue: Document upload fails**
- **Cause**: File size limit exceeded
- **Solution**: Check nginx/apache upload limits

**Issue: Access denied error**
- **Cause**: Missing portal access rights
- **Solution**: Grant portal access to user

---

## Best Practices

1. **Always validate user input** in controllers
2. **Use CSRF tokens** for all POST requests
3. **Implement proper access control** with record rules
4. **Provide clear error messages** to users
5. **Optimize queries** for better performance
6. **Cache static content** (CSS, JS, images)
7. **Use responsive design** for mobile compatibility
8. **Test on multiple browsers** and devices

---

**Last Updated**: November 2, 2025  
**Version**: 1.0

