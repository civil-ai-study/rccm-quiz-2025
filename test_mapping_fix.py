"""
英語→日本語マッピング修正がちゃんと動作しているかテスト
"""
import requests
import re

BASE_URL = "https://rccm-quiz-2025.onrender.com"

def test_mapping():
    """河川専門問題のマッピングをテスト"""
    
    # 河川専門問題を取得
    session = requests.Session()
    response = session.get(f"{BASE_URL}/exam?department=river&question_type=specialist&category=all")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        html = response.text
        
        # QIDを抽出
        qid_match = re.search(r'name="qid" value="([^"]*)"', html)
        if qid_match:
            qid = qid_match.group(1)
            print(f"取得されたQID: {qid}")
            
            # 問題文の一部を確認
            question_match = re.search(r'<h3[^>]*>問題 \d+</h3>\s*<p[^>]*>([^<]+)', html)
            if question_match:
                question_text = question_match.group(1)[:50]
                print(f"問題文の一部: {question_text}")
                
                # 河川関連キーワードチェック
                river_keywords = ['河川', '砂防', '海岸', '海洋', '流域', '洪水', '治水', '水文']
                has_river_keyword = any(keyword in question_text for keyword in river_keywords)
                print(f"河川関連キーワード検出: {has_river_keyword}")
                
                if not has_river_keyword:
                    print("⚠️ 警告: 河川専門を選択したのに河川関連問題ではない")
                else:
                    print("✅ 正常: 河川関連問題が正しく表示されている")
            else:
                print("問題文の抽出に失敗")
        else:
            print("QIDの抽出に失敗")
    else:
        print(f"リクエスト失敗: {response.status_code}")

if __name__ == "__main__":
    test_mapping()