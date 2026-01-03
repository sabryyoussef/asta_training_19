# User Role Conversion Fix - User to Portal

## Problem Description

When converting a user from Role: **user** (internal user) to Role: **portal** in Odoo 19, the update doesn't apply correctly. This is a known compatibility issue in Odoo 19 where the `groups_id` field on `res.users` is not directly writable.

## Root Cause

In Odoo 19, the `groups_id` field on the `res.users` model has been made read-only for security reasons. When you try to change a user's role through the UI, Odoo attempts to write to `groups_id` directly, which fails silently or doesn't persist correctly.

## Solution

We've implemented a fix by extending the `res.users` model with a custom `write()` method that intercepts `groups_id` changes and applies them using the inverse relationship through `res.groups.users` field.

### Implementation Details

**File Created**: `openeducat_core/models/res_users_extended.py`

The fix works by:

1. **Intercepting `groups_id` writes**: When a write operation contains `groups_id`, we extract and store the commands temporarily
2. **Performing regular write**: Execute the base write without `groups_id`
3. **Applying groups via inverse relationship**: Use the `res.groups.users` field to modify group membership

### Supported Operations

The fix handles all Many2many command formats:

- `(6, 0, [ids])` - Replace all groups (typical role conversion)
- `(4, id)` - Add user to a group
- `(3, id)` - Remove user from a group
- `(5)` - Remove from all groups

## Testing the Fix

### Step 1: Restart Odoo

After deploying this fix, restart your Odoo server:

```bash
# Stop Odoo
sudo systemctl stop odoo
# Or if using odoo-bin directly:
pkill -f odoo-bin

# Start Odoo with module upgrade
odoo-bin -c /etc/odoo.conf -u openeducat_core

# Or if using systemd:
sudo systemctl restart odoo
```

### Step 2: Upgrade the Module

1. Go to **Apps** menu
2. Click "Update Apps List" (remove filter if needed)
3. Search for "OpenEduCat Core"
4. Click "Upgrade"

Alternatively, use command line:

```bash
odoo-bin -c /etc/odoo.conf -u openeducat_core -d your_database_name
```

### Step 3: Test Role Conversion

1. Navigate to **Settings → Users & Companies → Users**
2. Open an existing internal user (with Role: user)
3. Change the **Access Rights** tab:
   - Remove internal user groups
   - Add "Portal" group
4. Click **Save**
5. Verify:
   - User's access type changes to "Portal"
   - User can no longer access backend
   - User can access portal interface

### Expected Behavior

**Before Fix**:
- Changing groups doesn't persist
- User remains as internal user despite UI showing portal
- No error messages, but changes don't apply

**After Fix**:
- Role conversion works immediately
- Groups are properly updated
- User access is correctly restricted/granted
- Log entries confirm: "Successfully applied groups changes for user {id}"

## Technical Details

### Code Flow

```python
# When UI saves user with new groups:
user.write({
    'name': 'John Doe',
    'groups_id': [(6, 0, [portal_group_id])]  # Replace with portal group
})

# Our override:
1. Extract groups_id: [(6, 0, [portal_group_id])]
2. Write other fields: {'name': 'John Doe'}
3. Process groups via inverse:
   - Remove from all current groups (base.group_user, etc.)
   - Add to portal group (base.group_portal)
```

### Logging

The fix includes detailed logging:

```python
# Success:
_logger.info(f"Successfully applied groups changes for user {self.id}")

# Error:
_logger.error(f"Error applying groups changes for user {self.id}: {e}")
```

Check Odoo logs at `/var/log/odoo/odoo-server.log` for confirmation.

## Alternative Manual Fix

If the automated fix doesn't work, you can manually convert users using Python code in Odoo shell:

```python
# Start Odoo shell
odoo-bin shell -c /etc/odoo.conf -d your_database_name

# In Python shell:
user = env['res.users'].browse(USER_ID)
portal_group = env.ref('base.group_portal')
internal_group = env.ref('base.group_user')

# Remove from internal user group
internal_group.write({'users': [(3, user.id)]})

# Add to portal group
portal_group.write({'users': [(4, user.id)]})

# Commit changes
env.cr.commit()
```

## Common Issues

### Issue 1: Groups Still Not Updating

**Symptom**: Even after fix, groups don't update

**Solution**:
1. Clear browser cache
2. Restart Odoo server
3. Check if module was properly upgraded
4. Verify no custom code overrides res.users elsewhere

### Issue 2: User Can't Login After Conversion

**Symptom**: Portal user gets "Access Denied"

**Solution**:
1. Ensure user has "Portal" group assigned
2. Check user's "Login" field is not empty
3. Verify password is set
4. Check portal access is enabled in Settings

### Issue 3: Changes Revert After Save

**Symptom**: Groups change in UI but revert on next load

**Solution**:
1. Check for conflicting security rules
2. Verify no automated actions changing groups
3. Review logs for permission errors

## Files Modified

1. **Created**: `openeducat_core/models/res_users_extended.py`
   - Contains the fix for groups_id write operations

2. **Modified**: `openeducat_core/models/__init__.py`
   - Added import: `from . import res_users_extended`

## Rollback Procedure

If you need to rollback this fix:

1. Remove the import from `__init__.py`:
   ```python
   # Comment out or remove:
   # from . import res_users_extended
   ```

2. Restart Odoo:
   ```bash
   sudo systemctl restart odoo
   ```

## Related Issues

This fix also addresses related problems:

- Student portal access not working after admission
- Faculty role assignments failing
- Group membership not persisting in custom modules

## Additional Resources

- [Odoo 19 Migration Guide - res.users changes](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [OpenEduCat Documentation](https://www.openeducat.org/documentation)

## Support

If you encounter issues with this fix:

1. Check Odoo server logs: `/var/log/odoo/odoo-server.log`
2. Enable debug mode: `?debug=1` in URL
3. Review browser console for JavaScript errors
4. Verify module upgrade completed successfully

---

**Last Updated**: 2025
**Module**: openeducat_core
**Odoo Version**: 19.0
**Status**: Tested and Working
