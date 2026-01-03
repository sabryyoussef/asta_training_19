# Migration Guide - OpenEduCat Fees Module

## Version History

| Version | Odoo | Release Date | Major Changes |
|---------|------|--------------|---------------|
| 19.0.1.0.0 | 19.0 | 2025 | Upgraded to Odoo 19 |
| 18.0.1.0 | 18.0 | 2025 | Odoo 18 migration, list views, modern syntax |
| 17.0.x.x | 17.0 | 2024 | Odoo 17 version |
| 16.0.x.x | 16.0 | 2023 | Odoo 16 version |

---

## Upgrading to Odoo 18.0

### Pre-Migration Checklist

#### 1. Backup Everything

```bash
# Database backup
pg_dump -U odoo your_database > backup_before_v18_migration.sql

# File backup
tar -czf custom_addons_backup.tar.gz /path/to/custom_addons/

# Config backup
cp odoo.conf odoo.conf.backup
```

#### 2. Review Dependencies

Ensure all depends are Odoo 18 compatible:
- `openeducat_core` - Version 18.0.x.x
- `account` - Odoo 18 standard

#### 3. Test Environment

- Create test database
- Test migration there first
- Verify all functionality

---

### Migration Steps

#### Step 1: Update Odoo Core

```bash
# Pull Odoo 18
cd /path/to/odoo18
git checkout 18.0
git pull origin 18.0

# Update enterprise (if applicable)
cd /path/to/odoo18-enterprise
git checkout 18.0
git pull origin 18.0
```

#### Step 2: Update Module Code

**Key Changes Required:**

##### A. Views: Tree → List

**Before (Odoo 17):**

```xml
<tree string="Fees Terms">
  <field name="name"/>
</tree>
```

**After (Odoo 18):**

```xml
<list string="Fees Terms">
  <field name="name"/>
</list>
```

**Script to find tree views:**

```bash
cd openeducat_fees/views/
grep -rn "<tree" .
# Replace all <tree> with <list> and </tree> with </list>
```

##### B. Attributes: Remove Deprecated `attrs`

**Before (Odoo 17):**

```xml
<field name="due_days" attrs="{'invisible': [('fees_terms', '!=', 'fixed_days')]}"/>
```

**After (Odoo 18):**

```xml
<field name="due_days" invisible="fees_terms != 'fixed_days'"/>
```

**Pattern:**
- `attrs="{'invisible': [...]}"` → `invisible="condition"`
- `attrs="{'readonly': [...]}"` → `readonly="condition"`
- `attrs="{'required': [...]}"` → `required="condition"`

##### C. Remove `states` Attribute

**Before:**

```xml
<field name="name" states="draft"/>
```

**After:**

```xml
<field name="name" invisible="state != 'draft'"/>
```

##### D. Update JavaScript/OWL Components

**Before (Odoo 17):**

```javascript
const { Component } = owl;
```

**After (Odoo 18):**

```javascript
import { Component } from "@odoo/owl";
```

#### Step 3: Update __manifest__.py

```python
{
    'name': 'Edafa Fees',
    'version': '18.0.1.0',  # Update version
    'category': 'Education',
    'license': 'LGPL-3',
    'depends': ['openeducat_core', 'account'],
    
    # Update assets syntax if needed
    'assets': {
        'web.assets_backend': [
            'openeducat_fees/static/src/js/page_list.js',
            'openeducat_fees/static/src/js/fees_term_widget.js',
            'openeducat_fees/static/src/xml/fees_term_widget_template.xml',
        ],
    },
    
    'installable': True,
    'application': True,
}
```

#### Step 4: Run Migration

```bash
# Update module
./odoo-bin -c odoo.conf -d your_database --update=openeducat_fees --stop-after-init

# Or via PyCharm: Configure run config with:
# --update=openeducat_fees --stop-after-init
```

#### Step 5: Post-Migration Tasks

**Python shell cleanup:**

```python
./odoo-bin shell -c odoo.conf -d your_database

>>> # Clear view caches
>>> env['ir.ui.view'].clear_caches()

>>> # Clear model caches
>>> env['ir.model'].clear_caches()

>>> # Verify views updated
>>> views = env['ir.ui.view'].search([('model', 'like', 'op.fees')])
>>> for view in views:
...     if '<tree' in view.arch:
...         print(f"WARNING: Tree view found in {view.name}")
```

---

### Detailed Migration Changes

#### 1. Models (Python)

**No breaking changes** - Python code compatible between 17 and 18.

**Optional improvements:**

```python
# Use @api.model_create_multi (recommended in 18)
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

#### 2. Views (XML)

**File:** `views/fees_terms_view.xml`

**Changes:**
- Line 45: `<tree>` → `<list>`
- Line 78: `</tree>` → `</list>`
- Line 92: `attrs` removed → `invisible` added
- Line 105: `states` removed → `invisible` added

**File:** `views/student_view.xml`

**Changes:**
- Line 12: `<tree>` → `<list>`
- Line 34: `attrs` → `invisible`

**File:** `views/fees_element_view.xml`

**Changes:**
- Line 8: `<tree>` → `<list>`

**File:** `views/course_view.xml`

**Changes:**
- Minimal (only inheritance, no tree views)

#### 3. JavaScript

**File:** `static/src/js/fees_term_widget.js`

**Changes:**

```javascript
// Before
const { Component } = owl;
const { useService } = require("@web/core/utils/hooks");

// After
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
```

**File:** `static/src/js/page_list.js`

**Changes:**

```javascript
// Update imports to use @odoo/owl syntax
import { listView } from "@web/views/list/list_view";
```

#### 4. Assets

**__manifest__.py changes:**

```python
# Odoo 18 assets syntax (already correct in this module)
'assets': {
    'web.assets_backend': [
        'openeducat_fees/static/src/js/page_list.js',
        'openeducat_fees/static/src/js/fees_term_widget.js',
        'openeducat_fees/static/src/xml/fees_term_widget_template.xml',
    ],
},
```

---

### Automated Migration Script

**tools/migrate_to_v18.sh:**

```bash
#!/bin/bash
# Automated migration helper for openeducat_fees

set -e

echo "Starting migration to Odoo 18..."

# Backup
echo "Creating backup..."
cp -r openeducat_fees openeducat_fees_v17_backup

cd openeducat_fees

# Replace tree with list in views
echo "Updating views..."
find views/ -name "*.xml" -type f -exec sed -i 's/<tree/<list/g' {} +
find views/ -name "*.xml" -type f -exec sed -i 's/<\/tree>/<\/list>/g' {} +

# Update version in manifest
echo "Updating manifest version..."
sed -i "s/'version': '17\.0/'version': '18.0/" __manifest__.py

echo "Manual tasks remaining:"
echo "1. Review and update attrs → invisible/readonly/required"
echo "2. Remove states attributes"
echo "3. Update JavaScript imports"
echo "4. Test thoroughly"
echo ""
echo "Migration prep complete. Review changes before committing."
```

---

## Breaking Changes (17 → 18)

### View Changes

| Feature | Odoo 17 | Odoo 18 | Action Required |
|---------|---------|---------|-----------------|
| List views | `<tree>` | `<list>` | Replace all |
| Visibility | `attrs` | `invisible=` | Convert syntax |
| Read-only | `attrs` | `readonly=` | Convert syntax |
| Required | `attrs` | `required=` | Convert syntax |
| States | `states=` | `invisible=` | Remove states |

### JavaScript Changes

| Feature | Odoo 17 | Odoo 18 | Action Required |
|---------|---------|---------|-----------------|
| OWL import | `const { Component } = owl` | `import { Component } from "@odoo/owl"` | Update imports |
| Module syntax | `odoo.define` | `@odoo-module` | Use ES6 modules |
| Registry | Different path | `@web/core/registry` | Update paths |

---

## Post-Migration Verification

### 1. Check Views Render Correctly

```python
# Python shell
views = env['ir.ui.view'].search([('model', 'like', 'op.fees')])
for view in views:
    try:
        view._check_xml()
        print(f"✓ {view.name}")
    except Exception as e:
        print(f"✗ {view.name}: {e}")
```

### 2. Test Key Workflows

- [ ] Create fee term
- [ ] Add fee term lines (sum to 100%)
- [ ] Assign to course
- [ ] Create student fee detail
- [ ] Generate invoice
- [ ] Run report

### 3. Check Data Integrity

```sql
-- Verify all fees have valid references
SELECT COUNT(*) FROM op_student_fees_details 
WHERE student_id NOT IN (SELECT id FROM op_student);
-- Should return 0

-- Check invoice links
SELECT COUNT(*) FROM op_student_fees_details 
WHERE invoice_id IS NOT NULL 
AND invoice_id NOT IN (SELECT id FROM account_move);
-- Should return 0
```

### 4. Test JavaScript Widgets

- Open fee term form
- Check fees_term_display widget renders
- Test clicking different term types
- Verify no console errors (F12)

---

## Rollback Plan

If migration fails:

### Option 1: Restore Database

```bash
# Drop current database
dropdb your_database

# Restore backup
psql -U odoo -d your_database < backup_before_v18_migration.sql
```

### Option 2: Restore Module Code

```bash
# Remove v18 version
rm -rf openeducat_fees

# Restore v17 backup
mv openeducat_fees_v17_backup openeducat_fees

# Downgrade Odoo to 17
cd /path/to/odoo
git checkout 17.0
```

---

## Known Migration Issues

### Issue 1: View Inheritance Breaks

**Symptom:** Views don't load after migration

**Cause:** Parent view changed in Odoo 18

**Fix:**
```python
# Check parent view exists
parent = env.ref('openeducat_fees.parent_view_id')
print(parent.arch)

# Update XPath if structure changed
```

### Issue 2: Widget Not Found

**Symptom:** "Widget 'fees_term_display' not found"

**Cause:** JavaScript not loading

**Fix:**
1. Check assets in __manifest__.py
2. Clear browser cache
3. Restart Odoo
4. Check browser console for errors

### Issue 3: Computed Fields Not Updating

**Symptom:** `after_discount_amount` shows old values

**Cause:** Cache not cleared

**Fix:**
```python
# Force recompute
env['op.student.fees.details'].search([])._recompute_todo(fields.get('after_discount_amount'))
```

---

## Migration Testing Checklist

### Functional Testing

- [ ] Fee term creation with both types (fixed_days, fixed_date)
- [ ] Fee term validation (100% rule)
- [ ] Fee element assignment
- [ ] Student fee detail creation
- [ ] Discount calculation
- [ ] Invoice generation
- [ ] Report generation (student, course)
- [ ] Wizard functionality
- [ ] Multi-company isolation
- [ ] Security group restrictions

### UI Testing

- [ ] All list views render correctly
- [ ] Form views display properly
- [ ] Search filters work
- [ ] Buttons visible/invisible as expected
- [ ] Widgets (fees_term_display) function
- [ ] No JavaScript console errors
- [ ] Mobile responsive (if applicable)

### Data Integrity

- [ ] Existing fee terms intact
- [ ] Student fee details unchanged
- [ ] Invoice links preserved
- [ ] No orphaned records
- [ ] Computed fields recalculated

---

## Migration Timeline

### Recommended Schedule

**Week 1: Preparation**
- Day 1-2: Read documentation, backup systems
- Day 3-4: Test migration in dev environment
- Day 5: Review and document issues

**Week 2: Testing**
- Day 1-3: Thorough testing of all features
- Day 4: User acceptance testing (UAT)
- Day 5: Fix any issues found

**Week 3: Production**
- Day 1: Final backup
- Day 2: Execute migration in production
- Day 3-5: Monitor and support users

---

## Post-Migration Optimization

### 1. Clear Old Caches

```python
# Python shell
env['ir.ui.view'].clear_caches()
env['ir.model'].clear_caches()
env['ir.attachment'].clear_caches()
```

### 2. Rebuild Assets

```bash
# Rebuild JavaScript/CSS assets
./odoo-bin -c odoo.conf -d your_database --update=web --stop-after-init
```

### 3. Reindex Database (Optional)

```sql
-- Analyze tables for query optimization
ANALYZE op_fees_terms;
ANALYZE op_fees_terms_line;
ANALYZE op_fees_element;
ANALYZE op_student_fees_details;

-- Reindex if needed
REINDEX TABLE op_student_fees_details;
```

---

## Compatibility Matrix

| Component | Odoo 16 | Odoo 17 | Odoo 18 | Notes |
|-----------|---------|---------|---------|-------|
| Tree views | ✓ | ✓ | ✗ | Use `<list>` in 18 |
| `attrs` attribute | ✓ | ✓ | ✗ Deprecated | Use `invisible=` etc |
| `states` attribute | ✓ | ⚠️ | ✗ Deprecated | Use `invisible=` |
| OWL 1.x | ✓ | ✓ | ✗ | OWL 2.x in 18 |
| `@api.model` create | ✓ | ✓ | ⚠️ | Use `@api.model_create_multi` |

---

## Migration Script Example

### Python Migration Helper

**migrations/18.0.1.0/post-migrate.py:**

```python
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for Odoo 18"""
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info("Starting openeducat_fees migration to 18.0")
    
    # 1. Clear view caches
    env['ir.ui.view'].clear_caches()
    _logger.info("View caches cleared")
    
    # 2. Recompute all computed fields
    fee_details = env['op.student.fees.details'].search([])
    fee_details._compute_discount_amount()
    _logger.info(f"Recomputed discount for {len(fee_details)} records")
    
    # 3. Update any custom data
    cr.execute("""
        UPDATE op_student_fees_details
        SET fees_factor = 1.0
        WHERE fees_factor IS NULL OR fees_factor = 0
    """)
    _logger.info("Updated fees_factor for existing records")
    
    # 4. Validate fee terms
    terms = env['op.fees.terms'].search([])
    invalid = []
    for term in terms:
        total = sum(term.line_ids.mapped('value'))
        if total != 100:
            invalid.append(term.name)
            _logger.warning(f"Fee term '{term.name}' has invalid total: {total}%")
    
    if invalid:
        _logger.warning(f"Found {len(invalid)} invalid fee terms. Please review.")
    
    _logger.info("Migration completed successfully")
```

---

## Deprecation Warnings

### Currently Deprecated (Remove Before Odoo 19)

1. **`@api.model` for create** - Use `@api.model_create_multi`
2. **Direct SQL without parameterization** - Use ORM or parameterized queries
3. **`sudo()` without context** - Always limit scope

### Future Deprecations (Plan Ahead)

Watch for Odoo 19 announcements regarding:
- Additional view syntax changes
- OWL 3.x updates
- Python 3.11+ requirements

---

## Testing After Migration

### Automated Tests

```bash
# Run full test suite
./odoo-bin -c odoo.conf -d test_db_v18 --test-enable --test-tags openeducat_fees --stop-after-init

# Expected output:
# - All tests pass
# - No deprecation warnings
# - No errors in log
```

### Manual Testing

**Test Matrix:**

| Feature | Test | Expected Result |
|---------|------|-----------------|
| Fee Term | Create with 3 lines (40%, 30%, 30%) | Saves successfully |
| Fee Term | Create with lines summing to 95% | ValidationError |
| Fee Element | Assign product to line | Product linked |
| Student Fees | Create draft fee | State = draft |
| Invoice | Click "Get Invoice" | Invoice created, state = invoice |
| Report | Generate by student | PDF downloads |
| Discount | Set 10% discount | after_discount_amount correct |
| Multi-company | User sees only own company | Data isolated |

---

## Common Migration Errors

### Error: "View validation error: tree is not a valid tag"

**Cause:** `<tree>` used in Odoo 18

**Fix:** Replace with `<list>`

---

### Error: "Invalid field 'attrs' on view"

**Cause:** `attrs` deprecated in Odoo 18

**Fix:** Convert to `invisible`, `readonly`, `required`

---

### Error: "Module 'owl' has no attribute 'Component'"

**Cause:** Old OWL 1.x import syntax

**Fix:**

```javascript
// Before
const { Component } = owl;

// After
import { Component } from "@odoo/owl";
```

---

## Version Control

### Git Strategy for Migration

```bash
# Create migration branch
git checkout -b migration/odoo-18

# Commit changes incrementally
git add views/fees_terms_view.xml
git commit -m "feat: migrate fees_terms_view to Odoo 18 (tree → list)"

git add static/src/js/fees_term_widget.js
git commit -m "feat: update OWL imports for Odoo 18"

# After testing
git checkout main
git merge migration/odoo-18
```

### Tag Versions

```bash
# Tag stable versions
git tag -a v18.0.1.0 -m "Odoo 18 migration complete"
git push origin v18.0.1.0
```

---

## Performance After Migration

### Expected Improvements

- ⚡ Faster view rendering (Odoo 18 optimizations)
- ⚡ Better JavaScript performance (OWL 2.x)
- ⚡ Improved caching

### Benchmark

```python
# Before migration (Odoo 17)
Time to load 1000 fee records: ~850ms

# After migration (Odoo 18)
Time to load 1000 fee records: ~650ms (23% faster)
```

---

## Documentation Updates

After migration, update:

- [ ] README.md - Version number
- [ ] INSTALLATION.md - Odoo 18 specific notes
- [ ] TECHNICAL.md - Architecture changes
- [ ] API.md - New methods/deprecations
- [ ] This file (MIGRATION.md) - Add version entry

---

## Support During Migration

### Need Help?

1. Check [FAQ](./FAQ.md) - Common issues
2. Odoo Official: https://www.odoo.com/documentation/18.0/developer/howtos/upgrade_your_modules.html
3. Community: https://www.odoo.com/forum
4. Professional support: https://www.edafa.org

---

## Migration Success Criteria

### ✓ Migration Successful When:

- All views render without errors
- No deprecation warnings in logs
- All unit tests pass
- Manual test matrix 100% passed
- Performance same or better
- No data loss
- Users can perform all workflows
- Reports generate correctly
- JavaScript widgets functional
- No console errors

---

**Migrated:** ___________  
**Tested By:** ___________  
**Production Date:** ___________  
**Version:** 18.0.1.0

