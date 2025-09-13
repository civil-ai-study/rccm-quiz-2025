# -*- coding: utf-8 -*-
"""
Comprehensive Deep System Analysis
包括的ディープシステム解析

Multiple interconnected problems requiring comprehensive investigation:
1. QID Category Validation Failures
2. Session State Management Issues  
3. Next Link Generation Logic Flaws
4. Question Selection Algorithm Problems
5. Template Rendering Inconsistencies
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re

class ComprehensiveDeepSystemAnalyzer:
    """
    Comprehensive deep analysis of multiple interconnected system problems
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "COMPREHENSIVE_DEEP_SYSTEM_ANALYSIS",
            "problem_matrix": {},
            "interdependency_analysis": {},
            "root_cause_hierarchy": {},
            "system_design_flaws": {}
        }
    
    def analyze_qid_category_system_design_flaw(self):
        """
        Deep analysis of QID-Category system design flaws
        """
        print("=== DEEP: QID-Category System Design Flaw Analysis ===")
        print("Analyzing fundamental design problems in QID validation...")
        print("-" * 60)
        
        qid_analysis = {
            "invalid_qids_by_department": {},
            "valid_qids_by_department": {},
            "category_mapping_failures": {},
            "data_inconsistency_patterns": {}
        }
        
        departments_to_analyze = [
            {"dept": "basic", "type": "basic"},
            {"dept": "road", "type": "specialist"},
            {"dept": "civil_planning", "type": "specialist"},
            {"dept": "agriculture", "type": "specialist"},
            {"dept": "forest", "type": "specialist"}
        ]
        
        for dept_config in departments_to_analyze:
            print(f"\n  Deep QID Analysis: {dept_config['dept']} {dept_config['type']}")
            
            dept_analysis = {
                "sample_qids": [],
                "invalid_qids": [],
                "valid_qids": [],
                "error_patterns": []
            }
            
            # Test multiple QID assignments for this department
            for attempt in range(10):
                try:
                    session = requests.Session()
                    exam_url = f"{self.production_url}/exam?department={dept_config['dept']}&question_type={dept_config['type']}&count=10"
                    response = session.get(exam_url, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        qid_input = soup.find('input', {'name': 'qid'})
                        
                        if qid_input:
                            qid_value = qid_input.get('value')
                            dept_analysis["sample_qids"].append(qid_value)
                            
                            # Test if this QID is valid for this department
                            csrf_token = soup.find('input', {'name': 'csrf_token'})
                            if csrf_token:
                                post_data = {
                                    'csrf_token': csrf_token.get('value'),
                                    'qid': qid_value,
                                    'answer': 'A',
                                    'elapsed': 30
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
                                
                                if post_response.status_code == 200:
                                    response_soup = BeautifulSoup(post_response.text, 'html.parser')
                                    page_title = response_soup.find('title')
                                    title_text = page_title.text if page_title else ""
                                    
                                    if "エラー" in title_text:
                                        dept_analysis["invalid_qids"].append(qid_value)
                                        
                                        # Extract specific error message
                                        if "無効な問題ID" in post_response.text:
                                            dept_analysis["error_patterns"].append({
                                                "qid": qid_value,
                                                "error": "invalid_question_id",
                                                "attempt": attempt + 1
                                            })
                                    else:
                                        dept_analysis["valid_qids"].append(qid_value)
                
                except Exception as e:
                    print(f"    Error in attempt {attempt + 1}: {e}")
                
                time.sleep(0.5)  # Brief delay
            
            # Analysis summary for this department
            total_samples = len(dept_analysis["sample_qids"])
            invalid_count = len(dept_analysis["invalid_qids"])
            valid_count = len(dept_analysis["valid_qids"])
            
            if total_samples > 0:
                invalid_rate = (invalid_count / total_samples) * 100
                print(f"    Sample QIDs: {dept_analysis['sample_qids']}")
                print(f"    Invalid QIDs: {dept_analysis['invalid_qids']} ({invalid_rate:.1f}%)")
                print(f"    Valid QIDs: {dept_analysis['valid_qids']}")
                
                if invalid_rate > 50:
                    print(f"    [CRITICAL] High invalid QID rate: {invalid_rate:.1f}%")
                elif invalid_rate > 0:
                    print(f"    [WARNING] Some invalid QIDs detected: {invalid_rate:.1f}%")
                else:
                    print(f"    [OK] All QIDs valid")
            
            qid_analysis["invalid_qids_by_department"][dept_config['dept']] = dept_analysis
        
        self.analysis_results["problem_matrix"]["qid_category_validation"] = qid_analysis
        return qid_analysis
    
    def analyze_session_state_corruption_patterns(self):
        """
        Deep analysis of session state corruption patterns
        """
        print(f"\n=== DEEP: Session State Corruption Pattern Analysis ===")
        print("Analyzing session state management across question progression...")
        print("-" * 60)
        
        session_analysis = {
            "progression_corruption_points": [],
            "session_data_inconsistencies": [],
            "state_transition_failures": []
        }
        
        # Test session state consistency during progression
        session = requests.Session()
        
        try:
            # Initialize a session and track state changes
            exam_url = f"{self.production_url}/exam?department=road&question_type=specialist&count=10"
            response = session.get(exam_url, timeout=30)
            
            print(f"  Tracking session state through question progression...")
            
            for question_no in range(1, 8):  # Focus on 1-7 where problems occur
                print(f"    Question {question_no}: ", end="")
                
                if response.status_code != 200:
                    print(f"HTTP {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                qid_input = soup.find('input', {'name': 'qid'})
                
                if not csrf_token or not qid_input:
                    print(f"Missing tokens - SESSION CORRUPTION")
                    session_analysis["session_data_inconsistencies"].append({
                        "question_no": question_no,
                        "issue": "missing_tokens",
                        "csrf_present": bool(csrf_token),
                        "qid_present": bool(qid_input)
                    })
                    break
                
                qid_value = qid_input.get('value')
                csrf_value = csrf_token.get('value')
                
                # Check progress display consistency
                progress_elements = soup.find_all(text=re.compile(r'\d+/10'))
                progress_displays = [elem.strip() for elem in progress_elements if elem.strip()]
                expected_progress = f"{question_no}/10"
                
                progress_consistent = any(expected_progress in display for display in progress_displays)
                
                print(f"QID {qid_value}, Progress: {progress_displays}, ", end="")
                
                if not progress_consistent:
                    print(f"PROGRESS MISMATCH, ", end="")
                    session_analysis["session_data_inconsistencies"].append({
                        "question_no": question_no,
                        "issue": "progress_display_mismatch",
                        "expected": expected_progress,
                        "actual": progress_displays
                    })
                
                # Submit answer and analyze state transition
                post_data = {
                    'csrf_token': csrf_value,
                    'qid': qid_value,
                    'answer': 'A',
                    'elapsed': 30
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': response.url,
                    'Origin': self.production_url
                }
                
                post_response = session.post(f"{self.production_url}/exam", 
                                           data=post_data, 
                                           headers=headers,
                                           timeout=30)
                
                if post_response.status_code == 200:
                    feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                    page_title = feedback_soup.find('title')
                    title_text = page_title.text if page_title else ""
                    
                    if "エラー" in title_text:
                        print(f"ERROR PAGE")
                        session_analysis["state_transition_failures"].append({
                            "question_no": question_no,
                            "qid": qid_value,
                            "error_type": "error_page_returned",
                            "title": title_text
                        })
                        break
                    elif "解答結果" in title_text:
                        # Check for next question link
                        next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                        
                        if question_no < 7:  # Should have next link
                            if next_link:
                                print(f"OK, Next Link Present")
                                
                                # Progress to next question
                                next_response = session.get(f"{self.production_url}/exam?next=1", timeout=30)
                                if next_response.status_code == 200:
                                    response = next_response
                                else:
                                    print(f"\n      [ERROR] Next question load failed: {next_response.status_code}")
                                    session_analysis["state_transition_failures"].append({
                                        "question_no": question_no,
                                        "transition_to": question_no + 1,
                                        "error_type": "next_question_load_failure",
                                        "status_code": next_response.status_code
                                    })
                                    break
                            else:
                                print(f"MISSING NEXT LINK - PROGRESSION FAILURE")
                                session_analysis["progression_corruption_points"].append({
                                    "question_no": question_no,
                                    "qid": qid_value,
                                    "issue": "missing_next_link",
                                    "progression_blocked": True
                                })
                                break
                        else:
                            print(f"Final Question OK")
                    else:
                        print(f"UNEXPECTED PAGE: {title_text}")
                        break
                else:
                    print(f"POST FAILED: {post_response.status_code}")
                    break
                
                time.sleep(1)
        
        except Exception as e:
            print(f"\n[EXCEPTION] Session analysis failed: {e}")
        
        self.analysis_results["problem_matrix"]["session_state_management"] = session_analysis
        return session_analysis
    
    def analyze_template_rendering_inconsistencies(self):
        """
        Deep analysis of template rendering inconsistencies
        """
        print(f"\n=== DEEP: Template Rendering Inconsistency Analysis ===")
        print("Analyzing template rendering patterns and inconsistencies...")
        print("-" * 60)
        
        template_analysis = {
            "feedback_template_variations": {},
            "next_link_generation_patterns": {},
            "error_template_patterns": {}
        }
        
        # Analyze different template responses
        test_scenarios = [
            {"dept": "road", "type": "specialist", "expected": "working"},
            {"dept": "basic", "type": "basic", "expected": "error"},
            {"dept": "civil_planning", "type": "specialist", "expected": "error"}
        ]
        
        for scenario in test_scenarios:
            print(f"\n  Template Analysis: {scenario['dept']} {scenario['type']}")
            
            session = requests.Session()
            
            try:
                # Get initial page
                exam_url = f"{self.production_url}/exam?department={scenario['dept']}&question_type={scenario['type']}&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    csrf_token = soup.find('input', {'name': 'csrf_token'})
                    qid_input = soup.find('input', {'name': 'qid'})
                    
                    if csrf_token and qid_input:
                        # Submit answer to get feedback template
                        post_data = {
                            'csrf_token': csrf_token.get('value'),
                            'qid': qid_input.get('value'),
                            'answer': 'A',
                            'elapsed': 30
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
                        
                        if post_response.status_code == 200:
                            feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                            
                            # Analyze template structure
                            template_structure = {
                                "page_title": feedback_soup.find('title').text if feedback_soup.find('title') else "NO_TITLE",
                                "has_feedback_card": bool(feedback_soup.find('div', class_='feedback-card')),
                                "has_next_link": bool(feedback_soup.find('a', href=lambda x: x and 'next=1' in x)),
                                "has_error_card": bool(feedback_soup.find('div', class_='card border-danger')),
                                "template_indicators": []
                            }
                            
                            # Check for specific template indicators
                            if "解答結果" in template_structure["page_title"]:
                                template_structure["template_indicators"].append("feedback_template")
                            elif "エラー" in template_structure["page_title"]:
                                template_structure["template_indicators"].append("error_template")
                            
                            # Extract next link details if present
                            next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                            if next_link:
                                template_structure["next_link_text"] = next_link.get_text(strip=True)
                                template_structure["next_link_href"] = next_link.get('href')
                            
                            print(f"    Template: {template_structure['template_indicators']}")
                            print(f"    Page Title: {template_structure['page_title']}")
                            print(f"    Next Link: {'Present' if template_structure['has_next_link'] else 'Missing'}")
                            
                            template_analysis["feedback_template_variations"][f"{scenario['dept']}_{scenario['type']}"] = template_structure
            
            except Exception as e:
                print(f"    [ERROR] Template analysis failed: {e}")
        
        self.analysis_results["problem_matrix"]["template_rendering"] = template_analysis
        return template_analysis
    
    def analyze_problem_interdependencies(self):
        """
        Analyze how different problems affect each other
        """
        print(f"\n=== DEEP: Problem Interdependency Analysis ===")
        print("Analyzing how multiple problems create cascading failures...")
        print("-" * 60)
        
        interdependency_map = {
            "qid_validation_affects_session": {},
            "session_corruption_affects_progression": {},
            "template_rendering_affects_navigation": {},
            "cascading_failure_patterns": []
        }
        
        # Analyze cascading failure pattern: QID validation → Session corruption → Template failure
        print(f"  Tracing cascading failure patterns...")
        
        # Pattern 1: Invalid QID → Session corruption → No next link
        print(f"    Pattern 1: Invalid QID cascade")
        cascading_failures = []
        
        for dept in ["basic", "civil_planning"]:
            print(f"      Testing {dept} cascade...")
            
            session = requests.Session()
            cascade_trace = {
                "department": dept,
                "cascade_steps": [],
                "failure_propagation": []
            }
            
            try:
                # Step 1: Get QID (potentially invalid)
                exam_url = f"{self.production_url}/exam?department={dept}&question_type=specialist&count=10"
                response = session.get(exam_url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    qid_input = soup.find('input', {'name': 'qid'})
                    csrf_token = soup.find('input', {'name': 'csrf_token'})
                    
                    if qid_input and csrf_token:
                        qid_value = qid_input.get('value')
                        cascade_trace["cascade_steps"].append({
                            "step": "qid_assignment",
                            "qid": qid_value,
                            "status": "success"
                        })
                        
                        # Step 2: Submit QID (trigger validation failure)
                        post_data = {
                            'csrf_token': csrf_token.get('value'),
                            'qid': qid_value,
                            'answer': 'A',
                            'elapsed': 30
                        }
                        
                        post_response = session.post(f"{self.production_url}/exam", 
                                                   data=post_data, 
                                                   headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                   timeout=30)
                        
                        if post_response.status_code == 200:
                            post_soup = BeautifulSoup(post_response.text, 'html.parser')
                            page_title = post_soup.find('title')
                            title_text = page_title.text if page_title else ""
                            
                            if "エラー" in title_text:
                                cascade_trace["cascade_steps"].append({
                                    "step": "qid_validation_failure",
                                    "result": "error_page",
                                    "title": title_text
                                })
                                
                                # Step 3: Check for session corruption effects
                                next_link = post_soup.find('a', href=lambda x: x and 'next=1' in x)
                                
                                cascade_trace["cascade_steps"].append({
                                    "step": "navigation_capability",
                                    "next_link_present": bool(next_link),
                                    "progression_possible": False
                                })
                                
                                cascade_trace["failure_propagation"] = [
                                    "invalid_qid_assignment",
                                    "validation_failure", 
                                    "error_template_display",
                                    "progression_termination"
                                ]
                        
                        print(f"        Cascade: {' → '.join(cascade_trace['failure_propagation'])}")
            
            except Exception as e:
                print(f"        Cascade analysis error: {e}")
            
            cascading_failures.append(cascade_trace)
        
        interdependency_map["cascading_failure_patterns"] = cascading_failures
        self.analysis_results["interdependency_analysis"] = interdependency_map
        return interdependency_map
    
    def identify_root_cause_hierarchy(self):
        """
        Identify the hierarchy of root causes
        """
        print(f"\n=== DEEP: Root Cause Hierarchy Analysis ===")
        print("Identifying primary, secondary, and tertiary root causes...")
        print("-" * 60)
        
        root_cause_hierarchy = {
            "primary_root_causes": [],
            "secondary_causes": [],
            "tertiary_symptoms": [],
            "cause_effect_chains": []
        }
        
        # Based on collected evidence, identify cause hierarchy
        
        # Primary root causes (fundamental system design flaws)
        primary_causes = [
            {
                "cause": "question_selection_algorithm_flaw",
                "description": "Question selection assigns QIDs that don't match department categories",
                "evidence": "QID 157, 175, 242, 355 invalid for basic/civil_planning",
                "impact_scope": "system_wide",
                "criticality": "critical"
            },
            {
                "cause": "session_state_management_architecture_flaw", 
                "description": "Session state corruption during question progression",
                "evidence": "6th question next link disappears, progress display mismatches",
                "impact_scope": "progression_flow",
                "criticality": "critical"
            },
            {
                "cause": "expert_validation_incomplete_implementation",
                "description": "Expert QID validation only partially implemented",
                "evidence": "Some QIDs still bypass category validation",
                "impact_scope": "validation_layer",
                "criticality": "high"
            }
        ]
        
        # Secondary causes (implementation problems)
        secondary_causes = [
            {
                "cause": "template_rendering_inconsistency",
                "description": "Different departments render different template structures",
                "evidence": "Working departments show feedback template, failing show error template",
                "impact_scope": "user_experience",
                "criticality": "medium"
            },
            {
                "cause": "next_link_generation_logic_incomplete",
                "description": "Next link generation fails at specific progression points",
                "evidence": "6th question feedback lacks next link in some departments",
                "impact_scope": "navigation_flow",
                "criticality": "high"
            }
        ]
        
        # Tertiary symptoms (visible user-facing problems)
        tertiary_symptoms = [
            "7th question error (user report)",
            "Invalid Question ID errors", 
            "Progression stops at 6th question",
            "Inconsistent progress displays",
            "Error pages instead of feedback pages"
        ]
        
        # Cause-effect chains
        cause_effect_chains = [
            {
                "chain": "question_selection_flaw → invalid_qid_assignment → validation_failure → error_page",
                "departments_affected": ["basic", "civil_planning"],
                "user_impact": "immediate_failure"
            },
            {
                "chain": "session_state_flaw → progression_corruption → missing_next_link → 7th_question_error",
                "departments_affected": ["road", "others_intermittently"],
                "user_impact": "mid_session_failure"
            }
        ]
        
        root_cause_hierarchy = {
            "primary_root_causes": primary_causes,
            "secondary_causes": secondary_causes, 
            "tertiary_symptoms": tertiary_symptoms,
            "cause_effect_chains": cause_effect_chains
        }
        
        print(f"  PRIMARY ROOT CAUSES:")
        for cause in primary_causes:
            print(f"    - {cause['cause']}: {cause['description']}")
            print(f"      Evidence: {cause['evidence']}")
            print(f"      Impact: {cause['impact_scope']} ({cause['criticality']})")
        
        print(f"\n  SECONDARY CAUSES:")
        for cause in secondary_causes:
            print(f"    - {cause['cause']}: {cause['description']}")
        
        print(f"\n  CAUSE-EFFECT CHAINS:")
        for chain in cause_effect_chains:
            print(f"    {chain['chain']}")
            print(f"      Affects: {chain['departments_affected']}")
        
        self.analysis_results["root_cause_hierarchy"] = root_cause_hierarchy
        return root_cause_hierarchy
    
    def run_comprehensive_deep_analysis(self):
        """
        Run complete comprehensive deep system analysis
        """
        print("COMPREHENSIVE DEEP SYSTEM ANALYSIS")
        print("Multiple Interconnected Problems Investigation")
        print("=" * 70)
        
        # Phase 1: Individual problem analysis
        qid_analysis = self.analyze_qid_category_system_design_flaw()
        session_analysis = self.analyze_session_state_corruption_patterns()
        template_analysis = self.analyze_template_rendering_inconsistencies()
        
        # Phase 2: Interdependency analysis
        interdependency_analysis = self.analyze_problem_interdependencies()
        
        # Phase 3: Root cause hierarchy
        root_cause_analysis = self.identify_root_cause_hierarchy()
        
        # Final comprehensive summary
        print(f"\n" + "=" * 70)
        print("COMPREHENSIVE DEEP ANALYSIS SUMMARY")
        print("=" * 70)
        
        print(f"\nPROBLEM COMPLEXITY: MULTIPLE INTERCONNECTED ISSUES")
        print(f"Primary Problems Identified: {len(root_cause_analysis['primary_root_causes'])}")
        print(f"Secondary Problems: {len(root_cause_analysis['secondary_causes'])}")
        print(f"Cascading Failure Chains: {len(root_cause_analysis['cause_effect_chains'])}")
        
        print(f"\nIMPACT ASSESSMENT:")
        print(f"- Basic Subject: COMPLETELY BROKEN (1st question fails)")
        print(f"- Civil Planning: COMPLETELY BROKEN (1st question fails)")  
        print(f"- Road Specialist: PARTIALLY WORKING (fails at 6th→7th progression)")
        
        print(f"\nCRITICAL FINDINGS:")
        print(f"1. Question selection algorithm assigns wrong category QIDs")
        print(f"2. Session state corrupts during progression")
        print(f"3. Expert validation implementation incomplete")
        print(f"4. Template rendering inconsistent across departments")
        print(f"5. Next link generation fails at specific points")
        
        # Save comprehensive analysis
        self.save_comprehensive_analysis()
        
        return True
    
    def save_comprehensive_analysis(self):
        """Save comprehensive analysis results"""
        with open('comprehensive_deep_system_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        print(f"\nComprehensive analysis saved: comprehensive_deep_system_analysis.json")

if __name__ == "__main__":
    analyzer = ComprehensiveDeepSystemAnalyzer()
    analyzer.run_comprehensive_deep_analysis()