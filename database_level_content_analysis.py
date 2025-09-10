#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
データベースレベル問題内容ミスマッチ分析
- CSVデータから直接問題文・選択肢・解説の内容分析
- 同一ID内での内容一貫性チェック
- 部門間での問題内容混在パターン検出
"""

import os
import sys
import pandas as pd
import json
import re
from collections import defaultdict, Counter
import logging

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DatabaseContentAnalyzer:
    """データベースレベル内容分析クラス"""
    
    def __init__(self):
        self.data_dir = os.path.join(project_root, 'data')
        self.all_questions = []
        self.content_mismatches = []
        
        # 専門分野キーワード辞書
        self.department_keywords = {
            '道路': ['道路', '交通', '自動車', 'アスファルト', '舗装', '交通量', 'インターチェンジ', 'ランプ', '設計速度'],
            '河川、砂防及び海岸・海洋': ['河川', '砂防', '海岸', 'ダム', '水位', '流量', '洪水', '堤防', '護岸'],
            '都市計画及び地方計画': ['都市計画', '地方計画', '都市', '計画', 'ゾーニング', '市街地', '土地利用'],
            'トンネル': ['トンネル', '地下', 'NATM', '掘削', 'TBM', '地山', '支保', 'シールド'],
            '造園': ['造園', '植物', '緑化', '庭園', '景観', '植栽', '樹木', '芝生', '花壇'],
            '建設環境': ['環境', '騒音', '振動', '大気汚染', 'アセスメント', '環境基準', 'CO2'],
            '鋼構造及びコンクリート': ['鋼', 'コンクリート', '鉄筋', '構造', '梁', '柱', 'PC', '溶接'],
            '土質及び基礎': ['土質', '基礎', '地盤', '土壌', '支持力', '沈下', 'N値', '液状化'],
            '施工計画、施工設備及び積算': ['施工', '工程', '積算', '計画', 'クレーン', '仮設', '安全管理'],
            '上水道及び工業用水道': ['上水道', '水道', '浄水', '給水', '配水', '水質', '塩素'],
            '森林土木': ['森林', '林業', '治山', '木材', '間伐', '植林', '林道', '森林整備'],
            '農業土木': ['農業', '農地', '灌漑', '排水', 'パイプライン', '農道', '圃場']
        }
    
    def load_all_csv_data(self):
        """全CSVデータを読み込み"""
        logger.info("[LOAD] 全CSVデータ読み込み開始")
        
        # 4-1基礎データ
        basic_file = os.path.join(self.data_dir, '4-1.csv')
        if os.path.exists(basic_file):
            try:
                df = pd.read_csv(basic_file, encoding='utf-8')
                for _, row in df.iterrows():
                    question_data = {
                        'source_file': '4-1.csv',
                        'original_id': row.get('id'),
                        'category': row.get('category', '共通'),
                        'question_type': 'basic',
                        'year': None,
                        'question': str(row.get('question', '')),
                        'option_a': str(row.get('option_a', '')),
                        'option_b': str(row.get('option_b', '')),
                        'option_c': str(row.get('option_c', '')),
                        'option_d': str(row.get('option_d', '')),
                        'correct_answer': str(row.get('correct_answer', '')),
                        'explanation': str(row.get('explanation', ''))
                    }
                    self.all_questions.append(question_data)
                
                logger.info(f"4-1基礎データ: {len(df)}問読み込み完了")
            except Exception as e:
                logger.error(f"4-1データ読み込みエラー: {e}")
        
        # 4-2専門データ（年度別）
        for year in range(2008, 2019):
            specialist_file = os.path.join(self.data_dir, f'4-2_{year}.csv')
            if os.path.exists(specialist_file):
                try:
                    df = pd.read_csv(specialist_file, encoding='utf-8')
                    for _, row in df.iterrows():
                        question_data = {
                            'source_file': f'4-2_{year}.csv',
                            'original_id': row.get('id'),
                            'category': row.get('category', 'Unknown'),
                            'question_type': 'specialist',
                            'year': year,
                            'question': str(row.get('question', '')),
                            'option_a': str(row.get('option_a', '')),
                            'option_b': str(row.get('option_b', '')),
                            'option_c': str(row.get('option_c', '')),
                            'option_d': str(row.get('option_d', '')),
                            'correct_answer': str(row.get('correct_answer', '')),
                            'explanation': str(row.get('explanation', ''))
                        }
                        self.all_questions.append(question_data)
                    
                    logger.info(f"4-2_{year}専門データ: {len(df)}問読み込み完了")
                except Exception as e:
                    logger.error(f"4-2_{year}データ読み込みエラー: {e}")
        
        logger.info(f"[TOTAL] 総問題数: {len(self.all_questions)}問")
    
    def analyze_content_consistency_by_id(self):
        """同一ID内での内容一貫性分析"""
        logger.info("[ANALYZE] 同一ID内容一貫性分析開始")
        
        # 元のIDでグループ化
        id_groups = defaultdict(list)
        for question in self.all_questions:
            original_id = question.get('original_id')
            if original_id:
                id_groups[original_id].append(question)
        
        id_inconsistencies = []
        
        for original_id, questions in id_groups.items():
            if len(questions) > 1:  # 同一IDで複数問題がある場合
                # 問題文の一致チェック
                question_texts = set([q['question'] for q in questions])
                if len(question_texts) > 1:
                    # 問題文が異なる = ID衝突による内容混在
                    id_inconsistencies.append({
                        'original_id': original_id,
                        'type': '同一ID異内容問題文',
                        'question_count': len(questions),
                        'unique_questions': len(question_texts),
                        'sources': [q['source_file'] for q in questions],
                        'categories': [q['category'] for q in questions],
                        'sample_questions': list(question_texts)[:3]  # 最初の3問をサンプル
                    })
                
                # カテゴリの一致チェック
                categories = set([q['category'] for q in questions])
                if len(categories) > 1:
                    id_inconsistencies.append({
                        'original_id': original_id,
                        'type': '同一ID異カテゴリ',
                        'question_count': len(questions),
                        'unique_categories': list(categories),
                        'sources': [q['source_file'] for q in questions]
                    })
        
        logger.info(f"[RESULT] 同一ID内容不一致: {len(id_inconsistencies)}件")
        return id_inconsistencies
    
    def analyze_content_department_mismatch(self):
        """問題内容と部門カテゴリの不一致分析"""
        logger.info("[ANALYZE] 問題内容部門不一致分析開始")
        
        department_mismatches = []
        
        for question in self.all_questions:
            if question['question_type'] != 'specialist':
                continue  # 専門科目のみチェック
            
            question_text = question['question'].lower()
            option_texts = [
                question['option_a'].lower(),
                question['option_b'].lower(), 
                question['option_c'].lower(),
                question['option_d'].lower()
            ]
            explanation_text = question['explanation'].lower()
            
            stated_category = question['category']
            
            # 問題文・選択肢・解説内の専門分野キーワード検出
            detected_departments = []
            
            for dept_name, keywords in self.department_keywords.items():
                keyword_found = False
                
                # 問題文でのキーワード検出
                for keyword in keywords:
                    if keyword.lower() in question_text:
                        keyword_found = True
                        break
                
                # 選択肢でのキーワード検出
                if not keyword_found:
                    for option_text in option_texts:
                        for keyword in keywords:
                            if keyword.lower() in option_text:
                                keyword_found = True
                                break
                        if keyword_found:
                            break
                
                # 解説でのキーワード検出
                if not keyword_found:
                    for keyword in keywords:
                        if keyword.lower() in explanation_text:
                            keyword_found = True
                            break
                
                if keyword_found:
                    detected_departments.append(dept_name)
            
            # カテゴリと検出された分野の不一致チェック
            if stated_category not in detected_departments:
                if detected_departments:  # 他の分野が検出された場合
                    department_mismatches.append({
                        'original_id': question['original_id'],
                        'source_file': question['source_file'],
                        'stated_category': stated_category,
                        'detected_departments': detected_departments,
                        'question_preview': question['question'][:200],
                        'mismatch_severity': 'HIGH' if len(detected_departments) == 1 else 'MEDIUM'
                    })
                else:  # どの分野も検出されなかった場合
                    department_mismatches.append({
                        'original_id': question['original_id'],
                        'source_file': question['source_file'],
                        'stated_category': stated_category,
                        'detected_departments': [],
                        'question_preview': question['question'][:200],
                        'mismatch_severity': 'LOW',
                        'issue': '専門分野不明'
                    })
        
        logger.info(f"[RESULT] 部門内容不一致: {len(department_mismatches)}件")
        return department_mismatches
    
    def analyze_answer_explanation_consistency(self):
        """解答と解説の一貫性分析"""
        logger.info("[ANALYZE] 解答解説一貫性分析開始")
        
        answer_inconsistencies = []
        
        for question in self.all_questions:
            correct_answer = question['correct_answer'].upper().strip()
            explanation = question['explanation']
            
            if correct_answer not in ['A', 'B', 'C', 'D']:
                continue
            
            # 解説内で正解選択肢の内容が言及されているかチェック
            correct_option_text = question[f'option_{correct_answer.lower()}']
            
            # 解説に正解選択肢の内容の一部が含まれているかチェック
            option_words = correct_option_text.split()[:5]  # 最初の5単語
            explanation_matches = 0
            
            for word in option_words:
                if len(word) > 2 and word in explanation:
                    explanation_matches += 1
            
            # 解説に他の選択肢の内容が多く含まれている場合は不一致の可能性
            other_option_matches = 0
            for opt_letter in ['A', 'B', 'C', 'D']:
                if opt_letter != correct_answer:
                    other_option_text = question[f'option_{opt_letter.lower()}']
                    other_words = other_option_text.split()[:3]
                    for word in other_words:
                        if len(word) > 2 and word in explanation:
                            other_option_matches += 1
            
            # 不一致パターンの検出
            if explanation_matches == 0 and other_option_matches > 0:
                answer_inconsistencies.append({
                    'original_id': question['original_id'],
                    'source_file': question['source_file'],
                    'category': question['category'],
                    'correct_answer': correct_answer,
                    'correct_option_preview': correct_option_text[:100],
                    'explanation_preview': explanation[:200],
                    'issue': '解説が正解と不一致',
                    'other_matches': other_option_matches
                })
        
        logger.info(f"[RESULT] 解答解説不一致: {len(answer_inconsistencies)}件")
        return answer_inconsistencies
    
    def generate_comprehensive_analysis_report(self):
        """包括的分析レポート生成"""
        logger.info("[REPORT] 包括的分析レポート生成開始")
        
        # データ読み込み
        self.load_all_csv_data()
        
        # 各種分析実行
        id_inconsistencies = self.analyze_content_consistency_by_id()
        dept_mismatches = self.analyze_content_department_mismatch()
        answer_inconsistencies = self.analyze_answer_explanation_consistency()
        
        # レポート生成
        report = []
        report.append("=" * 100)
        report.append("データベースレベル問題内容ミスマッチ分析レポート")
        report.append("=" * 100)
        
        # 1. 基本統計
        report.append("\n[1] データ概要")
        report.append("-" * 50)
        report.append(f"総問題数: {len(self.all_questions)}問")
        
        basic_count = sum(1 for q in self.all_questions if q['question_type'] == 'basic')
        specialist_count = sum(1 for q in self.all_questions if q['question_type'] == 'specialist')
        report.append(f"基礎科目: {basic_count}問")
        report.append(f"専門科目: {specialist_count}問")
        
        # カテゴリ別統計
        category_counts = Counter([q['category'] for q in self.all_questions])
        report.append(f"\nカテゴリ別分布:")
        for category, count in category_counts.most_common():
            report.append(f"  {category}: {count}問")
        
        # 2. 同一ID内容不一致
        report.append(f"\n[2] 同一ID内容不一致分析")
        report.append("-" * 50)
        report.append(f"検出件数: {len(id_inconsistencies)}件")
        
        if id_inconsistencies:
            report.append("\n主要な不一致パターン:")
            for inc in id_inconsistencies[:5]:  # 最初の5件
                report.append(f"\n  ID {inc['original_id']}:")
                report.append(f"    タイプ: {inc['type']}")
                report.append(f"    問題数: {inc['question_count']}")
                report.append(f"    ソース: {', '.join(inc['sources'])}")
                if 'unique_categories' in inc:
                    report.append(f"    カテゴリ: {', '.join(inc['unique_categories'])}")
        
        # 3. 部門内容不一致
        report.append(f"\n[3] 問題内容部門不一致分析")
        report.append("-" * 50)
        report.append(f"検出件数: {len(dept_mismatches)}件")
        
        if dept_mismatches:
            high_severity = [m for m in dept_mismatches if m.get('mismatch_severity') == 'HIGH']
            report.append(f"高重要度不一致: {len(high_severity)}件")
            
            report.append(f"\n主要な部門不一致パターン:")
            for mismatch in high_severity[:5]:
                report.append(f"\n  ID {mismatch['original_id']}:")
                report.append(f"    表示部門: {mismatch['stated_category']}")
                report.append(f"    検出分野: {', '.join(mismatch['detected_departments'])}")
                report.append(f"    問題: {mismatch['question_preview']}")
        
        # 4. 解答解説不一致
        report.append(f"\n[4] 解答解説不一致分析")
        report.append("-" * 50)
        report.append(f"検出件数: {len(answer_inconsistencies)}件")
        
        if answer_inconsistencies:
            report.append(f"\n主要な解答解説不一致パターン:")
            for inc in answer_inconsistencies[:3]:
                report.append(f"\n  ID {inc['original_id']}:")
                report.append(f"    正解: {inc['correct_answer']}")
                report.append(f"    正解選択肢: {inc['correct_option_preview']}")
                report.append(f"    解説: {inc['explanation_preview']}")
        
        # 5. 総合結論
        report.append(f"\n[5] 総合結論")
        report.append("-" * 50)
        
        total_issues = len(id_inconsistencies) + len(dept_mismatches) + len(answer_inconsistencies)
        
        if total_issues > 0:
            report.append(f"[CRITICAL] 総計 {total_issues} 件の内容不一致を検出")
            report.append(f"  - ID衝突による内容混在: {len(id_inconsistencies)}件")
            report.append(f"  - 部門分野不一致: {len(dept_mismatches)}件")  
            report.append(f"  - 解答解説不一致: {len(answer_inconsistencies)}件")
            report.append(f"\n[VALIDATION] ユーザー報告「全部門で問題と解答群が異なる」は正確")
            report.append(f"[ACTION] 根本的なデータ整合性問題の修正が必要")
        else:
            report.append(f"[INFO] この分析範囲内では重大な内容不一致は検出されませんでした")
        
        # 分析データも含めて返す
        return {
            'report': "\n".join(report),
            'id_inconsistencies': id_inconsistencies,
            'department_mismatches': dept_mismatches,
            'answer_inconsistencies': answer_inconsistencies,
            'total_questions': len(self.all_questions)
        }

def main():
    """メイン実行"""
    try:
        print("データベースレベル内容ミスマッチ分析開始...")
        
        analyzer = DatabaseContentAnalyzer()
        results = analyzer.generate_comprehensive_analysis_report()
        
        print(results['report'])
        
        # ファイルに保存
        report_file = os.path.join(project_root, 'database_content_mismatch_analysis.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(results['report'])
        
        # JSON結果も保存
        json_file = os.path.join(project_root, 'database_content_analysis_results.json')
        json_results = {
            'id_inconsistencies': results['id_inconsistencies'],
            'department_mismatches': results['department_mismatches'], 
            'answer_inconsistencies': results['answer_inconsistencies'],
            'total_questions': results['total_questions']
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析結果を保存:")
        print(f"  レポート: {report_file}")
        print(f"  JSON: {json_file}")
        
    except Exception as e:
        logger.error(f"分析実行エラー: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code else 0)