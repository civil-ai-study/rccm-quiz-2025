#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask-WTF Configuration Solution
Flask-WTF設定でreferrer検証を無効化する方法
"""

def add_csrf_ssl_strict_config():
    """
    config.py に WTF_CSRF_SSL_STRICT = False を追加
    CSRF保護レベルを維持しながらreferrer検証を緩和
    """
    
    config_additions = """
    
# 🔧 CRITICAL FIX: Flask-WTF CSRF referrer header対応
# Render.com HTTPS環境での requests.Session() 対応
WTF_CSRF_SSL_STRICT = False        # referrer検証を緩和（HTTPSでも）
WTF_CSRF_CHECK_DEFAULT = True      # CSRF保護は維持
WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']  # 対象メソッド

# 追加セキュリティ設定
WTF_CSRF_FIELD_NAME = 'csrf_token' # CSRFフィールド名明示
SESSION_COOKIE_SECURE = True       # HTTPS環境でのセキュア設定
SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF攻撃対策
"""
    
    print("🔧 Flask-WTF設定解決策:")
    print("config.py に以下を追加してください:")
    print("-" * 50)
    print(config_additions)
    print("-" * 50)
    print()
    print("🎯 この設定の効果:")
    print("✅ CSRF保護は完全に維持")
    print("✅ referrer header検証のみ緩和")
    print("✅ requests.Session()でのPOST成功")
    print("✅ Render.com HTTPS環境対応")

def add_csrf_exempt_solution():
    """
    特定ルートでCSRF保護を部分的に無効化
    """
    
    app_py_additions = """
    
# Flask-WTF CSRFエラー回避（部分的無効化）
from flask_wtf.csrf import exempt

@app.route('/exam', methods=['POST'])
@exempt  # この1行でCSRF保護を無効化
def exam_post():
    # 既存のPOST処理...
    pass
"""
    
    print("⚠️ 代替案: 部分的CSRF無効化")
    print("app.py の /exam POST ルートに以下を追加:")
    print("-" * 50)
    print(app_py_additions)
    print("-" * 50)
    print()
    print("🚨 注意: この方法はセキュリティレベルが下がります")
    print("❌ CSRF攻撃に対して脆弱になる可能性")
    print("✅ 一時的な解決策としてのみ使用推奨")

def main():
    print("Flask-WTF CSRF Referrer Header 設定解決策")
    print("=" * 60)
    print()
    
    print("【推奨】解決策2A: WTF_CSRF_SSL_STRICT = False")
    add_csrf_ssl_strict_config()
    print()
    
    print("【非推奨】解決策2B: 部分的CSRF無効化")
    add_csrf_exempt_solution()

if __name__ == "__main__":
    main()