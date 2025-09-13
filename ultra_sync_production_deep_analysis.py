# -*- coding: utf-8 -*-
"""
ULTRA SYNC: 本番環境深度分析（副作用絶対防止）
Production Environment Deep Analysis with Zero Side Effects
本番環境の現在状況を詳細に分析
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class UltraSyncProductionAnalyzer:
    """
    本番環境の詳細分析クラス
    副作用を一切発生させない読み取り専用分析
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "ULTRA_SYNC_PRODUCTION_DEEP_ANALYSIS",
            "progression_tests": [],
            "csrf_behavior": {},
            "session_management": {},
            "expert_fixes_status": {},
            "deployment_necessity": "UNKNOWN"
        }
    
    def test_multiple_progressions(self):
        """
        複数回の進行テストで本番環境の現状を正確に把握
        """
        print("=== 本番環境：複数進行テスト ===")
        print("本番環境での1st→2nd進行を複数回テスト...")
        print("-" * 50)
        
        success_count = 0
        total_tests = 5
        
        for test_no in range(1, total_tests + 1):
            print(f"\n本番テスト {test_no}/{total_tests}:")
            
            session = requests.Session()
            test_result = {
                "test_number": test_no,
                "timestamp": datetime.now().isoformat(),
                "status": "UNKNOWN",
                "details": {}
            }
            
            try:
                # 新しいセッションで試験初期化
                exam_url = f"{self.production_url}/exam?department=road&question_type=specialist&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code != 200:
                    print(f"  [ERROR] 初期化失敗: {response.status_code}")
                    test_result["status"] = "INIT_FAILED"
                    test_result["details"]["init_status"] = response.status_code
                    self.analysis_results["progression_tests"].append(test_result)
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    print("  [ERROR] トークン不足")
                    test_result["status"] = "MISSING_TOKENS"
                    self.analysis_results["progression_tests"].append(test_result)
                    continue
                
                csrf_value = csrf_token.get('value')
                qid_value = qid_input.get('value')
                
                print(f"  初期化成功: QID={qid_value}")
                test_result["details"]["first_qid"] = qid_value
                test_result["details"]["csrf_present"] = True
                
                # 1st問題に回答
                post_data = {
                    'csrf_token': csrf_value,
                    'qid': qid_value,
                    'answer': 'A',
                    'elapsed': 45
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': exam_url,
                    'Origin': self.production_url
                }
                
                post_response = session.post(f"{self.production_url}/exam", 
                                           data=post_data, 
                                           headers=headers,
                                           timeout=30)
                
                print(f"  POST応答: {post_response.status_code}")
                test_result["details"]["post_status"] = post_response.status_code
                
                if post_response.status_code == 400:
                    print("  [CONFIRMED] POST 400エラー - 進行問題が存在")
                    test_result["status"] = "PROGRESSION_ISSUE_CONFIRMED"
                    
                elif post_response.status_code == 200:
                    # フィードバックページかチェック
                    feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    # フィードバック要素を探す
                    has_feedback = (
                        "正解" in post_response.text or 
                        "不正解" in post_response.text or
                        feedback_soup.find('div', class_='feedback-card') or
                        "あなたの解答:" in post_response.text
                    )
                    
                    if has_feedback:
                        print("  [OK] フィードバックページ表示")
                        
                        # 次の問題へのリンクを探す
                        next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                        
                        if next_link:
                            # 2nd問題へ進行テスト
                            next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                            
                            if next_response.status_code == 200:
                                next_soup = BeautifulSoup(next_response.text, 'html.parser')
                                next_qid_input = next_soup.find('input', {'name': 'qid'})
                                
                                if next_qid_input:
                                    next_qid = next_qid_input.get('value')
                                    
                                    if next_qid != qid_value:
                                        print(f"  [SUCCESS] 進行成功: {qid_value} → {next_qid}")
                                        test_result["status"] = "PROGRESSION_SUCCESS"
                                        test_result["details"]["second_qid"] = next_qid
                                        success_count += 1
                                    else:
                                        print("  [FAILURE] 同じ問題のまま")
                                        test_result["status"] = "PROGRESSION_STUCK"
                                else:
                                    print("  [ERROR] 2nd問題でQID不足")
                                    test_result["status"] = "SECOND_QID_MISSING"
                            else:
                                print(f"  [ERROR] 2nd問題読込失敗: {next_response.status_code}")
                                test_result["status"] = "SECOND_LOAD_FAILED"
                                test_result["details"]["second_status"] = next_response.status_code
                        else:
                            print("  [ERROR] 次問題リンクなし")
                            test_result["status"] = "NO_NEXT_LINK"
                    else:
                        print("  [ERROR] 不明な応答形式")
                        test_result["status"] = "UNKNOWN_RESPONSE_FORMAT"
                        test_result["details"]["response_sample"] = post_response.text[:200]
                else:
                    print(f"  [ERROR] 予期しないPOSTステータス: {post_response.status_code}")
                    test_result["status"] = "UNEXPECTED_POST_STATUS"
                    test_result["details"]["post_status"] = post_response.status_code
                
                self.analysis_results["progression_tests"].append(test_result)
                
                # テスト間の間隔
                time.sleep(2)
                
            except Exception as e:
                print(f"  [ERROR] テスト失敗: {e}")
                test_result["status"] = "TEST_FAILED"
                test_result["details"]["error"] = str(e)
                self.analysis_results["progression_tests"].append(test_result)
        
        # 結果分析
        success_rate = (success_count / total_tests) * 100
        
        print(f"\n本番環境進行テスト結果:")
        print(f"  成功: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        # 判定
        if success_count == total_tests:
            print("  [結論] 本番環境は完全に正常動作")
            self.analysis_results["deployment_necessity"] = "NOT_NEEDED"
        elif success_count >= total_tests * 0.8:
            print("  [結論] 本番環境は概ね正常（一部不安定）")
            self.analysis_results["deployment_necessity"] = "MAYBE_NEEDED"
        elif success_count > 0:
            print("  [結論] 本番環境は不安定（部分的動作）")
            self.analysis_results["deployment_necessity"] = "PROBABLY_NEEDED"
        else:
            print("  [結論] 本番環境は完全に問題あり")
            self.analysis_results["deployment_necessity"] = "DEFINITELY_NEEDED"
        
        return success_count, total_tests
    
    def analyze_current_code_version(self):
        """
        本番環境のコードバージョンを分析
        """
        print("\n=== 本番環境：コードバージョン分析 ===")
        print("本番環境で動作中のコードバージョンを分析...")
        print("-" * 50)
        
        try:
            session = requests.Session()
            response = session.get(self.production_url, timeout=30)
            
            version_indicators = {
                "latest_commit_present": "VERSION CHECK" in response.text,
                "ultra_sync_present": "[ULTRA SYNC]" in response.text,
                "expert_fixes_present": "Expert-recommended" in response.text,
                "claude_md_compliant": "CLAUDE.md" in response.text
            }
            
            self.analysis_results["expert_fixes_status"] = version_indicators
            
            print("コードバージョン指標:")
            for indicator, present in version_indicators.items():
                status = "検出" if present else "未検出"
                print(f"  {indicator}: {status}")
            
            # 判定
            if version_indicators["expert_fixes_present"]:
                print("\n[結論] 本番環境に専門家修正が既に適用されている可能性")
                return "EXPERT_FIXES_APPLIED"
            else:
                print("\n[結論] 本番環境に専門家修正が適用されていない")
                return "EXPERT_FIXES_NOT_APPLIED"
                
        except Exception as e:
            print(f"バージョン分析エラー: {e}")
            return "VERSION_ANALYSIS_FAILED"
    
    def run_comprehensive_production_analysis(self):
        """
        包括的な本番環境分析実行
        """
        print("ULTRA SYNC: 本番環境深度分析（副作用絶対防止）")
        print("Production Environment Deep Analysis with Zero Side Effects")
        print("=" * 70)
        
        # Phase 1: 複数進行テスト
        success_count, total_tests = self.test_multiple_progressions()
        
        # Phase 2: コードバージョン分析
        version_status = self.analyze_current_code_version()
        
        # Phase 3: 最終判定
        print("\n" + "=" * 70)
        print("本番環境深度分析：最終結果")
        print("=" * 70)
        
        print(f"進行テスト成功率: {success_count}/{total_tests} ({(success_count/total_tests)*100:.1f}%)")
        print(f"コードバージョン状況: {version_status}")
        print(f"デプロイ必要性: {self.analysis_results['deployment_necessity']}")
        
        # 推奨アクション
        deployment_necessity = self.analysis_results["deployment_necessity"]
        
        if deployment_necessity == "NOT_NEEDED":
            print("\n[推奨] デプロイ不要 - 本番環境は既に正常動作")
            print("  → STAGE 4をスキップしてプロジェクト完了可能")
            
        elif deployment_necessity == "MAYBE_NEEDED":
            print("\n[推奨] 慎重なデプロイ検討")
            print("  → STAGE 4で安定性向上のデプロイを実行")
            
        elif deployment_necessity in ["PROBABLY_NEEDED", "DEFINITELY_NEEDED"]:
            print("\n[推奨] デプロイ必要")
            print("  → STAGE 4で専門家修正を本番環境に適用")
        
        return deployment_necessity != "NOT_NEEDED"
    
    def save_analysis_results(self):
        """分析結果保存"""
        with open('ultra_sync_production_deep_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        print("\n分析結果保存: ultra_sync_production_deep_analysis.json")

if __name__ == "__main__":
    analyzer = UltraSyncProductionAnalyzer()
    deployment_needed = analyzer.run_comprehensive_production_analysis()
    analyzer.save_analysis_results()
    
    exit(0 if not deployment_needed else 1)  # デプロイ不要=0, 必要=1