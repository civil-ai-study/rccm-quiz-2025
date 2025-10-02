"""
Decorators for RCCM Quiz Application
安全なデコレータ抽出 - リスクゼロ
"""
from functools import wraps
from flask import request, jsonify, render_template, session
import logging

logger = logging.getLogger(__name__)


def require_questions(f):
    """
    問題データの読み込みを保証するデコレータ
    問題データが存在しない場合はエラーページを表示

    Usage:
        @app.route('/exam')
        @require_questions
        def exam(questions):
            # questions は自動的に渡される
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 遅延インポートで循環依存回避
            from utils import load_questions_improved

            questions = load_questions_improved()
            if not questions or len(questions) == 0:
                logger.error("問題データが存在しません")
                return render_template('error.html',
                                     error="問題データが存在しません。管理者に連絡してください。",
                                     error_type='data_not_found')

            # questions を引数として渡す
            return f(*args, questions=questions, **kwargs)
        except Exception as e:
            logger.error(f"問題データ読み込みエラー: {e}")
            return render_template('error.html',
                                 error=f"問題データの読み込み中にエラーが発生しました: {str(e)}",
                                 error_type='data_load_error')

    return decorated_function


def require_api_key(permission=None):
    """
    API認証を要求するデコレータ

    Args:
        permission: 必要な権限（'read_users', 'write_data'等）

    Usage:
        @app.route('/api/users')
        @require_api_key(permission='read_users')
        def api_users():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # API キーの取得
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                logger.warning(f"API key missing for {request.path}")
                return jsonify({
                    'success': False,
                    'error': 'API key required',
                    'message': 'X-API-Key ヘッダーが必要です'
                }), 401

            try:
                # 遅延インポートで循環依存回避
                from api_integration import APIIntegrationManager
                api_manager = APIIntegrationManager()

                # API キーの検証
                validation = api_manager.validate_api_key(api_key, permission)
                if not validation.get('valid'):
                    logger.warning(f"Invalid API key for {request.path}: {validation.get('error')}")
                    return jsonify({
                        'success': False,
                        'error': validation.get('error', 'Invalid API key'),
                        'message': 'API キーが無効です'
                    }), 401

                # 検証成功 - 元の関数を実行
                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"API key validation error: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Authentication error',
                    'message': f'認証エラー: {str(e)}'
                }), 500

        return decorated_function
    return decorator


def handle_errors(error_template='error.html'):
    """
    例外を自動的にキャッチしてエラーページを表示するデコレータ

    Args:
        error_template: エラー表示用のテンプレート

    Usage:
        @app.route('/statistics')
        @handle_errors()
        def statistics():
            # 例外が発生しても自動的にエラーページ表示
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
                return render_template(error_template,
                                     error=f"{f.__name__}実行中にエラーが発生しました: {str(e)}",
                                     error_type='internal_error')
        return decorated_function
    return decorator


def track_performance(f):
    """
    関数の実行時間を記録するデコレータ（デバッグ用）

    Usage:
        @app.route('/exam')
        @track_performance
        def exam():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        start_time = time.time()

        result = f(*args, **kwargs)

        elapsed_time = time.time() - start_time
        if elapsed_time > 1.0:  # 1秒以上かかった場合のみログ
            logger.warning(f"⏱️ {f.__name__} took {elapsed_time:.2f}s")

        return result

    return decorated_function


def require_session_data(required_keys):
    """
    セッションに必要なデータが存在することを確認するデコレータ

    Args:
        required_keys: 必要なセッションキーのリスト

    Usage:
        @app.route('/result')
        @require_session_data(['exam_question_ids', 'history'])
        def result():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing_keys = [key for key in required_keys if key not in session]

            if missing_keys:
                logger.warning(f"Missing session data for {f.__name__}: {missing_keys}")
                return render_template('error.html',
                                     error="セッションデータが不足しています。最初からやり直してください。",
                                     error_type='session_error')

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def api_json_response(f):
    """
    APIレスポンスを標準化するデコレータ
    例外を自動的にJSON形式でラップ

    Usage:
        @app.route('/api/data')
        @api_json_response
        def get_data():
            return {'data': [...]}  # 自動的に {'success': True, 'data': [...]} に変換
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)

            # 既に JSONify されている場合はそのまま返す
            if isinstance(result, tuple):
                return result

            # 辞書を標準フォーマットでラップ
            if isinstance(result, dict) and 'success' not in result:
                result = {'success': True, **result}

            return jsonify(result)

        except Exception as e:
            logger.error(f"API error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'APIエラーが発生しました'
            }), 500

    return decorated_function