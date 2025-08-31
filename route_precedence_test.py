#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Route Precedence Test - Flask routing precedence issue investigation
"""

import requests

def test_route_precedence():
    """Test Flask route precedence issue"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ROUTE PRECEDENCE INVESTIGATION")
    print("=" * 50)
    
    # Test 1: /departments/road (should match /departments/<department_id>)
    print("Test 1: /departments/road")
    try:
        response = requests.get(f"{base_url}/departments/road", allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirects to: {location}")
            # この場合、location は /departments/road/types になるはず
        elif response.status_code == 200:
            print("Returns 200 (no redirect)")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: /departments/road/types (should match /departments/<department_id>/types)
    print("Test 2: /departments/road/types")
    try:
        response = requests.get(f"{base_url}/departments/road/types", allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirects to: {location}")
            
            # 重要: ここで /exam へのリダイレクトが発生している
            # これは question_types 関数ではなく、別の処理が実行されていることを示す
            
        elif response.status_code == 200:
            print("Returns 200 (question_types function executed)")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Check if /departments/road%2Ftypes is being treated as a single parameter
    print("Test 3: URL encoding check")
    encoded_url = f"{base_url}/departments/road%2Ftypes"
    try:
        response = requests.get(encoded_url, allow_redirects=False)
        print(f"Encoded URL Status: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Encoded URL Redirects to: {location}")
    except Exception as e:
        print(f"Encoded URL Error: {e}")
    
    print()
    
    # Hypothesis Test: Check if Flask is misinterpreting the route
    print("HYPOTHESIS:")
    print("1. /departments/road/types should match route: @app.route('/departments/<department_id>/types')")
    print("2. department_id should be 'road'")
    print("3. Function question_types(department_id='road') should be called")
    print("4. But instead, some OTHER function is being called that returns a redirect")
    
    print("\nPOSSIBLE CAUSES:")
    print("1. Route precedence issue (unlikely with Flask's specific routing)")
    print("2. Hidden global redirect rule")
    print("3. Exception in question_types function causing redirect")
    print("4. Server-side URL rewriting")

if __name__ == "__main__":
    test_route_precedence()