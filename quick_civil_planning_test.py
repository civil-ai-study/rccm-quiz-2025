# -*- coding: utf-8 -*-
"""
Quick Civil Planning QID Fix Test
Civil Planning QID修正の緊急検証
"""

import requests
from bs4 import BeautifulSoup

def test_civil_planning_qid_fix():
    """
    Quick test for Civil Planning QID fix
    """
    print("Quick Civil Planning QID Fix Test")
    print("Testing QID 336 acceptance...")
    print("=" * 40)
    
    session = requests.Session()
    
    try:
        # Test civil_planning specialist
        exam_url = "https://rccm-quiz-2025.onrender.com/exam?department=civil_planning&question_type=specialist&count=10"
        response = session.get(exam_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            qid_input = soup.find('input', {'name': 'qid'})
            
            if qid_input:
                qid_value = qid_input.get('value')
                qid = int(qid_value)
                
                print(f"QID assigned: {qid}")
                
                # Check if page shows error or normal question
                page_title = soup.find('title')
                title_text = page_title.text if page_title else ""
                
                if "エラー" in title_text:
                    print(f"[FAIL] Still getting error page: {title_text}")
                    return False
                else:
                    print(f"[SUCCESS] Normal question page displayed")
                    print(f"[SUCCESS] QID {qid} is now accepted")
                    return True
            else:
                print(f"[ERROR] No QID found in response")
                return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return False

if __name__ == "__main__":
    success = test_civil_planning_qid_fix()
    exit(0 if success else 1)