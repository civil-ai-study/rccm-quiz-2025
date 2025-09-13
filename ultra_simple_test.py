# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def ultra_simple_test():
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("Ultra Simple Test")
    print("=" * 20)
    
    try:
        # 1. GET
        quiz_url = f"{base_url}/exam?department=road&question_type=specialist&count=10"
        response = session.get(quiz_url)
        print(f"GET Status: {response.status_code}")
        
        # 2. Extract tokens
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        qid_input = soup.find('input', {'name': 'qid'})
        
        if not csrf_input or not qid_input:
            print("Token missing")
            return False
        
        csrf_token = csrf_input.get('value')
        qid = qid_input.get('value')
        print(f"CSRF: {csrf_token[:20]}...")
        print(f"QID: {qid}")
        
        # 3. POST with referrer
        post_data = {
            'csrf_token': csrf_token,
            'qid': qid,
            'selected_option': 'A',
            'elapsed': 30
        }
        
        headers = {
            'Referer': quiz_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        post_response = session.post(f"{base_url}/exam", data=post_data, headers=headers)
        print(f"POST Status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            post_soup = BeautifulSoup(post_response.text, 'html.parser')
            if "2/10" in post_soup.get_text():
                print("SUCCESS: 2/10 found!")
                return True
            else:
                print("Still 1/10")
                return False
        else:
            # Simple error output without Unicode
            error_text = post_response.text[:200].encode('ascii', 'ignore').decode('ascii')
            print(f"Error: {error_text}")
            return False
            
    except Exception as e:
        print(f"Exception: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    success = ultra_simple_test()
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")