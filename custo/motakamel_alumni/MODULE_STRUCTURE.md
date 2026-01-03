# OpenEduCat Alumni Enterprise - Module Structure

## Module Overview

**Module Name**: `openeducat_alumni_enterprise`  
**Version**: 18.0.1.0  
**Category**: Education  
**License**: LGPL-3  
**Author**: OpenEduCat Inc  

## Purpose

This module provides comprehensive alumni management functionality for educational institutions, enabling them to:
- Maintain alumni records and profiles
- Organize alumni events and track attendance
- Facilitate job postings and applications
- Create an engaged alumni community
- Convert graduated students to alumni status

---

## Module Structure

```
openeducat_alumni_enterprise/
│
├── __init__.py                          # Module initialization
├── __manifest__.py                      # Module manifest/configuration
├── README.md                            # Module documentation
├── MODULE_STRUCTURE.md                  # This file
│
├── models/                              # Business logic and data models
│   ├── __init__.py
│   ├── alumni.py                        # Main alumni model (op.alumni)
│   ├── alumni_group.py                  # Alumni groups (op.alumni.group)
│   ├── alumni_event.py                  # Events & registrations
│   ├── alumni_job.py                    # Job postings & applications
│   ├── student.py                       # Student model extension
│   └── res_config_settings.py           # Configuration settings
│
├── controllers/                         # Web controllers
│   ├── __init__.py
│   ├── alumni_portal.py                 # Portal routes for alumni
│   └── alumni_website.py                # Public website routes
│
├── views/                               # XML view definitions
│   ├── alumni_view.xml                  # Alumni list, form, kanban views
│   ├── alumni_group_view.xml            # Alumni group views
│   ├── alumni_event_view.xml            # Event views (list, form, calendar)
│   ├── alumni_job_view.xml              # Job posting views
│   ├── alumni_portal_templates.xml      # Portal page templates
│   └── alumni_website_templates.xml     # Public website templates
│
├── wizard/                              # Transient models (wizards)
│   ├── __init__.py
│   ├── convert_to_alumni_wizard.py      # Student to alumni conversion
│   └── alumni_bulk_email_wizard.py      # Bulk email sender
│
├── security/                            # Access rights and security
│   ├── alumni_security.xml              # Security groups and rules
│   └── ir.model.access.csv              # Model access rights
│
├── data/                                # Data files
│   ├── alumni_sequence.xml              # Number sequences
│   └── alumni_data.xml                  # Default data (groups)
│
├── demo/                                # Demo data (optional)
│   └── alumni_demo.xml                  # Sample alumni records
│
├── report/                              # Reports and templates
│   ├── alumni_report.xml                # Report definitions
│   └── alumni_card_template.xml         # Alumni ID card template
│
├── menus/                               # Menu definitions
│   └── alumni_menu.xml                  # Main menu structure
│
└── static/                              # Static assets
    ├── description/                     # Module description assets
    │   ├── icon.png                     # Module icon
    │   └── openeducat_alumni_enterprise_banner.jpg
    └── src/
        ├── css/                         # Stylesheets
        │   ├── alumni.css               # Backend styles
        │   └── alumni_portal.css        # Portal styles
        └── js/                          # JavaScript files
            └── alumni_dashboard.js      # Dashboard widgets
```

---

## Core Models

### 1. op.alumni
**File**: `models/alumni.py`  
**Description**: Main alumni record model

**Key Fields**:
- `alumni_number`: Unique alumni identifier
- `first_name`, `middle_name`, `last_name`: Name fields
- `email`, `phone`, `mobile`: Contact information
- `course_id`, `batch_id`: Academic information
- `graduation_date`, `grade`, `cgpa`: Graduation details
- `current_company`, `current_designation`: Professional info
- `user_id`: Portal user reference
- `state`: Status (draft/active/inactive)

**Key Methods**:
- `action_activate()`: Activate alumni record
- `action_create_portal_user()`: Create portal access
- `action_view_events()`: View alumni's events
- `action_view_jobs()`: View jobs posted by alumni

---

### 2. op.alumni.group
**File**: `models/alumni_group.py`  
**Description**: Alumni groups/categories

**Key Fields**:
- `name`, `code`: Group identification
- `group_type`: Type (batch/course/interest/location)
- `alumni_ids`: Group members
- `admin_ids`: Group administrators

**Key Methods**:
- `action_view_members()`: View group members

---

### 3. op.alumni.event
**File**: `models/alumni_event.py`  
**Description**: Alumni events management

**Key Fields**:
- `event_number`: Unique event identifier
- `event_type`: Type (reunion/networking/seminar)
- `event_date`, `event_end_date`: Event dates
- `venue`, `is_online`: Location information
- `registration_required`, `max_attendees`: Registration settings
- `state`: Status workflow

**Key Methods**:
- `action_publish()`: Publish event
- `action_open_registration()`: Open registrations
- `action_close_registration()`: Close registrations
- `action_complete_event()`: Mark as completed

---

### 4. op.alumni.event.registration
**File**: `models/alumni_event.py`  
**Description**: Event registrations

**Key Fields**:
- `event_id`, `alumni_id`: Event and alumni references
- `number_of_guests`: Guest count
- `attended`: Attendance flag
- `state`: Registration status

---

### 5. op.alumni.job
**File**: `models/alumni_job.py`  
**Description**: Job postings

**Key Fields**:
- `job_number`: Unique job identifier
- `company_name`: Employer name
- `job_type`: Type (full-time/part-time/contract)
- `location`, `is_remote`: Location details
- `application_deadline`: Deadline date
- `posted_by`: Alumni who posted
- `state`: Status (draft/published/closed)

---

### 6. op.alumni.job.application
**File**: `models/alumni_job.py`  
**Description**: Job applications

**Key Fields**:
- `job_id`, `applicant_id`: Job and applicant references
- `applicant_name`, `applicant_email`: Applicant details
- `resume`: CV attachment
- `state`: Application status

---

## Security Groups

### 1. Alumni User
- **Access**: Read-only access to active alumni records
- **Purpose**: For staff who need to view alumni information

### 2. Alumni Manager
- **Access**: Full CRUD access to all alumni features
- **Purpose**: For administrators managing alumni system

### 3. Portal User (Alumni)
- **Access**: Access to own record and public content
- **Purpose**: For alumni accessing their portal

---

## Workflows

### Student to Alumni Conversion
1. Select graduated students
2. Run "Convert to Alumni" wizard
3. Enter graduation details
4. Optionally create portal user
5. Alumni record created
6. Student marked as alumni

### Event Management
1. Create event (draft)
2. Publish event
3. Open registration
4. Alumni register
5. Close registration
6. Mark event in progress
7. Record attendance
8. Complete event

### Job Posting
1. Alumni creates job posting (draft)
2. Manager reviews and publishes
3. Applicants apply
4. Track applications
5. Close or mark as filled

---

## Key Features

### ✅ Implemented

1. **Alumni Management**
   - Complete alumni profiles
   - Alumni groups
   - Portal access
   - Student conversion

2. **Event Management**
   - Event creation and publishing
   - Online registration
   - Attendance tracking
   - Multiple event types

3. **Job Board**
   - Job posting by alumni
   - Job applications
   - Application tracking
   - Multiple job types

4. **Communication**
   - Bulk email wizard
   - Event notifications
   - Mail tracking

5. **Portal Features**
   - Alumni profile page
   - Event registration
   - Job browsing
   - Profile updates

### 🔄 To Be Implemented (Views)

1. **XML Views**
   - Alumni list/form/kanban views
   - Event calendar view
   - Job board views
   - Portal templates
   - Website templates

2. **Reports**
   - Alumni ID card
   - Directory report
   - Event reports
   - Job analytics

3. **Assets**
   - CSS stylesheets
   - JavaScript widgets
   - Images and icons

---

## Dependencies

### Required Modules
- `openeducat_core`: Core educational management
- `website`: Website functionality
- `portal`: Portal access
- `mail`: Email and messaging

### Python Libraries
- Standard Odoo dependencies

---

## Installation Steps

1. Copy module to addons directory
2. Update apps list
3. Install module
4. Configure security groups
5. Create alumni groups
6. Configure settings

---

## Usage Scenarios

### Scenario 1: Graduation Season
1. Identify graduating students
2. Bulk convert to alumni
3. Send welcome emails
4. Create portal access
5. Add to graduation year group

### Scenario 2: Alumni Reunion
1. Create reunion event
2. Target specific graduation years
3. Publish event
4. Send invitations
5. Track RSVPs
6. Record attendance

### Scenario 3: Job Networking
1. Alumni posts job opportunity
2. Manager approves posting
3. Students/alumni apply
4. Track applications
5. Close when filled

---

## Technical Notes

### Sequences
- Alumni: `ALM/00001`
- Events: `EVT/00001`
- Jobs: `JOB/00001`

### Record Rules
- Users see active alumni only
- Managers have full access
- Portal users see own record

### Computed Fields
- `name`: Computed from first/middle/last name
- `graduation_year`: Extracted from graduation_date
- `event_count`: Count of attended events
- `job_count`: Count of jobs posted

---

## Future Enhancements

1. **Alumni Blog** (separate module)
2. **Alumni Donations** (fundraising)
3. **Mentorship Program**
4. **Alumni Directory Search**
5. **Advanced Analytics**
6. **Mobile App Integration**
7. **Social Media Integration**
8. **Newsletter Management**

---

**Document Version**: 1.0  
**Last Updated**: November 3, 2025  
**Status**: Module Structure Complete - Views Pending

