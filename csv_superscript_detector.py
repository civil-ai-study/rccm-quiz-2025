#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Superscript Character Detector
Specifically searches for Unicode superscript characters that cause floating display
"""
import os
import csv
import glob

def detect_superscript_characters():
    """Find all superscript Unicode characters in CSV files"""

    os.chdir(r"C:\Users\ABC\Desktop\rccm-quiz-app")

    # Superscript characters that cause floating display
    superscript_chars = ['²', '³', '¹', '⁰', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']

    # Find all main CSV files (exclude backups and archives)
    csv_files = []
    csv_files.append('data/4-1.csv')
    csv_files.extend(glob.glob('data/4-2_*.csv'))

    # Filter out backup files and archive folders
    main_csv_files = [f for f in csv_files
                     if 'backup' not in f.lower()
                     and 'archive' not in f.lower()
                     and os.path.exists(f)]

    print(f"ANALYZING {len(main_csv_files)} main CSV files for superscript characters...")
    print("=" * 80)

    total_issues = 0
    issues_by_file = {}

    for csv_file in sorted(main_csv_files):
        print(f"\nAnalyzing: {csv_file}")

        if not os.path.exists(csv_file):
            print(f"   ERROR: File not found: {csv_file}")
            continue

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            file_issues = []

            # Check for each superscript character
            for char in superscript_chars:
                if char in content:
                    count = content.count(char)
                    file_issues.append((char, count))
                    total_issues += count
                    print(f"   FOUND '{char}': {count} occurrences")

            if file_issues:
                issues_by_file[csv_file] = file_issues

                # Show specific examples
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for char in superscript_chars:
                        if char in line:
                            print(f"   Line {i}: {line[:100]}...")
                            break
            else:
                print("   OK: No superscript characters found")

        except Exception as e:
            print(f"   ERROR reading {csv_file}: {e}")

    print("\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"   Files analyzed: {len(main_csv_files)}")
    print(f"   Files with issues: {len(issues_by_file)}")
    print(f"   Total superscript characters: {total_issues}")

    if issues_by_file:
        print(f"\nFILES REQUIRING FIXES:")
        for file_path, issues in issues_by_file.items():
            print(f"   {file_path}:")
            for char, count in issues:
                print(f"      - '{char}': {count} times")
    else:
        print(f"\nSUCCESS: NO SUPERSCRIPT ISSUES FOUND IN MAIN CSV FILES!")

    return issues_by_file, total_issues

if __name__ == "__main__":
    issues, total = detect_superscript_characters()

    if total == 0:
        print(f"\nSUCCESS: All main CSV files are clean!")
        exit(0)
    else:
        print(f"\nACTION REQUIRED: {total} superscript characters need fixing")
        exit(1)