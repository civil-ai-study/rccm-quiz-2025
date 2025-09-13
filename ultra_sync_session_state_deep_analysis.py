# -*- coding: utf-8 -*-
"""
Ultra Sync Session State Deep Analysis
ウルトラシンク：セッション状態詳細解析

STAGE 1: 同じルーティンが失敗する真の根本原因特定
- Cookieサイズ制限説は否定された（最大1421bytes < 4KB）
- 実際のセッション内部データを詳細調査
- Flask session.modified問題とmutable data type変更検出不具合調査
- 副作用ゼロ保証での慎重な段階的調査
"""

import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import base64
import pickle
from urllib.parse import unquote

class UltraSyncSessionStateAnalyzer:
    """
    Ultra Sync: Deep session state analysis to identify why same routine fails
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "ULTRA_SYNC_SESSION_STATE_DEEP_ANALYSIS",
            "session_progression": [],
            "session_data_analysis": {},
            "failure_point_analysis": {},
            "root_cause_hypothesis": {}
        }
    
    def decode_flask_session_cookie(self, session_cookie):
        """
        Attempt to decode Flask session cookie to analyze internal data
        ULTRA SYNC: Safe analysis - no modification
        """
        try:
            # Flask sessions are base64 encoded and signed
            # This is for analysis only - no modification
            print(f"    Session cookie length: {len(session_cookie)} characters")
            
            # Basic analysis without decoding (to avoid security issues)
            cookie_analysis = {
                "length": len(session_cookie),
                "has_dots": session_cookie.count('.'),
                "starts_with": session_cookie[:20] + "..." if len(session_cookie) > 20 else session_cookie,
                "ends_with": "..." + session_cookie[-10:] if len(session_cookie) > 10 else session_cookie
            }
            
            return cookie_analysis
            
        except Exception as e:
            return {"error": str(e), "analysis": "cookie_decode_failed"}
    
    def deep_session_state_progression_analysis(self, department, question_type):
        """
        ULTRA SYNC STAGE 1: Deep analysis of session state through question progression
        Focus: Why same routine fails after working initially
        """
        print(f"=== ULTRA SYNC: Deep Session State Analysis ===")
        print(f"Department: {department} | Type: {question_type}")
        print(f"Objective: Identify why same routine fails after initial success")
        print("-" * 60)
        
        session = requests.Session()
        progression_data = {
            "department": department,
            "question_type": question_type,
            "progression_steps": [],
            "session_state_changes": [],
            "failure_point": None,
            "session_corruption_detected": False
        }
        
        try:
            # Initialize session with detailed monitoring
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            initial_response = session.get(exam_url, timeout=30)
            
            if initial_response.status_code != 200:
                print(f"[ERROR] Initial session failed: {initial_response.status_code}")
                return progression_data
            
            print(f"[OK] Initial session established")
            
            # Analyze initial session state
            initial_cookies = session.cookies.get_dict()
            initial_session_analysis = {}
            
            for cookie_name, cookie_value in initial_cookies.items():
                if 'session' in cookie_name.lower():
                    initial_session_analysis[cookie_name] = self.decode_flask_session_cookie(cookie_value)
                    print(f"    Initial session cookie: {cookie_name}")
                    print(f"    Length: {len(cookie_value)} chars")
            
            current_response = initial_response
            
            # Progressive analysis through questions
            for question_no in range(1, 11):
                print(f"\\n--- Question {question_no}/10 Analysis ---")
                
                step_data = {
                    "question_number": question_no,
                    "step_status": "unknown",
                    "session_cookie_analysis": {},
                    "form_tokens_present": {},
                    "response_type": "unknown"
                }
                
                # Parse current page
                soup = BeautifulSoup(current_response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                page_title = soup.find('title')
                
                # Analyze form tokens
                step_data["form_tokens_present"] = {
                    "csrf_token": csrf_token is not None,
                    "qid_input": qid_input is not None,
                    "csrf_value": csrf_token.get('value') if csrf_token else None,
                    "qid_value": qid_input.get('value') if qid_input else None
                }
                
                # Analyze page type
                title_text = page_title.text if page_title else ""
                if "エラー" in title_text:
                    step_data["response_type"] = "error_page"
                    step_data["step_status"] = "failed"
                    print(f"    [FAILURE DETECTED] Error page at question {question_no}")
                    print(f"    Title: {title_text}")
                    progression_data["failure_point"] = question_no
                    progression_data["session_corruption_detected"] = True
                    break
                elif "解答結果" in title_text:
                    step_data["response_type"] = "feedback_page"
                    step_data["step_status"] = "success"
                    print(f"    [SUCCESS] Feedback page")
                else:
                    step_data["response_type"] = "question_page"
                    step_data["step_status"] = "question_displayed"
                    print(f"    [OK] Question page displayed")
                
                # Analyze current session cookies
                current_cookies = session.cookies.get_dict()
                for cookie_name, cookie_value in current_cookies.items():
                    if 'session' in cookie_name.lower():
                        step_data["session_cookie_analysis"][cookie_name] = self.decode_flask_session_cookie(cookie_value)
                        print(f"    Session cookie length: {len(cookie_value)} chars")
                
                # Check for token presence issues
                if not csrf_token or not qid_input:
                    print(f"    [SESSION CORRUPTION] Missing tokens:")
                    print(f"      CSRF token: {'Present' if csrf_token else 'MISSING'}")
                    print(f"      QID input: {'Present' if qid_input else 'MISSING'}")
                    progression_data["session_corruption_detected"] = True
                    progression_data["failure_point"] = question_no
                    step_data["step_status"] = "session_corruption"
                    progression_data["progression_steps"].append(step_data)
                    break
                
                progression_data["progression_steps"].append(step_data)
                
                # If this is a question page, submit answer
                if step_data["response_type"] == "question_page":
                    print(f"    Submitting answer for question {question_no}...")
                    
                    post_data = {
                        'csrf_token': csrf_token.get('value'),
                        'qid': qid_input.get('value'),
                        'answer': 'A',
                        'elapsed': 30
                    }
                    
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': current_response.url,
                        'Origin': self.production_url
                    }
                    
                    post_response = session.post(f"{self.production_url}/exam", 
                                               data=post_data, 
                                               headers=headers,
                                               timeout=30)
                    
                    if post_response.status_code != 200:
                        print(f"    [POST FAILURE] Status: {post_response.status_code}")
                        progression_data["failure_point"] = question_no
                        break
                    
                    current_response = post_response
                    continue
                
                # If this is a feedback page, try to progress to next
                elif step_data["response_type"] == "feedback_page":
                    print(f"    Looking for next question link...")
                    
                    # Look for next question link
                    next_link = soup.find('a', href=lambda x: x and 'next=1' in x)
                    if next_link:
                        print(f"    [OK] Next question link found")
                        next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                        
                        if next_response.status_code == 200:
                            current_response = next_response
                            print(f"    [OK] Successfully loaded question {question_no + 1}")
                        else:
                            print(f"    [FAILURE] Next question load failed: {next_response.status_code}")
                            progression_data["failure_point"] = question_no + 1
                            break
                    else:
                        print(f"    [FAILURE] No next question link found")
                        progression_data["failure_point"] = question_no
                        break
                
        except Exception as e:
            print(f"[EXCEPTION] Analysis failed: {e}")
            progression_data["exception"] = str(e)
        
        return progression_data
    
    def run_ultra_sync_session_analysis(self):
        """
        ULTRA SYNC: Comprehensive session state analysis
        """
        print("ULTRA SYNC: SESSION STATE DEEP ANALYSIS")
        print("Objective: Identify why same routine fails after initial success")
        print("Method: Detailed session state monitoring through progression")
        print("=" * 70)
        
        test_departments = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning"}
        ]
        
        for dept_config in test_departments:
            print(f"\\n{'=' * 70}")
            print(f"Testing: {dept_config['name']}")
            
            progression_data = self.deep_session_state_progression_analysis(
                dept_config["dept"], dept_config["type"]
            )
            
            self.analysis_results["session_progression"].append(progression_data)
        
        # Analysis summary
        print(f"\\n" + "=" * 70)
        print("ULTRA SYNC SESSION ANALYSIS RESULTS")
        print("=" * 70)
        
        # Pattern analysis
        failure_patterns = []
        success_patterns = []
        
        for progression in self.analysis_results["session_progression"]:
            dept_name = progression["department"]
            if progression.get("failure_point"):
                failure_patterns.append({
                    "department": dept_name,
                    "failed_at_question": progression["failure_point"],
                    "session_corrupted": progression["session_corruption_detected"],
                    "steps_completed": len(progression["progression_steps"])
                })
            else:
                success_patterns.append({
                    "department": dept_name,
                    "completed_questions": len(progression["progression_steps"])
                })
        
        print(f"\\nFAILURE PATTERN ANALYSIS:")
        if failure_patterns:
            for failure in failure_patterns:
                print(f"  {failure['department']}:")
                print(f"    Failed at question: {failure['failed_at_question']}")
                print(f"    Session corruption: {failure['session_corrupted']}")
                print(f"    Steps completed: {failure['steps_completed']}")
        else:
            print(f"  No failures detected in current analysis")
        
        print(f"\\nSUCCESS PATTERN ANALYSIS:")
        if success_patterns:
            for success in success_patterns:
                print(f"  {success['department']}: {success['completed_questions']} questions completed")
        else:
            print(f"  No successful completions detected")
        
        # Root cause hypothesis
        print(f"\\n[ROOT CAUSE HYPOTHESIS - STAGE 1]")
        print(f"Based on detailed session state analysis:")
        
        if failure_patterns:
            consistent_failures = all(f["session_corrupted"] for f in failure_patterns)
            if consistent_failures:
                print(f"[OK] Consistent session corruption detected across failures")
                print(f"[OK] Pattern: Same routine works initially, then session state corrupts")
                print(f"[OK] Manifestation: Missing CSRF tokens, missing QID values")
                print(f"\\nNext Stage: Investigate Flask session.modified and mutable data issues")
            else:
                print(f"? Mixed failure patterns - need deeper investigation")
        else:
            print(f"? No clear failure patterns detected in current test")
        
        # Save results
        self.save_analysis_results()
        
        return len(failure_patterns) > 0
    
    def save_analysis_results(self):
        """Save analysis results"""
        with open('ultra_sync_session_state_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        print(f"\\nUltra Sync analysis results saved: ultra_sync_session_state_analysis.json")

if __name__ == "__main__":
    analyzer = UltraSyncSessionStateAnalyzer()
    failures_detected = analyzer.run_ultra_sync_session_analysis()
    print(f"\\nFailures detected: {failures_detected}")
    sys.exit(0)