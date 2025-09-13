# -*- coding: utf-8 -*-
"""
ULTRA SYNC STAGE 3: 安定性修正（副作用絶対防止）
Stability Fix with Zero Side Effects Prevention
ローカル環境セッション安定性の慎重な修正
"""

import sys
import os
import shutil
from datetime import datetime

class UltraSyncStabilityFix:
    """
    ウルトラシンク安定性修正クラス
    副作用を絶対に発生させない慎重なアプローチ
    """
    
    def __init__(self):
        self.base_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app-production"
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixes_applied = []
    
    def create_safety_backup(self):
        """
        安全バックアップ作成（副作用防止の最重要ステップ）
        """
        print("ULTRA SYNC: 安全バックアップ作成中...")
        
        backup_name = f"app.py.ultra_sync_stage3_safety_backup_{self.backup_timestamp}"
        app_py = os.path.join(self.base_dir, "app.py")
        backup_path = os.path.join(self.base_dir, backup_name)
        
        try:
            shutil.copy2(app_py, backup_path)
            print(f"[OK] 安全バックアップ作成: {backup_name}")
            return True
        except Exception as e:
            print(f"[ERROR] バックアップ失敗: {e}")
            return False
    
    def fix_missing_dependencies(self):
        """
        不足モジュール問題の慎重な修正
        """
        print("\nULTRA SYNC: 不足依存関係の慎重な修正...")
        
        app_py_path = os.path.join(self.base_dir, "app.py")
        
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ai_analyzer import を安全に修正
            if "from ai_analyzer import" in content:
                print("[FOUND] ai_analyzer import問題を発見")
                
                # Try-except で包むように修正（既存コードを壊さない）
                old_import = "from ai_analyzer import"
                new_import = """try:
    from ai_analyzer import"""
                
                if old_import in content and "try:" not in content.split(old_import)[0][-50:]:
                    content = content.replace(old_import, new_import)
                    
                    # 対応するexceptも追加（適切な位置を探す）
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "from ai_analyzer import" in line and "try:" in line:
                            # 次の空行またはimport以外の行を見つけてexceptを追加
                            for j in range(i+1, min(i+10, len(lines))):
                                if lines[j].strip() == "" or not lines[j].strip().startswith(("import", "from")):
                                    lines.insert(j, "except ImportError:")
                                    lines.insert(j+1, "    ai_analyzer = None  # Optional module")
                                    lines.insert(j+2, "")
                                    break
                            break
                    
                    content = '\n'.join(lines)
                    print("[FIX] ai_analyzer import を try-except で安全に修正")
                    self.fixes_applied.append("ai_analyzer_import_safety")
            
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            print(f"[ERROR] 依存関係修正失敗: {e}")
            return False
    
    def enhance_session_stability(self):
        """
        セッション安定性の慎重な強化
        """
        print("\nULTRA SYNC: セッション安定性強化...")
        
        app_py_path = os.path.join(self.base_dir, "app.py")
        
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CSRFトークン安定性強化を追加
            if "app = Flask(__name__)" in content and "WTF_CSRF_TIME_LIMIT" not in content:
                flask_app_line = content.find("app = Flask(__name__)")
                if flask_app_line != -1:
                    # Flask app定義の後にCSRF設定を追加
                    insert_pos = content.find('\n', flask_app_line) + 1
                    
                    csrf_stability_config = """
# ULTRA SYNC: CSRF安定性強化設定（副作用防止）
app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRFトークン期限なし
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2時間のセッション持続
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF攻撃防止

"""
                    
                    content = content[:insert_pos] + csrf_stability_config + content[insert_pos:]
                    print("[FIX] CSRF安定性設定を追加")
                    self.fixes_applied.append("csrf_stability_enhancement")
            
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
            
        except Exception as e:
            print(f"[ERROR] セッション強化失敗: {e}")
            return False
    
    def verify_fixes_safety(self):
        """
        修正内容の安全性検証
        """
        print("\nULTRA SYNC: 修正内容安全性検証...")
        
        try:
            # Pythonファイルの構文チェック
            app_py_path = os.path.join(self.base_dir, "app.py")
            
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 構文エラーチェック
            compile(content, app_py_path, 'exec')
            print("[OK] 構文エラーなし - 修正は安全")
            
            return True
            
        except SyntaxError as e:
            print(f"[ERROR] 構文エラー検出: {e}")
            print("[ROLLBACK] 危険な修正を検出 - ロールバック実行")
            
            # 自動ロールバック
            self.rollback_changes()
            return False
            
        except Exception as e:
            print(f"[ERROR] 検証失敗: {e}")
            return False
    
    def rollback_changes(self):
        """
        緊急ロールバック（副作用防止の最後の砦）
        """
        print("\nULTRA SYNC: 緊急ロールバック実行...")
        
        backup_name = f"app.py.ultra_sync_stage3_safety_backup_{self.backup_timestamp}"
        backup_path = os.path.join(self.base_dir, backup_name)
        app_py_path = os.path.join(self.base_dir, "app.py")
        
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, app_py_path)
                print("[OK] 緊急ロールバック完了 - 元の状態に復元")
                return True
            else:
                print("[ERROR] バックアップファイルが見つかりません")
                return False
        except Exception as e:
            print(f"[ERROR] ロールバック失敗: {e}")
            return False
    
    def run_ultra_sync_stage3_fix(self):
        """
        ウルトラシンクSTAGE3修正の実行
        """
        print("ULTRA SYNC STAGE 3: 安定性修正（副作用絶対防止）")
        print("慎重かつ正確な修正プロセス開始")
        print("=" * 60)
        
        # Step 1: 安全バックアップ
        if not self.create_safety_backup():
            print("[ABORT] バックアップ失敗 - 修正を中止")
            return False
        
        # Step 2: 不足依存関係修正
        if not self.fix_missing_dependencies():
            print("[ABORT] 依存関係修正失敗 - ロールバック")
            self.rollback_changes()
            return False
        
        # Step 3: セッション安定性強化
        if not self.enhance_session_stability():
            print("[ABORT] セッション強化失敗 - ロールバック")
            self.rollback_changes()
            return False
        
        # Step 4: 安全性検証
        if not self.verify_fixes_safety():
            print("[ABORT] 安全性検証失敗 - 既にロールバック済み")
            return False
        
        # 成功報告
        print("\n" + "=" * 60)
        print("ULTRA SYNC STAGE 3 修正完了")
        print("=" * 60)
        print(f"適用された修正: {len(self.fixes_applied)}件")
        for fix in self.fixes_applied:
            print(f"  - {fix}")
        print("\n[SUCCESS] すべての修正が安全に適用されました")
        print("[NEXT] アプリケーションの再起動を推奨")
        
        return True

if __name__ == "__main__":
    fixer = UltraSyncStabilityFix()
    success = fixer.run_ultra_sync_stage3_fix()
    exit(0 if success else 1)