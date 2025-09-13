# -*- coding: utf-8 -*-
"""
Production Environment Deep Verification Test
Non-superficial Deep Operation Verification
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json

def deep_production_verification():
    """Production Environment Deep Verification"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("=== Production Environment Deep Verification Test ===")
    print("Executing non-superficial deep operation verification")
    print("=" * 50)
    
    verification_results = {
        "session_consistency": False,
        "progression_1_to_2": False,
        "progression_2_to_3": False,
        "csrf_token_valid": False,
        "session_data_preserved": False,
        "error_details": []
    }
    
    try:
        # 1. Session start and Q1 detailed verification
        print("\n1. Session start and Q1 detailed acquisition...")
        quiz_url = f"{base_url}/exam?department=road&question_type=specialist&count=10"
        response = session.get(quiz_url)
        
        if response.status_code != 200:
            verification_results["error_details"].append(f"Q1 acquisition failed: {response.status_code}")
            print(f"X Q1 acquisition failed: {response.status_code}")
            return verification_results
        
        # 2. Detailed HTML analysis
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # CSRF token verification
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input or not csrf_input.get('value'):
            verification_results["error_details"].append("CSRF token not found")
            print("X CSRF token not found")
            return verification_results
        
        csrf_token = csrf_input.get('value')
        verification_results["csrf_token_valid"] = len(csrf_token) > 20
        print(f"O CSRF token verified: {csrf_token[:25]}... (length: {len(csrf_token)})")
        
        # QID verification
        qid_input = soup.find('input', {'name': 'qid'})
        if not qid_input:
            verification_results["error_details"].append("QID not found")
            print("X QID not found")
            return verification_results
        
        qid1 = qid_input.get('value')
        print(f"O Q1 QID: {qid1}")
        
        # Progress display verification
        progress_text = soup.get_text()
        if "1/" not in progress_text:
            verification_results["error_details"].append("Q1 progress display not found")
            print("X Q1 progress display not found")
        else:
            print("O Q1 progress display confirmed")
        
        # Session data verification (Cookie header check)
        session_cookies = session.cookies.get_dict()
        print(f"Session Cookies: {list(session_cookies.keys())}")
        verification_results["session_data_preserved"] = 'rccm_session' in session_cookies
        
        # 3. Q1 answer submission (actual POST request)
        print("\n2. Q1 answer submission detailed verification...")
        
        post_data = {
            'csrf_token': csrf_token,
            'qid': qid1,
            'selected_option': 'A',
            'elapsed': 45
        }
        
        headers = {
            'Referer': quiz_url,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url
        }
        
        print(f"POST transmission data: csrf_token={csrf_token[:20]}..., qid={qid1}, option=A")
        
        # POST execution
        start_time = time.time()
        post_response = session.post(f"{base_url}/exam", data=post_data, headers=headers)
        response_time = time.time() - start_time
        
        print(f"POST response time: {response_time:.2f} seconds")
        print(f"POST response code: {post_response.status_code}")
        
        if post_response.status_code != 200:
            verification_results["error_details"].append(f"POST failed: {post_response.status_code}")
            print(f"X POST failed: {post_response.status_code}")
            print(f"Error details: {post_response.text[:300]}")
            return verification_results
        
        print("O POST successful")
        
        # 4. Feedback screen analysis
        print("\n3. Feedback screen detailed analysis...")
        feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
        
        # Next question link search
        next_button = feedback_soup.find('a', href=re.compile(r'/exam\?.*next='))
        if not next_button:
            verification_results["error_details"].append("Next question button not found")
            print("X Next question button not found")
            return verification_results
        
        next_url = next_button.get('href')
        print(f"O Next question URL: {next_url}")
        
        # 5. Q2 acquisition verification
        print("\n4. Q2 acquisition detailed verification...")
        full_next_url = f"{base_url}{next_url}" if next_url.startswith('/') else next_url
        
        response2 = session.get(full_next_url)
        
        if response2.status_code != 200:
            verification_results["error_details"].append(f"Q2 acquisition failed: {response2.status_code}")
            print(f"X Q2 acquisition failed: {response2.status_code}")
            return verification_results
        
        # 6. Q2 detailed analysis
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        
        # QID change confirmation
        qid2_input = soup2.find('input', {'name': 'qid'})
        if not qid2_input:
            verification_results["error_details"].append("Q2 QID not found")
            print("X Q2 QID not found")
            return verification_results
        
        qid2 = qid2_input.get('value')
        print(f"O Q2 QID: {qid2}")
        
        # QID change confirmation
        if qid1 == qid2:
            verification_results["error_details"].append(f"QID not changed: {qid1}={qid2}")
            print(f"X QID not changed: {qid1}={qid2}")
        else:
            verification_results["progression_1_to_2"] = True
            print(f"O QID normal change: {qid1}->{qid2}")
        
        # Progress display confirmation
        progress_text2 = soup2.get_text()
        if "2/" in progress_text2:
            print("O Q2 progress display confirmed")
            verification_results["progression_1_to_2"] = True
        else:
            verification_results["error_details"].append("Q2 progress display not found")
            print("X Q2 progress display not found")
        
        # 7. Final session consistency confirmation
        verification_results["session_consistency"] = (
            verification_results["csrf_token_valid"] and
            verification_results["session_data_preserved"] and
            verification_results["progression_1_to_2"]
        )
        
        return verification_results
        
    except Exception as e:
        verification_results["error_details"].append(f"Test execution error: {str(e)}")
        print(f"X Test execution error: {e}")
        return verification_results

def print_verification_summary(results):
    """Verification results summary display"""
    print("\n" + "=" * 50)
    print("Comprehensive Verification Results Summary")
    print("=" * 50)
    
    total_checks = 5
    passed_checks = sum([
        results["session_consistency"],
        results["progression_1_to_2"],
        results["csrf_token_valid"],
        results["session_data_preserved"],
        len(results["error_details"]) == 0
    ])
    
    print(f"Passed checks: {passed_checks}/{total_checks}")
    
    if results["session_consistency"]:
        print("O Session consistency: Normal")
    else:
        print("X Session consistency: Problems detected")
    
    if results["progression_1_to_2"]:
        print("O Q1->Q2 progression: Normal")
    else:
        print("X Q1->Q2 progression: Failed")
    
    if results["csrf_token_valid"]:
        print("O CSRF protection: Normal")
    else:
        print("X CSRF protection: Problems detected")
    
    if results["session_data_preserved"]:
        print("O Session data preservation: Normal")
    else:
        print("X Session data preservation: Problems detected")
    
    if results["error_details"]:
        print(f"\nAlert: Detected errors ({len(results['error_details'])} items):")
        for i, error in enumerate(results["error_details"], 1):
            print(f"  {i}. {error}")
    else:
        print("\nO No errors detected")
    
    # Final judgment
    if passed_checks == total_checks:
        print("\nSuccess: All verification items cleared!")
        return True
    else:
        print(f"\nWarning: Problems detected in {total_checks - passed_checks} items")
        return False

if __name__ == "__main__":
    results = deep_production_verification()
    success = print_verification_summary(results)
    
    if success:
        print("\nO Production environment normal operation confirmed")
    else:
        print("\nX Production environment has problems - Additional fixes needed")
    
    # Save results in JSON
    with open('production_verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)