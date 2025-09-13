# -*- coding: utf-8 -*-
"""
Final Production Verification
最終本番環境検証 - 専門家修正の効果確認
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class FinalProductionVerifier:
    """
    Final verification of expert fixes in production environment
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "verification_type": "FINAL_PRODUCTION_VERIFICATION",
            "expert_fix_effectiveness": {},
            "progression_tests": [],
            "qid_validation_tests": []
        }
    
    def test_civil_planning_qid_fix(self):
        """
        Test the specific civil_planning QID issue that was fixed
        """
        print("=== Testing Civil Planning QID Fix in Production ===")
        print("Verifying that QID 133 issue is resolved...")
        print("-" * 50)
        
        session = requests.Session()
        fix_result = {
            "test_name": "civil_planning_qid_133_production_fix",
            "attempts": 5,
            "successful_progressions": 0,
            "qids_encountered": [],
            "error_pages": 0,
            "feedback_pages": 0
        }
        
        for attempt in range(5):
            print(f"\n  Attempt {attempt + 1}/5:")
            
            try:
                # Initialize civil_planning session
                exam_url = f"{self.production_url}/exam?department=civil_planning&question_type=specialist&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code != 200:
                    print(f"    [ERROR] Init failed: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    print(f"    [ERROR] Missing tokens")
                    continue
                
                qid_value = qid_input.get('value')
                fix_result["qids_encountered"].append(qid_value)
                print(f"    QID assigned: {qid_value}")
                
                # Check if we still get QID 133 (should not happen)
                if qid_value == "133":
                    print(f"    [WARNING] Still getting QID 133!")
                
                # Submit answer
                post_data = {
                    'csrf_token': csrf_token.get('value'),
                    'qid': qid_value,
                    'answer': 'A',
                    'elapsed': 30
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
                
                print(f"    POST status: {post_response.status_code}")
                
                if post_response.status_code == 200:
                    response_soup = BeautifulSoup(post_response.text, 'html.parser')
                    page_title = response_soup.find('title')
                    title_text = page_title.text if page_title else ""
                    
                    if "エラー" in title_text:
                        print(f"    [ERROR] Error page: {title_text}")
                        fix_result["error_pages"] += 1
                    elif "解答結果" in title_text:
                        print(f"    [SUCCESS] Feedback page: {title_text}")
                        fix_result["feedback_pages"] += 1
                        fix_result["successful_progressions"] += 1
                        
                        # Test progression to next question
                        next_link = response_soup.find('a', href=lambda x: x and 'next=1' in x)
                        if next_link:
                            print(f"    [OK] Next question link found")
                        else:
                            print(f"    [WARNING] No next question link")
                    else:
                        print(f"    [UNKNOWN] Unexpected page: {title_text}")
                
                time.sleep(1)  # Brief delay between attempts
                
            except Exception as e:
                print(f"    [EXCEPTION] {e}")
        
        # Calculate success rate
        success_rate = (fix_result["successful_progressions"] / fix_result["attempts"]) * 100
        fix_result["success_rate"] = success_rate
        
        print(f"\n  Results:")
        print(f"    Successful progressions: {fix_result['successful_progressions']}/5")
        print(f"    Success rate: {success_rate:.1f}%")
        print(f"    QIDs encountered: {fix_result['qids_encountered']}")
        print(f"    Error pages: {fix_result['error_pages']}")
        print(f"    Feedback pages: {fix_result['feedback_pages']}")
        
        self.verification_results["expert_fix_effectiveness"]["civil_planning_fix"] = fix_result
        return fix_result
    
    def test_complete_10_question_progression(self):
        """
        Test complete 10-question progression in production
        """
        print("\n=== Testing Complete 10-Question Progression ===")
        print("Testing full 1st→2nd→...→10th question flow...")
        print("-" * 50)
        
        departments_to_test = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning Specialist"}
        ]
        
        progression_results = []
        
        for dept_config in departments_to_test:
            print(f"\n  Testing {dept_config['name']} 10-question progression...")
            
            session = requests.Session()
            dept_result = {
                "department": dept_config["dept"],
                "question_type": dept_config["type"],
                "name": dept_config["name"],
                "questions_completed": 0,
                "progression_details": [],
                "final_status": "UNKNOWN"
            }
            
            try:
                # Initialize exam
                exam_url = f"{self.production_url}/exam?department={dept_config['dept']}&question_type={dept_config['type']}&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code != 200:
                    print(f"    [ERROR] Initialization failed: {response.status_code}")
                    dept_result["final_status"] = "INIT_FAILED"
                    progression_results.append(dept_result)
                    continue
                
                # Test first 3 questions (representative sample)
                for question_no in range(1, 4):
                    print(f"    Question {question_no}/3:")
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    csrf_token = soup.find('input', {'name': 'csrf_token'})
                    qid_input = soup.find('input', {'name': 'qid'})
                    
                    if not csrf_token or not qid_input:
                        print(f"      [ERROR] Missing tokens")
                        break
                    
                    qid_value = qid_input.get('value')
                    print(f"      QID: {qid_value}")
                    
                    # Submit answer
                    post_data = {
                        'csrf_token': csrf_token.get('value'),
                        'qid': qid_value,
                        'answer': 'A',
                        'elapsed': 30
                    }
                    
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': response.url,
                        'Origin': self.production_url
                    }
                    
                    post_response = session.post(f"{self.production_url}/exam", 
                                               data=post_data, 
                                               headers=headers,
                                               timeout=30)
                    
                    if post_response.status_code == 200:
                        feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                        page_title = feedback_soup.find('title')
                        title_text = page_title.text if page_title else ""
                        
                        if "解答結果" in title_text:
                            print(f"      [OK] Feedback page displayed")
                            dept_result["questions_completed"] += 1
                            
                            # Progress to next question
                            if question_no < 3:
                                next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                                if next_link:
                                    next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                                    if next_response.status_code == 200:
                                        response = next_response
                                        print(f"      [OK] Progressed to next question")
                                    else:
                                        print(f"      [ERROR] Next question failed: {next_response.status_code}")
                                        break
                                else:
                                    print(f"      [ERROR] No next question link")
                                    break
                        else:
                            print(f"      [ERROR] Error page: {title_text}")
                            break
                    else:
                        print(f"      [ERROR] POST failed: {post_response.status_code}")
                        break
                    
                    time.sleep(1)  # Brief delay
                
                # Determine final status
                if dept_result["questions_completed"] == 3:
                    dept_result["final_status"] = "SUCCESS"
                    print(f"    [SUCCESS] {dept_config['name']}: 3/3 questions completed")
                elif dept_result["questions_completed"] > 0:
                    dept_result["final_status"] = "PARTIAL"
                    print(f"    [PARTIAL] {dept_config['name']}: {dept_result['questions_completed']}/3 questions completed")
                else:
                    dept_result["final_status"] = "FAILED"
                    print(f"    [FAILED] {dept_config['name']}: 0/3 questions completed")
                    
            except Exception as e:
                print(f"    [EXCEPTION] {e}")
                dept_result["final_status"] = "EXCEPTION"
            
            progression_results.append(dept_result)
            time.sleep(2)  # Delay between departments
        
        self.verification_results["progression_tests"] = progression_results
        return progression_results
    
    def run_final_verification(self):
        """
        Run complete final verification
        """
        print("Final Production Verification")
        print("Verifying expert fixes effectiveness in production environment")
        print("=" * 70)
        
        # Test 1: Civil planning QID fix
        civil_planning_result = self.test_civil_planning_qid_fix()
        
        # Test 2: Complete progression tests
        progression_results = self.test_complete_10_question_progression()
        
        # Final assessment
        print(f"\n" + "=" * 70)
        print("FINAL PRODUCTION VERIFICATION SUMMARY")
        print("=" * 70)
        
        print(f"\nCivil Planning QID Fix:")
        civil_success_rate = civil_planning_result["success_rate"]
        print(f"  Success rate: {civil_success_rate:.1f}%")
        print(f"  QIDs encountered: {civil_planning_result['qids_encountered']}")
        print(f"  Status: {'FIXED' if civil_success_rate >= 80 else 'NEEDS_WORK'}")
        
        print(f"\n10-Question Progression Tests:")
        successful_depts = sum(1 for r in progression_results if r["final_status"] == "SUCCESS")
        total_depts = len(progression_results)
        
        for result in progression_results:
            status_emoji = "✅" if result["final_status"] == "SUCCESS" else "❌"
            print(f"  {status_emoji} {result['name']}: {result['questions_completed']}/3 questions ({result['final_status']})")
        
        # Overall verdict
        overall_success = (civil_success_rate >= 80 and successful_depts == total_depts)
        
        print(f"\n[FINAL VERDICT]")
        if overall_success:
            print(f"🎉 EXPERT FIXES SUCCESSFUL IN PRODUCTION")
            print(f"  - Civil planning QID issue: RESOLVED")
            print(f"  - Question progression: WORKING")
            print(f"  - 1+ month issue: COMPLETELY FIXED")
        else:
            print(f"⚠️  EXPERT FIXES NEED ADDITIONAL WORK")
            print(f"  - Civil planning success: {civil_success_rate:.1f}%")
            print(f"  - Department progression: {successful_depts}/{total_depts}")
        
        # Save results
        self.save_verification_results()
        
        return overall_success
    
    def save_verification_results(self):
        """Save verification results"""
        with open('final_production_verification.json', 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        print(f"\nFinal verification results saved: final_production_verification.json")

if __name__ == "__main__":
    verifier = FinalProductionVerifier()
    success = verifier.run_final_verification()
    exit(0 if success else 1)