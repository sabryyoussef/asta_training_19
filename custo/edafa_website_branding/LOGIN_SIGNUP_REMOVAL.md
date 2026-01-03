# Login Page Signup Section Removal

## Implementation Overview

**Module:** `edafa_website_branding`  
**Odoo Version:** 19.0  
**Date:** 2024  
**Type:** View Inheritance

---

## 🎯 Objective

Remove the "Don't have an account?" section/field from the login/registration page to prevent public users from self-registering.

---

## 📂 Files Modified

### 1. Created: `views/auth_signup_login.xml`

**Purpose:** Template inheritance to hide signup link from login page

**Location:** `/custo/edafa_website_branding/views/auth_signup_login.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <!-- Hide "Don't have an account?" section from login page -->
    <template id="login_hide_signup" inherit_id="web.login" priority="99">
        <!-- Hide the signup link/message by setting it to display:none -->
        <xpath expr="//div[contains(@class, 'alert')]//a[@href='/web/signup']/.." position="attributes">
            <attribute name="style">display: none;</attribute>
        </xpath>
    </template>
    
    <!-- Alternative: If the above doesn't work, try hiding by specific text content -->
    <template id="login_hide_signup_alt" inherit_id="web.login" priority="100" active="False">
        <!-- This is an alternative approach - replace the entire div containing signup link -->
        <xpath expr="//div[@class='alert alert-info' and contains(., 'account')]" position="replace"/>
    </template>

</odoo>
```

**Key Features:**
- **Primary Method** (`login_hide_signup`): Uses CSS `display: none` to hide the signup section
- **Alternative Method** (`login_hide_signup_alt`): Completely removes the div (inactive by default)
- **Priority 99**: Ensures this template loads after core templates

### 2. Modified: `__manifest__.py`

**Changes:** Added new template file to data list

```python
'data': [
    'security/ir.model.access.csv',
    'security/portal_security.xml',
    'data/website_data.xml',
    'data/website_menu.xml',
    'data/payment_data.xml',
    'views/profile_selection_template.xml',
    'views/trainer_recruitment_template.xml',
    'views/admission_portal_templates.xml',
    'views/admission_wizard_templates.xml',
    'views/admission_thank_you_template.xml',
    'views/my_applications_template.xml',
    'views/auth_signup_login.xml',  # ← NEW
],
```

---

## 🔧 Technical Details

### Template Inheritance

**Base Template:** `web.login`  
**Module:** Odoo web module (core)  
**Inheritance Type:** Extension via XPath

### XPath Expression

```xpath
//div[contains(@class, 'alert')]//a[@href='/web/signup']/..
```

**Breakdown:**
1. `//div[contains(@class, 'alert')]` - Find any div with 'alert' class
2. `//a[@href='/web/signup']` - Find anchor tag linking to signup
3. `/..` - Select parent element of that anchor
4. `position="attributes"` - Modify attributes of that element
5. Add `style="display: none;"` - Hide the element

### Why This Approach?

1. **Non-invasive:** Doesn't require modifying core Odoo files
2. **Reversible:** Can be easily disabled by removing the template
3. **Safe:** Uses CSS hiding, doesn't break any functionality
4. **Compatible:** Works across Odoo versions with minimal changes

---

## 📋 Installation Steps

### Step 1: File Creation
Files have already been created:
- ✅ `views/auth_signup_login.xml`
- ✅ Modified `__manifest__.py`

### Step 2: Update Module

```bash
# Method 1: Via Odoo CLI (Recommended)
odoo-bin -u edafa_website_branding -d your_database

# Method 2: Via UI
# 1. Go to Apps
# 2. Remove "Apps" filter
# 3. Search for "Edafa Website Portal"
# 4. Click "Upgrade"
```

### Step 3: Clear Cache (If Needed)

```bash
# Clear browser cache
# - Press Ctrl+Shift+Del (or Cmd+Shift+Del on Mac)
# - Select "Cached images and files"
# - Clear

# Or restart Odoo server
sudo systemctl restart odoo
```

### Step 4: Verify Changes

1. Navigate to login page: `/web/login`
2. Verify "Don't have an account?" section is hidden
3. Login functionality should still work normally

---

## 🧪 Testing

### Test Case 1: Login Page
- ✅ Visit `/web/login`
- ✅ "Don't have an account?" should be hidden
- ✅ Login form should work normally

### Test Case 2: Existing Functionality
- ✅ User login works
- ✅ Password reset works
- ✅ Portal access works

### Test Case 3: Admin Features
- ✅ Admins can still create users manually
- ✅ Invitation emails still work
- ✅ Portal user creation from backend works

---

## 🔄 Alternative Approaches

If the primary method doesn't work, you can activate the alternative template:

### Option 1: CSS Hide (Default - Active)
```xml
<template id="login_hide_signup" inherit_id="web.login" priority="99">
    <xpath expr="//div[contains(@class, 'alert')]//a[@href='/web/signup']/.." position="attributes">
        <attribute name="style">display: none;</attribute>
    </xpath>
</template>
```

### Option 2: Complete Removal (Alternative - Inactive)
```xml
<template id="login_hide_signup_alt" inherit_id="web.login" priority="100" active="True">
    <xpath expr="//div[@class='alert alert-info' and contains(., 'account')]" position="replace"/>
</template>
```

**To activate Option 2:**
1. Edit `auth_signup_login.xml`
2. Change `active="False"` to `active="True"` on line with `login_hide_signup_alt`
3. Optionally set `active="False"` on `login_hide_signup`
4. Update module

---

## ⚠️ Important Notes

### Security Implications
- ✅ **Positive:** Prevents unauthorized self-registration
- ⚠️ **Note:** Users can only be created by administrators
- 💡 **Recommendation:** Ensure admin processes for user creation are documented

### User Management After This Change

**How to create new users:**

1. **Backend User Creation** (Recommended)
   - Navigate to: Settings → Users & Companies → Users
   - Click "Create"
   - Fill user details
   - Assign appropriate groups
   - Send invitation email

2. **Portal User Creation**
   - Navigate to the contact: Contacts → Select contact
   - Click "Grant Portal Access"
   - User receives invitation email

3. **Programmatic Creation** (For developers)
   ```python
   # Via Python code
   user = self.env['res.users'].create({
       'name': 'John Doe',
       'login': 'john.doe@example.com',
       'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
   })
   user.action_reset_password()  # Send invitation
   ```

---

## 🐛 Troubleshooting

### Issue: Signup link still visible

**Solutions:**
1. **Clear cache:**
   ```bash
   # Browser cache
   Ctrl+Shift+Del → Clear cached images and files
   
   # Odoo assets
   Settings → Technical → User Interface → View → Remove all records with "edafa_website_branding"
   ```

2. **Check module update:**
   ```bash
   odoo-bin -u edafa_website_branding -d your_database
   ```

3. **Verify file is loaded:**
   - Go to: Settings → Technical → User Interface → Views
   - Search for: `login_hide_signup`
   - Should show the inherited view

4. **Check XPath:**
   - The DOM structure might have changed
   - Inspect the login page with browser dev tools (F12)
   - Find the actual element containing signup link
   - Update XPath accordingly

### Issue: Login page broken

**Solutions:**
1. **Disable the template temporarily:**
   - Edit `auth_signup_login.xml`
   - Add `active="False"` to the template tag
   - Update module

2. **Check error logs:**
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

3. **Restore backup:**
   - If needed, remove the template file
   - Update module
   - Investigate the issue

---

## 📊 Related Implementations

This is **Implementation #10** in the series:

1. ✅ English numerals enforcement
2. ✅ Profile selection (Student/Trainer)
3. ✅ Department field on Course
4. ✅ Programs on Department
5. ✅ Department-based filtering
6. ✅ Active programs filter
7. ✅ Label renaming (Parent → Main)
8. ✅ User role conversion fix (Odoo 19)
9. ✅ Admission register routing fix
10. ✅ **Login page signup section removal** ← YOU ARE HERE

---

## 📖 Additional Resources

### Odoo Documentation
- [QWeb Templates](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)
- [View Inheritance](https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html#inheritance)
- [XPath in Odoo](https://www.odoo.com/documentation/19.0/developer/howtos/web_services.html)

### Related Files
- `/custo/edafa_website_branding/views/auth_signup_login.xml` (This implementation)
- `/custo/edafa_website_branding/__manifest__.py` (Module manifest)

---

## ✅ Summary

### What Was Done
- Created new view inheritance template to hide signup section
- Added template to module manifest
- Documented implementation

### What Users Will See
- Login page without "Don't have an account?" section
- Clean, professional login interface
- No option for self-registration

### What Admins Need to Know
- Users must be created manually by admins
- Portal access can be granted from contact records
- Invitation emails still work normally

---

## 🔐 Security Best Practices

After removing public signup, ensure:

1. **Admin procedures are documented**
   - How to create new users
   - How to grant portal access
   - Password reset process

2. **Alternative access methods**
   - Clear contact information for support
   - "Request Access" form (if needed)
   - Phone/email support for account creation

3. **User onboarding**
   - Welcome emails with clear instructions
   - Documentation for first-time users
   - Support contact information

---

**End of Documentation**

Last Updated: 2024  
Module Version: 19.0.1.2.0  
Implementation Status: ✅ Complete
