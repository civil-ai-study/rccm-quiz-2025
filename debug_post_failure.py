#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POST Status 400 Debug - Real cause identification
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_post_failure():
    """Debug why POST returns 400"""
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("POST Status 400 Debug Analysis")
    print("=" * 50)
    
    # Step 1: Get the actual question page
    print("\nStep 1: Get question page and extract form data")
    quiz_url = f"{base_url}/exam?department=env&question_type=specialist&category=all&count=10"
    
    try:
        response = session.get(quiz_url, timeout=30)
        if response.status_code != 200:
            print(f"FAILED: Cannot get question page - Status: {response.status_code}")
            return False
            
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Step 2: Extract actual form data
        print("\nStep 2: Extract form fields")
        form = soup.find('form', id='questionForm')
        
        if not form:
            print("FAILED: No form found with id='questionForm'")
            return False
            
        print("SUCCESS: Form found")
        
        # Extract hidden fields
        hidden_fields = {}
        for hidden in form.find_all('input', type='hidden'):
            name = hidden.get('name')
            value = hidden.get('value')
            if name:
                hidden_fields[name] = value
                print(f"Hidden field: {name} = '{value}'")
                
        # Check qid specifically
        qid_value = hidden_fields.get('qid')
        if not qid_value:
            print("CRITICAL: qid field is empty or None!")
            return False
        elif qid_value == '{{ question.id }}':
            print("CRITICAL: qid field not rendered - template issue!")
            return False
        else:
            print(f"SUCCESS: qid value = '{qid_value}'")
            
        # Step 3: Test POST with extracted data
        print("\nStep 3: Test POST with real form data")
        
        post_data = {
            'answer': 'A',
            'qid': qid_value,
            'elapsed': '5'
        }
        
        print(f"POST data: {post_data}")
        
        post_response = session.post(f"{base_url}/exam", data=post_data, timeout=30)
        print(f"POST Status: {post_response.status_code}")
        print(f"Response Length: {len(post_response.text)} bytes")
        
        if post_response.status_code == 400:
            print("POST Status 400 Analysis:")
            # Try to extract error message
            error_content = post_response.text
            if 'error' in error_content.lower():
                print("Error content found in response")
                # Extract first 500 chars for analysis
                error_sample = error_content[:500].replace('\n', ' ')
                print(f"Error sample: {error_sample}")
            else:
                print("No obvious error message in response")
                
        elif post_response.status_code == 200:
            print("SUCCESS: POST worked!")
            # Check response content
            post_content = post_response.text
            response_indicators = ['正解', '不正解', 'correct', 'incorrect', 'next', '問題']
            found_indicators = [ind for ind in response_indicators if ind in post_content]
            print(f"Response indicators: {found_indicators}")
            return True
            
        elif post_response.status_code == 302:
            location = post_response.headers.get('Location', 'No Location')
            print(f"Redirect to: {location}")
            return True
            
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("Starting detailed POST failure analysis...")
    success = debug_post_failure()
    
    if success:
        print("\nRESULT: POST mechanism WORKS")
    else:
        print("\nRESULT: POST mechanism BROKEN - cause identified")

if __name__ == "__main__":
    main()