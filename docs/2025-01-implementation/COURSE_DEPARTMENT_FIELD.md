# Course Department Field Visibility

## Overview
Made the Department field visible on the Course Creation page by removing security group restrictions.

## Implementation Date
January 3, 2026

## Module
**openeducat_core**

## Deployment Instructions

```bash
odoo-bin -u openeducat_core -d <database_name>
```

After upgrading, the Department field will be immediately visible without needing to clear cache.

## Changes Made

### Problem
The Department field (`department_id`) existed in the `op.course` model but was hidden behind the `group_multi_department` security group, making it invisible to most users.

### Solution
Removed the `groups="openeducat_core.group_multi_department"` attribute from the Department field in both list and form views.

## Files Modified

### `/custo/openeducat_core/views/course_view.xml`

**List View (Tree)**:
- **Before**: `<field name="department_id" groups="openeducat_core.group_multi_department"/>`
- **After**: `<field name="department_id"/>`

**Form View**:
- **Before**: `<field name="department_id" groups="openeducat_core.group_multi_department"/>`
- **After**: `<field name="department_id"/>`

## Affected Views

1. **Course List View** (`view_op_course_tree`)
   - Department column now visible in the course list for all users

2. **Course Form View** (`view_op_course_form`)
   - Department field now visible when creating/editing courses for all users

3. **Course Search View** (`view_op_course_search`)
   - Department field was already searchable (no change needed)

## Field Details

- **Field Name**: `department_id`
- **Field Type**: Many2one
- **Related Model**: `op.department`
- **Default Value**: Current user's department (if set)
- **Location in Form**: Left column, after "Min Unit Load"

## Testing Checklist

- [ ] Department field visible in Course creation form
- [ ] Department field visible in Course list view
- [ ] Department dropdown populated with available departments
- [ ] Can successfully save a Course with a Department selected
- [ ] Can successfully save a Course without a Department (field is optional)
- [ ] Department field searchable in Course search view
- [ ] Department field visible for all user roles (not just multi-department group)

## Notes

- The field was already present in the model, so no database migration is needed
- The field is optional (not required)
- The default value comes from the current user's department if they have one assigned
- No security implications - the field was only hidden in the UI, not protected at the data level

---

**Author**: Edafa Inc  
**License**: LGPL-3
