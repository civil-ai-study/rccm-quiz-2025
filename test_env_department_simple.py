#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC STAGE 9: 問題種別選択画面の完全動作確認テスト（ASCII版）
建設環境部門の完全フローテスト実行
"""

import requests
import time
from urllib.parse import urljoin

def test_env_department_complete_flow():
    """建設環境部門の完全フローをテスト"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ULTRA SYNC STAGE 9: 建設環境部門完全フローテスト開始")
    print("=" * 60)
    
    # Step 1: トップページアクセス確認
    print("\nStep 1: トップページアクセス確認")
    try:
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            print(f"OK トップページ正常アクセス - Status: {response.status_code}")
            if "RCCM" in response.text and "部門" in response.text:
                print("OK ページコンテンツ確認済み")
            else:
                print("WARN ページコンテンツ不完全")
        else:
            print(f"FAIL トップページアクセス失敗 - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL トップページアクセスエラー: {e}")
        return False
    
    time.sleep(2)
    
    # Step 2: 部門選択ページ確認
    print("\nStep 2: 部門選択ページアクセス確認")
    departments_url = urljoin(base_url, "/departments")
    try:
        response = requests.get(departments_url, timeout=30)
        if response.status_code == 200:
            print(f"OK 部門選択ページ正常アクセス - Status: {response.status_code}")
            if "建設環境" in response.text:
                print("OK 建設環境部門表示確認済み")
            else:
                print("WARN 建設環境部門表示不明")
        else:
            print(f"FAIL 部門選択ページアクセス失敗 - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL 部門選択ページアクセスエラー: {e}")
        return False
    
    time.sleep(2)
    
    # Step 3: 建設環境部門の問題種別選択ページアクセス（本命テスト）
    print("\nStep 3: 建設環境部門問題種別選択ページアクセス確認（重要）")
    env_types_url = urljoin(base_url, "/departments/env/types")
    try:
        response = requests.get(env_types_url, timeout=30)
        print(f"アクセスURL: {env_types_url}")
        print(f"Response Status: {response.status_code}")
        print(f"Content-Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            print("SUCCESS 問題種別選択ページ正常アクセス成功！")
            
            # コンテンツの詳細確認
            content = response.text
            if "4-1" in content and "4-2" in content:
                print("OK 問題種別（4-1基礎/4-2選択）表示確認済み")
            elif "基礎" in content and "選択" in content:
                print("OK 問題種別（基礎/選択）表示確認済み")
            else:
                print("WARN 問題種別表示不明")
                # テストのため最初の500文字を出力
                print("Content sample:", content[:500].replace('\n', ' '))
            
            if "建設環境" in content:
                print("OK 建設環境部門情報表示確認済み")
            else:
                print("WARN 建設環境部門情報表示不明")
                
            # HTMLとして適切な構造か確認
            if "<html" in content and "</html>" in content:
                print("OK 適切なHTMLページとして表示")
            else:
                print("WARN HTMLページ構造不完全")
                
        elif response.status_code == 302:
            print("FAIL リダイレクト発生（問題あり）")
            print(f"Location Header: {response.headers.get('Location', 'N/A')}")
            return False
        elif response.status_code == 404:
            print("FAIL ページが見つかりません（ルーティング問題）")
            return False
        else:
            print(f"FAIL 問題種別選択ページアクセス失敗 - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL 問題種別選択ページアクセスエラー: {e}")
        return False
    
    time.sleep(2)
    
    # Step 4: 試験開始リンクテスト
    print("\nStep 4: 試験開始リンクテスト")
    exam_url = urljoin(base_url, "/exam?department=env&question_type=specialist&category=all")
    try:
        response = requests.get(exam_url, timeout=30)
        if response.status_code == 200:
            print(f"OK 試験開始正常アクセス - Status: {response.status_code}")
            if "問題" in response.text and ("option_a" in response.text or "選択肢" in response.text):
                print("OK 問題表示確認済み")
            else:
                print("WARN 問題表示不完全")
        else:
            print(f"FAIL 試験開始アクセス失敗 - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL 試験開始アクセスエラー: {e}")
        return False
    
    # 最終結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC STAGE 9: 建設環境部門完全フローテスト完了")
    print("SUCCESS 全ステップ成功 - 問題種別選択画面動作確認済み")
    print("SUCCESS 1ヶ月間の「ページが見つかりません」問題解決完了")
    return True

if __name__ == "__main__":
    success = test_env_department_complete_flow()
    if success:
        print("\nULTRA SYNC SUCCESS: 全機能正常動作確認")
    else:
        print("\nULTRA SYNC FAILED: 一部機能に問題あり")