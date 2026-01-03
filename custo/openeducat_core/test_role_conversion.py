#!/usr/bin/env python3
"""
Test script for user role conversion fix
Run this in Odoo shell to verify the fix works correctly
"""

def test_user_role_conversion(env, user_id):
    """
    Test converting a user from internal to portal role
    
    Args:
        env: Odoo environment
        user_id: ID of the user to test with
    """
    print("\n" + "="*60)
    print("USER ROLE CONVERSION TEST")
    print("="*60)
    
    # Get the user
    user = env['res.users'].browse(user_id)
    if not user.exists():
        print(f"❌ ERROR: User with ID {user_id} does not exist")
        return False
    
    print(f"\n📋 Testing with user: {user.name} (ID: {user.id})")
    print(f"   Login: {user.login}")
    
    # Get groups
    portal_group = env.ref('base.group_portal', raise_if_not_found=False)
    internal_group = env.ref('base.group_user', raise_if_not_found=False)
    
    if not portal_group or not internal_group:
        print("❌ ERROR: Required groups not found")
        return False
    
    print(f"\n📦 Portal Group: {portal_group.name} (ID: {portal_group.id})")
    print(f"📦 Internal Group: {internal_group.name} (ID: {internal_group.id})")
    
    # Check current groups
    print(f"\n🔍 Current groups ({len(user.groups_id)}):")
    for group in user.groups_id:
        print(f"   - {group.name}")
    
    is_portal_before = portal_group in user.groups_id
    is_internal_before = internal_group in user.groups_id
    
    print(f"\n📊 Status BEFORE:")
    print(f"   Portal User: {'✅ Yes' if is_portal_before else '❌ No'}")
    print(f"   Internal User: {'✅ Yes' if is_internal_before else '❌ No'}")
    
    # Test 1: Convert internal user to portal
    if is_internal_before and not is_portal_before:
        print("\n🔄 TEST 1: Converting INTERNAL → PORTAL")
        
        try:
            user.write({
                'groups_id': [(6, 0, [portal_group.id])]
            })
            print("   ✅ Write operation completed")
            
            # Refresh user
            user.invalidate_recordset()
            
            # Check result
            is_portal_after = portal_group in user.groups_id
            is_internal_after = internal_group in user.groups_id
            
            print(f"\n📊 Status AFTER:")
            print(f"   Portal User: {'✅ Yes' if is_portal_after else '❌ No'}")
            print(f"   Internal User: {'✅ Yes' if is_internal_after else '❌ No'}")
            
            if is_portal_after and not is_internal_after:
                print("\n✅ TEST 1 PASSED: User successfully converted to portal")
                return True
            else:
                print("\n❌ TEST 1 FAILED: Conversion did not work correctly")
                return False
                
        except Exception as e:
            print(f"\n❌ TEST 1 FAILED with exception: {e}")
            return False
    
    # Test 2: Convert portal user to internal
    elif is_portal_before and not is_internal_before:
        print("\n🔄 TEST 2: Converting PORTAL → INTERNAL")
        
        try:
            # Give basic internal user access
            employee_group = env.ref('base.group_user')
            
            user.write({
                'groups_id': [(6, 0, [employee_group.id])]
            })
            print("   ✅ Write operation completed")
            
            # Refresh user
            user.invalidate_recordset()
            
            # Check result
            is_portal_after = portal_group in user.groups_id
            is_internal_after = internal_group in user.groups_id
            
            print(f"\n📊 Status AFTER:")
            print(f"   Portal User: {'✅ Yes' if is_portal_after else '❌ No'}")
            print(f"   Internal User: {'✅ Yes' if is_internal_after else '❌ No'}")
            
            if is_internal_after and not is_portal_after:
                print("\n✅ TEST 2 PASSED: User successfully converted to internal")
                return True
            else:
                print("\n❌ TEST 2 FAILED: Conversion did not work correctly")
                return False
                
        except Exception as e:
            print(f"\n❌ TEST 2 FAILED with exception: {e}")
            return False
    
    else:
        print("\n⚠️  WARNING: User has unusual group configuration")
        print("   Cannot determine appropriate test")
        return None


def create_test_user(env):
    """
    Create a test user for testing role conversion
    
    Args:
        env: Odoo environment
        
    Returns:
        User record ID
    """
    print("\n🔧 Creating test user...")
    
    # Create partner first
    partner = env['res.partner'].create({
        'name': 'Test User Role Conversion',
        'email': 'test_role_conversion@example.com',
    })
    
    # Create user with internal access
    internal_group = env.ref('base.group_user')
    
    user = env['res.users'].create({
        'name': 'Test User Role Conversion',
        'login': 'test_role_conversion@example.com',
        'email': 'test_role_conversion@example.com',
        'partner_id': partner.id,
        'groups_id': [(6, 0, [internal_group.id])],
    })
    
    print(f"✅ Test user created: {user.name} (ID: {user.id})")
    return user.id


def cleanup_test_user(env, user_id):
    """
    Delete the test user
    
    Args:
        env: Odoo environment
        user_id: ID of user to delete
    """
    user = env['res.users'].browse(user_id)
    if user.exists():
        partner = user.partner_id
        user.unlink()
        if partner.exists():
            partner.unlink()
        print(f"🗑️  Test user deleted (ID: {user_id})")


# Example usage in Odoo shell:
# 
# # Start Odoo shell:
# odoo-bin shell -c /etc/odoo.conf -d your_database_name
#
# # Run the test:
# exec(open('/workspaces/asta_training_19/custo/openeducat_core/test_role_conversion.py').read())
# 
# # Option 1: Test with existing user
# test_user_role_conversion(env, USER_ID)
#
# # Option 2: Create test user and run test
# test_user_id = create_test_user(env)
# test_user_role_conversion(env, test_user_id)
# cleanup_test_user(env, test_user_id)
#
# # Don't forget to commit if you want to keep changes:
# env.cr.commit()

print("""
╔══════════════════════════════════════════════════════════════╗
║  USER ROLE CONVERSION TEST SCRIPT LOADED                     ║
╚══════════════════════════════════════════════════════════════╝

Available functions:

1. test_user_role_conversion(env, user_id)
   - Test role conversion with an existing user
   
2. create_test_user(env)
   - Create a test user for testing
   - Returns: user_id
   
3. cleanup_test_user(env, user_id)
   - Delete the test user after testing

Example:
--------
# Test with existing user ID 5:
test_user_role_conversion(env, 5)

# Or create and test:
test_id = create_test_user(env)
test_user_role_conversion(env, test_id)
cleanup_test_user(env, test_id)
env.cr.commit()

""")
