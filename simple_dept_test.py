#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple department test - post dictionary fix verification
"""
import sys
import os

# Add the application path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_departments():
    """Test all 13 departments after dictionary structure fix"""
    print("Testing all 13 departments after dictionary structure fix")
    print("=" * 60)

    departments = [
        'basic', 'road', 'river', 'urban', 'garden', 'env',
        'steel', 'soil', 'construction', 'water', 'forest',
        'agri', 'tunnel'
    ]

    results = {'success': [], 'error': []}

    with app.test_client() as client:
        for dept in departments:
            try:
                response = client.get(f'/departments/{dept}')
                if response.status_code in [200, 302]:
                    content = response.get_data(as_text=True)
                    if 'エラー' in content or '無効な部門ID' in content:
                        results['error'].append(f"{dept}: エラーページ表示")
                        print(f"❌ {dept}: エラーページ表示")
                    else:
                        results['success'].append(f"{dept}: 正常動作")
                        print(f"✅ {dept}: 正常動作")
                else:
                    results['error'].append(f"{dept}: HTTP {response.status_code}")
                    print(f"❌ {dept}: HTTP {response.status_code}")
            except Exception as e:
                results['error'].append(f"{dept}: 例外 - {str(e)}")
                print(f"❌ {dept}: 例外 - {str(e)}")

    # Summary
    print("\n" + "=" * 60)
    print("結果サマリー")
    print("=" * 60)

    success_count = len(results['success'])
    error_count = len(results['error'])
    total = len(departments)
    success_rate = (success_count / total) * 100

    print(f"✅ 正常動作: {success_count}/{total} ({success_rate:.1f}%)")
    print(f"❌ エラー: {error_count}/{total}")

    if success_count == total:
        print("🎉 完全成功: 全部門正常動作")
        return True
    else:
        print("⚠️ 一部に問題あり")
        return False

if __name__ == "__main__":
    test_departments()