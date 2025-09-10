"""
実際のall_questionsデータに河川関連問題が含まれているか検証
load_rccm_data_files関数の動作を直接確認
"""
import os
import sys
sys.path.append('.')

from utils import load_rccm_data_files
from config import DataConfig

def verify_data_loading():
    """データロード検証"""
    
    print("=== データロード検証開始 ===")
    
    # 実際のデータディレクトリパス
    data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
    print(f"データディレクトリ: {data_dir}")
    
    # load_rccm_data_files関数を直接呼び出し
    all_questions = load_rccm_data_files(data_dir)
    print(f"総問題数: {len(all_questions)}")
    
    # 専門科目問題を抽出
    specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
    print(f"専門科目問題数: {len(specialist_questions)}")
    
    # 河川関連問題を検索
    river_questions = [q for q in specialist_questions if q.get('category') == '河川、砂防及び海岸・海洋']
    print(f"河川関連問題数: {len(river_questions)}")
    
    if river_questions:
        print("\n=== 河川関連問題の例 ===")
        for i, q in enumerate(river_questions[:3]):
            print(f"{i+1}. ID={q.get('id')}, 年度={q.get('year')}, 問題文の一部: {q.get('question', '')[:30]}...")
    else:
        print("❌ 河川関連問題が見つかりません")
        
        # 全カテゴリを確認
        categories = set()
        for q in specialist_questions:
            cat = q.get('category')
            if cat:
                categories.add(cat)
        
        print(f"\n利用可能なカテゴリ一覧 ({len(categories)}種類):")
        for cat in sorted(categories):
            count = len([q for q in specialist_questions if q.get('category') == cat])
            print(f"  - {cat}: {count}問")
    
    # 土質及び基礎問題（誤って選択される問題）の確認
    soil_questions = [q for q in specialist_questions if q.get('category') == '土質及び基礎']
    print(f"\n土質及び基礎問題数: {len(soil_questions)}")
    if soil_questions:
        print("土質及び基礎問題のID例:")
        ids = [q.get('id') for q in soil_questions[:10]]
        print(f"  ID: {ids}")

if __name__ == "__main__":
    verify_data_loading()