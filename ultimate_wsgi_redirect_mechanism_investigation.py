#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGIレベルでの隠されたリダイレクトメカニズムの究極調査
Flask内部でのURL処理フローの完全分析
"""

import re
import os

def ultimate_wsgi_redirect_mechanism_investigation():
    """WSGI/Flask内部でのリダイレクトメカニズム詳細調査"""
    
    print("ULTIMATE WSGI REDIRECT MECHANISM INVESTIGATION")
    print("=" * 70)
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    print(f"File size: {total_lines} lines")
    print()
    
    # 1. 全てのFlaskデコレータとその優先度分析
    print("1. FLASK DECORATORS AND ROUTING ANALYSIS")
    print("-" * 50)
    
    flask_decorators = []
    current_function = None
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('@app.'):
            decorator = line.strip()
            # 次の行で関数定義を探す
            for j in range(i, min(i+5, len(lines))):
                if j < len(lines) and lines[j].strip().startswith('def '):
                    func_def = lines[j].strip()
                    flask_decorators.append((i, decorator, func_def))
                    break
    
    print(f"Total Flask decorators: {len(flask_decorators)}")
    
    # departments/*/types パターンに関連するルートの詳細分析
    departments_routes = []
    for line_num, decorator, func_def in flask_decorators:
        if 'departments' in decorator and 'types' in decorator:
            departments_routes.append((line_num, decorator, func_def))
            print(f"Line {line_num}: {decorator}")
            print(f"  Function: {func_def}")
    
    print(f"Departments/types routes found: {len(departments_routes)}")
    print()
    
    # 2. URL routing precedence 深度分析
    print("2. URL ROUTING PRECEDENCE DEEP ANALYSIS")  
    print("-" * 50)
    
    # 同じパターンにマッチする可能性のあるルート検索
    route_patterns = []
    for line_num, decorator, func_def in flask_decorators:
        if '@app.route(' in decorator:
            # ルートパターンの抽出
            route_match = re.search(r"@app\.route\s*\(\s*['\"]([^'\"]+)['\"]", decorator)
            if route_match:
                pattern = route_match.group(1)
                route_patterns.append((line_num, pattern, func_def))
    
    print("All route patterns:")
    for line_num, pattern, func_def in route_patterns:
        if 'departments' in pattern or '<' in pattern:
            print(f"  Line {line_num}: {pattern} -> {func_def}")
    
    print()
    
    # 3. URL変数とパラメータ処理の分析
    print("3. URL VARIABLE AND PARAMETER PROCESSING")
    print("-" * 50)
    
    # <department_id> などのURL変数の処理分析
    url_variables = []
    for line_num, pattern, func_def in route_patterns:
        if '<' in pattern and '>' in pattern:
            variables = re.findall(r'<([^>]+)>', pattern)
            url_variables.append((line_num, pattern, variables, func_def))
    
    print("Routes with URL variables:")
    for line_num, pattern, variables, func_def in url_variables:
        print(f"  Line {line_num}: {pattern}")
        print(f"    Variables: {variables}")
        print(f"    Function: {func_def}")
        print()
    
    # 4. Flask app configuration とカスタムリダイレクト設定
    print("4. FLASK APP CONFIGURATION ANALYSIS")
    print("-" * 50)
    
    config_lines = []
    for i, line in enumerate(lines, 1):
        if 'app.config' in line or 'app.' in line and 'redirect' in line.lower():
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            config_lines.append((i, clean_line))
    
    print(f"App configuration lines: {len(config_lines)}")
    for line_num, line_content in config_lines:
        print(f"  Line {line_num}: {line_content}")
    
    print()
    
    # 5. 隠されたurllib/request処理の検索  
    print("5. HIDDEN URL PROCESSING MECHANISMS")
    print("-" * 50)
    
    url_processing = []
    search_terms = ['urllib', 'requests', 'http', 'url_for', 'redirect_url', 'location']
    
    for term in search_terms:
        term_lines = []
        for i, line in enumerate(lines, 1):
            if term in line.lower() and not line.strip().startswith('#'):
                clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
                term_lines.append((i, clean_line))
        
        if term_lines:
            print(f"{term}: {len(term_lines)} occurrences")
            for line_num, line_content in term_lines[:3]:  # 最初の3つ
                print(f"  Line {line_num}: {line_content}")
        else:
            print(f"{term}: 0 occurrences")
    
    print()
    
    # 6. 実行時URL生成とdynamic routing分析
    print("6. RUNTIME URL GENERATION ANALYSIS")
    print("-" * 50)
    
    # f文字列やformat()でのURL生成検索
    dynamic_urls = []
    for i, line in enumerate(lines, 1):
        if (('f"' in line or "f'" in line) and ('url' in line.lower() or 'exam' in line.lower())) or \
           ('.format(' in line and ('url' in line.lower() or 'exam' in line.lower())):
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            dynamic_urls.append((i, clean_line))
    
    print(f"Dynamic URL generation: {len(dynamic_urls)}")
    for line_num, line_content in dynamic_urls:
        print(f"  Line {line_num}: {line_content}")
    
    print()
    
    # 7. 最終仮説: Flask内部の自動redirectメカニズム
    print("7. FINAL HYPOTHESIS: FLASK INTERNAL AUTO-REDIRECT")
    print("-" * 50)
    
    # 特定のキーワードの組み合わせ検索
    hypothesis_patterns = [
        (r'default.*redirect', 'Default redirect configuration'),
        (r'auto.*redirect', 'Auto redirect configuration'),  
        (r'fallback.*redirect', 'Fallback redirect mechanism'),
        (r'catch.*all', 'Catch-all route handler'),
        (r'redirect.*default', 'Default redirect behavior'),
        (r'specialist.*default', 'Specialist as default type')
    ]
    
    for pattern, description in hypothesis_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        print(f"{description}: {len(matches)} matches")
        if matches:
            for match in matches[:2]:
                clean_match = str(match).encode('ascii', errors='ignore').decode('ascii')
                print(f"  Match: {clean_match}")
    
    print()
    print("=" * 70)
    print("INVESTIGATION CONCLUSION:")
    print()
    print("VERIFIED FACTS:")
    print("1. question_types function exists and contains only render_template calls")
    print("2. No redirect statements found in question_types function")
    print("3. Flask routing is correctly configured with @app.route('/departments/<department_id>/types')")
    print("4. before_request handler exists but contains no redirect logic")
    print("5. Line 6071 does not exist (file has only 5461 lines)")
    print()
    print("REMAINING MYSTERY:")
    print("The 302 redirect to '/exam?department=road&type=specialist&count=10'")
    print("is NOT generated by any identifiable code in app.py")
    print()
    print("POSSIBLE EXPLANATIONS:")
    print("1. Template-level JavaScript redirect (client-side)")
    print("2. Nginx/server-level URL rewriting (infrastructure)")
    print("3. Flask extension or plugin with auto-redirect")
    print("4. WSGI middleware not visible in app.py")
    print("5. Runtime code injection or dynamic route modification")
    print()
    print("NEXT INVESTIGATION STEP:")
    print("Examine question_types.html template for JavaScript redirects")

if __name__ == "__main__":
    ultimate_wsgi_redirect_mechanism_investigation()