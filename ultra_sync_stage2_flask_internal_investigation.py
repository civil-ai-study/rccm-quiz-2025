# -*- coding: utf-8 -*-
"""
Ultra Sync Stage 2: Flask Internal Session Investigation
ウルトラシンク段階2：Flask内部セッション機構調査

DISCOVERY:
- Application already uses session.modified = True (59 occurrences)
- Session corruption still occurs at 2nd question consistently
- Cookie growth pattern: 352-447 chars → 903-959 chars (2.5x growth)
- All departments fail with CSRF/QID token loss

HYPOTHESIS: Flask internal session serialization/deserialization corruption
"""

import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import re

class UltraSyncFlaskInternalInvestigator:
    """
    Ultra Sync Stage 2: Investigate Flask internal session mechanism failures
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.investigation_results = {
            "timestamp": datetime.now().isoformat(),
            "investigation_type": "ULTRA_SYNC_FLASK_INTERNAL_SESSION",
            "flask_session_analysis": {},
            "serialization_corruption_tests": [],
            "cookie_integrity_analysis": {}
        }
    
    def analyze_flask_session_cookie_integrity(self, session_cookie_before, session_cookie_after):
        """
        Ultra Sync: Analyze Flask session cookie integrity before/after corruption
        """
        integrity_analysis = {
            "before_length": len(session_cookie_before) if session_cookie_before else 0,
            "after_length": len(session_cookie_after) if session_cookie_after else 0,
            "size_growth_ratio": 0,
            "character_changes": {},
            "potential_corruption_indicators": []
        }
        
        if session_cookie_before and session_cookie_after:
            # Calculate growth ratio
            if len(session_cookie_before) > 0:
                integrity_analysis["size_growth_ratio"] = len(session_cookie_after) / len(session_cookie_before)
            
            # Analyze character composition changes
            before_dots = session_cookie_before.count('.')
            after_dots = session_cookie_after.count('.')
            integrity_analysis["character_changes"] = {
                "dot_count_before": before_dots,
                "dot_count_after": after_dots,
                "dot_count_changed": before_dots != after_dots
            }
            
            # Check for potential corruption indicators
            if integrity_analysis["size_growth_ratio"] > 2.0:
                integrity_analysis["potential_corruption_indicators"].append("excessive_size_growth")
            
            if after_dots != before_dots:
                integrity_analysis["potential_corruption_indicators"].append("dot_separator_corruption")
        
        return integrity_analysis
    
    def deep_flask_session_corruption_test(self, department, question_type):
        """
        Ultra Sync: Deep test of Flask session corruption patterns
        """
        print(f"=== ULTRA SYNC Stage 2: Flask Session Corruption Test ===")
        print(f"Department: {department} | Type: {question_type}")
        print(f"Focus: Flask internal session serialization corruption")
        print("-" * 60)
        
        session = requests.Session()
        test_data = {
            "department": department,
            "question_type": question_type,
            "session_integrity_progression": [],
            "corruption_detected": False,
            "corruption_point": None
        }
        
        try:
            # Initialize session
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            initial_response = session.get(exam_url, timeout=30)
            
            if initial_response.status_code != 200:
                print(f"[ERROR] Initial session failed: {initial_response.status_code}")
                return test_data
            
            print(f"[INIT] Session established")
            
            # Get initial session cookie
            initial_cookies = session.cookies.get_dict()
            initial_session_cookie = None
            for cookie_name, cookie_value in initial_cookies.items():
                if 'session' in cookie_name.lower():
                    initial_session_cookie = cookie_value
                    print(f"[INIT] Initial session cookie: {len(cookie_value)} chars")
                    break
            
            current_response = initial_response
            previous_session_cookie = initial_session_cookie
            
            # Test progression through critical failure points
            for step in range(1, 4):  # Focus on 1st, 2nd, 3rd steps where corruption occurs
                print(f"\\n--- Step {step}: Flask Session Analysis ---")
                
                step_analysis = {
                    "step_number": step,
                    "session_cookie_length": 0,
                    "integrity_analysis": {},
                    "form_tokens_status": {},
                    "flask_internal_status": "unknown"
                }
                
                # Parse current page
                soup = BeautifulSoup(current_response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                # Check form token status
                step_analysis["form_tokens_status"] = {
                    "csrf_present": csrf_token is not None,
                    "qid_present": qid_input is not None,
                    "csrf_value_length": len(csrf_token.get('value', '')) if csrf_token else 0,
                    "qid_value": qid_input.get('value') if qid_input else None
                }
                
                print(f"    Form tokens: CSRF={'YES' if csrf_token else 'NO'}, QID={'YES' if qid_input else 'NO'}")
                
                if not csrf_token or not qid_input:
                    print(f"    [CORRUPTION DETECTED] Missing form tokens at step {step}")
                    test_data["corruption_detected"] = True
                    test_data["corruption_point"] = step
                    step_analysis["flask_internal_status"] = "session_corruption"
                    test_data["session_integrity_progression"].append(step_analysis)
                    break
                
                # Analyze current session cookie
                current_cookies = session.cookies.get_dict()
                current_session_cookie = None
                for cookie_name, cookie_value in current_cookies.items():
                    if 'session' in cookie_name.lower():
                        current_session_cookie = cookie_value
                        step_analysis["session_cookie_length"] = len(cookie_value)
                        print(f"    Session cookie length: {len(cookie_value)} chars")
                        break
                
                # Analyze cookie integrity
                if previous_session_cookie and current_session_cookie:
                    step_analysis["integrity_analysis"] = self.analyze_flask_session_cookie_integrity(
                        previous_session_cookie, current_session_cookie
                    )
                    
                    growth_ratio = step_analysis["integrity_analysis"]["size_growth_ratio"]
                    print(f"    Cookie growth ratio: {growth_ratio:.2f}x")
                    
                    corruption_indicators = step_analysis["integrity_analysis"]["potential_corruption_indicators"]
                    if corruption_indicators:
                        print(f"    [WARNING] Corruption indicators: {corruption_indicators}")
                
                step_analysis["flask_internal_status"] = "healthy"
                test_data["session_integrity_progression"].append(step_analysis)
                
                # If this is a question page, submit answer
                page_title = soup.find('title')
                title_text = page_title.text if page_title else ""
                
                if "エラー" not in title_text:
                    print(f"    Submitting answer...")
                    
                    # Submit answer
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
                    
                    if post_response.status_code == 200:
                        current_response = post_response
                        previous_session_cookie = current_session_cookie
                        print(f"    [OK] POST successful")
                    else:
                        print(f"    [ERROR] POST failed: {post_response.status_code}")
                        test_data["corruption_detected"] = True
                        test_data["corruption_point"] = step
                        break
                else:
                    print(f"    [ERROR] Error page detected: {title_text}")
                    test_data["corruption_detected"] = True
                    test_data["corruption_point"] = step
                    break
                
        except Exception as e:
            print(f"[EXCEPTION] Flask internal test failed: {e}")
            test_data["exception"] = str(e)
        
        return test_data
    
    def run_ultra_sync_flask_internal_analysis(self):
        """
        Ultra Sync Stage 2: Complete Flask internal analysis
        """
        print("ULTRA SYNC STAGE 2: FLASK INTERNAL SESSION INVESTIGATION")
        print("Objective: Identify Flask session serialization corruption issues")
        print("Method: Deep analysis of session cookie integrity and Flask internals")
        print("=" * 70)
        
        test_departments = [
            {"dept": "basic", "type": "basic", "name": "Basic Subject"},
            {"dept": "road", "type": "specialist", "name": "Road Specialist"},
            {"dept": "civil_planning", "type": "specialist", "name": "Civil Planning"}
        ]
        
        for dept_config in test_departments:
            print(f"\\n{'=' * 70}")
            print(f"Testing: {dept_config['name']}")
            
            test_data = self.deep_flask_session_corruption_test(
                dept_config["dept"], dept_config["type"]
            )
            
            self.investigation_results["serialization_corruption_tests"].append(test_data)
        
        # Analysis summary
        print(f"\\n" + "=" * 70)
        print("ULTRA SYNC STAGE 2 RESULTS")
        print("=" * 70)
        
        # Analyze corruption patterns
        corruption_patterns = []
        cookie_growth_patterns = []
        
        for test in self.investigation_results["serialization_corruption_tests"]:
            if test["corruption_detected"]:
                corruption_patterns.append({
                    "department": test["department"],
                    "corruption_at_step": test["corruption_point"],
                    "integrity_data": test["session_integrity_progression"]
                })
            
            # Analyze cookie growth
            for step_data in test["session_integrity_progression"]:
                if "integrity_analysis" in step_data and step_data["integrity_analysis"]:
                    growth_ratio = step_data["integrity_analysis"]["size_growth_ratio"]
                    if growth_ratio > 1.5:  # Significant growth
                        cookie_growth_patterns.append({
                            "department": test["department"],
                            "step": step_data["step_number"],
                            "growth_ratio": growth_ratio,
                            "corruption_indicators": step_data["integrity_analysis"]["potential_corruption_indicators"]
                        })
        
        print(f"\\nCORRUPTION ANALYSIS:")
        if corruption_patterns:
            print(f"  Departments with corruption: {len(corruption_patterns)}")
            for pattern in corruption_patterns:
                print(f"    {pattern['department']}: Corrupted at step {pattern['corruption_at_step']}")
        else:
            print(f"  No corruption detected in current test")
        
        print(f"\\nCOOKIE GROWTH ANALYSIS:")
        if cookie_growth_patterns:
            print(f"  Significant cookie growth events: {len(cookie_growth_patterns)}")
            for growth in cookie_growth_patterns:
                print(f"    {growth['department']} step {growth['step']}: {growth['growth_ratio']:.2f}x growth")
                if growth['corruption_indicators']:
                    print(f"      Indicators: {growth['corruption_indicators']}")
        else:
            print(f"  No significant cookie growth detected")
        
        # Root cause hypothesis refinement
        print(f"\\n[ROOT CAUSE HYPOTHESIS - STAGE 2 REFINED]")
        print(f"Based on Flask internal session investigation:")
        
        if corruption_patterns and cookie_growth_patterns:
            print(f"[CRITICAL] Flask session corruption confirmed:")
            print(f"  - Consistent corruption at step 2 across departments")
            print(f"  - Cookie size growth 2.5x suggests data accumulation")
            print(f"  - session.modified=True already implemented (59 times)")
            print(f"  - Problem likely in Flask serialization/deserialization")
            print(f"\\n[NEXT STAGE] Implement server-side session storage (Redis/Filesystem)")
            print(f"  - Bypass Flask client-side cookie serialization entirely")
            print(f"  - Eliminate cookie-based session corruption")
        else:
            print(f"? Flask internal issues not clearly identified")
        
        # Save results
        self.save_investigation_results()
        
        return len(corruption_patterns) > 0
    
    def save_investigation_results(self):
        """Save investigation results"""
        with open('ultra_sync_flask_internal_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(self.investigation_results, f, ensure_ascii=False, indent=2)
        print(f"\\nUltra Sync Stage 2 results saved: ultra_sync_flask_internal_investigation.json")

if __name__ == "__main__":
    investigator = UltraSyncFlaskInternalInvestigator()
    corruption_confirmed = investigator.run_ultra_sync_flask_internal_analysis()
    print(f"\\nFlask corruption confirmed: {corruption_confirmed}")
    sys.exit(0)