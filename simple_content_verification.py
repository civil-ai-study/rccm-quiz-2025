#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from collections import defaultdict

project_root = os.path.dirname(__file__)
data_dir = os.path.join(project_root, 'data')

def analyze_id_conflicts():
    """ID衝突の詳細分析"""
    print("ID衝突詳細分析開始...")
    
    all_questions = []
    
    # 4-1基礎データ
    basic_file = os.path.join(data_dir, '4-1.csv')
    if os.path.exists(basic_file):
        df = pd.read_csv(basic_file, encoding='utf-8')
        for _, row in df.iterrows():
            all_questions.append({
                'source': '4-1.csv',
                'original_id': row.get('id'),
                'category': row.get('category', 'Unknown'),
                'question': str(row.get('question', ''))[:100],
                'type': 'basic'
            })
        print(f"4-1: {len(df)}問読み込み")
    
    # 4-2専門データ
    for year in range(2008, 2019):
        file_path = os.path.join(data_dir, f'4-2_{year}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='utf-8')
            for _, row in df.iterrows():
                all_questions.append({
                    'source': f'4-2_{year}.csv',
                    'original_id': row.get('id'),
                    'category': row.get('category', 'Unknown'),
                    'question': str(row.get('question', ''))[:100],
                    'type': 'specialist',
                    'year': year
                })
            print(f"4-2_{year}: {len(df)}問読み込み")
    
    print(f"総問題数: {len(all_questions)}問")
    
    # ID別にグループ化
    id_groups = defaultdict(list)
    for q in all_questions:
        id_groups[q['original_id']].append(q)
    
    # ID衝突分析
    conflicts = []
    for original_id, questions in id_groups.items():
        if len(questions) > 1:
            # 異なる問題文があるかチェック
            question_texts = set([q['question'] for q in questions])
            categories = set([q['category'] for q in questions])
            
            if len(question_texts) > 1 or len(categories) > 1:
                conflicts.append({
                    'id': original_id,
                    'count': len(questions),
                    'sources': [q['source'] for q in questions],
                    'categories': list(categories),
                    'different_questions': len(question_texts),
                    'sample_questions': list(question_texts)[:3]
                })
    
    print(f"\nID衝突検出: {len(conflicts)}件")
    
    # 重大な衝突（異なる問題文）を表示
    serious_conflicts = [c for c in conflicts if c['different_questions'] > 1]
    print(f"深刻な内容衝突: {len(serious_conflicts)}件")
    
    if serious_conflicts:
        print(f"\n=== 深刻なID衝突例 ===")
        for conflict in serious_conflicts[:5]:
            print(f"\nID {conflict['id']}:")
            print(f"  出現回数: {conflict['count']}")
            print(f"  ソース: {', '.join(conflict['sources'])}")
            print(f"  カテゴリ: {', '.join(conflict['categories'])}")
            print(f"  異なる問題文数: {conflict['different_questions']}")
            for i, question in enumerate(conflict['sample_questions']):
                print(f"  問題{i+1}: {question}...")
    
    # 結果をファイル出力
    with open('id_conflicts_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(f"ID衝突分析結果\n")
        f.write(f"================\n")
        f.write(f"総問題数: {len(all_questions)}\n")
        f.write(f"ID衝突件数: {len(conflicts)}\n")
        f.write(f"深刻な内容衝突: {len(serious_conflicts)}\n\n")
        
        f.write("深刻な衝突詳細:\n")
        for conflict in serious_conflicts[:10]:
            f.write(f"\nID {conflict['id']}:\n")
            f.write(f"  出現: {conflict['count']}回\n")
            f.write(f"  ソース: {', '.join(conflict['sources'])}\n")
            f.write(f"  カテゴリ: {', '.join(conflict['categories'])}\n")
            for i, question in enumerate(conflict['sample_questions']):
                f.write(f"  問題{i+1}: {question}\n")
    
    return len(serious_conflicts) > 0

if __name__ == "__main__":
    try:
        has_conflicts = analyze_id_conflicts()
        
        if has_conflicts:
            print("\n[結論] 重大なID衝突による内容混在を検出")
            print("ユーザー報告「問題文と選択肢が異なる」は正確")
        else:
            print("\n[結論] 深刻なID衝突は検出されませんでした")
        
        print("詳細結果: id_conflicts_analysis.txt")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()