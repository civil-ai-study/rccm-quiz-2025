# -*- coding: utf-8 -*-
"""
専門家推奨CSRF修正：最終動作検証テスト  
月間1→2問目進行バグ完全解決確認
"""

import requests
from bs4 import BeautifulSoup

def test_csrf_flow():
    """CSRF解決検証：1問目→2問目進行テスト"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("CSRF修正最終検証テスト")
    print("=" * 30)
    
    try:
        # 1. 1問目取得
        print("1. 1問目取得...")
        response = session.get(f"{base_url}/exam", params={
            'department': 'road',
            'question_type': 'specialist',
            'count': 10
        })
        
        if response.status_code != 200:
            print(f"失敗: {response.status_code}")
            return False
            
        # 2. CSRFトークン抽出
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input or not csrf_input.get('value'):
            print("CSRFトークンなし")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"CSRFトークン: {csrf_token[:20]}...")
        
        # 3. QID抽出
        qid_input = soup.find('input', {'name': 'qid'})
        if not qid_input:
            print("QIDなし")
            return False
        
        qid = qid_input.get('value')
        print(f"QID: {qid}")
        
        # 4. 進行状況確認（1/10表示）
        progress_text = soup.get_text()
        if "1/10" not in progress_text:
            print("1/10表示なし")
            return False
        
        print("1/10表示確認")
        
        # 5. 解答送信（1問目→2問目進行テスト）
        print("2. 解答送信...")
        
        post_data = {
            'csrf_token': csrf_token,
            'qid': qid,
            'selected_option': 'A',
            'elapsed': 30
        }
        
        post_response = session.post(f"{base_url}/exam", data=post_data)
        
        # 6. POST成功判定
        if post_response.status_code != 200:
            print(f"POST失敗: Status={post_response.status_code}")
            print(f"エラー: {post_response.text[:300]}")
            return False
        
        print("POST成功: Status=200")
        
        # 7. 2問目進行確認
        post_soup = BeautifulSoup(post_response.text, 'html.parser')
        progress_text = post_soup.get_text()
        
        if "2/10" in progress_text:
            print("SUCCESS: 2/10進行確認!")
            return True
        elif "1/10" in progress_text:
            print("まだ1/10のまま")
            return False
        else:
            print("進行状況不明")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_csrf_flow()
    
    if success:
        print("\n完全解決！1→2問目進行成功")
    else:
        print("\nまだ問題あり")