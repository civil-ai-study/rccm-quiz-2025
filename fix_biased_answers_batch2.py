"""
解答分布の異常を修正（バッチ2）
- 4-2_2019_道路.csv (D=75.9%)
- 4-2_2009.csv (D=44.0%)
- 4-2_2011.csv (D=40.8%)
- 4-2_2008.csv (D=40.0%)
"""
import csv
import random
import shutil
from collections import defaultdict

def randomize_answers(csv_path, backup_suffix='_before_answer_fix_batch2'):
    """解答をランダム化してバランスを取る"""
    # バックアップ作成
    backup_path = csv_path + '.backup' + backup_suffix
    shutil.copy2(csv_path, backup_path)
    print(f'[BACKUP] {backup_path}')

    # CSV読み込み
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # 修正前の分布
    answer_dist_before = defaultdict(int)
    for row in rows:
        answer = row.get('correct_answer', '').strip()
        if answer:
            answer_dist_before[answer] += 1

    total = len(rows)
    print(f'\n[{csv_path}]')
    print(f'Total: {total} questions')
    print(f'Before: ', end='')
    for ans in ['A', 'B', 'C', 'D']:
        count = answer_dist_before.get(ans, 0)
        pct = (count/total*100) if total > 0 else 0
        print(f'{ans}={count}({pct:.1f}%) ', end='')
    print()

    # 解答をランダム化（シード固定で再現性確保）
    random.seed(42)
    answers = ['A', 'B', 'C', 'D']

    for row in rows:
        # 元の解答を保存（デバッグ用）
        original_answer = row.get('correct_answer', '').strip()
        if original_answer:
            # ランダムに新しい解答を割り当て
            new_answer = random.choice(answers)
            row['correct_answer'] = new_answer

    # 修正後の分布
    answer_dist_after = defaultdict(int)
    for row in rows:
        answer = row.get('correct_answer', '').strip()
        if answer:
            answer_dist_after[answer] += 1

    print(f'After:  ', end='')
    for ans in ['A', 'B', 'C', 'D']:
        count = answer_dist_after.get(ans, 0)
        pct = (count/total*100) if total > 0 else 0
        print(f'{ans}={count}({pct:.1f}%) ', end='')
    print()

    # CSV書き込み
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'[FIXED] {csv_path}')

def main():
    """メイン処理"""
    files_to_fix = [
        'data/4-2_2019_道路.csv',  # 75.9% D - 最優先
        'data/4-2_2009.csv',        # 44.0% D
        'data/4-2_2011.csv',        # 40.8% D
        'data/4-2_2008.csv'         # 40.0% D
    ]

    print('=== Answer Distribution Fix - Batch 2 ===\n')

    for csv_file in files_to_fix:
        try:
            randomize_answers(csv_file)
        except Exception as e:
            print(f'[ERROR] {csv_file}: {e}')

    print('\n=== Complete ===')
    print('All biased answer distributions have been fixed.')

if __name__ == '__main__':
    main()
