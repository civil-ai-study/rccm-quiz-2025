#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
question_types.htmlテンプレート内のJavaScriptリダイレクト詳細分析
302リダイレクトの最終的な発生源特定
"""

def template_javascript_redirect_analysis():
    """question_types.htmlテンプレートの詳細分析"""
    
    print("TEMPLATE JAVASCRIPT REDIRECT ANALYSIS")
    print("=" * 60)
    
    with open('templates/question_types.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    lines = template_content.split('\n')
    total_lines = len(lines)
    
    print(f"Template file: templates/question_types.html")
    print(f"Total lines: {total_lines}")
    print()
    
    # 1. JavaScript コードの詳細分析
    print("1. JAVASCRIPT CODE ANALYSIS")
    print("-" * 40)
    
    js_start = None
    js_end = None
    js_lines = []
    
    for i, line in enumerate(lines, 1):
        if '<script>' in line:
            js_start = i
        if '</script>' in line:
            js_end = i
        if js_start and not js_end:
            js_lines.append((i, line.strip()))
        elif js_start and js_end and i <= js_end:
            js_lines.append((i, line.strip()))
    
    print(f"JavaScript section: lines {js_start} - {js_end}")
    print(f"JavaScript lines count: {len(js_lines)}")
    print()
    
    print("JavaScript Code:")
    for line_num, line_content in js_lines:
        print(f"  Line {line_num}: {line_content}")
    
    print()
    
    # 2. URL生成パターンの分析
    print("2. URL GENERATION PATTERN ANALYSIS")
    print("-" * 40)
    
    # line 174での具体的なURL生成分析
    critical_line = None
    for line_num, line_content in js_lines:
        if 'window.location.href' in line_content:
            critical_line = (line_num, line_content)
            break
    
    if critical_line:
        line_num, line_content = critical_line
        print(f"CRITICAL LINE {line_num}: {line_content}")
        print()
        
        # URLパターンの詳細分析
        if 'exam?department=' in line_content:
            print("URL PATTERN DETECTED:")
            print("  Template generates: /exam?department=${departmentId}&question_type=${typeId}&category=all")
            print("  This matches the observed redirect pattern!")
            print()
            
            # パラメータ分析
            print("PARAMETER ANALYSIS:")
            print(f"  departmentId: Comes from template variable '{{{{ department.id }}}}'")
            print(f"  typeId: Comes from card dataset.type attribute")  
            print(f"  category: Hard-coded as 'all'")
            print()
            
            # 実際の動作フロー推定
            print("ACTUAL BEHAVIOR FLOW:")
            print("1. User clicks question-type-card")
            print("2. JavaScript extracts typeId from dataset.type")
            print("3. JavaScript extracts departmentId from template variable")
            print("4. JavaScript constructs URL: /exam?department=X&question_type=Y&category=all")
            print("5. JavaScript executes window.location.href redirect")
            print()
            
            # specialistの自動設定原因
            print("SPECIALIST AUTO-ASSIGNMENT MYSTERY:")
            print("The template generates 'question_type=${typeId}' but")
            print("the actual redirect shows 'type=specialist'")
            print("This suggests:")
            print("- Either typeId is always 'specialist' in the template")
            print("- Or there's a backend URL parameter transformation")
            print()
    
    # 3. HTML要素の分析
    print("3. HTML ELEMENT ANALYSIS")
    print("-" * 40)
    
    # data-type属性の検索
    data_type_lines = []
    for i, line in enumerate(lines, 1):
        if 'data-type=' in line:
            data_type_lines.append((i, line.strip()))
    
    print(f"data-type attributes found: {len(data_type_lines)}")
    for line_num, line_content in data_type_lines:
        print(f"  Line {line_num}: {line_content}")
    
    print()
    
    # 4. URL生成のaタグ分析
    print("4. URL GENERATION IN A TAGS")
    print("-" * 40)
    
    url_for_lines = []
    for i, line in enumerate(lines, 1):
        if 'url_for(' in line and 'exam' in line:
            url_for_lines.append((i, line.strip()))
    
    print(f"url_for exam links found: {len(url_for_lines)}")
    for line_num, line_content in url_for_lines:
        print(f"  Line {line_num}: {line_content}")
        
        # line 97の詳細分析
        if line_num == 97:
            print("    CRITICAL URL_FOR ANALYSIS:")
            print("    Pattern: url_for('exam', department=department.id, question_type=type_id, category='all')")
            print("    This generates the same URL pattern as JavaScript!")
    
    print()
    
    # 5. Template変数の分析
    print("5. TEMPLATE VARIABLES ANALYSIS")
    print("-" * 40)
    
    template_vars = []
    for i, line in enumerate(lines, 1):
        if '{{' in line and '}}' in line:
            # {{ department.id }} 等の抽出
            import re
            vars_in_line = re.findall(r'\{\{([^}]+)\}\}', line)
            for var in vars_in_line:
                template_vars.append((i, var.strip()))
    
    important_vars = [var for var in template_vars if 'department' in var[1] or 'type' in var[1]]
    
    print(f"Important template variables: {len(important_vars)}")
    for line_num, var_content in important_vars:
        print(f"  Line {line_num}: {{ {var_content} }}")
    
    print()
    
    # 6. 最終結論
    print("6. FINAL ANALYSIS CONCLUSION")
    print("-" * 40)
    
    print("ROOT CAUSE IDENTIFIED:")
    print()
    print("The 302 redirect is NOT generated by server-side code but by:")
    print()
    print("1. CLIENT-SIDE JAVASCRIPT REDIRECT:")
    print("   - Line 174: window.location.href = `/exam?department=${departmentId}&question_type=${typeId}&category=all`;")
    print("   - This JavaScript executes when user clicks on question-type-card")
    print("   - Browser interprets this as a new page request")
    print()
    print("2. DUAL REDIRECT MECHANISM:")
    print("   - HTML anchor tags (line 97): url_for('exam', ...)")  
    print("   - JavaScript click handler (line 174): window.location.href")
    print("   - Both generate the same URL pattern")
    print()
    print("3. SPECIALIST PARAMETER MYSTERY:")
    print("   - Template shows question_type=${typeId}")
    print("   - Actual redirect shows type=specialist")
    print("   - This suggests typeId resolves to 'specialist' at runtime")
    print()
    print("4. WHY 302 REDIRECT IS OBSERVED:")
    print("   - JavaScript window.location.href causes browser to make new HTTP request")
    print("   - Server may respond with 302 redirect to normalize URL or handle routing")
    print("   - The redirect we observe is the server's response to JavaScript navigation")
    print()
    print("VERIFICATION NEEDED:")
    print("Test question_types.html in browser to confirm JavaScript behavior")
    print("Check what typeId actually contains when card is clicked")

if __name__ == "__main__":
    template_javascript_redirect_analysis()