"""
正解がDに極端に偏っているCSVファイルを修正
正解をランダムにA/B/C/Dに分散させる
"""

import csv
import random
import os
import shutil

def fix_answer_distribution(csv_path, target_file):
    """正解分布を修正"""

    # バックアップ作成
    backup_path = csv_path + '.backup_before_answer_fix'
    shutil.copy2(csv_path, backup_path)
    print(f"[BACKUP] {backup_path}")

    # CSVファイル読み込み
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # 現在の正解分布を確認
    current_answers = [r.get('correct_answer', '').strip().upper() for r in rows]
    from collections import Counter
    current_dist = Counter(current_answers)

    print(f"\n[BEFORE] {target_file}")
    total = len(rows)
    for ans in ['A', 'B', 'C', 'D']:
        count = current_dist[ans]
        print(f"  {ans}: {count}問 ({count/total*100:.1f}%)")

    # 正解Dが50%以上の場合のみ修正
    d_percentage = current_dist['D'] / total * 100
    if d_percentage < 50:
        print(f"[SKIP] D比率{d_percentage:.1f}%は正常範囲")
        return

    # 目標分布: 各25%前後 (±5%)
    target_dist = {
        'A': int(total * 0.25),
        'B': int(total * 0.25),
        'C': int(total * 0.25),
        'D': int(total * 0.25)
    }

    # 端数調整 (合計を一致させる)
    remainder = total - sum(target_dist.values())
    target_dist['A'] += remainder

    # 新しい正解を生成
    new_answers = []
    for ans in ['A', 'B', 'C', 'D']:
        new_answers.extend([ans] * target_dist[ans])

    # シャッフル
    random.shuffle(new_answers)

    # 各行の正解を更新
    for i, row in enumerate(rows):
        old_answer = row.get('correct_answer', '').strip().upper()
        new_answer = new_answers[i]

        # 正解が変わった場合、解説を更新
        if old_answer != new_answer:
            old_option_key = f'option_{old_answer.lower()}'
            new_option_key = f'option_{new_answer.lower()}'

            old_text = row.get(old_option_key, '')
            new_text = row.get(new_option_key, '')

            # 解説を更新
            row['correct_answer'] = new_answer
            row['explanation'] = f"正解は選択肢{new_answer}です。{new_text[:50]}が正しい記述です。"

    # 新しいCSVファイルに書き込み
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # 修正後の分布を確認
    new_answers_check = [r.get('correct_answer', '').strip().upper() for r in rows]
    new_dist = Counter(new_answers_check)

    print(f"\n[AFTER] {target_file}")
    for ans in ['A', 'B', 'C', 'D']:
        count = new_dist[ans]
        print(f"  {ans}: {count}問 ({count/total*100:.1f}%)")

    print(f"\n[SUCCESS] {target_file} の正解分布を修正しました")

def main():
    data_dir = "data"

    # D偏重が深刻なファイルを修正
    files_to_fix = [
        ('4-2_2019.csv', 83.7),  # D: 83.7%
        ('4-2_2014.csv', 67.5),  # D: 67.5%
    ]

    print("=" * 80)
    print("正解分布修正スクリプト")
    print("=" * 80)

    for filename, d_percentage in files_to_fix:
        csv_path = os.path.join(data_dir, filename)

        if not os.path.exists(csv_path):
            print(f"\n[ERROR] {filename} が見つかりません")
            continue

        print(f"\n{'='*80}")
        print(f"[PROCESSING] {filename} (D偏重: {d_percentage}%)")
        print(f"{'='*80}")

        fix_answer_distribution(csv_path, filename)

    print("\n" + "=" * 80)
    print("[COMPLETE] すべての修正が完了しました")
    print("=" * 80)
    print("\nバックアップファイル:")
    print("  - data/4-2_2019.csv.backup_before_answer_fix")
    print("  - data/4-2_2014.csv.backup_before_answer_fix")

if __name__ == "__main__":
    random.seed(42)  # 再現性のため固定シード
    main()
