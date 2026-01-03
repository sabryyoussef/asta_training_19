# Core Models Documentation

## Overview

This document provides comprehensive documentation of all models in the OpenEduCat Core module, including field descriptions, relationships, methods, and usage examples.

---

## Table of Contents

1. [Student Management Models](#student-management-models)
2. [Faculty Management Models](#faculty-management-models)
3. [Academic Structure Models](#academic-structure-models)
4. [Administrative Models](#administrative-models)
5. [Model Relationships](#model-relationships)
6. [Common Patterns](#common-patterns)

---

## Student Management Models

### 1. op.student

**Description**: Main student model containing comprehensive student information

**Inherits**: 
- `mail.thread`: Chatter functionality
- `mail.activity.mixin`: Activity tracking
- `res.partner` (via `_inherits`): Contact information

#### Fields

##### Personal Information
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `first_name` | Char | Student's first name | No | - |
| `middle_name` | Char | Student's middle name | No | - |
| `last_name` | Char | Student's last name | No | - |
| `name` | Char | Full name (inherited from partner) | Yes | - |
| `birth_date` | Date | Date of birth | No | - |
| `gender` | Selection | Gender (m/f/o) | Yes | 'm' |
| `blood_group` | Selection | Blood group (A+, B+, etc.) | No | - |
| `nationality` | Many2one | Nationality (res.country) | No | - |

##### Identification
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `gr_no` | Char | Registration/GR number | No | - |
| `id_number` | Char | ID card number | No | - |
| `certificate_number` | Char | Certificate number | No | - |
| `visa_info` | Char | Visa information | No | - |

##### Relationships
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `partner_id` | Many2one | Related partner record | Yes | - |
| `user_id` | Many2one | Portal user account | No | - |
| `category_id` | Many2one | Student category | No | - |
| `emergency_contact` | Many2one | Emergency contact (res.partner) | No | - |

##### Academic Information
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `course_detail_ids` | One2many | Course enrollments | No | [] |

##### System Fields
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `active` | Boolean | Active status | No | True |

#### Computed Fields

```python
# Name computation from first, middle, last name
@api.onchange('first_name', 'middle_name', 'last_name')
def _onchange_name_1(self):
    fname = self.first_name or ""
    mname = self.middle_name or ""
    lname = self.last_name or ""
    
    if fname or mname or lname:
        self.name = " ".join(filter(None, [fname, mname, lname]))
    else:
        self.name = "New"
```

#### Constraints

```python
# SQL Constraints
_sql_constraints = [(
    'unique_gr_no',
    'unique(gr_no)',
    'Registration Number must be unique per student!'
)]

# Python Constraints
@api.constrains('birth_date')
def _check_birthdate(self):
    for record in self:
        if record.birth_date and record.birth_date > fields.Date.today():
            raise ValidationError("Birth Date can't be greater than current date!")
```

#### Methods

##### create_student_user()
**Purpose**: Create portal user account for student

```python
def create_student_user(self):
    """Create portal user for student"""
    user_group = self.env.ref("base.group_portal")
    users_res = self.env['res.users']
    
    for record in self:
        if not record.user_id:
            user_id = users_res.create({
                'name': record.name,
                'partner_id': record.partner_id.id,
                'login': record.email,
                'groups_id': user_group,
                'is_student': True,
                'tz': self._context.get('tz'),
            })
            record.user_id = user_id
```

##### get_import_templates()
**Purpose**: Provide import template for bulk student import

```python
@api.model
def get_import_templates(self):
    return [{
        'label': _('Import Template for Students'),
        'template': '/openeducat_core/static/xls/op_student.xls'
    }]
```

#### Usage Examples

```python
# Create a student
student = env['op.student'].create({
    'first_name': 'John',
    'middle_name': 'Michael',
    'last_name': 'Doe',
    'birth_date': '2005-01-15',
    'gender': 'm',
    'email': 'john.doe@example.com',
    'phone': '+1234567890',
    'gr_no': 'GR2024001',
    'category_id': category.id,
})

# Create portal user
student.create_student_user()

# Search students
active_students = env['op.student'].search([('active', '=', True)])
male_students = env['op.student'].search([('gender', '=', 'm')])

# Update student
student.write({
    'blood_group': 'A+',
    'nationality': country.id,
})
```

---

### 2. op.student.course

**Description**: Student course enrollment details

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `student_id` | Many2one | Student reference | No | - |
| `course_id` | Many2one | Course reference | Yes | - |
| `batch_id` | Many2one | Batch assignment | No | - |
| `roll_number` | Char | Roll number in batch | No | - |
| `subject_ids` | Many2many | Enrolled subjects | No | [] |
| `academic_years_id` | Many2one | Academic year | No | - |
| `academic_term_id` | Many2one | Academic term | No | - |
| `state` | Selection | Status (running/finished) | No | 'running' |

#### Constraints

```python
_sql_constraints = [
    ('unique_name_roll_number_id',
     'unique(roll_number,course_id,batch_id,student_id)',
     'Roll Number & Student must be unique per Batch!'),
    ('unique_name_roll_number_course_id',
     'unique(roll_number,course_id,batch_id)',
     'Roll Number must be unique per Batch!'),
    ('unique_name_roll_number_student_id',
     'unique(student_id,course_id,batch_id)',
     'Student must be unique per Batch!'),
]
```

#### Usage Examples

```python
# Enroll student in course
enrollment = env['op.student.course'].create({
    'student_id': student.id,
    'course_id': course.id,
    'batch_id': batch.id,
    'roll_number': 'ROLL001',
    'academic_years_id': academic_year.id,
    'academic_term_id': academic_term.id,
    'subject_ids': [(6, 0, subject_ids)],
})

# Get student's active enrollments
active_enrollments = student.course_detail_ids.filtered(
    lambda c: c.state == 'running'
)

# Mark course as finished
enrollment.state = 'finished'
```

---

## Faculty Management Models

### 3. op.faculty

**Description**: Faculty member information

**Inherits**: 
- `mail.thread`
- `mail.activity.mixin`
- `res.partner` (via `_inherits`)

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `first_name` | Char | First name | No | - |
| `middle_name` | Char | Middle name | No | - |
| `last_name` | Char | Last name | No | - |
| `partner_id` | Many2one | Related partner | Yes | - |
| `user_id` | Many2one | User account | No | - |
| `employee_id` | Many2one | Employee record (hr.employee) | No | - |
| `department_id` | Many2one | Department | No | - |
| `active` | Boolean | Active status | No | True |

#### Methods

##### create_employee()
**Purpose**: Create HR employee record for faculty

```python
def create_employee(self):
    """Create employee record for faculty member"""
    for record in self:
        if not record.employee_id:
            employee = self.env['hr.employee'].create({
                'name': record.name,
                'work_email': record.email,
                'work_phone': record.phone,
                'department_id': record.department_id.id,
            })
            record.employee_id = employee.id
```

##### create_faculty_user()
**Purpose**: Create portal user for faculty

```python
def create_faculty_user(self):
    """Create portal user for faculty"""
    user_group = self.env.ref("openeducat_core.group_op_faculty")
    
    for record in self:
        if not record.user_id:
            user = self.env['res.users'].create({
                'name': record.name,
                'partner_id': record.partner_id.id,
                'login': record.email,
                'groups_id': [(6, 0, [user_group.id])],
            })
            record.user_id = user.id
```

#### Usage Examples

```python
# Create faculty member
faculty = env['op.faculty'].create({
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane.smith@university.edu',
    'phone': '+1234567890',
    'department_id': department.id,
})

# Create employee and user accounts
faculty.create_employee()
faculty.create_faculty_user()

# Search faculty by department
dept_faculty = env['op.faculty'].search([
    ('department_id', '=', department.id),
    ('active', '=', True)
])
```

---

## Academic Structure Models

### 4. op.program

**Description**: Academic program definition

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Program name | Yes | - |
| `code` | Char | Program code | Yes | - |
| `department_id` | Many2one | Department | No | - |
| `active` | Boolean | Active status | No | True |

#### Constraints

```python
_sql_constraints = [
    ('unique_program_code',
     'unique(code)',
     'Code should be unique per program!')
]
```

---

### 5. op.course

**Description**: Course catalog and management

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Course name | Yes | - |
| `code` | Char | Course code | Yes | - |
| `parent_id` | Many2one | Parent course | No | - |
| `evaluation_type` | Selection | Evaluation type | Yes | 'normal' |
| `subject_ids` | Many2many | Subjects | No | [] |
| `max_unit_load` | Float | Maximum unit load | No | 0.0 |
| `min_unit_load` | Float | Minimum unit load | No | 0.0 |
| `department_id` | Many2one | Department | No | - |
| `program_id` | Many2one | Program | No | - |
| `active` | Boolean | Active status | No | True |

#### Evaluation Types

| Value | Description |
|-------|-------------|
| `normal` | Normal evaluation |
| `GPA` | Grade Point Average |
| `CWA` | Cumulative Weighted Average |
| `CCE` | Continuous Comprehensive Evaluation |

#### Constraints

```python
_sql_constraints = [
    ('unique_course_code',
     'unique(code)',
     'Code should be unique per course!')
]

@api.constrains('parent_id')
def _check_category_recursion(self):
    if self._has_cycle():
        raise ValidationError(_('You cannot create recursive categories.'))
```

#### Usage Examples

```python
# Create a course
course = env['op.course'].create({
    'name': 'Computer Science',
    'code': 'CS101',
    'program_id': program.id,
    'department_id': department.id,
    'evaluation_type': 'GPA',
    'min_unit_load': 120.0,
    'max_unit_load': 180.0,
    'subject_ids': [(6, 0, subject_ids)],
})

# Search courses by program
program_courses = env['op.course'].search([
    ('program_id', '=', program.id),
    ('active', '=', True)
])
```

---

### 6. op.batch

**Description**: Class/section management

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Batch name | Yes | - |
| `code` | Char | Batch code | Yes | - |
| `course_id` | Many2one | Course | Yes | - |
| `academic_years_id` | Many2one | Academic year | No | - |
| `academic_term_id` | Many2one | Academic term | No | - |
| `start_date` | Date | Start date | No | - |
| `end_date` | Date | End date | No | - |
| `active` | Boolean | Active status | No | True |

#### Constraints

```python
_sql_constraints = [
    ('unique_batch_code',
     'unique(code)',
     'Code should be unique per batch!')
]
```

---

### 7. op.subject

**Description**: Subject/course content management

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Subject name | Yes | - |
| `code` | Char | Subject code | Yes | - |
| `grade_weightage` | Float | Grade weightage | No | 0.0 |
| `type` | Selection | Subject type | No | 'theory' |
| `department_id` | Many2one | Department | No | - |
| `active` | Boolean | Active status | No | True |

#### Subject Types

| Value | Description |
|-------|-------------|
| `theory` | Theory subject |
| `practical` | Practical/Lab subject |
| `both` | Theory and Practical |
| `other` | Other type |

---

## Administrative Models

### 8. op.department

**Description**: Organizational department structure

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Department name | Yes | - |
| `code` | Char | Department code | Yes | - |
| `parent_id` | Many2one | Parent department | No | - |
| `active` | Boolean | Active status | No | True |

---

### 9. op.academic.year

**Description**: Academic year management

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Year name | Yes | - |
| `code` | Char | Year code | Yes | - |
| `date_start` | Date | Start date | Yes | - |
| `date_stop` | Date | End date | Yes | - |
| `current` | Boolean | Current year flag | No | False |
| `active` | Boolean | Active status | No | True |

---

### 10. op.academic.term

**Description**: Academic term/semester management

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Term name | Yes | - |
| `code` | Char | Term code | Yes | - |
| `academic_year_id` | Many2one | Academic year | Yes | - |
| `date_start` | Date | Start date | Yes | - |
| `date_stop` | Date | End date | Yes | - |
| `active` | Boolean | Active status | No | True |

---

### 11. op.category

**Description**: Student classification categories

**Inherits**: `mail.thread`

#### Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `name` | Char | Category name | Yes | - |
| `code` | Char | Category code | Yes | - |
| `active` | Boolean | Active status | No | True |

---

## Model Relationships

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│ op.student  │────────>│ op.student.  │
│             │         │   course     │
└─────────────┘         └──────────────┘
      │                        │
      │                        │
      v                        v
┌─────────────┐         ┌──────────────┐
│ op.category │         │  op.course   │
└─────────────┘         └──────────────┘
                               │
                               │
                               v
                        ┌──────────────┐
                        │  op.program  │
                        └──────────────┘
                               │
                               │
                               v
                        ┌──────────────┐
                        │ op.department│
                        └──────────────┘
```

### Relationship Matrix

| From Model | To Model | Relationship Type | Field Name |
|------------|----------|-------------------|------------|
| op.student | res.partner | Many2one (inherits) | partner_id |
| op.student | res.users | Many2one | user_id |
| op.student | op.category | Many2one | category_id |
| op.student | op.student.course | One2many | course_detail_ids |
| op.student.course | op.student | Many2one | student_id |
| op.student.course | op.course | Many2one | course_id |
| op.student.course | op.batch | Many2one | batch_id |
| op.student.course | op.subject | Many2many | subject_ids |
| op.faculty | res.partner | Many2one (inherits) | partner_id |
| op.faculty | res.users | Many2one | user_id |
| op.faculty | hr.employee | Many2one | employee_id |
| op.faculty | op.department | Many2one | department_id |
| op.course | op.program | Many2one | program_id |
| op.course | op.department | Many2one | department_id |
| op.course | op.subject | Many2many | subject_ids |
| op.batch | op.course | Many2one | course_id |
| op.batch | op.academic.year | Many2one | academic_years_id |
| op.batch | op.academic.term | Many2one | academic_term_id |

---

## Common Patterns

### 1. Creating Records with Portal Access

```python
# Student with portal user
student = env['op.student'].create({
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
})
student.create_student_user()

# Faculty with portal user
faculty = env['op.faculty'].create({
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane@example.com',
})
faculty.create_faculty_user()
```

### 2. Searching with Filters

```python
# Active students in a specific category
students = env['op.student'].search([
    ('active', '=', True),
    ('category_id', '=', category.id)
])

# Faculty by department
faculty = env['op.faculty'].search([
    ('department_id', '=', dept.id),
    ('active', '=', True)
])

# Courses by program
courses = env['op.course'].search([
    ('program_id', '=', program.id),
    ('active', '=', True)
])
```

### 3. Bulk Operations

```python
# Bulk student creation
student_vals = [
    {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
    {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
]
students = env['op.student'].create(student_vals)

# Bulk update
students.write({'category_id': category.id})

# Bulk archive
students.write({'active': False})
```

### 4. Computed Fields Pattern

```python
class OpStudent(models.Model):
    _inherit = 'op.student'
    
    total_courses = fields.Integer(
        'Total Courses',
        compute='_compute_total_courses'
    )
    
    @api.depends('course_detail_ids')
    def _compute_total_courses(self):
        for student in self:
            student.total_courses = len(student.course_detail_ids)
```

---

## Best Practices

### 1. Always Use Constraints
- Add SQL constraints for uniqueness
- Add Python constraints for complex validation
- Provide clear error messages

### 2. Use Proper Field Types
- Use Selection for fixed choices
- Use Many2one for relationships
- Use Computed fields for derived data

### 3. Implement Proper Security
- Define access rights in CSV
- Create record rules for data isolation
- Use groups for field-level security

### 4. Follow Naming Conventions
- Use snake_case for field names
- Prefix custom fields with `x_`
- Use descriptive names

### 5. Add Tracking
- Use `tracking=True` for important fields
- Inherit `mail.thread` for chatter
- Inherit `mail.activity.mixin` for activities

---

**Last Updated**: November 3, 2025  
**Version**: 1.0

