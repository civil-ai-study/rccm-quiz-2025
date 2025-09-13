# -*- coding: utf-8 -*-
"""
POST 400 Error Investigation - Production Environment
Deep analysis of the 1st to 2nd question progression failure
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json

def investigate_post_400_error():
    """Investigate POST 400 error in production environment"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("=== POST 400 Error Investigation ===")
    print("Deep analysis of production environment POST failure")
    print("=" * 50)
    
    investigation_results = {
        "get_success": False,
        "csrf_token_valid": False,
        "qid_valid": False,
        "post_error_details": "",
        "response_headers": {},
        "error_analysis": []
    }
    
    try:
        # 1. GET request analysis
        print("\n1. GET request detailed analysis...")
        quiz_url = f"{base_url}/exam?department=road&question_type=specialist&count=10"
        
        get_response = session.get(quiz_url)
        print(f"GET Status: {get_response.status_code}")
        print(f"GET Response headers: {dict(get_response.headers)}")
        
        if get_response.status_code != 200:
            investigation_results["error_analysis"].append(f"GET failed: {get_response.status_code}")
            return investigation_results
        
        investigation_results["get_success"] = True
        
        # 2. HTML parsing and token extraction
        print("\n2. HTML parsing and token extraction...")
        soup = BeautifulSoup(get_response.text, 'html.parser')
        
        # CSRF token analysis
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input or not csrf_input.get('value'):
            investigation_results["error_analysis"].append("CSRF token not found in HTML")
            print("X CSRF token not found")
            return investigation_results
        
        csrf_token = csrf_input.get('value')
        investigation_results["csrf_token_valid"] = len(csrf_token) > 20
        print(f"CSRF token: {csrf_token[:30]}... (length: {len(csrf_token)})")
        
        # QID analysis
        qid_input = soup.find('input', {'name': 'qid'})
        if not qid_input:
            investigation_results["error_analysis"].append("QID not found in HTML")
            print("X QID not found")
            return investigation_results
        
        qid = qid_input.get('value')
        investigation_results["qid_valid"] = qid is not None
        print(f"QID: {qid}")
        
        # 3. POST request preparation and execution
        print("\n3. POST request preparation and execution...")
        
        post_data = {
            'csrf_token': csrf_token,
            'qid': qid,
            'selected_option': 'A',
            'elapsed': 45
        }
        
        headers = {
            'Referer': quiz_url,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"POST data: {post_data}")
        print(f"POST headers: {headers}")
        
        # Execute POST request
        post_response = session.post(f"{base_url}/exam", data=post_data, headers=headers)
        
        print(f"POST Status: {post_response.status_code}")
        print(f"POST Response headers: {dict(post_response.headers)}")
        
        investigation_results["response_headers"] = dict(post_response.headers)
        
        if post_response.status_code == 400:
            print("POST 400 Error detected - analyzing response content...")
            
            # Save response content for analysis
            response_text = post_response.text
            investigation_results["post_error_details"] = response_text[:1000]
            
            print(f"Response content (first 500 chars): {response_text[:500]}")
            
            # Look for specific error messages
            if "csrf" in response_text.lower():
                investigation_results["error_analysis"].append("CSRF validation error detected")
                print("CSRF validation error detected in response")
            
            if "invalid" in response_text.lower():
                investigation_results["error_analysis"].append("Invalid data error detected")
                print("Invalid data error detected in response")
            
            if "expired" in response_text.lower():
                investigation_results["error_analysis"].append("Session expired error detected")
                print("Session expired error detected in response")
                
            # Check if error page contains specific form validation errors
            error_soup = BeautifulSoup(response_text, 'html.parser')
            error_messages = error_soup.find_all(['div', 'span', 'p'], class_=re.compile(r'error|alert|warning'))
            
            for error_msg in error_messages:
                error_text = error_msg.get_text().strip()
                if error_text:
                    investigation_results["error_analysis"].append(f"Error message found: {error_text}")
                    print(f"Error message: {error_text}")
        
        elif post_response.status_code == 200:
            print("POST succeeded - analyzing progression...")
            post_soup = BeautifulSoup(post_response.text, 'html.parser')
            if "2/10" in post_soup.get_text():
                print("SUCCESS: Progression to question 2 confirmed")
            else:
                print("WARNING: Still on question 1")
        
        return investigation_results
        
    except Exception as e:
        investigation_results["error_analysis"].append(f"Investigation error: {str(e)}")
        print(f"Investigation error: {e}")
        return investigation_results

def analyze_production_vs_local():
    """Compare production environment vs local environment behavior"""
    
    print("\n=== Production vs Local Environment Analysis ===")
    
    # Test local environment behavior (if available)
    local_url = "http://localhost:5000"
    session_local = requests.Session()
    
    try:
        local_response = session_local.get(f"{local_url}/exam?department=road&question_type=specialist&count=10")
        if local_response.status_code == 200:
            print("Local environment accessible - comparison possible")
            # Add local environment comparison logic here
        else:
            print("Local environment not accessible - production-only analysis")
    except:
        print("Local environment not accessible - production-only analysis")

if __name__ == "__main__":
    results = investigate_post_400_error()
    analyze_production_vs_local()
    
    print("\n" + "=" * 50)
    print("Investigation Results Summary")
    print("=" * 50)
    
    print(f"GET Success: {results['get_success']}")
    print(f"CSRF Token Valid: {results['csrf_token_valid']}")
    print(f"QID Valid: {results['qid_valid']}")
    
    if results['error_analysis']:
        print(f"\nError Analysis ({len(results['error_analysis'])} items):")
        for i, error in enumerate(results['error_analysis'], 1):
            print(f"  {i}. {error}")
    else:
        print("\nNo specific errors detected")
    
    # Save investigation results
    with open('post_400_investigation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\nInvestigation results saved to post_400_investigation_results.json")