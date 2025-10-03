"""
計算問題6問の解説を推奨案に修正
"""
import csv
import shutil

# バックアップ作成
shutil.copy2('data/4-1.csv', 'data/4-1.csv.backup_before_explanation_fix')

# 修正対象の問題と新しい解説
fixes = {
    # 問題21: 単純梁のモーメント (検索キーワードで特定)
    'P=10kN L=40m M=PL/4=100kN': '単純梁の固定端モーメント計算：荷重P=10kN、支間L=40mの場合、固定端モーメントM=P×L/4=10×40/4=100kN·m。梁の境界条件により固定端には曲げモーメントが発生します。',

    # 問題44: 速度換算
    '1km/h=1000m/3600s=0.28m/s': '速度の単位換算：1km/h = 1000m/3600s = 0.278m/s ≒ 0.28m/s。時速を秒速に換算する基本計算です。1時間=3600秒、1km=1000mを代入して計算します。',

    # 問題68: 相似形の面積比
    '面積比は辺の比の2乗に等しい。3': '相似な図形の面積比は辺の比の2乗：辺の比が3:5の場合、面積比=(3)²:(5)²=9:25。これは相似図形の基本定理で、面積比は対応する辺の比の2乗になります。',

    # 問題52: 縮尺と面積
    '縮尺の2乗倍 400×500': '縮尺図面の面積換算：図上面積400cm² × 縮尺分母の2乗 = 400cm² × (500)² = 100,000,000cm² = 10,000m²。面積は長さの2乗なので、縮尺も2乗して換算します。',

    # 問題11: ベルヌーイの定理
    'v^{2}=2gh より v=': '自由落下の流速計算（ベルヌーイの定理）：v²=2gh より v=√(2×g×h)=√(2×9.8m/s²×3.0m)=√58.8≒7.7m/s。静水面からの落差hと重力加速度g=9.8m/s²を用いて流出速度を求めます。',

    # 問題28: 水圧
    'P=γhA/2=9.8×4.0×(2.0×4.0)/2=156.8kN': '壁面に作用する全水圧：P=(γ×h×A)/2=(9.8kN/m³×4.0m×8.0m²)/2=156.8kN。水深hの壁面に作用する水圧は三角形分布となり、全水圧は平均水圧×面積で求めます。γは水の単位体積重量9.8kN/m³です。'
}

# CSVファイル読み込み
with open('data/4-1.csv', 'r', encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

# 修正実行
fixed_count = 0
for row in rows:
    explanation = row.get('explanation', '')
    for old_pattern, new_explanation in fixes.items():
        if old_pattern in explanation:
            row['explanation'] = new_explanation
            qid = row.get('id')
            print(f'[FIX] 問題{qid}: 解説を更新')
            fixed_count += 1
            break

# CSVファイル書き込み
with open('data/4-1.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n[完了] {fixed_count}問の解説を修正しました')
print('[バックアップ] data/4-1.csv.backup_before_explanation_fix')
