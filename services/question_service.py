"""
Question Service for RCCM Quiz Application
問題管理の統合サービス - Phase 3 Refactoring

このモジュールは問題データ関連のすべての操作を統合します。
"""
from typing import List, Dict, Any, Optional
import logging
import random
from datetime import datetime, timedelta
from config import ExamConfig, SRSConfig, LIGHTWEIGHT_DEPARTMENT_MAPPING

logger = logging.getLogger(__name__)


class QuestionService:
    """問題管理の中央サービス"""

    def __init__(self):
        self._cache = None
        self._cache_timestamp = None

    @staticmethod
    def load_questions() -> List[Dict[str, Any]]:
        """
        問題データを読み込む

        Returns:
            list: 問題データのリスト
        """
        try:
            # app.pyのload_questions()を使用（循環インポート回避のため遅延インポート）
            import app
            questions = app.load_questions()
            logger.info(f"問題データ読込成功: {len(questions)}問")
            return questions
        except Exception as e:
            logger.error(f"問題データ読込エラー: {e}")
            return []

    @staticmethod
    def filter_by_department(questions: List[Dict], department: str) -> List[Dict]:
        """
        部門でフィルタリング

        Args:
            questions: 問題リスト
            department: 部門ID

        Returns:
            list: フィルタリングされた問題
        """
        from helpers.department_helpers import get_department_name
        dept_name = get_department_name(department)
        return [q for q in questions if q.get('category') == dept_name or q.get('department') == department]

    @staticmethod
    def filter_by_type(questions: List[Dict], question_type: str) -> List[Dict]:
        """
        問題タイプでフィルタリング

        Args:
            questions: 問題リスト
            question_type: 'basic' or 'specialist'

        Returns:
            list: フィルタリングされた問題
        """
        return [q for q in questions if q.get('question_type') == question_type]

    @staticmethod
    def get_question_by_id(questions: List[Dict], question_id: int) -> Optional[Dict]:
        """
        IDで問題を取得

        Args:
            questions: 問題リスト
            question_id: 問題ID

        Returns:
            dict: 問題データ（見つからない場合None）
        """
        for q in questions:
            if q.get('id') == question_id:
                return q
        return None

    @staticmethod
    def filter_by_year(questions: List[Dict], year: str) -> List[Dict]:
        """
        年度でフィルタリング（専門科目のみ）

        Args:
            questions: 問題リスト
            year: 年度

        Returns:
            list: フィルタリングされた問題
        """
        return [q for q in questions
                if str(q.get('year', '')) == str(year)
                and q.get('question_type') == 'specialist']

    @staticmethod
    def filter_by_category(questions: List[Dict], category: str) -> List[Dict]:
        """
        カテゴリでフィルタリング

        Args:
            questions: 問題リスト
            category: カテゴリ名

        Returns:
            list: フィルタリングされた問題
        """
        if category == '全体':
            return questions

        # 正確な文字列マッチング
        filtered = [q for q in questions if q.get('category') == category]

        # 文字化けフォールバック（部分マッチ）
        if len(filtered) == 0 and category:
            for q in questions:
                cat = q.get('category', '')
                if ('道路' in cat and ('道' in category or 'road' in category.lower())) or \
                   ('トンネル' in cat and ('トンネル' in category or 'tunnel' in category.lower())) or \
                   ('河川' in cat and ('河川' in category or 'civil' in category.lower())) or \
                   ('土質' in cat and ('土質' in category or 'soil' in category.lower())):
                    if q not in filtered:
                        filtered.append(q)

        return filtered

    @staticmethod
    def get_due_questions(user_session: Dict, all_questions: List[Dict]) -> List[Dict]:
        """
        復習期限が来ている問題を取得

        Args:
            user_session: ユーザーセッションデータ
            all_questions: 全問題リスト

        Returns:
            list: 復習が必要な問題（優先度順）
        """
        srs_data = user_session.get('advanced_srs', {})
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

    @staticmethod
    def get_mixed_questions(
        user_session: Dict,
        all_questions: List[Dict],
        requested_category: str = '全体',
        session_size: Optional[int] = None,
        department: str = '',
        question_type: str = '',
        year: Optional[str] = None
    ) -> List[Dict]:
        """
        新問題と復習問題をミックスした出題（RCCM部門対応版）

        Args:
            user_session: ユーザーセッション
            all_questions: 全問題リスト
            requested_category: カテゴリ（デフォルト: '全体'）
            session_size: 問題数（デフォルト: ExamConfig.QUESTIONS_PER_SESSION）
            department: 部門ID
            question_type: 'basic' or 'specialist'
            year: 年度（専門科目のみ）

        Returns:
            list: ミックスされた問題リスト
        """
        if session_size is None:
            session_size = ExamConfig.QUESTIONS_PER_SESSION

        due_questions = QuestionService.get_due_questions(user_session, all_questions)

        # 復習問題の比率設定
        max_review_count = min(len(due_questions),
                              int(session_size * SRSConfig.MAX_REVIEW_RATIO))
        selected_questions = []

        # 復習問題を追加（部門・問題種別・年度でフィルタリング）
        for i, due_item in enumerate(due_questions):
            if i >= max_review_count:
                break

            question = due_item['question']
            # 部門・問題種別の条件チェック
            if department and question.get('department') != department:
                continue
            if question_type and question.get('question_type') != question_type:
                continue
            if year and str(question.get('year', '')) != str(year):
                continue

            selected_questions.append(question)

        # 残りを新問題で埋める
        remaining_count = session_size - len(selected_questions)
        available_questions = all_questions

        # AI学習分析による弱点重視出題
        weak_categories = []
        if user_session.get('history'):
            try:
                from ai_analyzer import ai_analyzer
                weak_analysis = ai_analyzer.analyze_weak_areas(user_session, department)
                weak_categories = weak_analysis.get('weak_categories', [])
            except Exception as e:
                logger.error(f"AI分析エラー: {e}")
                weak_categories = []

        # 問題種別でフィルタリング（最優先・厳格）
        if question_type:
            if question_type == 'basic':
                available_questions = [q for q in available_questions
                                     if q.get('question_type') == 'basic'
                                     and q.get('year') is None]
                logger.info(f"基礎科目フィルタ適用: 結果 {len(available_questions)}問")

            elif question_type == 'specialist':
                available_questions = [q for q in available_questions
                                     if q.get('question_type') == 'specialist'
                                     and q.get('year') is not None]
                logger.info(f"専門科目フィルタ適用: 結果 {len(available_questions)}問")

            else:
                available_questions = [q for q in available_questions
                                     if q.get('question_type') == question_type]
                logger.info(f"問題種別フィルタ適用: {question_type}, 結果: {len(available_questions)}問")

            # 専門科目で部門指定がある場合のみ部門フィルタ適用
            if question_type == 'specialist' and department:
                target_categories = LIGHTWEIGHT_DEPARTMENT_MAPPING.get(department, department)
                logger.info(f"✅ 日本語直接マッチング: {department} → {target_categories}")

                dept_match_questions = [q for q in available_questions
                                      if q.get('category') == target_categories]
                if dept_match_questions:
                    available_questions = dept_match_questions
                    logger.info(f"専門科目部門マッチング成功: {len(available_questions)}問")
                else:
                    logger.warning(f"専門科目部門マッチング失敗: {target_categories} に該当する問題が見つかりません")

        # 部門でフィルタリング（基礎科目・専門科目以外）
        elif department and question_type != 'basic' and question_type != 'specialist':
            available_questions = [q for q in available_questions
                                 if q.get('department') == department]
            logger.info(f"部門フィルタ適用: {department}, 結果: {len(available_questions)}問")

        # カテゴリでフィルタリング
        if requested_category != '全体':
            available_questions = QuestionService.filter_by_category(available_questions, requested_category)
            logger.info(f"カテゴリフィルタ適用: {requested_category}, 結果: {len(available_questions)}問")

        # 年度でフィルタリング（専門科目のみ）
        if year:
            pre_year_count = len(available_questions)
            available_questions = QuestionService.filter_by_year(available_questions, year)
            logger.info(f"年度フィルタ適用: {year}年度, {pre_year_count} → {len(available_questions)}問")

        # 既に選択済みの問題を除外
        selected_ids = [int(q.get('id', 0)) for q in selected_questions]
        new_questions = [q for q in available_questions
                        if int(q.get('id', 0)) not in selected_ids]

        random.shuffle(new_questions)
        selected_questions.extend(new_questions[:remaining_count])

        random.shuffle(selected_questions)

        return selected_questions

    @staticmethod
    def select_random_questions(questions: List[Dict], count: int, exclude_ids: List[int] = None) -> List[Dict]:
        """
        ランダムに問題を選択

        Args:
            questions: 問題リスト
            count: 選択する問題数
            exclude_ids: 除外する問題ID

        Returns:
            list: ランダムに選択された問題
        """
        if exclude_ids is None:
            exclude_ids = []

        available = [q for q in questions if int(q.get('id', 0)) not in exclude_ids]

        if len(available) < count:
            logger.warning(f"利用可能な問題数({len(available)})が要求数({count})未満です")
            count = len(available)

        selected = random.sample(available, count) if available else []
        return selected