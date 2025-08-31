#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/exam ルートがquestion_types.html特徴を持つレスポンスを返す原因を調査
"""

import requests
from datetime import datetime

def verify_exam_rendering_question_types():
    """exam関数がquestion_types.htmlをレンダリングしている可能性を検証"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("EXAM ROUTE RENDERING ANALYSIS")
    print("=" * 50)
    
    # Test 1: /examの詳細レスポンス分析
    print("Test 1: /exam Response Analysis")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/exam", 
                              allow_redirects=False, 
                              timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        print(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # question_types.htmlの特徴的な要素を検索
            qt_indicators = {
                'question-type-card': 'question-type-card' in content,
                'breadcrumb': 'breadcrumb' in content,
                '4-1_basic': '4-1' in content and ('基礎' in content or '必須' in content),
                '4-2_specialist': '4-2' in content and ('選択' in content or '専門' in content),
                'type_selection_ui': '問題種別' in content,
                'department_info': '部門' in content,
                'progress_display': '進捗' in content or 'progress' in content
            }
            
            # exam.htmlの特徴的な要素を検索  
            exam_indicators = {
                'question_form': 'questionform' in content,
                'answer_options': 'option_a' in content and 'option_b' in content,
                'timer_display': 'timer' in content,
                'submit_button': 'answer-submit' in content,
                'question_text': '問題' in content and '選択' in content,
                'explanation': '解説' in content
            }
            
            print("\nCONTENT ANALYSIS:")
            print("question_types.html indicators:")
            for indicator, present in qt_indicators.items():
                status = "PRESENT" if present else "ABSENT"
                print(f"  {indicator}: {status}")
            
            print("\nexam.html indicators:")
            for indicator, present in exam_indicators.items():
                status = "PRESENT" if present else "ABSENT"
                print(f"  {indicator}: {status}")
            
            # スコア計算
            qt_score = sum(qt_indicators.values())
            exam_score = sum(exam_indicators.values())
            
            print(f"\nSCORE ANALYSIS:")
            print(f"  question_types.html score: {qt_score}/7")
            print(f"  exam.html score: {exam_score}/6")
            
            if qt_score > exam_score:
                print("  >> VERDICT: This response has question_types.html characteristics")
            elif exam_score > qt_score:
                print("  >> VERDICT: This response has exam.html characteristics")
            else:
                print("  >> VERDICT: Mixed or unclear template characteristics")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: department & type パラメータ付きでの /exam アクセス
    print("Test 2: /exam with Parameters Analysis")
    print("-" * 30)
    
    test_urls = [
        "/exam?department=road&type=specialist&count=10",  # リダイレクト先のURL
        "/exam?department=road",
        "/exam?type=specialist", 
        "/exam?type=basic"
    ]
    
    for test_url in test_urls:
        try:
            print(f"\nTesting: {test_url}")
            response = requests.get(f"{base_url}{test_url}", 
                                  allow_redirects=False, 
                                  timeout=30)
            
            print(f"  Status: {response.status_code}")
            print(f"  Content Length: {len(response.text)}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # 重要な特徴の存在確認
                has_qt_features = ('4-1' in content and '4-2' in content) or 'question-type-card' in content
                has_exam_features = 'option_a' in content and 'option_b' in content
                
                if has_qt_features:
                    print("  >> CONTAINS: question_types features")
                if has_exam_features:
                    print("  >> CONTAINS: exam features")
                if not has_qt_features and not has_exam_features:
                    print("  >> CONTAINS: Other content (possibly error or different template)")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: 実際のHTMLサンプル取得
    print("Test 3: HTML Sample Extraction")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/exam", timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # HTML構造の重要部分を抽出
            import re
            
            # タイトル抽出
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "No title found"
            print(f"Page Title: {title}")
            
            # メインコンテンツ領域の検索
            main_content_patterns = [
                r'<div[^>]*class="[^"]*question-type[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*exam[^"]*"[^>]*>(.*?)</div>',
                r'<main[^>]*>(.*?)</main>',
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>'
            ]
            
            for i, pattern in enumerate(main_content_patterns):
                matches = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    sample = matches.group(1)[:200].replace('\n', ' ').replace('\r', ' ')
                    print(f"Content Pattern {i+1} Sample: {sample}...")
                    break
            
            # キーワード密度分析
            important_keywords = {
                '4-1': content.lower().count('4-1'),
                '4-2': content.lower().count('4-2'),
                '基礎': content.lower().count('基礎'),
                '専門': content.lower().count('専門'),
                '問題種別': content.lower().count('問題種別'),
                'option_a': content.lower().count('option_a'),
                'questionform': content.lower().count('questionform'),
                '選択してください': content.lower().count('選択してください')
            }
            
            print(f"\nKeyword Frequency Analysis:")
            for keyword, count in important_keywords.items():
                if count > 0:
                    print(f"  '{keyword}': {count} occurrences")
        
    except Exception as e:
        print(f"Error in HTML analysis: {e}")
    
    print("\n" + "=" * 50)
    print("ANALYSIS CONCLUSION:")
    print("If /exam returns question_types.html characteristics, then:")
    print("1. exam() function may be rendering question_types.html under certain conditions")
    print("2. OR there may be template inheritance/inclusion causing mixed content")
    print("3. OR there may be conditional rendering logic in exam() function")
    print("4. This could explain why /departments/road/types redirects to /exam")
    print("   - If exam() can handle question type selection, redirect makes sense")
    print("=" * 50)

if __name__ == "__main__":
    verify_exam_rendering_question_types()