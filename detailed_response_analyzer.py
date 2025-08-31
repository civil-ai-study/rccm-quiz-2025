#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門アクセス時の詳細レスポンス解析
実際に何が返されているかを完全に調査
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_road_department_response():
    """道路部門アクセス時のレスポンス詳細解析"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("DETAILED RESPONSE ANALYSIS for Road Department")
    print("=" * 60)
    
    # Test URL: /departments/road/types  
    test_url = f"{base_url}/departments/road/types"
    
    try:
        response = requests.get(test_url, timeout=30)
        
        print(f"URL: {test_url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Content-Length: {len(response.text)} bytes")
        print(f"Server: {response.headers.get('Server', 'Unknown')}")
        
        if response.status_code != 200:
            print(f"CRITICAL: Non-200 status code")
            return False
            
        # HTML解析
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # タイトル確認
        title = soup.find('title')
        if title:
            print(f"Page Title: {title.text}")
        else:
            print("Page Title: Not found")
        
        # 1. question_types.htmlテンプレートの特徴を探す
        print("\n=== question_types.html Template Features Check ===")
        
        # 特徴1: ブレッドクラム
        breadcrumb = soup.find('nav', {'aria-label': 'breadcrumb'})
        print(f"Breadcrumb navigation: {'Found' if breadcrumb else 'NOT FOUND'}")
        
        # 特徴2: 4-1と4-2の選択肢
        type_cards = soup.find_all('div', class_='question-type-card')
        print(f"Question type cards: {len(type_cards)} found")
        
        # 特徴3: 「4-1必須科目」「4-2選択科目」テキスト
        has_41_text = '4-1必須科目' in content or '4-1 必須科目' in content
        has_42_text = '4-2選択科目' in content or '4-2 選択科目' in content
        print(f"4-1 Basic text: {'Found' if has_41_text else 'NOT FOUND'}")
        print(f"4-2 Specialist text: {'Found' if has_42_text else 'NOT FOUND'}")
        
        # 特徴4: 「問題種別選択」ヘッダー
        has_type_selection_header = '問題種別選択' in content
        print(f"Question type selection header: {'Found' if has_type_selection_header else 'NOT FOUND'}")
        
        # 2. exam.htmlテンプレートの特徴を探す
        print("\n=== exam.html Template Features Check ===")
        
        # 特徴1: 問題文のパターン
        question_patterns = ['どれか', '何か', '誤っているもの', '正しいもの', '適切な', '不適切な']
        found_patterns = [p for p in question_patterns if p in content]
        print(f"Question text patterns: {found_patterns}")
        
        # 特徴2: 選択肢フォーム
        form = soup.find('form', id='questionForm')
        print(f"Question form (questionForm): {'Found' if form else 'NOT FOUND'}")
        
        # 特徴3: 進捗表示
        progress_info = soup.find('div', class_='progress-info')
        print(f"Progress info: {'Found' if progress_info else 'NOT FOUND'}")
        
        # 特徴4: タイマー表示
        timer = soup.find('span', id='timer-display')
        print(f"Timer display: {'Found' if timer else 'NOT FOUND'}")
        
        # 3. 実際のコンテンツの性質判定
        print("\n=== Content Nature Analysis ===")
        
        if form and any(found_patterns):
            print("VERDICT: This is showing EXAM QUESTION (exam.html)")
            print("PROBLEM: question_types function is NOT being called correctly")
        elif type_cards and (has_41_text or has_42_text):
            print("VERDICT: This is showing QUESTION TYPE SELECTION (question_types.html)")
            print("SUCCESS: question_types function is working correctly")
        else:
            print("VERDICT: Unknown template or error page")
            
        # 4. URL解析 - リダイレクトの確認
        print("\n=== Redirect Analysis ===")
        print(f"Final URL: {response.url}")
        if response.url != test_url:
            print(f"REDIRECT DETECTED: {test_url} -> {response.url}")
            # リダイレクトの理由を推測
            if 'exam' in response.url:
                print("LIKELY CAUSE: Direct redirect to exam function")
        else:
            print("NO REDIRECT: URL unchanged")
            
        # 5. 最初の500文字のサンプル表示
        print("\n=== Content Sample (first 500 chars) ===")
        clean_content = re.sub(r'\s+', ' ', content[:500])
        print(clean_content)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    analyze_road_department_response()