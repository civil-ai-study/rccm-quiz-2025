# -*- coding: utf-8 -*-
"""
Deep Data Validation - Production Environment Issue Investigation
civil_planningの"無効な問題ID"エラーの根本原因調査
"""

import os
import pandas as pd
import glob
import json
from datetime import datetime

class DeepDataValidator:
    """
    Deep Data Validation for civil_planning question availability
    """
    
    def __init__(self):
        self.data_dir = "data"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "DEEP_DATA_VALIDATION",
            "csv_analysis": {},
            "civil_planning_investigation": {},
            "department_mapping_validation": {}
        }
    
    def analyze_csv_data_availability(self):
        """
        Analyze CSV data availability for civil_planning
        """
        print("=== Deep CSV Data Analysis ===")
        print("Investigating civil_planning question availability...")
        print("-" * 50)
        
        csv_files = glob.glob(os.path.join(self.data_dir, "4-2_*.csv"))
        total_civil_planning = 0
        csv_analysis = {}
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                print(f"\nAnalyzing: {csv_file}")
                print(f"  Total rows: {len(df)}")
                
                # Check for civil_planning related categories
                if 'category' in df.columns:
                    categories = df['category'].unique()
                    print(f"  Categories found: {list(categories)}")
                    
                    # Look for river-related categories (civil_planning maps to river)
                    river_patterns = ['河川', '砂防', '海岸', '海洋']
                    matching_categories = []
                    river_data = pd.DataFrame()
                    
                    for category in categories:
                        if any(pattern in str(category) for pattern in river_patterns):
                            matching_categories.append(category)
                            category_data = df[df['category'] == category]
                            river_data = pd.concat([river_data, category_data])
                    
                    print(f"  River-related categories: {matching_categories}")
                    print(f"  River questions count: {len(river_data)}")
                    
                    if len(river_data) > 0:
                        print(f"  Sample IDs: {list(river_data['id'].head())}")
                        total_civil_planning += len(river_data)
                    
                    csv_analysis[csv_file] = {
                        "total_rows": len(df),
                        "categories": list(categories),
                        "river_categories": matching_categories,
                        "river_questions": len(river_data),
                        "sample_ids": list(river_data['id'].head()) if len(river_data) > 0 else []
                    }
                else:
                    print(f"  [ERROR] No 'category' column found!")
                    csv_analysis[csv_file] = {"error": "No category column"}
                    
            except Exception as e:
                print(f"  [ERROR] Failed to read {csv_file}: {e}")
                csv_analysis[csv_file] = {"error": str(e)}
        
        print(f"\nTotal civil_planning (river) questions across all CSVs: {total_civil_planning}")
        self.validation_results["csv_analysis"] = csv_analysis
        self.validation_results["civil_planning_investigation"]["total_available"] = total_civil_planning
        
        return total_civil_planning > 0
    
    def test_emergency_get_questions(self):
        """
        Test the emergency_get_questions function for civil_planning
        """
        print(f"\n=== Testing emergency_get_questions Function ===")
        print("Testing civil_planning specialist question loading...")
        print("-" * 50)
        
        try:
            # Import the function from app.py
            import sys
            sys.path.append('.')
            
            # Try to import and test
            from app import emergency_get_questions
            
            print("Testing: emergency_get_questions('civil_planning', 'specialist', 10)")
            questions = emergency_get_questions('civil_planning', 'specialist', 10)
            
            print(f"Questions returned: {len(questions)}")
            
            if len(questions) > 0:
                print(f"Sample question IDs: {[q.get('id') for q in questions[:5]]}")
                print(f"Sample categories: {[q.get('category') for q in questions[:3]]}")
                
                # Check if QID 133 exists
                qid_133_found = any(q.get('id') == 133 for q in questions)
                print(f"QID 133 found in results: {qid_133_found}")
                
                self.validation_results["civil_planning_investigation"]["function_test"] = {
                    "questions_returned": len(questions),
                    "sample_ids": [q.get('id') for q in questions[:5]],
                    "qid_133_found": qid_133_found,
                    "status": "SUCCESS"
                }
            else:
                print("[ERROR] No questions returned!")
                self.validation_results["civil_planning_investigation"]["function_test"] = {
                    "questions_returned": 0,
                    "status": "NO_QUESTIONS"
                }
                
        except Exception as e:
            print(f"[ERROR] Function test failed: {e}")
            self.validation_results["civil_planning_investigation"]["function_test"] = {
                "error": str(e),
                "status": "FAILED"
            }
    
    def validate_department_mapping(self):
        """
        Validate department mapping for civil_planning
        """
        print(f"\n=== Department Mapping Validation ===")
        print("Validating civil_planning -> Japanese category mapping...")
        print("-" * 50)
        
        try:
            # Check config.py for department mapping
            if os.path.exists('config.py'):
                with open('config.py', 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                print("Found config.py, analyzing department mapping...")
                
                # Look for civil_planning mapping
                if 'civil_planning' in config_content:
                    print("civil_planning found in config.py")
                    
                    # Extract the mapping line
                    lines = config_content.split('\n')
                    mapping_lines = [line for line in lines if 'civil_planning' in line]
                    
                    for line in mapping_lines:
                        print(f"  Mapping line: {line.strip()}")
                    
                    self.validation_results["department_mapping_validation"]["config_found"] = True
                    self.validation_results["department_mapping_validation"]["mapping_lines"] = mapping_lines
                else:
                    print("[WARNING] civil_planning not found in config.py")
                    self.validation_results["department_mapping_validation"]["civil_planning_in_config"] = False
            else:
                print("[ERROR] config.py not found!")
                self.validation_results["department_mapping_validation"]["config_exists"] = False
                
        except Exception as e:
            print(f"[ERROR] Department mapping validation failed: {e}")
            self.validation_results["department_mapping_validation"]["error"] = str(e)
    
    def investigate_qid_133_specifically(self):
        """
        Specifically investigate QID 133 issue
        """
        print(f"\n=== QID 133 Specific Investigation ===")
        print("Investigating why QID 133 returns 'Invalid Question ID' error...")
        print("-" * 50)
        
        # Search all CSVs for ID 133
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        qid_133_locations = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                if 'id' in df.columns:
                    id_133_rows = df[df['id'] == 133]
                    if len(id_133_rows) > 0:
                        qid_133_locations.append({
                            "file": csv_file,
                            "rows": len(id_133_rows),
                            "categories": list(id_133_rows['category'].unique()) if 'category' in df.columns else []
                        })
                        print(f"Found ID 133 in {csv_file}: {len(id_133_rows)} rows")
                        if 'category' in df.columns:
                            print(f"  Categories: {list(id_133_rows['category'].unique())}")
                            
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
        
        if qid_133_locations:
            print(f"\nQID 133 found in {len(qid_133_locations)} files")
            self.validation_results["civil_planning_investigation"]["qid_133_locations"] = qid_133_locations
        else:
            print("\n[CRITICAL] QID 133 not found in any CSV files!")
            self.validation_results["civil_planning_investigation"]["qid_133_found"] = False
    
    def run_comprehensive_validation(self):
        """
        Run comprehensive data validation
        """
        print("Deep Data Validation - Production Environment Issue Investigation")
        print("civil_planningの\"無効な問題ID\"エラーの根本原因調査")
        print("=" * 70)
        
        # Phase 1: CSV Data Analysis
        csv_data_available = self.analyze_csv_data_availability()
        
        # Phase 2: Function Testing
        self.test_emergency_get_questions()
        
        # Phase 3: Department Mapping Validation
        self.validate_department_mapping()
        
        # Phase 4: QID 133 Specific Investigation
        self.investigate_qid_133_specifically()
        
        # Final Analysis
        print(f"\n" + "=" * 70)
        print("DEEP DATA VALIDATION SUMMARY")
        print("=" * 70)
        
        csv_status = "AVAILABLE" if csv_data_available else "NOT_AVAILABLE"
        print(f"CSV Data Status: {csv_status}")
        
        function_test = self.validation_results["civil_planning_investigation"].get("function_test", {})
        function_status = function_test.get("status", "UNKNOWN")
        print(f"Function Test Status: {function_status}")
        
        qid_133_found = self.validation_results["civil_planning_investigation"].get("qid_133_found", True)
        qid_status = "FOUND" if qid_133_found else "NOT_FOUND"
        print(f"QID 133 Status: {qid_status}")
        
        # Save results
        self.save_validation_results()
        
        return self.validation_results
    
    def save_validation_results(self):
        """Save validation results"""
        with open('deep_data_validation.json', 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)
        print(f"\nDeep validation results saved: deep_data_validation.json")

if __name__ == "__main__":
    validator = DeepDataValidator()
    results = validator.run_comprehensive_validation()