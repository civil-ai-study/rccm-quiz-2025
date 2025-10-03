"""
専門科目（4-2シリーズ）CSVファイルの信頼性検証
- 解答分布の確認
- 計算問題の抽出
- 短すぎる解説の検出
"""
import csv
import os
from collections import defaultdict
import json

def verify_specialist_csvs():
    """専門科目CSV全体の検証"""
    csv_files = [f for f in os.listdir('data') if f.startswith('4-2_') and f.endswith('.csv')]

    report = {
        'total_files': len(csv_files),
        'files': {}
    }

    print('=== Specialist CSV Verification Report ===\n')

    for csv_file in sorted(csv_files):
        path = os.path.join('data', csv_file)
        file_report = verify_single_file(path, csv_file)
        report['files'][csv_file] = file_report

    # レポート保存
    with open('specialist_csv_verification_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('\n=== Summary ===')
    print(f'Total files checked: {report["total_files"]}')

    # 異常な偏りのあるファイルをリスト
    biased_files = []
    for filename, file_info in report['files'].items():
        max_pct = max(file_info['answer_distribution_percent'].values())
        if max_pct > 40:
            biased_files.append((filename, max_pct))

    if biased_files:
        print(f'\nFiles with biased answers (>40%):')
        for filename, pct in sorted(biased_files, key=lambda x: x[1], reverse=True):
            print(f'  - {filename}: {pct:.1f}%')

    print('\nReport saved: specialist_csv_verification_report.json')

def verify_single_file(path, filename):
    """単一CSVファイルの検証"""
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 解答分布
    answer_dist = defaultdict(int)
    for row in rows:
        answer = row.get('correct_answer', '').strip()
        if answer:
            answer_dist[answer] += 1

    total = sum(answer_dist.values())

    # パーセンテージ計算
    answer_pct = {}
    for ans in ['A', 'B', 'C', 'D']:
        count = answer_dist.get(ans, 0)
        pct = (count/total*100) if total > 0 else 0
        answer_pct[ans] = pct

    # 計算問題の検出（数式を含む問題）
    calculation_questions = []
    for idx, row in enumerate(rows, 1):
        question_text = row.get('question', '')
        explanation = row.get('explanation', '')

        # 数式キーワード
        calc_keywords = ['計算', '求め', '算出', '=', '×', '÷', 'm²', 'km', 'kN', 'm/s']

        if any(kw in question_text or kw in explanation for kw in calc_keywords):
            calculation_questions.append({
                'row': idx,
                'id': row.get('id', ''),
                'question_preview': question_text[:50]
            })

    # 短い解説の検出
    short_explanations = []
    for idx, row in enumerate(rows, 1):
        explanation = row.get('explanation', '').strip()
        if len(explanation) < 20:
            short_explanations.append({
                'row': idx,
                'id': row.get('id', ''),
                'explanation': explanation,
                'length': len(explanation)
            })

    file_report = {
        'total_questions': total,
        'answer_distribution': dict(answer_dist),
        'answer_distribution_percent': answer_pct,
        'max_bias': max(answer_pct.values()),
        'calculation_questions_count': len(calculation_questions),
        'short_explanations_count': len(short_explanations),
        'calculation_questions': calculation_questions[:5],  # 最初の5件
        'short_explanations': short_explanations[:5]  # 最初の5件
    }

    # コンソール出力
    print(f'\n--- {filename} ---')
    print(f'Total questions: {total}')
    print(f'Answer distribution: ', end='')
    for ans in ['A', 'B', 'C', 'D']:
        print(f'{ans}={answer_dist.get(ans, 0)}({answer_pct[ans]:.1f}%) ', end='')
    print()

    if file_report['max_bias'] > 40:
        print(f'  WARNING: Max bias {file_report["max_bias"]:.1f}%')

    print(f'Calculation questions: {len(calculation_questions)}')
    print(f'Short explanations (<20 chars): {len(short_explanations)}')

    return file_report

if __name__ == '__main__':
    verify_specialist_csvs()
