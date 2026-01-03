# ASTA Training 19 - Complete Testing Guide

**Project:** ASTA Training 19  
**Odoo Version:** 19.0  
**Test Date:** January 3, 2026  
**Total Implementations:** 10

---

## 📋 Table of Contents

1. [Pre-Testing Setup](#pre-testing-setup)
2. [Implementation #1: English Numerals](#test-1-english-numerals)
3. [Implementation #2: Profile Selection](#test-2-profile-selection)
4. [Implementation #3: Course Department Field](#test-3-course-department-field)
5. [Implementation #4: Department Programs](#test-4-department-programs)
6. [Implementation #5: Admission Filtering](#test-5-admission-filtering)
7. [Implementation #6: Active Programs Filter](#test-6-active-programs-filter)
8. [Implementation #7: Label Renaming](#test-7-label-renaming)
9. [Implementation #8: Role Conversion](#test-8-role-conversion)
10. [Implementation #9: Admission Routing](#test-9-admission-routing)
11. [Implementation #10: Login Signup Removal](#test-10-login-signup-removal)
12. [Post-Testing Checklist](#post-testing-checklist)

---

## 🔧 Pre-Testing Setup

### Environment Requirements

- ✅ Odoo 19.0 installed
- ✅ PostgreSQL 13+ running
- ✅ Python 3.10+
- ✅ All custom modules installed

### Module Installation

```bash
# Install/Update all modules
odoo-bin -c /etc/odoo.conf -d your_database \
  -u edafa_website_branding,openeducat_core,motakamel_alumni,motakamel_dashboard,openeducat_fees \
  --stop-after-init

# Restart Odoo
sudo systemctl restart odoo
```

### Test User Setup

Create these test users for comprehensive testing:

1. **Admin User** (already exists)
   - Login: admin
   - Groups: Administration / Settings

2. **Portal User**
   ```
   Name: Test Portal User
   Login: portal@test.com
   Groups: Portal
   ```

3. **Internal User**
   ```
   Name: Test Internal User
   Login: internal@test.com
   Groups: Internal User
   ```

4. **Education Manager**
   ```
   Name: Test Education Manager
   Login: edumanager@test.com
   Groups: Education Manager
   ```

### Test Data Preparation

Create test data:

1. **Departments** (at least 3)
   - Computer Science
   - Business Administration
   - Engineering

2. **Programs** (2-3 per department)
   - Link programs to departments
   - Ensure each program has courses

3. **Courses** (3-4 per program)
   - Link to departments and programs
   - Mark some as active, some as inactive

4. **Admission Registers** (2-3)
   - Different entities/governorates
   - Link to specific courses/programs

---

## Test #1: English Numerals

**Implementation:** CSS enforcement for English numerals (0-9)  
**Modules:** 5 modules  
**Priority:** Medium

### Test Steps

1. **Change Browser Locale to Arabic**
   - Open browser settings
   - Change language to Arabic (العربية)
   - Restart browser

2. **Backend Testing**
   ```
   ✅ Navigate to: Dashboard
   ✅ Check: Numbers display as 0-9 (not ٠-٩)
   
   ✅ Navigate to: Education → Courses
   ✅ Check: Course codes, IDs use English numerals
   
   ✅ Navigate to: Accounting → Invoices
   ✅ Check: Amounts, dates use English numerals
   
   ✅ Navigate to: Alumni Management
   ✅ Check: Alumni IDs, years use English numerals
   
   ✅ Navigate to: Fees Management
   ✅ Check: Fee amounts use English numerals
   ```

3. **Frontend Testing**
   ```
   ✅ Navigate to: /admission/apply
   ✅ Check: Form fields, numbers use English numerals
   
   ✅ Navigate to: Portal (logged in as portal user)
   ✅ Check: All numbers in portal use English numerals
   ```

### Expected Results

- ✅ All numbers display as 0-9 across the entire system
- ✅ No Arabic numerals (٠-٩) visible anywhere
- ✅ Works in all modules: backend and frontend

### Failure Scenarios

- ❌ If Arabic numerals appear: Check browser cache, CSS loading
- ❌ If inconsistent: Verify module upgrade completed

### Verification Commands

```bash
# Check CSS files exist
ls -la /workspaces/asta_training_19/custo/*/static/src/css/english_numerals.css

# Should list 5 files
```

---

## Test #2: Profile Selection

**Implementation:** Profile type selection (Student/Trainer)  
**Module:** edafa_website_branding  
**Priority:** High

### Test Steps

1. **Access Profile Selection Page**
   ```
   ✅ Navigate to: /admission/apply
   ✅ Verify: Page loads with two cards (Student/Trainer)
   ✅ Check: Student card shows graduation cap icon
   ✅ Check: Trainer card shows chalkboard icon
   ✅ Check: Both cards have clear descriptions
   ```

2. **Test Student Route**
   ```
   ✅ Click: "Apply as Student" button
   ✅ Verify: Redirects to /admission/wizard
   ✅ Check: Admission wizard form loads
   ✅ Check: Form is pre-filled with demo data
   ```

3. **Test Trainer Route** (if hr_recruitment installed)
   ```
   ✅ Go back to: /admission/apply
   ✅ Click: "Apply as Trainer" button
   ✅ Verify: Redirects to /jobs or recruitment page
   ```

4. **Test Trainer Route** (if hr_recruitment NOT installed)
   ```
   ✅ Go back to: /admission/apply
   ✅ Click: "Apply as Trainer" button
   ✅ Verify: Shows information page
   ✅ Check: Page explains trainer recruitment
   ✅ Check: Contact information displayed
   ```

### Expected Results

- ✅ Profile selection page is visually appealing
- ✅ Student route → Admission wizard
- ✅ Trainer route → Appropriate destination
- ✅ Responsive design works on mobile

### Failure Scenarios

- ❌ If 404 error: Check route registration
- ❌ If cards not showing: Check template loading
- ❌ If redirect fails: Check controller logic

---

## Test #3: Course Department Field

**Implementation:** Department field visible on Course page  
**Module:** openeducat_core  
**Priority:** Medium

### Test Steps

1. **Login as any user** (not just admin)

2. **Create New Course**
   ```
   ✅ Navigate to: Education → Configuration → Courses
   ✅ Click: Create
   ✅ Verify: Department field is visible
   ✅ Check: Can select department from dropdown
   ✅ Fill: All required fields
   ✅ Save: Course
   ✅ Verify: Department saved correctly
   ```

3. **List View**
   ```
   ✅ Navigate to: Education → Configuration → Courses
   ✅ Verify: Department column visible in list
   ✅ Check: Department shown for all courses
   ```

4. **Search/Filter**
   ```
   ✅ Click: Search icon
   ✅ Verify: "Department" filter available
   ✅ Select: A department
   ✅ Verify: Only courses from that department shown
   ```

### Expected Results

- ✅ Department field visible to all users
- ✅ No group restrictions
- ✅ Department can be set and modified
- ✅ Filter works correctly

### Failure Scenarios

- ❌ If field hidden: Check groups attribute removed
- ❌ If can't save: Check field permissions

---

## Test #4: Department Programs

**Implementation:** Programs field on Department page  
**Module:** openeducat_core  
**Priority:** High

### Test Steps

1. **Open Department Form**
   ```
   ✅ Navigate to: Education → Configuration → Departments
   ✅ Click: Any department
   ✅ Verify: "Programs" tab exists
   ✅ Click: Programs tab
   ```

2. **Add Programs**
   ```
   ✅ Click: Add a line
   ✅ Select: 2-3 programs
   ✅ Save: Department
   ✅ Verify: Programs saved
   ✅ Reopen: Department
   ✅ Check: Programs still linked
   ```

3. **List View**
   ```
   ✅ Navigate to: Education → Configuration → Departments (list view)
   ✅ Verify: "Programs" column visible
   ✅ Check: Programs count shown for each department
   ```

4. **Search/Filter**
   ```
   ✅ Click: Search icon
   ✅ Verify: "Programs" filter available
   ✅ Use filter: Select a program
   ✅ Verify: Departments with that program shown
   ```

### Expected Results

- ✅ Programs can be linked to departments
- ✅ Many2many relationship works both ways
- ✅ Data persists correctly
- ✅ Filter and search work

### Failure Scenarios

- ❌ If tab missing: Check XML view
- ❌ If can't add programs: Check model field

---

## Test #5: Admission Filtering

**Implementation:** Department-based admission filtering  
**Module:** edafa_website_branding  
**Priority:** High

### Test Steps

1. **Start Admission Process**
   ```
   ✅ Navigate to: /admission/apply
   ✅ Click: "Apply as Student"
   ✅ Verify: Wizard loads
   ```

2. **Test Department Selection**
   ```
   ✅ Scroll to: Academic Information section
   ✅ Verify: Department is FIRST field
   ✅ Check: Department field is REQUIRED
   ✅ Select: Computer Science department
   ```

3. **Test Program Filtering**
   ```
   ✅ After selecting department:
   ✅ Check: Program dropdown updates
   ✅ Verify: Only programs from Computer Science shown
   ✅ Try: Selecting a program
   ✅ Verify: Selection works
   ```

4. **Test Course Filtering**
   ```
   ✅ After selecting program:
   ✅ Check: Course dropdown updates
   ✅ Verify: Only courses from selected department + program shown
   ✅ Try: Different combinations
   ✅ Verify: Filtering always correct
   ```

5. **Test Form Submission**
   ```
   ✅ Fill: All required fields
   ✅ Ensure: Department, Program, Course selected
   ✅ Submit: Form
   ✅ Verify: Submission successful
   ✅ Check backend: Admission has correct department
   ```

6. **Test Validation**
   ```
   ✅ Try submitting without department
   ✅ Verify: Error message shown
   ✅ Check: "Department is required"
   ```

### Expected Results

- ✅ Department is first and required
- ✅ Programs filter by department
- ✅ Courses filter by department + program
- ✅ JavaScript filtering works in real-time
- ✅ Backend validation enforces rules

### Failure Scenarios

- ❌ If filtering doesn't work: Check JavaScript console
- ❌ If all programs shown: Check controller logic
- ❌ If can submit without department: Check validation

---

## Test #6: Active Programs Filter

**Implementation:** Show only programs with active courses  
**Module:** edafa_website_branding  
**Priority:** Medium

### Test Steps

1. **Prepare Test Data**
   ```
   Backend:
   ✅ Create Program A with 3 active courses
   ✅ Create Program B with 0 active courses (all inactive)
   ✅ Create Program C with mix of active/inactive
   ✅ Link all to same department
   ```

2. **Test Admission Form**
   ```
   ✅ Navigate to: /admission/wizard
   ✅ Select: The test department
   ✅ Check program dropdown:
      ✅ Verify: Program A appears (has active courses)
      ✅ Verify: Program B does NOT appear (no active courses)
      ✅ Verify: Program C appears (has some active courses)
   ```

3. **Test Course Dropdown**
   ```
   ✅ Select: Program C
   ✅ Check course dropdown:
      ✅ Verify: Only active courses shown
      ✅ Verify: Inactive courses NOT shown
   ```

### Expected Results

- ✅ Only programs with active courses appear
- ✅ Empty programs hidden from students
- ✅ Course dropdown shows only active courses

### Failure Scenarios

- ❌ If all programs shown: Check controller filter logic
- ❌ If inactive courses shown: Check course filter

---

## Test #7: Label Renaming

**Implementation:** Parent → Main label changes  
**Module:** openeducat_core  
**Priority:** Low

### Test Steps

1. **Course Views**
   ```
   ✅ Navigate to: Education → Configuration → Courses (list view)
   ✅ Verify: Column says "Main Courses" (not "Parent Course")
   
   ✅ Click: Any course (form view)
   ✅ Verify: Field label is "Main Courses" (not "Parent Course")
   
   ✅ Click: Search icon
   ✅ Verify: Filter says "Main Courses" (not "Parent Course")
   ```

2. **Department Views**
   ```
   ✅ Navigate to: Education → Configuration → Departments (list view)
   ✅ Verify: Column says "Main Department" (not "Parent Department")
   
   ✅ Click: Any department (form view)
   ✅ Verify: Field label is "Main Department" (not "Parent Department")
   
   ✅ Click: Search icon
   ✅ Verify: Filter says "Main Department" (not "Parent Department")
   ```

### Expected Results

- ✅ All labels changed from "Parent" to "Main"
- ✅ Consistent across list, form, and search views
- ✅ No "Parent" labels remaining

### Failure Scenarios

- ❌ If old labels showing: Check view inheritance
- ❌ If inconsistent: Verify all view types updated

---

## Test #8: Role Conversion

**Implementation:** User role conversion fix for Odoo 19  
**Module:** openeducat_core  
**Priority:** Critical

### Test Steps

1. **Create Test User**
   ```
   ✅ Navigate to: Settings → Users & Companies → Users
   ✅ Click: Create
   ✅ Name: "Test Role User"
   ✅ Login: "roletest@test.com"
   ✅ Groups: Internal User
   ✅ Save
   ```

2. **Convert User → Portal**
   ```
   ✅ Open: The test user
   ✅ Click: Edit
   ✅ Remove: Internal User group
   ✅ Add: Portal group
   ✅ Click: Save
   ✅ Verify: Save successful (no error)
   ✅ Reopen: User record
   ✅ Check: User now has Portal group
   ✅ Verify: Internal User removed
   ```

3. **Convert Portal → User**
   ```
   ✅ Open: Same test user
   ✅ Click: Edit
   ✅ Remove: Portal group
   ✅ Add: Internal User group
   ✅ Click: Save
   ✅ Verify: Save successful
   ✅ Reopen: User record
   ✅ Check: User now has Internal User group
   ✅ Verify: Portal removed
   ```

4. **Test Login**
   ```
   ✅ Logout as admin
   ✅ Login as: roletest@test.com
   ✅ Verify: Can access backend (if internal user)
   ✅ Or: Can access portal only (if portal user)
   ✅ Check: Appropriate access based on role
   ```

5. **Check Logs** (optional but recommended)
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   # Look for: "Groups updated successfully via inverse relationship"
   ```

### Expected Results

- ✅ Role conversion works in both directions
- ✅ No errors during save
- ✅ Groups actually change
- ✅ User access reflects new role
- ✅ Log entries confirm fix is working

### Failure Scenarios

- ❌ If save fails: Check res_users_extended.py loaded
- ❌ If groups don't change: Check write() override
- ❌ If errors in log: Review implementation

### Alternative Test (Using Script)

```bash
# SSH to server
odoo-bin shell -c /etc/odoo.conf -d your_database

# In Python shell:
user_id = 123  # Replace with test user ID
exec(open('/workspaces/asta_training_19/custo/openeducat_core/test_role_conversion.py').read())
test_user_role_conversion(env, user_id)
```

---

## Test #9: Admission Routing

**Implementation:** Multiple admission registers routing fix  
**Module:** edafa_website_branding  
**Priority:** High

### Test Steps

1. **Prepare Test Data**
   ```
   Backend - Create 3 Admission Registers:
   
   Register 1: "Cairo CS Applications"
   - Course: Advanced Programming
   - Program: Computer Science
   - Entity: Cairo
   
   Register 2: "Alex Business Applications"
   - Course: Marketing 101
   - Program: Business Administration
   - Entity: Alexandria
   
   Register 3: "General Applications"
   - Course: (none - empty)
   - Program: (none - empty)
   - Entity: General
   
   ✅ Ensure all registers are active
   ✅ Start dates: today or past
   ✅ End dates: future
   ```

2. **Test Course-Specific Routing**
   ```
   ✅ Navigate to: /admission/wizard
   ✅ Select: Advanced Programming course
   ✅ Fill: All required fields
   ✅ Submit: Form
   
   Backend:
   ✅ Navigate to: Admission → Registers
   ✅ Click: "Cairo CS Applications"
   ✅ Check Applications: Verify your application is here
   ✅ Open: The application
   ✅ Verify: register_id = "Cairo CS Applications"
   ```

3. **Test Program-Specific Routing**
   ```
   ✅ Navigate to: /admission/wizard
   ✅ Select: Business Administration program
   ✅ Select: Any course from that program
   ✅ Submit: Form
   
   Backend:
   ✅ Navigate to: "Alex Business Applications" register
   ✅ Verify: Application routed correctly
   ```

4. **Test Fallback Routing**
   ```
   ✅ Navigate to: /admission/wizard
   ✅ Select: A course NOT linked to any specific register
   ✅ Submit: Form
   
   Backend:
   ✅ Check: "General Applications" register
   ✅ Verify: Application routed to general register
   ```

5. **Test Routing Logic Priority**
   ```
   Scenario: Course matches Register 1, Program matches Register 2
   
   ✅ Submit application with that course/program
   ✅ Backend verification:
      ✅ Should route to Register 1 (Course match wins)
      ✅ NOT Register 2 (Program is lower priority)
   ```

### Expected Results

- ✅ Applications route to correct register based on course
- ✅ Fallback to program-based routing works
- ✅ General fallback works when no specific match
- ✅ Routing hierarchy respected: Course → Program → General

### Failure Scenarios

- ❌ If all go to one register: Check routing logic
- ❌ If routing inconsistent: Review controller code
- ❌ If new register created: Check create fallback

---

## Test #10: Login Signup Removal

**Implementation:** Remove signup section from login page  
**Module:** edafa_website_branding  
**Priority:** Medium

### Test Steps

1. **Logout Completely**
   ```
   ✅ If logged in: Logout
   ✅ Clear: Browser cookies/cache
   ```

2. **Test Login Page**
   ```
   ✅ Navigate to: /web/login
   ✅ Verify: Page loads correctly
   ✅ Check: Login form is visible
   ✅ Check: Username and password fields present
   ✅ Look for: "Don't have an account?" section
   ✅ Verify: Signup section is HIDDEN (should not be visible)
   ✅ Check: No "Sign up" link visible
   ```

3. **Test Login Functionality**
   ```
   ✅ Enter: Valid username and password
   ✅ Click: Login
   ✅ Verify: Login works normally
   ✅ Access: Backend or portal as appropriate
   ```

4. **Test Password Reset**
   ```
   ✅ Navigate to: /web/login
   ✅ Click: "Reset Password" (if available)
   ✅ Verify: Password reset still works
   ✅ Or test: Direct URL /web/reset_password
   ```

5. **Inspect Element** (Developer Check)
   ```
   ✅ Right-click on login page: Inspect Element
   ✅ Look for: Elements with 'display: none' or 'signup'
   ✅ Verify: Signup elements are hidden via CSS
   ```

6. **Test User Creation** (Admin)
   ```
   ✅ Login as: Admin
   ✅ Navigate to: Settings → Users → Create
   ✅ Verify: Can still create users manually
   ✅ Create: Test user
   ✅ Send: Invitation email
   ✅ Verify: User receives email
   ```

### Expected Results

- ✅ Signup section completely hidden
- ✅ Login works normally
- ✅ Password reset works
- ✅ No way for public users to self-register
- ✅ Admins can still create users manually

### Failure Scenarios

- ❌ If signup still visible: Clear cache, check template
- ❌ If login broken: Check XPath expression
- ❌ If template error: Review auth_signup_login.xml

---

## 📊 Post-Testing Checklist

### Functionality Verification

- [ ] All 10 implementations working
- [ ] No errors in Odoo logs
- [ ] No JavaScript console errors
- [ ] All forms submitting correctly
- [ ] All redirects working
- [ ] All filters/searches working

### Performance Check

- [ ] Page load times acceptable (< 3 seconds)
- [ ] No slow queries in logs
- [ ] Database queries optimized
- [ ] JavaScript execution smooth
- [ ] No memory leaks

### Cross-Browser Testing

Test in multiple browsers:

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if Mac available)
- [ ] Edge
- [ ] Mobile browsers (Chrome/Safari)

### Responsive Design

Test on different screen sizes:

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

### User Role Testing

Test with different user roles:

- [ ] Administrator
- [ ] Internal User
- [ ] Portal User
- [ ] Education Manager
- [ ] Public/Unauthenticated

### Data Integrity

- [ ] All submissions saved correctly
- [ ] No data loss on form submission
- [ ] Relationships maintained correctly
- [ ] No orphaned records
- [ ] Cascade deletes work if applicable

---

## 🐛 Common Issues & Solutions

### Issue: English numerals not showing

**Solution:**
```bash
# Clear browser cache completely
Ctrl+Shift+Del → Select all time → Clear

# Restart Odoo
sudo systemctl restart odoo

# Force asset rebuild
Settings → Technical → User Interface → Views → Delete edafa_website_branding views
Then refresh browser
```

### Issue: Profile selection 404

**Solution:**
```bash
# Check route registration
grep -r "'/admission/apply'" custo/edafa_website_branding/controllers/

# Verify template exists
ls -la custo/edafa_website_branding/views/profile_selection_template.xml

# Update module
odoo-bin -u edafa_website_branding -d your_database
```

### Issue: Filtering not working

**Solution:**
```
# Check JavaScript console (F12)
# Look for errors

# Verify data-* attributes on elements
# Inspect select elements in browser dev tools

# Check controller returns correct data
# Add logging to controller methods
```

### Issue: Role conversion fails

**Solution:**
```bash
# Check res_users_extended.py loaded
grep "res_users_extended" custo/openeducat_core/models/__init__.py

# Check logs
tail -f /var/log/odoo/odoo-server.log | grep "groups"

# Run test script
odoo-bin shell -c /etc/odoo.conf -d your_database
exec(open('custo/openeducat_core/test_role_conversion.py').read())
```

### Issue: Admission routing wrong

**Solution:**
```python
# Add logging to controller
import logging
_logger = logging.getLogger(__name__)

# In admission_submit method:
_logger.info(f"Selected course: {course_id}, program: {program_id}")
_logger.info(f"Found register: {register.name if register else 'None'}")

# Check logs to see routing logic
```

### Issue: Login signup still showing

**Solution:**
```bash
# Check template loaded
Settings → Technical → Views → Search "login_hide_signup"

# Verify inheritance
# Should show inherited template

# Check module update
odoo-bin -u edafa_website_branding -d your_database

# Clear browser cache
```

---

## 📈 Test Results Documentation

### Template for Test Report

```
Test Date: _______________
Tester Name: _______________
Odoo Version: 19.0
Database: _______________

Implementation Results:
[ ] #1 - English Numerals: PASS / FAIL
[ ] #2 - Profile Selection: PASS / FAIL
[ ] #3 - Course Department: PASS / FAIL
[ ] #4 - Department Programs: PASS / FAIL
[ ] #5 - Admission Filtering: PASS / FAIL
[ ] #6 - Active Programs Filter: PASS / FAIL
[ ] #7 - Label Renaming: PASS / FAIL
[ ] #8 - Role Conversion: PASS / FAIL
[ ] #9 - Admission Routing: PASS / FAIL
[ ] #10 - Login Signup Removal: PASS / FAIL

Issues Found: _______________
_______________
_______________

Overall Status: PASS / FAIL

Notes:
_______________
_______________
_______________
```

---

## 🎯 Success Criteria

### All Tests Must:

✅ Execute without errors  
✅ Produce expected results  
✅ Handle edge cases properly  
✅ Maintain data integrity  
✅ Perform acceptably (< 3sec page loads)  
✅ Work across all browsers  
✅ Be responsive on all devices  
✅ Meet accessibility standards

---

## 📞 Support & Escalation

### Level 1: Documentation
1. Check this testing guide
2. Review implementation MD files
3. Check README.md

### Level 2: Logs & Debug
1. Check Odoo logs
2. Check JavaScript console
3. Enable debug mode (?debug=1)
4. Check database directly

### Level 3: Developer Support
Contact development team with:
- Test details
- Error logs
- Steps to reproduce
- Expected vs actual results
- Screenshots/videos

---

**End of Testing Guide**

**Last Updated:** January 3, 2026  
**Version:** 1.0  
**Status:** Ready for Testing
