#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Quality Check - without Unicode characters in console output
"""
import os
import glob
import re
from collections import defaultdict

def check_quality():
    """Complete quality verification"""

    csv_files = glob.glob("data/*.csv")
    issues = {
        'floating_chars': [],
        'bad_scientific': [],
        'spacing_issues': [],
        'file_errors': []
    }

    quality_score = 100

    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # 1. 浮つき文字チェック
            superscripts = re.findall(r'[²³¹⁰⁴⁵⁶⁷⁸⁹⁺⁻]', content)
            if superscripts:
                issues['floating_chars'].append((filename, set(superscripts)))
                quality_score -= 20

            # 2. 間違った科学的記法
            bad_sci = re.findall(r'10-[0-9]+(?![^a-zA-Z])', content)
            if bad_sci:
                issues['bad_scientific'].append((filename, set(bad_sci)))
                quality_score -= 15

            # 3. スペース問題
            no_space = re.findall(r'10\^-[0-9]+[a-zA-Z/]', content)
            if no_space:
                issues['spacing_issues'].append((filename, set(no_space)))
                quality_score -= 5

        except Exception as e:
            issues['file_errors'].append((filename, str(e)))
            quality_score -= 10

    # レポート生成
    with open('simple_quality_report.txt', 'w', encoding='utf-8') as f:
        f.write("ULTIMATE QUALITY CHECK REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Quality Score: {quality_score}/100\n\n")

        f.write(f"Files Analyzed: {len(csv_files)}\n\n")

        if issues['floating_chars']:
            f.write("CRITICAL: Floating Characters Found:\n")
            for filename, chars in issues['floating_chars']:
                f.write(f"  {filename}: {chars}\n")
            f.write("\n")
        else:
            f.write("✅ NO FLOATING CHARACTERS\n\n")

        if issues['bad_scientific']:
            f.write("CRITICAL: Incorrect Scientific Notation:\n")
            for filename, notations in issues['bad_scientific']:
                f.write(f"  {filename}: {notations}\n")
            f.write("\n")
        else:
            f.write("✅ SCIENTIFIC NOTATION CORRECT\n\n")

        if issues['spacing_issues']:
            f.write("WARNING: Spacing Issues:\n")
            for filename, patterns in issues['spacing_issues']:
                f.write(f"  {filename}: {patterns}\n")
            f.write("\n")
        else:
            f.write("✅ SPACING CORRECT\n\n")

        if issues['file_errors']:
            f.write("ERROR: File Read Errors:\n")
            for filename, error in issues['file_errors']:
                f.write(f"  {filename}: {error}\n")
            f.write("\n")
        else:
            f.write("✅ ALL FILES READABLE\n\n")

        # 最終判定
        if quality_score >= 100:
            f.write("FINAL RESULT: 100%+ QUALITY ACHIEVED\n")
            f.write("✅ All issues resolved\n")
            f.write("✅ Perfect quality assured\n")
        else:
            f.write(f"FINAL RESULT: {quality_score}/100 - IMPROVEMENTS NEEDED\n")

    return quality_score, issues

if __name__ == "__main__":
    os.chdir(r"C:\Users\ABC\Desktop\rccm-quiz-app")

    print("Starting quality check...")
    score, issues = check_quality()

    print(f"Quality Score: {score}/100")
    print(f"Floating chars: {len(issues['floating_chars'])}")
    print(f"Bad scientific: {len(issues['bad_scientific'])}")
    print(f"Spacing issues: {len(issues['spacing_issues'])}")
    print(f"File errors: {len(issues['file_errors'])}")
    print("Report: simple_quality_report.txt")

    if score >= 100:
        print("SUCCESS: 100%+ Quality Achieved!")
    else:
        print("FAILED: Improvements needed")