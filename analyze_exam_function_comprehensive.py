#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exam関数内のquestion_types機能統合を包括的に解析
隠されたリダイレクト生成ロジックを特定する
"""

import re

def analyze_exam_function_comprehensive():
    """exam関数の包括的解析"""
    
    print("COMPREHENSIVE EXAM FUNCTION ANALYSIS")
    print("=" * 60)
    
    # Step 1: app.pyファイルを読み込み
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading app.py: {e}")
        return
    
    # Step 2: exam関数の開始と終了を特定
    exam_match = re.search(r'@app\.route\(\'/exam\'.*?\ndef exam\(\):(.*?)(?=\n@app\.route|\n\nif __name__|\napp\.run|\Z)', content, re.DOTALL)
    
    if not exam_match:
        print("ERROR: exam function not found")
        return
    
    exam_function = exam_match.group(1)
    print(f"Exam function length: {len(exam_function)} characters")
    print()
    
    # Step 3: リダイレクト生成パターンの検索
    print("REDIRECT GENERATION PATTERN ANALYSIS")
    print("-" * 40)
    
    # パターン1: 直接的なリダイレクト生成
    redirect_patterns = [
        r'redirect\s*\(\s*[\'"].*?department.*?type.*?specialist.*?count.*?10',
        r'redirect\s*\(\s*f[\'"].*?department.*?type.*?specialist.*?count.*?10',
        r'redirect\s*\(\s*.*?department.*?type.*?specialist.*?count.*?10',
        r'/exam\?department=.*?&type=specialist&count=10'
    ]
    
    for i, pattern in enumerate(redirect_patterns, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE | re.DOTALL)
        print(f"Pattern {i} matches: {len(matches)}")
        for match in matches[:3]:  # 最初の3つまで表示
            print(f"  Match: {match[:100]}...")
    
    print()
    
    # Step 4: 条件分岐でのリダイレクト生成
    print("CONDITIONAL REDIRECT ANALYSIS")
    print("-" * 40)
    
    conditional_patterns = [
        r'if.*?request\.path.*?types.*?:.*?redirect',
        r'if.*?department.*?:.*?redirect',
        r'if.*?question_type.*?specialist.*?:.*?redirect',
        r'if.*?types.*?in.*?path.*?:.*?redirect'
    ]
    
    for i, pattern in enumerate(conditional_patterns, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE | re.DOTALL)
        print(f"Conditional Pattern {i} matches: {len(matches)}")
        for match in matches[:2]:
            print(f"  Match: {match[:150]}...")
    
    print()
    
    # Step 5: question_type=specialist の自動設定箇所
    print("QUESTION_TYPE SPECIALIST AUTO-ASSIGNMENT")  
    print("-" * 40)
    
    specialist_patterns = [
        r'[\'"]?question_type[\'"]?\s*=\s*[\'"]specialist[\'"]',
        r'type[\'"]?\s*=\s*[\'"]specialist[\'"]',
        r'specialist[\'"].*?type',
        r'type.*?specialist'
    ]
    
    specialist_found = False
    for i, pattern in enumerate(specialist_patterns, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE)
        if matches:
            specialist_found = True
            print(f"Specialist Assignment Pattern {i} matches: {len(matches)}")
            for match in matches[:3]:
                print(f"  Match: {match}")
    
    if not specialist_found:
        print("No explicit specialist assignment found in exam function")
    
    print()
    
    # Step 6: URL parameter handling analysis
    print("URL PARAMETER HANDLING ANALYSIS")
    print("-" * 40)
    
    param_patterns = [
        r'request\.args\.get\([\'"]department[\'"]',
        r'request\.args\.get\([\'"]type[\'"]',
        r'request\.args\.get\([\'"]count[\'"]',
        r'department.*?road.*?type.*?specialist',
        r'f[\'"].*?/exam.*?department.*?{.*?}.*?type.*?specialist'
    ]
    
    for i, pattern in enumerate(param_patterns, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE)
        print(f"Parameter Pattern {i} matches: {len(matches)}")
        for match in matches[:2]:
            print(f"  Match: {match}")
    
    print()
    
    # Step 7: Function calls that might generate redirects
    print("FUNCTION CALL ANALYSIS")
    print("-" * 40)
    
    # exam関数内で呼び出される他の関数
    function_calls = re.findall(r'(\w+)\s*\([^)]*\)', exam_function)
    function_counts = {}
    for call in function_calls:
        function_counts[call] = function_counts.get(call, 0) + 1
    
    suspicious_functions = [func for func, count in function_counts.items() 
                           if any(keyword in func.lower() for keyword in 
                                ['redirect', 'route', 'url', 'department', 'type'])]
    
    print(f"Total function calls: {len(function_calls)}")
    print(f"Suspicious function calls: {suspicious_functions}")
    
    # 特に重要な関数呼び出しの詳細
    important_calls = [
        r'redirect\s*\([^)]*\)',
        r'url_for\s*\([^)]*\)',
        r'generate_\w+\s*\([^)]*\)',
        r'\w*redirect\w*\s*\([^)]*\)'
    ]
    
    for i, pattern in enumerate(important_calls, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE)
        if matches:
            print(f"Important Call Pattern {i}: {len(matches)} matches")
            for match in matches[:3]:
                print(f"  {match}")
    
    print()
    
    # Step 8: Template rendering analysis
    print("TEMPLATE RENDERING ANALYSIS")
    print("-" * 40)
    
    template_patterns = [
        r'render_template\s*\(\s*[\'"]question_types\.html[\'"]',
        r'render_template\s*\(\s*[\'"]exam\.html[\'"]',
        r'render_template\s*\([^)]*question.*?type[^)]*\)'
    ]
    
    for i, pattern in enumerate(template_patterns, 1):
        matches = re.findall(pattern, exam_function, re.IGNORECASE)
        print(f"Template Pattern {i} matches: {len(matches)}")
        for match in matches[:2]:
            print(f"  Match: {match}")
    
    print()
    
    # Step 9: 条件分岐の詳細分析
    print("DETAILED CONDITIONAL LOGIC ANALYSIS")
    print("-" * 40)
    
    # if文のブロックを抽出
    if_blocks = re.findall(r'if\s+([^:]+):(.*?)(?=\n\s*(?:if|elif|else|def|class|\Z))', exam_function, re.DOTALL)
    
    print(f"Total if blocks found: {len(if_blocks)}")
    
    for i, (condition, block) in enumerate(if_blocks[:5], 1):  # 最初の5つまで
        condition_clean = condition.strip().replace('\n', ' ')[:100]
        block_clean = block.strip().replace('\n', ' ')[:200]
        
        print(f"If Block {i}:")
        print(f"  Condition: {condition_clean}")
        
        if any(keyword in block.lower() for keyword in ['redirect', 'specialist', 'type']):
            print(f"  Block (SUSPICIOUS): {block_clean}")
        else:
            print(f"  Block: {block_clean}")
        print()
    
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    
    # 最終的な判定
    if any(pattern in exam_function.lower() for pattern in ['redirect', '/exam?department', 'type=specialist']):
        print("🚨 VERDICT: exam function contains redirect logic")
    else:
        print("✅ VERDICT: exam function does not contain obvious redirect logic")

if __name__ == "__main__":
    analyze_exam_function_comprehensive()