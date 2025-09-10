"""
本番環境で実際に使用されているall_questionsデータを調査
get_mixed_questions関数の動作を直接シミュレート
"""
import requests
import re

BASE_URL = "https://rccm-quiz-2025.onrender.com"

def debug_production_data():
    """本番環境データのデバッグ"""
    
    print("=== 本番環境データ調査 ===")
    
    # 河川専門問題を複数回取得してIDパターンを確認
    session = requests.Session()
    
    ids_collected = []
    for attempt in range(5):
        print(f"\n--- 試行 {attempt + 1} ---")
        
        response = session.get(f"{BASE_URL}/exam?department=river&question_type=specialist&category=all")
        
        if response.status_code == 200:
            # QIDを抽出
            qid_match = re.search(r'name="qid" value="([^"]*)"', response.text)
            if qid_match:
                qid = qid_match.group(1)
                ids_collected.append(qid)
                print(f"取得されたQID: {qid}")
                
                # 問題文の一部を抽出して河川関連かチェック
                question_match = re.search(r'<h3[^>]*>問題 \d+</h3>\s*<p[^>]*>([^<]+)', response.text)
                if question_match:
                    question_text = question_match.group(1)[:50]
                    print(f"問題文の一部: {question_text}")
                    
                    # 河川関連キーワードチェック
                    river_keywords = ['河川', '砂防', '海岸', '海洋', '流域', '洪水', '治水', '水文']
                    has_river_keyword = any(keyword in question_text for keyword in river_keywords)
                    print(f"河川関連キーワード: {has_river_keyword}")
                else:
                    print("問題文の抽出に失敗")
            else:
                print("QIDの抽出に失敗")
        else:
            print(f"リクエスト失敗: {response.status_code}")
        
        # セッションリセット（新しいセッションで次の問題を取得）
        session = requests.Session()
    
    print(f"\n=== 収集されたID一覧 ===")
    print(f"ID: {ids_collected}")
    
    # IDの範囲を分析
    if ids_collected:
        numeric_ids = []
        for id_str in ids_collected:
            try:
                numeric_ids.append(int(id_str))
            except ValueError:
                pass
        
        if numeric_ids:
            print(f"数値ID範囲: {min(numeric_ids)} - {max(numeric_ids)}")
            print(f"平均ID: {sum(numeric_ids) / len(numeric_ids):.1f}")
            
            # 期待される河川IDレンジ（1061-1383）と比較
            expected_min, expected_max = 1061, 1383
            actual_in_range = [id for id in numeric_ids if expected_min <= id <= expected_max]
            
            print(f"期待される河川IDレンジ（{expected_min}-{expected_max}）内のID: {actual_in_range}")
            if not actual_in_range:
                print("❌ 本番環境で河川IDレンジ外の問題が選択されています")
                print("   → フィルタリング処理が失敗している可能性")
            else:
                print("✅ 河川IDレンジ内の問題が正常に選択されています")

if __name__ == "__main__":
    debug_production_data()