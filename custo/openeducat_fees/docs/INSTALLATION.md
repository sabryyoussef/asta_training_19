# Installation Guide - OpenEduCat Fees

## Prerequisites

### System Requirements

- Odoo 18.0
- Python 3.10+
- PostgreSQL 12+
- Ubuntu 20.04+ / Debian 10+ (or compatible)

### Required Modules

- `openeducat_core` - Must be installed first
- `account` - Odoo standard accounting module

---

## Installation Steps

### Step 1: Install Dependencies

Ensure `openeducat_core` is installed and activated:

```bash
# Via Odoo UI:
# Apps → Search "OpenEduCat Core" → Install
```

### Step 2: Install openeducat_fees

**Method A: Via Odoo UI (Recommended)**

1. Navigate to **Apps** menu
2. Remove "Apps" filter to show all modules
3. Search for "Edafa Fees" or "openeducat_fees"
4. Click **Install**

**Method B: Via Command Line**

```bash
# Update module list
./odoo-bin -c /path/to/odoo.conf --update=openeducat_fees -d your_database --stop-after-init

# Or install in PyCharm:
# Configure run config with: --update=openeducat_fees -d your_database --stop-after-init
```

**Method C: Manual Installation**

```bash
# 1. Ensure module is in addons path
# 2. Update apps list in Odoo
# 3. Search and install from UI
```

---

## Post-Installation Configuration

### Step 1: Configure Access Rights

Assign users to security groups:

**Navigate to:** Settings → Users & Companies → Users

**Groups:**
- **Fees User** (`group_openeducat_fees_user`) - Regular users
- **Fees Manager** (`group_op_fees_admin`) - Administrators

### Step 2: Configure Chart of Accounts

Ensure accounting is configured:

1. Navigate to **Accounting** → Configuration → Settings
2. Set up Chart of Accounts if not already done
3. Configure income accounts for fee products

### Step 3: Create Fee Products

Navigate to **Fees** → Configuration → Fees Elements

Create products for fee types:
- Admission fees
- Library fees
- Tuition fees
- Transportation fees
- Lab fees
- etc.

### Step 4: Set Up Fee Terms

Navigate to **Fees** → Configuration → Fees Terms

Create fee term templates:

**Example: Semester 1 Fees (Fixed Days)**
- Name: "Semester 1 Fees Term"
- Code: "S1FT"
- Type: Fixed Fees of Days
- Lines:
  - Day 0: 40% (Admission + Library fees)
  - Day 30: 30% (Tuition fees)
  - Day 60: 30% (Remaining fees)

**Example: Semester 2 Fees (Fixed Dates)**
- Name: "Semester 2 Fees Term"
- Code: "S2FT"
- Type: Fixed Fees of Dates
- Lines:
  - 2025-01-15: 50%
  - 2025-02-15: 50%

### Step 5: Assign Fee Terms to Courses

Navigate to **Courses** → Select a course

Set the **Fees Term** field to appropriate term.

---

## Verification

### Test Installation

1. **Check module is installed:**
   ```sql
   SELECT name, state FROM ir_module_module WHERE name = 'openeducat_fees';
   -- Should show: state = 'installed'
   ```

2. **Verify menus visible:**
   - Open Odoo
   - Look for "Fees" menu
   - Check sub-menus: Fees Terms, Fees Elements

3. **Check models created:**
   ```sql
   SELECT model FROM ir_model WHERE model LIKE 'op.fees%';
   -- Should return: op.fees.terms, op.fees.terms.line, op.fees.element, op.student.fees.details
   ```

4. **Verify access rights:**
   ```sql
   SELECT * FROM ir_model_access WHERE name LIKE '%fees%';
   -- Should show access rules for fees models
   ```

### Load Demo Data (Optional)

Demo data includes:
- Sample fee products
- Pre-configured fee terms
- Sample student fee details

**Enable during installation:**
- Check "Demo data" option when installing
- Or install with `--without-demo=False`

---

## Troubleshooting

### Issue: Module not appearing in Apps list

**Solution:**
```bash
# Update apps list
./odoo-bin -c /path/to/odoo.conf -d your_database --update-apps-list --stop-after-init
```

### Issue: Dependency error (openeducat_core not found)

**Solution:**
1. Install `openeducat_core` first
2. Ensure it's in the addons path
3. Update apps list
4. Retry installation

### Issue: Access Rights Error

**Solution:**
1. Navigate to Settings → Users
2. Assign appropriate Fees groups to users
3. Log out and log back in

### Issue: Fee invoice not creating

**Solution:**
1. Check Chart of Accounts is configured
2. Verify income account on fee products
3. Check user has accounting rights
4. Review Odoo server logs

### Issue: Views not loading / showing tree instead of list

**Solution:**
- This module uses Odoo 18 list views
- Clear browser cache
- Restart Odoo
- Check view definitions in database:
  ```sql
  SELECT name, arch FROM ir_ui_view WHERE model LIKE 'op.fees%' AND arch LIKE '%<tree%';
  -- Should return empty (no tree views, only list)
  ```

---

## Upgrade Notes

### From Odoo 17 to 18

**Key Changes:**
- ✅ All `<tree>` views converted to `<list>`
- ✅ Removed deprecated `attrs` usage
- ✅ Removed `states` attribute
- ✅ Updated OWL components to Odoo 18 standards
- ✅ Assets syntax updated

**Migration Script:**

```python
# Run after upgrade
# Clears old view cache
self.env['ir.ui.view'].clear_caches()
```

---

## Uninstallation

### Warning
Uninstalling will:
- ❌ Delete all fee terms, fee elements, and student fee details
- ❌ Remove fee-related fields from courses and students
- ⚠️ Keep generated invoices (account.move) but unlink from fees

### Backup First

```bash
# Backup database before uninstalling
pg_dump -U odoo your_database > backup_before_fees_uninstall.sql
```

### Uninstall Steps

1. Navigate to **Apps**
2. Search "openeducat_fees"
3. Click **Uninstall**
4. Confirm warning

---

## Next Steps

After installation:

1. ✅ Read [User Guide](./USER_GUIDE.md) - Learn how to use the module
2. ✅ Review [Technical Reference](./TECHNICAL.md) - Understand architecture
3. ✅ Check [FAQ](./FAQ.md) - Common questions and answers

---

**Need Help?**
- Check [FAQ.md](./FAQ.md)
- Review Odoo logs: `/var/log/odoo/odoo-server.log`
- Contact: https://www.edafa.org

---

**Installation Date:** _________  
**Installed By:** _________  
**Database:** _________

