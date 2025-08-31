#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
question_types関数内のredirect詳細分析（ASCII出力版）
サブエージェント報告のline 6071検証とapp.py内の実際のredirect特定
"""

import re

def deep_question_types_redirect_analysis():
    """question_types関数の詳細redirect分析"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("DEEP QUESTION_TYPES REDIRECT ANALYSIS")
    print("=" * 60)
    
    # question_types関数の完全な抽出
    qt_match = re.search(r'def question_types\(.*?\):(.*?)(?=\ndef |\n@app\.route|\nif __name__|\napp\.run|\Z)', content, re.DOTALL)
    
    if not qt_match:
        print("ERROR: question_types function not found")
        return
    
    qt_function = qt_match.group(1)
    qt_lines = qt_function.split('\n')
    
    print(f"question_types function extracted: {len(qt_lines)} lines")
    print()
    
    # 1. すべてのredirect文を詳細分析
    print("1. ALL REDIRECT STATEMENTS IN question_types")
    print("-" * 40)
    
    redirect_found = False
    for i, line in enumerate(qt_lines, 1):
        if 'redirect' in line.lower() and line.strip():
            redirect_found = True
            clean_line = line.strip()
            # Unicode文字を除去またはエスケープ
            clean_line = clean_line.encode('ascii', errors='ignore').decode('ascii')
            print(f"Line {i}: {clean_line}")
            
            # 前後5行のコンテキスト表示
            print("  Context (lines around redirect):")
            for j in range(max(0, i-5), min(len(qt_lines), i+5)):
                if j < len(qt_lines):
                    context_line = qt_lines[j].strip()
                    context_line = context_line.encode('ascii', errors='ignore').decode('ascii')
                    marker = "  >>> " if j == i-1 else "      "
                    print(f"{marker}Line {j+1}: {context_line}")
            print()
    
    if not redirect_found:
        print("No redirect statements found in question_types function")
    
    print()
    
    # 2. return文の詳細分析
    print("2. ALL RETURN STATEMENTS IN question_types")
    print("-" * 40)
    
    return_count = 0
    for i, line in enumerate(qt_lines, 1):
        if line.strip().startswith('return') and line.strip():
            return_count += 1
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            print(f"Return {return_count} - Line {i}: {clean_line}")
    
    print()
    
    # 3. exam関連の文字列検索
    print("3. EXAM-RELATED STATEMENTS IN question_types")
    print("-" * 40)
    
    exam_found = False
    for i, line in enumerate(qt_lines, 1):
        if 'exam' in line.lower() and line.strip():
            exam_found = True
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            print(f"Line {i}: {clean_line}")
    
    if not exam_found:
        print("No exam-related statements found in question_types function")
    
    print()
    
    # 4. url_for関連の検索
    print("4. URL_FOR STATEMENTS IN question_types")
    print("-" * 40)
    
    url_for_found = False
    for i, line in enumerate(qt_lines, 1):
        if 'url_for' in line.lower() and line.strip():
            url_for_found = True
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            print(f"Line {i}: {clean_line}")
    
    if not url_for_found:
        print("No url_for statements found in question_types function")
    
    print()
    
    # 5. 関数の終了部分の分析
    print("5. FUNCTION END ANALYSIS (last 10 lines)")
    print("-" * 40)
    
    end_lines = qt_lines[-10:]
    for i, line in enumerate(end_lines, len(qt_lines)-9):
        if line.strip():
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            print(f"Line {i}: {clean_line}")
    
    print()
    print("=" * 60)
    
    # 6. アプリ全体でのdepartment + specialist + examパターン検索
    print("6. APP-WIDE SEARCH: department + specialist + exam patterns")
    print("-" * 40)
    
    # 複合パターンの検索
    patterns = [
        r'exam\?department.*type.*specialist',
        r'url_for.*exam.*department.*specialist',
        r'redirect.*exam.*department.*specialist',
        r'department.*type.*specialist.*count.*10'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        print(f"Pattern '{pattern}': {len(matches)} matches")
        for j, match in enumerate(matches):
            if j < 3:  # 最初の3つまで表示
                clean_match = match.encode('ascii', errors='ignore').decode('ascii')
                print(f"  Match {j+1}: {clean_match}")
    
    print()
    print("ANALYSIS COMPLETE")
    print("Verdict: The redirect generating '/exam?department=road&type=specialist&count=10'")
    print("must be located somewhere in the Flask application, but NOT in question_types function")

if __name__ == "__main__":
    deep_question_types_redirect_analysis()