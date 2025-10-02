"""
Department Management Helpers for RCCM Quiz Application
部門マッピング関連のヘルパー関数 - 20以上の重複を削減
"""
from config import LIGHTWEIGHT_DEPARTMENT_MAPPING
import logging

logger = logging.getLogger(__name__)


def get_department_name(dept_id):
    """
    部門IDから日本語部門名を取得

    Args:
        dept_id (str): 部門ID (例: 'road', 'river', 'urban')

    Returns:
        str: 日本語部門名 (例: '道路', '河川、砂防及び海岸・海洋')
             存在しない場合は dept_id をそのまま返す

    Examples:
        >>> get_department_name('road')
        '道路'
        >>> get_department_name('river')
        '河川、砂防及び海岸・海洋'
        >>> get_department_name('invalid')
        'invalid'
    """
    return LIGHTWEIGHT_DEPARTMENT_MAPPING.get(dept_id, dept_id)


def get_department_id(dept_name):
    """
    日本語部門名から部門IDを逆引き

    Args:
        dept_name (str): 日本語部門名 (例: '道路', '河川、砂防及び海岸・海洋')

    Returns:
        str: 部門ID (例: 'road', 'river')
             見つからない場合は dept_name をそのまま返す

    Examples:
        >>> get_department_id('道路')
        'road'
        >>> get_department_id('河川、砂防及び海岸・海洋')
        'river'
    """
    for dept_id, name in LIGHTWEIGHT_DEPARTMENT_MAPPING.items():
        if name == dept_name:
            return dept_id
    return dept_name


def validate_department_id(dept_id):
    """
    部門IDの妥当性チェック

    Args:
        dept_id (str): 部門ID

    Returns:
        bool: 有効な部門IDの場合 True、無効な場合 False

    Examples:
        >>> validate_department_id('road')
        True
        >>> validate_department_id('invalid_dept')
        False
    """
    return dept_id in LIGHTWEIGHT_DEPARTMENT_MAPPING


def get_all_departments():
    """
    全部門のマッピング辞書を取得

    Returns:
        dict: {dept_id: dept_name} の辞書

    Examples:
        >>> depts = get_all_departments()
        >>> depts['road']
        '道路'
    """
    return LIGHTWEIGHT_DEPARTMENT_MAPPING.copy()


def get_department_list():
    """
    全部門のリストを取得 (ID, 名前のタプルのリスト)

    Returns:
        list: [(dept_id, dept_name), ...] のリスト

    Examples:
        >>> depts = get_department_list()
        >>> ('road', '道路') in depts
        True
    """
    return list(LIGHTWEIGHT_DEPARTMENT_MAPPING.items())


def get_department_count():
    """
    登録されている部門数を取得

    Returns:
        int: 部門数

    Examples:
        >>> get_department_count()
        13
    """
    return len(LIGHTWEIGHT_DEPARTMENT_MAPPING)


def filter_questions_by_department(questions, dept_id):
    """
    部門IDで問題をフィルタリング

    Args:
        questions (list): 問題リスト
        dept_id (str): 部門ID

    Returns:
        list: フィルタリングされた問題リスト

    Examples:
        >>> questions = [{'category': '道路', ...}, {'category': '河川、砂防及び海岸・海洋', ...}]
        >>> filtered = filter_questions_by_department(questions, 'road')
        >>> len(filtered) == 1
        True
    """
    if not questions:
        return []

    # 部門IDから日本語名を取得
    dept_name = get_department_name(dept_id)

    # カテゴリーフィールドで一致する問題を抽出
    filtered = [
        q for q in questions
        if q.get('category') == dept_name or q.get('department') == dept_id
    ]

    logger.debug(f"フィルタリング結果: 部門'{dept_name}' ({dept_id}) - {len(filtered)}問")
    return filtered


def get_department_info(dept_id):
    """
    部門の詳細情報を取得

    Args:
        dept_id (str): 部門ID

    Returns:
        dict: 部門情報
            - id: 部門ID
            - name: 日本語部門名
            - exists: 存在するかどうか

    Examples:
        >>> info = get_department_info('road')
        >>> info['name']
        '道路'
        >>> info['exists']
        True
    """
    exists = validate_department_id(dept_id)
    return {
        'id': dept_id,
        'name': get_department_name(dept_id) if exists else dept_id,
        'exists': exists
    }


def normalize_department(dept_input):
    """
    部門の入力を正規化 (IDまたは名前 → ID)

    Args:
        dept_input (str): 部門IDまたは日本語部門名

    Returns:
        str: 正規化された部門ID

    Examples:
        >>> normalize_department('road')
        'road'
        >>> normalize_department('道路')
        'road'
        >>> normalize_department('invalid')
        'invalid'
    """
    # まず部門IDとして存在するかチェック
    if validate_department_id(dept_input):
        return dept_input

    # 日本語名として逆引き
    dept_id = get_department_id(dept_input)
    return dept_id


def get_departments_by_type(question_type='specialist'):
    """
    問題タイプに応じた部門リストを取得

    Args:
        question_type (str): 'basic' または 'specialist'

    Returns:
        list: 部門リスト [(dept_id, dept_name), ...]

    Examples:
        >>> basic_depts = get_departments_by_type('basic')
        >>> ('basic', '基礎科目（共通）') in basic_depts
        True
    """
    if question_type == 'basic':
        # 基礎科目のみ
        return [('basic', LIGHTWEIGHT_DEPARTMENT_MAPPING.get('basic', '基礎科目（共通）'))]
    else:
        # 基礎科目以外の全部門
        return [(dept_id, name) for dept_id, name in LIGHTWEIGHT_DEPARTMENT_MAPPING.items()
                if dept_id != 'basic']


def is_basic_department(dept_id):
    """
    基礎科目かどうかを判定

    Args:
        dept_id (str): 部門ID

    Returns:
        bool: 基礎科目の場合 True

    Examples:
        >>> is_basic_department('basic')
        True
        >>> is_basic_department('road')
        False
    """
    return dept_id == 'basic'


def format_department_display(dept_id, include_id=False):
    """
    部門の表示用文字列を生成

    Args:
        dept_id (str): 部門ID
        include_id (bool): IDを含めるかどうか

    Returns:
        str: 表示用文字列

    Examples:
        >>> format_department_display('road')
        '道路'
        >>> format_department_display('road', include_id=True)
        '道路 (road)'
    """
    dept_name = get_department_name(dept_id)

    if include_id and dept_id in LIGHTWEIGHT_DEPARTMENT_MAPPING:
        return f"{dept_name} ({dept_id})"
    else:
        return dept_name