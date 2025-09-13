# -*- coding: utf-8 -*-
"""
Critical QID Validation Fix - Direct Implementation
クリティカルQID検証修正 - 直接実装

Based on deep analysis findings:
- Basic Subject: 70% invalid QIDs (84, 167, 99, etc.)
- Civil Planning: 100% invalid QIDs (106, 310, 167, etc.)

Direct fix to get_mixed_questions function
"""

import os
import shutil
from datetime import datetime

class CriticalQIDValidationFix:
    """
    Critical fix for QID validation issues identified in deep analysis
    """
    
    def __init__(self):
        self.base_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app-production"
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixes_applied = []
    
    def create_ultra_sync_backup(self):
        """
        Create ultra-sync safety backup
        """
        print("CRITICAL FIX: Creating safety backup...")
        
        backup_name = f"app.py.critical_qid_fix_backup_{self.backup_timestamp}"
        app_py = os.path.join(self.base_dir, "app.py")
        backup_path = os.path.join(self.base_dir, backup_name)
        
        try:
            shutil.copy2(app_py, backup_path)
            print(f"[OK] Critical backup created: {backup_name}")
            return True
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False
    
    def fix_get_mixed_questions_qid_validation(self):
        """
        CRITICAL FIX: Add QID validation to get_mixed_questions function
        
        ROOT CAUSE: Questions with invalid QIDs are being selected and returned
        SOLUTION: Add comprehensive QID validation before question selection
        """
        print("\\nCRITICAL FIX: Adding QID validation to get_mixed_questions...")
        
        app_py_path = os.path.join(self.base_dir, "app.py")
        
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CRITICAL FIX: Add QID validation before final question selection
            old_final_selection = """    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]
    
    random.shuffle(new_questions)
    selected_questions.extend(new_questions[:remaining_count])"""
            
            new_validated_selection = '''    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]
    
    # CRITICAL FIX: QID Validation before final selection
    validated_questions = []
    invalid_qids = []
    
    for q in new_questions:
        qid = int(q.get('id', 0))
        category = q.get('category', '')
        source = q.get('source', '')
        
        # CRITICAL VALIDATION 1: Basic Subject QID validation
        if question_type == 'basic':
            # Basic questions must be from 4-1.csv with QID 1-202 and category="共通"
            if (source == '4-1.csv' and 
                category == '共通' and 
                1 <= qid <= 202):
                validated_questions.append(q)
                logger.info(f"[CRITICAL FIX] Basic question validated: QID={qid}, category={category}")
            else:
                invalid_qids.append(qid)
                logger.error(f"[CRITICAL FIX] Invalid basic question filtered: QID={qid}, category={category}, source={source}")
        
        # CRITICAL VALIDATION 2: Specialist Subject QID validation
        elif question_type == 'specialist':
            # Specialist questions must be from 4-2_*.csv with QID 1000+ and matching department category
            if (source.startswith('4-2') and 
                qid >= 1000 and 
                category == target_categories):
                validated_questions.append(q)
                logger.info(f"[CRITICAL FIX] Specialist question validated: QID={qid}, category={category}")
            else:
                invalid_qids.append(qid)
                logger.error(f"[CRITICAL FIX] Invalid specialist question filtered: QID={qid}, category={category}, expected={target_categories}, source={source}")
        
        # CRITICAL VALIDATION 3: Other question types
        else:
            # For other types, basic validation
            if qid > 0:
                validated_questions.append(q)
            else:
                invalid_qids.append(qid)
    
    if invalid_qids:
        logger.error(f"[CRITICAL FIX] Filtered {len(invalid_qids)} invalid QIDs: {invalid_qids}")
    
    logger.info(f"[CRITICAL FIX] QID validation: {len(new_questions)} -> {len(validated_questions)} valid questions")
    
    random.shuffle(validated_questions)
    selected_questions.extend(validated_questions[:remaining_count])'''
            
            if old_final_selection in content:
                content = content.replace(old_final_selection, new_validated_selection)
                print("[CRITICAL FIX] QID validation added to get_mixed_questions")
                self.fixes_applied.append("get_mixed_questions_qid_validation")
            else:
                print("[WARNING] Final selection code not found for QID validation")
            
            # Write updated content
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] QID validation fix failed: {e}")
            return False
    
    def add_comprehensive_error_handling(self):
        """
        CRITICAL FIX: Add comprehensive error handling for invalid QIDs in exam route
        """
        print("\\nCRITICAL FIX: Adding comprehensive error handling...")
        
        app_py_path = os.path.join(self.base_dir, "app.py")
        
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CRITICAL FIX: Enhanced error handling in exam route POST processing
            old_qid_processing = "            qid = int(request.form.get('qid', 0))"
            
            new_comprehensive_qid_processing = '''            # CRITICAL FIX: Comprehensive QID processing with validation
            qid_raw = request.form.get('qid', 0)
            try:
                qid = int(qid_raw)
            except (ValueError, TypeError):
                logger.error(f"[CRITICAL FIX] Invalid QID format: {qid_raw}")
                return render_template('error.html', 
                                     error=f"無効な問題ID形式です: {qid_raw}",
                                     error_type="invalid_qid_format")
            
            # CRITICAL FIX: Pre-validation QID range check
            department = session.get('selected_department', '')
            question_type = session.get('selected_question_type', 'basic')
            
            # Basic subject QID range validation
            if question_type == 'basic' and not (1 <= qid <= 202):
                logger.error(f"[CRITICAL FIX] Basic QID {qid} out of valid range (1-202)")
                return render_template('error.html', 
                                     error=f"基礎科目の問題ID {qid} は有効範囲外です (1-202)",
                                     error_type="qid_range_validation")
            
            # Specialist subject QID range validation
            elif question_type == 'specialist' and qid < 1000:
                logger.error(f"[CRITICAL FIX] Specialist QID {qid} out of valid range (1000+)")
                return render_template('error.html', 
                                     error=f"専門科目の問題ID {qid} は有効範囲外です (1000以上)",
                                     error_type="qid_range_validation")'''
            
            if old_qid_processing in content:
                content = content.replace(old_qid_processing, new_comprehensive_qid_processing)
                print("[CRITICAL FIX] Comprehensive QID processing added to exam route")
                self.fixes_applied.append("comprehensive_qid_processing")
            
            # Write updated content
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Comprehensive error handling fix failed: {e}")
            return False
    
    def run_critical_qid_validation_fix(self):
        """
        Execute critical QID validation fix
        """
        print("CRITICAL QID VALIDATION FIX")
        print("Addressing invalid QID assignment issues")
        print("=" * 60)
        
        # Safety backup
        if not self.create_ultra_sync_backup():
            print("[ABORT] Safety backup failed - cannot proceed")
            return False
        
        # Execute critical fixes
        fixes_success = []
        
        # FIX 1: QID validation in get_mixed_questions
        fixes_success.append(self.fix_get_mixed_questions_qid_validation())
        
        # FIX 2: Comprehensive error handling
        fixes_success.append(self.add_comprehensive_error_handling())
        
        # Verify fixes successful
        if not all(fixes_success):
            print("[ERROR] Some critical fixes failed")
            return False
        
        # Success report
        print("\\n" + "=" * 60)
        print("CRITICAL QID VALIDATION FIX COMPLETED")
        print("=" * 60)
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"  + {fix}")
        
        print("\\n[EXPECTED RESULTS]")
        print("- Basic Subject: Invalid QIDs filtered out before selection")
        print("- Civil Planning: Invalid QIDs filtered out before selection") 
        print("- Comprehensive error handling for invalid QID ranges")
        print("- Enhanced logging for QID validation process")
        
        print("\\n[NEXT STEPS]")
        print("1. Restart application to apply fixes")
        print("2. Test Basic Subject (should now get valid QIDs 1-202)")
        print("3. Test Civil Planning (should now get valid QIDs 1000+)")
        print("4. Verify 1->10 question progression works")
        
        return True

if __name__ == "__main__":
    fixer = CriticalQIDValidationFix()
    success = fixer.run_critical_qid_validation_fix()
    exit(0 if success else 1)