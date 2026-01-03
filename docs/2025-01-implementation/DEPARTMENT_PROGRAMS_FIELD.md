# Department Programs Field

## Overview
Added a Programs field to the Department page to define which programs belong to each department, enabling controlled filtering and proper organizational structure.

## Implementation Date
January 3, 2026

## Module
**openeducat_core**

## Deployment Instructions

```bash
odoo-bin -u openeducat_core -d <database_name>
```

After upgrading, the Programs field will be available on all department forms and lists.

## Changes Made

### Problem
Departments had no way to specify which programs belonged to them, making it difficult to:
- Filter programs by department
- Ensure proper organizational structure
- Control program visibility based on department context

### Solution
Added a Many2many relationship field (`program_ids`) to link multiple programs to a department.

## Files Modified

### 1. `/custo/openeducat_core/models/department.py`

**Added Field**:
```python
program_ids = fields.Many2many(
    'op.program', 
    'department_program_rel', 
    'department_id', 
    'program_id', 
    string='Programs',
    help='Programs that belong to this department'
)
```

**Details**:
- Field Type: Many2many
- Related Model: `op.program`
- Relation Table: `department_program_rel`
- Allows multiple programs per department
- Allows programs to belong to multiple departments

### 2. `/custo/openeducat_core/views/department_view.xml`

**List View**:
- Added Programs column with `many2many_tags` widget
- Shows all programs as colored tags in the department list

**Form View**:
- Added new "Programs" notebook tab
- Contains editable tree view showing:
  - Program name
  - Program code
- Allows adding/removing programs directly from department form

**Search View**:
- Added Programs field for filtering departments by program

## Features

### Department List View
- **Programs Column**: Displays all assigned programs as tags
- Quick visual reference of program assignments
- Color-coded tags for easy identification

### Department Form View
- **Programs Tab**: Dedicated section for managing programs
- **Editable Tree**: Add/remove programs inline
- **Quick View**: See program name and code without leaving form
- Easy program assignment and management

### Search and Filter
- Search departments by program name
- Filter departments containing specific programs
- Improved department discovery

## Use Cases

1. **Program Organization**
   - Group related programs under departments
   - Maintain clear organizational hierarchy

2. **Filtered Lists**
   - Show only programs from a specific department
   - Department-based program selection in forms

3. **Access Control** (future enhancement)
   - Restrict program visibility by department
   - Department-based permissions

4. **Reporting**
   - Programs per department statistics
   - Department-based program analytics

## Database Changes

**New Table**: `department_program_rel`
- Columns:
  - `department_id` (foreign key to op.department)
  - `program_id` (foreign key to op.program)
- Indexes on both foreign keys for performance

## Testing Checklist

- [ ] Programs tab visible on Department form
- [ ] Can add programs to a department
- [ ] Can remove programs from a department
- [ ] Programs display as tags in department list
- [ ] Can search departments by program
- [ ] Multiple departments can share same program
- [ ] Program information displays correctly in editable tree
- [ ] Changes save correctly to database
- [ ] No errors when creating new department
- [ ] No errors when editing existing department

## Future Enhancements

1. **Automatic Course Filtering**
   - Filter courses by department's programs
   - Ensure course-program-department consistency

2. **Student Assignment**
   - Auto-assign students to department based on program
   - Department-based student lists

3. **Access Rules**
   - Department managers see only their programs
   - Role-based program visibility

4. **Smart Defaults**
   - Auto-populate program field when department is selected
   - Context-aware program selection

5. **Validation Rules**
   - Ensure courses belong to programs in same department
   - Prevent orphaned program assignments

## Related Fields

This field complements:
- `department_id` on Course model
- `program_id` on Course model
- Department hierarchies (parent_id)

## Notes

- Programs field is optional (not required)
- Multiple programs can be assigned to one department
- One program can belong to multiple departments
- No impact on existing data (backward compatible)
- Relationship is bi-directional (can be accessed from both sides)

---

**Author**: Edafa Inc  
**License**: LGPL-3
