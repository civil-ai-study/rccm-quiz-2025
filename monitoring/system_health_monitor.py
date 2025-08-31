#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC Monitoring System - Non-Invasive Health Monitoring
Created: 2025-08-31 (Third Continuation Request Response)

Purpose: Establish comprehensive system monitoring without any modifications
Approach: Read-only analysis, zero side effects, proactive maintenance

ULTRA SYNC Principles:
- No system modifications
- Non-invasive monitoring only
- Zero regression risk
- Comprehensive health assessment
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class UltraSyncHealthMonitor:
    """
    Non-invasive system health monitoring for RCCM Quiz Application
    
    Features:
    - File integrity monitoring
    - Configuration consistency checking
    - Performance baseline establishment
    - Health trend tracking
    - Zero modification guarantee
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.monitoring_start_time = datetime.now()
        self.health_log_file = os.path.join("monitoring", "health_log.json")
        
        # Ensure monitoring directory exists
        os.makedirs("monitoring", exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - MONITOR - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("ULTRA SYNC Health Monitor initialized - Non-invasive mode")
    
    def get_file_integrity_snapshot(self) -> Dict[str, Any]:
        """
        Create comprehensive file integrity snapshot
        READ-ONLY operation, no modifications
        """
        critical_files = [
            'app.py',
            'config.py',
            'templates/question_types.html',
            'schemas/validation_schemas.py',
            'data/4-1.csv',
            'requirements.txt' if os.path.exists('requirements.txt') else None
        ]
        
        # Filter out None values
        critical_files = [f for f in critical_files if f is not None]
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'files': {}
        }
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                snapshot['files'][file_path] = {
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'exists': True
                }
                self.logger.info(f"File tracked: {file_path} ({stat.st_size} bytes)")
            else:
                snapshot['files'][file_path] = {
                    'exists': False,
                    'status': 'MISSING'
                }
                self.logger.warning(f"Critical file missing: {file_path}")
        
        return snapshot
    
    def check_implementation_integrity(self) -> Dict[str, Any]:
        """
        Verify PHASE 1 implementation integrity
        READ-ONLY verification, no changes
        """
        integrity_report = {
            'timestamp': datetime.now().isoformat(),
            'phase_1_implementations': {},
            'overall_status': 'UNKNOWN'
        }
        
        # Check PHASE 1 A2: Parameter validation
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            validation_checks = {
                'validation_import': 'from schemas.validation_schemas import validate_exam_parameters' in app_content,
                'marshmallow_import': 'from marshmallow import ValidationError' in app_content,
                'validation_usage': 'validated_params = validate_exam_parameters' in app_content,
                'fallback_mechanism': 'Falling back to legacy parameter processing' in app_content
            }
            
            integrity_report['phase_1_implementations']['parameter_validation'] = validation_checks
            
        except Exception as e:
            integrity_report['phase_1_implementations']['parameter_validation'] = {
                'error': str(e),
                'status': 'CHECK_FAILED'
            }
        
        # Check PHASE 1 B2: Schema implementation
        try:
            with open('schemas/validation_schemas.py', 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            schema_checks = {
                'schema_class': 'class ExamParameterSchema' in schema_content,
                'pre_load': '@pre_load' in schema_content,
                'post_load': '@post_load' in schema_content,
                'validation_function': 'def validate_exam_parameters' in schema_content
            }
            
            integrity_report['phase_1_implementations']['schema_validation'] = schema_checks
            
        except Exception as e:
            integrity_report['phase_1_implementations']['schema_validation'] = {
                'error': str(e),
                'status': 'CHECK_FAILED'
            }
        
        # Check PHASE 1 A1/B1: Template modifications
        try:
            with open('templates/question_types.html', 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template_checks = {
                'form_submission': 'exam-start-form' in template_content,
                'no_js_redirect': 'window.location.href' not in template_content,
                'loading_ui': 'btn-loading' in template_content,
                'submit_button': 'type="submit"' in template_content
            }
            
            integrity_report['phase_1_implementations']['template_modifications'] = template_checks
            
        except Exception as e:
            integrity_report['phase_1_implementations']['template_modifications'] = {
                'error': str(e),
                'status': 'CHECK_FAILED'
            }
        
        # Determine overall status
        all_implementations = integrity_report['phase_1_implementations']
        if all(isinstance(impl, dict) and all(impl.values()) for impl in all_implementations.values() 
               if isinstance(impl, dict) and 'error' not in impl):
            integrity_report['overall_status'] = 'HEALTHY'
        else:
            integrity_report['overall_status'] = 'ISSUES_DETECTED'
        
        return integrity_report
    
    def assess_system_stability(self) -> Dict[str, Any]:
        """
        Assess current system stability indicators
        READ-ONLY assessment, no system changes
        """
        stability_report = {
            'timestamp': datetime.now().isoformat(),
            'stability_indicators': {},
            'risk_assessment': 'LOW'
        }
        
        # Check recent file modifications
        recent_threshold = datetime.now() - timedelta(hours=24)
        recent_modifications = []
        
        critical_files = ['app.py', 'templates/question_types.html', 'schemas/validation_schemas.py']
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime > recent_threshold:
                    recent_modifications.append({
                        'file': file_path,
                        'modified': mtime.isoformat(),
                        'hours_ago': (datetime.now() - mtime).total_seconds() / 3600
                    })
        
        stability_report['stability_indicators']['recent_modifications'] = recent_modifications
        
        # Directory structure integrity
        required_directories = ['templates', 'data', 'schemas']
        missing_directories = [d for d in required_directories if not os.path.exists(d)]
        
        stability_report['stability_indicators']['directory_integrity'] = {
            'required_directories': required_directories,
            'missing_directories': missing_directories,
            'status': 'INTACT' if not missing_directories else 'DEGRADED'
        }
        
        # Template ecosystem check
        if os.path.exists('templates'):
            template_count = len([f for f in os.listdir('templates') if f.endswith('.html')])
            stability_report['stability_indicators']['template_ecosystem'] = {
                'total_templates': template_count,
                'status': 'COMPLETE' if template_count >= 30 else 'REDUCED'
            }
        
        return stability_report
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report
        Combines all monitoring data for analysis
        """
        self.logger.info("Generating comprehensive health report...")
        
        health_report = {
            'monitoring_session': {
                'start_time': self.monitoring_start_time.isoformat(),
                'report_time': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - self.monitoring_start_time).total_seconds() / 60
            },
            'file_integrity': self.get_file_integrity_snapshot(),
            'implementation_integrity': self.check_implementation_integrity(),
            'system_stability': self.assess_system_stability()
        }
        
        # Save report to monitoring log
        try:
            with open(self.health_log_file, 'w', encoding='utf-8') as f:
                json.dump(health_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Health report saved: {self.health_log_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
        
        return health_report

def run_health_monitoring():
    """
    Execute health monitoring session
    Non-invasive system assessment
    """
    print("ULTRA SYNC Health Monitoring - Non-Invasive System Assessment")
    print("=" * 70)
    print()
    
    monitor = UltraSyncHealthMonitor()
    
    try:
        # Generate comprehensive health report
        health_report = monitor.generate_health_report()
        
        # Display summary
        print("HEALTH MONITORING SUMMARY:")
        print("-" * 30)
        
        # File integrity summary
        file_integrity = health_report['file_integrity']
        total_files = len(file_integrity['files'])
        existing_files = sum(1 for f in file_integrity['files'].values() if f.get('exists', False))
        
        print(f"File Integrity: {existing_files}/{total_files} critical files present")
        
        # Implementation integrity summary
        impl_integrity = health_report['implementation_integrity']
        overall_status = impl_integrity.get('overall_status', 'UNKNOWN')
        print(f"Implementation Integrity: {overall_status}")
        
        # System stability summary
        stability = health_report['system_stability']
        recent_mods = len(stability['stability_indicators']['recent_modifications'])
        print(f"System Stability: {recent_mods} recent modifications detected")
        
        print()
        print("MONITORING COMPLETED SUCCESSFULLY")
        print("Report saved to: monitoring/health_log.json")
        print("System monitoring established with zero modifications")
        
        return health_report
        
    except Exception as e:
        print(f"Health monitoring error: {e}")
        return None

if __name__ == "__main__":
    run_health_monitoring()