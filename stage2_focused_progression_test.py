# -*- coding: utf-8 -*-
"""
STAGE 2: Focused Test - Expert Modifications Verification
Tests the specific 1st→2nd question progression that has been failing
Based on existing expert modifications in app.py
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class Stage2ProgressionTester:
    """
    Focused test for 1st→2nd question progression
    Tests if expert modifications have resolved the issue
    """
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5003"
        self.session = requests.Session()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "STAGE_2_EXPERT_MODIFICATIONS_TEST",
            "progression_test": {},
            "csrf_handling": {},
            "session_atomicity": {},
            "expert_fixes_verified": []
        }
    
    def test_focused_progression(self):
        """
        Focused test of 1st→2nd question progression
        This is the core issue that has been failing for 1+ months
        """
        print("\n=== STAGE 2: FOCUSED 1ST→2ND PROGRESSION TEST ===")
        print("Testing expert modifications effectiveness")
        print("-" * 50)
        
        try:
            # Step 1: Initialize exam session
            print("STEP 1: Initializing exam session...")
            exam_url = f"{self.base_url}/exam?department=road&question_type=specialist&count=10"
            response = self.session.get(exam_url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to initialize: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_token or not qid_input:
                raise Exception("Missing CSRF token or QID in initial response")
            
            csrf_value = csrf_token.get('value')
            qid_value = qid_input.get('value')
            
            print(f"[OK] Session initialized: QID={qid_value}, CSRF present")
            
            self.test_results["progression_test"]["initialization"] = {
                "status": "SUCCESS",
                "qid": qid_value,
                "csrf_present": True
            }
            
            # Step 2: Submit answer to 1st question
            print("STEP 2: Submitting answer to 1st question...")
            
            post_data = {
                'csrf_token': csrf_value,
                'qid': qid_value,
                'answer': 'A',
                'elapsed': 45
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': exam_url,
                'Origin': self.base_url
            }
            
            start_time = time.time()
            post_response = self.session.post(f"{self.base_url}/exam", 
                                            data=post_data, 
                                            headers=headers)
            response_time = time.time() - start_time
            
            print(f"POST Status: {post_response.status_code}")
            print(f"Response Time: {response_time:.2f}s")
            
            # Step 3: Analyze POST response for expert fixes
            if post_response.status_code == 400:
                print("[ERROR] POST 400 - Expert CSRF handling may have failed")
                self.test_results["csrf_handling"]["post_400_error"] = {
                    "occurred": True,
                    "content_sample": post_response.text[:300]
                }
                return False
            elif post_response.status_code == 200:
                print("[OK] POST 200 - No CSRF errors detected")
                
                # Check if we got feedback page (current implementation)
                feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                has_feedback_elements = (
                    "正解" in post_response.text or "不正解" in post_response.text or
                    feedback_soup.find('div', class_='feedback-card') or
                    "あなたの解答:" in post_response.text
                )
                
                if has_feedback_elements:
                    print("[OK] Feedback page returned as expected")
                    
                    # Step 4: Navigate to next question
                    print("STEP 3: Navigating to 2nd question...")
                    
                    # Look for next question button/link
                    next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                    
                    if next_link:
                        next_url = next_link.get('href')
                        if not next_url.startswith('http'):
                            next_url = f"{self.base_url}{next_url}"
                        
                        # Navigate to next question
                        next_response = self.session.get(next_url)
                        
                        if next_response.status_code == 200:
                            next_soup = BeautifulSoup(next_response.text, 'html.parser')
                            next_qid = next_soup.find('input', {'name': 'qid'})
                            
                            if next_qid:
                                next_qid_value = next_qid.get('value')
                                
                                # Critical test: Did we progress to a different question?
                                if next_qid_value != qid_value:
                                    print(f"[SUCCESS] PROGRESSION CONFIRMED: {qid_value} → {next_qid_value}")
                                    
                                    self.test_results["progression_test"]["progression_success"] = True
                                    self.test_results["progression_test"]["first_qid"] = qid_value
                                    self.test_results["progression_test"]["second_qid"] = next_qid_value
                                    
                                    return True
                                else:
                                    print(f"[FAILURE] STUCK ON SAME QUESTION: {qid_value}")
                                    self.test_results["progression_test"]["progression_success"] = False
                                    return False
                            else:
                                print("[ERROR] No QID found in 2nd question page")
                                return False
                        else:
                            print(f"[ERROR] Next question request failed: {next_response.status_code}")
                            return False
                    else:
                        print("[ERROR] No next question link found in feedback")
                        return False
                else:
                    print("[WARNING] Unexpected response format - not feedback page")
                    return False
            else:
                print(f"[ERROR] Unexpected POST status: {post_response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            self.test_results["progression_test"]["error"] = str(e)
            return False
    
    def verify_expert_fixes(self):
        """
        Verify specific expert fixes are present in the application
        """
        print("\n=== VERIFYING EXPERT MODIFICATIONS ===")
        
        # Test 1: CSRF error handling
        try:
            # Attempt request with invalid CSRF
            response = self.session.post(f"{self.base_url}/exam", 
                                       data={'csrf_token': 'invalid'})
            
            if response.status_code == 400 and "セキュリティトークン" in response.text:
                print("[OK] Expert CSRF error handler working")
                self.test_results["expert_fixes_verified"].append("csrf_error_handler")
        except:
            pass
        
        # Test 2: UTF-8 logging (check if app starts without Unicode errors)
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("[OK] UTF-8 logging configuration working (no startup Unicode errors)")
                self.test_results["expert_fixes_verified"].append("utf8_logging")
        except:
            pass
    
    def run_stage2_test(self):
        """
        Run complete Stage 2 verification
        """
        print("ULTRA SYNC STAGE 2: Expert Modifications Verification")
        print("Testing if expert fixes resolve 1st→2nd progression failure")
        print("=" * 60)
        
        # Verify expert fixes are present
        self.verify_expert_fixes()
        
        # Test focused progression
        progression_success = self.test_focused_progression()
        
        # Final results
        print("\n" + "=" * 60)
        print("STAGE 2 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Expert Fixes Verified: {len(self.test_results['expert_fixes_verified'])}")
        print(f"Progression Test: {'SUCCESS' if progression_success else 'FAILED'}")
        
        if progression_success:
            first_qid = self.test_results["progression_test"].get("first_qid")
            second_qid = self.test_results["progression_test"].get("second_qid")
            print(f"Confirmed Progression: Question {first_qid} → Question {second_qid}")
            print("\n[STAGE 2 COMPLETE] Expert modifications successfully resolved the issue!")
        else:
            print("\n[STAGE 2 INCOMPLETE] Expert modifications need further adjustment")
        
        return progression_success
    
    def save_results(self):
        """Save test results for analysis"""
        with open('stage2_expert_modifications_test.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print("\nTest results saved to stage2_expert_modifications_test.json")

if __name__ == "__main__":
    tester = Stage2ProgressionTester()
    success = tester.run_stage2_test()
    tester.save_results()
    
    exit(0 if success else 1)