# Automatic Portal Access on Student Enrollment

## Overview
When a student is enrolled through the admission process, the system automatically creates portal user access for them, allowing them to log in and access their student portal.

## Implementation

### Modified Files

#### 1. `/custo/openeducat_admission/models/admission.py`
**Method**: `enroll_student()`

**Changes**:
- Added automatic portal user creation after student enrollment
- Handles both new student creation and existing student enrollment
- Creates portal access only if the student doesn't already have a user account

```python
# When new student is created
if record.student_id and not record.student_id.user_id:
    record.student_id.create_student_user()

# When existing student is enrolled in new course
if record.student_id and not record.student_id.user_id:
    record.student_id.create_student_user()
```

#### 2. `/custo/openeducat_core/models/student.py`
**Method**: `create_student_user()`

**Enhancements**:
- Updated for Odoo 19 compatibility
- Fixed portal group assignment using inverse relationship
- Added automatic password reset email
- Improved error handling and logging
- Email validation before user creation

**Key Features**:
1. **Odoo 19 Compatibility**: Uses `portal_group.write({'users': [(4, user_id.id)]})` instead of direct `groups_id` assignment
2. **Email Requirement**: Only creates portal user if student has an email address
3. **Password Reset**: Automatically sends password reset email to student
4. **Error Handling**: Graceful error handling with detailed logging
5. **Logging**: Comprehensive logging for troubleshooting

## How It Works

### Enrollment Flow
```
1. Admission → Click "Enroll Student" button
   ↓
2. Student record created/updated
   ↓
3. System checks if student has portal user
   ↓
4. If NO user exists:
   - Create res.users record
   - Assign portal group
   - Send password reset email
   ↓
5. Student receives email with login link
```

### User Creation Process
```python
# 1. Create user (without groups)
user_id = users_res.create({
    'name': record.name,
    'partner_id': record.partner_id.id,
    'login': record.email,
    'is_student': True,
})

# 2. Assign portal group (Odoo 19 compatible)
portal_group.write({'users': [(4, user_id.id)]})

# 3. Send password reset email
user_id.action_reset_password()
```

## Requirements

### Student Email
- Student **must have an email address** for portal user creation
- Email is used as login credential
- Password reset instructions sent to this email

### Portal Group
- System must have `base.group_portal` available
- This is a standard Odoo group

## Benefits

### For Students
✅ **Automatic Access**: No manual intervention needed
✅ **Email Notification**: Receive password setup instructions automatically
✅ **Immediate Access**: Can log in right after enrollment
✅ **Self-Service**: Set their own password via email link

### For Administrators
✅ **No Manual Work**: Portal users created automatically
✅ **Consistent Process**: Same flow for all students
✅ **Error Logging**: Issues are logged for troubleshooting
✅ **Graceful Handling**: System continues even if email fails

## Portal Access After Enrollment

Once enrolled, students can:
1. Receive password reset email
2. Click the link to set password
3. Log in at: `https://your-domain.com/web/login`
4. Access student portal features:
   - View personal information
   - Check course enrollments
   - View grades and attendance
   - Download documents
   - Submit applications

## Error Scenarios

### No Email Address
- Portal user is **not created**
- Warning logged: `"Cannot create portal user: No email address"`
- Student can still be enrolled (user creation skipped)

### Group Assignment Fails
- User is created but without portal group
- Error logged with details
- Administrator can manually assign group later

### Email Send Fails
- User and group are created successfully
- Email sending fails (logged as warning)
- Student can use "Reset Password" on login page

## Manual Portal Creation

If automatic creation fails or is skipped, you can manually create portal access:

### Method 1: Via Student Record
1. Open student record
2. Navigate to "Users" tab (if available)
3. Click "Create Portal User" button (from wizard)

### Method 2: Via Wizard
1. Select student(s) from list view
2. Action → "Create Portal User"
3. Wizard creates users for selected students

### Method 3: Via Partner
1. Open student's partner record
2. Click "Grant Portal Access" button
3. Send invitation

## Testing

### Test Automatic Creation
1. Create admission application
2. Fill in student email address
3. Click "Enroll Student"
4. Verify:
   - Student record created
   - User record created (student.user_id)
   - Portal group assigned
   - Email sent

### Verify Portal Access
1. Check email inbox (student email)
2. Click password reset link
3. Set password
4. Log in to portal
5. Verify student can access their dashboard

## Configuration

No additional configuration needed. The feature works automatically when:
- ✅ Student has email address
- ✅ System has portal module installed
- ✅ Email server is configured (for password reset)

## Logging

All actions are logged for troubleshooting:

```
INFO: Portal access created for student: John Doe (ID: 123)
INFO: Password reset email sent to: john.doe@example.com
WARNING: Could not send password reset email to john@example.com: [reason]
ERROR: Could not create portal user for student Jane Smith: [error details]
```

Check logs at: **Settings → Technical → Logging**

## Odoo 19 Compatibility Notes

This implementation is fully compatible with Odoo 19's group assignment restrictions:

- ✅ Uses inverse relationship (group.users) instead of user.groups_id
- ✅ Avoids "cannot be at the same time in exclusive groups" error
- ✅ Proper error handling for group assignment
- ✅ Follows Odoo 19 best practices

## Related Documentation

- [Student Portal Access Guide](../openeducat_core/static/doc/README.md#student-portal-features)
- [Admission Module Docs](static/doc/README.md)
- [Role Conversion Fix](../openeducat_core/ROLE_CONVERSION_IMPLEMENTATION.md)
