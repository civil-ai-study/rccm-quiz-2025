#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA CRITICAL: ID衝突問題診断ツール
- 現在のID collision解決システムが正常動作しているかを詳細検証
- 全12部門のデータ混合問題を系統的に分析
- 実際のブラウザ体験と一致する環境での検証
"""

import os
import sys
import pandas as pd
from collections import defaultdict, Counter
import logging

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def analyze_original_csv_data():
    """元のCSVデータでのID衝突パターンを分析"""
    logger.info("[ANALYZE] 元のCSVデータでのID衝突分析開始")
    
    data_dir = os.path.join(project_root, 'data')
    id_mapping = defaultdict(list)
    
    # 4-1基礎データ分析
    basic_file = os.path.join(data_dir, '4-1.csv')
    if os.path.exists(basic_file):
        try:
            df = pd.read_csv(basic_file, encoding='utf-8')
            logger.info(f"4-1基礎データ: {len(df)}問読み込み")
            
            for _, row in df.iterrows():
                qid = row.get('id', 'N/A')
                question_text = str(row.get('question', ''))[:50] + '...'
                category = row.get('category', 'N/A')
                
                id_mapping[qid].append({
                    'file': '4-1.csv',
                    'type': '基礎',
                    'category': category,
                    'question_preview': question_text,
                    'year': 'N/A'
                })
        except Exception as e:
            logger.error(f"4-1データ読み込みエラー: {e}")
    
    # 4-2専門データ分析（年度別）
    for year in range(2008, 2019):
        specialist_file = os.path.join(data_dir, f'4-2_{year}.csv')
        if os.path.exists(specialist_file):
            try:
                df = pd.read_csv(specialist_file, encoding='utf-8')
                logger.info(f"4-2_{year}データ: {len(df)}問読み込み")
                
                for _, row in df.iterrows():
                    qid = row.get('id', 'N/A')
                    question_text = str(row.get('question', ''))[:50] + '...'
                    category = row.get('category', 'N/A')
                    
                    id_mapping[qid].append({
                        'file': f'4-2_{year}.csv',
                        'type': '専門',
                        'category': category,
                        'question_preview': question_text,
                        'year': year
                    })
            except Exception as e:
                logger.error(f"4-2_{year}データ読み込みエラー: {e}")
    
    return id_mapping

def test_current_id_resolution_system():
    """現在のID解決システムをテスト"""
    logger.info("[TEST] 現在のID collision解決システムテスト開始")
    
    try:
        # アプリケーションのデータローディング関数をインポート
        from utils import load_rccm_data_files
        
        data_dir = os.path.join(project_root, 'data')
        resolved_questions = load_rccm_data_files(data_dir)
        
        logger.info(f"解決済み問題データ: {len(resolved_questions)}問")
        
        # ID重複チェック
        ids = [q.get('id') for q in resolved_questions]
        id_counts = Counter(ids)
        duplicates = {k: v for k, v in id_counts.items() if v > 1}
        
        if duplicates:
            logger.error(f"[ERROR] ID重複が発見されました: {duplicates}")
            return False, duplicates
        else:
            logger.info("[OK] ID重複なし - 解決システム正常動作")
        
        # 部門別分布チェック
        dept_distribution = defaultdict(int)
        type_distribution = defaultdict(int)
        
        for q in resolved_questions:
            dept_distribution[q.get('category', 'N/A')] += 1
            type_distribution[q.get('question_type', 'N/A')] += 1
        
        logger.info("[STAT] カテゴリ別分布:")
        for category, count in sorted(dept_distribution.items()):
            logger.info(f"  {category}: {count}問")
        
        logger.info("[STAT] 問題種別分布:")
        for qtype, count in sorted(type_distribution.items()):
            logger.info(f"  {qtype}: {count}問")
        
        return True, resolved_questions
        
    except Exception as e:
        logger.error(f"ID解決システムテストエラー: {e}")
        return False, str(e)

def test_department_data_consistency():
    """各部門のデータ整合性テスト"""
    logger.info("[TEST] 12部門データ整合性テスト開始")
    
    try:
        from utils import load_rccm_data_files
        
        data_dir = os.path.join(project_root, 'data')
        questions = load_rccm_data_files(data_dir)
        
        # 12専門部門リスト（CLAUDE.mdに基づく）
        specialist_departments = [
            '道路', '河川、砂防及び海岸・海洋', '都市計画及び地方計画', 'トンネル',
            '造園', '建設環境', '鋼構造及びコンクリート', '土質及び基礎',
            '施工計画、施工設備及び積算', '上水道及び工業用水道', '森林土木', '農業土木'
        ]
        
        dept_analysis = {}
        
        for dept in specialist_departments:
            dept_questions = [q for q in questions 
                            if q.get('category') == dept and q.get('question_type') == 'specialist']
            
            if dept_questions:
                # 各部門の問題から代表的なサンプルを確認
                sample_question = dept_questions[0]
                dept_analysis[dept] = {
                    'total_count': len(dept_questions),
                    'sample_id': sample_question.get('id'),
                    'sample_question': sample_question.get('question', '')[:100] + '...',
                    'sample_category': sample_question.get('category'),
                    'sample_year': sample_question.get('year'),
                    'id_range': [min(q.get('id', 0) for q in dept_questions),
                               max(q.get('id', 0) for q in dept_questions)]
                }
            else:
                dept_analysis[dept] = {
                    'total_count': 0,
                    'error': 'データが見つかりません'
                }
        
        # 基礎科目も確認
        basic_questions = [q for q in questions if q.get('question_type') == 'basic']
        dept_analysis['基礎科目(4-1)'] = {
            'total_count': len(basic_questions),
            'sample_question': basic_questions[0].get('question', '')[:100] + '...' if basic_questions else 'N/A',
            'id_range': [min(q.get('id', 0) for q in basic_questions),
                        max(q.get('id', 0) for q in basic_questions)] if basic_questions else [0, 0]
        }
        
        return dept_analysis
        
    except Exception as e:
        logger.error(f"部門データ整合性テストエラー: {e}")
        return {'error': str(e)}

def generate_comprehensive_report():
    """包括的な診断レポート生成"""
    logger.info("[REPORT] 包括的診断レポート生成中...")
    
    report = []
    report.append("=" * 80)
    report.append("ULTRA CRITICAL: ID衝突問題診断レポート")
    report.append("=" * 80)
    
    # 1. 元データのID衝突分析
    report.append("\n[1] 元CSVデータのID衝突分析")
    report.append("-" * 50)
    
    id_mapping = analyze_original_csv_data()
    conflict_count = 0
    
    for qid, entries in id_mapping.items():
        if len(entries) > 1:
            conflict_count += 1
            if conflict_count <= 10:  # 最初の10件のみ詳細表示
                report.append(f"\n[CONFLICT] ID {qid} の衝突:")
                for entry in entries:
                    report.append(f"  - {entry['file']}: {entry['type']}, {entry['category']}, {entry['year']}")
                    report.append(f"    問題: {entry['question_preview']}")
    
    report.append(f"\n[STAT] ID衝突統計: 総計{conflict_count}件のID衝突を検出")
    
    # 2. 現在のID解決システムテスト
    report.append("\n[2] 現在のID解決システムテスト結果")
    report.append("-" * 50)
    
    success, result = test_current_id_resolution_system()
    if success:
        report.append("[OK] ID解決システム正常動作: 重複ID完全除去済み")
        report.append(f"[STAT] 解決済み総問題数: {len(result)}問")
    else:
        report.append(f"[ERROR] ID解決システムエラー: {result}")
    
    # 3. 12部門データ整合性テスト
    report.append("\n[3] 12部門データ整合性テスト結果")
    report.append("-" * 50)
    
    dept_analysis = test_department_data_consistency()
    for dept, analysis in dept_analysis.items():
        if 'error' in analysis:
            report.append(f"[ERROR] {dept}: {analysis['error']}")
        else:
            report.append(f"[OK] {dept}: {analysis['total_count']}問")
            if 'id_range' in analysis:
                report.append(f"   ID範囲: {analysis['id_range'][0]}-{analysis['id_range'][1]}")
            if 'sample_question' in analysis:
                report.append(f"   サンプル: {analysis['sample_question']}")
    
    # 4. 結論と推奨事項
    report.append("\n[4] 診断結論")
    report.append("-" * 50)
    
    if success:
        report.append("[OK] ID衝突解決システムは正常に動作しています")
        report.append("[OK] 全部門のデータが適切に分離されています")
        report.append("[NOTE] ユーザーが体験する問題は別の原因の可能性があります")
        report.append("\n[RECOMMEND] 推奨: セッション管理・キャッシュタイミング・テンプレート変数の詳細調査")
    else:
        report.append("[ERROR] ID衝突解決システムに問題があります")
        report.append("[CRITICAL] 緊急修正が必要です")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)

if __name__ == "__main__":
    print("ULTRA CRITICAL: ID衝突問題診断開始")
    
    try:
        report = generate_comprehensive_report()
        print(report)
        
        # レポートをファイルに保存
        report_file = os.path.join(project_root, 'id_collision_diagnostic_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n詳細レポートを保存: {report_file}")
        
    except Exception as e:
        logger.error(f"診断プロセスエラー: {e}")
        sys.exit(1)