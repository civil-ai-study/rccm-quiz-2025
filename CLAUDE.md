# CLAUDE.md - RCCM Quiz Application Development Guide

## 🎯 **現在の状況: 完全動作中** (2025-09-23)

**本番環境**: https://rccm-quiz-2025.onrender.com ✅ **完全動作確認済み**
**開発環境**: localhost:5005 ✅ **即座に利用可能**
**状態**: 基本機能完璧・10問フロー完全動作・フィードバック画面正常

---

## 🏗️ **アプリケーション構成**

### **重要ファイル**
- `app.py` - メインアプリケーション（Flask-Session無効化済み）
- `config.py` - 13部門設定（LIGHTWEIGHT_DEPARTMENT_MAPPING）
- `requirements.txt` - 依存関係（Flask-Session無効化済み）
- `render.yaml` - Render.com デプロイ設定
- `wsgi.py` - 本番環境エントリーポイント
- `templates/exam_feedback.html` - フィードバック画面（統合完了）

### **データファイル（修正禁止）**
- `data/4-1.csv` - 基礎科目問題
- `data/4-2_2008.csv` ～ `data/4-2_2019.csv` - 専門科目問題（13部門）

---

## 🔧 **技術仕様（動作確認済み）**

### **セッション管理**
```python
# ✅ 現在の動作方式（Flask デフォルト cookie-based）
from flask import session
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')

# 🚨 絶対禁止: Flask-Session は完全に無効化済み
```

### **部門マッピング**
```python
# config.py - 13部門完全対応（修正禁止）
LIGHTWEIGHT_DEPARTMENT_MAPPING = {
    'basic': '基礎科目（共通）',
    'road': '道路',
    'river': '河川、砂防及び海岸・海洋',
    'urban': '都市計画及び地方計画',
    'garden': '造園',
    'env': '建設環境',
    'steel': '鋼構造及びコンクリート',
    'soil': '土質及び基礎',
    'construction': '施工計画、施工設備及び積算',
    'water': '上水道及び工業用水道',
    'forest': '森林土木',
    'agri': '農業土木',
    'tunnel': 'トンネル'
}
```

### **クイズフロー（完全動作中）**
```
問題表示 → 回答選択 → フィードバック画面 → 次の問題へ → ... → 結果画面
```

---

## 🚀 **開発・デプロイ手順**

### **ローカル開発開始**
```bash
cd rccm-quiz-app
python -m flask --app app run --host localhost --port 5005
# http://localhost:5005 でアクセス
```

### **本番デプロイ**
```bash
# 修正後のデプロイ手順
git add [修正ファイル]
git commit -m "修正内容"
git push origin main

# 3分待機後に動作確認
curl -I https://rccm-quiz-2025.onrender.com
```

### **動作確認テスト**
```bash
# 13部門テスト
python simple_test.py

# 10問フローテスト
python final_emergency_test.py
```

---

## ⚠️ **重要な注意事項**

### **絶対にやってはいけないこと**
1. **Flask-Session の再有効化** - Python 3.13で確実にエラー
2. **CSV ファイルの修正** - データ破損の原因
3. **LIGHTWEIGHT_DEPARTMENT_MAPPING の変更** - 部門混在エラー復活

### **Flask-Session 関連（触らない）**
```python
# 🚨 これらは絶対に復活させない
# from flask_session import Session
# Session(app)
# Flask-Session==任意のバージョン in requirements.txt
```

---

## 🆘 **問題発生時の復旧手順**

### **緊急復旧（現在の完璧な状態に戻す）**
```bash
cd rccm-quiz-app

# 1. 現在の動作コミットに戻す
git reset --hard 6fd1bc4

# 2. 強制プッシュで本番環境復旧
git push origin main --force

# 3. 動作確認
curl -I https://rccm-quiz-2025.onrender.com
```

### **状態確認コマンド**
```bash
# Flask-Session 無効化確認
grep -n "Flask-Session" requirements.txt  # コメントアウト状態確認
grep -n "from flask_session" app.py      # インポート無効化確認

# 部門マッピング確認
python -c "from config import LIGHTWEIGHT_DEPARTMENT_MAPPING; print(len(LIGHTWEIGHT_DEPARTMENT_MAPPING))"  # 13 が出力されること
```

---

## 🎯 **今後の開発指針**

### **安全な機能追加手順**
1. **localhost:5005 で完全テスト**
2. **既存機能への影響確認**
3. **デプロイ前の最終確認**
4. **本番環境での動作検証**

### **推奨する拡張開発**
- UI/UX 改善
- 新機能追加（既存機能は完璧動作中）
- パフォーマンス最適化
- セキュリティ強化

### **開発環境最適化**
- localhost:5005 を主要開発サーバーとして使用
- 他のポート（5000-5004, 5010）は実験用
- 本番環境は安定稼働中のため安心して開発可能

---

## 📊 **現在の動作状況**

| 機能 | 状況 | 確認方法 |
|------|------|----------|
| ホームページ | ✅ 動作 | https://rccm-quiz-2025.onrender.com |
| 13部門選択 | ✅ 動作 | 部門選択メニュー確認済み |
| 10問クイズフロー | ✅ 動作 | 河川砂防部門で実測済み |
| フィードバック画面 | ✅ 動作 | 回答後の画面表示確認済み |
| 結果画面 | ✅ 動作 | 10問完了後の表示確認済み |

---

## 🎉 **最終状態**

**RCCM Quiz Application**: ✅ **本番環境完全稼働中**

- **学習者**: 即座に学習開始可能
- **開発者**: 安全な機能拡張環境完備
- **保守性**: 完全な復旧手順文書化済み

**基本機能は完璧 - エンハンスメント作業に集中可能**

---

*このドキュメントは現在の完璧な動作状態（2025-09-23）を記録しています。*