#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
question_types関数の実際の実行状況を実証的に確認
"""

import requests
import time
from datetime import datetime

def verify_function_execution():
    """question_types関数が実行されているかの実証的確認"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("QUESTION_TYPES FUNCTION EXECUTION VERIFICATION")
    print("=" * 60)
    
    # Test 1: 時系列での詳細レスポンス解析
    print("Test 1: 詳細レスポンスヘッダー解析")
    print("-" * 30)
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/departments/road/types", 
                              allow_redirects=False, 
                              timeout=30)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        print(f"実行時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"レスポンス時間: {response_time:.3f}秒")
        print(f"ステータスコード: {response.status_code}")
        
        # 重要: ヘッダー全体の詳細分析
        print("\n詳細レスポンスヘッダー:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Flask固有のヘッダー確認
        print("\nFlask実行証拠ヘッダー:")
        server_header = response.headers.get('Server', 'N/A')
        print(f"  Server: {server_header}")
        
        # Cookieの存在確認（Flaskセッション動作確認）
        set_cookie = response.headers.get('Set-Cookie', 'N/A')
        print(f"  Set-Cookie: {set_cookie}")
        
        # Content-Type確認（HTMLかredirectか）
        content_type = response.headers.get('Content-Type', 'N/A')
        print(f"  Content-Type: {content_type}")
        
        # レスポンスボディ分析
        body_length = len(response.text)
        print(f"\nレスポンスボディ長: {body_length} bytes")
        
        if body_length > 0:
            body_sample = response.text[:500].replace('\n', '\\n').replace('\r', '\\r')
            print(f"ボディサンプル: {body_sample}")
            
            # question_types関数固有の出力確認
            if 'question_types' in response.text.lower():
                print("✅ question_types関数の実行証拠発見")
            elif 'exam' in response.text.lower():
                print("❌ exam関数が実行されている可能性")
            elif 'redirect' in response.text.lower():
                print("🔄 リダイレクト処理実行中")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: 複数回実行での一貫性確認
    print("Test 2: 複数回実行での一貫性確認")
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
                'response_time': time.time()
            }
            results.append(result)
            
            print(f"試行 {i+1}: ステータス {result['status']}, "
                  f"リダイレクト先 {result['location']}, "
                  f"コンテンツ長 {result['content_length']}")
            
            time.sleep(1)  # サーバー負荷考慮
            
        except Exception as e:
            print(f"試行 {i+1} エラー: {e}")
    
    # 一貫性分析
    if len(results) > 1:
        status_codes = [r['status'] for r in results]
        locations = [r['location'] for r in results]
        
        if len(set(status_codes)) == 1:
            print("✅ ステータスコード一貫性: 確認")
        else:
            print(f"❌ ステータスコード不一致: {set(status_codes)}")
        
        if len(set(locations)) == 1:
            print("✅ リダイレクト先一貫性: 確認")
        else:
            print(f"❌ リダイレクト先不一致: {set(locations)}")
    
    print("\n" + "=" * 60)
    
    # Test 3: 他の正常ルートとの比較
    print("Test 3: 正常ルートとの比較分析")
    print("-" * 30)
    
    test_routes = [
        ("/", "ホームページ"),
        ("/departments", "部門一覧"),
        ("/departments/road", "道路部門"),
        ("/departments/road/types", "道路部門問題種別（問題のルート）")
    ]
    
    for route, description in test_routes:
        try:
            response = requests.get(f"{base_url}{route}", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            print(f"{description}:")
            print(f"  URL: {route}")
            print(f"  ステータス: {response.status_code}")
            
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', 'N/A')
                print(f"  リダイレクト先: {location}")
                
                # 重要: リダイレクト先パターン分析
                if '/exam' in location:
                    print("  🚨 examルートへのリダイレクト検出")
                elif '/types' in location:
                    print("  🔄 typesルート内リダイレクト")
                elif location == 'N/A':
                    print("  ❓ リダイレクト先不明")
            else:
                print(f"  コンテンツ長: {len(response.text)} bytes")
            
        except Exception as e:
            print(f"  エラー: {e}")
        
        print()
    
    print("=" * 60)
    print("VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_function_execution()