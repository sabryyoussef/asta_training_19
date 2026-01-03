# Quick Fix Guide - User Role Conversion

## 🎯 What Was Fixed

**Problem:** Converting user from "user" role to "portal" role doesn't work in Odoo 19

**Solution:** Added custom code to handle role conversions properly

## 🚀 Quick Start - Apply the Fix

### 1. Restart Odoo

Pick ONE method:

```bash
# Method A: Systemd
sudo systemctl restart odoo

# Method B: Kill and restart
pkill -f odoo-bin
odoo-bin -c /etc/odoo.conf -u openeducat_core

# Method C: Ctrl+C if running in terminal, then restart
```

### 2. Upgrade Module

**Option A - Web UI:**
1. Apps menu → Update Apps List
2. Search "OpenEduCat Core"
3. Click Upgrade

**Option B - Command Line:**
```bash
odoo-bin -c /etc/odoo.conf -u openeducat_core -d YOUR_DATABASE --stop-after-init
```

### 3. Test It

1. Settings → Users & Companies → Users
2. Pick any internal user
3. Access Rights tab → Remove internal groups → Add "Portal"
4. Save
5. ✅ Should work now!

## 📋 What Was Changed

| File | Change |
|------|--------|
| `models/res_users_extended.py` | ✅ Created (fix code) |
| `models/__init__.py` | ✅ Modified (added import) |

## ✅ Verification

Check if it worked:

- [ ] User role changes persist after save
- [ ] Portal users can access portal
- [ ] Internal users can access backend
- [ ] No errors in Odoo logs

## 🔍 Check Logs

```bash
# View recent logs
tail -f /var/log/odoo/odoo-server.log | grep "groups changes"

# Should see:
# INFO ... Successfully applied groups changes for user X
```

## ⚠️ If It Still Doesn't Work

1. **Clear browser cache** (Ctrl+Shift+Del)
2. **Verify module upgraded:**
   - Apps → Remove filter → Search "OpenEduCat Core"
   - Check version updated
3. **Restart Odoo again**
4. **Try in incognito/private window**

## 🆘 Emergency Rollback

If something breaks:

1. Edit `/custo/openeducat_core/models/__init__.py`
2. Comment out: `# from . import res_users_extended`
3. Restart Odoo

## 📖 More Info

- Full docs: `USER_ROLE_CONVERSION_FIX.md`
- Implementation: `ROLE_CONVERSION_IMPLEMENTATION.md`
- Test script: `test_role_conversion.py`

## 💡 Common Use Cases

### Convert User to Portal
```
1. Settings → Users → Select user
2. Access Rights → Remove all groups
3. Add "Portal" group
4. Save
```

### Convert Portal to User
```
1. Settings → Users → Select portal user
2. Access Rights → Remove "Portal"
3. Add appropriate internal groups
4. Save
```

---

**Status:** ✅ Fix Ready  
**Action Required:** Restart Odoo + Upgrade Module  
**Time Needed:** 2-5 minutes
