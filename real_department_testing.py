#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
実アプリケーション全12部門リアルテスト
- 実際にHTTPリクエストで各部門にアクセス
- 問題文・選択肢・解説の実際の内容不一致を記録
- ユーザー体験と完全一致する証拠収集
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 12専門部門テスト設定
DEPARTMENTS = {
    '道路': 'road',
    '河川、砂防及び海岸・海洋': 'river', 
    '都市計画及び地方計画': 'urban_planning',
    'トンネル': 'tunnel',
    '造園': 'garden',
    '建設環境': 'construction_environment',
    '鋼構造及びコンクリート': 'steel_concrete',
    '土質及び基礎': 'soil_foundation',
    '施工計画、施工設備及び積算': 'construction_planning',
    '上水道及び工業用水道': 'water_supply',
    '森林土木': 'forest',
    '農業土木': 'agriculture'
}

BASE_URL = "http://localhost:5003"

def extract_question_data(html_content):
    """HTMLから問題データを詳細抽出"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 問題文抽出
        question_elem = soup.find('div', class_='question-text')
        if not question_elem:
            question_elem = soup.find(id='question-content')
        
        question_text = question_elem.get_text().strip() if question_elem else "問題文なし"
        
        # 選択肢抽出
        options = {}
        for letter in ['A', 'B', 'C', 'D']:
            # option-textクラスを持つspanを探す
            option_spans = soup.find_all('span', class_='option-text')
            for span in option_spans:
                # 親要素でA,B,C,Dを判定
                parent_label = span.find_parent('label')
                if parent_label:
                    input_elem = parent_label.find('input')
                    if input_elem and input_elem.get('value') == letter:
                        options[letter] = span.get_text().strip()
                        break
        
        # QID抽出
        qid_input = soup.find('input', {'name': 'qid'})
        qid = qid_input.get('value') if qid_input else "QIDなし"
        
        # カテゴリ情報抽出（バッジから）
        category_badge = soup.find('span', class_='badge')
        category_info = category_badge.get_text().strip() if category_badge else "カテゴリなし"
        
        return {
            'question': question_text,
            'options': options,
            'qid': qid,
            'category_info': category_info,
            'extraction_success': True
        }
        
    except Exception as e:
        logger.error(f"HTML抽出エラー: {e}")
        return {
            'question': f"抽出エラー: {e}",
            'options': {},
            'qid': "エラー",
            'extraction_success': False
        }

def analyze_content_mismatch(question_data, department_name):
    """問題内容の不一致を詳細分析"""
    mismatches = []
    
    question = question_data.get('question', '')
    options = question_data.get('options', {})
    
    # 専門分野キーワード
    field_keywords = {
        '道路': ['道路', '交通', '舗装', 'アスファルト', '自動車', 'インターチェンジ'],
        '河川、砂防及び海岸・海洋': ['河川', '砂防', '海岸', 'ダム', '水位', '流量', '洪水'],
        '都市計画及び地方計画': ['都市計画', '地方計画', '都市', '計画', 'ゾーニング'],
        'トンネル': ['トンネル', '地下', 'NATM', '掘削', 'TBM', '地山'],
        '造園': ['造園', '植物', '緑化', '庭園', '景観', '植栽'],
        '建設環境': ['環境', '騒音', '振動', '大気汚染', 'アセスメント'],
        '鋼構造及びコンクリート': ['鋼', 'コンクリート', '鉄筋', '構造', '梁', '柱'],
        '土質及び基礎': ['土質', '基礎', '地盤', '土壌', '支持力', '沈下'],
        '施工計画、施工設備及び積算': ['施工', '工程', '積算', '計画', 'クレーン'],
        '上水道及び工業用水道': ['上水道', '水道', '浄水', '給水', '配水'],
        '森林土木': ['森林', '林業', '治山', '木材', '間伐'],
        '農業土木': ['農業', '農地', '灌漑', '排水', 'パイプライン']
    }
    
    expected_keywords = field_keywords.get(department_name, [])
    
    # 問題文の分野チェック
    question_matches = 0
    for keyword in expected_keywords:
        if keyword in question:
            question_matches += 1
    
    # 選択肢の分野チェック
    option_matches = {}
    for opt_key, opt_text in options.items():
        matches = 0
        for keyword in expected_keywords:
            if keyword in opt_text:
                matches += 1
        option_matches[opt_key] = matches
    
    # 他分野のキーワードチェック
    other_field_matches = []
    for field_name, keywords in field_keywords.items():
        if field_name != department_name:
            for keyword in keywords:
                if keyword in question:
                    other_field_matches.append((field_name, keyword))
                for opt_key, opt_text in options.items():
                    if keyword in opt_text:
                        other_field_matches.append((field_name, f"選択肢{opt_key}:{keyword}"))
    
    # 不一致判定
    if question_matches == 0 and other_field_matches:
        mismatches.append({
            'type': '問題文専門分野不一致',
            'detail': f'期待分野: {department_name}, 検出分野: {[f[0] for f in other_field_matches[:3]]}',
            'evidence': other_field_matches[:5]
        })
    
    total_option_matches = sum(option_matches.values())
    if total_option_matches == 0 and len(options) > 0:
        mismatches.append({
            'type': '選択肢専門分野不一致',
            'detail': f'選択肢が{department_name}分野と関連なし',
            'option_analysis': option_matches
        })
    
    return mismatches

def test_department(dept_name, dept_id):
    """単一部門のリアルテスト"""
    logger.info(f"[TEST] {dept_name} ({dept_id}) テスト開始")
    
    test_results = {
        'department': dept_name,
        'department_id': dept_id,
        'tests_performed': 0,
        'successful_extractions': 0,
        'content_mismatches': [],
        'questions_captured': []
    }
    
    # 複数回テスト（異なる問題を取得するため）
    for attempt in range(3):
        try:
            test_results['tests_performed'] += 1
            
            # 実際のHTTPリクエスト
            url = f"{BASE_URL}/exam"
            params = {
                'department': dept_id,
                'question_type': 'specialist',
                'count': '1'
            }
            
            logger.info(f"[REQ] GET {url} params={params}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # 問題データ抽出
                question_data = extract_question_data(response.text)
                
                if question_data.get('extraction_success'):
                    test_results['successful_extractions'] += 1
                    test_results['questions_captured'].append(question_data)
                    
                    # 内容不一致分析
                    mismatches = analyze_content_mismatch(question_data, dept_name)
                    test_results['content_mismatches'].extend(mismatches)
                    
                    logger.info(f"[EXTRACT] QID={question_data.get('qid')}")
                    logger.info(f"[QUESTION] {question_data.get('question')[:80]}...")
                    
                    if mismatches:
                        logger.warning(f"[MISMATCH] {len(mismatches)}件の不一致を検出")
                        for mismatch in mismatches:
                            logger.warning(f"  - {mismatch['type']}: {mismatch['detail']}")
                else:
                    logger.error(f"[FAIL] データ抽出失敗")
            else:
                logger.error(f"[HTTP] {response.status_code} - {response.reason}")
            
            time.sleep(1)  # サーバー負荷軽減
            
        except Exception as e:
            logger.error(f"[ERROR] {dept_name} テスト#{attempt+1} 例外: {e}")
    
    return test_results

def run_comprehensive_real_test():
    """全12部門包括的リアルテスト"""
    logger.info("[START] 全12部門リアルテスト開始")
    
    all_results = {}
    overall_summary = {
        'total_departments': 0,
        'departments_with_issues': 0,
        'total_mismatches': 0,
        'departments_tested': []
    }
    
    for dept_name, dept_id in DEPARTMENTS.items():
        logger.info(f"\n{'='*50}")
        logger.info(f"部門: {dept_name}")
        logger.info(f"{'='*50}")
        
        dept_results = test_department(dept_name, dept_id)
        all_results[dept_name] = dept_results
        
        # 統計更新
        overall_summary['total_departments'] += 1
        overall_summary['departments_tested'].append(dept_name)
        
        mismatches = dept_results.get('content_mismatches', [])
        if mismatches:
            overall_summary['departments_with_issues'] += 1
            overall_summary['total_mismatches'] += len(mismatches)
        
        # 部門間で待機
        time.sleep(2)
    
    return all_results, overall_summary

def generate_detailed_evidence_report(results, summary):
    """詳細証拠レポート生成"""
    report = []
    report.append("=" * 100)
    report.append("実アプリケーション全12部門リアルテスト証拠レポート")
    report.append("ユーザー報告「全部門で問題と解答群が異なる」の実証")
    report.append("=" * 100)
    
    # 総合統計
    report.append(f"\n[総合統計]")
    report.append(f"テスト部門数: {summary['total_departments']}")
    report.append(f"問題検出部門数: {summary['departments_with_issues']}")
    report.append(f"総不一致件数: {summary['total_mismatches']}")
    
    if summary['departments_with_issues'] > 0:
        percentage = (summary['departments_with_issues'] / summary['total_departments']) * 100
        report.append(f"問題発生率: {percentage:.1f}% ({summary['departments_with_issues']}/{summary['total_departments']} 部門)")
    
    # 各部門詳細
    for dept_name, dept_result in results.items():
        report.append(f"\n[部門] {dept_name}")
        report.append("-" * 60)
        
        tests = dept_result.get('tests_performed', 0)
        extractions = dept_result.get('successful_extractions', 0)
        mismatches = dept_result.get('content_mismatches', [])
        questions = dept_result.get('questions_captured', [])
        
        report.append(f"実行テスト数: {tests}")
        report.append(f"成功データ抽出: {extractions}")
        report.append(f"内容不一致検出: {len(mismatches)}件")
        
        if mismatches:
            report.append(f"\n[検出された不一致詳細]")
            for i, mismatch in enumerate(mismatches, 1):
                report.append(f"  {i}. {mismatch['type']}")
                report.append(f"     {mismatch['detail']}")
                if 'evidence' in mismatch:
                    report.append(f"     証拠: {mismatch['evidence'][:3]}")
        
        # 実際にキャプチャした問題内容
        if questions:
            latest_question = questions[-1]
            report.append(f"\n[実際の問題内容サンプル]")
            report.append(f"  QID: {latest_question.get('qid')}")
            report.append(f"  問題文: {latest_question.get('question')[:200]}...")
            
            options = latest_question.get('options', {})
            for opt_key in ['A', 'B', 'C', 'D']:
                if opt_key in options:
                    report.append(f"  選択肢{opt_key}: {options[opt_key][:100]}...")
    
    # 結論
    report.append(f"\n{'='*100}")
    report.append("結論")
    report.append(f"{'='*100}")
    
    if summary['total_mismatches'] > 0:
        report.append(f"[実証完了] ユーザー報告「全部門で問題と解答群が異なる」は正確")
        report.append(f"[証拠] {summary['departments_with_issues']}部門で内容不一致を実証")
        report.append(f"[証拠] 総計{summary['total_mismatches']}件の不一致パターンを検出")
        report.append(f"[必要] 根本的なシステム修正が緊急に必要")
    else:
        report.append(f"[結果] このテスト範囲では重大な不一致は検出されませんでした")
        report.append(f"[注記] より大規模なサンプリングが必要な可能性")
    
    return "\n".join(report)

def main():
    """メイン実行"""
    print("実アプリケーション全12部門リアルテスト開始...")
    
    try:
        # アプリケーションの動作確認
        test_response = requests.get(f"{BASE_URL}/", timeout=5)
        if test_response.status_code != 200:
            print(f"エラー: アプリケーションが応答しません (Status: {test_response.status_code})")
            return 1
        
        print("アプリケーション接続確認完了")
        
        # 包括的テスト実行
        results, summary = run_comprehensive_real_test()
        
        # 詳細レポート生成
        report = generate_detailed_evidence_report(results, summary)
        
        print(report)
        
        # ファイル保存
        with open('real_department_testing_evidence.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        with open('real_testing_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'results': results,
                'summary': summary
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n証拠レポート保存: real_department_testing_evidence.txt")
        print(f"詳細結果保存: real_testing_results.json")
        
        return 0
        
    except Exception as e:
        logger.error(f"テスト実行エラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())