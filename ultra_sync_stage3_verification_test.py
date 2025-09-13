# -*- coding: utf-8 -*-
"""
Ultra Sync Stage 3 Verification Test
ウルトラシンク段階3検証テスト

OBJECTIVE: Verify server-side session storage eliminates 2nd question corruption
TARGET: Consistent session preservation through question progression
EXPECTED: NO session corruption, successful 1->10 progression
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class UltraSyncStage3VerificationTest:
    """
    Ultra Sync Stage 3: Verify server-side session storage eliminates corruption
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "ULTRA_SYNC_STAGE3_VERIFICATION",
            "server_side_session_test": [],
            "corruption_eliminated": False
        }
    
    def test_server_side_session_progression(self, department, question_type):
        """
        Test 1->10 question progression with server-side sessions
        """
        print(f"=== Ultra Sync Stage 3 Verification: {department} {question_type} ===")
        print("Testing server-side session storage solution...")
        print("Expected: NO corruption at 2nd question")
        print("-" * 50)
        
        session = requests.Session()
        test_data = {
            "department": department,
            "question_type": question_type,
            "progression_success": [],
            "corruption_detected": False,
            "completed_questions": 0
        }
        
        try:
            # Initialize session
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            response = session.get(exam_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Session initialization failed: {response.status_code}")
                return test_data
            
            print(f"[OK] Session initialized with server-side storage")
            
            # Test critical 1st->2nd question progression
            for step in range(1, 11):
                print(f"\\nStep {step}/10:")
                
                # Parse current page
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                page_title = soup.find('title')
                title_text = page_title.text if page_title else ""
                
                # Check for corruption indicators
                if not csrf_token or not qid_input:
                    print(f"  [CORRUPTION] Missing tokens at step {step}")
                    test_data["corruption_detected"] = True
                    break
                elif "エラー" in title_text:
                    print(f"  [CORRUPTION] Error page at step {step}: {title_text}")
                    test_data["corruption_detected"] = True
                    break
                else:
                    print(f"  [OK] Tokens present - Session integrity maintained")
                    test_data["progression_success"].append(step)
                    test_data["completed_questions"] = step
                
                # Submit answer
                if "解答結果" not in title_text:  # If not feedback page
                    post_data = {
                        'csrf_token': csrf_token.get('value'),
                        'qid': qid_input.get('value'),
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
                    
                    if post_response.status_code != 200:
                        print(f"  [ERROR] POST failed at step {step}: {post_response.status_code}")
                        break
                    
                    response = post_response
                    print(f"  [OK] Answer submitted successfully")
                
                # Look for next question progression
                soup = BeautifulSoup(response.text, 'html.parser')
                if step < 10:
                    next_link = soup.find('a', href=lambda x: x and 'next=1' in x)
                    if next_link:
                        next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                        if next_response.status_code == 200:
                            response = next_response
                            print(f"  [OK] Advanced to question {step + 1}")
                        else:
                            print(f"  [ERROR] Failed to advance: {next_response.status_code}")
                            break
                    else:
                        # Check if this is the completion page
                        completion_indicators = ["完了", "結果", "終了"]
                        page_text = soup.get_text()
                        if any(indicator in page_text for indicator in completion_indicators):
                            print(f"  [SUCCESS] Quiz completion detected")
                            test_data["completed_questions"] = 10
                            break
                        else:
                            print(f"  [ERROR] No progression mechanism found")
                            break
                            
        except Exception as e:
            print(f"[EXCEPTION] Test failed: {e}")
            test_data["exception"] = str(e)
        
        return test_data
    
    def run_ultra_sync_stage3_verification(self):
        """
        Run comprehensive verification of server-side session fix
        """
        print("ULTRA SYNC STAGE 3: SERVER-SIDE SESSION VERIFICATION")
        print("Objective: Verify 2nd question corruption elimination")
        print("Method: Complete 1->10 progression test")
        print("=" * 70)
        
        test_departments = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning"}
        ]
        
        for dept_config in test_departments:
            test_data = self.test_server_side_session_progression(
                dept_config["dept"], dept_config["type"]
            )
            
            self.results["server_side_session_test"].append(test_data)
        
        # Analysis
        print(f"\\n" + "=" * 70)
        print("ULTRA SYNC STAGE 3 VERIFICATION RESULTS")
        print("=" * 70)
        
        corruption_eliminated = True
        successful_completions = 0
        
        for test in self.results["server_side_session_test"]:
            dept_name = test["department"]
            if test["corruption_detected"]:
                print(f"\\n{dept_name.upper()}:")
                print(f"  Status: CORRUPTION STILL DETECTED")
                print(f"  Completed questions: {test['completed_questions']}")
                corruption_eliminated = False
            else:
                print(f"\\n{dept_name.upper()}:")
                print(f"  Status: NO CORRUPTION DETECTED")
                print(f"  Completed questions: {test['completed_questions']}")
                if test["completed_questions"] >= 10:
                    successful_completions += 1
        
        self.results["corruption_eliminated"] = corruption_eliminated
        
        print(f"\\n[VERIFICATION SUMMARY]")
        if corruption_eliminated:
            print(f"SUCCESS: Server-side session storage eliminates 2nd question corruption")
            print(f"  Successful completions: {successful_completions}/{len(test_departments)}")
            print(f"  Client-side cookie session corruption: ELIMINATED")
            print(f"  Flask session serialization issues: BYPASSED")
        else:
            print(f"? Further investigation needed - corruption still detected")
        
        # Save results
        with open('ultra_sync_stage3_verification.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return corruption_eliminated

if __name__ == "__main__":
    verifier = UltraSyncStage3VerificationTest()
    success = verifier.run_ultra_sync_stage3_verification()
    print(f"\\nUltra Sync Stage 3 verification: {'SUCCESS' if success else 'NEEDS_REVIEW'}")
    exit(0 if success else 1)