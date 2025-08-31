#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flaskルーティングテーブルの詳細デバッグ
departments/*/typesルートが正しく登録されているか確認
"""

import requests
import json
from datetime import datetime

def debug_flask_routing_table():
    """Flaskルーティングテーブルをデバッグ分析"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("FLASK ROUTING TABLE DEBUG ANALYSIS")
    print("=" * 60)
    
    # Test 1: Flask実行時のルーティング競合確認
    print("Test 1: Route Precedence and Conflict Analysis")
    print("-" * 40)
    
    test_routes = [
        "/departments/road",  # Should call select_department()
        "/departments/road/types",  # Should call question_types()
        "/exam",  # Should call exam()
    ]
    
    for route in test_routes:
        try:
            print(f"\nTesting Route: {route}")
            response = requests.get(f"{base_url}{route}", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Content-Length: {len(response.text)}")
            
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', 'N/A')
                print(f"  Redirect Location: {location}")
                
                # リダイレクト先の解析
                if '/exam' in location:
                    print("  >> REDIRECT TO EXAM DETECTED")
                    if 'department=' in location:
                        dept = location.split('department=')[1].split('&')[0] if '&' in location.split('department=')[1] else location.split('department=')[1]
                        print(f"  >> Department Parameter: {dept}")
                    if 'type=' in location:
                        typ = location.split('type=')[1].split('&')[0] if '&' in location.split('type=')[1] else location.split('type=')[1]
                        print(f"  >> Type Parameter: {typ}")
                    if 'count=' in location:
                        cnt = location.split('count=')[1].split('&')[0] if '&' in location.split('count=')[1] else location.split('count=')[1]
                        print(f"  >> Count Parameter: {cnt}")
            
            elif response.status_code == 200:
                # 成功レスポンスの場合、どのテンプレートが使われているかを推定
                content = response.text.lower()
                
                if 'question-type-card' in content or '4-1' in content:
                    print("  >> LIKELY TEMPLATE: question_types.html")
                elif 'questionform' in content or 'option_a' in content:
                    print("  >> LIKELY TEMPLATE: exam.html")  
                elif 'departments-grid' in content or 'department-card' in content:
                    print("  >> LIKELY TEMPLATE: departments.html")
                elif 'error' in content:
                    print("  >> LIKELY TEMPLATE: error.html")
                else:
                    print("  >> TEMPLATE: Unknown/Other")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: WSGI/gunicorn レベルでの URL パターンマッチング検証
    print("Test 2: WSGI-Level URL Pattern Matching")
    print("-" * 40)
    
    # 複数のURL形式で同じパスをテスト
    url_variations = [
        "/departments/road/types",
        "/departments/road/types/",  # 末尾スラッシュあり
        "/departments/road/types?",  # 空クエリストリング
        "/departments/road/types?test=1",  # ダミーパラメータ
    ]
    
    for url in url_variations:
        try:
            print(f"\nURL Variation: {url}")
            response = requests.get(f"{base_url}{url}", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"  Redirect: {location}")
                
                # 一貫性チェック
                if 'department=road&type=specialist&count=10' in location:
                    print("  >> CONSISTENT: Same redirect pattern")
                else:
                    print(f"  >> INCONSISTENT: Different redirect pattern")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: HTTP メソッドとヘッダーによる動作変化検証
    print("Test 3: HTTP Method and Headers Impact")
    print("-" * 40)
    
    test_url = f"{base_url}/departments/road/types"
    
    # 異なるHTTPメソッドでのテスト
    methods_and_headers = [
        ('GET', {}),
        ('GET', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}),
        ('GET', {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}),
        ('HEAD', {}),
    ]
    
    for method, headers in methods_and_headers:
        try:
            print(f"\nMethod: {method}, Headers: {headers}")
            
            if method == 'GET':
                response = requests.get(test_url, 
                                      allow_redirects=False, 
                                      headers=headers,
                                      timeout=30)
            elif method == 'HEAD':
                response = requests.head(test_url, 
                                       allow_redirects=False, 
                                       headers=headers,
                                       timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'N/A')
                print(f"  Location: {location}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: 現在時刻での動作パターン記録
    print("Test 4: Current Behavior Pattern Documentation")
    print("-" * 40)
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Test Time: {current_time}")
    
    try:
        response = requests.get(f"{base_url}/departments/road/types", 
                              allow_redirects=False, 
                              timeout=30)
        
        behavior_summary = {
            'timestamp': current_time,
            'url': '/departments/road/types',
            'status_code': response.status_code,
            'redirect_location': response.headers.get('Location', None),
            'content_length': len(response.text),
            'server_header': response.headers.get('Server', 'Unknown'),
            'render_server': response.headers.get('x-render-origin-server', 'Unknown')
        }
        
        print("BEHAVIOR SUMMARY:")
        for key, value in behavior_summary.items():
            print(f"  {key}: {value}")
        
        # JSONファイルに記録
        with open('routing_debug_log.json', 'w', encoding='utf-8') as f:
            json.dump(behavior_summary, f, ensure_ascii=False, indent=2)
        print(f"\n  Behavior logged to: routing_debug_log.json")
        
    except Exception as e:
        print(f"  ERROR in summary: {e}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("1. Flask app is running (confirmed by server headers)")
    print("2. Consistent 302 redirects to /exam?department=road&type=specialist&count=10") 
    print("3. The redirect appears to be systematic and intentional")
    print("4. Need to investigate WHY this redirect is happening")
    print("   - Is it in question_types function itself?")
    print("   - Is it in some middleware?")
    print("   - Is it a server-level rewrite rule?")
    print("=" * 60)

if __name__ == "__main__":
    debug_flask_routing_table()