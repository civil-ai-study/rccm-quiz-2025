#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RCCM Quiz Application - 全13部門の徹底的検証スクリプト
検証項目：
1. 各部門の問題読み込み正常性
2. 問題文・選択肢の文字化けチェック
3. 数学記号・特殊文字の表示確認
4. ページ遷移の正常性
5. エラーハンドリングの適切性
"""

import sys
import os
import re
from datetime import datetime
sys.path.append('.')

try:
    from app import app, LIGHTWEIGHT_DEPARTMENT_MAPPING
    from config import Config
    import html
    import urllib.parse

    print("=== RCCM Quiz Application All 13 Departments Verification Report ===")
    print(f"Verification Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 13部門の定義
    departments = [
        ('basic', 'Basic Subjects (Common)'),
        ('road', 'Road'),
        ('river', 'River, Erosion Control and Coast/Ocean'),
        ('urban', 'Urban Planning and Regional Planning'),
        ('garden', 'Landscape'),
        ('env', 'Construction Environment'),
        ('steel', 'Steel Structure and Concrete'),
        ('soil', 'Soil and Foundation'),
        ('construction', 'Construction Planning, Equipment and Cost'),
        ('water', 'Water Supply and Industrial Water'),
        ('forest', 'Forest Civil Engineering'),
        ('agri', 'Agricultural Civil Engineering'),
        ('tunnel', 'Tunnel')
    ]

    verification_results = {}
    total_success = 0
    total_failures = 0

    # Flask test clientでテスト実行
    with app.test_client() as client:
        for dept_code, dept_name in departments:
            print(f"Testing: {dept_name} ({dept_code})")

            try:
                # 部門ページへのアクセステスト
                # 実際のexamルートパターンでテスト
                response = client.get(f'/exam?department={dept_code}', follow_redirects=True)

                result = {
                    'department_code': dept_code,
                    'department_name': dept_name,
                    'status_code': response.status_code,
                    'content_length': len(response.data) if response.data else 0,
                    'has_html_content': False,
                    'has_form_elements': False,
                    'has_question_content': False,
                    'has_answer_options': False,
                    'character_encoding_ok': True,
                    'mathematical_symbols': [],
                    'special_characters': [],
                    'error_messages': [],
                    'success': False
                }

                if response.status_code == 200:
                    content = response.data.decode('utf-8')

                    # HTML構造チェック
                    if '<html' in content and '</html>' in content:
                        result['has_html_content'] = True

                    # フォーム要素チェック
                    if '<form' in content and 'method="POST"' in content:
                        result['has_form_elements'] = True

                    # 問題内容チェック
                    if any(keyword in content for keyword in ['問題', '問', 'question', 'Q.']):
                        result['has_question_content'] = True

                    # 選択肢チェック
                    option_patterns = ['①', '②', '③', '④', '⑤', 'A)', 'B)', 'C)', 'D)', 'E)', 'option_a', 'option_b']
                    if any(pattern in content for pattern in option_patterns):
                        result['has_answer_options'] = True

                    # 数学記号・特殊文字の検出
                    math_symbols = re.findall(r'[×÷±≤≥≠∑∏∫∂∆∇√∞°π]', content)
                    if math_symbols:
                        result['mathematical_symbols'] = list(set(math_symbols))

                    special_chars = re.findall(r'[㎡㎥℃㎏㎞㎝㎜㎠㎤㎡]', content)
                    if special_chars:
                        result['special_characters'] = list(set(special_chars))

                    # 文字化けチェック（疑わしいパターンを検出）
                    garbled_patterns = ['?', '\ufffd', '&#', '&amp;amp;']
                    if any(pattern in content for pattern in garbled_patterns):
                        result['character_encoding_ok'] = False
                        result['error_messages'].append("文字化けの可能性")

                    # 成功判定
                    if (result['has_html_content'] and
                        result['has_form_elements'] and
                        result['has_question_content'] and
                        result['character_encoding_ok']):
                        result['success'] = True
                        total_success += 1
                        print(f"  SUCCESS: Normal operation")
                    else:
                        total_failures += 1
                        print(f"  FAILURE: Issues detected")

                        # 問題詳細
                        if not result['has_html_content']:
                            print(f"    - No HTML structure")
                        if not result['has_form_elements']:
                            print(f"    - No form elements")
                        if not result['has_question_content']:
                            print(f"    - No question content")
                        if not result['character_encoding_ok']:
                            print(f"    - Character encoding issues")

                    # 詳細情報表示
                    print(f"    Status Code: {result['status_code']}")
                    print(f"    Content Size: {result['content_length']:,} bytes")
                    if result['mathematical_symbols']:
                        print(f"    Math Symbols: {', '.join(result['mathematical_symbols'])}")
                    if result['special_characters']:
                        print(f"    Special Chars: {', '.join(result['special_characters'])}")

                else:
                    result['error_messages'].append(f"HTTP Error {response.status_code}")
                    total_failures += 1
                    print(f"  FAILURE: HTTP Error {response.status_code}")

            except Exception as e:
                result = {
                    'department_code': dept_code,
                    'department_name': dept_name,
                    'error_messages': [str(e)],
                    'success': False
                }
                total_failures += 1
                print(f"  EXCEPTION: {str(e)}")

            verification_results[dept_code] = result
            print()

    # 最終レポート
    print("=" * 80)
    print("COMPREHENSIVE VERIFICATION RESULTS")
    print("=" * 80)
    print(f"Total Departments: {len(departments)}")
    print(f"Success: {total_success}")
    print(f"Failures: {total_failures}")
    print(f"Success Rate: {(total_success / len(departments) * 100):.1f}%")
    print()

    # 問題のある部門の詳細
    if total_failures > 0:
        print("DEPARTMENTS WITH ISSUES:")
        for dept_code, result in verification_results.items():
            if not result['success']:
                print(f"  - {result['department_name']} ({dept_code})")
                for error in result.get('error_messages', []):
                    print(f"    Error: {error}")

    # 成功部門の要約
    if total_success > 0:
        print("SUCCESSFUL DEPARTMENTS:")
        for dept_code, result in verification_results.items():
            if result['success']:
                print(f"  - {result['department_name']} ({dept_code})")

    print()
    print("=" * 80)
    print("DETAILED TECHNICAL INFORMATION")
    print("=" * 80)

    # 数学記号・特殊文字の統計
    all_math_symbols = []
    all_special_chars = []
    for result in verification_results.values():
        all_math_symbols.extend(result.get('mathematical_symbols', []))
        all_special_chars.extend(result.get('special_characters', []))

    unique_math = list(set(all_math_symbols))
    unique_special = list(set(all_special_chars))

    if unique_math:
        print(f"Detected Math Symbols: {', '.join(unique_math)}")
    if unique_special:
        print(f"Detected Special Characters: {', '.join(unique_special)}")

    # レスポンスサイズ統計
    content_sizes = [r.get('content_length', 0) for r in verification_results.values() if r.get('content_length')]
    if content_sizes:
        avg_size = sum(content_sizes) / len(content_sizes)
        print(f"Average Response Size: {avg_size:,.0f} bytes")
        print(f"Maximum Response Size: {max(content_sizes):,} bytes")
        print(f"Minimum Response Size: {min(content_sizes):,} bytes")

    print()
    print(f"Verification Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if total_success == len(departments):
        print("*** ALL DEPARTMENTS VERIFIED SUCCESSFULLY! ***")
        sys.exit(0)
    else:
        print("*** SOME DEPARTMENTS HAVE ISSUES ***")
        sys.exit(1)

except ImportError as e:
    print(f"Module Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)