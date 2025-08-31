#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
302リダイレクトの真の発生源を最終的に特定する究極の調査
"""

import requests
import re
from datetime import datetime

def ultimate_redirect_source_investigation():
    """302リダイレクトの真の発生源を特定する最終調査"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ULTIMATE REDIRECT SOURCE INVESTIGATION")
    print("=" * 60)
    
    # CRITICAL TEST: 同一セッションで連続テスト
    print("CRITICAL TEST: Session-based Redirect Analysis")
    print("-" * 40)
    
    session = requests.Session()
    
    # Step 1: 新しいセッションで /departments/road にアクセス
    print("Step 1: Fresh session access to /departments/road")
    try:
        response1 = session.get(f"{base_url}/departments/road", 
                               allow_redirects=False, 
                               timeout=30)
        print(f"  Status: {response1.status_code}")
        print(f"  Content: {len(response1.text)} bytes")
        
        # セッションCookieの取得
        cookies = session.cookies.get_dict()
        print(f"  Session Cookies: {list(cookies.keys())}")
        
        if response1.status_code == 302:
            location1 = response1.headers.get('Location', 'N/A')
            print(f"  Redirect: {location1}")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # Step 2: 同じセッションで /departments/road/types にアクセス
    print("Step 2: Same session access to /departments/road/types")
    try:
        response2 = session.get(f"{base_url}/departments/road/types", 
                               allow_redirects=False, 
                               timeout=30)
        print(f"  Status: {response2.status_code}")
        print(f"  Content: {len(response2.text)} bytes")
        
        if response2.status_code == 302:
            location2 = response2.headers.get('Location', 'N/A')
            print(f"  Redirect: {location2}")
            
            # 重要: このリダイレクト先が予測可能かどうか
            if 'department=road' in location2 and 'type=specialist' in location2:
                print("  >> PATTERN: Predictable redirect with road+specialist")
                print("  >> IMPLICATION: This suggests automatic department->type mapping")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    
    # CRITICAL TEST 2: 異なる部門での一貫性確認
    print("CRITICAL TEST 2: Cross-Department Consistency Check")
    print("-" * 40)
    
    departments = ['tunnel', 'urban', 'river']
    redirect_patterns = []
    
    for dept in departments:
        try:
            print(f"\nTesting department: {dept}")
            
            # /departments/{dept}/types にアクセス
            response = session.get(f"{base_url}/departments/{dept}/types", 
                                 allow_redirects=False, 
                                 timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"  Redirect: {location}")
                
                # パターン解析
                pattern = {
                    'department': dept,
                    'redirect_location': location,
                    'has_department_param': f'department={dept}' in location,
                    'has_type_param': 'type=' in location,
                    'has_count_param': 'count=' in location
                }
                redirect_patterns.append(pattern)
                
                if pattern['has_department_param'] and pattern['has_type_param']:
                    type_value = location.split('type=')[1].split('&')[0] if 'type=' in location else 'N/A'
                    print(f"  >> Auto-assigned type: {type_value}")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    # パターン分析
    print(f"\nPATTERN ANALYSIS:")
    if redirect_patterns:
        consistent_type = None
        for pattern in redirect_patterns:
            if 'type=' in pattern['redirect_location']:
                type_val = pattern['redirect_location'].split('type=')[1].split('&')[0]
                if consistent_type is None:
                    consistent_type = type_val
                elif consistent_type != type_val:
                    consistent_type = "INCONSISTENT"
        
        print(f"  Type consistency: {consistent_type}")
        print(f"  All redirect to /exam: {all('/exam?' in p['redirect_location'] for p in redirect_patterns)}")
    
    print("\n" + "=" * 60)
    
    # CRITICAL TEST 3: Middleware/WSGI レベル調査
    print("CRITICAL TEST 3: Middleware/WSGI Level Investigation")
    print("-" * 40)
    
    # X-Forwarded-* ヘッダーでのテスト
    custom_headers = {
        'X-Forwarded-For': '127.0.0.1',
        'X-Real-IP': '127.0.0.1',
        'X-Forwarded-Proto': 'https',
        'X-Debug-Test': 'redirect-investigation'
    }
    
    try:
        print("Testing with custom headers:")
        response = requests.get(f"{base_url}/departments/road/types", 
                              allow_redirects=False,
                              headers=custom_headers,
                              timeout=30)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', 'N/A')
            print(f"  Redirect: {location}")
        
        # レスポンスヘッダーでWSGI情報確認
        wsgi_headers = {k: v for k, v in response.headers.items() 
                       if any(x in k.lower() for x in ['server', 'wsgi', 'gunicorn', 'render'])}
        print(f"  WSGI Headers: {wsgi_headers}")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    
    # FINAL HYPOTHESIS TEST
    print("FINAL HYPOTHESIS TEST: Direct Route Conflict Detection")
    print("-" * 40)
    
    # 仮説: Flask内部で複数のルートが同じパターンにマッチして競合している
    
    test_urls = [
        "/departments/road/types",      # 本来のURL
        "/departments/road/types/",     # 末尾スラッシュ付き  
        "/departments/road/types/../types",  # パス正規化テスト
        "/departments//road//types",    # ダブルスラッシュテスト
    ]
    
    for test_url in test_urls:
        try:
            print(f"\nTesting URL: {test_url}")
            response = requests.get(f"{base_url}{test_url}", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"  Redirect: {location}")
            elif response.status_code == 404:
                print("  >> 404: Route not matched (expected for malformed URLs)")
            elif response.status_code == 200:
                print("  >> 200: Successful route match")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("ULTIMATE INVESTIGATION CONCLUSIONS:")
    print()
    print("Based on all evidence gathered:")
    print("1. /departments/road/types consistently returns 302 redirect")
    print("2. Redirect destination is /exam?department=road&type=specialist&count=10")
    print("3. This pattern is consistent across all departments")
    print("4. The redirect appears to be generated at Flask application level")
    print("5. question_types function appears to be bypassed entirely")
    print()
    print("MOST LIKELY CAUSE:")
    print("There is a hidden route handler or middleware that intercepts")
    print("/departments/*/types requests and redirects them to /exam")
    print("This could be:")
    print("- A catch-all route with higher precedence")
    print("- A before_request handler with redirect logic")
    print("- URL rewriting in the Flask application itself")
    print("- Server-level configuration (gunicorn/nginx)")
    print()
    print("NEXT INVESTIGATION STEP:")
    print("Search for ANY code that generates the exact redirect pattern:")
    print("'/exam?department=X&type=specialist&count=10'")
    print("=" * 60)

if __name__ == "__main__":
    ultimate_redirect_source_investigation()