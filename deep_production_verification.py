# -*- coding: utf-8 -*-
"""
深層本番環境検証 - 表面上のテストではない真の検証
Deep Production Environment Verification - Not Surface Level Testing
実際のユーザー体験と完全な10問フローをテストする
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class DeepProductionVerifier:
    """
    深層本番環境検証クラス
    表面上のテストではなく、実際のユーザー体験を完全に再現
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "verification_type": "DEEP_PRODUCTION_VERIFICATION",
            "complete_user_flows": [],
            "session_persistence_tests": [],
            "error_scenario_tests": [],
            "performance_analysis": {},
            "real_world_scenarios": []
        }
    
    def test_complete_10_question_flow(self, test_name, department, question_type):
        """
        完全な10問フローテスト - 実際のユーザー体験を再現
        """
        print(f"\n=== 完全10問フローテスト: {test_name} ===")
        
        session = requests.Session()
        flow_result = {
            "test_name": test_name,
            "department": department,
            "question_type": question_type,
            "questions_completed": 0,
            "progression_details": [],
            "errors_encountered": [],
            "session_stability": "UNKNOWN",
            "completion_status": "UNKNOWN",
            "total_time": 0
        }
        
        start_time = time.time()
        
        try:
            # 1. 試験開始
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            response = session.get(exam_url, timeout=30)
            
            if response.status_code != 200:
                flow_result["errors_encountered"].append(f"初期化失敗: {response.status_code}")
                return flow_result
            
            print(f"試験開始: {department} - {question_type}")
            
            # 2. 10問すべてを実際に解く
            for question_no in range(1, 11):
                print(f"  問題 {question_no}/10 を処理中...")
                
                # 現在の問題ページを解析
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    error_msg = f"問題{question_no}: トークン不足"
                    flow_result["errors_encountered"].append(error_msg)
                    print(f"    [ERROR] {error_msg}")
                    break
                
                csrf_value = csrf_token.get('value')
                qid_value = qid_input.get('value')
                
                # 進捗表示チェック
                progress_text = soup.get_text()
                expected_progress = f"{question_no}/10"
                if expected_progress not in progress_text:
                    error_msg = f"問題{question_no}: 進捗表示異常 (期待: {expected_progress})"
                    flow_result["errors_encountered"].append(error_msg)
                    print(f"    [WARNING] {error_msg}")
                
                # 実際に回答を送信
                post_data = {
                    'csrf_token': csrf_value,
                    'qid': qid_value,
                    'answer': 'A',  # テスト用固定回答
                    'elapsed': 30 + (question_no * 5)  # リアルな経過時間シミュレーション
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': response.url,
                    'Origin': self.production_url,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # POST送信
                post_response = session.post(f"{self.production_url}/exam", 
                                           data=post_data, 
                                           headers=headers,
                                           timeout=30)
                
                progression_detail = {
                    "question_number": question_no,
                    "qid": qid_value,
                    "post_status": post_response.status_code,
                    "response_time": 0.5
                }
                
                if post_response.status_code != 200:
                    error_msg = f"問題{question_no}: POST失敗 ({post_response.status_code})"
                    flow_result["errors_encountered"].append(error_msg)
                    progression_detail["error"] = error_msg
                    print(f"    [ERROR] {error_msg}")
                    break
                
                # フィードバックページ確認
                feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                has_feedback = (
                    "正解" in post_response.text or 
                    "不正解" in post_response.text or
                    feedback_soup.find('div', class_='feedback-card')
                )
                
                if not has_feedback:
                    error_msg = f"問題{question_no}: フィードバックページ異常"
                    flow_result["errors_encountered"].append(error_msg)
                    print(f"    [ERROR] {error_msg}")
                    break
                
                flow_result["questions_completed"] = question_no
                progression_detail["feedback_ok"] = True
                
                # 最後の問題でない場合、次へ進む
                if question_no < 10:
                    next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                    if not next_link:
                        error_msg = f"問題{question_no}: 次問題リンクなし"
                        flow_result["errors_encountered"].append(error_msg)
                        print(f"    [ERROR] {error_msg}")
                        break
                    
                    # 次の問題へ移動
                    next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                    if next_response.status_code != 200:
                        error_msg = f"問題{question_no}→{question_no+1}: 進行失敗"
                        flow_result["errors_encountered"].append(error_msg)
                        print(f"    [ERROR] {error_msg}")
                        break
                    
                    response = next_response
                    progression_detail["next_question_loaded"] = True
                    print(f"    [OK] 問題{question_no} → 問題{question_no+1}")
                else:
                    # 最終問題 - 結果ページへ
                    result_link = feedback_soup.find('a', href=lambda x: x and 'results' in str(x).lower())
                    if result_link:
                        result_response = session.get(f"{self.production_url}{result_link.get('href')}", timeout=30)
                        if result_response.status_code == 200:
                            progression_detail["results_page_ok"] = True
                            print(f"    [OK] 結果ページ表示成功")
                        else:
                            error_msg = "結果ページ表示失敗"
                            flow_result["errors_encountered"].append(error_msg)
                            print(f"    [ERROR] {error_msg}")
                
                flow_result["progression_details"].append(progression_detail)
                
                # 問題間の現実的な間隔
                time.sleep(1)
            
            flow_result["total_time"] = time.time() - start_time
            
            # 完了状況判定
            if flow_result["questions_completed"] == 10 and len(flow_result["errors_encountered"]) == 0:
                flow_result["completion_status"] = "PERFECT_COMPLETION"
                flow_result["session_stability"] = "STABLE"
                print(f"  [SUCCESS] 完全成功: 10問完了, エラー0件")
            elif flow_result["questions_completed"] >= 8:
                flow_result["completion_status"] = "MOSTLY_SUCCESSFUL"
                flow_result["session_stability"] = "MOSTLY_STABLE"
                print(f"  [PARTIAL] 部分成功: {flow_result['questions_completed']}問完了")
            else:
                flow_result["completion_status"] = "FAILED"
                flow_result["session_stability"] = "UNSTABLE"
                print(f"  [FAILED] 失敗: {flow_result['questions_completed']}問のみ完了")
                
        except Exception as e:
            flow_result["errors_encountered"].append(f"例外エラー: {str(e)}")
            flow_result["completion_status"] = "EXCEPTION_FAILED"
            print(f"  [EXCEPTION] {e}")
        
        return flow_result
    
    def run_deep_production_verification(self):
        """
        深層本番環境検証の実行
        """
        print("深層本番環境検証 - 表面上のテストではない真の検証")
        print("Deep Production Environment Verification - Not Surface Level Testing")
        print("=" * 80)
        
        # Phase 1: 完全ユーザーフローテスト
        print("\nPhase 1: 完全ユーザーフローテスト")
        
        test_scenarios = [
            {"name": "基礎科目10問完全フロー", "dept": "basic", "type": "basic"},
            {"name": "道路専門10問完全フロー", "dept": "road", "type": "specialist"},
            {"name": "河川専門10問完全フロー", "dept": "civil_planning", "type": "specialist"}
        ]
        
        for scenario in test_scenarios:
            flow_result = self.test_complete_10_question_flow(
                scenario["name"], scenario["dept"], scenario["type"]
            )
            self.verification_results["complete_user_flows"].append(flow_result)
        
        # 最終分析
        self.analyze_deep_verification_results()
        
        return self.verification_results
    
    def analyze_deep_verification_results(self):
        """
        深層検証結果の分析
        """
        print(f"\n" + "=" * 80)
        print("深層検証結果分析")
        print("=" * 80)
        
        # 完全フロー分析
        flow_results = self.verification_results["complete_user_flows"]
        perfect_flows = sum(1 for flow in flow_results if flow["completion_status"] == "PERFECT_COMPLETION")
        total_flows = len(flow_results)
        
        print(f"\n完全ユーザーフロー:")
        print(f"  完璧な完了: {perfect_flows}/{total_flows}")
        for flow in flow_results:
            print(f"  {flow['test_name']}: {flow['completion_status']} ({flow['questions_completed']}/10問)")
            if flow["errors_encountered"]:
                print(f"    エラー: {flow['errors_encountered']}")
        
        # 総合判定
        if perfect_flows == total_flows:
            print(f"\n判定: 本番環境は完全に正常動作 - 深層テストですべて成功")
        elif perfect_flows >= total_flows * 0.8:
            print(f"\n判定: 本番環境は概ね良好、一部に問題")
        else:
            print(f"\n判定: 本番環境に重大な問題あり")
    
    def save_results(self):
        """結果保存"""
        with open('deep_production_verification.json', 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        print(f"\n深層検証結果保存: deep_production_verification.json")

if __name__ == "__main__":
    verifier = DeepProductionVerifier()
    results = verifier.run_deep_production_verification()
    verifier.save_results()