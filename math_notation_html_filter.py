#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mathematical Notation HTML Filter for Flask
数学記法をHTMLの<sup><sub>タグに自動変換するフィルター
"""
import re

def create_math_notation_filter():
    """数学記法を正しいHTMLに変換するFlaskテンプレートフィルター"""

    def math_notation_to_html(text):
        """
        数学記法を正しいHTMLの<sup><sub>タグに変換
        例: I=πd4/32 → I=πd<sup>4</sup>/32
        """
        if not text:
            return text

        # 変換ルール
        conversions = []

        # 1. Unicode上付き文字をHTMLに変換
        unicode_superscripts = {
            '²': '<sup>2</sup>',
            '³': '<sup>3</sup>',
            '¹': '<sup>1</sup>',
            '⁰': '<sup>0</sup>',
            '⁴': '<sup>4</sup>',
            '⁵': '<sup>5</sup>',
            '⁶': '<sup>6</sup>',
            '⁷': '<sup>7</sup>',
            '⁸': '<sup>8</sup>',
            '⁹': '<sup>9</sup>'
        }

        # 2. Unicode下付き文字はそのまま保持（化学式用）
        # CO₂, H₂O, A₁v₁=A₂v₂ などは正しい表記として保持

        # 3. 数学式パターンの検出と変換 - ULTRATHIN 完全網羅対応版
        math_patterns = [
            # 【最優先】データ誤り修正（LaTeX処理前に実行）ULTRA SYNC拡張版
            # 基本パターン: 6^{4} → 64, 15^{7} → 157, 17^{6} → 176, 19^{6} → 196, 26^{4} → 264
            (r'6\^\{4\}', r'64'),
            (r'15\^\{7\}', r'157'),
            (r'17\^\{6\}', r'176'),
            (r'19\^\{6\}', r'196'),
            (r'26\^\{4\}', r'264'),

            # ULTRA SYNC発見追加パターン: 1^{2}→12, 1^{6}→16, 1^{8}→18等
            (r'1\^\{2\}', r'12'),
            (r'1\^\{6\}', r'16'),
            (r'1\^\{8\}', r'18'),
            (r'2\^\{4\}', r'24'),
            (r'3\^\{5\}', r'35'),
            (r'3\^\{6\}', r'36'),
            (r'9\^\{6\}', r'96'),
            (r'9\^\{8\}', r'98'),
            (r'10\^\{8\}', r'108'),
            (r'22\^\{8\}', r'228'),
            (r'34\^\{8\}', r'348'),
            (r'201\^\{2\}', r'2012'),

            # CSV追加発見パターン: 0.3^{5}→0.35, 0.7^{5}→0.75, 1.^{5}→1.5等
            (r'0\.3\^\{5\}', r'0.35'),
            (r'0\.7\^\{5\}', r'0.75'),
            (r'1\.\^\{2\}', r'1.2'),
            (r'1\.\^\{5\}', r'1.5'),
            (r'1\.4\^\{5\}', r'1.45'),
            (r'0\.\^\{5\}', r'0.5'),

            # 【次優先】LaTeX記法の完全変換
            # ^{4} → <sup>4</sup>, ^{-3} → <sup>-3</sup>
            (r'\^\{([^}]+)\}', r'<sup>\1</sup>'),
            # _{2} → <sub>2</sub>, _{n+1} → <sub>n+1</sub>
            (r'_\{([^}]+)\}', r'<sub>\1</sub>'),

            # 【超優先】科学記数法の完全修正
            # 2×10^-4 → 2×10<sup>-4</sup>
            (r'(\d+(?:\.\d+)?×10)\^(-?\d+)', r'\1<sup>\2</sup>'),
            # 10^{-3} → 10<sup>-3</sup>は上で処理済み

            # 【次優先】単純LaTeX記法
            # ^2 → <sup>2</sup>, _1 → <sub>1</sub>
            (r'\^(-?\d+)', r'<sup>\1</sup>'),
            (r'_(-?\d+)', r'<sub>\1</sub>'),

            # 【工学単位最優先】N/mm2, kN/m3, kPa等
            # 500N/mm2 → 500N/mm<sup>2</sup>
            (r'([0-9.]+N/mm)([2-9])', r'\1<sup>\2</sup>'),
            # 24.5kN/m3 → 24.5kN/m<sup>3</sup>
            (r'([0-9.]+kN/m)([2-9])', r'\1<sup>\2</sup>'),
            # 一般的なN/mm, kN/m記法
            (r'(N/mm)([2-9])', r'\1<sup>\2</sup>'),
            (r'(kN/m)([2-9])', r'\1<sup>\2</sup>'),

            # 【密度・体積単位】kg/m3, g/cm3, t/m3
            (r'([0-9.]*kg/m)([2-9])', r'\1<sup>\2</sup>'),
            (r'([0-9.]*g/cm)([2-9])', r'\1<sup>\2</sup>'),
            (r'([0-9.]*t/m)([2-9])', r'\1<sup>\2</sup>'),

            # 【流量単位】m^{3}/s → m<sup>3</sup>/s
            (r'(m)\^?\{?([0-9])\}?(/s)', r'\1<sup>\2</sup>\3'),

            # 【専用単位記法】
            # m/s2 → m/s<sup>2</sup>
            (r'(m/s)([2-9])', r'\1<sup>\2</sup>'),

            # 【一般工学単位】kN/m2, MPa, GPa等
            (r'([a-zA-Z]+/[a-zA-Z]+)([2-9])', r'\1<sup>\2</sup>'),

            # 【面積・体積・慣性モーメント単位】
            # 400cm2 → 400cm<sup>2</sup>, 60cm4 → 60cm<sup>4</sup>
            (r'(\d+cm)([2-9])', r'\1<sup>\2</sup>'),
            (r'(\d+mm)([2-9])', r'\1<sup>\2</sup>'),

            # 【一般的な変数の指数】
            # v2=2gh → v<sup>2</sup>=2gh, bh3/12 → bh<sup>3</sup>/12
            (r'([a-zA-Zπγρσ])([2-9])([/=\+\-\*\s])', r'\1<sup>\2</sup>\3'),

            # 【括弧後の指数】
            # (10cm)3 → (10cm)<sup>3</sup>
            (r'(\))([2-9])([/=\+\-\*\s])', r'\1<sup>\2</sup>\3'),

            # 【数学記号・ギリシャ文字パターン】
            # ×105 → ×10<sup>5</sup>
            (r'(×\d+)([2-9])', r'\1<sup>\2</sup>'),

            # π関連: πd4/32 → πd<sup>4</sup>/32
            (r'(π[a-zA-Z])([2-9])([/=])', r'\1<sup>\2</sup>\3'),

            # 【特殊修正】不正LaTeX記法・誤記修正
            # 9.^{8} → 9.8, 24.^{5} → 24.5 (ドット後の不正上付き)
            (r'(\d+)\.\^?\{?([0-9])\}?', r'\1.\2'),

            # 【体積単位完全対応】cm3, mm3, m3 → cm³, mm³, m³
            (r'(\d*cm)3', r'\1³'),
            (r'(\d*mm)3', r'\1³'),
            (r'(\d*m)3(?![0-9])', r'\1³'),  # m30のような数字が続かない場合のみ

            # 【面積単位完全対応】cm2, mm2, m2 → cm², mm², m²
            (r'(\d*cm)2', r'\1²'),
            (r'(\d*mm)2', r'\1²'),
            (r'(\d*m)2(?![0-9])', r'\1²'),  # m20のような数字が続かない場合のみ

            # 【科学記数法完全復旧】ULTRA SYNC発見：systematic degradation修正
            # ×105 → ×10⁵, 2.0×105 → 2.0×10⁵
            (r'(×10)5', r'\1⁵'),
            (r'(×10)4', r'\1⁴'),
            (r'(×10)3', r'\1³'),
            (r'(×10)2', r'\1²'),
            (r'(×10)6', r'\1⁶'),
            (r'(×10)7', r'\1⁷'),
            (r'(×10)8', r'\1⁸'),
            (r'(×10)9', r'\1⁹'),
            # 負の指数
            (r'(×10)-1', r'\1⁻¹'),
            (r'(×10)-2', r'\1⁻²'),
            (r'(×10)-3', r'\1⁻³'),
            (r'(×10)-4', r'\1⁻⁴'),
            (r'(×10)-5', r'\1⁻⁵'),
            (r'(×10)-6', r'\1⁻⁶'),

            # 【指数表記統一強化】10^-3, 10^{-3}, 10^-6等 → 10⁻³, 10⁻⁶等
            (r'10\^{?-([0-9])}?', r'10⁻\1'),
            (r'10\^{?([0-9])}?', r'10^\1'),

            # 【単位記号完全復旧】N/mm2 → N/mm², kN/m3 → kN/m³
            (r'N/mm2', r'N/mm²'),
            (r'kN/m2', r'kN/m²'),
            (r'kN/m3', r'kN/m³'),
            (r'kPa', r'kPa'),  # kPaは正しいのでそのまま
            (r'MPa', r'MPa'),  # MPaは正しいのでそのまま
            (r'GPa', r'GPa'),  # GPaは正しいのでそのまま

            # 【体積・面積単位復旧】cm3→cm³, mm3→mm³, m3→m³, cm2→cm², mm2→mm², m2→m²
            (r'([0-9.]*)cm3', r'\1cm³'),
            (r'([0-9.]*)mm3', r'\1mm³'),
            (r'([0-9.]*)m3(?![0-9])', r'\1m³'),
            (r'([0-9.]*)cm2', r'\1cm²'),
            (r'([0-9.]*)mm2', r'\1mm²'),
            (r'([0-9.]*)m2(?![0-9])', r'\1m²'),

            # 【CRITICAL FIX】数学記号不一致修正 - UI Testing発見問題対応
            # ｙ＝L^{2}/8R, ｙ＝R/8L2 → y=L²/8R, y=R/8L² (全角文字と指数表記統一)
            (r'ｙ＝', r'y='),  # 全角y修正
            (r'L\^{2}', r'L²'),  # LaTeX記法をUnicode上付き文字に統一
            (r'L2([^0-9])', r'L²\\1'),  # L2 → L² (数字が続かない場合)
            (r'R/8L2', r'R/8L²'),  # 特定の不一致修正

            # 【全角文字統一】ULTRA SYNC発見パターン完全網羅
            # 括弧統一: （） → ()
            (r'（', r'('),
            (r'）', r')'),

            # 全角スラッシュ統一: ／ → /
            (r'／', r'/'),

            # 全角数字統一: ０１２３４５６７８９ → 0123456789
            (r'０', r'0'), (r'１', r'1'), (r'２', r'2'), (r'３', r'3'), (r'４', r'4'),
            (r'５', r'5'), (r'６', r'6'), (r'７', r'7'), (r'８', r'8'), (r'９', r'9'),

            # 全角英字統一: ＡＢＣ等 → ABC等
            (r'ａ', r'a'), (r'ｂ', r'b'), (r'ｃ', r'c'), (r'ｄ', r'd'),
            (r'ｅ', r'e'), (r'ｆ', r'f'), (r'ｇ', r'g'), (r'ｈ', r'h'),
            (r'ｉ', r'i'), (r'ｊ', r'j'), (r'ｋ', r'k'), (r'ｌ', r'l'),
            (r'ｍ', r'm'), (r'ｎ', r'n'), (r'ｏ', r'o'), (r'ｐ', r'p'),
            (r'ｑ', r'q'), (r'ｒ', r'r'), (r'ｓ', r's'), (r'ｔ', r't'),
            (r'ｕ', r'u'), (r'ｖ', r'v'), (r'ｗ', r'w'), (r'ｘ', r'x'),
            (r'ｙ', r'y'), (r'ｚ', r'z'),
            (r'Ａ', r'A'), (r'Ｂ', r'B'), (r'Ｃ', r'C'), (r'Ｄ', r'D'),
            (r'Ｅ', r'E'), (r'Ｆ', r'F'), (r'Ｇ', r'G'), (r'Ｈ', r'H'),
            (r'Ｉ', r'I'), (r'Ｊ', r'J'), (r'Ｋ', r'K'), (r'Ｌ', r'L'),
            (r'Ｍ', r'M'), (r'Ｎ', r'N'), (r'Ｏ', r'O'), (r'Ｐ', r'P'),
            (r'Ｑ', r'Q'), (r'Ｒ', r'R'), (r'Ｓ', r'S'), (r'Ｔ', r'T'),
            (r'Ｕ', r'U'), (r'Ｖ', r'V'), (r'Ｗ', r'W'), (r'Ｘ', r'X'),
            (r'Ｙ', r'Y'), (r'Ｚ', r'Z'),

            # 単位記号の全角文字統一: ｃｍ → cm, ｍ → m
            (r'ｃｍ', r'cm'), (r'ｍｍ', r'mm'), (r'ｍ', r'm'),

            # 【土木工学専用】質量記号の下付き文字統一
            # ms, mw → m<sub>s</sub>, m<sub>w</sub>
            # ｍs, ｍw → m<sub>s</sub>, m<sub>w</sub> (全角m対応)
            (r'([^a-zA-Z]|^)(ｍ|m)(s)([^a-zA-Z]|$)', r'\1m<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(ｍ|m)(w)([^a-zA-Z]|$)', r'\1m<sub>\3</sub>\4'),

            # 【ギリシャ文字下付き文字統一】ULTRA SYNC追加修正
            # ρs, ρw, ρd → ρ<sub>s</sub>, ρ<sub>w</sub>, ρ<sub>d</sub>
            (r'([^a-zA-Z]|^)(ρ)(s)([^a-zA-Z]|$)', r'\1ρ<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(ρ)(w)([^a-zA-Z]|$)', r'\1ρ<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(ρ)(d)([^a-zA-Z]|$)', r'\1ρ<sub>\3</sub>\4'),

            # γs, γw, γd, γt, γt1, γt2 → γ<sub>s</sub>, γ<sub>w</sub>, γ<sub>d</sub>, γ<sub>t</sub>, γ<sub>t1</sub>, γ<sub>t2</sub>
            (r'([^a-zA-Z]|^)(γ)(s)([^a-zA-Z]|$)', r'\1γ<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(γ)(w)([^a-zA-Z]|$)', r'\1γ<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(γ)(d)([^a-zA-Z]|$)', r'\1γ<sub>\3</sub>\4'),
            (r'([^a-zA-Z]|^)(γ)(t[0-9]*)([^a-zA-Z]|$)', r'\1γ<sub>\3</sub>\4'),

            # σs, σw, σ1, σ2, σ3 → σ<sub>s</sub>, σ<sub>w</sub>, σ<sub>1</sub>, σ<sub>2</sub>, σ<sub>3</sub>
            (r'([^a-zA-Z]|^)(σ)(s|w|[0-9])([^a-zA-Z]|$)', r'\1σ<sub>\3</sub>\4'),

            # αs, αw, βs, βw → α<sub>s</sub>, α<sub>w</sub>, β<sub>s</sub>, β<sub>w</sub>
            (r'([^a-zA-Z]|^)(α|β)(s|w)([^a-zA-Z]|$)', r'\1\2<sub>\3</sub>\4'),

            # 【三角関数逆関数】cos-1, sin-1, tan-1 → cos<sup>-1</sup>, sin<sup>-1</sup>, tan<sup>-1</sup>
            (r'(cos|sin|tan)-1', r'\1<sup>-1</sup>'),

            # 【問題文の選択肢表記統一】a～d → A～D（問題文中の選択肢参照）
            (r'のをa～d', r'のをA～D'),
            (r'をa～dの', r'をA～Dの'),
            (r'からa～d', r'からA～D'),
        ]

        result = text

        # Unicode上付き文字を変換
        for unicode_char, html_replacement in unicode_superscripts.items():
            result = result.replace(unicode_char, html_replacement)

        # 数学式パターンを変換
        for pattern, replacement in math_patterns:
            result = re.sub(pattern, replacement, result)

        return result

    return math_notation_to_html

def add_math_filter_to_app(app):
    """Flaskアプリにmathフィルターを追加"""
    math_filter = create_math_notation_filter()

    @app.template_filter('math')
    def math_notation_filter(text):
        return math_filter(text)

    return app

# テスト用の例
if __name__ == "__main__":
    filter_func = create_math_notation_filter()

    test_cases = [
        "I=bh3/12=(6cm)(10cm)3/12=500cm4",
        "I=πd^{4}/32",  # LaTeX記法テスト
        "I=πd4/32",
        "v2=2gh",
        "2.0×10^{5}N/mm^{2}",  # LaTeX記法テスト
        "9.8m/s^{2}",  # LaTeX記法テスト
        "A₁v₁=A₂v₂",  # 下付き文字は保持
        "CO₂",  # 化学式は保持
        "重力加速度を9.8m/s2とする",
        "9.^{8}×2.0=19600Pa",  # 不正LaTeX修正テスト
        "24.^{5}kN/m3",  # 不正LaTeX修正テスト
        "500N/mm2～1000N/mm2",  # 工学単位テスト
        "100cm3",  # 体積単位テスト
        "360kg/m3",  # 密度単位テスト
        "1000kg/m3",  # 密度単位テスト（スクリーンショット1対応）
        "2400kg/m3",  # 密度単位テスト強化
        "2×10^-4 m^{3}/s",  # 科学記数法テスト
        # ULTRA SYNC追加テスト - ギリシャ文字下付き文字
        "含水比w=mw/ms×100(％)、土粒子の密度ρs=ms/Vs(g/cm3)、間隙比e=Vv/Vs",  # ρs テスト
        "乾燥密度ρdと含水比wの両方から算定される",  # ρd テスト
        "安全率はFs=(γ1h1+γ2h2)/γwhwで算定されます",  # γw テスト
        "応力σ1、σ2、σ3の主応力関係",  # σ1,σ2,σ3 テスト
        "内部摩擦角φ、粘着力c、αs、βwの関係",  # α,β テスト

        # ULTRA SYNC発見パターン - 科学記数法・単位記号劣化修正
        "ヤング係数は2.0×105N/mm2である",  # 2.0×105 → 2.0×10⁵, N/mm2 → N/mm²
        "単位重量は77.0kN/m3である",  # kN/m3 → kN/m³
        "断面係数は100cm3である",  # cm3 → cm³
        "面積は500cm2である",  # cm2 → cm²

        # ULTRA SYNC発見パターン - 全角文字統一
        "焦点距離３０ｃｍのカメラで",  # ３０ → 30, ｃｍ → cm
        "ＴＰ+１５ｍの高さ",  # Ｔ → T, Ｐ → P, １５ → 15, ｍ → m
        "正しいものをａ～ｄのなかから",  # ａ～ｄ → a～d
        "土の密度ρd＝ms／V（g／cm3）",  # ／ → /、（） → ()

        # ULTRA SYNC発見パターン - 無効LaTeX記法修正
        "連続の式より0.^{5}=π(0.05)^{2}×v₂",  # 0.^{5} → 0.5
    ]

    print("MATH NOTATION HTML FILTER TEST")
    print("=" * 50)

    for test in test_cases:
        result = filter_func(test)
        print(f"入力: {test}")
        print(f"出力: {result}")
        print()