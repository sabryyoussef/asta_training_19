# Profile Type Selection Feature

## Overview
This feature adds a profile type selection flow to the admission/application process, allowing users to identify themselves as either a **Student** or **Trainer** before proceeding with the appropriate application path.

## Implementation Date
January 3, 2026

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
     - Shows trainer recruitment information page
     - Provides link to `/jobs` page
     - Displays benefits and requirements
  3. **If recruitment module NOT installed**:
     - Redirects to `/contactus` page
     - Allows manual inquiry process

## Files Created/Modified

### New Files Created:
1. **`views/profile_selection_template.xml`**
   - Main profile selection page
   - Card-based UI for Student/Trainer choice
   - Responsive design with animations

2. **`views/trainer_recruitment_template.xml`**
   - Trainer information and benefits page
   - Links to job listings (if recruitment installed)
   - Fallback contact options

### Modified Files:
3. **`controllers/admission_portal.py`**
   - Updated main `/admission/apply` route to show profile selection
   - Added `/admission/apply/student` route for student applications
   - Added `/admission/apply/trainer` route with conditional logic:
     - Checks for hr_recruitment module installation
     - Routes to jobs page or contact us accordingly

4. **`__manifest__.py`**
   - Added new template files to data section
   - Proper loading order maintained

## Route Structure

```
/admission/apply
├── Student Selected → /admission/apply/student
│   └── Multi-step admission wizard (existing)
│
└── Trainer Selected → /admission/apply/trainer
    ├── If hr_recruitment installed
    │   ├── Shows recruitment info page
    │   └── Link to /jobs page
    │
    └── If hr_recruitment NOT installed
        └── Redirect to /contactus
```

## Technical Details

### Profile Selection Page Features:
- **Student Card**:
  - Graduation cap icon
  - List of student benefits
  - Blue primary button
  - Links to `/admission/apply/student`

- **Trainer Card**:
  - Chalkboard teacher icon
  - List of trainer benefits
  - Green success button
  - Links to `/admission/apply/trainer`

### Recruitment Module Detection:
```python
recruitment_module = request.env['ir.module.module'].sudo().search([
    ('name', '=', 'hr_recruitment'),
    ('state', '=', 'installed')
], limit=1)
```

### Conditional Routing Logic:
- If recruitment module exists:
  - Render trainer recruitment info template
  - Provide "View Open Positions" button → `/jobs`
  - Provide "Contact HR" button → `/contactus`

- If recruitment module doesn't exist:
  - Direct redirect to `/contactus`
  - Users can inquire manually about trainer positions

## User Experience Flow

### For Students:
1. Visit `/admission/apply`
2. See profile selection page
3. Click "Apply as Student"
4. Proceed to multi-step admission wizard
5. Complete application as before

### For Trainers (with recruitment):
1. Visit `/admission/apply`
2. See profile selection page
3. Click "Apply as Trainer"
4. See trainer benefits and information
5. Click "View Open Positions" → go to `/jobs`
6. Apply for specific trainer positions
7. Alternatively, click "Contact HR" for inquiries

### For Trainers (without recruitment):
1. Visit `/admission/apply`
2. See profile selection page
3. Click "Apply as Trainer"
4. Automatically redirected to `/contactus`
5. Fill out contact form to inquire about trainer positions

## CSS Styling

Custom styles included in profile selection template:
- Card hover effects with elevation
- Smooth transitions
- Pulse animation on icons
- Responsive button styling
- Mobile-friendly layout

## Backward Compatibility

- Original `/admission/apply/student` route preserves all existing functionality
- Student admission wizard remains unchanged
- Classic single-page form still accessible via `/admission/apply/classic`
- Existing "Apply Now" links throughout site work correctly

## Integration Points

### Website Menu:
- Main "Apply Now" menu item points to `/admission/apply`
- Shows profile selection as first step

### Portal:
- "My Applications" page links maintained
- "Apply Now" alerts point to profile selection

### Recruitment Module:
- Optional integration with hr_recruitment
- Graceful fallback if not installed
- No hard dependency required

## Testing Checklist

- [ ] Profile selection page displays correctly
- [ ] Student card links to student admission wizard
- [ ] Trainer card behavior with recruitment module installed
- [ ] Trainer card behavior without recruitment module
- [ ] Responsive design on mobile devices
- [ ] Card hover animations work smoothly
- [ ] Links in website menu function correctly
- [ ] Contact us fallback works properly
- [ ] Recruitment info page displays correctly (if applicable)
- [ ] Back navigation works from all pages

## Configuration

No additional configuration required. The feature works out of the box:

1. **With hr_recruitment module**:
   - Install hr_recruitment module
   - Configure job positions in HR > Recruitment
   - Trainer applicants will see recruitment info and job links

2. **Without hr_recruitment module**:
   - No installation needed
   - Trainer applicants automatically redirected to contact page
   - Manual inquiry process through contact form

## Future Enhancements

Potential improvements for future versions:

1. **Email notifications**: Send different welcome emails based on profile type
2. **Analytics tracking**: Track which profile types are selected
3. **Custom trainer application form**: Build dedicated trainer onboarding flow
4. **Multi-language support**: Translate profile selection page
5. **Additional profiles**: Add more profile types (e.g., Partner, Sponsor)
6. **Direct application**: Allow trainers to apply inline without recruitment module

## Dependencies

- **Required**: 
  - openeducat_core
  - openeducat_admission
  - website
  - portal

- **Optional**:
  - hr_recruitment (for trainer job listings)

## Deployment Instructions

1. **Update the module**:
   ```bash
   odoo-bin -u edafa_website_branding -d <database_name>
   ```

2. **Clear assets cache**:
   - Settings > Technical > Database Structure > Clear Assets Cache
   - Or restart with `--dev=all` flag

3. **Verify routes**:
   - Visit `/admission/apply` to see profile selection
   - Test both student and trainer paths
   - Verify recruitment module detection works

## Support

For questions or issues:
- Check logs for route errors
- Verify template loading in debug mode
- Ensure recruitment module state is correct
- Test with different user permissions

## Version History

- **v1.0.0** (2026-01-03): Initial implementation
  - Profile selection page
  - Student/Trainer routing logic
  - Recruitment module integration
  - Contact us fallback

---

**Module**: edafa_website_branding  
**Author**: Edafa Inc  
**License**: LGPL-3
