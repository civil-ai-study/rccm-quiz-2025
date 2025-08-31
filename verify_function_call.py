#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
question_types関数が実際に呼ばれているかの検証
"""

import requests

def verify_function_call():
    """question_types関数呼び出し検証"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("VERIFYING question_types function execution")
    print("=" * 50)
    
    # /departments/road/types にアクセスして、実際の応答を詳細確認
    test_url = f"{base_url}/departments/road/types"
    
    try:
        response = requests.get(test_url, timeout=30, allow_redirects=False)
        
        print(f"Initial Request: {test_url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Length: {len(response.text)} bytes")
        
        # リダイレクトレスポンスの確認
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', 'No Location header')
            print(f"REDIRECT DETECTED!")
            print(f"Redirect Location: {location}")
            print(f"Redirect Status: {response.status_code}")
            
            # リダイレクト元のボディ確認
            print(f"Redirect Body Length: {len(response.text)}")
            if response.text.strip():
                print(f"Redirect Body Sample: {response.text[:200]}")
            else:
                print("Redirect Body: Empty")
                
            # これは、question_types関数が呼ばれる前にリダイレクトが発生していることを示している
            print("\nCONCLUSION: question_types function is NOT being called")
            print("There's a redirect happening BEFORE the function executes")
            
            return False
            
        elif response.status_code == 200:
            print("Status 200: Direct response (no redirect)")
            
            # レスポンス内容の基本確認
            content = response.text
            
            # question_types.htmlの特徴があるか確認
            has_type_selection = any(pattern in content for pattern in [
                '問題種別選択', '4-1必須科目', '4-2選択科目', 'question-type-card'
            ])
            
            # exam.htmlの特徴があるか確認  
            has_exam_content = any(pattern in content for pattern in [
                'questionForm', 'timer-display', 'option_a', 'elapsedTime'
            ])
            
            print(f"Has question type selection content: {has_type_selection}")
            print(f"Has exam question content: {has_exam_content}")
            
            if has_exam_content and not has_type_selection:
                print("\nCONCLUSION: question_types function is being BYPASSED")
                print("Direct exam content is being returned instead")
                return False
            elif has_type_selection and not has_exam_content:
                print("\nCONCLUSION: question_types function is working correctly")
                return True
            else:
                print("\nCONCLUSION: Unexpected content mix or error")
                return False
                
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response body: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    result = verify_function_call()
    
    print("\n" + "=" * 50)
    if result:
        print("RESULT: question_types function IS working")
    else:
        print("RESULT: question_types function IS NOT working")
        print("Need to find the bypass/redirect mechanism")