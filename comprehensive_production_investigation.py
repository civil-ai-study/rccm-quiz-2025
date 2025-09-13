# -*- coding: utf-8 -*-
"""
Comprehensive Production Environment Investigation
Deep Analysis - Not Surface Level Testing
Based on user's specific request for thorough investigation
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re

class ProductionInvestigator:
    """
    Comprehensive investigation of production environment
    Focus: Deep analysis, not surface testing
    """
    
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.investigation_data = {
            "timestamp": datetime.now().isoformat(),
            "tests_performed": [],
            "errors_detected": [],
            "session_behavior": {},
            "server_responses": [],
            "code_version_indicators": []
        }
    
    def investigate_server_version(self):
        """
        Deep investigation of what code version is actually running
        """
        print("=== SERVER VERSION INVESTIGATION ===")
        
        try:
            # Test homepage for version indicators
            response = self.session.get(self.base_url)
            
            # Look for version indicators in HTML
            if "ULTRA SYNC26" in response.text:
                version_indicator = "ULTRA SYNC26 (OLD CODE)"
                self.investigation_data["code_version_indicators"].append({
                    "location": "homepage",
                    "indicator": "ULTRA SYNC26",
                    "status": "OLD_CODE_DETECTED"
                })
                print(f"CRITICAL: Old code detected - {version_indicator}")
            
            if "ULTRA SYNC段階26" in response.text:
                self.investigation_data["code_version_indicators"].append({
                    "location": "homepage", 
                    "indicator": "ULTRA SYNC段階26",
                    "status": "OLD_DEBUG_CODE"
                })
                print("CRITICAL: Old debug code detected")
            
            # Check for latest commit indicators
            if "702c793" in response.text:
                print("SUCCESS: Latest commit detected")
                self.investigation_data["code_version_indicators"].append({
                    "location": "homepage",
                    "indicator": "702c793",
                    "status": "LATEST_CODE"
                })
            
            self.investigation_data["server_responses"].append({
                "url": self.base_url,
                "status_code": response.status_code,
                "content_sample": response.text[:500]
            })
            
        except Exception as e:
            self.investigation_data["errors_detected"].append({
                "stage": "server_version_check",
                "error": str(e)
            })
            print(f"Error in version check: {e}")
    
    def investigate_session_initialization(self):
        """
        Deep investigation of session initialization behavior
        """
        print("\n=== SESSION INITIALIZATION INVESTIGATION ===")
        
        try:
            # Start fresh session
            self.session = requests.Session()
            
            # Test exam endpoint
            exam_url = f"{self.base_url}/exam?department=road&question_type=specialist&count=10"
            response = self.session.get(exam_url)
            
            print(f"Exam endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Analyze session cookies
                cookies = self.session.cookies.get_dict()
                print(f"Session cookies: {list(cookies.keys())}")
                
                # Check for CSRF token
                csrf_input = soup.find('input', {'name': 'csrf_token'})
                csrf_token = csrf_input.get('value') if csrf_input else None
                
                # Check for QID
                qid_input = soup.find('input', {'name': 'qid'})
                qid = qid_input.get('value') if qid_input else None
                
                # Look for progress indicators
                progress_text = soup.get_text()
                has_progress = "1/" in progress_text
                
                session_data = {
                    "cookies_set": len(cookies) > 0,
                    "csrf_token_present": csrf_token is not None,
                    "csrf_token_length": len(csrf_token) if csrf_token else 0,
                    "qid_present": qid is not None,
                    "qid_value": qid,
                    "progress_display": has_progress,
                    "content_sample": response.text[:300]
                }
                
                self.investigation_data["session_behavior"]["initialization"] = session_data
                
                print(f"CSRF Token: {'PRESENT' if csrf_token else 'MISSING'}")
                print(f"QID: {qid if qid else 'MISSING'}")
                print(f"Progress Display: {'PRESENT' if has_progress else 'MISSING'}")
                
                return csrf_token, qid
                
        except Exception as e:
            error_data = {
                "stage": "session_initialization", 
                "error": str(e)
            }
            self.investigation_data["errors_detected"].append(error_data)
            print(f"Session initialization error: {e}")
            return None, None
    
    def investigate_post_behavior(self, csrf_token, qid):
        """
        Deep investigation of POST request behavior
        This is where the 1st->2nd question progression fails
        """
        print("\n=== POST BEHAVIOR INVESTIGATION ===")
        
        if not csrf_token or not qid:
            print("Cannot test POST - missing tokens")
            return False
        
        try:
            # Prepare POST data
            post_data = {
                'csrf_token': csrf_token,
                'qid': qid,
                'selected_option': 'A',
                'elapsed': 45
            }
            
            # Prepare headers
            headers = {
                'Referer': f"{self.base_url}/exam?department=road&question_type=specialist&count=10",
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"POST Data: csrf_token={csrf_token[:20]}..., qid={qid}")
            
            # Execute POST request
            start_time = time.time()
            post_response = self.session.post(f"{self.base_url}/exam", 
                                            data=post_data, 
                                            headers=headers)
            response_time = time.time() - start_time
            
            print(f"POST Status: {post_response.status_code}")
            print(f"Response Time: {response_time:.2f} seconds")
            
            # Deep analysis of response
            post_analysis = {
                "status_code": post_response.status_code,
                "response_time": response_time,
                "headers": dict(post_response.headers),
                "content_sample": post_response.text[:500] if post_response.text else "NO_CONTENT"
            }
            
            self.investigation_data["session_behavior"]["post_request"] = post_analysis
            
            if post_response.status_code == 400:
                print("CRITICAL: POST 400 Error Detected")
                
                # Analyze error content
                error_content = post_response.text
                
                # Look for specific error indicators
                error_indicators = []
                if "ULTRA SYNC26" in error_content:
                    error_indicators.append("OLD_CODE_RUNNING")
                if "ULTRA SYNC段階26" in error_content:
                    error_indicators.append("OLD_DEBUG_VERSION")
                if "csrf" in error_content.lower():
                    error_indicators.append("CSRF_ERROR")
                if "invalid" in error_content.lower():
                    error_indicators.append("VALIDATION_ERROR")
                
                error_data = {
                    "stage": "post_request",
                    "status_code": 400,
                    "indicators": error_indicators,
                    "content_sample": error_content[:1000]
                }
                
                self.investigation_data["errors_detected"].append(error_data)
                
                print(f"Error indicators: {error_indicators}")
                return False
                
            elif post_response.status_code == 200:
                print("POST Success - Analyzing progression...")
                
                # Check if progression actually happened
                soup = BeautifulSoup(post_response.text, 'html.parser')
                progress_text = soup.get_text()
                
                if "2/10" in progress_text:
                    print("SUCCESS: Progression to question 2 confirmed")
                    return True
                elif "1/10" in progress_text:
                    print("FAILURE: Still stuck on question 1")
                    return False
                else:
                    print(f"UNCLEAR: Progress text = {progress_text[:100]}...")
                    return False
            
        except Exception as e:
            error_data = {
                "stage": "post_request",
                "error": str(e)
            }
            self.investigation_data["errors_detected"].append(error_data)
            print(f"POST investigation error: {e}")
            return False
    
    def investigate_deployment_status(self):
        """
        Investigate if latest code is actually deployed
        """
        print("\n=== DEPLOYMENT STATUS INVESTIGATION ===")
        
        try:
            # Check if we can find evidence of latest commits
            response = self.session.get(self.base_url)
            
            # Look for deployment indicators
            deployment_indicators = {
                "ultra_sync_26_present": "ULTRA SYNC26" in response.text,
                "latest_commit_present": "702c793" in response.text,
                "expert_fixes_present": "ULTRA SYNC]" in response.text,
                "old_debug_present": "段階26" in response.text
            }
            
            self.investigation_data["deployment_status"] = deployment_indicators
            
            print("Deployment Status Analysis:")
            for indicator, present in deployment_indicators.items():
                status = "DETECTED" if present else "NOT_FOUND"
                print(f"  {indicator}: {status}")
            
            # Determine deployment status
            if deployment_indicators["ultra_sync_26_present"]:
                print("CONCLUSION: OLD CODE IS RUNNING IN PRODUCTION")
                return "OLD_CODE"
            elif deployment_indicators["latest_commit_present"]:
                print("CONCLUSION: LATEST CODE IS DEPLOYED")  
                return "LATEST_CODE"
            else:
                print("CONCLUSION: DEPLOYMENT STATUS UNCLEAR")
                return "UNCLEAR"
                
        except Exception as e:
            print(f"Deployment investigation error: {e}")
            return "ERROR"
    
    def run_comprehensive_investigation(self):
        """
        Run complete investigation following user's requirements
        """
        print("Starting Comprehensive Production Investigation")
        print("Focus: Deep analysis, not surface level testing")
        print("=" * 60)
        
        # Phase 1: Server version investigation
        self.investigate_server_version()
        
        # Phase 2: Session behavior investigation  
        csrf_token, qid = self.investigate_session_initialization()
        
        # Phase 3: POST behavior investigation (the core issue)
        progression_success = self.investigate_post_behavior(csrf_token, qid)
        
        # Phase 4: Deployment status investigation
        deployment_status = self.investigate_deployment_status()
        
        # Compile final results
        self.investigation_data["final_results"] = {
            "session_initialization_success": csrf_token is not None and qid is not None,
            "post_request_success": progression_success,
            "deployment_status": deployment_status,
            "core_issue_identified": not progression_success,
            "requires_deployment": deployment_status == "OLD_CODE"
        }
        
        return self.investigation_data
    
    def save_investigation_results(self):
        """
        Save comprehensive investigation results
        """
        with open('comprehensive_production_investigation.json', 'w', encoding='utf-8') as f:
            json.dump(self.investigation_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nInvestigation results saved to comprehensive_production_investigation.json")

if __name__ == "__main__":
    investigator = ProductionInvestigator()
    results = investigator.run_comprehensive_investigation()
    investigator.save_investigation_results()
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE INVESTIGATION SUMMARY")
    print("=" * 60)
    
    final_results = results["final_results"]
    
    print(f"Session Initialization: {'SUCCESS' if final_results['session_initialization_success'] else 'FAILED'}")
    print(f"POST Request Success: {'SUCCESS' if final_results['post_request_success'] else 'FAILED'}")
    print(f"Deployment Status: {final_results['deployment_status']}")
    print(f"Core Issue Present: {'YES' if final_results['core_issue_identified'] else 'NO'}")
    print(f"Deployment Required: {'YES' if final_results['requires_deployment'] else 'NO'}")
    
    # Summary recommendation
    if final_results["requires_deployment"]:
        print("\n🚨 CRITICAL FINDING: Old code is running in production")
        print("   REQUIRED ACTION: Manual deployment needed on Render.com")
    elif final_results["core_issue_identified"]:
        print("\n🚨 CRITICAL FINDING: 1st->2nd progression still failing")
        print("   REQUIRED ACTION: Additional code fixes needed")
    else:
        print("\n✅ INVESTIGATION COMPLETE: System appears functional")