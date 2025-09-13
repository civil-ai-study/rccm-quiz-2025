# -*- coding: utf-8 -*-
"""
Simple Data Validation - No Dependencies
civil_planningの"無効な問題ID"エラーの根本原因調査
"""

import os
import csv
import glob
import json
from datetime import datetime

class SimpleDataValidator:
    """
    Simple Data Validation without external dependencies
    """
    
    def __init__(self):
        self.data_dir = "data"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "SIMPLE_DATA_VALIDATION",
            "csv_analysis": {},
            "civil_planning_investigation": {}
        }
    
    def analyze_csv_data_simple(self):
        """
        Simple CSV analysis using built-in csv module
        """
        print("=== Simple CSV Data Analysis ===")
        print("Investigating civil_planning question availability...")
        print("-" * 50)
        
        csv_files = glob.glob(os.path.join(self.data_dir, "4-2_*.csv"))
        total_civil_planning = 0
        csv_analysis = {}
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                print(f"\nAnalyzing: {csv_file}")
                print(f"  Total rows: {len(rows)}")
                
                # Get all categories
                categories = set()
                river_questions = []
                
                for row in rows:
                    if 'category' in row:
                        categories.add(row['category'])
                        # Look for river-related categories
                        if any(pattern in str(row['category']) for pattern in ['河川', '砂防', '海岸', '海洋']):
                            river_questions.append(row)
                
                print(f"  Categories found: {list(categories)}")
                print(f"  River questions count: {len(river_questions)}")
                
                if river_questions:
                    sample_ids = [q.get('id', 'NO_ID') for q in river_questions[:5]]
                    print(f"  Sample IDs: {sample_ids}")
                    total_civil_planning += len(river_questions)
                
                csv_analysis[csv_file] = {
                    "total_rows": len(rows),
                    "categories": list(categories),
                    "river_questions": len(river_questions),
                    "sample_ids": [q.get('id', 'NO_ID') for q in river_questions[:5]]
                }
                    
            except Exception as e:
                print(f"  [ERROR] Failed to read {csv_file}: {e}")
                csv_analysis[csv_file] = {"error": str(e)}
        
        print(f"\nTotal civil_planning (river) questions across all CSVs: {total_civil_planning}")
        self.validation_results["csv_analysis"] = csv_analysis
        self.validation_results["civil_planning_investigation"]["total_available"] = total_civil_planning
        
        return total_civil_planning > 0
    
    def test_app_import(self):
        """
        Test importing and calling emergency_get_questions
        """
        print(f"\n=== Testing App Import and Function ===")
        print("Testing emergency_get_questions function...")
        print("-" * 50)
        
        try:
            # Kill any running app processes first to avoid conflicts
            print("Attempting to import app module...")
            
            # Import app and test function
            import app
            
            print("App imported successfully. Testing emergency_get_questions...")
            questions = app.emergency_get_questions('civil_planning', 'specialist', 10)
            
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
                return True
            else:
                print("[ERROR] No questions returned!")
                self.validation_results["civil_planning_investigation"]["function_test"] = {
                    "questions_returned": 0,
                    "status": "NO_QUESTIONS"
                }
                return False
                
        except Exception as e:
            print(f"[ERROR] App import/function test failed: {e}")
            self.validation_results["civil_planning_investigation"]["function_test"] = {
                "error": str(e),
                "status": "FAILED"
            }
            return False
    
    def search_qid_133_all_files(self):
        """
        Search for QID 133 in all CSV files
        """
        print(f"\n=== QID 133 Global Search ===")
        print("Searching for QID 133 in all CSV files...")
        print("-" * 50)
        
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        qid_133_locations = []
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                id_133_rows = [row for row in rows if row.get('id') == '133']
                
                if id_133_rows:
                    categories = [row.get('category', 'NO_CATEGORY') for row in id_133_rows]
                    qid_133_locations.append({
                        "file": csv_file,
                        "rows": len(id_133_rows),
                        "categories": categories
                    })
                    print(f"Found ID 133 in {csv_file}: {len(id_133_rows)} rows")
                    print(f"  Categories: {categories}")
                            
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
        
        if qid_133_locations:
            print(f"\nQID 133 found in {len(qid_133_locations)} files")
            self.validation_results["civil_planning_investigation"]["qid_133_locations"] = qid_133_locations
            return True
        else:
            print("\n[CRITICAL] QID 133 not found in any CSV files!")
            self.validation_results["civil_planning_investigation"]["qid_133_found"] = False
            return False
    
    def check_config_mapping(self):
        """
        Check config.py for civil_planning mapping
        """
        print(f"\n=== Config Mapping Check ===")
        print("Checking config.py for civil_planning mapping...")
        print("-" * 50)
        
        try:
            if os.path.exists('config.py'):
                with open('config.py', 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                if 'civil_planning' in config_content:
                    print("civil_planning found in config.py")
                    
                    # Extract relevant lines
                    lines = config_content.split('\n')
                    civil_lines = [line.strip() for line in lines if 'civil_planning' in line]
                    
                    for line in civil_lines:
                        print(f"  {line}")
                    
                    self.validation_results["civil_planning_investigation"]["config_mapping"] = civil_lines
                    return True
                else:
                    print("civil_planning NOT found in config.py")
                    return False
            else:
                print("config.py not found!")
                return False
                
        except Exception as e:
            print(f"Error checking config: {e}")
            return False
    
    def run_simple_validation(self):
        """
        Run simple validation without dependencies
        """
        print("Simple Data Validation - No Dependencies")
        print("civil_planningの\"無効な問題ID\"エラーの根本原因調査")
        print("=" * 70)
        
        # Phase 1: CSV Data Analysis
        csv_data_available = self.analyze_csv_data_simple()
        
        # Phase 2: App Function Testing
        function_works = self.test_app_import()
        
        # Phase 3: QID 133 Search
        qid_133_exists = self.search_qid_133_all_files()
        
        # Phase 4: Config Mapping Check
        config_mapping_exists = self.check_config_mapping()
        
        # Summary
        print(f"\n" + "=" * 70)
        print("SIMPLE DATA VALIDATION SUMMARY")
        print("=" * 70)
        
        print(f"CSV Data Available: {'YES' if csv_data_available else 'NO'}")
        print(f"Function Test: {'PASS' if function_works else 'FAIL'}")
        print(f"QID 133 Exists: {'YES' if qid_133_exists else 'NO'}")
        print(f"Config Mapping: {'YES' if config_mapping_exists else 'NO'}")
        
        # Root cause analysis
        if not function_works and not qid_133_exists:
            print(f"\n[ROOT CAUSE IDENTIFIED]")
            print(f"QID 133 does not exist in CSV files, causing 'Invalid Question ID' error")
        elif not function_works and qid_133_exists:
            print(f"\n[ROOT CAUSE CANDIDATE]")
            print(f"QID 133 exists but function fails - possibly mapping issue")
        
        # Save results
        self.save_simple_validation_results()
        
        return self.validation_results
    
    def save_simple_validation_results(self):
        """Save validation results"""
        with open('simple_data_validation.json', 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)
        print(f"\nSimple validation results saved: simple_data_validation.json")

if __name__ == "__main__":
    validator = SimpleDataValidator()
    results = validator.run_simple_validation()