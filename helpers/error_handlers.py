"""
Error Handling Utilities for RCCM Quiz Application
エラーハンドリング標準化 - 50以上の重複を削減
"""
from flask import render_template, jsonify, request
import logging

logger = logging.getLogger(__name__)


def json_error(message, status_code=500, error_type='general_error', **kwargs):
    """
    JSON形式のエラーレスポンスを生成

    Args:
        message (str): エラーメッセージ
        status_code (int): HTTPステータスコード (デフォルト: 500)
        error_type (str): エラータイプ
        **kwargs: 追加情報

    Returns:
        tuple: (jsonify response, status_code)

    Examples:
        >>> json_error("データが見つかりません", 404)
        ({'error': 'データが見つかりません', ...}, 404)
    """
    error_response = {
        'success': False,
        'error': message,
        'error_type': error_type,
        'status_code': status_code
    }

    # 追加情報を含める
    if kwargs:
        error_response.update(kwargs)

    # ログ出力
    log_error(message, status_code, error_type)

    return jsonify(error_response), status_code


def template_error(message, error_type='general_error', template='error.html', **kwargs):
    """
    テンプレート形式のエラーレスポンスを生成

    Args:
        message (str): エラーメッセージ
        error_type (str): エラータイプ
        template (str): エラーテンプレート (デフォルト: 'error.html')
        **kwargs: テンプレートに渡す追加変数

    Returns:
        rendered template

    Examples:
        >>> template_error("セッションが切れました", 'session_error')
        render_template('error.html', error='セッションが切れました', ...)
    """
    # ログ出力
    log_error(message, 500, error_type)

    # テンプレート変数の準備
    template_vars = {
        'error': message,
        'error_type': error_type,
        **kwargs
    }

    return render_template(template, **template_vars)


def api_error(message, status_code=500, error_code=None, **kwargs):
    """
    API用の標準エラーレスポンス

    Args:
        message (str): エラーメッセージ
        status_code (int): HTTPステータスコード
        error_code (str): アプリケーション固有のエラーコード
        **kwargs: 追加情報

    Returns:
        tuple: (jsonify response, status_code)

    Examples:
        >>> api_error("API key required", 401, error_code='AUTH001')
        ({'success': False, 'error': 'API key required', ...}, 401)
    """
    error_response = {
        'success': False,
        'error': message,
        'status_code': status_code
    }

    if error_code:
        error_response['error_code'] = error_code

    if kwargs:
        error_response.update(kwargs)

    # ログ出力
    log_error(f"[API] {message}", status_code, error_code or 'api_error')

    return jsonify(error_response), status_code


def data_not_found_error(resource_name="データ", template_mode=True):
    """
    データ不在エラーの標準レスポンス

    Args:
        resource_name (str): リソース名
        template_mode (bool): Trueの場合テンプレート、Falseの場合JSON

    Returns:
        rendered template or json response

    Examples:
        >>> data_not_found_error("問題データ")
        render_template('error.html', error='問題データが存在しません。')
    """
    message = f"{resource_name}が存在しません。"

    if template_mode:
        return template_error(message, error_type='data_not_found')
    else:
        return json_error(message, 404, error_type='data_not_found')


def session_error(message="セッションデータが不足しています。最初からやり直してください。", template_mode=True):
    """
    セッションエラーの標準レスポンス

    Args:
        message (str): エラーメッセージ
        template_mode (bool): Trueの場合テンプレート、Falseの場合JSON

    Returns:
        rendered template or json response

    Examples:
        >>> session_error()
        render_template('error.html', error='セッションデータが不足しています。...')
    """
    if template_mode:
        return template_error(message, error_type='session_error')
    else:
        return json_error(message, 400, error_type='session_error')


def validation_error(field_name, message=None, template_mode=False):
    """
    バリデーションエラーの標準レスポンス

    Args:
        field_name (str): フィールド名
        message (str): カスタムメッセージ（オプション）
        template_mode (bool): Trueの場合テンプレート、Falseの場合JSON

    Returns:
        rendered template or json response

    Examples:
        >>> validation_error("answer", "無効な回答です")
        ({'success': False, 'error': '無効な回答です', ...}, 400)
    """
    if not message:
        message = f"{field_name}が無効です。"

    if template_mode:
        return template_error(message, error_type='validation_error')
    else:
        return json_error(message, 400, error_type='validation_error', field=field_name)


def permission_denied_error(message="この操作を実行する権限がありません。", template_mode=False):
    """
    権限エラーの標準レスポンス

    Args:
        message (str): エラーメッセージ
        template_mode (bool): Trueの場合テンプレート、Falseの場合JSON

    Returns:
        rendered template or json response
    """
    if template_mode:
        return template_error(message, error_type='permission_denied')
    else:
        return json_error(message, 403, error_type='permission_denied')


def log_error(message, status_code=500, error_type='general_error'):
    """
    エラーをログに記録

    Args:
        message (str): エラーメッセージ
        status_code (int): HTTPステータスコード
        error_type (str): エラータイプ
    """
    # リクエスト情報を含める
    try:
        request_info = f"{request.method} {request.path}"
        full_message = f"[{error_type}] {message} | Request: {request_info}"
    except RuntimeError:
        # リクエストコンテキスト外の場合
        full_message = f"[{error_type}] {message}"

    # ステータスコードに応じてログレベルを変更
    if status_code >= 500:
        logger.error(full_message)
    elif status_code >= 400:
        logger.warning(full_message)
    else:
        logger.info(full_message)


def standardize_error_response(exception, template_mode=True):
    """
    例外を標準エラーレスポンスに変換

    Args:
        exception (Exception): 例外オブジェクト
        template_mode (bool): Trueの場合テンプレート、Falseの場合JSON

    Returns:
        rendered template or json response

    Examples:
        >>> try:
        ...     raise ValueError("Invalid input")
        ... except Exception as e:
        ...     response = standardize_error_response(e)
    """
    error_message = str(exception)
    error_type = type(exception).__name__

    # カスタム例外タイプの処理
    if 'DataLoadError' in error_type or 'DataValidationError' in error_type:
        return data_not_found_error("データ", template_mode)
    elif 'ValidationError' in error_type:
        return validation_error("入力データ", error_message, template_mode)
    else:
        # 汎用エラー
        generic_message = f"エラーが発生しました: {error_message}"
        if template_mode:
            return template_error(generic_message, error_type='internal_error')
        else:
            return json_error(generic_message, 500, error_type='internal_error')


def create_error_context(error_message, error_type='general_error', **kwargs):
    """
    エラーコンテキスト辞書を生成（テンプレート用）

    Args:
        error_message (str): エラーメッセージ
        error_type (str): エラータイプ
        **kwargs: 追加情報

    Returns:
        dict: エラーコンテキスト

    Examples:
        >>> ctx = create_error_context("ファイルが見つかりません", 'file_not_found', file_path='/data/test.csv')
        >>> ctx['error']
        'ファイルが見つかりません'
    """
    context = {
        'error': error_message,
        'error_type': error_type,
        'has_error': True
    }

    context.update(kwargs)
    return context