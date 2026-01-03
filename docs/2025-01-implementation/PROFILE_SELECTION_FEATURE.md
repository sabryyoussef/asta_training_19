# Profile Type Selection Feature

## Overview
This feature adds a profile type selection flow to the admission/application process, allowing users to identify themselves as either a **Student** or **Trainer** before proceeding with the appropriate application path.

## Implementation Date
January 3, 2026

## Module
**edafa_website_branding**

## Deployment Instructions

```bash
odoo-bin -u edafa_website_branding -d <database_name>
```

After upgrading, clear assets cache:
- Settings > Technical > Database Structure > Clear Assets Cache
- Or restart with `--dev=all` flag

## Features

### 1. Profile Selection Page
- **Route**: `/admission/apply` (main entry point)
- **Template**: `profile_selection_template.xml`
- Modern, card-based interface with two options:
  - Student profile
  - Trainer profile
- Responsive design with hover animations
- Clear call-to-action buttons

### 2. Student Flow
- **Route**: `/admission/apply/student`
- **Behavior**: Redirects to the existing multi-step student admission wizard
- Process remains unchanged from original implementation
- Includes all student admission fields and validation

### 3. Trainer Flow
- **Route**: `/admission/apply/trainer`
- **Logic**: 
  1. Checks if `hr_recruitment` module is installed
  2. **If recruitment module installed**:
     - Redirects directly to `/jobs` page (HR recruitment)
  3. **If recruitment module NOT installed**:
     - Redirects to `/contactus` page
     - Allows manual inquiry process

## Files Created/Modified

### New Files Created:
1. **`custo/edafa_website_branding/views/profile_selection_template.xml`**
   - Main profile selection page
   - Card-based UI for Student/Trainer choice
   - Responsive design with animations

2. **`custo/edafa_website_branding/views/trainer_recruitment_template.xml`**
   - Trainer information and benefits page
   - Links to job listings (if recruitment installed)
   - Fallback contact options

### Modified Files:
3. **`custo/edafa_website_branding/controllers/admission_portal.py`**
   - Updated main `/admission/apply` route to show profile selection
   - Added `/admission/apply/student` route for student applications
   - Added `/admission/apply/trainer` route with conditional logic

4. **`custo/edafa_website_branding/__manifest__.py`**
   - Added new template files to data section

## Route Structure

```
/admission/apply
├── Student Selected → /admission/apply/student
│   └── Multi-step admission wizard (existing)
│
└── Trainer Selected → /admission/apply/trainer
    ├── If hr_recruitment installed → /jobs (direct redirect)
    └── If hr_recruitment NOT installed → /contactus (direct redirect)
```

## Testing Checklist

- [ ] Profile selection page displays correctly at `/admission/apply`
- [ ] Student card links to student admission wizard
- [ ] Trainer card behavior with recruitment module installed
- [ ] Trainer card behavior without recruitment module
- [ ] Responsive design on mobile devices
- [ ] Card hover animations work smoothly
- [ ] Links in website menu function correctly
- [ ] Contact us fallback works properly
- [ ] Recruitment info page displays correctly (if applicable)
- [ ] Back navigation works from all pages

## Dependencies

- **Required**: 
  - openeducat_core
  - openeducat_admission
  - website
  - portal

- **Optional**:
  - hr_recruitment (for trainer job listings)

---

**Author**: Edafa Inc  
**License**: LGPL-3
