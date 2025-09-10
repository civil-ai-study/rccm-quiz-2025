"""
QID検証エラーのデバッグ用スクリプト
実際に問題を再現してQIDの処理過程を調べる
"""
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 本番環境URL
BASE_URL = "https://rccm-quiz-2025.onrender.com"

def test_qid_issue():
    """QID検証エラーを再現"""
    
    session = requests.Session()
    
    # 1. 河川専門問題を開始
    print("=== 1. 河川専門問題を開始 ===")
    response = session.get(f"{BASE_URL}/exam?department=river&question_type=specialist&category=all")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("問題画面取得成功")
        
        # レスポンスからQID抽出
        html_content = response.text
        print(f"HTML長さ: {len(html_content)}")
        
        # QIDの存在確認
        import re
        qid_matches = re.findall(r'name="qid" value="([^"]*)"', html_content)
        if qid_matches:
            qid = qid_matches[0]
            print(f"抽出されたQID: '{qid}' (型: {type(qid)})")
            
            # CSRFトークンも抽出
            csrf_matches = re.findall(r'name="csrf_token" value="([^"]*)"', html_content)
            if csrf_matches:
                csrf_token = csrf_matches[0]
                print(f"CSRFトークン: {csrf_token[:20]}...")
                
                # 2. 解答送信テスト
                print("\n=== 2. 解答送信テスト ===")
                form_data = {
                    'answer': 'a',
                    'qid': qid,
                    'csrf_token': csrf_token
                }
                print(f"送信データ: {form_data}")
                
                response = session.post(f"{BASE_URL}/exam", data=form_data)
                print(f"POST Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    if "無効な問題IDです" in response.text:
                        print("🚨 無効な問題IDエラーが発生")
                        
                        # エラーページの内容を少し表示
                        print("エラーページの一部:")
                        lines = response.text.split('\n')
                        for i, line in enumerate(lines):
                            if "無効な問題ID" in line:
                                print(f"Line {i}: {line.strip()}")
                                break
                    else:
                        print("✅ 正常に処理された")
                else:
                    print(f"❌ POST失敗: {response.status_code}")
                    print(f"エラー内容: {response.text[:500]}...")
            else:
                print("❌ CSRFトークンが見つからない")
        else:
            print("❌ QIDが見つからない")
            print("HTML内容の一部:")
            print(html_content[:500])
    else:
        print(f"❌ 問題画面取得失敗: {response.status_code}")

if __name__ == "__main__":
    test_qid_issue()