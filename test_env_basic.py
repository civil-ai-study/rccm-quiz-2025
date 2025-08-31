#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC STAGE 9: 問題種別選択画面の基本動作確認
"""

import requests

def test_env_department_basic():
    """建設環境部門の基本テスト"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ULTRA SYNC STAGE 9: Basic Test Start")
    print("="*50)
    
    # Test the critical URL that was failing for 1 month
    test_url = f"{base_url}/departments/env/types"
    
    try:
        response = requests.get(test_url, timeout=30)
        
        print(f"URL: {test_url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for question types
            has_41 = "4-1" in content
            has_42 = "4-2" in content  
            has_basic = "基礎" in content
            has_specialist = "選択" in content or "専門" in content
            
            # Check for department info
            has_env = "建設環境" in content or "env" in content
            
            # Check for HTML structure
            has_html = "<html" in content and "</html>" in content
            
            print("\n=== Content Analysis ===")
            print(f"Has 4-1: {has_41}")
            print(f"Has 4-2: {has_42}")
            print(f"Has Basic: {has_basic}")
            print(f"Has Specialist: {has_specialist}")
            print(f"Has Environment: {has_env}")
            print(f"Valid HTML: {has_html}")
            
            if has_html and (has_41 or has_basic) and (has_42 or has_specialist):
                print("\n*** SUCCESS: Question type selection page working! ***")
                print("*** 1-month bug FIXED! ***")
                return True
            else:
                print("\n*** PARTIAL: Page loads but content incomplete ***")
                return False
                
        elif response.status_code == 302:
            print("FAILED: Still redirecting (routing issue)")
            print(f"Redirect to: {response.headers.get('Location', 'Unknown')}")
            return False
        elif response.status_code == 404:
            print("FAILED: Page not found (routing issue)")
            return False
        else:
            print(f"FAILED: Unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_env_department_basic()
    
    print("\n" + "="*50)
    if success:
        print("ULTRA SYNC STAGE 9: COMPLETE SUCCESS")
        print("/departments/env/types is now WORKING!")
    else:
        print("ULTRA SYNC STAGE 9: NEEDS MORE WORK")
        print("Issue still exists")