"""
4-2_2017.csv の重要な計算問題解説の詳細化
Web検索で確認した技術基準に基づき、正確で詳細な解説を追加
"""
import csv
import shutil

def enhance_explanations():
    """解説の詳細化"""
    csv_path = 'data/4-2_2017.csv'

    # バックアップ作成
    backup_path = csv_path + '.backup_before_explanation_enhancement'
    shutil.copy2(csv_path, backup_path)
    print(f'[BACKUP] {backup_path}')

    # CSV読み込み
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # 修正対象の問題と新しい解説
    enhancements = {
        # ID=44: 標準貫入試験（貫入不能の定義）- JIS A 1219:2013準拠
        '44': {
            'old': 'JIS A 1219における貫入不能の定義は本打ちで50回打撃により30mm未満の貫入量の場合です',
            'new': '標準貫入試験(JIS A 1219:2013)における貫入不能の定義：本打ちにおいて50回の打撃に対して累計貫入量が30mm未満の場合。試験ではハンマー質量63.5kg、落下高76cmの条件で実施し、30cm貫入に要する打撃回数をN値として記録します。'
        },

        # ID=52: 土の物理量（含水比・土粒子密度・間隙比）
        '52': {
            'old': '含水比w=mw/ms×100%土粒子の密度ρs=ms/Vs間隙比e=Vv/Vsが正しい定義です',
            'new': '土の基本的物理量の定義：含水比w=mw/ms×100(%)は水の質量を土粒子質量で除した値、土粒子密度ρs=ms/Vs(g/cm³)は土粒子質量を土粒子体積で除した値、間隙比e=Vv/Vsは間隙体積を土粒子体積で除した値。これらは地盤の力学特性を評価する基本パラメータです。'
        },

        # ID=46: 各種サウンディング試験
        '46': {
            'old': '原位置ベーンせん断試験は主に軟弱な粘性土地盤を対象とし砂質土地盤には適用されません',
            'new': '原位置ベーンせん断試験は軟弱な粘性土地盤のせん断強度評価に用いられますが、砂質土地盤には適用できません。砂質土では供試体が崩れやすく測定不能となるため、粘性土の非排水せん断強度測定に特化した試験方法です。'
        },

        # ID=50: 軟弱地盤の分布
        '50': {
            'old': '後背湿地は河川の氾濫により形成される低平地で、細粒分が堆積しやすく、有機質土や粘性土が分布する。軟弱地盤の代表的な分布位置である。',
            'new': '沖積平野における軟弱地盤の分布：後背湿地は河川の氾濫により形成される低平地で、流速が遅く細粒分(シルト・粘土)が堆積しやすい環境です。その結果、有機質土や軟弱な粘性土が厚く分布し、N値<4の極軟弱地盤となることが多く、軟弱地盤対策が必要です。'
        },

        # ID=54: 土量変化率
        '54': {
            'old': '地山を構成する土質が複数層の場合各土質の変化率を単純な比率計算で求めることはできません',
            'new': '土量変化率の測定上の注意：地山土量が多くなると構成する土質が複数層から成ることが多いですが、各層の土質特性(粒度・密度・含水比)が異なるため、土質別の変化率を単純な体積比から厳密に算定することは困難です。各層ごとに実測することが望ましい。'
        }
    }

    # 解説を更新
    modified_count = 0
    for row in rows:
        problem_id = row.get('id', '').strip()
        if problem_id in enhancements:
            old_exp = enhancements[problem_id]['old']
            new_exp = enhancements[problem_id]['new']

            if row['explanation'] == old_exp:
                row['explanation'] = new_exp
                modified_count += 1
                print(f"[ENHANCED] ID={problem_id}: {len(old_exp)}→{len(new_exp)} chars")

    # CSV書き込み
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'\n[COMPLETE] Enhanced {modified_count} explanations in {csv_path}')

if __name__ == '__main__':
    enhance_explanations()
