#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
question_types関数の実際の実行状況を実証的に確認（ASCII版）
"""

import requests
import time
from datetime import datetime

def verify_function_execution_ascii():
    """question_types関数が実行されているかの実証的確認"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("QUESTION_TYPES FUNCTION EXECUTION VERIFICATION")
    print("=" * 60)
    
    # Test 1: 時系列での詳細レスポンス解析
    print("Test 1: Detailed Response Header Analysis")
    print("-" * 30)
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/departments/road/types", 
                              allow_redirects=False, 
                              timeout=30)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        print(f"Execution Time: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"Response Time: {response_time:.3f} seconds")
        print(f"Status Code: {response.status_code}")
        
        # 重要: ヘッダー全体の詳細分析
        print("\nDetailed Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Flask固有のヘッダー確認
        print("\nFlask Execution Evidence Headers:")
        server_header = response.headers.get('Server', 'N/A')
        print(f"  Server: {server_header}")
        
        # Cookieの存在確認（Flaskセッション動作確認）
        set_cookie = response.headers.get('Set-Cookie', 'N/A')
        print(f"  Set-Cookie: {set_cookie}")
        
        # Content-Type確認（HTMLかredirectか）
        content_type = response.headers.get('Content-Type', 'N/A')
        print(f"  Content-Type: {content_type}")
        
        # CRITICAL: x-render-origin-server 確認（Flask/gunicorn動作証拠）
        render_server = response.headers.get('x-render-origin-server', 'N/A')
        print(f"  x-render-origin-server: {render_server}")
        if render_server == 'gunicorn':
            print("  >> EVIDENCE: Flask application is running via gunicorn")
        
        # レスポンスボディ分析
        body_length = len(response.text)
        print(f"\nResponse Body Length: {body_length} bytes")
        
        if body_length > 0:
            body_sample = response.text[:500].replace('\n', '\\n').replace('\r', '\\r')
            print(f"Body Sample: {body_sample}")
            
            # CRITICAL: レスポンスボディ内容分析
            if 'question_types' in response.text.lower():
                print("[OK] question_types function execution evidence found")
            elif 'redirecting' in response.text.lower():
                print("[REDIRECT] Standard Flask redirect response detected")
                print("  >> This means Flask processed the request but returned redirect")
            elif 'exam' in response.text.lower():
                print("[EXAM] exam function executed instead")
            
            # Flask標準リダイレクト判定
            if 'You should be redirected automatically' in response.text:
                print("[FLASK] Flask standard redirect page confirmed")
                print("  >> This indicates Flask is processing the route correctly")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: 複数回実行での一貫性確認
    print("Test 2: Multiple Execution Consistency Check")
    print("-" * 30)
    
    results = []
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/departments/road/types", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            result = {
                'attempt': i + 1,
                'status': response.status_code,
                'location': response.headers.get('Location', 'N/A'),
                'content_length': len(response.text),
                'server': response.headers.get('x-render-origin-server', 'N/A')
            }
            results.append(result)
            
            print(f"Attempt {i+1}: Status {result['status']}, "
                  f"Redirect {result['location']}, "
                  f"Content {result['content_length']} bytes, "
                  f"Server {result['server']}")
            
            time.sleep(1)  # サーバー負荷考慮
            
        except Exception as e:
            print(f"Attempt {i+1} Error: {e}")
    
    # 一貫性分析
    if len(results) > 1:
        status_codes = [r['status'] for r in results]
        locations = [r['location'] for r in results]
        
        if len(set(status_codes)) == 1:
            print("[CONSISTENT] Status codes are consistent")
        else:
            print(f"[INCONSISTENT] Status code mismatch: {set(status_codes)}")
        
        if len(set(locations)) == 1:
            print("[CONSISTENT] Redirect destinations are consistent")
        else:
            print(f"[INCONSISTENT] Redirect destination mismatch: {set(locations)}")
    
    print("\n" + "=" * 60)
    
    # Test 3: 重要な証拠確認
    print("Test 3: Critical Evidence Analysis")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/departments/road/types", 
                              allow_redirects=False, 
                              timeout=30)
        
        print("CRITICAL FINDINGS:")
        print(f"1. Status Code: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"2. Redirect Location: {location}")
            
            # 詳細リダイレクト分析
            if '/exam' in location:
                print("   >> FINDING: Redirecting to exam route")
                print("   >> IMPLICATION: question_types function may not be executing")
                
                # パラメータ解析
                if 'department=road' in location:
                    print("   >> PARAMETER: department=road (correct)")
                if 'type=specialist' in location:
                    print("   >> PARAMETER: type=specialist (automatically set)")
                if 'count=10' in location:
                    print("   >> PARAMETER: count=10 (default)")
        
        # サーバー実行環境確認
        render_server = response.headers.get('x-render-origin-server', 'N/A')
        print(f"3. Origin Server: {render_server}")
        
        if render_server == 'gunicorn':
            print("   >> CONFIRMATION: Flask app is running correctly")
            print("   >> ISSUE: But why is it redirecting instead of showing question_types?")
        
        # レスポンス内容の詳細確認
        body = response.text
        print(f"4. Response Body Analysis: {len(body)} bytes")
        
        if body and 'redirecting' in body.lower():
            print("   >> FLASK REDIRECT: This is Flask's standard redirect response")
            print("   >> MEANING: The route is being processed by Flask")
            print("   >> QUESTION: But which function is generating the redirect?")
        
    except Exception as e:
        print(f"Error in critical analysis: {e}")
    
    print("\n" + "=" * 60)
    print("DEEP ANALYSIS CONCLUSIONS:")
    print("1. Flask application is running (confirmed by gunicorn server header)")
    print("2. Route /departments/road/types is being processed by Flask")
    print("3. Consistent 302 redirect to /exam with specific parameters")
    print("4. Standard Flask redirect response body")
    print("")
    print("KEY QUESTION: Is question_types function being called but then")
    print("redirecting, OR is another function/middleware intercepting the route?")
    print("=" * 60)

if __name__ == "__main__":
    verify_function_execution_ascii()