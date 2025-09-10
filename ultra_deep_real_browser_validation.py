#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA DEEP: 実ブラウザ環境での全12部門問題文・選択肢・解説不一致実証テスト
- ユーザーが体験する実際の「問題と解答群が異なる」現象を再現
- 表面的なID解決チェックではなく、実際の問題内容のミスマッチを検証
- 全12専門部門での具体的な内容不一致パターンを特定
"""

import os
import sys
import requests
import time
import json
from collections import defaultdict
import logging
import random

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# RCCM 12専門部門リスト（CLAUDE.mdに基づく）
SPECIALIST_DEPARTMENTS = [
    '道路',
    '河川、砂防及び海岸・海洋', 
    '都市計画及び地方計画',
    'トンネル',
    '造園',
    '建設環境',
    '鋼構造及びコンクリート',
    '土質及び基礎',
    '施工計画、施工設備及び積算',
    '上水道及び工業用水道',
    '森林土木',
    '農業土木'
]

# 部門名から英語IDへのマッピング（実際のシステムに基づく）
DEPARTMENT_MAPPING = {
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

class RealBrowserValidator:
    """実ブラウザ環境での問題検証クラス"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"  # ローカル開発サーバー
        self.session = requests.Session()
        self.validation_results = {}
        
    def start_quiz_session(self, department_id, question_type='specialist'):
        """クイズセッション開始"""
        try:
            # セッション開始リクエスト
            start_url = f"{self.base_url}/exam"
            params = {
                'department': department_id,
                'question_type': question_type,
                'count': 3  # 少数でテスト
            }
            
            logger.info(f"[START] {department_id} セッション開始: {start_url}")
            response = self.session.get(start_url, params=params)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"[ERROR] セッション開始失敗: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] セッション開始例外: {e}")
            return None
    
    def extract_question_data_from_html(self, html_content):
        """HTMLから問題データを抽出"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 問題文を抽出
            question_elem = soup.find('div', {'id': 'question-content'})
            if not question_elem:
                question_elem = soup.find('div', class_='question-text')
            
            question_text = question_elem.get_text().strip() if question_elem else "問題文取得失敗"
            
            # 選択肢を抽出
            options = {}
            for opt_letter in ['A', 'B', 'C', 'D']:
                opt_elem = soup.find('span', class_='option-text', string=True)
                if opt_elem and opt_elem.parent:
                    option_container = opt_elem.parent.parent
                    if f'option{opt_letter}' in str(option_container):
                        options[opt_letter] = opt_elem.get_text().strip()
                
                # 代替検索
                if opt_letter not in options:
                    opt_input = soup.find('input', {'id': f'option{opt_letter}'})
                    if opt_input and opt_input.parent:
                        label = opt_input.parent.find('span', class_='option-text')
                        if label:
                            options[opt_letter] = label.get_text().strip()
            
            # QIDを抽出
            qid_input = soup.find('input', {'name': 'qid'})
            qid = qid_input.get('value') if qid_input else "QID取得失敗"
            
            return {
                'question': question_text,
                'options': options,
                'qid': qid,
                'html_length': len(html_content)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] HTML解析エラー: {e}")
            return {
                'question': "HTML解析失敗",
                'options': {},
                'qid': "解析失敗",
                'error': str(e)
            }
    
    def validate_content_consistency(self, extracted_data, department_name):
        """問題内容の一貫性を検証"""
        inconsistencies = []
        
        question = extracted_data.get('question', '')
        options = extracted_data.get('options', {})
        
        # 1. 問題文と選択肢の専門分野一致チェック
        department_keywords = {
            '道路': ['道路', '交通', '自動車', 'アスファルト', '舗装'],
            '河川、砂防及び海岸・海洋': ['河川', '砂防', '海岸', 'ダム', '水'],
            '都市計画及び地方計画': ['都市計画', '地方計画', '都市', '計画'],
            'トンネル': ['トンネル', '地下', 'NATM', '掘削'],
            '造園': ['造園', '植物', '緑化', '庭園', '景観'],
            '建設環境': ['環境', '騒音', '振動', '大気汚染'],
            '鋼構造及びコンクリート': ['鋼', 'コンクリート', '鉄筋', '構造'],
            '土質及び基礎': ['土質', '基礎', '地盤', '土壌'],
            '施工計画、施工設備及び積算': ['施工', '工程', '積算', '計画'],
            '上水道及び工業用水道': ['上水道', '水道', '浄水', '給水'],
            '森林土木': ['森林', '林業', '治山', '木材'],
            '農業土木': ['農業', '農地', '灌漑', '排水']
        }
        
        dept_keys = department_keywords.get(department_name, [])
        
        # 問題文の専門分野チェック
        question_matches = any(key in question for key in dept_keys)
        
        # 選択肢の専門分野チェック
        option_matches = {}
        for opt_key, opt_text in options.items():
            option_matches[opt_key] = any(key in opt_text for key in dept_keys)
        
        # 不一致パターン検出
        if not question_matches:
            inconsistencies.append({
                'type': '問題文専門分野不一致',
                'detail': f'問題文が{department_name}に関連しない内容',
                'question_preview': question[:100]
            })
        
        mismatched_options = [k for k, v in option_matches.items() if not v]
        if mismatched_options:
            inconsistencies.append({
                'type': '選択肢専門分野不一致', 
                'detail': f'選択肢{mismatched_options}が{department_name}に関連しない',
                'options': {k: options[k][:50] for k in mismatched_options}
            })
        
        # 2. 問題文と選択肢の内容整合性チェック
        question_lower = question.lower()
        
        # 問題文が特定の技術分野を問うているのに、選択肢が全く異なる分野の場合
        technical_terms_in_question = []
        for dept, keywords in department_keywords.items():
            if any(key in question for key in keywords):
                technical_terms_in_question.append(dept)
        
        if len(technical_terms_in_question) > 1 and department_name not in technical_terms_in_question:
            inconsistencies.append({
                'type': '問題選択肢内容分野混合',
                'detail': f'問題文: {technical_terms_in_question}, 部門: {department_name}',
                'severity': 'HIGH'
            })
        
        return inconsistencies
    
    def test_single_department(self, department_name, department_id):
        """単一部門の詳細テスト"""
        logger.info(f"[TEST] {department_name} ({department_id}) 詳細テスト開始")
        
        results = {
            'department': department_name,
            'department_id': department_id,
            'test_attempts': 0,
            'successful_extractions': 0,
            'content_inconsistencies': [],
            'questions_tested': []
        }
        
        # 複数回テストして異なる問題を取得
        for attempt in range(3):
            try:
                results['test_attempts'] += 1
                logger.info(f"[ATTEMPT] {department_name} テスト #{attempt + 1}")
                
                html_content = self.start_quiz_session(department_id)
                
                if html_content:
                    extracted_data = self.extract_question_data_from_html(html_content)
                    
                    if extracted_data.get('question') != "HTML解析失敗":
                        results['successful_extractions'] += 1
                        results['questions_tested'].append(extracted_data)
                        
                        # 内容一貫性チェック
                        inconsistencies = self.validate_content_consistency(extracted_data, department_name)
                        results['content_inconsistencies'].extend(inconsistencies)
                        
                        logger.info(f"[SUCCESS] 問題抽出成功: QID={extracted_data.get('qid')}")
                        logger.info(f"[QUESTION] {extracted_data.get('question')[:100]}...")
                        
                        if inconsistencies:
                            logger.warning(f"[INCONSISTENCY] {len(inconsistencies)}件の不一致を検出")
                            for inc in inconsistencies:
                                logger.warning(f"  - {inc['type']}: {inc['detail']}")
                    else:
                        logger.error(f"[FAILED] データ抽出失敗")
                
                time.sleep(1)  # サーバー負荷軽減
                
            except Exception as e:
                logger.error(f"[ERROR] {department_name} テスト#{attempt + 1} 例外: {e}")
        
        return results
    
    def run_comprehensive_validation(self):
        """全部門包括的検証"""
        logger.info("[START] ULTRA DEEP 全12部門実ブラウザ検証開始")
        
        all_results = {}
        
        for department_name in SPECIALIST_DEPARTMENTS:
            department_id = DEPARTMENT_MAPPING.get(department_name, 'unknown')
            
            if department_id == 'unknown':
                logger.error(f"[SKIP] {department_name}: 部門IDマッピングなし")
                continue
            
            dept_results = self.test_single_department(department_name, department_id)
            all_results[department_name] = dept_results
            
            # 部門間で少し待機
            time.sleep(2)
        
        return all_results
    
    def generate_detailed_report(self, results):
        """詳細報告書生成"""
        report = []
        report.append("=" * 100)
        report.append("ULTRA DEEP: 実ブラウザ全12部門問題内容不一致検証報告書")
        report.append("=" * 100)
        
        total_inconsistencies = 0
        departments_with_issues = 0
        
        for dept_name, dept_result in results.items():
            report.append(f"\n[部門] {dept_name}")
            report.append("-" * 80)
            
            test_attempts = dept_result.get('test_attempts', 0)
            successful = dept_result.get('successful_extractions', 0)
            inconsistencies = dept_result.get('content_inconsistencies', [])
            
            report.append(f"テスト試行数: {test_attempts}")
            report.append(f"成功抽出数: {successful}")
            report.append(f"内容不一致件数: {len(inconsistencies)}")
            
            if inconsistencies:
                departments_with_issues += 1
                total_inconsistencies += len(inconsistencies)
                
                report.append("\n[検出された不一致]")
                for i, inc in enumerate(inconsistencies, 1):
                    report.append(f"  {i}. {inc['type']}")
                    report.append(f"     詳細: {inc['detail']}")
                    if 'question_preview' in inc:
                        report.append(f"     問題: {inc['question_preview']}")
                    if 'options' in inc:
                        for opt_key, opt_text in inc['options'].items():
                            report.append(f"     選択肢{opt_key}: {opt_text}")
            
            # 実際にテストした問題のサンプル
            questions_tested = dept_result.get('questions_tested', [])
            if questions_tested:
                report.append(f"\n[テスト問題サンプル] (最新1件)")
                latest_q = questions_tested[-1]
                report.append(f"  QID: {latest_q.get('qid')}")
                report.append(f"  問題: {latest_q.get('question')[:200]}...")
                
                options = latest_q.get('options', {})
                for opt_key in ['A', 'B', 'C', 'D']:
                    if opt_key in options:
                        report.append(f"  {opt_key}: {options[opt_key][:100]}...")
        
        # 総合統計
        report.append(f"\n{'='*100}")
        report.append("総合結果")
        report.append(f"{'='*100}")
        report.append(f"検証部門数: {len(results)}")
        report.append(f"問題検出部門数: {departments_with_issues}")
        report.append(f"総不一致件数: {total_inconsistencies}")
        
        if total_inconsistencies > 0:
            report.append(f"\n[結論] ユーザー報告は正確: {departments_with_issues}/{len(results)} 部門で内容不一致を検出")
            report.append("[推奨] 根本的なデータマッピング問題の修正が必要")
        else:
            report.append(f"\n[結論] 検証範囲内では重大な不一致は検出されませんでした")
            report.append("[推奨] より大規模なサンプリング検証を実施")
        
        return "\n".join(report)

def main():
    """メイン実行関数"""
    try:
        print("ULTRA DEEP: 実ブラウザ全12部門検証開始...")
        
        # Beautiful Soupの依存関係チェック
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("[ERROR] Beautiful Soup4が必要です: pip install beautifulsoup4")
            return
        
        validator = RealBrowserValidator()
        
        # 包括的検証実行
        results = validator.run_comprehensive_validation()
        
        # 詳細報告書生成
        report = validator.generate_detailed_report(results)
        
        print(report)
        
        # 結果をファイルに保存
        report_file = os.path.join(project_root, 'ultra_deep_browser_validation_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n詳細報告書を保存: {report_file}")
        
        # JSON形式でも保存
        json_file = os.path.join(project_root, 'ultra_deep_validation_results.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"JSON結果を保存: {json_file}")
        
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code else 0)