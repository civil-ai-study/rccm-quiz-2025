#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC Test: Verify 'env' department fix (ASCII safe)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import RCCMConfig

def test_env_department():
    print("ULTRA SYNC TEST: Verifying env department mapping fix")
    print("=" * 50)
    
    # Test if 'env' exists
    if 'env' in RCCMConfig.DEPARTMENTS:
        print("SUCCESS: env department found")
        env_dept = RCCMConfig.DEPARTMENTS['env']
        print(f"Name: {env_dept['name']}")
        print(f"Description: {env_dept['description']}")
        print(f"Icon: {env_dept['icon']}")
        
        # Test if it points to correct department
        if env_dept['name'] == "建設環境":
            print("SUCCESS: env points to Construction Environment")
            return True
        else:
            print(f"ERROR: env points to wrong department: {env_dept['name']}")
            return False
    else:
        print("ERROR: env department not found")
        return False

if __name__ == "__main__":
    success = test_env_department()
    if success:
        print("\nALL TESTS PASSED - env department fix successful!")
        print("URL /departments/env/types should now work")
    else:
        print("\nTEST FAILED - fix needs review")