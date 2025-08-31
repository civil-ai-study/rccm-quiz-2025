#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

def check_error_response():
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # Get question page
    response = session.get(f"{base_url}/exam?department=env&question_type=specialist&category=all&count=10")
    
    # Extract form data
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', id='questionForm')
    
    post_data = {'answer': 'A'}
    for hidden in form.find_all('input', type='hidden'):
        name = hidden.get('name')
        value = hidden.get('value')
        if name and value:
            post_data[name] = value
    
    # Submit POST
    post_response = session.post(f"{base_url}/exam", data=post_data)
    
    print(f"Status: {post_response.status_code}")
    print(f"Content Length: {len(post_response.text)}")
    print("Response content:")
    print("="*50)
    print(post_response.text)

if __name__ == "__main__":
    check_error_response()