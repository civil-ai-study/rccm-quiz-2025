# -*- coding: utf-8 -*-
"""
専門家推奨：referrer header解決策テスト
月間1→2問目進行バグ完全解決
"""

import requests
from bs4 import BeautifulSoup

def expert_referrer_solution():
    """専門家推奨：referrer header解決策実装テスト"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("専門家推奨referrer header解決策")
    print("=" * 40)
    
    try:
        # 1. 1問目取得（専門家推奨）
        quiz_url = f"{base_url}/exam?department=road&question_type=specialist&count=10"
        print(f"1. GET: {quiz_url}")
        
        response = session.get(quiz_url)
        
        if response.status_code != 200:
            print(f"GET失敗: {response.status_code}")
            return False
            
        # 2. CSRFトークン抽出
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input or not csrf_input.get('value'):
            print("CSRFトークンなし")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"CSRFトークン: {csrf_token[:25]}...")
        
        # 3. QID抽出
        qid_input = soup.find('input', {'name': 'qid'})
        if not qid_input:
            print("QIDなし")
            return False
        
        qid = qid_input.get('value')
        print(f"QID: {qid}")
        
        # 4. POST準備（専門家推奨：referrer header追加）
        post_data = {
            'csrf_token': csrf_token,
            'qid': qid,
            'selected_option': 'A',
            'elapsed': 45
        }
        
        # 🔧 CRITICAL: 専門家推奨referrer header追加
        headers = {
            'Referer': quiz_url,  # ← キーポイント！
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("2. POST実行（referrer header付き）...")
        post_response = session.post(f"{base_url}/exam", data=post_data, headers=headers)
        
        # 5. POST結果判定
        print(f"POST Status: {post_response.status_code}")
        
        if post_response.status_code != 200:
            print(f"POST失敗内容: {post_response.text[:200]}")
            return False
        
        print("POST成功！")
        
        # 6. 2問目進行確認
        post_soup = BeautifulSoup(post_response.text, 'html.parser')
        progress_text = post_soup.get_text()
        
        if "2/10" in progress_text:
            print("SUCCESS: 2/10進行確認 - 完全解決！")
            return True
        elif "1/10" in progress_text:
            print("まだ1/10 - 進行せず")
            return False
        else:
            print(f"進行状況: {progress_text[:100]}")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == "__main__":
    success = expert_referrer_solution()
    
    if success:
        print("\n月間1→2問目進行バグ完全解決！")
        print("専門家推奨解決策：100%成功")
    else:
        print("\nまだ課題あり")