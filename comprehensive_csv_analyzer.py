#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive CSV Analyzer - Check every question and answer text
一問一問、回答一つ一つを全てチェックします
"""
import os
import csv
import glob

def analyze_all_csv_content():
    """すべてのCSVファイルの問題文・回答文を一つ一つ詳細チェック"""

    os.chdir(r"C:\Users\ABC\Desktop\rccm-quiz-app")

    # 検索対象文字
    superscript_chars = ['²', '³', '¹', '⁰', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
    subscript_chars = ['₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', '₀']

    # CSVファイルリスト
    csv_files = []
    csv_files.append('data/4-1.csv')
    csv_files.extend(glob.glob('data/4-2_*.csv'))

    # バックアップやアーカイブを除外
    main_csv_files = [f for f in csv_files
                     if 'backup' not in f.lower()
                     and 'archive' not in f.lower()
                     and os.path.exists(f)]

    print("COMPREHENSIVE CSV CONTENT ANALYSIS")
    print("=================================")
    print(f"Files to analyze: {len(main_csv_files)}")
    print("")

    total_questions = 0
    total_answers = 0
    superscript_issues = []
    subscript_found = []

    for csv_file in sorted(main_csv_files):
        print(f"ANALYZING FILE: {csv_file}")
        print("-" * 50)

        if not os.path.exists(csv_file):
            print(f"ERROR: File not found")
            continue

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)

            file_questions = 0
            file_answers = 0

            for row_num, row in enumerate(rows, 1):
                if len(row) < 8:  # CSVの基本構造チェック
                    continue

                file_questions += 1
                total_questions += 1

                # 各列をチェック
                question_text = row[3] if len(row) > 3 else ""
                option_a = row[4] if len(row) > 4 else ""
                option_b = row[5] if len(row) > 5 else ""
                option_c = row[6] if len(row) > 6 else ""
                option_d = row[7] if len(row) > 7 else ""
                explanation = row[9] if len(row) > 9 else ""

                # 全テキスト結合
                all_text = f"{question_text} {option_a} {option_b} {option_c} {option_d} {explanation}"
                file_answers += 4  # 4つの選択肢
                total_answers += 4

                # 上付き文字チェック
                for char in superscript_chars:
                    if char in all_text:
                        superscript_issues.append({
                            'file': csv_file,
                            'row': row_num,
                            'char': char,
                            'context': all_text[:100] + "..."
                        })

                # 下付き文字チェック
                for char in subscript_chars:
                    if char in all_text:
                        subscript_found.append({
                            'file': csv_file,
                            'row': row_num,
                            'char': char,
                            'context': all_text[:100] + "..."
                        })

            print(f"Questions checked: {file_questions}")
            print(f"Answer options checked: {file_answers}")
            print("")

        except Exception as e:
            print(f"ERROR reading {csv_file}: {e}")
            print("")

    print("FINAL COMPREHENSIVE ANALYSIS RESULTS")
    print("====================================")
    print(f"Total files analyzed: {len(main_csv_files)}")
    print(f"Total questions checked: {total_questions}")
    print(f"Total answer options checked: {total_answers}")
    print("")

    print("SUPERSCRIPT CHARACTER ISSUES:")
    if superscript_issues:
        print(f"FOUND {len(superscript_issues)} ISSUES:")
        for issue in superscript_issues:
            print(f"  File: {issue['file']}")
            print(f"  Row: {issue['row']}")
            print(f"  Character: '{issue['char']}'")
            print(f"  Context: {issue['context']}")
            print("")
    else:
        print("NO SUPERSCRIPT ISSUES FOUND")

    print("")
    print("SUBSCRIPT CHARACTERS (LEGITIMATE):")
    if subscript_found:
        print(f"FOUND {len(subscript_found)} OCCURRENCES:")
        for item in subscript_found[:10]:  # 最初の10件を表示
            print(f"  File: {item['file']}")
            print(f"  Character: '{item['char']}'")
            print(f"  Context: {item['context']}")
            print("")
        if len(subscript_found) > 10:
            print(f"  ... and {len(subscript_found) - 10} more occurrences")
    else:
        print("NO SUBSCRIPT CHARACTERS FOUND")

    return total_questions, total_answers, len(superscript_issues), len(subscript_found)

if __name__ == "__main__":
    questions, answers, super_issues, sub_count = analyze_all_csv_content()

    print(f"\nCOMPREHENSIVE CHECK COMPLETE:")
    print(f"- Questions analyzed: {questions}")
    print(f"- Answer options analyzed: {answers}")
    print(f"- Superscript issues: {super_issues}")
    print(f"- Subscript characters: {sub_count}")

    if super_issues == 0:
        print("\nSUCCESS: No floating character issues found!")
    else:
        print(f"\nWARNING: {super_issues} floating character issues need fixing!")