# Motakamel Alumni Management Module

## Overview

The **Motakamel Alumni** module provides comprehensive alumni management functionality for educational institutions. It enables institutions to maintain relationships with graduated students, organize events, facilitate job postings, and create an engaged alumni community.

## Features

### 1. Alumni Management
- **Alumni Records**: Complete alumni profiles with academic and professional information
- **Alumni Directory**: Searchable directory of all alumni
- **Alumni Groups**: Organize alumni by batch, course, location, or interest
- **Portal Access**: Alumni can access their portal to update information

### 2. Alumni Events
- **Event Management**: Create and manage alumni events (reunions, networking, seminars)
- **Event Registration**: Alumni can register for events online
- **RSVP Tracking**: Track event registrations and attendance
- **Event Types**: Support for various event types (reunion, networking, fundraiser, etc.)

### 3. Alumni Job Board
- **Job Postings**: Alumni can post job opportunities
- **Job Applications**: Students and alumni can apply for jobs
- **Job Categories**: Organize jobs by type (full-time, part-time, internship, etc.)
- **Application Tracking**: Track job applications and their status

### 4. Student to Alumni Conversion
- **Bulk Conversion**: Convert multiple students to alumni at once
- **Graduation Information**: Record graduation date, grade, CGPA
- **Automatic Portal Creation**: Optionally create portal access during conversion

### 5. Communication
- **Bulk Email**: Send emails to selected alumni or groups
- **Event Notifications**: Automatic notifications for event invitations
- **Newsletter Support**: Communicate with alumni community

## Installation

1. Copy the module to your Odoo addons directory:
   ```
   /path/to/odoo/addons/motakamel_alumni
   ```

2. Update the apps list in Odoo:
   - Go to Apps menu
   - Click "Update Apps List"

3. Search for "Motakamel Alumni" and install

## Dependencies

- `openeducat_core` - OpenEduCat Core module
- `website` - Odoo Website module
- `portal` - Odoo Portal module
- `mail` - Odoo Mail module

## Configuration

### Initial Setup

1. **Security Groups**:
   - Navigate to Settings > Users & Companies > Groups
   - Assign users to "Alumni User" or "Alumni Manager" groups

2. **Alumni Groups**:
   - Navigate to Alumni > Configuration > Alumni Groups
   - Create groups for different batches, courses, or interests

3. **Settings**:
   - Navigate to Settings > OpenEduCat > Alumni
   - Configure auto portal creation settings

### Converting Students to Alumni

1. Navigate to Students menu
2. Select students who have graduated
3. Click Action > Convert to Alumni
4. Fill in graduation details (date, grade, CGPA)
5. Choose whether to create portal access
6. Click "Convert"

## Usage

### For Alumni Managers

#### Creating Alumni Records
1. Navigate to Alumni > Alumni
2. Click "Create"
3. Fill in alumni information
4. Set status to "Active"
5. Save

#### Managing Events
1. Navigate to Alumni > Events
2. Click "Create"
3. Fill in event details (name, date, venue, type)
4. Set registration requirements
5. Publish event
6. Track registrations and attendance

#### Managing Job Postings
1. Navigate to Alumni > Jobs
2. Review job postings from alumni
3. Approve/reject postings
4. Monitor applications

### For Alumni (Portal Users)

#### Accessing Portal
1. Log in to the portal using credentials
2. Navigate to "My Alumni" section

#### Updating Profile
1. Go to My Alumni > Profile
2. Update professional information
3. Add current company and designation
4. Update contact information

#### Registering for Events
1. Go to My Alumni > Events
2. Browse available events
3. Click "Register" on desired event
4. Fill in registration details
5. Submit registration

#### Posting Jobs
1. Go to My Alumni > Jobs
2. Click "Post a Job"
3. Fill in job details
4. Submit for approval

## Models

### Main Models

1. **op.alumni**: Alumni records
2. **op.alumni.group**: Alumni groups/categories
3. **op.alumni.event**: Alumni events
4. **op.alumni.event.registration**: Event registrations
5. **op.alumni.job**: Job postings
6. **op.alumni.job.application**: Job applications

## Views

### Backend Views
- Alumni List View
- Alumni Form View
- Alumni Kanban View
- Event Calendar View
- Job Board View

### Portal Views
- Alumni Profile Page
- Events Listing
- Event Registration
- Jobs Listing
- Job Application

### Website Views
- Public Alumni Directory
- Public Events Page
- Public Jobs Board

## Security

### Access Rights
- **Alumni User**: Read access to alumni records and events
- **Alumni Manager**: Full access to all alumni features
- **Portal User**: Access to own alumni record and public content

### Record Rules
- Users can view all active alumni
- Managers have full access
- Portal users can only access their own records

## Reports

1. **Alumni Card**: Printable alumni ID card
2. **Alumni Directory Report**: Complete alumni listing
3. **Event Attendance Report**: Event participation statistics
4. **Job Posting Report**: Job board analytics

## Technical Details

### Module Structure
```
motakamel_alumni/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── alumni.py
│   ├── alumni_group.py
│   ├── alumni_event.py
│   ├── alumni_job.py
│   ├── student.py
│   └── res_config_settings.py
├── controllers/
│   ├── __init__.py
│   ├── alumni_portal.py
│   └── alumni_website.py
├── views/
│   ├── alumni_view.xml
│   ├── alumni_group_view.xml
│   ├── alumni_event_view.xml
│   ├── alumni_job_view.xml
│   ├── alumni_portal_templates.xml
│   └── alumni_website_templates.xml
├── wizard/
│   ├── __init__.py
│   ├── convert_to_alumni_wizard.py
│   └── alumni_bulk_email_wizard.py
├── security/
│   ├── alumni_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── alumni_sequence.xml
│   └── alumni_data.xml
├── report/
│   ├── alumni_report.xml
│   └── alumni_card_template.xml
└── static/
    ├── description/
    └── src/
        ├── css/
        └── js/
```

## Support

For support and documentation:
- Website: https://www.motakamel.com
- Email: support@motakamel.com

## License

LGPL-3

## Author

Motakamel Training Academy

## Version

18.0.1.0

