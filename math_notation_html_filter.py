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

        # 3. 数学式パターンの検出と変換 - ULTRATHIN LaTeX完全対応版
        math_patterns = [
            # 【最優先】LaTeX記法の完全変換
            # ^{4} → <sup>4</sup>, ^{-3} → <sup>-3</sup>
            (r'\^\{([^}]+)\}', r'<sup>\1</sup>'),
            # _{2} → <sub>2</sub>, _{n+1} → <sub>n+1</sub>
            (r'_\{([^}]+)\}', r'<sub>\1</sub>'),

            # 【次優先】単純LaTeX記法
            # ^2 → <sup>2</sup>, _1 → <sub>1</sub>
            (r'\^([0-9]+)', r'<sup>\1</sup>'),
            (r'_([0-9]+)', r'<sub>\1</sub>'),

            # 【優先度1】専用単位記法
            # m/s2 → m/s<sup>2</sup>
            (r'(m/s)([2-9])', r'\1<sup>\2</sup>'),

            # kN/m2, kN/m3, kN/m4 などの工学単位 (発見済み)
            (r'([a-zA-Z]+/[a-zA-Z]+)([2-9])', r'\1<sup>\2</sup>'),

            # 【優先度2】面積・体積・慣性モーメント単位 (大量発見済み)
            # 400cm2 → 400cm<sup>2</sup>, 60cm4 → 60cm<sup>4</sup>
            (r'(\d+cm)([2-9])', r'\1<sup>\2</sup>'),
            (r'(\d+mm)([2-9])', r'\1<sup>\2</sup>'),

            # 【優先度3】一般的な変数の指数
            # v2=2gh → v<sup>2</sup>=2gh, bh3/12 → bh<sup>3</sup>/12
            (r'([a-zA-Zπ])([2-9])([/=\+\-\*\s])', r'\1<sup>\2</sup>\3'),

            # 【優先度4】括弧後の指数
            # (10cm)3 → (10cm)<sup>3</sup>
            (r'(\))([2-9])([/=\+\-\*\s])', r'\1<sup>\2</sup>\3'),

            # 【優先度5】数学記号・ギリシャ文字パターン (調査で発見済み)
            # ×105 → ×10<sup>5</sup>
            (r'(×\d+)([2-9])', r'\1<sup>\2</sup>'),

            # π関連: πd4/32 → πd<sup>4</sup>/32
            (r'(π[a-zA-Z])([2-9])([/=])', r'\1<sup>\2</sup>\3'),

            # 【優先度6】科学記数法 - 拡張版
            # 2.0×10^5 → 2.0×10<sup>5</sup>
            (r'(\d+(?:\.\d+)?×10)\^([0-9\-]+)', r'\1<sup>\2</sup>'),

            # 10^{-3} → 10<sup>-3</sup> (既に上で処理済み)
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
        "重力加速度を9.8m/s2とする"
    ]

    print("MATH NOTATION HTML FILTER TEST")
    print("=" * 50)

    for test in test_cases:
        result = filter_func(test)
        print(f"入力: {test}")
        print(f"出力: {result}")
        print()