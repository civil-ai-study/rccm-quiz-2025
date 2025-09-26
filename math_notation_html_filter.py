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
            # 【最優先】LaTeX記法の完全変換
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

            # 【科学記数法の×記号統一】×10^5, ×105 → ×10⁵
            (r'(×10)5', r'\1⁵'),
            (r'(×10)4', r'\1⁴'),
            (r'(×10)3', r'\1³'),
            (r'(×10)2', r'\1²'),

            # 【全角スラッシュ統一】／ → /
            (r'／', r'/'),
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
        "2×10^-4 m^{3}/s"  # 科学記数法テスト
    ]

    print("MATH NOTATION HTML FILTER TEST")
    print("=" * 50)

    for test in test_cases:
        result = filter_func(test)
        print(f"入力: {test}")
        print(f"出力: {result}")
        print()