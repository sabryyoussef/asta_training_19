# Edafa Website Portal

## Overview

This module provides Edafa branding and a complete student admission portal for the Edafa Education Platform. It extends the base OpenEducat admission system with public-facing website functionality.

## Features

### 🎨 Website Branding
- Custom Edafa logo throughout the website
- Branded website name: "Edafa Education Platform"
- Consistent visual identity

### 📝 Public Admission Portal
- **Public Application Form** (`/admission/apply`)
  - Complete student registration form
  - Course and batch selection
  - Photo upload capability
  - Address and contact information collection
  - Real-time form validation
  - Mobile-responsive design

- **Application Status Checker** (`/admission/check-status`)
  - Public page to check application status
  - Search by application number and email
  - No login required

- **Thank You Page**
  - Confirmation after successful submission
  - Display application number for reference
  - Next steps information

### 🔐 Portal Features (for logged-in users)
- **My Applications** (`/my/applications`)
  - View all submitted applications
  - Track application status
  - Sortable and filterable list

- **Application Details** (`/my/application/{id}`)
  - Detailed view of individual applications
  - Complete application information
  - Status tracking

## Installation

### Prerequisites
- Odoo 18
- `openeducat_core` module installed
- `openeducat_admission` module installed
- `portal` module (standard Odoo)
- `website` module (standard Odoo)

### Installation Steps

1. **Install dependencies first:**
   ```bash
   python3 odoo18/odoo-bin -c odoo.conf/odoo.conf -d edu_demo \
     -i openeducat_core,openeducat_admission --stop-after-init
   ```

2. **Install this module:**
   ```bash
   python3 odoo18/odoo-bin -c odoo.conf/odoo.conf -d edu_demo \
     -i edafa_website_branding --stop-after-init
   ```

3. **Restart your server:**
   ```bash
   python3 odoo18/odoo-bin -c odoo.conf/odoo.conf
   ```

## Usage

### For Website Visitors

1. **Apply for Admission:**
   - Go to website homepage
   - Click "Apply Now" in the header menu
   - Fill out the application form
   - Submit and receive an application number

2. **Check Application Status:**
   - Click "Check Status" in the header menu
   - Enter application number and email
   - View current status

### For Registered Users

1. **Log in to your portal account**
2. **Navigate to "My Applications"**
3. **View all your submitted applications**
4. **Click on any application to see details**

### For Administrators

1. **Go to Admission → Admissions** in the backend
2. **Review applications submitted through the website**
3. **Process applications (Submit → Confirm → Admission)**
4. **Applicants can track status changes in real-time**

## Technical Details

### Module Structure
```
edafa_website_branding/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── admission_portal.py       # Website routes and logic
├── data/
│   ├── website_data.xml           # Website configuration
│   └── website_menu.xml           # Website menu items
├── models/
│   ├── __init__.py
│   └── website.py                 # Website model extensions
├── security/
│   └── ir.model.access.csv        # Access rights
├── static/
│   ├── description/
│   │   └── icon.png               # Module icon
│   └── src/
│       ├── css/
│       │   └── admission_portal.css
│       ├── img/
│       │   └── edafa_logo.svg
│       └── js/
│           └── admission_form.js  # Form validation and enhancements
└── views/
    ├── admission_portal_templates.xml    # Main form template
    ├── admission_thank_you_template.xml  # Success page
    ├── my_applications_template.xml      # Portal views
    └── website_assets.xml                # Asset bundles
```

### Key Routes

| Route | Auth | Description |
|-------|------|-------------|
| `/admission/apply` | Public | Student application form |
| `/admission/submit` | Public | Form submission handler |
| `/admission/thank-you` | Public | Success confirmation page |
| `/admission/check-status` | Public | Application status checker |
| `/my/applications` | User | List of user's applications |
| `/my/application/{id}` | User | Application detail view |

### Application States

1. **Draft** - Initial state (not used in web portal)
2. **Submit** - Application submitted through website
3. **Confirm** - Application confirmed by admin
4. **Admission** - Student admitted
5. **Reject** - Application rejected
6. **Pending** - Awaiting decision

### Form Validation

The module includes client-side and server-side validation:
- Required field checking
- Email format validation
- Phone number format validation
- Age verification (minimum 16 years)
- Image file type validation

### Security

- Public users can create admission records
- Public users can read courses and batches (read-only)
- Portal users can only view their own applications
- CSRF protection on all forms

## Customization

### Change Branding

Edit `data/website_data.xml` to modify website name and domain.

### Add Custom Fields to Form

1. Extend the template in `views/admission_portal_templates.xml`
2. Update the controller in `controllers/admission_portal.py`
3. Ensure fields exist in `op.admission` model

### Modify Styling

Edit `static/src/css/admission_portal.css` for custom styles.

### Email Notifications

To enable email notifications upon submission, create an email template with ID `admission_confirmation_email`.

## Support

For issues or questions:
- Check the Odoo logs for errors
- Review the browser console for JavaScript errors
- Ensure all dependencies are installed
- Verify access rights in Settings → Technical → Security

## License

LGPL-3

## Author

Edafa Inc  
Website: https://www.edafa.org

## Version

18.0.1.0 - Odoo 18 Compatible

