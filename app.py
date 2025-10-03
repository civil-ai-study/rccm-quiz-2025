from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, make_response
from flask_wtf.csrf import CSRFProtect
# from flask_session import Session  # 🚨 DISABLED: Python 3.13互換性問題のため無効化
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from typing import Dict, List
import re
import html
from functools import wraps
import threading
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows環境では使用不可
import time
import uuid

# 🚨 PHASE 1: Session State Lock Mechanism for Race Condition Resolution
session_locks = {}
session_lock = threading.Lock()

# 新しいファイルからインポート
from config import Config, ExamConfig, SRSConfig, DataConfig, LIGHTWEIGHT_DEPARTMENT_MAPPING
# 🚨 ULTRA SYNC FIX: データ混合防止のため統一インポート
from utils import DataLoadError, DataValidationError, get_sample_data_improved, load_rccm_data_files
from math_notation_html_filter import create_math_notation_filter

# 🎯 REFACTORING PHASE 1: ヘルパー関数のインポート（リスクゼロ）
from helpers.decorators import (
    require_questions, require_api_key, handle_errors,
    track_performance, require_session_data, api_json_response
)
from helpers.department_helpers import (
    get_department_name, get_department_id, validate_department_id,
    get_all_departments, filter_questions_by_department, get_department_info
)
from helpers.error_handlers import (
    json_error, template_error, api_error,
    data_not_found_error, session_error, validation_error
)

# 🎯 REFACTORING PHASE 2: セッションサービスのインポート
from services.session_service import SessionService

# 🎯 REFACTORING PHASE 3: 問題サービスのインポート
from services.question_service import QuestionService

# 🎯 REFACTORING PHASE 4: SRSサービスのインポート
from services.srs_service import SRSService

# 🎯 REFACTORING PHASE 5: 統計サービスのインポート
from services.statistics_service import StatisticsService

# 🎯 REFACTORING PHASE 6-19: Blueprintのインポート
from blueprints.api_blueprint import api_bp
from blueprints.data_blueprint import data_bp
from blueprints.mobile_blueprint import mobile_bp
from blueprints.learning_blueprint import learning_bp
from blueprints.auth_blueprint import auth_bp
from blueprints.enterprise_blueprint import enterprise_bp
from blueprints.user_blueprint import user_bp
from blueprints.certification_blueprint import certification_bp
from blueprints.personalization_blueprint import personalization_bp
from blueprints.analytics_blueprint import analytics_bp

# ULTRA SYNC STAGE 6: Parameter Validation (PHASE 1 Task B2) - TEMPORARILY DISABLED
# from marshmallow import ValidationError
# from schemas.validation_schemas import validate_exam_parameters, validate_department_parameter

# 企業環境最適化: 遅延インポートで重複読み込み防止
gamification_manager = None
ai_analyzer = None
adaptive_engine = None  
exam_simulator = None
advanced_analytics = None
mobile_manager = None
learning_optimizer = None
admin_dashboard = None
social_learning_manager = None
api_manager = None  
advanced_personalization = None

# ログ設定
# 🚨 ULTRA SYNC FIX: パフォーマンス向上のためログレベル最適化
logging.basicConfig(
    level=logging.ERROR,  # INFO→ERROR変更でI/O削減
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rccm_app.log'),
        logging.StreamHandler()
    ]
)

# 🔥 CRITICAL: セッション競合状態解決のためのロック管理
session_locks = {}
lock_cleanup_lock = threading.Lock()
logger = logging.getLogger(__name__)

# Flask アプリケーション初期化
app = Flask(__name__)

# 設定適用（改善版）
app.config.from_object(Config)

# 🚨 DISABLED: Flask-Session無効化（Python 3.13互換性問題のため）
# Session(app)

# 🎯 ULTRA SIMPLE FIX: HTTP 413エラー解決 - MAX_CONTENT_LENGTH調整
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB (デフォルト16MB → 50MB)

# 🎯 MATHEMATICAL NOTATION HTML FILTER: 数学記法を正しいHTMLに変換
math_filter = create_math_notation_filter()

@app.template_filter('math')
def math_notation_filter(text):
    """数学記法をHTMLの<sup><sub>タグに変換するフィルター"""
    return math_filter(text)

# 🚫 REMOVED: Mathematical notation filter completely removed to prevent floating character issues
# Previously caused normal numbers to display as superscript characters

# 🔧 SECURITY: CSRF保護を有効化（10万人規模での必須セキュリティ）
csrf = CSRFProtect(app)

# セッション設定を明示的に追加
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# 🎯 PHASE 6-19 REFACTORING: Blueprint登録
app.register_blueprint(api_bp)
app.register_blueprint(data_bp)
app.register_blueprint(mobile_bp)
app.register_blueprint(learning_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(enterprise_bp)
app.register_blueprint(user_bp)
app.register_blueprint(certification_bp)
app.register_blueprint(personalization_bp)
app.register_blueprint(analytics_bp)

# 企業環境最適化: 遅延初期化で重複読み込み防止
data_manager = None
session_data_manager = None
enterprise_user_manager = None
enterprise_data_manager = None

# 問題データのキャッシュ
_questions_cache = None
_cache_timestamp = None

def get_rccm_questions_with_cache():
    """RCCMの問題データをキャッシュ付きで取得"""
    global _questions_cache, _cache_timestamp

    # キャッシュが有効かチェック（5分間）
    if (_questions_cache is not None and
        _cache_timestamp is not None and
        time.time() - _cache_timestamp < 300):
        return _questions_cache

    try:
        # データディレクトリから問題データを読み込み
        data_dir = DataConfig.BASE_DIR + "/data"
        questions = load_rccm_data_files(data_dir)

        # キャッシュを更新
        _questions_cache = questions
        _cache_timestamp = time.time()

        logger.info(f"問題データキャッシュ更新: {len(questions)}問")
        return questions

    except Exception as e:
        logger.error(f"問題データ読み込みエラー: {e}")
        # フォールバック用のサンプルデータ
        fallback_data = get_sample_data_improved()
        _questions_cache = fallback_data
        _cache_timestamp = time.time()
        return fallback_data

# 🔥 CRITICAL: セッション安全性確保のための排他制御関数
def get_session_lock(user_id):
    """ユーザー固有のセッションロックを取得"""
    global session_locks, lock_cleanup_lock
    
    with lock_cleanup_lock:
        if user_id not in session_locks:
            session_locks[user_id] = threading.RLock()
        return session_locks[user_id]

def cleanup_old_locks():
    """古いロックをクリーンアップ（メモリリーク防止）"""
    global session_locks, lock_cleanup_lock
    
    try:
        with lock_cleanup_lock:
            # 使用されていないロックを定期的にクリーンアップ
            # 本番環境では定期タスクで実行
            if len(session_locks) > 100:  # 100ユーザー以上でクリーンアップ
                # 実装を簡略化：全てクリア（実際の使用中ロックは再作成される）
                session_locks.clear()
                logger.info("セッションロックのクリーンアップを実行しました")
    except Exception as e:
        logger.error(f"ロッククリーンアップエラー: {e}")

def generate_unique_session_id():
    """一意なセッションIDを生成"""
    return f"{uuid.uuid4().hex[:8]}_{int(time.time())}"

def safe_session_operation(user_id, operation_func, *args, **kwargs):
    """セッション操作を安全に実行（排他制御付き）"""
    if not user_id:
        logger.error("user_idが提供されていません - セッション操作をスキップ")
        return None
    
    session_lock = get_session_lock(user_id)
    
    try:
        with session_lock:
            return operation_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"セッション操作エラー (user_id: {user_id}): {e}")
        return None

# 🎯 CLAUDE.md準拠: 10/20/30問題数システム実装
def get_question_count_from_request():
    """🚨 ULTRA SYNC FIX: 10問固定強制 - 可変問題数システム完全無効化"""
    # 問題数変動の根本原因：パラメーターでの動的変更防止
    return 10  # ユーザー要求による絶対固定値

def validate_question_count(count, available_questions_count):
    """問題数が利用可能な問題数に対して適切かチェック"""
    if count not in ExamConfig.SUPPORTED_QUESTION_COUNTS:
        return False

    config = ExamConfig.SESSION_TYPE_CONFIG.get(count, {})
    min_required = config.get('min_questions_required', count + 5)

    return available_questions_count >= min_required

def get_session_config_by_count(count):
    """問題数に基づいてセッション設定を取得"""
    return ExamConfig.SESSION_TYPE_CONFIG.get(count, {
        'name': f'{count}問セッション',
        'description': f'{count}問の学習セッション',
        'time_limit': None,
        'min_questions_required': count + 5
    })

# 強力なキャッシュ制御ヘッダーを設定（マルチユーザー・企業環境対応）
@app.after_request
def after_request(response):
    """
    全てのレスポンスにキャッシュ制御ヘッダーを追加
    企業環境での複数ユーザー利用に対応
    🔥 CRITICAL: ユーザー要求による超強力キャッシュクリア
    """
    # 🔥 ULTRA強力なキャッシュ制御でブラウザキャッシュを完全無効化
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'  # 過去の日付で強制期限切れ
    
    # 🔥 問題関連ページの追加キャッシュクリア（ユーザー要求による）
    if any(path in request.path for path in ['/exam', '/result', '/review', '/feedback']):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private, no-transform'
        response.headers['Last-Modified'] = 'Wed, 11 Jan 1984 05:00:00 GMT'  # 強制古い日付
        response.headers['ETag'] = '"0"'  # 無効なETAG
        response.headers['Vary'] = '*'    # 全リクエストで異なることを示す
    
    # セキュリティヘッダー追加
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # CORS対応（企業環境でのクロスオリジンアクセス）
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # サービスワーカー更新強制
    if '/sw.js' in request.path:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Service-Worker-Allowed'] = '/'
    
    return response

# セキュリティ機能
def sanitize_input(input_string):
    """入力値をサニタイズ（日本語対応）"""
    if not input_string:
        return ""
    # 文字列に変換
    sanitized = str(input_string)
    # 危険なHTMLタグのみ除去（日本語文字は保持）
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    # SQLインジェクション対策（クォートのみエスケープ）
    sanitized = sanitized.replace("'", "").replace('"', '')
    return sanitized.strip()

# =============================================================================
# 高度なSRS（間隔反復学習）システム - 忘却曲線ベース
# =============================================================================

def calculate_next_review_date(correct_count, wrong_count, last_interval=1):
    """
    忘却曲線に基づく次回復習日の計算

    🎯 PHASE 4 REFACTORING: SRSServiceへのラッパー関数
    後方互換性のため、既存の関数シグネチャを維持
    """
    return SRSService.calculate_next_review_date(correct_count, wrong_count, last_interval)

def update_advanced_srs_data(question_id, is_correct, session):
    """
    高度なSRSデータの更新

    🎯 PHASE 4 REFACTORING: SRSServiceへのラッパー関数
    後方互換性のため、既存の関数シグネチャを維持
    """
    return SRSService.update_srs_data(question_id, is_correct, session)

def get_due_review_questions(session, max_count=50):
    """
    復習が必要な問題を取得（優先度順）

    🎯 PHASE 4 REFACTORING: SRSServiceへのラッパー関数
    後方互換性のため、既存の関数シグネチャを維持
    """
    return SRSService.get_due_review_questions(session, max_count)

def get_adaptive_review_list(session):
    """
    アダプティブな復習リストを生成

    🎯 PHASE 4 REFACTORING: SRSServiceへのラッパー関数
    後方互換性のため、既存の関数シグネチャを維持
    """
    return SRSService.get_adaptive_review_list(session)

def cleanup_mastered_questions(session):
    """
    マスター済み問題の旧復習リストからの除去

    🎯 PHASE 4 REFACTORING: SRSServiceへのラッパー関数
    後方互換性のため、既存の関数シグネチャを維持
    """
    return SRSService.cleanup_mastered_questions(session)

# validate_exam_parameters function is imported from schemas.validation_schemas
# Removing duplicate local function to resolve signature mismatch

def rate_limit_check(max_requests=1000, window_minutes=60):
    """レート制限チェック"""
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # セッションからリクエスト履歴を取得
    request_history = session.get('request_history', [])
    
    # 古いリクエストを除去
    request_history = [req_time for req_time in request_history if datetime.fromisoformat(req_time) > window_start]
    
    # 現在のリクエストを追加
    request_history.append(now.isoformat())
    
    # セッションに保存
    session['request_history'] = request_history
    session.modified = True
    
    # レート制限チェック
    if len(request_history) > max_requests:
        return False
    
    return True

def validate_question_data_integrity(questions):
    """問題データの整合性チェックと自動修復"""
    valid_questions = []
    
    for i, question in enumerate(questions):
        try:
            # 必須フィールドのチェック
            if not question.get('id') or not question.get('question'):
                logger.warning(f"問題{i+1}: 必須フィールドが不足")
                continue
            
            # 選択肢の完整性チェック
            options = ['option_a', 'option_b', 'option_c', 'option_d']
            if not all(question.get(opt) for opt in options):
                logger.warning(f"問題{question.get('id')}: 選択肢が不完全")
                continue
            
            # 正解の妥当性チェック
            correct_answer = question.get('correct_answer', '').upper()
            if correct_answer not in ['A', 'B', 'C', 'D']:
                logger.warning(f"問題{question.get('id')}: 正解が無効 ({correct_answer})")
                continue
            
            # 部門・問題種別の整合性チェック
            question_type = question.get('question_type', '')
            if question_type not in ['basic', 'specialist']:
                # 年度があれば専門、なければ基礎と推定
                if question.get('year'):
                    question['question_type'] = 'specialist'
                else:
                    question['question_type'] = 'basic'
                logger.debug(f"問題{question.get('id')}: 問題種別を推定設定 ({question['question_type']})")
            
            valid_questions.append(question)
            
        except Exception as e:
            logger.error(f"問題{i+1}の検証エラー: {e}")
            continue
    
    removed_count = len(questions) - len(valid_questions)
    if removed_count > 0:
        logger.warning(f"データ整合性チェック: {removed_count}問を除外しました")
    
    return valid_questions

# 🚨 PHASE 1: Session State Management Functions (Critical Race Condition Fix)
def acquire_session_lock(session_id):
    """セッション状態の排他制御を取得"""
    global session_locks, session_lock
    
    with session_lock:
        if session_id not in session_locks:
            session_locks[session_id] = threading.Lock()
    
    # セッション固有のロックを取得
    return session_locks[session_id]

def get_current_session_state():
    """セッション状態の安全な読み取り（Single Source of Truth）"""
    session_id = session.get('session_id', str(uuid.uuid4()))
    
    with acquire_session_lock(session_id):
        return {
            'session_id': session_id,
            'exam_question_ids': session.get('exam_question_ids', []),
            'exam_current': session.get('exam_current', 0),
            'exam_category': session.get('exam_category', '全体'),
            'selected_question_type': session.get('selected_question_type', ''),
            'selected_department': session.get('selected_department', ''),
            'selected_year': session.get('selected_year', ''),
            'timestamp': time.time()
        }

def update_session_state(state_dict, force_modified=True):
    """セッション状態の安全な更新（Race Condition Prevention）"""
    session_id = session.get('session_id', str(uuid.uuid4()))
    
    with acquire_session_lock(session_id):
        # セッション状態を安全に更新
        for key, value in state_dict.items():
            if key != 'session_id':  # session_idは更新しない
                session[key] = value
        
        # セッションIDが設定されていない場合は設定
        if 'session_id' not in session:
            session['session_id'] = session_id
            
        if force_modified:
            session.modified = True
            
        # デバッグ用ログ（重要な変更のみ）
        if 'exam_question_ids' in state_dict:
            logger.info(f"🔒 Session State Updated: {len(state_dict['exam_question_ids'])} questions, current: {state_dict.get('exam_current', 'N/A')}")

def load_questions():
    """
    RCCM統合問題データの読み込み（4-1基礎・4-2専門対応）
    キャッシュ機能と詳細エラーハンドリング
    """
    global _questions_cache, _cache_timestamp
    
    current_time = datetime.now()
    
    # キャッシュが有効かチェック
    if (_questions_cache is not None and 
        _cache_timestamp is not None and 
        (current_time - _cache_timestamp).seconds < DataConfig.CACHE_TIMEOUT):
        logger.debug("キャッシュからデータを返却")
        return _questions_cache
    
    logger.info("RCCM統合問題データの読み込み開始")
    
    # 🎯 CLAUDE.md準拠: キャッシュ強制クリア（本番環境の古いキャッシュ対策）
    _questions_cache = None
    _cache_timestamp = None
    logger.info("[CACHE] CLAUDE.md compliant: Cache clearing initiated")
    
    # 🎯 ULTRA SYNC 根本解決: フォールバック処理完全無効化
    # 本番環境でload_rccm_data_filesのみ使用を強制
    data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
    logger.info(f"🎯 CLAUDE.md準拠: 正規データロード強制開始 - data_dir={data_dir}")
    
    # 🔥 EMERGENCY FIX: 直接CSVファイル読み込み（緊急修正）
    try:
        questions = load_rccm_data_files(data_dir)
        logger.info(f"🎯 CLAUDE.md準拠: load_rccm_data_files returned {len(questions) if questions else 0} questions")

        if not questions:
            logger.warning("🚨 統合関数が0件返却 - 直接読み込みに切り替え")
            # 緊急フォールバック: 4-1.csvを直接読み込み
            basic_file = os.path.join(data_dir, '4-1.csv')
            if os.path.exists(basic_file):
                from utils import load_questions_improved
                questions = load_questions_improved(basic_file)
                logger.info(f"🆘 緊急フォールバック成功: {len(questions)}問を4-1.csvから読み込み")
            else:
                logger.error(f"🚨 基礎ファイル不存在: {basic_file}")
                questions = []
    except Exception as e:
        logger.error(f"🚨 データ読み込みエラー: {e}")
        # 最後の手段: 直接4-1.csvを読み込み
        basic_file = os.path.join(data_dir, '4-1.csv')
        if os.path.exists(basic_file):
            from utils import load_questions_improved
            questions = load_questions_improved(basic_file)
            logger.info(f"🆘 最終フォールバック成功: {len(questions)}問")
        else:
            questions = []

    if not questions:
        logger.error(f"🚨 全ての読み込み方法が失敗")
        questions = []  # 空リストではなく例外を出さないよう修正
    
    # データ整合性チェック
    logger.info(f"🎯 CLAUDE.md準拠: データ整合性チェック開始")
    validated_questions = validate_question_data_integrity(questions)
    _questions_cache = validated_questions
    _cache_timestamp = current_time
    logger.info(f"✅ CLAUDE.md準拠: 正規RCCM統合データ読み込み完了: {len(validated_questions)}問 (ID体系=基礎1-202,専門1000+)")
    return validated_questions

def clear_questions_cache():
    """問題データキャッシュのクリア"""
    global _questions_cache, _cache_timestamp
    _questions_cache = None
    _cache_timestamp = None
    logger.info("問題データキャッシュをクリア")

# 🔥 CRITICAL: ウルトラシンク復習セッション管理システム（統合管理）
def validate_review_session_integrity(session_data):
    """復習セッションの整合性を検証し、必要に応じて修復する"""
    try:
        exam_question_ids = session_data.get('exam_question_ids', [])
        exam_current = session_data.get('exam_current', 0)
        selected_question_type = session_data.get('selected_question_type', '')
        
        # 復習セッションの基本チェック
        if selected_question_type != 'review':
            return False, "復習セッションではありません"
        
        if not exam_question_ids or not isinstance(exam_question_ids, list):
            return False, "復習問題リストが無効です"
        
        if exam_current < 0 or exam_current > len(exam_question_ids):
            return False, f"現在位置が範囲外です: {exam_current}/{len(exam_question_ids)}"
        
        # 問題IDの有効性チェック
        for qid in exam_question_ids:
            if not isinstance(qid, int) or qid <= 0:
                return False, f"無効な問題ID: {qid}"
        
        logger.debug(f"復習セッション整合性チェック成功: {len(exam_question_ids)}問, 位置{exam_current}")
        return True, "OK"
        
    except Exception as e:
        logger.error(f"復習セッション整合性チェックエラー: {e}")
        return False, str(e)

def create_robust_review_session(user_session, all_questions, review_type='mixed'):
    """堅牢な復習セッションを作成する（ウルトラシンク版）"""
    try:
        logger.info(f"堅牢復習セッション作成開始: タイプ={review_type}")
        
        # 復習対象問題を収集
        review_question_ids = set()
        
        # SRSデータから復習必要問題を取得
        srs_data = user_session.get('advanced_srs', {})
        due_questions = get_due_questions(user_session, all_questions)
        for due_item in due_questions:
            qid = due_item['question'].get('id')
            if qid:
                review_question_ids.add(int(qid))
        
        # ブックマークから復習問題を取得
        bookmarks = user_session.get('bookmarks', [])
        for bookmark_id in bookmarks:
            try:
                review_question_ids.add(int(bookmark_id))
            except (ValueError, TypeError):
                continue
        
        # 積極的な復習候補を追加（間違いの多い問題）
        history = user_session.get('history', [])
        wrong_questions = []
        for entry in history[-50:]:  # 直近50問をチェック
            if not entry.get('is_correct', True):  # 間違えた問題
                qid = entry.get('question_id')
                if qid:
                    wrong_questions.append(int(qid))
        
        # 間違いの多い問題を優先的に追加
        for qid in wrong_questions[-10:]:  # 最近10問の間違い
            review_question_ids.add(qid)
        
        # 有効な問題IDのみを保持
        valid_review_ids = []
        for qid in review_question_ids:
            # 問題データが存在するかチェック
            if any(int(q.get('id', 0)) == qid for q in all_questions):
                valid_review_ids.append(qid)
        
        # 最低限の復習問題数を保証
        if len(valid_review_ids) < 3:
            # ランダムに問題を追加
            random_questions = random.sample(all_questions, min(7, len(all_questions)))
            for q in random_questions:
                qid = int(q.get('id', 0))
                if qid not in valid_review_ids:
                    valid_review_ids.append(qid)
                if len(valid_review_ids) >= 10:  # 最大4-10問
                    break
        
        # 問題数を適切に調整
        if len(valid_review_ids) > 10:
            valid_review_ids = valid_review_ids[:10]  # 最大10問に制限
        
        valid_review_ids.sort()  # 一貫性のためにソート
        
        logger.info(f"堅牢復習セッション作成完了: {len(valid_review_ids)}問")
        logger.info(f"復習問題ID: {valid_review_ids[:5]}..." if len(valid_review_ids) > 5 else f"復習問題ID: {valid_review_ids}")
        
        return valid_review_ids
        
    except Exception as e:
        logger.error(f"堅牢復習セッション作成エラー: {e}")
        # フォールバック: シンプルな復習セッション
        fallback_questions = random.sample(all_questions, min(5, len(all_questions)))
        return [int(q.get('id', 0)) for q in fallback_questions]

def safe_update_review_session(session_data, question_ids, current_index=0):
    """復習セッションを安全に更新する"""
    try:
        # セッションクリア（復習関連のみ）
        review_keys_to_clear = [
            'exam_question_ids', 'exam_current', 'exam_category',
            'selected_question_type', 'selected_department', 'selected_year'
        ]
        
        for key in review_keys_to_clear:
            session_data.pop(key, None)
        
        # 新しい復習セッションデータを設定
        session_data.update({
            'exam_question_ids': question_ids,
            'exam_current': current_index,
            'exam_category': f'復習問題（統合{len(question_ids)}問）',
            'selected_question_type': 'review',
            'review_session_active': True,
            'review_session_created': datetime.now().isoformat(),
            'review_session_protected': True  # 保護フラグ
        })
        
        session_data.permanent = True
        session_data.modified = True
        
        logger.info(f"復習セッション安全更新完了: {len(question_ids)}問, 現在位置{current_index}")
        return True
        
    except Exception as e:
        logger.error(f"復習セッション安全更新エラー: {e}")
        return False

# Removed old update_srs_data function - replaced with update_advanced_srs_data

def get_due_questions(user_session, all_questions):
    """復習が必要な問題を取得"""
    if 'srs_data' not in user_session:
        return []
    
    srs_data = user_session['srs_data']
    today = datetime.now().date()
    due_questions = []
    
    for question_id, data in srs_data.items():
        try:
            next_review = datetime.fromisoformat(data['next_review']).date()
            if next_review <= today:
                question = next((q for q in all_questions if str(q.get('id', 0)) == question_id), None)
                if question:
                    due_questions.append({
                        'question': question,
                        'srs_data': data,
                        'days_overdue': (today - next_review).days
                    })
        except (ValueError, KeyError) as e:
            logger.warning(f"SRSデータ解析エラー (ID: {question_id}): {e}")
            continue
    
    due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
    return due_questions

def get_mixed_questions(user_session, all_questions, requested_category='全体', session_size=None, department='', question_type='', year=None):
    """新問題と復習問題をミックスした出題（RCCM部門対応版）"""
    # 🎯 CLAUDE.md準拠: 可変問題数システム (10/20/30問対応)
    if session_size is None:
        session_size = ExamConfig.QUESTIONS_PER_SESSION
    
    due_questions = get_due_questions(user_session, all_questions)
    
    # 設定から復習問題の比率を取得
    max_review_count = min(len(due_questions), 
                          int(session_size * SRSConfig.MAX_REVIEW_RATIO))
    selected_questions = []
    
    # 復習問題を追加（部門・問題種別・年度でもフィルタリング）
    for i, due_item in enumerate(due_questions):
        if i >= max_review_count:
            break
        
        question = due_item['question']
        # 部門・問題種別の条件チェック
        if department and question.get('department') != department:
            continue
        if question_type and question.get('question_type') != question_type:
            continue
        # 🚨 年度フィルタリング追加（ウルトラシンク修正）
        if year and str(question.get('year', '')) != str(year):
            continue
        
        selected_questions.append(question)
    
    # 残りを新問題で埋める（学習効率重視の選択）
    remaining_count = session_size - len(selected_questions)
    
    # 問題フィルタリング条件
    available_questions = all_questions
    
    # AI学習分析による弱点重視出題
    weak_categories = []
    if user_session.get('history'):
        try:
            from ai_analyzer import ai_analyzer
            weak_analysis = ai_analyzer.analyze_weak_areas(user_session, department)
            weak_categories = weak_analysis.get('weak_categories', [])
        except Exception as e:
            logger.error(f"quiz関数でエラー: {e}")
            weak_categories = []
    
    # 問題種別でフィルタリング（最優先・厳格）
    if question_type:
        # 基礎科目の場合
        if question_type == 'basic':
            available_questions = [q for q in available_questions 
                                 if q.get('question_type') == 'basic' 
                                 and q.get('year') is None]  # 基礎科目は年度なし
            logger.info(f"基礎科目フィルタ適用: 結果 {len(available_questions)}問")
        
        # 専門科目の場合
        elif question_type == 'specialist':
            available_questions = [q for q in available_questions 
                                 if q.get('question_type') == 'specialist' 
                                 and q.get('year') is not None]  # 専門科目は年度必須
            logger.info(f"専門科目フィルタ適用: 結果 {len(available_questions)}問")
        
        # その他の場合
        else:
            available_questions = [q for q in available_questions if q.get('question_type') == question_type]
            logger.info(f"問題種別フィルタ適用: {question_type}, 結果: {len(available_questions)}問")
        
        # 専門科目で部門指定がある場合のみ部門フィルタ適用
        if question_type == 'specialist' and department:
            # 🎯 CLAUDE.md準拠: 英語ID完全禁止 - 日本語直接マッチングのみ
            
            # 🚨 CLAUDE.md準拠: 英語ID系統完全禁止
            # LIGHTWEIGHT_DEPARTMENT_MAPPINGを使用して日本語カテゴリに変換
            target_categories = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
            logger.info(f"✅ 日本語直接マッチング: {department} → {target_categories}")
            
            logger.info(f"🔍 フィルタリング前の問題数={len(available_questions)}, 専門科目問題数={len([q for q in available_questions if q.get('question_type') == 'specialist'])}")
            
            # 日本語カテゴリでマッチング（category フィールドを使用）
            # 選択部門名（日本語）とCSVのcategory（日本語）の直接一致のみ
            dept_match_questions = [q for q in available_questions 
                                  if q.get('category') == target_categories]
            if dept_match_questions:
                available_questions = dept_match_questions
                logger.info(f"専門科目部門マッチング成功: {len(available_questions)}問")
            else:
                logger.warning(f"専門科目部門マッチング失敗: {target_categories} に該当する問題が見つかりません")
    
    # 部門でフィルタリング（基礎科目の場合はスキップ、専門科目で既に適用済みの場合もスキップ）
    elif department and question_type != 'basic' and question_type != 'specialist':
        available_questions = [q for q in available_questions if q.get('department') == department]
        logger.info(f"部門フィルタ適用: {department}, 結果: {len(available_questions)}問")
    
    # カテゴリでフィルタリング（文字化け考慮）
    if requested_category != '全体':
        pre_category_count = len(available_questions)
        # 正確な文字列マッチング
        available_questions = [q for q in available_questions if q.get('category') == requested_category]
        
        # 文字化けしている場合のフォールバック（部分マッチ）
        if len(available_questions) == 0 and requested_category:
            # 文字化けを考慮した部分マッチ
            logger.warning(f"正確なカテゴリマッチ失敗: {requested_category}, 部分マッチを試行")
            for q in [q for q in all_questions if q.get('question_type') == question_type]:
                category = q.get('category', '')
                # 道路、トンネル等の主要カテゴリのマッチング
                if ('道路' in category and ('道' in requested_category or 'road' in requested_category.lower())) or \
                   ('トンネル' in category and ('トンネル' in requested_category or 'tunnel' in requested_category.lower())) or \
                   ('河川' in category and ('河川' in requested_category or 'civil' in requested_category.lower())) or \
                   ('土質' in category and ('土質' in requested_category or 'soil' in requested_category.lower())):
                    if q not in available_questions:
                        available_questions.append(q)
        
        logger.info(f"カテゴリフィルタ適用: {requested_category}, {pre_category_count} → {len(available_questions)}問")
    
    # 年度でフィルタリング（専門科目のみ対象）
    if year:
        pre_year_count = len(available_questions)
        available_questions = [q for q in available_questions 
                              if str(q.get('year', '')) == str(year) 
                              and q.get('question_type') == 'specialist']
        logger.info(f"年度フィルタ適用: {year}年度, {pre_year_count} → {len(available_questions)}問")
    
    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]
    
    random.shuffle(new_questions)
    selected_questions.extend(new_questions[:remaining_count])
    
    random.shuffle(selected_questions)
    
    filter_info = []
    if department:
        filter_info.append(f"部門:{LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)}")
    if question_type:
        filter_info.append(f"種別:{question_type}")
    if requested_category != '全体':
        filter_info.append(f"カテゴリ:{requested_category}")
    if year:
        filter_info.append(f"年度:{year}")
    
    logger.info(f"問題選択完了: 復習{len([q for q in selected_questions if any(due['question'] == q for due in due_questions)])}問, "
                f"新規{len(selected_questions) - len([q for q in selected_questions if any(due['question'] == q for due in due_questions)])}問, "
                f"フィルタ:[{', '.join(filter_info) if filter_info else '全体'}]")
    
    return selected_questions

@app.before_request
def before_request():
    """リクエスト前の処理（企業環境最適化版）"""
    # ULTRA SYNC DEBUG: before_request確認
    if request.endpoint == 'question_types' or '/departments/' in request.path and '/types' in request.path:
        logger.info(f"🔍 ULTRA SYNC DEBUG: before_request for question_types, path: {request.path}, endpoint: {request.endpoint}")
    
    session.permanent = True
    
    # セッションIDの取得（簡素化）
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    
    # データロード済みフラグの確認（競合回避）
    if 'data_loaded' not in session:
        # 🚨 PHASE 1: セッション初期化をthread-safeに変更
        initial_state = {
            'data_loaded': True,
            'exam_question_ids': [],
            'exam_current': 0,
            'history': [],
            'bookmarks': [],
            'srs_data': {}
        }
        update_session_state(initial_state)
        
        # 企業環境用データロードは必要時のみ実行
        fast_mode = os.environ.get('RCCM_FAST_MODE', 'true').lower() == 'true'
        if not fast_mode:
            # 従来のデータロード（後方互換性）
            try:
                user_name = session.get('user_name')
                session_data_manager.load_session_data(session, session['session_id'], user_name)
            except Exception as e:
                logger.warning(f"セッションデータロード失敗（続行可能）: {e}")

@app.after_request
def after_request_data_save(response):
    """リクエスト後の処理（企業環境最適化版）"""
    # 高速化モードでは自動保存を軽量化
    fast_mode = os.environ.get('RCCM_FAST_MODE', 'true').lower() == 'true'
    
    if not fast_mode:
        # 従来のデータ保存（後方互換性）
        session_id = session.get('session_id')
        if session_id and session.get('history'):
            try:
                user_name = session.get('user_name')
                session_data_manager.auto_save_trigger(session, session_id, user_name)
            except Exception as e:
                logger.warning(f"セッション自動保存失敗（続行可能）: {e}")
    
    # セッション修正フラグを明示的に設定
    if hasattr(session, 'modified'):
        session.modified = True
    
    return response

@app.route('/')
def index():
    """ホーム画面（ユーザー識別対応）"""
    try:
        # 🎯 PHASE 2 REFACTORING: SessionServiceを使用
        SessionService.clear_exam_session()
        SessionService.initialize_user_session()
        
        user_name = session.get('user_name')
        if user_name:
            logger.info(f"ホームページアクセス - ユーザー: {user_name}")
        else:
            logger.info("ホームページアクセス - 未認証ユーザー")
        
        session.modified = True
        return render_template('index.html')
        
    except Exception as e:
        logger.error(f"ホームページエラー: {e}")
        return render_template('error.html', error_message=str(e)), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """設定画面"""
    try:
        available_options = [5, 10, 15, 20, 25, 30]
        current_setting = session.get('questions_per_session', 10)

        if request.method == 'POST':
            questions_per_session = int(request.form.get('questions_per_session', 10))
            if questions_per_session in available_options:
                session['questions_per_session'] = questions_per_session
                flash(f'問題数を{questions_per_session}問に設定しました', 'success')
            else:
                flash('無効な問題数です', 'error')
            return redirect(url_for('settings'))

        return render_template('settings.html',
                             available_options=available_options,
                             current_setting=current_setting)
    except Exception as e:
        logger.error(f"設定画面エラー: {e}")
        return render_template('error.html', error_message=str(e)), 500

@app.route('/set_user', methods=['POST', 'GET'])
def set_user():
    """ユーザー名を設定（企業環境での個別識別）"""
    try:
        # POST/GET両方に対応（テスト用）
        if request.method == 'POST':
            user_name = request.form.get('user_name', '').strip()
        else:
            user_name = request.args.get('user', '').strip()
        
        if not user_name:
            return redirect(url_for('index'))
        
        # 入力値のサニタイズ
        user_name = sanitize_input(user_name)
        
        # ユーザー名の長さ制限
        if len(user_name) > 20:
            user_name = user_name[:20]
        
        # 🎯 PHASE 2 REFACTORING: SessionServiceを使用
        unique_session_id = generate_unique_session_id()
        base_user_id = f"user_{hash(user_name) % 100000:05d}"

        SessionService.set_user(user_name, base_user_id, unique_session_id)

        logger.info(f"🔒 セッション安全性確保: {user_name} (セッションID: {unique_session_id})")
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"ユーザー設定エラー: {e}")
        return redirect(url_for('index'))

@app.route('/change_user')
def change_user():
    """ユーザー変更（ログアウト）"""
    try:
        old_user = session.get('user_name', '不明')
        
        # ユーザー情報のみクリア（学習データは保持）
        session.pop('user_name', None)
        session.pop('user_id', None)
        session.pop('login_time', None)
        
        logger.info(f"ユーザー変更: {old_user} がログアウト")
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"ユーザー変更エラー: {e}")
        return redirect(url_for('index'))

@app.route('/force_refresh')
def force_refresh():
    """強制的にキャッシュをクリアして最新版を表示"""
    response = make_response(redirect('/'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/submit_answer', methods=['POST'])
# @csrf.exempt  # CSRF無効化に伴い一時コメントアウト
def submit_answer():
    """回答提出エンドポイント - Ultra Sync セッション継続保証"""
    # 🚨 ULTRA SYNC FIX: POST処理後の自動GET要求をセッション継続として認識させる
    session['_post_answer_processed'] = True
    session.modified = True
    return exam()

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    """シンプル統合版exam関数 - 問題文と選択肢の一致を保証"""
    try:
        # データ読み込み
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        all_questions = load_rccm_data_files(data_dir)
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")

        # POST処理（回答送信）
        if request.method == 'POST':
            answer = sanitize_input(request.form.get('answer'))
            # qidとquestion_idの両方に対応（下位互換性確保）
            qid = sanitize_input(request.form.get('qid')) or sanitize_input(request.form.get('question_id'))

            if answer not in ['A', 'B', 'C', 'D']:
                return render_template('error.html', error="無効な回答が選択されました。")

            if not qid:
                return render_template('error.html', error="問題IDが指定されていません。")

            try:
                qid = int(qid)
            except (ValueError, TypeError):
                return render_template('error.html', error="問題IDが無効です。")

            # 問題を直接IDで検索
            current_question = None
            for q in all_questions:
                if q.get('id') == qid:
                    current_question = q
                    break

            if not current_question:
                return render_template('error.html', error="指定された問題が見つかりません。")

            # 正答チェック
            is_correct = (answer == current_question.get('correct_answer'))

            # 履歴追加
            if 'history' not in session:
                session['history'] = []

            session['history'].append({
                'id': qid,
                'category': current_question.get('category', '不明'),
                'question_type': current_question.get('question_type', 'basic'),
                'is_correct': is_correct,
                'user_answer': answer,
                'correct_answer': current_question.get('correct_answer', ''),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            # 🚀 新機能: 間違った問題を自動的に復習リストに登録
            if not is_correct:
                # SRSシステムで管理
                if 'advanced_srs' not in session:
                    session['advanced_srs'] = {}

                srs_data = session['advanced_srs']
                qid_str = str(qid)

                # 新規登録または既存データ更新
                if qid_str not in srs_data:
                    srs_data[qid_str] = {
                        'level': 1,
                        'next_review': datetime.now().isoformat(),
                        'incorrect_count': 1,
                        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'question_type': current_question.get('question_type', 'basic'),
                        'category': current_question.get('category', '不明')
                    }
                else:
                    # 既存の問題の場合、間違い回数を増加
                    srs_data[qid_str]['incorrect_count'] = srs_data[qid_str].get('incorrect_count', 0) + 1
                    srs_data[qid_str]['level'] = max(1, srs_data[qid_str].get('level', 1) - 1)
                    srs_data[qid_str]['next_review'] = datetime.now().isoformat()

                session['advanced_srs'] = srs_data

            session.modified = True

            # 次の問題のID取得（現在のセッションから）
            exam_question_ids = session.get('exam_question_ids', [])
            current_index = session.get('exam_current', 0)
            next_index = current_index + 1

            # フィードバック画面に必要な情報を準備
            selected_options = {
                'A': current_question.get('option_a', ''),
                'B': current_question.get('option_b', ''),
                'C': current_question.get('option_c', ''),
                'D': current_question.get('option_d', '')
            }

            # フィードバック画面を表示（全必要変数を追加）
            # 部門名を取得
            department = session.get('selected_department', '')
            department_name = "未選択"
            if department:
                department_name = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)

            return render_template('exam_feedback.html',
                question=current_question,
                user_answer=answer,
                user_answer_text=selected_options.get(answer, ''),
                correct_answer_text=selected_options.get(current_question.get('correct_answer', ''), ''),
                is_correct=is_correct,
                current_question_number=current_index + 1,
                total_questions=len(exam_question_ids),
                is_last_question=(next_index >= len(exam_question_ids)),
                next_question_number=current_index + 2 if next_index < len(exam_question_ids) else None,
                current_streak=0,  # 修正: current_streak変数を追加
                performance_comparison=None,  # 修正: performance_comparison変数を追加
                new_badges=None,  # 修正: new_badges変数を追加
                badge_info=None,   # 修正: badge_info変数を追加
                department_name=department_name
            )

        # GET処理（問題表示）
        # フィードバック画面からの「次の問題へ」ボタン処理
        if request.args.get('next') == '1':
            current_index = session.get('exam_current', 0)
            session['exam_current'] = current_index + 1
            session.modified = True

        # セッション状態確認
        exam_question_ids = session.get('exam_question_ids', [])
        current_index = session.get('exam_current', 0)

        # セッションが空の場合、新しいセッションを作成
        if not exam_question_ids:
            # URL パラメータから設定を取得
            question_type = request.args.get('question_type', session.get('selected_question_type', 'basic'))
            department = request.args.get('department', session.get('selected_department', ''))
            count = request.args.get('count', '10')

            # カウントを整数に変換（デフォルト10、最大30）
            try:
                count = int(count)
                count = max(1, min(30, count))  # 1-30の範囲に制限
            except (ValueError, TypeError):
                count = 10

            # セッションに保存
            session['selected_question_type'] = question_type
            if department:
                session['selected_department'] = department

            if question_type == 'basic':
                questions = [q for q in all_questions if q.get('question_type') == 'basic']
            elif question_type == 'specialist':
                questions = [q for q in all_questions if q.get('question_type') == 'specialist']
                if department:
                    # LIGHTWEIGHT_DEPARTMENT_MAPPINGを使用
                    target_category = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
                    questions = [q for q in questions if q.get('category') == target_category]
            else:
                questions = all_questions

            if not questions:
                return render_template('error.html', error="指定された条件の問題が見つかりません。")

            # 指定された問数をランダム選択
            import random
            selected_questions = random.sample(questions, min(count, len(questions)))
            exam_question_ids = [q.get('id') for q in selected_questions]

            session['exam_question_ids'] = exam_question_ids
            session['exam_current'] = 0
            session.modified = True
            current_index = 0

        # 現在の問題取得
        if current_index >= len(exam_question_ids):
            return redirect(url_for('result'))

        current_qid = exam_question_ids[current_index]
        current_question = None
        for q in all_questions:
            if q.get('id') == current_qid:
                current_question = q
                break

        if not current_question:
            return render_template('error.html', error="問題データが見つかりません。")

        # 部門名を取得
        department = session.get('selected_department', '')
        department_name = "未選択"
        if department:
            department_name = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)

        # 問題表示用データ準備
        context = {
            'question': current_question,
            'current_no': current_index + 1,
            'total_questions': len(exam_question_ids),
            'exam_question_ids': exam_question_ids,
            'is_exam_mode': True,
            'department_name': department_name
        }

        return render_template('exam.html', **context)

    except Exception as e:
        logger.error(f"exam関数でエラー: {e}")
        return render_template('error.html', error="問題表示中にエラーが発生しました。")

@app.route('/exam/next')
def exam_next():
    """次の問題に進む"""
    # 🚨 PHASE 1: セッション状態をthread-safe読み取り
    session_state = get_current_session_state()
    current_no = session_state['exam_current']
    exam_question_ids = session_state['exam_question_ids']
    
    if current_no >= len(exam_question_ids):
        return redirect(url_for('result'))
    
    category = session_state['exam_category']
    return redirect(url_for('exam', category=category))

@app.route('/result')
def result():
    """結果画面"""
    try:
        history = session.get('history', [])
        
        # デバッグ用：セッション内容を詳細出力
        logger.info(f"結果画面: 履歴件数={len(history)}")
        logger.info(f"セッションキー={list(session.keys())}")
        logger.info(f"セッション内容(最初の5件): {dict(list(session.items())[:5])}")
        
        
        exam_question_ids = session.get('exam_question_ids', [])
        session_size = len(exam_question_ids) if exam_question_ids else ExamConfig.QUESTIONS_PER_SESSION
        
        # 履歴が空の場合は適切にハンドリング（ダミーデータは削除）
        if not history:
            logger.info("履歴なしのため/examにリダイレクト")
            return redirect(url_for('exam'))
            
        recent_history = history[-session_size:] if len(history) >= session_size else history
        
        # 基本統計
        correct_count = sum(1 for h in recent_history if h.get('is_correct', False))
        total_questions = len(recent_history) if recent_history else 1
        elapsed_time = sum(h.get('elapsed', 0) for h in recent_history)
        
        # 共通・専門別成績
        basic_specialty_scores = {
            'basic': {'correct': 0, 'total': 0},
            'specialty': {'correct': 0, 'total': 0}
        }
        
        for h in recent_history:
            # 問題種別から4-1（基礎）か4-2（専門）かを判定
            question_type = h.get('question_type', '')
            question_id = h.get('id', '')
            file_source = h.get('file_source', '')
            
            # 優先度: question_type > ID判定 > ファイル名判定
            if question_type == 'basic' or '4-1' in str(question_id) or '4-1' in file_source:
                score_type = 'basic'
            elif question_type == 'specialist' or '4-2' in str(question_id) or '4-2' in file_source:
                score_type = 'specialty'
            else:
                # デフォルトは基礎科目とする
                score_type = 'basic'
                logger.debug(f"問題種別不明 - 基礎科目として扱う: {h}")
            
            basic_specialty_scores[score_type]['total'] += 1
            if h.get('is_correct'):
                basic_specialty_scores[score_type]['correct'] += 1
        
        # セッションから部門情報を取得
        selected_department = session.get('selected_department')
        selected_question_type = session.get('selected_question_type')

        # 部門名を取得
        department_name = "未選択"
        if selected_department:
            if selected_department in LIGHTWEIGHT_DEPARTMENT_MAPPING:
                department_name = LIGHTWEIGHT_DEPARTMENT_MAPPING[selected_department]
            elif selected_department in LIGHTWEIGHT_DEPARTMENT_MAPPING:
                department_name = LIGHTWEIGHT_DEPARTMENT_MAPPING[selected_department]

        return render_template(
            'result.html',
            correct_count=correct_count,
            total_questions=total_questions,
            selected_department=selected_department,
            department_name=department_name,
            selected_question_type=selected_question_type,
            debug_session_id=session.get('session_id', 'MISSING'),
            elapsed_time=elapsed_time,
            basic_specialty_scores=basic_specialty_scores
        )
        
    except Exception as e:
        logger.error(f"result関数でエラー: {e}")
        return render_template('error.html', error="結果表示中にエラーが発生しました。")

@app.route('/statistics')
def statistics():
    """
    統計画面

    🎯 PHASE 5 REFACTORING: StatisticsServiceを使用
    """
    try:
        history = session.get('history', [])

        # 全体統計（StatisticsServiceを使用）
        overall_stats = StatisticsService.get_overall_statistics(history)

        # 基礎・専門別統計（StatisticsServiceを使用）
        basic_specialty_details = StatisticsService.get_basic_specialty_statistics(history)

        # 最近の履歴（StatisticsServiceを使用）
        exam_history = StatisticsService.get_recent_history(history, limit=30)

        # 日付別統計（StatisticsServiceを使用）
        daily_accuracy_list = StatisticsService.get_daily_statistics(history)

        return render_template(
            'statistics.html',
            overall_stats=overall_stats,
            basic_specialty_details=basic_specialty_details,
            exam_history=exam_history,
            daily_accuracy_list=daily_accuracy_list
        )

    except Exception as e:
        logger.error(f"statistics関数でエラー: {e}")
        return render_template('error.html', error="統計表示中にエラーが発生しました。")

@app.route('/department_statistics')
def department_statistics():
    """部門別詳細統計画面"""
    try:
        from department_statistics import department_statistics as dept_stats_analyzer
        
        # 現在のユーザーセッション
        user_session = session
        
        # 包括的な部門別統計レポートを生成
        report = dept_stats_analyzer.generate_comprehensive_department_report(user_session)
        
        # 部門情報を追加
        departments = LIGHTWEIGHT_DEPARTMENT_MAPPING
        
        logger.info(f"部門別統計レポート生成: {report.get('total_questions_analyzed', 0)}問分析")
        
        return render_template(
            'department_statistics.html',
            report=report,
            departments=departments,
            title='部門別詳細統計'
        )
        
    except Exception as e:
        logger.error(f"department_statistics関数でエラー: {e}")
        return render_template('error.html', error="部門別統計表示中にエラーが発生しました。")

@app.route('/departments')
def departments():
    """RCCM部門選択画面"""
    try:
        # 現在選択されている部門を取得
        current_department = session.get('selected_department', 'basic')
        
        # 各部門の学習進捗を計算
        department_progress = {}
        history = session.get('history', [])
        
        for dept_id, dept_info in LIGHTWEIGHT_DEPARTMENT_MAPPING.items():
            # この部門での問題数と正答数を集計
            dept_history = [h for h in history if h.get('department') == dept_id]
            total_answered = len(dept_history)
            correct_count = sum(1 for h in dept_history if h.get('is_correct', False))
            
            department_progress[dept_id] = {
                'total_answered': total_answered,
                'correct_count': correct_count,
                'accuracy': (correct_count / total_answered * 100) if total_answered > 0 else 0.0
            }
        
        return render_template(
            'departments.html',
            departments=LIGHTWEIGHT_DEPARTMENT_MAPPING,
            current_department=current_department,
            department_progress=department_progress
        )
        
    except Exception as e:
        logger.error(f"departments関数でエラー: {e}")
        return render_template('error.html', error="部門選択画面の表示中にエラーが発生しました。")

@app.route('/departments/<department_id>', methods=['GET', 'POST'])
def select_department(department_id):
    """部門選択処理"""
    try:
        if department_id not in LIGHTWEIGHT_DEPARTMENT_MAPPING:
            logger.error(f"無効な部門ID: {department_id}")
            return render_template('error.html', error="指定された部門が見つかりません。")

        # POST処理（部門選択確定）
        if request.method == 'POST':
            # セッションに部門を保存
            session['selected_department'] = department_id
            session.modified = True
            logger.info(f"部門選択確定: {department_id}")
            return redirect(url_for('question_types', department_id=department_id))

        # GET処理（部門情報表示）
        # セッションに部門を保存
        session['selected_department'] = department_id
        session.modified = True

        logger.info(f"部門選択: {department_id} ({LIGHTWEIGHT_DEPARTMENT_MAPPING[department_id]})")

        # 問題種別選択画面にリダイレクト
        return redirect(url_for('question_types', department_id=department_id))
        
    except Exception as e:
        logger.error(f"部門選択エラー: {e}")
        return render_template('error.html', error="部門選択中にエラーが発生しました。")

@app.route('/ultra_sync_test')
def ultra_sync_test():
    """ULTRA SYNC Flask動作確認テスト"""
    return "✅ ULTRA SYNC SUCCESS: Flask application is working correctly!"

@app.route('/ultra_sync_road_debug')
def ultra_sync_road_debug():
    """🚨 ULTRA SYNC 道路部門デバッグ専用ルート - 副作用なし"""
    from datetime import datetime
    
    debug_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ULTRA SYNC Road Debug Route</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #fff3cd; }
        .debug { color: #856404; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>🚨 ULTRA SYNC Road Debug Route Active</h1>
    <div class="debug">✅ This route is definitely executing</div>
    <div class="debug">✅ Flask routing system is functional</div>
    <div class="debug">⚠️ URL: /ultra_sync_road_debug</div>
    <div class="debug">🔍 Timestamp: {timestamp}</div>
    <hr>
    <p><strong>DEBUG PURPOSE:</strong> Verify Flask routing system works</p>
    <p><strong>NEXT STEP:</strong> If this works, investigate /departments/road/types routing conflict</p>
    <p><a href="/departments/road/types">Test Problem Route</a></p>
</body>
</html>""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return debug_html

@app.route('/departments/<department_id>/types', methods=['GET', 'POST'])
def question_types(department_id):
    """問題種別選択画面（4-1基礎 / 4-2専門）- ULTRA SYNC強制表示版"""
    try:
        # 🚨 ULTRA SYNC CRITICAL: 強制実行確認
        logger.info(f"🔥 ULTRA SYNC FORCE: question_types route EXECUTED for department_id='{department_id}'")

        # EMERGENCY FIX: POST処理追加（専門分野選択処理）
        if request.method == 'POST':
            question_type = request.form.get('question_type')
            logger.info(f"🔥 EMERGENCY POST: question_type='{question_type}' selected for department='{department_id}'")

            # セッションに選択内容を保存
            session['selected_department'] = department_id
            session['selected_question_type'] = question_type

            # 試験開始ページにリダイレクト
            return redirect(url_for('exam'))

        # CRITICAL FIX: 緊急テストコードを削除 - 正常な道路部門アクセスを復旧
        # 道路部門も他の部門と同じ正常な処理フローで動作させる
        
        if department_id not in LIGHTWEIGHT_DEPARTMENT_MAPPING:
            logger.error(f"🚨 ULTRA SYNC DEBUG: department_id '{department_id}' not found in LIGHTWEIGHT_DEPARTMENT_MAPPING")
            logger.info(f"🔍 ULTRA SYNC DEBUG: Available departments: {list(LIGHTWEIGHT_DEPARTMENT_MAPPING.keys())}")
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        # 🎯 REFACTORING FIX: helper関数を使用
        from helpers.department_helpers import get_department_info
        department_info = get_department_info(department_id)

        # 各問題種別の学習進捗を計算
        type_progress = {}
        history = session.get('history', [])

        for type_id in ['basic', 'specialist']:
            # この部門・種別での問題数と正答数を集計
            type_history = [h for h in history
                          if h.get('department') == department_id and h.get('question_type') == type_id]
            total_answered = len(type_history)
            correct_count = sum(1 for h in type_history if h.get('is_correct', False))

            type_progress[type_id] = {
                'total_answered': total_answered,
                'correct_count': correct_count,
                'accuracy': (correct_count / total_answered * 100) if total_answered > 0 else 0.0
            }

        # ULTRA SYNC DEBUG: テンプレート描画前確認
        logger.info(f"✅ ULTRA SYNC DEBUG: Rendering question_types.html for department '{department_id}' ({department_info['name']})")
        logger.info(f"🔍 ULTRA SYNC DEBUG: Available question types: ['basic', 'specialist']")
        logger.info(f"🔍 ULTRA SYNC DEBUG: department_info content: {department_info}")
        logger.info(f"🔍 ULTRA SYNC DEBUG: About to call render_template - this should return HTML page, not redirect")
        
        # ULTRA SYNC STAGE 8: 正式にテンプレート描画を復旧
        logger.info(f"✅ ULTRA SYNC STAGE 8: Attempting template rendering with question_types.html")
        
        return render_template('question_types.html',
            department=department_info,
            question_types={'basic': {'name': '基礎科目'}, 'specialist': {'name': '専門科目'}},
            type_progress=type_progress
        )
        
    except Exception as e:
        logger.error(f"問題種別選択エラー: {e}")
        return render_template('error.html', error="問題種別選択画面の表示中にエラーが発生しました。")

@app.route('/departments/<department_id>/types/<question_type>/categories')
def department_categories(department_id, question_type):
    """部門・問題種別別のカテゴリ画面"""
    try:
        if department_id not in LIGHTWEIGHT_DEPARTMENT_MAPPING:
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        if question_type not in ['basic', 'specialist']:
            return render_template('error.html', error="指定された問題種別が見つかりません。")
        
        # セッションに選択情報を保存
        session['selected_department'] = department_id
        session['selected_question_type'] = question_type
        session.modified = True
        
        department_info = LIGHTWEIGHT_DEPARTMENT_MAPPING[department_id]
        type_info = {'basic': {'name': '基礎科目'}, 'specialist': {'name': '専門科目'}}[question_type]
        
        questions = load_questions()
        
        # 指定された部門・問題種別の問題のみをフィルタリング
        filtered_questions = [q for q in questions 
                             if q.get('department') == department_id and q.get('question_type') == question_type]
        
        # カテゴリ情報を集計
        category_details = {}
        for q in filtered_questions:
            cat = q.get('category')
            if cat:
                if cat not in category_details:
                    category_details[cat] = {
                        'total_questions': 0,
                        'total_answered': 0,
                        'correct_count': 0,
                        'accuracy': 0.0
                    }
                category_details[cat]['total_questions'] += 1
        
        # 統計情報を追加（部門・種別を考慮）
        cat_stats = session.get('category_stats', {})
        for cat, stat in cat_stats.items():
            if cat in category_details:
                # 部門・種別別の統計が必要な場合は履歴から計算
                history = session.get('history', [])
                dept_type_history = [h for h in history 
                                   if h.get('department') == department_id 
                                   and h.get('question_type') == question_type 
                                   and h.get('category') == cat]
                
                total = len(dept_type_history)
                correct = sum(1 for h in dept_type_history if h.get('is_correct', False))
                
                category_details[cat]['total_answered'] = total
                category_details[cat]['correct_count'] = correct
                category_details[cat]['accuracy'] = (correct / total * 100) if total > 0 else 0.0
        
        # 進捗率計算
        progresses = {}
        for cat, detail in category_details.items():
            total_q = detail.get('total_questions', 0)
            answered = detail.get('total_answered', 0)
            progresses[cat] = round((answered / total_q) * 100, 1) if total_q > 0 else 0.0
        
        return render_template(
            'department_categories.html',
            department=department_info,
            question_type=type_info,
            category_details=category_details,
            progresses=progresses,
            total_questions=len(filtered_questions)
        )
        
    except Exception as e:
        logger.error(f"部門別カテゴリ表示エラー: {e}")
        return render_template('error.html', error="カテゴリ表示中にエラーが発生しました。")

@app.route('/department_study/<department>')
def department_study(department):
    """部門特化学習画面 - ユーザーフレンドリーな部門学習インターフェース"""
    try:
        # 部門名を英語キーに変換
        department_key = None
        for key, info in LIGHTWEIGHT_DEPARTMENT_MAPPING.items():
            if info['name'] == department or key == department:
                department_key = key
                break
        
        if not department_key:
            logger.error(f"無効な部門名: {department}")
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        department_info = LIGHTWEIGHT_DEPARTMENT_MAPPING[department_key]
        
        # セッションに部門を保存
        session['selected_department'] = department_key
        session.modified = True
        
        # 問題データを読み込み
        questions = load_questions()
        
        # 4-1基礎問題（全部門共通）の統計
        basic_questions = [q for q in questions if q.get('question_type') == 'basic']
        basic_history = [h for h in session.get('history', []) if h.get('question_type') == 'basic']
        basic_stats = {
            'total_questions': len(basic_questions),
            'answered': len(basic_history),
            'correct': sum(1 for h in basic_history if h.get('is_correct', False)),
            'accuracy': (sum(1 for h in basic_history if h.get('is_correct', False)) / len(basic_history) * 100) if basic_history else 0.0
        }
        
        # 4-2専門問題（選択部門のみ）の統計
        specialist_questions = [q for q in questions 
                              if q.get('question_type') == 'specialist' and q.get('department') == department_key]
        specialist_history = [h for h in session.get('history', []) 
                             if h.get('question_type') == 'specialist' and h.get('department') == department_key]
        specialist_stats = {
            'total_questions': len(specialist_questions),
            'answered': len(specialist_history),
            'correct': sum(1 for h in specialist_history if h.get('is_correct', False)),
            'accuracy': (sum(1 for h in specialist_history if h.get('is_correct', False)) / len(specialist_history) * 100) if specialist_history else 0.0
        }
        
        # 復習対象問題数
        review_questions = [h for h in session.get('history', []) 
                           if not h.get('is_correct', False) and h.get('department') == department_key]
        
        logger.info(f"部門特化学習画面表示: {department} ({department_info['name']})")
        logger.info(f"4-1基礎: {basic_stats['total_questions']}問, 4-2専門: {specialist_stats['total_questions']}問")
        
        return render_template(
            'department_study.html',
            department=department_info,
            department_key=department_key,
            basic_stats=basic_stats,
            specialist_stats=specialist_stats,
            review_count=len(review_questions),
            question_types={'basic': {'name': '基礎科目'}, 'specialist': {'name': '専門科目'}}
        )
        
    except Exception as e:
        logger.error(f"部門特化学習画面エラー: {e}")
        return render_template('error.html', error="部門学習画面の表示中にエラーが発生しました。")

@app.route('/categories')
def categories():
    """部門別問題選択画面（選択部門+共通のみ表示）"""
    try:
        questions = load_questions()
        cat_stats = session.get('category_stats', {})
        
        # 現在選択されている部門を取得
        selected_department = session.get('selected_department', request.args.get('department'))
        
        # カテゴリ情報を集計（選択部門+共通のみ）
        category_details = {}
        for q in questions:
            cat = q.get('category')
            q_dept = q.get('department', '')
            q_type = q.get('question_type', '')
            
            # フィルタリング: 共通問題 OR 選択部門の専門問題のみ
            include_question = False
            if q_type == 'basic' or cat == '共通':  # 基礎科目（共通）は常に表示
                include_question = True
            elif selected_department and q_dept == selected_department and q_type == 'specialist':  # 選択部門の専門問題のみ
                include_question = True
            elif not selected_department:  # 部門未選択の場合は全表示
                include_question = True
            
            if include_question and cat:
                if cat not in category_details:
                    category_details[cat] = {
                        'total_questions': 0,
                        'total_answered': 0,
                        'correct_count': 0,
                        'accuracy': 0.0
                    }
                category_details[cat]['total_questions'] += 1
        
        # 統計情報を追加
        for cat, stat in cat_stats.items():
            if cat in category_details:
                total = stat.get('total', 0)
                correct = stat.get('correct', 0)
                category_details[cat]['total_answered'] = total
                category_details[cat]['correct_count'] = correct
                category_details[cat]['accuracy'] = (correct / total * 100) if total > 0 else 0.0
        
        # 進捗率計算
        progresses = {}
        for cat, detail in category_details.items():
            total_q = detail.get('total_questions', 0)
            answered = detail.get('total_answered', 0)
            progresses[cat] = round((answered / total_q) * 100, 1) if total_q > 0 else 0.0
        
        return render_template(
            'categories.html',
            category_details=category_details,
            progresses=progresses
        )
        
    except Exception as e:
        logger.error(f"categories関数でエラー: {e}")
        return render_template('error.html', error="カテゴリ表示中にエラーが発生しました。")

@app.route('/review')
def review_list():
    """復習リスト表示（高度なSRSシステム対応版）"""
    try:
        # 新しいSRSシステムからデータを取得
        srs_data = session.get('advanced_srs', {})
        bookmarks = session.get('bookmarks', [])  # 互換性維持
        
        # すべての復習対象問題を統合
        all_review_ids = set()
        all_review_ids.update(srs_data.keys())
        all_review_ids.update(bookmarks)
        
        if not all_review_ids:
            return render_template('review_enhanced.html', 
                                 message="まだ復習問題が登録されていません。問題を解いて間違えることで、科学的な復習システムが自動的に最適な学習計画を作成します。",
                                 departments=LIGHTWEIGHT_DEPARTMENT_MAPPING,
                                 srs_stats={
                                     'total_questions': 0,
                                     'due_now': 0,
                                     'mastered': 0,
                                     'in_progress': 0
                                 })
        
        # 問題データを読み込み（防御的プログラミング強化）
        try:
            all_questions = load_questions()
            if not all_questions:
                logger.warning("load_questions()が空のリストを返しました")
                return render_template('review_enhanced.html',
                                     message="問題データの読み込みに問題があります。管理者に連絡してください。",
                                     departments=LIGHTWEIGHT_DEPARTMENT_MAPPING,
                                     srs_stats={'total_questions': 0, 'due_now': 0, 'mastered': 0, 'in_progress': 0})

            questions_dict = {str(q.get('id')): q for q in all_questions if q.get('id')}
            logger.info(f"問題データロード成功: {len(all_questions)}問, 辞書変換: {len(questions_dict)}問")

        except Exception as data_error:
            logger.error(f"問題データ読み込みエラー: {data_error}")
            return render_template('review_enhanced.html',
                                 message=f"問題データの読み込みでエラーが発生しました: {str(data_error)}",
                                 departments=LIGHTWEIGHT_DEPARTMENT_MAPPING,
                                 srs_stats={'total_questions': 0, 'due_now': 0, 'mastered': 0, 'in_progress': 0})
        
        # 復習問題の詳細情報を作成（SRSデータ統合）
        review_questions = []
        departments = set()
        
        # SRS統計計算
        srs_stats = {
            'total_questions': len(all_review_ids),
            'due_now': 0,
            'mastered': 0,
            'in_progress': 0,
            'high_priority': 0
        }
        
        from datetime import datetime
        now = datetime.now()
        
        for qid in all_review_ids:
            if qid in questions_dict:
                question = questions_dict[qid]
                
                # SRSデータを取得
                srs_info = srs_data.get(qid, {})
                
                # 基本情報
                question_data = {
                    'id': qid,
                    'question': question.get('question', ''),
                    'department': question.get('department', ''),
                    'question_type': question.get('question_type', ''),
                    'year': question.get('year', ''),
                    'category': question.get('category', ''),
                    # SRS情報
                    'correct_count': srs_info.get('correct_count', 0),
                    'wrong_count': srs_info.get('wrong_count', 0),
                    'total_attempts': srs_info.get('total_attempts', 0),
                    'difficulty_level': srs_info.get('difficulty_level', 5),
                    'mastered': srs_info.get('mastered', False),
                    'first_attempt': srs_info.get('first_attempt', ''),
                    'last_attempt': srs_info.get('last_attempt', ''),
                    'next_review': srs_info.get('next_review', ''),
                    'interval_days': srs_info.get('interval_days', 1)
                }
                
                # 統計更新
                if question_data['mastered']:
                    srs_stats['mastered'] += 1
                else:
                    srs_stats['in_progress'] += 1
                    
                    # 復習期限チェック
                    try:
                        if question_data['next_review']:
                            next_review = datetime.fromisoformat(question_data['next_review'])
                            if next_review <= now:
                                srs_stats['due_now'] += 1
                        else:
                            srs_stats['due_now'] += 1  # 未設定は即座に復習対象
                    except ValueError:
                        srs_stats['due_now'] += 1
                    
                    # 高優先度（間違いが多い）問題
                    if question_data['wrong_count'] >= 2:
                        srs_stats['high_priority'] += 1
                
                # 部門情報
                if question_data['department']:
                    departments.add(question_data['department'])
                
                # 優先度計算（表示順序用）
                if question_data['mastered']:
                    priority = -1000  # マスター済みは最後
                else:
                    wrong_ratio = question_data['wrong_count'] / max(1, question_data['total_attempts'])
                    overdue_bonus = 0
                    try:
                        if question_data['next_review']:
                            next_review = datetime.fromisoformat(question_data['next_review'])
                            days_overdue = max(0, (now - next_review).days)
                            overdue_bonus = days_overdue * 10
                    except ValueError:
                        overdue_bonus = 100  # 日時エラーは高優先度
                    
                    priority = (wrong_ratio * 100) + overdue_bonus + question_data['difficulty_level']
                
                question_data['priority'] = priority
                review_questions.append(question_data)
        
        # 優先度順でソート（マスター済み問題は最後）
        review_questions.sort(key=lambda x: x['priority'], reverse=True)
        
        # マスター済み問題とアクティブ問題を分離
        active_questions = [q for q in review_questions if not q['mastered']]
        mastered_questions = [q for q in review_questions if q['mastered']]
        
        logger.info(f"復習リスト表示: 総計{len(review_questions)}問, "
                   f"アクティブ{len(active_questions)}問, マスター済み{len(mastered_questions)}問")
        
        return render_template('review_enhanced.html',
                             questions=active_questions,
                             mastered_questions=mastered_questions,
                             total_count=len(active_questions),
                             mastered_count=len(mastered_questions),
                             departments=LIGHTWEIGHT_DEPARTMENT_MAPPING,
                             srs_stats=srs_stats,
                             show_srs_details=True)
    
    except Exception as e:
        logger.error(f"復習リスト表示エラー: {e}")
        import traceback
        logger.error(f"詳細エラー情報: {traceback.format_exc()}")

        # 🚨 ULTRATHIN区段階: より詳細なエラー情報をユーザーに提供
        error_details = f"復習リスト表示中にエラーが発生しました。詳細: {str(e)}"

        # データロード問題の場合の特別処理
        if "load_questions" in str(e).lower() or "data" in str(e).lower():
            error_details = "問題データの読み込みでエラーが発生しました。データファイルを確認してください。"
        elif "template" in str(e).lower():
            error_details = "テンプレートエラーが発生しました。"
        elif "session" in str(e).lower():
            error_details = "セッションエラーが発生しました。ページを再読み込みしてください。"

        return render_template('error.html', error=error_details)

# 🎯 PHASE 7 REFACTORING: 以下の3ルートをapi_blueprintに移動
# @app.route('/api/review/questions', methods=['POST'])
# @app.route('/api/review/remove', methods=['POST'])
# @app.route('/api/review/bulk_remove', methods=['POST'])
# → blueprints/api_blueprint.py に統合済み

@app.route('/srs')
def srs_list():
    """SRS復習リスト（/reviewへのリダイレクト）"""
    return redirect(url_for('review_list'))

@app.route('/srs_stats')
def srs_statistics():
    """SRS学習統計の表示（エラー処理強化版）"""
    try:
        # セッションデータの安全な取得
        srs_data = session.get('srs_data', {})
        
        # 基本統計の初期化
        stats = {
            'total_learned': 0,
            'mastered': 0,
            'review_needed': 0,
            'learning': 0,
            'error_data': 0
        }
        
        today = datetime.now().date()
        processed_data = {}
        
        # SRSデータの安全な処理
        for question_id, data in srs_data.items():
            try:
                # データが辞書形式かチェック
                if not isinstance(data, dict):
                    logger.warning(f"SRS統計: 無効なデータ形式 ID={question_id}, type={type(data)}")
                    stats['error_data'] += 1
                    continue
                
                # レベルと日時の安全な取得
                level = int(data.get('level', 0))
                next_review_str = data.get('next_review')
                
                if not next_review_str:
                    # 復習日が設定されていない場合
                    stats['learning'] += 1
                    processed_data[question_id] = {
                        'level': level,
                        'status': '学習中',
                        'next_review': '未設定'
                    }
                    continue
                
                # 日時の解析
                try:
                    next_review = datetime.fromisoformat(next_review_str).date()
                except (ValueError, TypeError):
                    # 日時解析失敗時のフォールバック
                    stats['learning'] += 1
                    processed_data[question_id] = {
                        'level': level,
                        'status': '学習中',
                        'next_review': '日時エラー'
                    }
                    continue
                
                # レベルと復習日に基づく分類
                if level >= 5:
                    stats['mastered'] += 1
                    status = 'マスター'
                elif next_review <= today:
                    stats['review_needed'] += 1
                    status = '復習必要'
                else:
                    stats['learning'] += 1
                    status = '学習中'
                
                processed_data[question_id] = {
                    'level': level,
                    'status': status,
                    'next_review': next_review.isoformat()
                }
                
            except Exception as item_error:
                logger.warning(f"SRS統計処理エラー ID={question_id}: {item_error}")
                stats['error_data'] += 1
        
        # 合計学習数の更新
        stats['total_learned'] = stats['mastered'] + stats['review_needed'] + stats['learning']
        
        # 学習進捗計算
        progress_percentage = 0
        if stats['total_learned'] > 0:
            progress_percentage = round((stats['mastered'] / stats['total_learned']) * 100, 1)
        
        stats['progress_percentage'] = progress_percentage
        
        logger.info(f"SRS統計生成完了: 総計={stats['total_learned']}, マスター={stats['mastered']}, 復習必要={stats['review_needed']}")
        
        return render_template('srs_stats.html', 
                             stats=stats, 
                             srs_data=processed_data,
                             last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'))
        
    except Exception as e:
        logger.error(f"SRS統計表示エラー: {e}")
        # エラー時のフォールバック表示
        fallback_stats = {
            'total_learned': 0,
            'mastered': 0,
            'review_needed': 0,
            'learning': 0,
            'progress_percentage': 0,
            'error_data': 0
        }
        return render_template('srs_stats.html', 
                             stats=fallback_stats, 
                             srs_data={},
                             error_message="学習統計の読み込み中にエラーが発生しました。問題を続けることで統計が蓄積されます。")

# 🎯 PHASE 8 REFACTORING: 以下の2ルートをdata_blueprintに移動
# @app.route('/api/data/export')
# @app.route('/api/cache/clear', methods=['POST'])
# → blueprints/data_blueprint.py に統合済み

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """リセット画面"""
    if request.method == 'POST':
        session.clear()
        # 強制的なキャッシュクリア
        clear_questions_cache()
        logger.info("セッションとキャッシュを完全リセット")
        return redirect(url_for('index'))
    
    # 現在のデータ分析
    history = session.get('history', [])
    analytics = {
        'total_questions': len(history),
        'accuracy': 0
    }
    
    if history:
        correct = sum(1 for h in history if h.get('is_correct'))
        analytics['accuracy'] = round((correct / len(history)) * 100, 1)
    
    return render_template('reset_confirm.html', analytics=analytics)

@app.route('/force_reset')
def force_reset():
    """強制リセット（トラブルシューティング用）"""
    try:
        # セッション完全削除
        session.clear()
        # キャッシュクリア
        clear_questions_cache()
        # セッションIDも新規生成
        session['session_id'] = os.urandom(16).hex()
        session.permanent = True
        logger.info("強制リセット実行完了")
        return jsonify({
            'success': True, 
            'message': '完全リセットが完了しました。ページを再読み込みしてください。',
            'new_session_id': session['session_id']
        })
    except Exception as e:
        logger.error(f"強制リセットエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/help')
def help_page():
    """包括的なヘルプページ"""

    # 統計データを取得
    history = session.get('history', [])
    srs_data = session.get('advanced_srs', {})
    bookmarks = session.get('bookmarks', [])

    help_data = {
        'total_questions': ExamConfig.QUESTIONS_PER_SESSION,
        'departments': LIGHTWEIGHT_DEPARTMENT_MAPPING,
        'total_solved': len(history),
        'review_count': len(srs_data),
        'bookmark_count': len(bookmarks),
        'features': {
            'basic_exam': '基礎科目10問題での学習',
            'specialist_exam': '13専門部門から選択して10問題での学習',
            'auto_review': '間違った問題の自動復習リスト登録',
            'srs_system': '科学的反復学習システム',
            'bookmarks': '重要問題のブックマーク機能',
            'statistics': '詳細学習統計・分析',
            'mobile_support': 'モバイル対応・オフライン学習',
            'ai_analysis': 'AI学習分析・推奨機能'
        }
    }

    return render_template('help.html', **help_data)

@app.route('/debug')
def debug_page():
    """デバッグページ"""
    import json
    session_data = dict(session)
    session_data_json = json.dumps(session_data, indent=2, default=str)
    return render_template('debug.html', session_data=session_data_json)

# 🎯 PHASE 6 REFACTORING: 以下の3ルートをapi_blueprintに移動
# @app.route('/api/bookmark', methods=['POST'])
# @app.route('/api/bookmarks', methods=['GET'])
# @app.route('/api/bookmark', methods=['DELETE'])
# → blueprints/api_blueprint.py に統合済み

@app.route('/bookmark', methods=['POST'])
def add_bookmark():
    """フォーム形式でのブックマーク追加"""
    try:
        qid = request.form.get('qid')
        
        if not qid:
            logger.warning("ブックマーク追加: 問題IDが指定されていません")
            return redirect(request.referrer or '/exam')
        
        # セッションにブックマークリストがなければ作成
        if 'bookmarks' not in session:
            session['bookmarks'] = []
        
        # 問題IDがリストになければ追加
        if qid not in session['bookmarks']:
            session['bookmarks'].append(qid)
            session.modified = True
            logger.info(f"問題ID {qid} を復習リストに追加しました")
        
        return redirect(request.referrer or '/exam')
        
    except Exception as e:
        logger.error(f"ブックマーク追加エラー: {e}")
        return redirect(request.referrer or '/exam')

@app.route('/bookmarks')
def bookmarks_page():
    """復習リストページ（HTMLページ）"""
    try:
        # 復習リストから問題IDを取得
        bookmarks = session.get('bookmarks', [])
        
        if not bookmarks:
            return render_template('bookmarks.html', 
                                 questions=[],
                                 total_count=0,
                                 message="まだ復習問題が登録されていません。")
        
        # 問題データを読み込み
        all_questions = load_questions()
        questions = []
        
        # ブックマークされた問題の詳細情報を取得
        for qid in bookmarks:
            question = next((q for q in all_questions if str(q.get('id', '')) == str(qid)), None)
            if question:
                # 部門名を取得
                dept_key = question.get('department', '')
                dept_name = ''
                if dept_key:
                    dept_name = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(dept_key, dept_key)
                
                questions.append({
                    'id': question.get('id'),
                    'question': question.get('question', '')[:100] + '...' if len(question.get('question', '')) > 100 else question.get('question', ''),
                    'category': question.get('category', ''),
                    'department_name': dept_name,
                    'year': question.get('year'),
                    'question_type': question.get('question_type', '')
                })
        
        return render_template('bookmarks.html',
                             questions=questions,
                             total_count=len(questions))
        
    except Exception as e:
        logger.error(f"復習リストページエラー: {e}")
        return render_template('error.html', error="復習リストの表示中にエラーが発生しました。")

# 🎯 PHASE 6 REFACTORING: DELETE /api/bookmark → blueprints/api_blueprint.py に移動済み


@app.route('/exam/review')
def review_quiz():
    """🔥 ULTRA堅牢な高度SRSシステム復習問題練習（ウルトラシンク対応）"""
    try:
        # 🔥 CRITICAL: 包括的エラーハンドリング
        logger.info("=== 復習開始処理開始 ===")
        
        # 問題データロード（エラーハンドリング強化）
        try:
            # データディレクトリの設定
            data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
            all_questions = load_rccm_data_files(data_dir)
            if not all_questions:
                logger.error("問題データが空です")
                return render_template('error.html', 
                                     error="問題データが読み込めませんでした。システム管理者に連絡してください。",
                                     error_type="data_load_error")
        except Exception as load_error:
            logger.error(f"問題データロードエラー: {load_error}")
            return render_template('error.html', 
                                 error="問題データの読み込み中にエラーが発生しました。",
                                 error_type="data_load_exception")
        
        # 🔥 ULTRA堅牢: 復習対象問題を統合取得（安全性強化・ウルトラシンク対応）
        try:
            srs_data = session.get('advanced_srs', {})
            bookmarks = session.get('bookmarks', [])
            
            # データ型チェック（ウルトラシンク対応）
            if not isinstance(srs_data, dict):
                logger.warning(f"SRSデータが辞書型ではありません: {type(srs_data)} - 初期化")
                srs_data = {}
            if not isinstance(bookmarks, list):
                logger.warning(f"ブックマークがリスト型ではありません: {type(bookmarks)} - 初期化")
                bookmarks = []
            
            # 🔥 ULTRA堅牢: SRSデータの詳細検証と修復
            valid_srs_data = {}
            for qid, srs_info in srs_data.items():
                try:
                    # SRS情報の型チェック
                    if not isinstance(srs_info, dict):
                        logger.warning(f"SRS情報が無効な型: 問題ID {qid}, 型: {type(srs_info)}")
                        continue
                    
                    # 🔥 FIXED: SRSデータフィールド名を実際のデータ構造に合わせて修正
                    # 実際のSRSデータは: incorrect_count, level, category, next_review, question_type
                    # より柔軟な検証にして、最低限の情報があれば受け入れる
                    if 'incorrect_count' in srs_info:
                        # 間違い回数があれば復習対象として扱う
                        incorrect_count = int(srs_info.get('incorrect_count', 0))
                        if incorrect_count >= 0:  # 0以上であれば有効
                            valid_srs_data[qid] = srs_info
                    else:
                        logger.warning(f"SRS情報に必要フィールド(incorrect_count)が不足: 問題ID {qid}, フィールド: {srs_info.keys()}")
                except (ValueError, TypeError) as field_error:
                    logger.warning(f"SRS情報の数値変換エラー: 問題ID {qid}, エラー: {field_error}")
                    continue
            
            logger.info(f"SRSデータ検証: 元データ{len(srs_data)}問 → 有効データ{len(valid_srs_data)}問")
            srs_data = valid_srs_data
            
            # 🔥 ULTRA堅牢: ブックマークデータの詳細検証と修復
            valid_bookmarks = []
            for bookmark in bookmarks:
                try:
                    # ブックマークの型チェック（文字列または数値）
                    if isinstance(bookmark, (str, int)):
                        bookmark_str = str(bookmark).strip()
                        if bookmark_str and bookmark_str.isdigit():
                            valid_bookmarks.append(bookmark_str)
                    else:
                        logger.warning(f"ブックマークが無効な型: {bookmark}, 型: {type(bookmark)}")
                except Exception as bookmark_error:
                    logger.warning(f"ブックマーク処理エラー: {bookmark}, エラー: {bookmark_error}")
                    continue
            
            logger.info(f"ブックマーク検証: 元データ{len(bookmarks)}問 → 有効データ{len(valid_bookmarks)}問")
            bookmarks = valid_bookmarks
                
            # すべての復習対象問題IDを統合（重複除去）
            all_review_ids = set()
            
            # SRSデータから取得（文字列に変換してから統合）
            for qid in srs_data.keys():
                if qid and str(qid).strip():  # 空文字や None をスキップ
                    all_review_ids.add(str(qid))
            
            # ブックマークから取得（文字列に変換してから統合）
            for qid in bookmarks:
                if qid and str(qid).strip():  # 空文字や None をスキップ
                    all_review_ids.add(str(qid))
            
            # リストに変換
            review_question_ids = list(all_review_ids)
            
            logger.info(f"復習対象問題統合: SRS={len(srs_data)}問, ブックマーク={len(bookmarks)}問, 統合後={len(review_question_ids)}問")
            
        except Exception as integration_error:
            logger.error(f"復習データ統合エラー: {integration_error}")
            return render_template('error.html', 
                                 error="復習データの処理中にエラーが発生しました。",
                                 error_type="data_integration_error")
        
        if not review_question_ids:
            # SRSデータがない場合の案内メッセージ
            srs_data = session.get('advanced_srs', {})
            if not srs_data:
                return render_template('error.html', 
                                     error="復習リストが空です。まず問題を解いて間違えることで、科学的な復習システムが学習を開始します。",
                                     error_type="no_srs_data")
            else:
                return render_template('error.html', 
                                     error="現在復習が必要な問題がありません。素晴らしい！新しい問題に挑戦するか、時間が経ってから復習してください。",
                                     error_type="all_mastered")
        
        # 🔥 CRITICAL: 問題データマッチングと弱点スコア計算（ウルトラシンク対応）
        try:
            # 問題IDから実際の問題データを取得（安全性強化）
            questions_dict = {}
            for q in all_questions:
                try:
                    q_id = str(q.get('id', ''))
                    if q_id and q_id.strip():  # 空文字チェック
                        questions_dict[q_id] = q
                except Exception as q_parse_error:
                    logger.warning(f"問題ID変換エラー: {q_parse_error}, question={q}")
                    continue
            
            logger.info(f"問題辞書作成完了: {len(questions_dict)}問")
            
            review_questions_with_score = []
            successful_matches = 0
            failed_matches = 0
            
            for qid in review_question_ids:
                try:
                    if qid in questions_dict:
                        question = questions_dict[qid]
                        
                        # 弱点スコア計算（安全性強化）
                        try:
                            srs_info = srs_data.get(qid, {})
                            
                            # 🔥 FIXED: 実際のSRSデータ構造に合わせてフィールド名を修正
                            wrong_count = max(0, int(srs_info.get('incorrect_count', 0)))
                            total_attempts = max(1, wrong_count + 1)  # 間違い回数+1で概算
                            difficulty_level = max(0, float(srs_info.get('level', 1) * 2))  # レベルから難易度を概算
                            
                            # 復習期限チェック（エラーハンドリング強化）
                            overdue_bonus = 0
                            next_review = srs_info.get('next_review', '')
                            if next_review:
                                try:
                                    from datetime import datetime
                                    next_review_date = datetime.fromisoformat(next_review)
                                    days_overdue = max(0, (datetime.now() - next_review_date).days)
                                    overdue_bonus = min(50, days_overdue * 2)  # 最大50に制限
                                except Exception as date_error:
                                    logger.debug(f"日付解析エラー（問題ID: {qid}）: {date_error}")
                                    overdue_bonus = 5  # デフォルト値
                            
                            # 弱点スコア計算（オーバーフロー防止）
                            error_rate = min(1.0, wrong_count / total_attempts)
                            weakness_score = min(1000, (error_rate * 100) + difficulty_level + overdue_bonus)
                            
                            review_questions_with_score.append({
                                'question': question,
                                'weakness_score': weakness_score,
                                'wrong_count': wrong_count,
                                'total_attempts': total_attempts,
                                'overdue_bonus': overdue_bonus
                            })
                            
                            successful_matches += 1
                            
                        except Exception as score_error:
                            logger.warning(f"弱点スコア計算エラー（問題ID: {qid}）: {score_error}")
                            # エラーが発生した問題もデフォルトスコアで追加
                            review_questions_with_score.append({
                                'question': question,
                                'weakness_score': 50,  # デフォルトスコア
                                'wrong_count': 1,
                                'total_attempts': 1,
                                'overdue_bonus': 0
                            })
                            successful_matches += 1
                    else:
                        failed_matches += 1
                        logger.debug(f"問題IDが見つかりません: {qid}")
                        
                except Exception as match_error:
                    logger.warning(f"問題マッチングエラー（ID: {qid}）: {match_error}")
                    failed_matches += 1
                    continue
            
            logger.info(f"問題マッチング結果: 成功={successful_matches}問, 失敗={failed_matches}問")
            
        except Exception as processing_error:
            logger.error(f"弱点スコア処理の重大エラー: {processing_error}")
            return render_template('error.html', 
                                 error="復習問題の評価中にエラーが発生しました。",
                                 error_type="score_processing_error")
        
        if not review_questions_with_score:
            return render_template('error.html', 
                                 error="復習対象の問題が見つかりません。新しい問題を解いて間違えることで復習リストが作成されます。",
                                 error_type="no_filtered_questions")
        
        # 🔥 ULTRA CRITICAL: 最終問題選択とセッション設定（ウルトラシンク対応）
        try:
            # 🔥 ULTRA堅牢: 弱点スコア順でソート（安全なソート・完全エラーハンドリング）
            try:
                # 各問題の弱点スコアが数値であることを確認
                for item in review_questions_with_score:
                    if not isinstance(item.get('weakness_score'), (int, float)):
                        item['weakness_score'] = 50.0  # デフォルトスコア
                
                review_questions_with_score.sort(key=lambda x: float(x.get('weakness_score', 0)), reverse=True)
                logger.info(f"弱点スコア順ソート完了: {len(review_questions_with_score)}問")
            except Exception as sort_error:
                logger.warning(f"ソートエラー（デフォルト順序を使用）: {sort_error}")
                # ソートに失敗してもそのまま続行
            
            # 🔥 ULTRA CRITICAL: セッション問題数の動的決定（最低保証とユーザー要求バランス）
            available_questions = len(review_questions_with_score)
            min_session_size = min(3, available_questions)  # 最低3問、または利用可能問題数
            target_session_size = 10  # 理想は10問
            session_size = min(target_session_size, available_questions)  # 利用可能問題数に制限
            
            if session_size < min_session_size:
                logger.error(f"復習問題が不足: 利用可能{available_questions}問, 最低必要{min_session_size}問")
                return render_template('error.html', 
                                     error=f"復習問題が不足しています（{available_questions}問）。もう少し問題を解いてから復習してください。",
                                     error_type="insufficient_review_questions")
            
            logger.info(f"復習セッション問題数決定: 理想{target_session_size}問 → 実際{session_size}問（利用可能{available_questions}問）")
            
            selected_review_items = review_questions_with_score[:session_size]
            review_questions = []
            
            # 問題データの安全な抽出
            for item in selected_review_items:
                try:
                    question = item.get('question')
                    if question and question.get('id'):
                        review_questions.append(question)
                except Exception as extract_error:
                    logger.warning(f"問題抽出エラー: {extract_error}")
                    continue
            
            if not review_questions:
                logger.error("最終的に有効な復習問題が0問になりました")
                return render_template('error.html', 
                                     error="復習問題の準備中に問題が発生しました。しばらく待ってから再度お試しください。",
                                     error_type="final_question_preparation_error")
            
            logger.info(f"復習問題最終選択: 全{len(review_questions_with_score)}問中{len(review_questions)}問を弱点スコア順で選択")
            
            # 上位問題のスコア情報をログ出力（安全な範囲）
            for i, item in enumerate(selected_review_items[:min(5, len(selected_review_items))]):
                try:
                    q_id = item.get('question', {}).get('id', 'unknown')
                    score = item.get('weakness_score', 0)
                    wrong = item.get('wrong_count', 0)
                    total = item.get('total_attempts', 1)
                    logger.info(f"  {i+1}位: 問題ID{q_id}, 弱点スコア{score:.1f}, 間違い{wrong}/{total}")
                except Exception as log_error:
                    logger.debug(f"ログ出力エラー: {log_error}")
            
            # セッションに安全に設定
            try:
                category_name = f'復習問題（弱点優先{len(review_questions)}問）'
                
                # 問題IDの安全な変換
                question_ids = []
                for q in review_questions:
                    try:
                        q_id = int(q.get('id', 0))
                        if q_id > 0:  # 有効なIDのみ追加
                            question_ids.append(q_id)
                    except (ValueError, TypeError) as id_error:
                        logger.warning(f"問題ID変換エラー: {id_error}, question={q}")
                        continue
                
                if not question_ids:
                    logger.error("有効な問題IDが0個になりました")
                    return render_template('error.html', 
                                         error="復習問題IDの処理中にエラーが発生しました。",
                                         error_type="question_id_processing_error")
                
                # 🔥 ULTRA堅牢: セッション変数を安全に設定（ウルトラシンク対応・完全検証）
                try:
                    # セッションクリア（競合防止）
                    session.pop('exam_question_ids', None)
                    session.pop('exam_current', None)
                    session.pop('exam_category', None)
                    session.pop('selected_question_type', None)
                    session.pop('department', None)
                    session.pop('selected_department', None)
                    
                    # 新しいセッション設定
                    session['exam_question_ids'] = question_ids
                    session['exam_current'] = 0
                    session['exam_category'] = category_name
                    session['selected_question_type'] = 'review'  # 復習専用タイプ
                    session['department'] = ''  # 復習では部門指定なし
                    session['selected_department'] = ''  # セッション再構築用（復習では部門なし）
                    session.modified = True
                    
                    # セッション即座保存強制
                    session.permanent = False
                    
                    logger.info(f"復習セッション設定完了: {len(question_ids)}問, モード: {category_name}")
                    logger.info(f"復習詳細: 弱点スコア順優先, 全部門対象, 問題ID={question_ids[:5] if question_ids else []}")
                    
                except Exception as set_error:
                    logger.error(f"セッション変数設定エラー: {set_error}")
                    return render_template('error.html', 
                                         error="復習セッション変数の設定中にエラーが発生しました。",
                                         error_type="session_variable_error")
                
                # 🔥 ULTRA堅牢: セッション状態の最終確認（複数回検証）
                verification_attempts = 0
                max_verification_attempts = 3
                
                while verification_attempts < max_verification_attempts:
                    try:
                        final_ids = session.get('exam_question_ids', [])
                        final_current = session.get('exam_current', -1)
                        final_category = session.get('exam_category', '')
                        final_question_type = session.get('selected_question_type', '')
                        
                        logger.info(f"セッション設定確認 (試行{verification_attempts + 1}): exam_question_ids={len(final_ids) if final_ids else 0}問, exam_current={final_current}, exam_category='{final_category}', question_type='{final_question_type}'")
                        
                        # 検証条件
                        if (final_ids and len(final_ids) > 0 and 
                            final_current >= 0 and 
                            final_category and 
                            final_question_type == 'review'):
                            logger.info(f"✅ セッション設定検証成功 (試行{verification_attempts + 1})")
                            break
                        else:
                            verification_attempts += 1
                            if verification_attempts < max_verification_attempts:
                                logger.warning(f"セッション設定検証失敗 (試行{verification_attempts}) - 再設定中...")
                                # 再設定
                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = 0
                                session['exam_category'] = category_name
                                session['selected_question_type'] = 'review'
                                session.modified = True
                            else:
                                logger.error(f"セッション設定検証失敗 (最大試行{max_verification_attempts}回)")
                                return render_template('error.html', 
                                                     error="復習セッションの設定検証に失敗しました。ページを再読み込みして再度お試しください。",
                                                     error_type="session_verification_error")
                    except Exception as verify_error:
                        logger.error(f"セッション検証エラー (試行{verification_attempts + 1}): {verify_error}")
                        verification_attempts += 1
                
            except Exception as session_error:
                logger.error(f"セッション設定エラー: {session_error}")
                return render_template('error.html', 
                                     error="復習セッションの準備中にエラーが発生しました。",
                                     error_type="session_preparation_error")
            
        except Exception as final_error:
            logger.error(f"最終処理エラー: {final_error}")
            return render_template('error.html', 
                                 error="復習問題の最終準備中にエラーが発生しました。",
                                 error_type="final_processing_error")
        
        logger.info("=== 復習開始処理完了 - examページへリダイレクト ===")
        
        # 最初の問題にリダイレクト
        return redirect(url_for('exam'))
        
    except Exception as e:
        logger.error(f"🔥 復習問題開始の重大エラー: {e}")
        import traceback
        logger.error(f"詳細エラー情報: {traceback.format_exc()}")
        return render_template('error.html', 
                             error="復習問題の開始中に予期しないエラーが発生しました。ページを再読み込みして再度お試しください。",
                             error_type="critical_review_error")

@app.route('/debug/create_review_data')
def create_review_test_data():
    """🔥 復習テスト用ダミーデータ作成（ウルトラシンク対応）"""
    try:
        from datetime import datetime, timedelta
        import random
        
        # データディレクトリの設定
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        all_questions = load_rccm_data_files(data_dir)
        if not all_questions:
            return "問題データが見つかりません", 400
        
        # ランダムに10-20問を選択してSRSデータを作成
        sample_size = min(20, len(all_questions))
        sample_questions = random.sample(all_questions, sample_size)
        
        srs_data = {}
        bookmarks = []
        
        for i, question in enumerate(sample_questions):
            q_id = str(question.get('id', ''))
            if not q_id:
                continue
                
            # 多様な復習データを作成
            wrong_count = random.randint(1, 5)
            total_attempts = wrong_count + random.randint(1, 3)
            difficulty_level = random.uniform(3.0, 8.0)
            
            # 復習期限（一部は期限切れに設定）
            days_ago = random.randint(-5, 10)  # 過去5日〜未来10日
            next_review = (datetime.now() + timedelta(days=days_ago)).isoformat()
            
            srs_data[q_id] = {
                'wrong_count': wrong_count,
                'total_attempts': total_attempts,
                'difficulty_level': difficulty_level,
                'next_review': next_review,
                'correct_count': total_attempts - wrong_count,
                'mastered': False
            }
            
            # 一部をブックマークにも追加
            if i < 5:
                bookmarks.append(q_id)
        
        # セッションに保存
        session['advanced_srs'] = srs_data
        session['bookmarks'] = bookmarks
        session.modified = True
        
        logger.info(f"復習テストデータ作成: SRS={len(srs_data)}問, ブックマーク={len(bookmarks)}問")
        
        return f"""
        <h2>🔥 復習テストデータ作成完了！</h2>
        <p>SRSデータ: {len(srs_data)}問</p>
        <p>ブックマーク: {len(bookmarks)}問</p>
        <p><a href="/review">復習リストを確認</a></p>
        <p><a href="/exam/review">復習開始をテスト</a></p>
        <p><a href="/">ホームに戻る</a></p>
        """
        
    except Exception as e:
        logger.error(f"復習テストデータ作成エラー: {e}")
        return f"エラー: {e}", 500

@app.route('/debug/clear_session')
def clear_session_debug():
    """🔥 セッションクリア（デバッグ用）"""
    try:
        # 復習関連データのみクリア
        session.pop('advanced_srs', None)
        session.pop('bookmarks', None)
        session.pop('exam_question_ids', None)
        session.pop('exam_current', None)
        session.pop('exam_category', None)
        session.modified = True
        
        return "セッションクリア完了"
    except Exception as e:
        return f"エラー: {e}", 500

@app.route('/achievements')
def achievements():
    """達成バッジ・ゲーミフィケーション画面"""
    try:
        earned_badges = session.get('earned_badges', [])
        badge_details = []
        
        for badge_id in earned_badges:
            badge_info = gamification_manager.get_badge_info(badge_id)
            badge_details.append({
                'id': badge_id,
                'name': badge_info['name'],
                'description': badge_info['description'],
                'icon': badge_info['icon'],
                'color': badge_info['color']
            })
        
        # 学習インサイト
        try:
            insights = gamification_manager.get_study_insights(session) if gamification_manager else {}
        except Exception as e:
            logger.error(f"ゲーミフィケーション状態取得エラー: {e}")
            insights = {}
        logger.debug(f"Insights keys: {list(insights.keys()) if insights else 'None'}")
        
        # 学習カレンダー
        try:
            calendar_data = gamification_manager.generate_study_calendar(session) if gamification_manager else {}
        except Exception as e:
            logger.error(f"学習カレンダー生成エラー: {e}")
            calendar_data = {}
        
        return render_template(
            'achievements.html',
            earned_badges=badge_details,
            all_badges=gamification_manager.achievements,
            insights=insights,
            calendar_data=calendar_data
        )
        
    except Exception as e:
        logger.error(f"達成画面エラー: {e}")
        return render_template('error.html', error="達成画面の表示中にエラーが発生しました。")

@app.route('/study_calendar')
def study_calendar():
    """学習カレンダー画面"""
    try:
        calendar_data = gamification_manager.generate_study_calendar(session, months=6)
        try:
            insights = gamification_manager.get_study_insights(session) if gamification_manager else {}
        except Exception as e:
            logger.error(f"ゲーミフィケーション状態取得エラー: {e}")
            insights = {}
        
        return render_template(
            'study_calendar.html',
            calendar_data=calendar_data,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"学習カレンダーエラー: {e}")
        return render_template('error.html', error="学習カレンダーの表示中にエラーが発生しました。")

# 🎯 PHASE 9 REFACTORING: 以下のルートをapi_blueprintに移動
# @app.route('/api/gamification/status')
# → blueprints/api_blueprint.py に統合済み

@app.route('/ai_analysis')
def ai_analysis():
    """AI弱点分析画面（部門別対応版）"""
    try:
        # 部門フィルタを取得
        department_filter = request.args.get('department')
        
        # AI分析実行（部門別）
        try:
            analysis_result = ai_analyzer.analyze_weak_areas(session, department_filter) if ai_analyzer else {}
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            analysis_result = {}
        
        # 推奨学習モード取得
        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)
        
        # 利用可能な部門リスト
        available_departments = {}
        history = session.get('history', [])
        for entry in history:
            dept = entry.get('department')
            if dept and dept in LIGHTWEIGHT_DEPARTMENT_MAPPING:
                if dept not in available_departments:
                    available_departments[dept] = {'count': 0, 'name': LIGHTWEIGHT_DEPARTMENT_MAPPING[dept]['name']}
                available_departments[dept]['count'] += 1
        
        return render_template(
            'ai_analysis.html',
            analysis=analysis_result,
            recommended_mode=recommended_mode,
            learning_modes=adaptive_engine.learning_modes,
            available_departments=available_departments,
            current_department=department_filter,
            departments=LIGHTWEIGHT_DEPARTMENT_MAPPING
        )
        
    except Exception as e:
        logger.error(f"AI分析エラー: {e}")
        return render_template('error.html', error="AI分析の表示中にエラーが発生しました。")

@app.route('/adaptive_quiz')
def adaptive_quiz():
    """アダプティブ問題練習モード（部門別対応版）"""
    try:
        learning_mode = request.args.get('mode', 'balanced')
        # 🎯 CLAUDE.md準拠: 可変問題数システム (10/20/30問対応)
        session_size = get_question_count_from_request()
        department = request.args.get('department', session.get('selected_department', ''))
        
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # AI分析実行（部門フィルタ適用）
        try:
            ai_analysis = ai_analyzer.analyze_weak_areas(session, department) if ai_analyzer else {}
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            ai_analysis = {}
        
        # アダプティブ問題選択（部門対応）
        adaptive_questions = adaptive_engine.get_adaptive_questions(
            session, all_questions, ai_analysis, session_size, learning_mode, department
        )
        
        if not adaptive_questions:
            return render_template('error.html', error="選択可能な問題がありません。")
        
        # アダプティブセッション開始（部門情報も保存）
        question_ids = [int(q.get('id', 0)) for q in adaptive_questions]
        session['exam_question_ids'] = question_ids
        session['exam_current'] = 0
        
        # カテゴリ名を部門別に調整
        category_name = 'AI適応学習'
        if department:
            dept_name = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
            category_name = f'AI適応学習 ({dept_name})'
        
        session['exam_category'] = category_name
        session['adaptive_mode'] = learning_mode
        if department:
            session['selected_department'] = department
        session.modified = True
        
        logger.info(f"アダプティブ問題開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}")
        
        # 最初の問題を表示
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"アダプティブ問題エラー: {e}")
        return render_template('error.html', error="アダプティブ問題の開始中にエラーが発生しました。")

@app.route('/integrated_learning')
def integrated_learning():
    """4-1基礎と4-2専門の連携学習モード"""
    try:
        # パラメータ取得
        learning_mode = request.args.get('mode', 'basic_to_specialist')
        # 🎯 CLAUDE.md準拠: 可変問題数システム (10/20/30問対応)
        session_size = get_question_count_from_request()
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 連携学習モードの検証
        if learning_mode not in ['basic_to_specialist', 'foundation_reinforced']:
            learning_mode = 'basic_to_specialist'
        
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # 基礎理解度を事前評価
        foundation_mastery = adaptive_engine._assess_foundation_mastery(session, department)
        
        # AI分析実行（部門フィルタ適用）
        try:
            ai_analysis = ai_analyzer.analyze_weak_areas(session, department) if ai_analyzer else {}
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            ai_analysis = {}
        
        # 連携学習用問題選択
        integrated_questions = adaptive_engine.get_adaptive_questions(
            session, all_questions, ai_analysis, session_size, learning_mode, department
        )
        
        if not integrated_questions:
            return render_template('error.html', error="選択可能な問題がありません。")
        
        # 連携学習セッション開始
        question_ids = [int(q.get('id', 0)) for q in integrated_questions]
        session['exam_question_ids'] = question_ids
        session['exam_current'] = 0
        
        # カテゴリ名設定
        mode_names = {
            'basic_to_specialist': '基礎→専門連携学習',
            'foundation_reinforced': '基礎強化学習'
        }
        category_name = mode_names.get(learning_mode, '連携学習')
        
        if department:
            dept_name = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
            category_name = f'{category_name} ({dept_name})'
        
        session['exam_category'] = category_name
        session['adaptive_mode'] = learning_mode
        session['foundation_mastery'] = foundation_mastery
        if department:
            session['selected_department'] = department
        session.modified = True
        
        logger.info(f"連携学習開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}, 基礎習熟度: {foundation_mastery:.2f}")
        
        # 最初の問題を表示
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"連携学習エラー: {e}")
        return render_template('error.html', error="連携学習の開始中にエラーが発生しました。")

@app.route('/integrated_learning_selection')
def integrated_learning_selection():
    """連携学習モード選択画面"""
    try:
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 現在の基礎理解度を評価
        foundation_mastery = adaptive_engine._assess_foundation_mastery(session, department)
        
        # 部門情報
        departments = LIGHTWEIGHT_DEPARTMENT_MAPPING
        department_patterns = adaptive_engine.department_learning_patterns
        
        return render_template(
            'integrated_learning_selection.html',
            foundation_mastery=foundation_mastery,
            department=department,
            departments=departments,
            department_patterns=department_patterns,
            title='連携学習モード選択'
        )
        
    except Exception as e:
        logger.error(f"連携学習選択画面エラー: {e}")
        return render_template('error.html', error="連携学習選択画面の表示中にエラーが発生しました。")

@app.route('/learner_insights')
def learner_insights():
    """学習者インサイト画面（動的難易度制御情報を含む）"""
    try:
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 学習者インサイト取得
        insights = adaptive_engine.get_learner_insights(session, department)
        
        # 部門情報
        departments = LIGHTWEIGHT_DEPARTMENT_MAPPING
        
        return render_template(
            'learner_insights.html',
            insights=insights,
            department=department,
            departments=departments,
            title='学習者レベル・インサイト'
        )
        
    except Exception as e:
        logger.error(f"学習者インサイト画面エラー: {e}")
        return render_template('error.html', error="学習者インサイト画面の表示中にエラーが発生しました。")

# 🎯 PHASE 10 REFACTORING: 以下のルートをapi_blueprintに移動
# @app.route('/api/difficulty/status')
# → blueprints/api_blueprint.py に統合済み

@app.route('/learning_optimization')
def learning_optimization():
    """学習効率最適化画面"""
    try:
        # 個人学習パターン分析
        learning_pattern = learning_optimizer.analyze_personal_learning_pattern(session)
        
        # 最適学習時間推奨
        optimization_data = learning_optimizer.get_optimal_study_time_recommendation(session)
        
        return render_template(
            'learning_optimization.html',
            learning_pattern=learning_pattern,
            optimization_data=optimization_data,
            title='学習効率最適化'
        )
        
    except Exception as e:
        logger.error(f"学習効率最適化画面エラー: {e}")
        return render_template('error.html', error="学習効率最適化画面の表示中にエラーが発生しました。")

# 🎯 PHASE 13 REFACTORING: 以下の3ルートをlearning_blueprintに移動
# @app.route('/api/learning/realtime_tracking', methods=['POST'])
# @app.route('/api/learning/biorhythm', methods=['POST'])
# @app.route('/api/learning/optimal_schedule', methods=['GET'])
# → blueprints/learning_blueprint.py に統合済み (Lines 23-148)

# 🎯 PHASE 19 REFACTORING: AI分析APIをanalytics_blueprintに移動
# @app.route('/api/ai_analysis', methods=['GET'])
# → blueprints/analytics_blueprint.py に統合済み (Lines 23-53)

@app.route('/learning_plan')
def learning_plan():
    """個人学習プラン画面"""
    try:
        # AI分析実行
        analysis_result = ai_analyzer.analyze_weak_areas(session)
        
        # 学習プラン詳細
        learning_plan = analysis_result.get('learning_plan', {})
        weak_areas = analysis_result.get('weak_areas', {})
        
        # 推奨スケジュール生成
        schedule = generate_weekly_schedule(learning_plan, weak_areas)
        
        return render_template(
            'learning_plan.html',
            analysis=analysis_result,
            plan=learning_plan,
            schedule=schedule
        )
        
    except Exception as e:
        logger.error(f"学習プランエラー: {e}")
        return render_template('error.html', error="学習プランの表示中にエラーが発生しました。")

def generate_weekly_schedule(learning_plan: Dict, weak_areas: Dict) -> List[Dict]:
    """週間学習スケジュールの生成"""
    schedule = []
    
    for day in range(7):
        day_names = ['月', '火', '水', '木', '金', '土', '日']
        
        if learning_plan.get('plan_type') == 'weakness_focused':
            primary_focus = learning_plan.get('primary_focus', {})
            if day % 3 == 0 and primary_focus:  # 3日に1回集中学習
                schedule.append({
                    'day': day_names[day],
                    'type': 'intensive',
                    'focus': primary_focus.get('category', ''),
                    'questions': primary_focus.get('recommended_questions', 10),
                    'description': f"{primary_focus.get('category', '')}の集中学習"
                })
            else:
                schedule.append({
                    'day': day_names[day],
                    'type': 'light',
                    'focus': 'mixed',
                    'questions': 5,
                    'description': '軽い復習とバランス学習'
                })
        else:
            schedule.append({
                'day': day_names[day],
                'type': 'balanced',
                'focus': 'mixed',
                'questions': 8,
                'description': 'バランス学習'
            })
    
    return schedule

def submit_exam_answer():
    """試験回答提出"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session or exam_session['status'] != 'in_progress':
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        answer = request.form.get('answer')
        elapsed = float(request.form.get('elapsed', 0))
        question_index = exam_session['current_question']
        
        # 自動提出チェック
        if exam_simulator.auto_submit_check(exam_session):
            result = exam_simulator.finish_exam(exam_session)
            session['exam_session'] = exam_session
            session.modified = True
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })
        
        # 回答提出
        result = exam_simulator.submit_exam_answer(exam_session, question_index, answer, elapsed)
        
        # セッション更新
        session['exam_session'] = exam_session
        session.modified = True
        
        if result.get('exam_completed'):
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })
        else:
            return jsonify({
                'success': True,
                'next_question': result.get('next_question', 0),
                'remaining_questions': result.get('remaining_questions', 0)
            })
        
    except Exception as e:
        logger.error(f"試験回答提出エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

def flag_exam_question():
    """試験問題フラグ設定"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        question_index = int(request.form.get('question_index', 0))
        action = request.form.get('action', 'flag')  # flag or unflag
        
        if action == 'flag':
            success = exam_simulator.flag_question(exam_session, question_index)
        else:
            success = exam_simulator.unflag_question(exam_session, question_index)
        
        session['exam_session'] = exam_session
        session.modified = True
        
        return jsonify({'success': success})
        
    except Exception as e:
        logger.error(f"問題フラグエラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exam_navigation')
def exam_navigation():
    """試験ナビゲーション画面"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return redirect(url_for('exam_simulator_page'))
        
        summary = exam_simulator.get_exam_summary(exam_session)
        
        return render_template('exam_navigation.html', summary=summary, exam_session=exam_session)
        
    except Exception as e:
        logger.error(f"試験ナビゲーションエラー: {e}")
        return render_template('error.html', error="試験ナビゲーションの表示中にエラーが発生しました。")

def finish_exam():
    """試験終了"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        result = exam_simulator.finish_exam(exam_session)
        session['exam_session'] = exam_session
        session.modified = True
        
        return jsonify({
            'success': True,
            'redirect': url_for('exam_results')
        })
        
    except Exception as e:
        logger.error(f"試験終了エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/results')
def results():
    """結果画面（/resultsエイリアス）"""
    return redirect(url_for('exam_results'))

def exam_results():
    """試験結果画面"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session or 'results' not in exam_session:
            return redirect(url_for('exam_simulator_page'))
        
        results = exam_session['results']
        
        # 過去の試験結果を記録
        if 'exam_history' not in session:
            session['exam_history'] = []
        
        session['exam_history'].append({
            'exam_id': exam_session['exam_id'],
            'exam_type': exam_session['exam_type'],
            'score': results['score'],
            'date': exam_session['start_time'][:10],
            'passed': results['passed']
        })
        session.modified = True
        
        return render_template('exam_results.html', results=results, exam_session=exam_session)
        
    except Exception as e:
        logger.error(f"試験結果表示エラー: {e}")
        return render_template('error.html', error="試験結果の表示中にエラーが発生しました。")

@app.route('/advanced_statistics')
def advanced_statistics():
    """高度な統計分析画面"""
    try:
        # 試験履歴を取得
        exam_history = session.get('exam_history', [])
        
        # 包括的なレポートを生成
        comprehensive_report = advanced_analytics.generate_comprehensive_report(session, exam_history)
        
        return render_template(
            'advanced_statistics.html',
            report=comprehensive_report
        )
        
    except Exception as e:
        logger.error(f"高度な統計エラー: {e}")
        return render_template('error.html', error="高度な統計の表示中にエラーが発生しました。")

def api_exam_status():
    """試験状態API"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'exam_active': False})
        
        return jsonify({
            'exam_active': exam_session['status'] == 'in_progress',
            'time_remaining': exam_simulator.get_time_remaining(exam_session),
            'current_question': exam_session['current_question'],
            'total_questions': len(exam_session['questions']),
            'auto_submit_warning': exam_simulator.get_time_remaining(exam_session) <= 5
        })
        
    except Exception as e:
        logger.error(f"試験状態API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# モバイル機能のAPI エンドポイント

# 🎯 PHASE 11 REFACTORING: 以下の5ルートをmobile_blueprintに移動
# @app.route('/api/mobile/manifest')
# @app.route('/api/mobile/offline/save', methods=['POST'])
# @app.route('/api/mobile/offline/sync', methods=['POST'])
# @app.route('/api/mobile/question/<int:question_id>')
# @app.route('/api/mobile/cache/questions')
# → blueprints/mobile_blueprint.py に統合済み

# 🎯 PHASE 12 REFACTORING: 以下の3ルートをmobile_blueprintに移動
# @app.route('/api/mobile/voice/settings', methods=['GET', 'POST'])
# @app.route('/api/mobile/touch/settings', methods=['GET', 'POST'])
# @app.route('/api/mobile/performance', methods=['GET'])
# → blueprints/mobile_blueprint.py に統合済み (Lines 155-227)

@app.route('/mobile_settings')
def mobile_settings():
    """モバイル設定画面"""
    return render_template('mobile_settings.html')

@app.route('/manifest.json')
def pwa_manifest():
    """PWAマニフェストの配信"""
    try:
        manifest = mobile_manager.get_pwa_manifest()
        response = jsonify(manifest)
        response.headers['Content-Type'] = 'application/manifest+json'
        return response
    except Exception as e:
        logger.error(f"マニフェスト配信エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sw.js')
def service_worker():
    """Service Workerの配信"""
    try:
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')
    except Exception as e:
        logger.debug(f"Service Worker配信エラー: {e}")
        return '', 404

@app.route('/favicon.ico')
def favicon():
    """Faviconの配信"""
    try:
        return send_from_directory('static/icons', 'favicon.ico')
    except Exception as e:
        logger.debug(f"Favicon配信エラー: {e}")
        return '', 404

@app.route('/icon-<size>.png')
def app_icon(size):
    """アプリアイコンの配信"""
    try:
        return send_from_directory('static/icons', f'icon-{size}.png')
    except Exception as e:
        logger.debug(f"アイコン配信エラー: {e}")
        return '', 404

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404エラー: {request.url}")
    # 静的ファイル（アイコン、sw.js等）の404エラーは警告レベルを下げる
    if any(path in request.url for path in ['/static/icons/', '/sw.js', '/favicon.ico', '/icon-']):
        logger.debug(f"静的ファイル404: {request.url}")
        return '', 404  # 空のレスポンスを返す
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500エラー: {e}")
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

# === 管理者ダッシュボード ===

@app.route('/admin')
def admin_dashboard_page():
    """管理者ダッシュボードメイン"""
    try:
        # 全データを取得
        overview = admin_dashboard.get_system_overview()
        questions = admin_dashboard.get_question_management_data()
        users = admin_dashboard.get_user_progress_overview()
        content = admin_dashboard.get_content_analytics()
        performance = admin_dashboard.get_performance_metrics()
        
        return render_template('admin_dashboard.html',
                             overview=overview,
                             questions=questions,
                             users=users,
                             content=content,
                             performance=performance,
                             data={
                                 'overview': overview,
                                 'questions': questions,
                                 'users': users,
                                 'content': content,
                                 'performance': performance
                             })
    except Exception as e:
        logger.error(f"管理者ダッシュボードエラー: {e}")
        return render_template('error.html', error="ダッシュボードの読み込み中にエラーが発生しました")

@app.route('/admin/api/overview')
def admin_api_overview():
    """システム概要API"""
    try:
        overview = admin_dashboard.get_system_overview()
        return jsonify(overview)
    except Exception as e:
        logger.error(f"概要API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/questions')
def admin_api_questions():
    """問題管理API"""
    try:
        questions = admin_dashboard.get_question_management_data()
        return jsonify(questions)
    except Exception as e:
        logger.error(f"問題管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/users')
def admin_api_users():
    """ユーザー管理API"""
    try:
        users = admin_dashboard.get_user_progress_overview()
        return jsonify(users)
    except Exception as e:
        logger.error(f"ユーザー管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/users/<user_id>')
def admin_api_user_detail(user_id):
    """ユーザー詳細API"""
    try:
        user_detail = admin_dashboard.get_detailed_user_analysis(user_id)
        return jsonify(user_detail)
    except Exception as e:
        logger.error(f"ユーザー詳細API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/content')
def admin_api_content():
    """コンテンツ分析API"""
    try:
        content = admin_dashboard.get_content_analytics()
        return jsonify(content)
    except Exception as e:
        logger.error(f"コンテンツ分析API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/performance')
def admin_api_performance():
    """パフォーマンス指標API"""
    try:
        performance = admin_dashboard.get_performance_metrics()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"パフォーマンス指標API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/reports/<report_type>')
def admin_api_reports(report_type):
    """レポート生成API"""
    try:
        if report_type not in ['comprehensive', 'users', 'content', 'performance']:
            return jsonify({'error': 'Invalid report type'}), 400
        
        report = admin_dashboard.generate_reports(report_type)
        return jsonify(report)
    except Exception as e:
        logger.error(f"レポート生成API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/refresh')
def admin_api_refresh():
    """データ更新API"""
    try:
        # キャッシュをクリア
        global _questions_cache, _cache_timestamp
        _questions_cache = None
        _cache_timestamp = None
        
        # 新しい管理者ダッシュボードインスタンスを作成
        from admin_dashboard import AdminDashboard
        global admin_dashboard
        admin_dashboard = AdminDashboard()
        
        return jsonify({'success': True, 'message': 'データが更新されました'})
    except Exception as e:
        logger.error(f"データ更新API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === ソーシャル学習機能 ===

@app.route('/social')
def social_learning_page():
    """ソーシャル学習メインページ"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        # ユーザーの参加グループ取得
        user_groups = social_learning_manager.get_user_groups(user_id)
        
        # おすすめグループ取得
        recommended_groups = social_learning_manager.discover_groups(user_id, limit=6)
        
        # ディスカッション一覧取得
        discussions = social_learning_manager.get_discussions(limit=10)
        
        # ピア比較データ取得（エラーハンドリング強化）
        try:
            peer_comparison = social_learning_manager.get_peer_comparison(user_id, 'department')
            # エラーレスポンスの場合、Noneに設定
            if isinstance(peer_comparison, dict) and 'error' in peer_comparison:
                peer_comparison = None
        except Exception as e:
            logger.warning(f"ピア比較データ取得エラー: {e}")
            peer_comparison = None
        
        # リーダーボード取得
        leaderboard = social_learning_manager.get_leaderboard(time_period='month')
        
        return render_template('social_learning.html',
                             user_groups=user_groups,
                             recommended_groups=recommended_groups,
                             discussions=discussions,
                             peer_comparison=peer_comparison,
                             leaderboard=leaderboard)
    
    except Exception as e:
        logger.error(f"ソーシャル学習ページエラー: {e}")
        return render_template('error.html', error="ソーシャル学習ページの読み込み中にエラーが発生しました")

@app.route('/social/create_group', methods=['POST'])
def create_study_group():
    """学習グループ作成"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        group_name = request.form.get('group_name')
        description = request.form.get('description', '')
        department = request.form.get('department')
        target_exam_date = request.form.get('target_exam_date')
        
        if not group_name:
            return jsonify({'success': False, 'error': 'グループ名は必須です'})
        
        result = social_learning_manager.create_study_group(
            user_id, group_name, description, department, target_exam_date
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ作成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/join_group', methods=['POST'])
def join_study_group():
    """学習グループ参加"""
    try:
        user_id = session.get('user_id', 'anonymous')
        group_id = request.form.get('group_id')
        
        if not group_id:
            return jsonify({'success': False, 'error': 'グループIDが必要です'})
        
        result = social_learning_manager.join_group(user_id, group_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ参加エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/leave_group', methods=['POST'])
def leave_study_group():
    """学習グループ退会"""
    try:
        user_id = session.get('user_id', 'anonymous')
        group_id = request.form.get('group_id')
        
        if not group_id:
            return jsonify({'success': False, 'error': 'グループIDが必要です'})
        
        result = social_learning_manager.leave_group(user_id, group_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ退会エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/create_discussion', methods=['POST'])
def create_discussion():
    """ディスカッション作成"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'general')
        question_id = request.form.get('question_id')
        group_id = request.form.get('group_id')
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'タイトルと内容は必須です'})
        
        # question_idを整数に変換（存在する場合）
        if question_id:
            try:
                question_id = int(question_id)
            except ValueError:
                question_id = None
        
        result = social_learning_manager.create_discussion(
            user_id, title, content, question_id, group_id, category
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"ディスカッション作成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/discussion/<discussion_id>')
def discussion_detail(discussion_id):
    """ディスカッション詳細"""
    try:
        user_id = session.get('user_id', 'anonymous')
        discussion = social_learning_manager.get_discussion_detail(discussion_id, user_id)
        
        if 'error' in discussion:
            return render_template('error.html', error=discussion['error'])
        
        return render_template('discussion_detail.html', discussion=discussion)
    
    except Exception as e:
        logger.error(f"ディスカッション詳細エラー: {e}")
        return render_template('error.html', error="ディスカッション詳細の読み込み中にエラーが発生しました")

@app.route('/social/peer_comparison')
def peer_comparison():
    """ピア比較API"""
    try:
        user_id = session.get('user_id', 'anonymous')
        comparison_type = request.args.get('type', 'department')
        
        result = social_learning_manager.get_peer_comparison(user_id, comparison_type)
        
        # HTMLレスポンスとして返す（AJAX用）
        return render_template('peer_comparison_partial.html', peer_comparison=result)
    
    except Exception as e:
        logger.error(f"ピア比較エラー: {e}")
        return f'<div class="alert alert-danger">エラー: {str(e)}</div>'

@app.route('/social/leaderboard')
def leaderboard():
    """リーダーボードAPI"""
    try:
        period = request.args.get('period', 'month')
        department = request.args.get('department')
        
        result = social_learning_manager.get_leaderboard(department, period)
        
        # HTMLレスポンスとして返す（AJAX用）
        return render_template('leaderboard_partial.html', leaderboard=result, period=period)
    
    except Exception as e:
        logger.error(f"リーダーボードエラー: {e}")
        return f'<div class="alert alert-danger">エラー: {str(e)}</div>'

@app.route('/social/study_partners')
def study_partners():
    """学習パートナー推奨"""
    try:
        user_id = session.get('user_id', 'anonymous')
        partners = social_learning_manager.get_recommended_study_partners(user_id)
        
        return jsonify(partners)
    
    except Exception as e:
        logger.error(f"学習パートナー推奨エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ========================
# API統合・プロフェッショナル機能
# ========================

@app.route('/api_integration')
def api_integration_dashboard():
    """API統合ダッシュボード"""
    try:
        # API統合データ取得
        api_keys = api_manager._load_api_keys()
        certifications = api_manager._load_certifications()
        organizations = api_manager._load_organizations()
        
        # APIキー一覧を整形
        formatted_api_keys = []
        for key, info in api_keys.items():
            formatted_api_keys.append({
                'api_key': key,
                'organization': info['organization'],
                'permissions': info['permissions'],
                'created_at': info['created_at'],
                'is_active': info['is_active'],
                'usage_stats': info['usage_stats']
            })
        
        # 認定プログラム一覧を整形
        formatted_certifications = []
        for cert_id, cert_info in certifications.items():
            formatted_certifications.append({
                'id': cert_id,
                'name': cert_info['name'],
                'description': cert_info['description'],
                'requirements': cert_info['requirements'],
                'statistics': cert_info['statistics']
            })
        
        # 組織一覧を整形
        formatted_organizations = []
        for org_id, org_info in organizations.items():
            formatted_organizations.append({
                'id': org_id,
                'name': org_info['name'],
                'description': org_info['description'],
                'statistics': org_info['statistics']
            })
        
        # 認定サマリー計算
        certifications_summary = {
            'total_programs': len(certifications),
            'total_participants': sum(cert['statistics']['total_participants'] for cert in certifications.values()),
            'completion_rate': sum(cert['statistics']['completion_rate'] for cert in certifications.values()) / len(certifications) if certifications else 0
        }
        
        return render_template('api_integration.html',
                             api_keys=formatted_api_keys,
                             certification_programs=formatted_certifications,
                             certifications_summary=certifications_summary,
                             organizations=formatted_organizations,
                             generated_reports=[])  # TODO: 実装
        
    except Exception as e:
        logger.error(f"API統合ダッシュボードエラー: {e}")
        return render_template('error.html', error=str(e))

# === API認証エンドポイント ===

# 🎯 PHASE 14 REFACTORING: 以下の3ルートをauth_blueprintに移動
# @app.route('/api/auth/generate_key', methods=['POST'])
# @app.route('/api/auth/validate_key', methods=['POST'])
# @app.route('/api/auth/revoke_key', methods=['DELETE'])
# → blueprints/auth_blueprint.py に統合済み (Lines 23-113)

# 🎯 PHASE 16 REFACTORING: 以下の5ルートをuser_blueprintに移動
# @app.route('/api/users', methods=['GET'])
# @app.route('/api/users/<user_id>/progress', methods=['GET'])
# @app.route('/api/users/<user_id>/certifications', methods=['GET'])
# @app.route('/api/reports/progress', methods=['GET'])
# @app.route('/api/reports/organization/<org_id>', methods=['GET'])
# → blueprints/user_blueprint.py に統合済み (Lines 23-222)

# 🎯 PHASE 19 REFACTORING: レポートエクスポートAPIをanalytics_blueprintに移動
# @app.route('/api/reports/export/<format>', methods=['GET'])
# → blueprints/analytics_blueprint.py に統合済み (Lines 60-88)

# 🎯 PHASE 17 REFACTORING: 以下の4ルートをcertification_blueprintに移動
# @app.route('/api/certifications', methods=['GET', 'POST'])
# @app.route('/api/certifications/<cert_id>/progress', methods=['GET'])
# @app.route('/api/organizations', methods=['GET', 'POST'])
# @app.route('/api/organizations/<org_id>/users', methods=['GET'])
# → blueprints/certification_blueprint.py に統合済み (Lines 23-168)

# 🎯 PHASE 18 REFACTORING: 以下の3ルートをpersonalization_blueprintに移動
# @app.route('/api/personalization/profile/<user_id>')
# @app.route('/api/personalization/recommendations/<user_id>')
# @app.route('/api/personalization/ui/<user_id>')
# → blueprints/personalization_blueprint.py に統合済み (Lines 23-99)

# 🎯 PHASE 15 REFACTORING: 以下の5ルートをenterprise_blueprintに移動
# @app.route('/api/enterprise/users', methods=['GET'])
# @app.route('/api/enterprise/user/<user_name>/report', methods=['GET'])
# @app.route('/api/enterprise/data/integrity', methods=['GET'])
# @app.route('/api/enterprise/cache/stats', methods=['GET'])
# @app.route('/api/enterprise/cache/clear', methods=['POST'])
# → blueprints/enterprise_blueprint.py に統合済み (Lines 23-152)

@app.route('/enterprise/dashboard')
def enterprise_dashboard():
    """企業環境用管理ダッシュボード"""
    try:
        # 管理者向けダッシュボード表示
        users = enterprise_user_manager.get_all_users()

        return render_template('enterprise_dashboard.html', users=users)

    except Exception as e:
        logger.error(f"企業ダッシュボードエラー: {e}")
        return render_template('error.html', error_message=str(e)), 500

# 初期化（企業環境最適化 - 重複読み込み解決版）
try:
    # 環境変数で読み込み方式を選択（デフォルト: 高速化モード）
    fast_mode = os.environ.get('RCCM_FAST_MODE', 'true').lower() == 'true'
    
    if fast_mode:
        # 高速化モード: 遅延インポートでデータ管理初期化
        logger.info("[ENTERPRISE] High-speed mode: Enterprise data loading started")
        
        # 遅延インポート: データ管理 (Ultra Sync Safe Fallback)
        try:
            from data_manager import DataManager, SessionDataManager, EnterpriseUserManager
            from utils import enterprise_data_manager as edm

            # グローバル変数に代入
            data_manager = DataManager()
            session_data_manager = SessionDataManager(data_manager)
            enterprise_user_manager = EnterpriseUserManager(data_manager)
            enterprise_data_manager = edm
            logger.info("[DATA_MANAGER] Enterprise data management modules loaded successfully")
        except ImportError as import_error:
            logger.warning(f"[DATA_MANAGER] Optional module not found: {import_error}")
            # フォールバック: 基本機能のみで継続
            data_manager = None
            session_data_manager = None
            enterprise_user_manager = None
            enterprise_data_manager = None
        
        # 遅延インポート: 機能モジュール (オプション)
        try:
            from gamification import gamification_manager as gam_mgr
            gamification_manager = gam_mgr
            logger.info("[GAMIFICATION] Module loaded successfully")
        except ImportError as e:
            logger.warning(f"[GAMIFICATION] Optional module not found: {e}")
            gamification_manager = None

        try:
            from ai_analyzer import ai_analyzer as ai_ana
            ai_analyzer = ai_ana
        except ImportError as e:
            logger.warning(f"[AI_ANALYZER] Optional module not found: {e}")
            ai_analyzer = None

        try:
            from adaptive_learning import adaptive_engine as adp_eng
            adaptive_engine = adp_eng
        except ImportError as e:
            logger.warning(f"[ADAPTIVE_LEARNING] Optional module not found: {e}")
            adaptive_engine = None

        try:
            from exam_simulator import exam_simulator as exam_sim
            exam_simulator = exam_sim
        except ImportError as e:
            logger.warning(f"[EXAM_SIMULATOR] Optional module not found: {e}")
            exam_simulator = None
        try:
            from advanced_analytics import advanced_analytics as adv_ana
            advanced_analytics = adv_ana
        except ImportError as e:
            logger.warning(f"[ADVANCED_ANALYTICS] Optional module not found: {e}")
            advanced_analytics = None

        try:
            from mobile_features import mobile_manager as mob_mgr
            mobile_manager = mob_mgr
        except ImportError as e:
            logger.warning(f"[MOBILE_FEATURES] Optional module not found: {e}")
            mobile_manager = None

        try:
            from learning_optimizer import learning_optimizer as lrn_opt
            learning_optimizer = lrn_opt
        except ImportError as e:
            logger.warning(f"[LEARNING_OPTIMIZER] Optional module not found: {e}")
            learning_optimizer = None

        try:
            from admin_dashboard import admin_dashboard as adm_dash
            admin_dashboard = adm_dash
        except ImportError as e:
            logger.warning(f"[ADMIN_DASHBOARD] Optional module not found: {e}")
            admin_dashboard = None

        try:
            from social_learning import social_learning_manager as soc_mgr
            social_learning_manager = soc_mgr
        except ImportError as e:
            logger.warning(f"[SOCIAL_LEARNING] Optional module not found: {e}")
            social_learning_manager = None

        try:
            from api_integration import api_manager as api_mgr
            api_manager = api_mgr
        except ImportError as e:
            logger.warning(f"[API_INTEGRATION] Optional module not found: {e}")
            api_manager = None

        try:
            from advanced_personalization import advanced_personalization as adv_per
            advanced_personalization = adv_per
        except ImportError as e:
            logger.warning(f"[ADVANCED_PERSONALIZATION] Optional module not found: {e}")
            advanced_personalization = None

        preload_success = False
        if enterprise_data_manager:
            preload_success = enterprise_data_manager.preload_all_data()

        if preload_success:
            logger.info("✅ 企業環境用データ事前読み込み完了 - 高速アクセス準備完了")
            
            # データ整合性チェック（軽量版）
            integrity_report = enterprise_data_manager.get_file_integrity_check()
            logger.info(f"📊 データ整合性チェック: {integrity_report['status']} - 総計{integrity_report['total_questions']}問")
        else:
            logger.warning("⚠️ 企業環境用データ読み込み失敗 - 従来モードに切り替え")
            # フォールバック: 従来の読み込み
            initial_questions = load_questions()
            logger.info(f"📂 従来モード: {len(initial_questions)}問読み込み完了")
    else:
        # 従来モード: 後方互換性保持
        logger.info("📂 従来モード: 基本データ読み込み")
        initial_questions = load_questions()
        logger.info(f"✅ 基本アプリケーション初期化完了: {len(initial_questions)}問読み込み")
    
except Exception as e:
    logger.error(f"[ERROR] Application initialization failed: {e}")
    logger.info("[FALLBACK] Continuing with basic functionality")

# 🔥 CRITICAL FIX: 専門部門問題ルート追加（index.htmlとの整合性確保）
@app.route('/quiz/<department>')
def quiz_department(department):
    """専門部門別試験問題開始（index.htmlからの直接リンク対応）"""
    try:
        # 🔥 CRITICAL FIX: 基礎科目と専門科目の分離処理
        if department == 'basic':
            # 基礎科目の場合
            session['selected_question_type'] = 'basic'
            session['selected_department'] = 'common'  # 基礎科目は共通
            session['exam_category'] = '4-1 必須科目（基礎技術）'
            session.modified = True

            logger.info(f"基礎科目問題開始: {department}")
            return redirect(url_for('exam', question_type='basic', count=10))
        else:
            # 専門科目の場合
            department_mapping = {
                'road': '道路',
                'river': '河川、砂防及び海岸・海洋',
                'tunnel': 'トンネル',
                'urban': '都市計画及び地方計画',
                'garden': '造園',
                'env': '建設環境',
                'steel': '鋼構造及びコンクリート',
                'soil': '土質及び基礎',
                'construction': '施工計画、施工設備及び積算',
                'water': '上水道及び工業用水道',
                'forest': '森林土木',
                'agri': '農業土木'
            }

            # 日本語部門名に変換
            department_name = department_mapping.get(department, department)

            # 専門科目として試験開始
            session['selected_question_type'] = 'specialist'
            session['selected_department'] = department_name
            session['exam_category'] = f'{department_name}部門'
            session.modified = True

            logger.info(f"専門部門問題開始: {department} -> {department_name}")

        # exam.pyに専門科目パラメータ付きでリダイレクト
        return redirect(f'/exam?question_type=specialist&department={department_name}&count=10')

    except Exception as e:
        logger.error(f"専門部門問題開始エラー: {e}")
        return render_template('error.html', error="専門部門試験問題の開始中にエラーが発生しました。")

if __name__ == '__main__':
    # 🔥 本番環境のポート設定: Renderではポート10000を使用
    port = int(os.environ.get('PORT', 5003))
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '0.0.0.0'
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # サーバー配布版の場合の起動ログ
    if os.environ.get('FLASK_ENV') == 'production':
        logger.info("🌐 RCCM試験問題集2025 - サーバー配布版起動")
        logger.info("📊 問題データ事前読み込み開始...")
        try:
            questions = load_questions()
            logger.info(f"✅ 問題データ読み込み完了: {len(questions)}問")
        except Exception as e:
            logger.error(f"⚠️ 問題データ読み込み警告: {e}")
    else:
        # 開発環境の場合のWSL2 IPアドレス表示
        logger.info("RCCM試験問題集アプリケーション起動中...")
        logger.info("アクセスURL: http://172.18.44.152:5003")
        logger.info("アクセスURL: http://localhost:5003")
    
    # サーバー起動
    logger.info(f"[STARTUP] RCCM Quiz Application 2025 Enterprise Edition starting...")
    logger.info(f"[CONFIG] Host: {host}, Port: {port}, Debug: {debug_mode}")
    
    if __name__ == '__main__':
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True,
            use_reloader=False
        )
