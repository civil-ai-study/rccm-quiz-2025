#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SRS (Spaced Repetition System) Service for RCCM Quiz Application
間隔反復学習システムサービス - Phase 4 Refactoring

このモジュールはSRS（間隔反復学習）関連のすべての操作を統合します。
忘却曲線に基づく復習スケジュール管理、学習進捗追跡、アダプティブ学習を提供します。
"""
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SRSService:
    """SRS（間隔反復学習）管理の中央サービス"""

    # SRSセッションキー定数
    KEY_ADVANCED_SRS = 'advanced_srs'
    KEY_BOOKMARKS = 'bookmarks'

    # SRS設定定数
    BASE_INTERVALS = [1, 3, 7, 14, 30, 90, 180, 365]  # 日数（エビングハウスの忘却曲線ベース）
    MASTERY_THRESHOLD = 5  # マスター判定に必要な正解回数
    MAX_DIFFICULTY = 10  # 最大難易度レベル
    MIN_DIFFICULTY = 1   # 最小難易度レベル

    @staticmethod
    def calculate_next_review_date(
        correct_count: int,
        wrong_count: int,
        last_interval: int = 1
    ) -> Tuple[datetime, int]:
        """
        忘却曲線に基づく次回復習日の計算

        Args:
            correct_count: 連続正解回数
            wrong_count: 間違い回数
            last_interval: 前回の間隔（日数）

        Returns:
            次回復習日時と間隔（日数）のタプル
        """
        # 難易度係数（間違いが多いほど頻繁に復習）
        difficulty_factor = max(0.1, 1.0 - (wrong_count * 0.1))

        # 習熟度レベル（正解回数に基づく）
        mastery_level = min(correct_count, len(SRSService.BASE_INTERVALS) - 1)

        # 次回間隔を計算
        base_interval = SRSService.BASE_INTERVALS[mastery_level]
        adjusted_interval = max(1, int(base_interval * difficulty_factor))

        # 次回復習日を計算
        next_review = datetime.now() + timedelta(days=adjusted_interval)

        return next_review, adjusted_interval

    @staticmethod
    def initialize_srs_data(session: Dict) -> Dict:
        """
        SRSデータの初期化

        Args:
            session: セッションオブジェクト

        Returns:
            初期化されたSRSデータ
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            session[SRSService.KEY_ADVANCED_SRS] = {}

        return session[SRSService.KEY_ADVANCED_SRS]

    @staticmethod
    def update_srs_data(
        question_id: int,
        is_correct: bool,
        session: Dict
    ) -> Dict:
        """
        高度なSRSデータの更新

        Args:
            question_id: 問題ID
            is_correct: 正解かどうか
            session: セッションオブジェクト

        Returns:
            更新されたSRSデータ
        """
        # SRSデータの初期化
        srs_data = SRSService.initialize_srs_data(session)
        qid_str = str(question_id)

        # 問題のSRSデータを取得または初期化
        if qid_str not in srs_data:
            srs_data[qid_str] = {
                'correct_count': 0,
                'wrong_count': 0,
                'total_attempts': 0,
                'first_attempt': datetime.now().isoformat(),
                'last_attempt': datetime.now().isoformat(),
                'mastered': False,
                'difficulty_level': 5,  # 1-10 (1=易しい, 10=難しい)
                'next_review': datetime.now().isoformat(),
                'interval_days': 1
            }

        question_data = srs_data[qid_str]

        # 後方互換性保証（interval_daysが存在しない古いデータへの対応）
        if 'interval_days' not in question_data:
            question_data['interval_days'] = 1
            logger.info(f"SRS後方互換性修正: 問題ID {qid_str} にinterval_days=1を追加")

        # 統計更新
        question_data['total_attempts'] += 1
        question_data['last_attempt'] = datetime.now().isoformat()

        if is_correct:
            question_data['correct_count'] += 1
            # 難易度を下げる（正解したので少し易しくなったと判定）
            question_data['difficulty_level'] = max(
                SRSService.MIN_DIFFICULTY,
                question_data['difficulty_level'] - 0.5
            )

            # マスター判定
            if question_data['correct_count'] >= SRSService.MASTERY_THRESHOLD:
                question_data['mastered'] = True
                logger.info(f"問題 {question_id} がマスターレベルに到達（{SRSService.MASTERY_THRESHOLD}回正解）")

        else:
            question_data['wrong_count'] += 1
            # 難易度を上げる（間違えたので難しいと判定）
            question_data['difficulty_level'] = min(
                SRSService.MAX_DIFFICULTY,
                question_data['difficulty_level'] + 1.0
            )
            # 間違えた場合はマスター状態を解除
            question_data['mastered'] = False

        # 次回復習日の計算
        if not question_data['mastered']:
            next_review, interval = SRSService.calculate_next_review_date(
                question_data['correct_count'],
                question_data['wrong_count'],
                question_data['interval_days']
            )
            question_data['next_review'] = next_review.isoformat()
            question_data['interval_days'] = interval

        session[SRSService.KEY_ADVANCED_SRS] = srs_data
        session.modified = True

        logger.info(
            f"SRS更新: 問題{question_id} - 正解:{question_data['correct_count']}, "
            f"間違い:{question_data['wrong_count']}, 難易度:{question_data['difficulty_level']:.1f}, "
            f"マスター:{question_data['mastered']}"
        )

        return question_data

    @staticmethod
    def get_due_review_questions(
        session: Dict,
        max_count: int = 50
    ) -> List[str]:
        """
        復習が必要な問題を取得（優先度順）

        Args:
            session: セッションオブジェクト
            max_count: 最大取得数

        Returns:
            復習が必要な問題IDのリスト（優先度順）
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return []

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        now = datetime.now()
        due_questions = []

        for qid, data in srs_data.items():
            # マスター済みの問題はスキップ
            if data.get('mastered', False):
                continue

            try:
                next_review = datetime.fromisoformat(data['next_review'])
                if next_review <= now:
                    # 優先度を計算（間違いが多い＋期限が過ぎているほど高優先度）
                    days_overdue = (now - next_review).days
                    wrong_ratio = data['wrong_count'] / max(1, data['total_attempts'])
                    priority = (wrong_ratio * 100) + days_overdue + data['difficulty_level']

                    due_questions.append((qid, priority, data))
            except (ValueError, KeyError):
                # 日時解析エラーの場合は優先度最高で追加
                due_questions.append((qid, 999, data))

        # 優先度順（降順）でソートして返す
        due_questions.sort(key=lambda x: x[1], reverse=True)

        result = [qid for qid, priority, data in due_questions[:max_count]]
        logger.info(f"復習対象問題: {len(result)}問（全体: {len(due_questions)}問）")

        return result

    @staticmethod
    def get_adaptive_review_list(session: Dict) -> List[str]:
        """
        アダプティブな復習リストを生成
        間違いが多い問題ほど頻繁に出題される

        Args:
            session: セッションオブジェクト

        Returns:
            復習問題IDのリスト（頻度調整済み）
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return []

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        weighted_questions = []

        for qid, data in srs_data.items():
            # マスター済みの問題はスキップ
            if data.get('mastered', False):
                continue

            # 重み計算（間違いが多いほど高い重み）
            wrong_count = data.get('wrong_count', 0)
            total_attempts = data.get('total_attempts', 1)
            difficulty = data.get('difficulty_level', 5)

            # 重み = 間違い率 × 難易度レベル × 係数
            weight = (wrong_count / total_attempts) * difficulty * 2
            weight = max(1, int(weight))  # 最低でも1回は含める

            # 重みに応じて複数回追加（重要な問題ほど出現頻度が高くなる）
            for _ in range(weight):
                weighted_questions.append(qid)

        # シャッフルして自然な順序にする
        import random
        random.shuffle(weighted_questions)

        logger.info(f"アダプティブ復習リスト生成: {len(weighted_questions)}問（重み付き）")
        return weighted_questions

    @staticmethod
    def cleanup_mastered_questions(session: Dict) -> int:
        """
        マスター済み問題の旧復習リストからの除去

        Args:
            session: セッションオブジェクト

        Returns:
            削除された問題数
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return 0

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        bookmarks = session.get(SRSService.KEY_BOOKMARKS, [])
        removed_count = 0

        # マスター済み問題を旧復習リストから除去
        for qid, data in srs_data.items():
            if data.get('mastered', False) and qid in bookmarks:
                bookmarks.remove(qid)
                removed_count += 1
                logger.info(f"マスター済み問題を復習リストから除去: {qid}")

        session[SRSService.KEY_BOOKMARKS] = bookmarks
        session.modified = True

        return removed_count

    @staticmethod
    def get_srs_statistics(session: Dict) -> Dict[str, Any]:
        """
        SRS統計情報を取得

        Args:
            session: セッションオブジェクト

        Returns:
            統計情報の辞書
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return {
                'total_questions': 0,
                'mastered_questions': 0,
                'in_progress_questions': 0,
                'due_questions': 0,
                'average_difficulty': 0.0
            }

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        total = len(srs_data)
        mastered = sum(1 for data in srs_data.values() if data.get('mastered', False))
        in_progress = total - mastered

        # 復習期限が来ている問題数
        now = datetime.now()
        due = 0
        total_difficulty = 0

        for data in srs_data.values():
            if not data.get('mastered', False):
                try:
                    next_review = datetime.fromisoformat(data['next_review'])
                    if next_review <= now:
                        due += 1
                except (ValueError, KeyError):
                    pass

            total_difficulty += data.get('difficulty_level', 5)

        average_difficulty = total_difficulty / total if total > 0 else 0.0

        return {
            'total_questions': total,
            'mastered_questions': mastered,
            'in_progress_questions': in_progress,
            'due_questions': due,
            'average_difficulty': average_difficulty
        }

    @staticmethod
    def get_question_srs_data(
        session: Dict,
        question_id: int
    ) -> Optional[Dict]:
        """
        特定問題のSRSデータを取得

        Args:
            session: セッションオブジェクト
            question_id: 問題ID

        Returns:
            SRSデータ（存在しない場合None）
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return None

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        qid_str = str(question_id)

        return srs_data.get(qid_str)

    @staticmethod
    def reset_question_srs_data(
        session: Dict,
        question_id: int
    ) -> bool:
        """
        特定問題のSRSデータをリセット

        Args:
            session: セッションオブジェクト
            question_id: 問題ID

        Returns:
            リセット成功したかどうか
        """
        if SRSService.KEY_ADVANCED_SRS not in session:
            return False

        srs_data = session[SRSService.KEY_ADVANCED_SRS]
        qid_str = str(question_id)

        if qid_str in srs_data:
            del srs_data[qid_str]
            session[SRSService.KEY_ADVANCED_SRS] = srs_data
            session.modified = True
            logger.info(f"問題 {question_id} のSRSデータをリセットしました")
            return True

        return False
