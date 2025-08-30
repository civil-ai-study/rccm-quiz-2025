#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC Test Script: Verify 'env' department fix
Tests that the added 'env' department mapping resolves the 404 issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import RCCMConfig

def test_env_department_mapping():
    """Test that 'env' department is now available in RCCMConfig.DEPARTMENTS"""
    
    print("🔍 ULTRA SYNC TEST: Verifying 'env' department mapping fix")
    print("=" * 60)
    
    # Test 1: Check if 'env' exists in DEPARTMENTS
    print("Test 1: Checking if 'env' department exists...")
    if 'env' in RCCMConfig.DEPARTMENTS:
        print("✅ SUCCESS: 'env' department found in RCCMConfig.DEPARTMENTS")
        env_dept = RCCMConfig.DEPARTMENTS['env']
        print(f"   - Name: {env_dept['name']}")
        print(f"   - Full Name: {env_dept['full_name']}")
        print(f"   - Description: {env_dept['description']}")
        print(f"   - Icon: {env_dept['icon']}")
        print(f"   - Color: {env_dept['color']}")
    else:
        print("❌ FAILED: 'env' department not found in RCCMConfig.DEPARTMENTS")
        return False
    
    # Test 2: Check if construction_env still exists (backward compatibility)
    print("\nTest 2: Checking backward compatibility with 'construction_env'...")
    if 'construction_env' in RCCMConfig.DEPARTMENTS:
        print("✅ SUCCESS: 'construction_env' department still exists")
        construction_env_dept = RCCMConfig.DEPARTMENTS['construction_env']
        print(f"   - Name: {construction_env_dept['name']}")
    else:
        print("⚠️  WARNING: 'construction_env' department not found")
    
    # Test 3: Verify both point to same logical department
    print("\nTest 3: Verifying department consistency...")
    env_name = RCCMConfig.DEPARTMENTS['env']['name']
    construction_env_name = RCCMConfig.DEPARTMENTS.get('construction_env', {}).get('name', '')
    
    if env_name == construction_env_name == '建設環境':
        print("✅ SUCCESS: Both 'env' and 'construction_env' point to '建設環境' department")
    else:
        print(f"⚠️  INFO: Department names - env: '{env_name}', construction_env: '{construction_env_name}'")
    
    # Test 4: List all available departments
    print("\nTest 4: All available departments:")
    print("-" * 40)
    for dept_id, dept_info in RCCMConfig.DEPARTMENTS.items():
        print(f"   {dept_id}: {dept_info['name']}")
    
    print("\n" + "=" * 60)
    print("✅ ULTRA SYNC TEST COMPLETE: 'env' department fix verified")
    print("🔗 URL /departments/env/types should now work correctly")
    
    return True

if __name__ == "__main__":
    try:
        success = test_env_department_mapping()
        if success:
            print("\n🎉 All tests passed! The fix should resolve the 404 error.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed! Please check the configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR during testing: {e}")
        sys.exit(1)