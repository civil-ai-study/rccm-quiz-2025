# -*- coding: utf-8 -*-
"""
STAGE 3: 本番環境デプロイ前の最終検証
Production Environment Pre-Deployment Verification
慎重な本番環境状況確認とローカル修正の最終検証
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class Stage3ProductionVerifier:
    """
    STAGE 3: 本番環境デプロイ前の最終検証
    - Production environment current status verification
    - Local fixes final confirmation
    - Deployment readiness assessment
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.local_url = "http://127.0.0.1:5003"
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "STAGE_3_PRODUCTION_VERIFICATION",
            "production_status": {},
            "local_status": {},
            "deployment_readiness": {},
            "comparison_results": {}
        }
    
    def verify_production_current_status(self):
        """
        Verify current production environment status
        Check if the 1st->2nd progression issue still exists
        """
        print("=== STAGE 3.1: PRODUCTION ENVIRONMENT STATUS ===")
        print("Verifying current production environment status...")
        print("-" * 50)
        
        session = requests.Session()
        
        try:
            # Test production environment
            print("Testing production environment progression...")
            
            # Initialize exam session
            exam_url = f"{self.production_url}/exam?department=road&question_type=specialist&count=10"
            response = session.get(exam_url, timeout=30)
            
            if response.status_code != 200:
                print(f"[ERROR] Production initialization failed: {response.status_code}")
                self.verification_results["production_status"]["initialization"] = "FAILED"
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_token or not qid_input:
                print("[ERROR] Production missing CSRF token or QID")
                self.verification_results["production_status"]["initialization"] = "MISSING_TOKENS"
                return False
            
            csrf_value = csrf_token.get('value')
            qid_value = qid_input.get('value')
            
            print(f"[OK] Production initialized: QID={qid_value}")
            
            # Submit answer to test progression
            post_data = {
                'csrf_token': csrf_value,
                'qid': qid_value,
                'answer': 'A',
                'elapsed': 45
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': exam_url,
                'Origin': self.production_url
            }
            
            post_response = session.post(f"{self.production_url}/exam", 
                                       data=post_data, 
                                       headers=headers,
                                       timeout=30)
            
            print(f"Production POST Status: {post_response.status_code}")
            
            if post_response.status_code == 400:
                print("[CONFIRMED] Production still has POST 400 errors (1st->2nd progression issue)")
                self.verification_results["production_status"]["progression_issue"] = "CONFIRMED"
                return True  # Issue confirmed = ready for deployment
            elif post_response.status_code == 200:
                print("[UNEXPECTED] Production POST 200 - issue may already be fixed")
                self.verification_results["production_status"]["progression_issue"] = "POSSIBLY_FIXED"
                return True
            else:
                print(f"[ERROR] Unexpected production status: {post_response.status_code}")
                self.verification_results["production_status"]["progression_issue"] = "UNKNOWN"
                return False
                
        except Exception as e:
            print(f"[ERROR] Production verification failed: {e}")
            self.verification_results["production_status"]["error"] = str(e)
            return False
    
    def verify_local_fixes_final(self):
        """
        Final verification of local fixes
        Ensure local environment is working perfectly
        """
        print("\n=== STAGE 3.2: LOCAL FIXES FINAL VERIFICATION ===")
        print("Final verification of local expert modifications...")
        print("-" * 50)
        
        session = requests.Session()
        
        try:
            # Test local environment multiple times for stability
            success_count = 0
            test_iterations = 3
            
            for i in range(test_iterations):
                print(f"Local Test Iteration {i+1}/{test_iterations}...")
                
                # Initialize exam session
                exam_url = f"{self.local_url}/exam?department=road&question_type=specialist&count=10"
                response = session.get(exam_url)
                
                if response.status_code != 200:
                    print(f"[ERROR] Local iteration {i+1} failed: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    print(f"[ERROR] Local iteration {i+1} missing tokens")
                    continue
                
                csrf_value = csrf_token.get('value')
                qid_value = qid_input.get('value')
                
                # Submit answer
                post_data = {
                    'csrf_token': csrf_value,
                    'qid': qid_value,
                    'answer': 'A',
                    'elapsed': 45
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': exam_url,
                    'Origin': self.local_url
                }
                
                post_response = session.post(f"{self.local_url}/exam", 
                                           data=post_data, 
                                           headers=headers)
                
                if post_response.status_code == 200:
                    # Check for progression capability
                    feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                    next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                    
                    if next_link:
                        next_response = session.get(f"{self.local_url}/exam?next=1")
                        if next_response.status_code == 200:
                            next_soup = BeautifulSoup(next_response.text, 'html.parser')
                            next_qid = next_soup.find('input', {'name': 'qid'})
                            
                            if next_qid and next_qid.get('value') != qid_value:
                                print(f"[OK] Local iteration {i+1}: {qid_value} -> {next_qid.get('value')}")
                                success_count += 1
                            else:
                                print(f"[ERROR] Local iteration {i+1}: progression failed")
                        else:
                            print(f"[ERROR] Local iteration {i+1}: next question failed")
                    else:
                        print(f"[ERROR] Local iteration {i+1}: no next link")
                else:
                    print(f"[ERROR] Local iteration {i+1}: POST {post_response.status_code}")
                
                time.sleep(1)  # Brief delay between tests
            
            stability_percentage = (success_count / test_iterations) * 100
            print(f"\nLocal Stability: {success_count}/{test_iterations} ({stability_percentage:.1f}%)")
            
            if success_count == test_iterations:
                print("[SUCCESS] Local fixes are 100% stable")
                self.verification_results["local_status"]["stability"] = "PERFECT"
                return True
            elif success_count >= test_iterations * 0.8:
                print("[GOOD] Local fixes are mostly stable")
                self.verification_results["local_status"]["stability"] = "GOOD"
                return True
            else:
                print("[ERROR] Local fixes are unstable")
                self.verification_results["local_status"]["stability"] = "UNSTABLE"
                return False
                
        except Exception as e:
            print(f"[ERROR] Local verification failed: {e}")
            self.verification_results["local_status"]["error"] = str(e)
            return False
    
    def assess_deployment_readiness(self):
        """
        Assess overall deployment readiness
        """
        print("\n=== STAGE 3.3: DEPLOYMENT READINESS ASSESSMENT ===")
        print("Assessing deployment readiness based on verification results...")
        print("-" * 50)
        
        production_status = self.verification_results.get("production_status", {})
        local_status = self.verification_results.get("local_status", {})
        
        # Check if production has the issue
        production_has_issue = production_status.get("progression_issue") == "CONFIRMED"
        
        # Check if local fixes are stable
        local_fixes_stable = local_status.get("stability") in ["PERFECT", "GOOD"]
        
        # Deployment readiness criteria
        deployment_ready = production_has_issue and local_fixes_stable
        
        if deployment_ready:
            print("[READY] Deployment is recommended")
            print("  - Production has confirmed progression issue")
            print("  - Local fixes are stable and working")
            self.verification_results["deployment_readiness"]["status"] = "READY"
            self.verification_results["deployment_readiness"]["recommendation"] = "DEPLOY"
        else:
            print("[NOT READY] Deployment not recommended")
            if not production_has_issue:
                print("  - Production issue status unclear")
            if not local_fixes_stable:
                print("  - Local fixes are not stable enough")
            self.verification_results["deployment_readiness"]["status"] = "NOT_READY"
            self.verification_results["deployment_readiness"]["recommendation"] = "DO_NOT_DEPLOY"
        
        return deployment_ready
    
    def run_stage3_verification(self):
        """
        Run complete Stage 3 verification
        """
        print("ULTRA SYNC STAGE 3: Production Environment Pre-Deployment Verification")
        print("慎重な本番環境状況確認とローカル修正の最終検証")
        print("=" * 70)
        
        # Phase 1: Production status verification
        production_verified = self.verify_production_current_status()
        
        # Phase 2: Local fixes final verification
        local_verified = self.verify_local_fixes_final()
        
        # Phase 3: Deployment readiness assessment
        deployment_ready = self.assess_deployment_readiness()
        
        # Final results
        print("\n" + "=" * 70)
        print("STAGE 3 VERIFICATION RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"Production Status Verified: {'YES' if production_verified else 'NO'}")
        print(f"Local Fixes Verified: {'YES' if local_verified else 'NO'}")
        print(f"Deployment Ready: {'YES' if deployment_ready else 'NO'}")
        
        overall_success = production_verified and local_verified and deployment_ready
        
        if overall_success:
            print("\n[STAGE 3 COMPLETE] Ready to proceed to STAGE 4 deployment")
        else:
            print("\n[STAGE 3 INCOMPLETE] Additional work needed before deployment")
        
        return overall_success
    
    def save_results(self):
        """Save verification results"""
        with open('stage3_production_verification.json', 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        print("\nVerification results saved to stage3_production_verification.json")

if __name__ == "__main__":
    verifier = Stage3ProductionVerifier()
    success = verifier.run_stage3_verification()
    verifier.save_results()
    
    exit(0 if success else 1)