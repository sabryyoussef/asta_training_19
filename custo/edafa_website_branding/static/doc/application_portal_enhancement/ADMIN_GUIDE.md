# 🔧 Edafa Admission Portal - Administrator Guide

**Version:** 18.0.1.2  
**Last Updated:** November 3, 2025  
**For:** System Administrators and Admissions Staff

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation & Upgrade](#installation--upgrade)
3. [Configuration](#configuration)
4. [Managing Applications](#managing-applications)
5. [Portal Features](#portal-features)
6. [Email Templates](#email-templates)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)
9. [Monitoring & Analytics](#monitoring--analytics)

---

## 🎯 Overview

### What This Module Does

The **Edafa Website Portal** module provides a public-facing admission application system with:

- ✅ Multi-step wizard interface (5 steps)
- ✅ Real-time validation and feedback
- ✅ Auto-save draft functionality
- ✅ Application status tracking
- ✅ Portal access for applicants
- ✅ Integration with OpenEduCat Admission module

### Architecture

```
Public Website (Frontend)
    ↓
Admission Portal Controller
    ↓
op.admission Model (OpenEduCat)
    ↓
Admissions Workflow (Backend)
```

---

## 🚀 Installation & Upgrade

### Prerequisites

**Required Modules:**
- `openeducat_core` (18.0.1.0+)
- `openeducat_admission` (18.0.1.0+)
- `website` (Odoo standard)
- `portal` (Odoo standard)

**System Requirements:**
- Odoo 18.0
- Python 3.10+
- PostgreSQL 13+

### Fresh Installation

```bash
# 1. Install dependencies first
python3 odoo-bin -c odoo.conf -d your_database \
    -i openeducat_core,openeducat_admission --stop-after-init

# 2. Install Edafa Website Portal
python3 odoo-bin -c odoo.conf -d your_database \
    -i edafa_website_branding --stop-after-init

# 3. Restart server
python3 odoo-bin -c odoo.conf -d your_database
```

### Upgrade from v1.1 to v1.2 (Phase 1)

```bash
# 1. Backup database first!
pg_dump your_database > backup_$(date +%Y%m%d).sql

# 2. Pull latest code
cd /path/to/addons
git pull origin feature/edafa-admission-portal

# 3. Upgrade module
python3 odoo-bin -c odoo.conf -d your_database \
    -u edafa_website_branding --stop-after-init

# 4. Restart server
python3 odoo-bin -c odoo.conf -d your_database

# 5. Clear browser cache and Odoo assets
```

### Post-Upgrade Checklist

- [ ] Visit `/admission/apply` - verify wizard appears
- [ ] Test clicking "Next" button - should advance to step 2
- [ ] Check browser console for JS errors (F12)
- [ ] Verify CSS loads correctly (progress bar styled)
- [ ] Test application submission end-to-end
- [ ] Check email notifications still work

---

## ⚙️ Configuration

### Initial Setup

#### 1. Create Admission Register

**Path:** Admission → Configuration → Admission Registers

```
1. Click "Create"
2. Fill in:
   - Name: "Online Applications 2025"
   - Start Date: 2025-01-01
   - End Date: 2025-12-31
   - Max Count: 1000
   - Min Count: 1
3. Save
4. Click "Confirm" to activate
```

**Why?** All online applications are linked to this register.

#### 2. Configure Email Server

**Path:** Settings → Technical → Email → Outgoing Mail Servers

```
1. Configure SMTP server
2. Test connection
3. Set as default
```

**Required for:** Confirmation emails, status updates

#### 3. Set Up Website

**Path:** Website → Configuration → Settings

```
1. Domain: Set your website domain
2. Logo: Upload Edafa logo (auto-configured)
3. Company Info: Update contact details
```

### Advanced Configuration

#### Menu Configuration

**Path:** Website → Configuration → Menus

**Current Menus:**
- **Apply Now** → `/admission/apply` (wizard)
- **Check Status** → `/admission/check-status`

**To Modify:**
```xml
<!-- In website_menu.xml -->
<record id="website_menu_admission" model="website.menu">
    <field name="name">Apply Now</field>
    <field name="url">/admission/apply</field>
    <field name="sequence">50</field>
</record>
```

#### Access Rights

**Path:** Settings → Users & Companies → Groups

**Portal User Rights:**
- Can create `op.admission` (public)
- Can read `op.course`, `op.batch`, `op.program` (public)
- Can view own applications only

**Public Rights:**
```csv
# In ir.model.access.csv
access_op_admission_public,op.admission.public,model_op_admission,base.group_public,1,0,1,0
```

---

## 📊 Managing Applications

### Viewing Applications

**Path:** Admission → Admissions

**List View Columns:**
- Application Number
- Name
- Email
- Course
- Application Date
- State (Status)

**Filter Options:**
- My Applications
- Submitted
- Under Review
- Accepted
- Rejected
- Online Applications

### Application Workflow

```
Draft → Submit → Confirm → Admission
                    ↓
                  Reject
```

**States Explained:**

| State | Description | Next Action |
|-------|-------------|-------------|
| **Submit** | Just submitted online | Review application |
| **Confirm** | Verified and confirmed | Process admission or reject |
| **Admission** | Accepted | Create student record |
| **Reject** | Not accepted | Notify applicant |
| **Pending** | Awaiting info | Request documents |

### Processing Applications

#### Standard Process

1. **Review Submission**
   - Open application
   - Verify all fields filled
   - Check for obvious issues

2. **Change State to "Confirm"**
   - Click "Confirm" button
   - Or use "Action" → "Confirm"

3. **Request Documents (if needed)**
   - Send email requesting:
     - ID copy
     - Previous transcripts
     - Certificates
     - Payment proof

4. **Make Decision**
   - **Accept:** Click "Admit" button
     - Creates student record
     - Sends acceptance email
   - **Reject:** Click "Reject" button
     - Sends rejection email
     - Application archived

#### Bulk Actions

**Select Multiple Applications:**
```
1. Check boxes next to applications
2. Action menu → Select action:
   - Confirm Selected
   - Send Email
   - Export to Excel
   - Delete (draft only)
```

---

## 🌐 Portal Features

### For Applicants

**Portal Access:** `/my/applications`

**Features:**
- View all submitted applications
- Check application status
- See application details
- Sort and filter
- Download application PDF (future)

**To Enable:**
```
1. User creates portal account
2. Uses same email as application
3. Can view applications with that email
```

### Portal Management

**Path:** Settings → Users & Companies → Portal Access Rights

**Configure:**
- Who can access portal
- What they can see
- Privacy settings

---

## 📧 Email Templates

### Available Templates

#### 1. Application Received (Auto-sent)

**Template ID:** `admission_confirmation_email`  
**Trigger:** When application created  
**Contains:**
- Welcome message
- Application number
- Next steps
- Contact information

**To Customize:**
```
Settings → Technical → Email → Email Templates
→ Search "Admission Confirmation"
→ Edit HTML/Text
```

#### 2. Status Change Notifications

**Triggers:**
- Submit → Confirm: "Application confirmed"
- Confirm → Admission: "Congratulations! You're accepted"
- Confirm → Reject: "Application update"

**To Add Auto-Notifications:**
```python
# In models/admission_extended.py
class OpAdmission(models.Model):
    _inherit = 'op.admission'
    
    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            self._send_status_email()
        return res
```

### Email Customization

**Variables Available:**
- `${object.application_number}` - Application number
- `${object.name}` - Applicant name
- `${object.email}` - Email address
- `${object.course_id.name}` - Course name
- `${object.state}` - Current status

**Example:**
```xml
<p>Dear ${object.first_name} ${object.last_name},</p>
<p>Your application ${object.application_number} has been received!</p>
```

---

## 🔐 Security

### Access Control

**Public Access (No Login):**
- ✅ Can submit applications
- ✅ Can check status (with app number + email)
- ❌ Cannot view other applications
- ❌ Cannot modify after submission

**Portal Users (Logged In):**
- ✅ Can view own applications
- ✅ Can track status
- ❌ Cannot edit submitted applications
- ❌ Cannot view others' applications

**Admissions Staff:**
- ✅ Full access to all applications
- ✅ Can change statuses
- ✅ Can edit applications
- ✅ Can delete draft applications

**Admissions Manager:**
- ✅ All staff permissions
- ✅ Can configure admission registers
- ✅ Can access analytics
- ✅ Can manage email templates

### Security Best Practices

1. **Restrict Admin Access**
   - Only give admission permissions to relevant staff
   - Use groups: `openeducat_core.group_op_admission_manager`

2. **Monitor Submissions**
   - Watch for spam applications
   - Block suspicious emails if needed
   - Use reCAPTCHA (future enhancement)

3. **Data Protection**
   - Regular database backups
   - GDPR compliance
   - Secure email transmission (HTTPS)

4. **CSRF Protection**
   - Enabled by default on all forms
   - Don't disable `csrf=True` on routes

---

## 🐛 Troubleshooting

### Common Issues

#### Applications Not Appearing

**Symptoms:** Public submits but nothing in backend

**Solutions:**
1. Check admission register exists and is confirmed
2. Verify `op.admission` access rights for public
3. Check Odoo logs for errors
4. Test with admin account first

**Debug:**
```python
# In Odoo shell
admission = env['op.admission'].sudo().search([], limit=5, order='id desc')
print(admission.mapped('application_number'))
```

---

#### Email Not Sending

**Symptoms:** No confirmation email received

**Solutions:**
1. Check SMTP server configured
2. Test email server connection
3. Verify email template exists
4. Check spam folder
5. Review Odoo logs

**Test Email:**
```
Settings → Technical → Email → Outgoing Mail Servers
→ Test Connection
```

---

#### Wizard Not Working

**Symptoms:** Can't click Next, steps don't change

**Solutions:**
1. Clear browser cache (Ctrl+Shift+R)
2. Check browser console for JS errors
3. Verify assets loaded (F12 → Network tab)
4. Update module to latest version
5. Clear Odoo assets cache

**Clear Assets:**
```
Settings → Technical → Assets → Clear Cache
```

---

#### Validation Errors

**Symptoms:** Form won't submit, validation errors shown

**Solutions:**
1. Check required fields filled (marked with *)
2. Verify email format is correct
3. Ensure age is 16+ years
4. Check phone number has 10+ digits
5. Accept terms and conditions (Step 5)

---

### Performance Issues

**Symptoms:** Slow loading, timeouts

**Solutions:**
1. Enable Odoo asset compression
2. Use CDN for static files
3. Optimize database (VACUUM)
4. Check server resources
5. Review slow queries

**Monitor Performance:**
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log

# Monitor PostgreSQL
SELECT * FROM pg_stat_activity WHERE datname = 'your_database';
```

---

## 📈 Monitoring & Analytics

### Application Metrics

**Track:**
- Applications per day/week/month
- Completion rate (started vs submitted)
- Average time to complete
- Most popular courses
- Geographic distribution

**Reports Available:**
```
Admission → Reports → Admission Analysis
```

**Custom Report (SQL):**
```sql
SELECT 
    DATE(create_date) as date,
    COUNT(*) as total_applications,
    COUNT(CASE WHEN state = 'admission' THEN 1 END) as accepted,
    COUNT(CASE WHEN state = 'reject' THEN 1 END) as rejected
FROM op_admission
WHERE create_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(create_date)
ORDER BY date DESC;
```

### Google Analytics Integration

**Add to Template:**
```xml
<script async="" src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

**Track Events:**
- Page views
- Step completions
- Validation errors
- Submissions
- Time spent per step

---

## 🔧 Advanced Configuration

### Customization Options

#### Change Step Count

To add/remove steps, modify:
```javascript
// In wizard inline script
totalSteps: 5  // Change to 4, 6, etc.
```

Then update template with corresponding steps.

#### Modify Field Requirements

**Make field required:**
```xml
<input type="text" name="phone" required="required"/>
```

**Make field optional:**
```xml
<input type="text" name="middle_name"/>  <!-- Remove required -->
```

#### Custom Validation Rules

Add to inline JavaScript:
```javascript
validateStep: function(stepNum) {
    // Your custom validation logic
    if (stepNum === 3) {
        // Require course selection
        if (!document.getElementById('course_id').value) {
            alert('Please select a course');
            return false;
        }
    }
    return true;
}
```

### Branding Customization

**Change Colors:**
```css
/* In wizard.css */
.wizard-progress {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

.step.active .step-icon {
    color: #YOUR_PRIMARY_COLOR;
}
```

**Change Logo:**
```xml
<!-- In website_data.xml -->
<record id="website.default_website" model="website">
    <field name="logo" type="base64" file="your_module/static/src/img/your_logo.svg"/>
</record>
```

---

## 📧 Email Management

### Email Template Management

**Path:** Settings → Technical → Email → Email Templates

### Create Custom Template

```xml
<record id="email_custom_template" model="mail.template">
    <field name="name">Custom Admission Email</field>
    <field name="model_id" ref="openeducat_admission.model_op_admission"/>
    <field name="subject">Application Update - ${object.application_number}</field>
    <field name="email_from">${(object.company_id.email or user.email)|safe}</field>
    <field name="email_to">${object.email|safe}</field>
    <field name="body_html"><![CDATA[
        <p>Dear ${object.first_name},</p>
        <p>Your application status: ${object.state}</p>
    ]]></field>
</record>
```

### Trigger Emails Automatically

```python
# Override create/write methods
@api.model
def create(self, vals):
    admission = super().create(vals)
    template = self.env.ref('your_module.email_template_id')
    template.send_mail(admission.id, force_send=True)
    return admission
```

---

## 🎨 Customization Examples

### Add Custom Field to Wizard

**Step 1: Add to Template**
```xml
<div class="mb-3">
    <label for="custom_field">Custom Field</label>
    <input type="text" name="custom_field" id="custom_field" class="form-control"/>
</div>
```

**Step 2: Add to Controller**
```python
admission_vals = {
    # ... existing fields ...
    'custom_field': post.get('custom_field', ''),
}
```

**Step 3: Add to Review**
```javascript
document.getElementById('review-custom-field').textContent = getName('custom_field');
```

### Add Conditional Logic

**Show field based on selection:**
```javascript
document.querySelector('#program_id').addEventListener('change', function() {
    const programName = this.options[this.selectedIndex].text;
    if (programName.includes('Graduate')) {
        document.querySelector('.degree-section').style.display = 'block';
    } else {
        document.querySelector('.degree-section').style.display = 'none';
    }
});
```

---

## 🔍 Monitoring

### Check Application Logs

```bash
# Odoo logs
tail -f /var/log/odoo/odoo.log | grep admission

# Filter errors only
tail -f /var/log/odoo/odoo.log | grep -i error | grep admission
```

### Database Queries

**Recent Applications:**
```sql
SELECT 
    application_number,
    name,
    email,
    course_id,
    state,
    create_date
FROM op_admission
ORDER BY create_date DESC
LIMIT 20;
```

**Applications by Status:**
```sql
SELECT 
    state,
    COUNT(*) as count
FROM op_admission
WHERE create_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY state;
```

**Conversion Rate:**
```sql
SELECT 
    COUNT(*) as total_applications,
    COUNT(CASE WHEN state = 'admission' THEN 1 END) as admitted,
    ROUND(100.0 * COUNT(CASE WHEN state = 'admission' THEN 1 END) / COUNT(*), 2) as acceptance_rate
FROM op_admission
WHERE create_date >= CURRENT_DATE - INTERVAL '30 days';
```

---

## 🚨 Emergency Procedures

### Portal Down

**Immediate Actions:**
1. Check Odoo server status
2. Check database connection
3. Review recent code changes
4. Check error logs

**Temporary Solution:**
```
# Disable module temporarily
python3 odoo-bin -c odoo.conf -d your_database \
    -u edafa_website_branding --uninstall --stop-after-init
```

**Recovery:**
```
# Restore from backup
psql your_database < backup_file.sql

# Restart server
systemctl restart odoo
```

### Spam Applications

**Symptoms:** Hundreds of fake applications

**Solutions:**
1. **Add reCAPTCHA** (future enhancement)
2. **Block IP addresses** (server level)
3. **Add honeypot field**
4. **Rate limiting**

**Quick Fix:**
```python
# Add to controller
if request.session.get('application_count', 0) > 5:
    return request.render('error_page', {'message': 'Too many attempts'})
request.session['application_count'] = request.session.get('application_count', 0) + 1
```

---

## 📚 Resources

### Documentation

- **User Guide:** USER_GUIDE.md
- **API Documentation:** API_DOCUMENTATION.md (coming soon)
- **Developer Guide:** DEVELOPER_GUIDE.md (coming soon)
- **Enhancement Plan:** PORTAL_ENHANCEMENT_PLAN.md

### External Links

- **OpenEduCat Docs:** https://www.openeducat.org
- **Odoo 18 Docs:** https://www.odoo.com/documentation/18.0/
- **Support Forum:** https://www.odoo.com/forum

### Support

- **Email:** support@edafa.org
- **Technical Issues:** Create GitHub issue
- **Urgent:** Call +1 555-555-5556

---

## 📝 Maintenance Schedule

### Daily
- [ ] Monitor application submissions
- [ ] Check for errors in logs
- [ ] Respond to applicant queries

### Weekly
- [ ] Review application metrics
- [ ] Process pending applications
- [ ] Update admission registers if needed

### Monthly
- [ ] Database backup
- [ ] Review analytics
- [ ] Update documentation if features added
- [ ] Security audit

### Quarterly
- [ ] User feedback survey
- [ ] Performance optimization
- [ ] Plan enhancements

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**For Module Version:** 18.0.1.2

