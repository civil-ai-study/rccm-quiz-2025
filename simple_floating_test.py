#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Floating Character Test - ASCII output only
"""
import requests
import re
import sys
import os

def test_floating_characters():
    """Test floating character issue fix"""

    base_url = "http://localhost:5050"

    print("Testing floating character fix...")
    print(f"Target URL: {base_url}")

    try:
        # Test exam page
        exam_url = f"{base_url}/exam?department=basic&question_count=10"
        response = requests.get(exam_url, timeout=10)

        if response.status_code != 200:
            print(f"ERROR: Failed to access exam page: {response.status_code}")
            return False

        print("SUCCESS: Exam page accessible")
        content = response.text

        # Check for floating characters
        floating_chars = ['²', '³', '¹', '⁰', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '⁺', '⁻']
        found_floating = []

        for char in floating_chars:
            if char in content:
                count = content.count(char)
                found_floating.append((char, count))
                print(f"FOUND floating character: '{char}' (count: {count})")

        if len(found_floating) == 0:
            print("SUCCESS: NO FLOATING CHARACTERS FOUND!")
            print("The math_notation filter removal is working correctly.")
            return True
        else:
            print(f"FAIL: Found {len(found_floating)} types of floating characters")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    os.chdir(r"C:\Users\ABC\Desktop\rccm-quiz-app")
    success = test_floating_characters()

    if success:
        print("\nFINAL RESULT: FLOATING CHARACTER FIX SUCCESSFUL!")
    else:
        print("\nFINAL RESULT: FLOATING CHARACTER FIX FAILED!")

    sys.exit(0 if success else 1)