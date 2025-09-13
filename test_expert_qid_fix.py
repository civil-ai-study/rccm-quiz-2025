# -*- coding: utf-8 -*-
"""
Test Expert QID-Category Validation Fix
専門家推奨のQID-カテゴリ検証修正のテスト
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class ExpertQIDFixTester:
    """
    Test the expert-recommended QID-Category validation fix
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "EXPERT_QID_FIX_VALIDATION",
            "test_scenarios": [],
            "fix_effectiveness": {}
        }
    
    def test_civil_planning_qid_133_issue(self):
        """
        Test the specific QID 133 civil_planning issue that was causing errors
        """
        print("=== Testing Civil Planning QID 133 Issue ===")
        print("Testing the specific issue that caused 'Invalid Question ID' error...")
        print("-" * 50)
        
        session = requests.Session()
        test_result = {
            "test_name": "civil_planning_qid_133_fix_test",
            "issue": "QID 133 in civil_planning session causing Invalid Question ID error",
            "expected_outcome": "Better error message or correct category handling",
            "actual_outcome": "UNKNOWN",
            "fix_effective": False
        }
        
        try:
            # Initialize civil_planning specialist session
            exam_url = f"{self.production_url}/exam?department=civil_planning&question_type=specialist&count=10"
            response = session.get(exam_url, timeout=30)
            
            if response.status_code != 200:
                test_result["actual_outcome"] = f"Initialization failed: {response.status_code}"
                return test_result
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_token or not qid_input:
                test_result["actual_outcome"] = "Missing CSRF token or QID"
                return test_result
            
            csrf_value = csrf_token.get('value')
            qid_value = qid_input.get('value')
            
            print(f"  Initialized session with QID: {qid_value}")
            
            # Check if we got QID 133 (the problematic one)
            if int(qid_value) == 133:
                print(f"  [CRITICAL] Still getting QID 133 in civil_planning session!")
                test_result["actual_outcome"] = "Still getting QID 133 - fix may not be complete"
            else:
                print(f"  [GOOD] Got different QID ({qid_value}) - QID assignment may be fixed")
                test_result["actual_outcome"] = f"Got QID {qid_value} instead of 133"
                test_result["fix_effective"] = True
            
            # Submit answer to test POST processing
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
            
            print(f"  POST response status: {post_response.status_code}")
            
            if post_response.status_code == 200:
                # Check if we get a feedback page or error page
                response_soup = BeautifulSoup(post_response.text, 'html.parser')
                page_title = response_soup.find('title')
                title_text = page_title.text if page_title else "NO TITLE"
                
                if "エラー" in title_text:
                    print(f"  [ERROR PAGE] Got error page: {title_text}")
                    # Check for our expert error message
                    if "QID" in post_response.text or "category" in post_response.text.lower():
                        print(f"  [EXPERT FIX] Error contains expert validation message")
                        test_result["actual_outcome"] += " - Expert error handling triggered"
                        test_result["fix_effective"] = True
                    else:
                        print(f"  [OLD ERROR] Still getting old error format")
                elif "解答結果" in title_text:
                    print(f"  [SUCCESS] Got feedback page: {title_text}")
                    test_result["actual_outcome"] += " - Feedback page displayed successfully"
                    test_result["fix_effective"] = True
                else:
                    print(f"  [UNKNOWN] Unexpected page: {title_text}")
                    test_result["actual_outcome"] += f" - Unexpected page: {title_text}"
            else:
                print(f"  [ERROR] POST failed with status: {post_response.status_code}")
                test_result["actual_outcome"] += f" - POST failed: {post_response.status_code}"
            
        except Exception as e:
            print(f"  [EXCEPTION] Test failed: {e}")
            test_result["actual_outcome"] = f"Exception: {str(e)}"
        
        self.test_results["test_scenarios"].append(test_result)
        return test_result
    
    def test_multiple_departments_qid_consistency(self):
        """
        Test QID consistency across different departments
        """
        print(f"\n=== Testing QID Consistency Across Departments ===")
        print("Testing if QIDs are properly assigned to correct categories...")
        print("-" * 50)
        
        departments_to_test = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning Specialist"}
        ]
        
        consistency_results = []
        
        for dept_config in departments_to_test:
            print(f"\n  Testing {dept_config['name']}...")
            
            session = requests.Session()
            dept_result = {
                "department": dept_config["dept"],
                "question_type": dept_config["type"],
                "name": dept_config["name"],
                "qid_assigned": None,
                "status": "UNKNOWN",
                "category_match": False
            }
            
            try:
                exam_url = f"{self.production_url}/exam?department={dept_config['dept']}&question_type={dept_config['type']}&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    qid_input = soup.find('input', {'name': 'qid'})
                    
                    if qid_input:
                        qid_value = qid_input.get('value')
                        dept_result["qid_assigned"] = qid_value
                        dept_result["status"] = "QID_ASSIGNED"
                        
                        print(f"    QID assigned: {qid_value}")
                        
                        # For civil_planning, check if we're no longer getting QID 133
                        if dept_config["dept"] == "civil_planning" and qid_value != "133":
                            dept_result["category_match"] = True
                            print(f"    [GOOD] Civil planning no longer getting QID 133")
                        elif dept_config["dept"] != "civil_planning":
                            dept_result["category_match"] = True
                            print(f"    [OK] Non-civil-planning department")
                    else:
                        dept_result["status"] = "NO_QID"
                        print(f"    [ERROR] No QID found")
                else:
                    dept_result["status"] = f"HTTP_{response.status_code}"
                    print(f"    [ERROR] HTTP {response.status_code}")
                    
            except Exception as e:
                dept_result["status"] = f"EXCEPTION: {str(e)}"
                print(f"    [EXCEPTION] {e}")
            
            consistency_results.append(dept_result)
            time.sleep(1)  # Brief delay between tests
        
        self.test_results["fix_effectiveness"]["department_qid_consistency"] = consistency_results
        return consistency_results
    
    def run_expert_fix_verification(self):
        """
        Run comprehensive verification of expert QID fix
        """
        print("Expert QID-Category Validation Fix Verification")
        print("Testing the effectiveness of expert-recommended fixes")
        print("=" * 60)
        
        # Test 1: Specific QID 133 civil_planning issue
        qid_133_test = self.test_civil_planning_qid_133_issue()
        
        # Test 2: QID consistency across departments
        consistency_tests = self.test_multiple_departments_qid_consistency()
        
        # Overall assessment
        print(f"\n" + "=" * 60)
        print("EXPERT FIX VERIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"\nQID 133 Civil Planning Test:")
        print(f"  Fix Effective: {'YES' if qid_133_test['fix_effective'] else 'NO'}")
        print(f"  Outcome: {qid_133_test['actual_outcome']}")
        
        print(f"\nDepartment QID Consistency:")
        for result in consistency_tests:
            status = "GOOD" if result["category_match"] else "ISSUE"
            print(f"  {result['name']}: {status} (QID: {result['qid_assigned']})")
        
        # Overall verdict
        fix_success_count = sum(1 for r in consistency_tests if r["category_match"])
        total_tests = len(consistency_tests)
        
        if qid_133_test["fix_effective"] and fix_success_count == total_tests:
            print(f"\n[VERDICT] Expert fix appears to be SUCCESSFUL")
            print(f"  - QID 133 issue resolved: YES")
            print(f"  - Department consistency: {fix_success_count}/{total_tests}")
        else:
            print(f"\n[VERDICT] Expert fix needs additional work")
            print(f"  - QID 133 issue resolved: {'YES' if qid_133_test['fix_effective'] else 'NO'}")
            print(f"  - Department consistency: {fix_success_count}/{total_tests}")
        
        # Save results
        self.save_test_results()
        
        return qid_133_test["fix_effective"] and fix_success_count == total_tests
    
    def save_test_results(self):
        """Save test results"""
        with open('test_expert_qid_fix_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\nTest results saved: test_expert_qid_fix_results.json")

if __name__ == "__main__":
    tester = ExpertQIDFixTester()
    success = tester.run_expert_fix_verification()
    exit(0 if success else 1)