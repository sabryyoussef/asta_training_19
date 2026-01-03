# English Numerals Enforcement

## Overview
This implementation ensures that all numbers across the website display using English/Western numerals (0-9) consistently, regardless of browser locale or language settings.

## Problem Solved
In multilingual environments or when the browser is set to certain locales (e.g., Arabic), numbers may display using localized numeral systems (e.g., ٠-٩ for Arabic). This can cause confusion and inconsistency in the user interface.

## Solution
A comprehensive CSS stylesheet (`english_numerals.css`) has been implemented across all modules to enforce English numerals throughout the entire application.

## Implementation Details

### CSS Properties Used
1. **`font-variant-numeric`**: Forces lining and tabular numerals
2. **`font-feature-settings`**: Ensures proper OpenType features for numbers
3. **`unicode-bidi: bidi-override`**: Overrides bidirectional text algorithm for numbers
4. **`direction: ltr !important`**: Forces left-to-right direction for numeric content

### Modules Updated
The following modules have been updated with `english_numerals.css`:

1. **edafa_website_branding**
   - Location: `/custo/edafa_website_branding/static/src/css/english_numerals.css`
   - Loaded in: Both frontend (`web.assets_frontend`) and backend (`web.assets_backend`)

2. **motakamel_alumni**
   - Location: `/custo/motakamel_alumni/static/src/css/english_numerals.css`
   - Loaded in: Both frontend and backend

3. **motakamel_dashboard**
   - Location: `/custo/motakamel_dashboard/static/src/css/english_numerals.css`
   - Loaded in: Backend only

4. **openeducat_core**
   - Location: `/custo/openeducat_core/static/src/css/english_numerals.css`
   - Loaded in: Both frontend and backend

5. **openeducat_fees**
   - Location: `/custo/openeducat_fees/static/src/css/english_numerals.css`
   - Loaded in: Backend only

### Coverage
The CSS rules enforce English numerals for:

#### Input Fields
- Text inputs
- Number inputs
- Email inputs
- Phone/Tel inputs
- Textareas
- Select dropdowns

#### Data Display
- Table cells (td, th)
- Data cells in Odoo views
- Badges and labels
- Portal tables
- List views and Kanban cards

#### Specific Field Types
- Monetary/currency fields
- Float and integer fields
- Date and time displays
- Phone numbers
- Email addresses
- ID numbers and codes

#### UI Components
- Progress indicators
- Counters and step numbers
- Dashboard statistics
- Pagination controls
- Chart labels and values
- Notification badges

#### Special Cases
- Wizard progress steps
- Alumni portal elements
- Admission portal elements
- Workflow dashboard elements

### Browser Compatibility
The implementation uses modern CSS features with vendor prefixes for compatibility:
- `-webkit-font-feature-settings`
- `-webkit-appearance`
- `-moz-appearance`

### RTL Support
Special overrides are included for RTL (right-to-left) layouts to ensure numbers remain in LTR format even when the page direction is RTL:

```css
[dir="rtl"] input[type="number"],
[dir="rtl"] .number,
[dir="rtl"] .amount {
    direction: ltr !important;
    unicode-bidi: bidi-override !important;
}
```

### Print Styles
Dedicated print media queries ensure numbers display correctly when printing:

```css
@media print {
    * {
        font-variant-numeric: lining-nums tabular-nums !important;
        direction: ltr !important;
    }
}
```

## Testing
After deployment, verify English numerals are displayed correctly in:

1. **Forms**: Check all input fields (text, number, email, phone)
2. **Tables**: Verify data tables show numbers correctly
3. **Dashboards**: Check statistics, KPIs, and metric displays
4. **Portal Pages**: Test admission portal, alumni portal
5. **Reports**: Verify printed reports show correct numerals
6. **Mobile**: Test on mobile devices to ensure numeric keyboard appears
7. **Different Locales**: Test with browser set to different languages

## Maintenance
If additional modules are added to the system:

1. Copy `english_numerals.css` to the module's `static/src/css/` directory
2. Add the CSS file to the module's `__manifest__.py` under `assets`:
   ```python
   'assets': {
       'web.assets_backend': [
           'module_name/static/src/css/english_numerals.css',
           # ... other assets
       ],
       'web.assets_frontend': [
           'module_name/static/src/css/english_numerals.css',
           # ... other assets
       ],
   }
   ```

## Technical Notes

### Why Multiple Copies?
Each module has its own copy of `english_numerals.css` to ensure:
- Module independence
- No dependency on other modules
- Easy maintenance per module
- Flexibility for module-specific customizations

### Performance Impact
- Minimal: CSS file is small (~10KB)
- Loaded once and cached by browser
- Applied efficiently using CSS selectors

### Future Enhancements
Consider these potential improvements:

1. **Centralized Asset**: Create a shared assets module to reduce duplication
2. **JavaScript Validation**: Add JS validation to ensure input values remain numeric
3. **Locale-specific Overrides**: Add support for locale-specific number formatting while maintaining English numerals
4. **Testing Suite**: Implement automated tests for numeral rendering

## Deployment

### Upgrading Modules
After updating the manifests, upgrade the modules:

```bash
# Upgrade all affected modules
odoo-bin -u edafa_website_branding,motakamel_alumni,motakamel_dashboard,openeducat_core,openeducat_fees -d <database_name>
```

### Asset Regeneration
Clear assets cache to force reload:

```bash
# In Odoo, go to Settings > Technical > Database Structure > Clear Assets Cache
# Or restart Odoo with --dev=all flag
```

## Troubleshooting

### Issue: Numbers still showing in localized format
**Solution**: Clear browser cache and force refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Issue: CSS not loading
**Solution**: 
1. Verify file exists in module's `static/src/css/` directory
2. Check `__manifest__.py` has correct path
3. Upgrade the module
4. Clear assets cache

### Issue: Conflicts with existing CSS
**Solution**: The rules use `!important` to override, but check for more specific selectors that might be interfering

### Issue: Numbers misaligned
**Solution**: Check if custom CSS is overriding `text-align` or `direction` properties

## Related Files
- `/custo/edafa_website_branding/static/src/css/english_numerals.css`
- `/custo/motakamel_alumni/static/src/css/english_numerals.css`
- `/custo/motakamel_dashboard/static/src/css/english_numerals.css`
- `/custo/openeducat_core/static/src/css/english_numerals.css`
- `/custo/openeducat_fees/static/src/css/english_numerals.css`

## Version History
- **v1.0.0** (2026-01-03): Initial implementation across all modules

## Support
For issues or questions, contact the development team or refer to Odoo's asset management documentation.
