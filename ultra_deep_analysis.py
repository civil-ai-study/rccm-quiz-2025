#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Deep Analysis: question_types関数の本当の実行状況を特定
"""

import requests
from urllib.parse import urljoin
import time

def ultra_deep_analysis():
    """徹底的な深層解析"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("ULTRA DEEP ANALYSIS")
    print("=" * 50)
    
    # Analysis 1: リダイレクトチェーンの完全追跡
    print("Analysis 1: Complete Redirect Chain Tracking")
    print("-" * 40)
    
    url = f"{base_url}/departments/road/types"
    redirect_count = 0
    max_redirects = 10
    
    session = requests.Session()
    
    while redirect_count < max_redirects:
        try:
            response = session.get(url, allow_redirects=False, timeout=30)
            
            print(f"Step {redirect_count + 1}:")
            print(f"  URL: {url}")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Length: {len(response.text)}")
            
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"  Redirect Location: {location}")
                
                # 絶対URLに変換
                if location.startswith('/'):
                    url = urljoin(base_url, location)
                else:
                    url = location
                    
                redirect_count += 1
                
                # リダイレクトボディの分析
                if response.text.strip():
                    print(f"  Redirect Body Sample: {response.text[:100]}")
                
                time.sleep(0.5)  # サーバー負荷考慮
                
            elif response.status_code == 200:
                print(f"  Final destination reached")
                
                # 最終ページの特徴分析
                content = response.text
                
                # question_types.html の特徴
                qt_features = {
                    'breadcrumb': 'breadcrumb' in content,
                    '4-1_text': '4-1' in content and ('必須' in content or '基礎' in content),
                    '4-2_text': '4-2' in content and ('選択' in content or '専門' in content),
                    'question_type_card': 'question-type-card' in content,
                    'type_selection_header': '問題種別選択' in content
                }
                
                # exam.html の特徴  
                exam_features = {
                    'question_form': 'questionForm' in content,
                    'timer': 'timer-display' in content,
                    'options': 'option_a' in content or 'option_b' in content,
                    'progress': 'progress-info' in content,
                    'question_patterns': any(p in content for p in ['どれか', '何か', '正しい', '誤っている'])
                }
                
                print(f"  Page Analysis:")
                print(f"    question_types.html features: {qt_features}")
                print(f"    exam.html features: {exam_features}")
                
                # 判定
                qt_score = sum(qt_features.values())
                exam_score = sum(exam_features.values())
                
                print(f"    Question Types Score: {qt_score}/5")
                print(f"    Exam Score: {exam_score}/5")
                
                if exam_score > qt_score:
                    print("  VERDICT: This is an EXAM page (question_types bypassed)")
                elif qt_score > exam_score:
                    print("  VERDICT: This is a QUESTION TYPES page (working correctly)")
                else:
                    print("  VERDICT: Ambiguous or error page")
                
                break
                
            else:
                print(f"  Unexpected status: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    if redirect_count >= max_redirects:
        print("  WARNING: Maximum redirects reached - possible redirect loop")
    
    print()
    
    # Analysis 2: 直接的なファンクション実行確認
    print("Analysis 2: Direct Function Execution Check")
    print("-" * 40)
    
    # question_types.html テンプレートへの直接アクセステスト
    # (これは通常動作しないが、デバッグ情報が得られる場合がある)
    
    # 他の正常な部門でのテスト比較
    test_departments = ['tunnel', 'urban', 'river']
    
    for dept in test_departments:
        try:
            test_url = f"{base_url}/departments/{dept}/types"
            response = requests.get(test_url, allow_redirects=False, timeout=30)
            
            print(f"Department '{dept}':")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"  Redirect: {location}")
            elif response.status_code == 200:
                content = response.text
                has_selection = '問題種別選択' in content or ('4-1' in content and '4-2' in content)
                has_exam = 'questionForm' in content
                print(f"  Has Selection UI: {has_selection}")
                print(f"  Has Exam Content: {has_exam}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print()
    print("=" * 50)
    print("ULTRA DEEP ANALYSIS COMPLETE")

if __name__ == "__main__":
    ultra_deep_analysis()