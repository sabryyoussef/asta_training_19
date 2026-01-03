# Department-Based Admission Filtering

## Overview
Made Department selection mandatory and the first step in the student application process, with automatic filtering of Programs and Courses based on the selected Department.

## Implementation Date
January 3, 2026

## Module
**edafa_website_branding**

## Deployment Instructions

```bash
odoo-bin -u edafa_website_branding -d <database_name>
```

After upgrading, the Department field will appear in the admission form and filtering will work automatically.

## Changes Made

### Problem
The admission process didn't enforce department selection, leading to:
- Unorganized applications without clear department assignment
- Students seeing all programs and courses regardless of department
- No way to control or filter program/course visibility by department
- Difficult to manage applications at department level
- Programs showing up even if they had no active courses

### Solution
1. Added mandatory `department_id` field to admission model
2. Placed Department selection as the first field in the Academic Information step
3. Implemented cascading filters: Department → Programs → Courses
4. Added JavaScript-based dynamic filtering in the frontend
5. Updated backend validation to require department selection
6. Filter programs to show only those with available and active courses

## Files Modified

### 1. `/custo/edafa_website_branding/models/admission_extended.py`

**Added Field**:
```python
department_id = fields.Many2one(
    'op.department',
    string='Department',
    required=True,
    tracking=True,
    help="Department for this admission - determines available programs and courses"
)
```

**Added Onchange Methods**:
- `_onchange_department_id()`: Filters programs and courses when department changes
- `_onchange_program_id()`: Further filters courses when program changes
- Both methods return domain filters to restrict available options

### 2. `/custo/edafa_website_branding/controllers/admission_portal.py`

**admission_form_student route**:
- Added departments to context for template rendering
- Passes all departments to populate the dropdown
- Filters programs to show only those with at least one active course
- Uses `courses.mapped('program_id')` to get program IDs from active courses
- Ensures students only see programs they can actually enroll in

**admission_submit route**:
- Added department_id validation (required field)
- Extracts and validates department_id from form submission
- Includes department_id in admission record creation

### 3. `/custo/edafa_website_branding/views/admission_wizard_templates.xml`

**Template Changes**:
- Added Department dropdown as first field in Step 3 (Academic Information)
- Made Department field required with visual indicator
- Updated Program dropdown:
  - Initially disabled until department is selected
  - Added `data-department` attribute to each option for filtering
- Updated Course dropdown:
  - Initially disabled until department is selected
  - Added `data-department` and `data-program` attributes for filtering

**JavaScript Filtering Logic**:
```javascript
// When department changes:
- Reset program and course selections
- Enable program dropdown
- Show only programs linked to selected department
- Enable course dropdown
- Show only courses linked to selected department

// When program changes:
- Reset course selection
- Filter courses by both department AND program
```

## User Experience

### Step-by-Step Process:

1. **Department Selection** (Required):
   - User arrives at Step 3: Academic Information
   - Must select a department first
   - Program and Course dropdowns are disabled with message "Select Department first..."

2. **Program Selection** (Optional):
   - After selecting department, Program dropdown enables
   - Shows only programs linked to the selected department
   - Empty programs list if department has no linked programs
   - Dropdown shows "Select Program..."

3. **Course Selection** (Optional):
   - Course dropdown enables after department selection
   - Shows only courses where `department_id` matches selection
   - If program is also selected, shows only courses matching both department AND program
   - Automatically updates when department or program changes

4. **Dynamic Filtering**:
   - All filtering happens instantly without page reload
   - Options are shown/hidden using CSS display property
   - Previously selected values are cleared when parent changes

## Filtering Logic

### Active Programs Only:
- Programs are filtered to show only those with active courses
- Query: `program_id IN (SELECT DISTINCT program_id FROM op_course WHERE active=True)`
- Empty programs (no courses) are automatically excluded

### Department → Programs:
- Programs are filtered using the `department_program_rel` Many2many relationship
- Only programs where `program.id IN department.program_ids` are shown
- Programs must also have at least one active course

### Department → Courses:
- Courses are filtered by `course.department_id == department.id`
- Only active courses are shown (`course.active == True`)

### Department + Program → Courses:
- Courses filtered by both:
  - `course.department_id == department.id` AND
  - `course.program_id == program.id` AND
  - `course.active == True`

## Data Attributes

Each option element includes data attributes for filtering:

**Program options**:
```html
<option value="1" data-department="3,5">Program Name</option>
```
- `data-department`: Comma-separated list of department IDs this program belongs to

**Course options**:
```html
<option value="10" data-department="3" data-program="1">Course Name</option>
```
- `data-department`: Single department ID
- `data-program`: Single program ID (or empty if no program assigned)

## Validation

### Frontend Validation:
- Department field has `required="required"` attribute
- HTML5 validation prevents form submission without department
- Visual feedback with `.is-invalid` class for empty required fields

### Backend Validation:
- Controller checks `if not post.get('department_id')`
- Returns error: "Department is required."
- Prevents admission creation without department

## Testing Checklist

- [ ] Department dropdown appears first in Academic Information step
- [ ] Department field is marked as required
- [ ] Cannot submit form without selecting department
- [ ] Program dropdown disabled until department selected
- [ ] Course dropdown disabled until department selected
- [ ] Selecting department enables both Program and Course dropdowns
- [ ] Program dropdown shows only programs linked to department
- [ ] Course dropdown shows only courses from selected department
- [ ] Selecting program further filters courses
- [ ] Changing department resets program and course selections
- [ ] Changing program resets course selection
- [ ] Form submission includes department_id
- [ ] Admission record created with correct department
- [ ] Validation error if department not selected

## Database Impact

**New Column**: `department_id` on `op.admission` table
- Type: Integer (foreign key to op.department)
- Required: True
- Indexed: Automatically (foreign key)

## Benefits

1. **Organized Applications**:
   - Every application assigned to a department
   - Easy to filter and manage by department

2. **Controlled Visibility**:
   - Students see only relevant programs and courses
   - Programs shown only if they have active courses available
   - Reduces confusion with irrelevant or empty options

3. **Data Integrity**:
   - Ensures course-program-department relationships are maintained
   - Prevents mismatched selections
   - No empty or inactive programs shown

4. **Better Reporting**:
   - Department-based admission statistics
   - Track applications by department
   - Accurate program enrollment forecasting

5. **Improved UX**:
   - Progressive disclosure (show options as needed)
   - Fewer overwhelming choices
   - Clear selection flow
   - Only actionable options displayed

## Future Enhancements

1. **Smart Defaults**:
   - Auto-select program if department has only one
   - Auto-select course if filtered list has only one option

2. **Visual Indicators**:
   - Show count of available options (e.g., "3 programs available")
   - Display department description or logo

3. **Batch Operations**:
   - Bulk assign departments to existing admissions
   - Migration tool for legacy data

4. **Access Control**:
   - Department-based user permissions
   - Restrict users to their department's applications

5. **Analytics**:
   - Department-wise conversion rates
   - Popular program/course combinations by department

## Notes

- Department field uses existing `op.department` model
- Leverages existing `program_ids` field added to departments
- Filtering is client-side for instant response
- No AJAX calls needed - all data loaded on page load
- Compatible with existing admission workflow

---

**Author**: Edafa Inc  
**License**: LGPL-3
