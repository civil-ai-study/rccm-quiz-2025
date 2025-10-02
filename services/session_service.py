"""
Session Service for RCCM Quiz Application
セッション管理の統合サービス - Phase 2 Refactoring

このモジュールはセッション関連のすべての操作を統合し、
以下の問題を解決します：
- セッションクリアコードの重複（10以上の箇所）
- セッション初期化の重複（5以上の箇所）
- セッション状態取得の散在
"""
from flask import session
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SessionService:
    """
    セッション管理の中央サービス
    スレッドセーフなセッション操作を提供
    """

    # セッションキーの定義（タイポ防止）
    KEY_EXAM_QUESTION_IDS = 'exam_question_ids'
    KEY_EXAM_CURRENT = 'exam_current'
    KEY_EXAM_CATEGORY = 'exam_category'
    KEY_SELECTED_DEPARTMENT = 'selected_department'
    KEY_SELECTED_QUESTION_TYPE = 'selected_question_type'
    KEY_SELECTED_YEAR = 'selected_year'
    KEY_HISTORY = 'history'
    KEY_CATEGORY_STATS = 'category_stats'
    KEY_ADVANCED_SRS = 'advanced_srs'
    KEY_BOOKMARKS = 'bookmarks'
    KEY_SESSION_ID = 'session_id'
    KEY_USER_NAME = 'user_name'
    KEY_USER_ID = 'user_id'
    KEY_BASE_USER_ID = 'base_user_id'
    KEY_LOGIN_TIME = 'login_time'
    KEY_REQUEST_HISTORY = 'request_history'

    @staticmethod
    def clear_exam_session():
        """
        試験セッションをクリア

        以下のセッションキーを削除：
        - exam_question_ids: 試験問題IDリスト
        - exam_current: 現在の問題インデックス
        - exam_category: 試験カテゴリ
        - selected_department: 選択部門
        - selected_question_type: 問題タイプ
        - selected_year: 選択年度
        - request_history: リクエスト履歴

        Examples:
            >>> SessionService.clear_exam_session()
            # 試験関連セッションが全てクリアされる
        """
        session_keys_to_clear = [
            SessionService.KEY_EXAM_QUESTION_IDS,
            SessionService.KEY_EXAM_CURRENT,
            SessionService.KEY_EXAM_CATEGORY,
            SessionService.KEY_SELECTED_DEPARTMENT,
            SessionService.KEY_SELECTED_QUESTION_TYPE,
            SessionService.KEY_SELECTED_YEAR,
            SessionService.KEY_REQUEST_HISTORY
        ]

        for key in session_keys_to_clear:
            session.pop(key, None)

        session.modified = True
        logger.debug("試験セッションをクリアしました")

    @staticmethod
    def start_exam_session(
        question_ids: List[int],
        category: str,
        question_type: str = 'basic',
        department: str = '',
        year: Optional[int] = None
    ):
        """
        新しい試験セッションを開始

        Args:
            question_ids: 試験問題IDのリスト
            category: カテゴリ名
            question_type: 問題タイプ ('basic' または 'specialist')
            department: 部門ID（オプション）
            year: 年度（オプション）

        Examples:
            >>> SessionService.start_exam_session(
            ...     question_ids=[1, 2, 3, 4, 5],
            ...     category='基礎科目',
            ...     question_type='basic'
            ... )
        """
        # 既存の試験セッションをクリア
        SessionService.clear_exam_session()

        # 新しいセッションデータを設定
        session[SessionService.KEY_EXAM_QUESTION_IDS] = question_ids
        session[SessionService.KEY_EXAM_CURRENT] = 0
        session[SessionService.KEY_EXAM_CATEGORY] = category
        session[SessionService.KEY_SELECTED_QUESTION_TYPE] = question_type

        if department:
            session[SessionService.KEY_SELECTED_DEPARTMENT] = department

        if year:
            session[SessionService.KEY_SELECTED_YEAR] = year

        session.modified = True

        logger.info(
            f"試験セッション開始: カテゴリ={category}, "
            f"タイプ={question_type}, 問題数={len(question_ids)}"
        )

    @staticmethod
    def get_exam_state() -> Dict[str, Any]:
        """
        現在の試験セッション状態を取得

        Returns:
            dict: 試験セッションの状態
                - question_ids: 問題IDリスト
                - current: 現在の問題インデックス
                - category: カテゴリ名
                - question_type: 問題タイプ
                - department: 部門ID
                - year: 年度
                - is_active: 試験セッションがアクティブか

        Examples:
            >>> state = SessionService.get_exam_state()
            >>> if state['is_active']:
            ...     print(f"問題 {state['current'] + 1}/{len(state['question_ids'])}")
        """
        question_ids = session.get(SessionService.KEY_EXAM_QUESTION_IDS, [])
        current = session.get(SessionService.KEY_EXAM_CURRENT, 0)

        return {
            'question_ids': question_ids,
            'current': current,
            'category': session.get(SessionService.KEY_EXAM_CATEGORY, ''),
            'question_type': session.get(SessionService.KEY_SELECTED_QUESTION_TYPE, 'basic'),
            'department': session.get(SessionService.KEY_SELECTED_DEPARTMENT, ''),
            'year': session.get(SessionService.KEY_SELECTED_YEAR),
            'is_active': len(question_ids) > 0 and current < len(question_ids)
        }

    @staticmethod
    def advance_to_next_question() -> int:
        """
        次の問題に進む

        Returns:
            int: 新しい問題インデックス

        Examples:
            >>> next_index = SessionService.advance_to_next_question()
            >>> print(f"次の問題: {next_index}")
        """
        current = session.get(SessionService.KEY_EXAM_CURRENT, 0)
        session[SessionService.KEY_EXAM_CURRENT] = current + 1
        session.modified = True

        logger.debug(f"次の問題に進みました: {current} -> {current + 1}")
        return session[SessionService.KEY_EXAM_CURRENT]

    @staticmethod
    def get_current_question_index() -> int:
        """
        現在の問題インデックスを取得

        Returns:
            int: 現在の問題インデックス（0-based）
        """
        return session.get(SessionService.KEY_EXAM_CURRENT, 0)

    @staticmethod
    def is_exam_active() -> bool:
        """
        試験セッションがアクティブかチェック

        Returns:
            bool: 試験がアクティブな場合 True
        """
        state = SessionService.get_exam_state()
        return state['is_active']

    @staticmethod
    def initialize_user_session():
        """
        ユーザーセッションの初期化
        history, category_stats, advanced_srs, bookmarksを初期化

        Examples:
            >>> SessionService.initialize_user_session()
            # 未初期化のセッションデータが初期化される
        """
        if SessionService.KEY_HISTORY not in session:
            session[SessionService.KEY_HISTORY] = []

        if SessionService.KEY_CATEGORY_STATS not in session:
            session[SessionService.KEY_CATEGORY_STATS] = {}

        if SessionService.KEY_ADVANCED_SRS not in session:
            session[SessionService.KEY_ADVANCED_SRS] = {}

        if SessionService.KEY_BOOKMARKS not in session:
            session[SessionService.KEY_BOOKMARKS] = []

        session.modified = True
        logger.debug("ユーザーセッションを初期化しました")

    @staticmethod
    def set_user(user_name: str, base_user_id: str, session_id: str):
        """
        ユーザー情報をセッションに設定

        Args:
            user_name: ユーザー名
            base_user_id: 基本ユーザーID（データ永続化用）
            session_id: セッションID（セッション固有）

        Examples:
            >>> SessionService.set_user("田中太郎", "tanaka_taro", "abc123")
        """
        session_aware_user_id = f"{base_user_id}_{session_id[:8]}"

        session[SessionService.KEY_USER_NAME] = user_name
        session[SessionService.KEY_USER_ID] = session_aware_user_id
        session[SessionService.KEY_BASE_USER_ID] = base_user_id
        session[SessionService.KEY_SESSION_ID] = session_id
        session[SessionService.KEY_LOGIN_TIME] = datetime.now().isoformat()

        session.modified = True

        logger.info(f"ユーザー設定完了: {user_name} (ID: {session_aware_user_id})")

    @staticmethod
    def get_user_info() -> Dict[str, Any]:
        """
        ユーザー情報を取得

        Returns:
            dict: ユーザー情報
                - user_name: ユーザー名
                - user_id: セッション固有ユーザーID
                - base_user_id: 基本ユーザーID
                - session_id: セッションID
                - login_time: ログイン時刻
        """
        return {
            'user_name': session.get(SessionService.KEY_USER_NAME, 'anonymous'),
            'user_id': session.get(SessionService.KEY_USER_ID, 'anonymous'),
            'base_user_id': session.get(SessionService.KEY_BASE_USER_ID, 'anonymous'),
            'session_id': session.get(SessionService.KEY_SESSION_ID),
            'login_time': session.get(SessionService.KEY_LOGIN_TIME)
        }

    @staticmethod
    def add_to_history(entry: Dict[str, Any]):
        """
        履歴に回答記録を追加

        Args:
            entry: 回答記録（辞書）
                - question_id: 問題ID
                - is_correct: 正解/不正解
                - category: カテゴリ
                - department: 部門
                - question_type: 問題タイプ
                - timestamp: タイムスタンプ

        Examples:
            >>> SessionService.add_to_history({
            ...     'question_id': 123,
            ...     'is_correct': True,
            ...     'category': '基礎科目',
            ...     'timestamp': datetime.now().isoformat()
            ... })
        """
        if SessionService.KEY_HISTORY not in session:
            session[SessionService.KEY_HISTORY] = []

        session[SessionService.KEY_HISTORY].append(entry)
        session.modified = True

        logger.debug(f"履歴に追加: 問題ID={entry.get('question_id')}, 正解={entry.get('is_correct')}")

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        """
        回答履歴を取得

        Returns:
            list: 回答履歴のリスト
        """
        return session.get(SessionService.KEY_HISTORY, [])

    @staticmethod
    def get_srs_data() -> Dict[str, Any]:
        """
        SRSデータを取得

        Returns:
            dict: SRSデータ（問題ID -> SRS情報）
        """
        return session.get(SessionService.KEY_ADVANCED_SRS, {})

    @staticmethod
    def update_srs_data(question_id: str, srs_info: Dict[str, Any]):
        """
        SRSデータを更新

        Args:
            question_id: 問題ID（文字列）
            srs_info: SRS情報（辞書）
        """
        if SessionService.KEY_ADVANCED_SRS not in session:
            session[SessionService.KEY_ADVANCED_SRS] = {}

        session[SessionService.KEY_ADVANCED_SRS][str(question_id)] = srs_info
        session.modified = True

    @staticmethod
    def get_bookmarks() -> List[int]:
        """
        ブックマークを取得

        Returns:
            list: ブックマークされた問題IDのリスト
        """
        return session.get(SessionService.KEY_BOOKMARKS, [])

    @staticmethod
    def add_bookmark(question_id: int):
        """
        ブックマークを追加

        Args:
            question_id: 問題ID
        """
        if SessionService.KEY_BOOKMARKS not in session:
            session[SessionService.KEY_BOOKMARKS] = []

        if question_id not in session[SessionService.KEY_BOOKMARKS]:
            session[SessionService.KEY_BOOKMARKS].append(question_id)
            session.modified = True
            logger.info(f"ブックマーク追加: 問題ID={question_id}")

    @staticmethod
    def remove_bookmark(question_id: int):
        """
        ブックマークを削除

        Args:
            question_id: 問題ID
        """
        bookmarks = session.get(SessionService.KEY_BOOKMARKS, [])
        if question_id in bookmarks:
            bookmarks.remove(question_id)
            session[SessionService.KEY_BOOKMARKS] = bookmarks
            session.modified = True
            logger.info(f"ブックマーク削除: 問題ID={question_id}")

    @staticmethod
    def generate_session_id() -> str:
        """
        新しいセッションIDを生成

        Returns:
            str: 16進数のセッションID
        """
        return os.urandom(16).hex()

    @staticmethod
    def ensure_session_id() -> str:
        """
        セッションIDを確保（なければ生成）

        Returns:
            str: セッションID
        """
        if SessionService.KEY_SESSION_ID not in session:
            session[SessionService.KEY_SESSION_ID] = SessionService.generate_session_id()
            session.modified = True

        return session[SessionService.KEY_SESSION_ID]