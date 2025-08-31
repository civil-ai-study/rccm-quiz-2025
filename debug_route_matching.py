#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ルートマッチング問題のデバッグ
"""

import requests

def debug_route_matching():
    """ルートマッチング問題をデバッグ"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ROUTE MATCHING DEBUG")
    print("=" * 40)
    
    # Test 1: /departments/road (単体)
    print("Test 1: /departments/road")
    try:
        response = requests.get(f"{base_url}/departments/road", allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"Redirect to: {response.headers.get('Location', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: /departments/road/types
    print("Test 2: /departments/road/types")  
    try:
        response = requests.get(f"{base_url}/departments/road/types", allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"Redirect to: {response.headers.get('Location', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Invalid department to see error handling
    print("Test 3: /departments/nonexistent")
    try:
        response = requests.get(f"{base_url}/departments/nonexistent", allow_redirects=False) 
        print(f"Status: {response.status_code}")
        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"Redirect to: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 200:
            if 'error' in response.text.lower():
                print("Error page returned (expected)")
            else:
                print("Unexpected success response")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_route_matching()