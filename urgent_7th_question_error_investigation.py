# -*- coding: utf-8 -*-
"""
URGENT: 7th Question Error Investigation
緊急：7問目エラー現象の詳細調査

ユーザー報告：6問目まで正常→7問目で「無効な問題IDです」エラー
This is a session state corruption or question ID exhaustion issue
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class Urgent7thQuestionErrorInvestigator:
    """
    Urgent investigation of 7th question error phenomenon
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.investigation_results = {
            "timestamp": datetime.now().isoformat(),
            "investigation_type": "URGENT_7TH_QUESTION_ERROR",
            "session_progression_analysis": [],
            "qid_tracking": [],
            "error_pattern_analysis": {}
        }
    
    def trace_complete_session_progression(self, department, question_type):
        """
        Trace complete session progression from 1st to 10th question
        Track exactly where and why the error occurs
        """
        print(f"=== URGENT: Tracing {department} {question_type} Session Progression ===")
        print("Tracking each question transition to identify 7th question error...")
        print("-" * 60)
        
        session = requests.Session()
        progression_trace = {
            "department": department,
            "question_type": question_type,
            "questions_completed": 0,
            "error_occurred_at": None,
            "qid_sequence": [],
            "error_details": {},
            "session_state_corruption": False
        }
        
        try:
            # Initialize session
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            response = session.get(exam_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Session initialization failed: {response.status_code}")
                return progression_trace
            
            print(f"Session initialized successfully")
            
            # Track progression through all 10 questions
            for question_no in range(1, 11):
                print(f"\n  Question {question_no}/10:")
                
                # Parse current question page
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    print(f"    [CRITICAL] Missing tokens at question {question_no}")
                    progression_trace["error_occurred_at"] = question_no
                    progression_trace["error_details"]["type"] = "missing_tokens"
                    progression_trace["session_state_corruption"] = True
                    break
                
                qid_value = qid_input.get('value')
                csrf_value = csrf_token.get('value')
                
                print(f"    QID: {qid_value}")
                progression_trace["qid_sequence"].append({
                    "question_no": question_no,
                    "qid": qid_value,
                    "csrf_present": True
                })
                
                # Check for progress display consistency
                progress_text = soup.get_text()
                expected_progress = f"{question_no}/10"
                if expected_progress not in progress_text:
                    print(f"    [WARNING] Progress display mismatch at question {question_no}")
                
                # Submit answer
                post_data = {
                    'csrf_token': csrf_value,
                    'qid': qid_value,
                    'answer': 'A',
                    'elapsed': 30
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': response.url,
                    'Origin': self.production_url
                }
                
                # CRITICAL: Submit POST and analyze response
                post_response = session.post(f"{self.production_url}/exam", 
                                           data=post_data, 
                                           headers=headers,
                                           timeout=30)
                
                print(f"    POST Status: {post_response.status_code}")
                
                if post_response.status_code != 200:
                    print(f"    [CRITICAL ERROR] POST failed at question {question_no}")
                    progression_trace["error_occurred_at"] = question_no
                    progression_trace["error_details"]["type"] = "post_failure"
                    progression_trace["error_details"]["status_code"] = post_response.status_code
                    break
                
                # Analyze response content
                response_soup = BeautifulSoup(post_response.text, 'html.parser')
                page_title = response_soup.find('title')
                title_text = page_title.text if page_title else ""
                
                if "エラー" in title_text or "Error" in title_text:
                    print(f"    [CRITICAL ERROR] Error page at question {question_no}!")
                    print(f"    Error page title: {title_text}")
                    
                    # Extract error message
                    error_content = post_response.text
                    if "無効な問題ID" in error_content:
                        print(f"    [CONFIRMED] Invalid Question ID error at question {question_no}")
                    
                    progression_trace["error_occurred_at"] = question_no
                    progression_trace["error_details"]["type"] = "invalid_question_id"
                    progression_trace["error_details"]["error_title"] = title_text
                    progression_trace["error_details"]["qid_at_error"] = qid_value
                    
                    # This is the critical finding!
                    if question_no == 7:
                        print(f"    [USER REPORT CONFIRMED] 7th question error reproduced!")
                        progression_trace["error_details"]["matches_user_report"] = True
                    
                    break
                
                elif "解答結果" in title_text:
                    print(f"    [OK] Feedback page displayed")
                    progression_trace["questions_completed"] = question_no
                    
                    # Progress to next question (unless it's the last one)
                    if question_no < 10:
                        next_link = response_soup.find('a', href=lambda x: x and 'next=1' in x)
                        if next_link:
                            print(f"    [OK] Next question link found")
                            next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                            
                            if next_response.status_code == 200:
                                response = next_response
                                print(f"    [OK] Successfully progressed to question {question_no + 1}")
                            else:
                                print(f"    [ERROR] Failed to load question {question_no + 1}: {next_response.status_code}")
                                progression_trace["error_occurred_at"] = question_no + 1
                                progression_trace["error_details"]["type"] = "next_question_load_failure"
                                break
                        else:
                            print(f"    [ERROR] No next question link at question {question_no}")
                            progression_trace["error_occurred_at"] = question_no
                            progression_trace["error_details"]["type"] = "missing_next_link"
                            break
                    else:
                        print(f"    [COMPLETE] Reached final question")
                        break
                else:
                    print(f"    [ERROR] Unexpected page type: {title_text}")
                    progression_trace["error_occurred_at"] = question_no
                    progression_trace["error_details"]["type"] = "unexpected_page"
                    break
                
                # Brief delay between questions
                time.sleep(1)
        
        except Exception as e:
            print(f"[EXCEPTION] Investigation failed: {e}")
            progression_trace["error_details"]["exception"] = str(e)
        
        return progression_trace
    
    def analyze_session_state_corruption_pattern(self):
        """
        Analyze if there's a pattern in session state corruption
        """
        print(f"\n=== Session State Corruption Pattern Analysis ===")
        print("Testing multiple session progressions to identify patterns...")
        print("-" * 60)
        
        test_scenarios = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning Specialist"}
        ]
        
        pattern_analysis = {
            "error_occurrence_positions": [],
            "qid_exhaustion_indicators": [],
            "session_corruption_indicators": []
        }
        
        for scenario in test_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            progression_result = self.trace_complete_session_progression(
                scenario["dept"], scenario["type"]
            )
            
            self.investigation_results["session_progression_analysis"].append(progression_result)
            
            # Analyze error patterns
            if progression_result["error_occurred_at"]:
                error_position = progression_result["error_occurred_at"]
                pattern_analysis["error_occurrence_positions"].append({
                    "department": scenario["name"],
                    "error_at_question": error_position,
                    "error_type": progression_result["error_details"].get("type"),
                    "qid_at_error": progression_result["error_details"].get("qid_at_error")
                })
                
                print(f"  [ERROR DETECTED] {scenario['name']}: Error at question {error_position}")
                print(f"  Error type: {progression_result['error_details'].get('type')}")
                print(f"  QID at error: {progression_result['error_details'].get('qid_at_error')}")
            else:
                print(f"  [SUCCESS] {scenario['name']}: No errors detected")
            
            print(f"  Questions completed: {progression_result['questions_completed']}/10")
            print(f"  QID sequence: {[q['qid'] for q in progression_result['qid_sequence']]}")
            
            time.sleep(2)  # Delay between tests
        
        self.investigation_results["error_pattern_analysis"] = pattern_analysis
        return pattern_analysis
    
    def run_urgent_investigation(self):
        """
        Run complete urgent investigation
        """
        print("URGENT: 7th Question Error Investigation")
        print("User Report: 6 questions OK → 7th question 'Invalid Question ID' error")
        print("=" * 70)
        
        # Comprehensive session progression analysis
        pattern_analysis = self.analyze_session_state_corruption_pattern()
        
        # Final analysis
        print(f"\n" + "=" * 70)
        print("URGENT INVESTIGATION RESULTS")
        print("=" * 70)
        
        error_positions = pattern_analysis["error_occurrence_positions"]
        
        if error_positions:
            print(f"\nERROR PATTERN IDENTIFIED:")
            for error in error_positions:
                print(f"  {error['department']}: Error at question {error['error_at_question']}")
                print(f"    Type: {error['error_type']}")
                print(f"    QID: {error['qid_at_error']}")
            
            # Check for 7th question pattern
            seventh_question_errors = [e for e in error_positions if e["error_at_question"] == 7]
            if seventh_question_errors:
                print(f"\n[USER REPORT CONFIRMED] 7th question errors found:")
                for error in seventh_question_errors:
                    print(f"  {error['department']}: QID {error['qid_at_error']}")
                
                print(f"\n[ROOT CAUSE HYPOTHESIS]")
                print(f"  1. Session question ID array exhaustion at 7th position")
                print(f"  2. Question selection logic fails after 6 questions")
                print(f"  3. Category-specific question pool depletion")
                print(f"  4. Session state corruption during progression")
            
        else:
            print(f"\nNo consistent error pattern found in current test")
        
        # Save investigation results
        self.save_investigation_results()
        
        return len(error_positions) > 0
    
    def save_investigation_results(self):
        """Save investigation results"""
        with open('urgent_7th_question_error_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(self.investigation_results, f, ensure_ascii=False, indent=2)
        print(f"\nUrgent investigation results saved: urgent_7th_question_error_investigation.json")

if __name__ == "__main__":
    investigator = Urgent7thQuestionErrorInvestigator()
    error_found = investigator.run_urgent_investigation()
    exit(1 if error_found else 0)  # Exit 1 if errors found for urgent attention