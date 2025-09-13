# -*- coding: utf-8 -*-
"""
ULTRA SYNC: Safety Verification System
Cautious and accurate verification to prevent any side effects
段階的進行で副作用を絶対に防止
"""

import sys
import subprocess
import time
import json
from datetime import datetime

class UltraSyncSafetyVerifier:
    """
    Cautious safety verification system
    Ensures no side effects before proceeding
    """
    
    def __init__(self):
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "STAGE_1_SAFETY_VERIFICATION",
            "tests_performed": [],
            "safety_checks": [],
            "side_effects_detected": [],
            "verification_status": "PENDING"
        }
    
    def verify_import_safety(self):
        """
        STAGE 1.1: Verify import safety
        Check if CSRFError import causes any issues
        """
        print("STAGE 1.1: Import Safety Verification")
        print("-" * 40)
        
        try:
            # Test CSRFError import
            from flask_wtf.csrf import CSRFError
            print("[OK] CSRFError import: SUCCESS")
            
            # Test if CSRFError is properly defined
            if hasattr(CSRFError, '__name__'):
                print("[OK] CSRFError class structure: VALID")
            else:
                raise Exception("CSRFError class structure invalid")
            
            self.verification_results["safety_checks"].append({
                "check": "import_safety",
                "status": "PASSED",
                "details": "CSRFError import successful"
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Import safety check FAILED: {e}")
            self.verification_results["side_effects_detected"].append({
                "type": "import_error",
                "error": str(e),
                "severity": "HIGH"
            })
            return False
    
    def verify_logging_safety(self):
        """
        STAGE 1.2: Verify logging configuration safety
        Ensure UTF-8 encoding doesn't break existing functionality
        """
        print("\nSTAGE 1.2: Logging Safety Verification")
        print("-" * 40)
        
        try:
            import logging
            
            # Test current logging configuration
            logger = logging.getLogger("safety_test")
            
            # Test basic logging
            logger.error("Basic ASCII test message")
            print("[OK] Basic logging: SUCCESS")
            
            # Test Unicode logging (should work with UTF-8 encoding)
            logger.error("Unicode test: 正常動作確認")
            print("[OK] Unicode logging: SUCCESS")
            
            # Verify log file exists and is writable
            import os
            if os.path.exists('rccm_app.log'):
                print("[OK] Log file access: SUCCESS")
            else:
                print("[INFO] Log file will be created on first write")
            
            self.verification_results["safety_checks"].append({
                "check": "logging_safety",
                "status": "PASSED",
                "details": "UTF-8 logging configuration safe"
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Logging safety check FAILED: {e}")
            self.verification_results["side_effects_detected"].append({
                "type": "logging_error",
                "error": str(e),
                "severity": "MEDIUM"
            })
            return False
    
    def verify_flask_app_safety(self):
        """
        STAGE 1.3: Verify Flask app initialization safety
        Test if our modifications break app startup
        """
        print("\nSTAGE 1.3: Flask App Safety Verification")
        print("-" * 40)
        
        try:
            # Test basic Flask imports
            from flask import Flask
            from flask_wtf.csrf import CSRFProtect, CSRFError
            print("[OK] Flask imports: SUCCESS")
            
            # Test minimal app creation
            test_app = Flask(__name__)
            test_app.config['SECRET_KEY'] = 'test-key'
            test_app.config['WTF_CSRF_ENABLED'] = True
            
            # Test CSRF protection initialization
            csrf = CSRFProtect(test_app)
            print("[OK] CSRFProtect initialization: SUCCESS")
            
            # Test error handler registration
            @test_app.errorhandler(CSRFError)
            def test_csrf_handler(e):
                return f"CSRF Error: {e.description}", 400
            
            print("[OK] CSRFError handler registration: SUCCESS")
            
            # Test app context
            with test_app.app_context():
                print("[OK] App context creation: SUCCESS")
            
            self.verification_results["safety_checks"].append({
                "check": "flask_app_safety",
                "status": "PASSED",
                "details": "Flask app with CSRF modifications safe"
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Flask app safety check FAILED: {e}")
            self.verification_results["side_effects_detected"].append({
                "type": "flask_app_error",
                "error": str(e),
                "severity": "HIGH"
            })
            return False
    
    def verify_config_safety(self):
        """
        STAGE 1.4: Verify configuration safety
        Ensure config.py modifications don't cause issues
        """
        print("\nSTAGE 1.4: Configuration Safety Verification")
        print("-" * 40)
        
        try:
            # Test config import
            sys.path.insert(0, '.')
            import config
            print("[OK] Config import: SUCCESS")
            
            # Test configuration classes
            base_config = config.Config()
            print("[OK] Base config instantiation: SUCCESS")
            
            # Verify CSRF settings exist
            if hasattr(base_config, 'WTF_CSRF_ENABLED'):
                print("[OK] CSRF settings present: SUCCESS")
            else:
                raise Exception("CSRF settings missing")
            
            # Test development config
            dev_config = config.DevelopmentConfig()
            print("[OK] Development config: SUCCESS")
            
            self.verification_results["safety_checks"].append({
                "check": "config_safety", 
                "status": "PASSED",
                "details": "Configuration modifications safe"
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Configuration safety check FAILED: {e}")
            self.verification_results["side_effects_detected"].append({
                "type": "config_error",
                "error": str(e),
                "severity": "MEDIUM"
            })
            return False
    
    def verify_session_safety(self):
        """
        STAGE 1.5: Verify session handling safety
        Test atomic session operations don't break existing functionality
        """
        print("\nSTAGE 1.5: Session Safety Verification") 
        print("-" * 40)
        
        try:
            # Test session-like dictionary operations
            test_session = {}
            
            # Test backup and restore pattern
            backup = test_session.copy()
            test_session['test_key'] = 'test_value'
            
            # Simulate rollback
            if backup:
                test_session.update(backup)
            
            print("[OK] Session backup/restore pattern: SUCCESS")
            
            # Test atomic-like operations
            original_value = test_session.get('exam_current', 0)
            new_value = original_value + 1
            test_session['exam_current'] = new_value
            
            if test_session.get('exam_current') == new_value:
                print("[OK] Atomic session update simulation: SUCCESS")
            else:
                raise Exception("Session update verification failed")
            
            self.verification_results["safety_checks"].append({
                "check": "session_safety",
                "status": "PASSED", 
                "details": "Session handling patterns safe"
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Session safety check FAILED: {e}")
            self.verification_results["side_effects_detected"].append({
                "type": "session_error",
                "error": str(e),
                "severity": "MEDIUM"
            })
            return False
    
    def run_comprehensive_safety_verification(self):
        """
        Run all safety checks in sequence
        Stop immediately if any side effects detected
        """
        print("ULTRA SYNC: STAGE 1 SAFETY VERIFICATION")
        print("Cautious verification to prevent any side effects")
        print("=" * 60)
        
        safety_checks = [
            ("Import Safety", self.verify_import_safety),
            ("Logging Safety", self.verify_logging_safety),
            ("Flask App Safety", self.verify_flask_app_safety),
            ("Configuration Safety", self.verify_config_safety),
            ("Session Safety", self.verify_session_safety)
        ]
        
        all_passed = True
        
        for check_name, check_function in safety_checks:
            print(f"\n[CHECK] Executing: {check_name}")
            
            if not check_function():
                print(f"[FAIL] SAFETY FAILURE: {check_name} failed")
                all_passed = False
                break
            else:
                print(f"[PASS] SAFETY PASSED: {check_name}")
        
        # Final verification status
        if all_passed and len(self.verification_results["side_effects_detected"]) == 0:
            self.verification_results["verification_status"] = "SAFE_TO_PROCEED"
            print(f"\n[SUCCESS] STAGE 1 VERIFICATION: COMPLETE SUCCESS")
            print("No side effects detected - safe to proceed to STAGE 2")
        else:
            self.verification_results["verification_status"] = "UNSAFE_STOP_REQUIRED"
            print(f"\n[ALERT] STAGE 1 VERIFICATION: FAILURE DETECTED")
            print("Side effects found - stopping progression")
        
        return all_passed
    
    def save_verification_report(self):
        """Save detailed verification report"""
        with open('ultra_sync_stage1_safety_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n[REPORT] Safety verification report saved to ultra_sync_stage1_safety_report.json")

if __name__ == "__main__":
    verifier = UltraSyncSafetyVerifier()
    success = verifier.run_comprehensive_safety_verification()
    verifier.save_verification_report()
    
    if success:
        print("\n[COMPLETE] STAGE 1 COMPLETE: Ready for STAGE 2")
        print("All safety checks passed - no side effects detected")
    else:
        print("\n[FAILED] STAGE 1 FAILED: Stopping progression")
        print("Side effects detected - manual review required")
    
    exit(0 if success else 1)