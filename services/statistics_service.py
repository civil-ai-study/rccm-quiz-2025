#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Statistics Service for RCCM Quiz Application
統計・分析サービス - Phase 5 Refactoring

このモジュールは統計計算、学習進捗分析、パフォーマンス追跡の全操作を統合します。
"""
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class StatisticsService:
    """統計・分析管理の中央サービス"""

    @staticmethod
    def calculate_accuracy(correct: int, total: int) -> float:
        """
        正答率を計算

        Args:
            correct: 正解数
            total: 総問題数

        Returns:
            正答率（パーセント）
        """
        return (correct / total * 100) if total > 0 else 0.0

    @staticmethod
    def get_overall_statistics(history: List[Dict]) -> Dict[str, Any]:
        """
        全体統計を取得

        Args:
            history: 学習履歴リスト

        Returns:
            全体統計の辞書
        """
        if not history:
            return {
                'total_quizzes': 0,
                'total_accuracy': 0.0,
                'average_time_per_question': None,
                'total_correct': 0,
                'total_incorrect': 0
            }

        total = len(history)
        correct = sum(1 for h in history if h.get('is_correct'))
        incorrect = total - correct
        total_time = sum(h.get('elapsed', 0) for h in history)

        return {
            'total_quizzes': total,
            'total_accuracy': StatisticsService.calculate_accuracy(correct, total),
            'average_time_per_question': round(total_time / total, 1) if total > 0 else None,
            'total_correct': correct,
            'total_incorrect': incorrect
        }

    @staticmethod
    def get_basic_specialty_statistics(history: List[Dict]) -> Dict[str, Dict]:
        """
        基礎科目・専門科目別統計を取得

        Args:
            history: 学習履歴リスト

        Returns:
            基礎/専門別統計の辞書
        """
        stats = {
            'basic': {'total_answered': 0, 'correct_count': 0, 'accuracy': 0.0},
            'specialty': {'total_answered': 0, 'correct_count': 0, 'accuracy': 0.0}
        }

        for h in history:
            question_id = h.get('id', h.get('question_id', ''))
            question_type = h.get('question_type', '')

            # 基礎科目判定
            if question_type == 'basic' or '4-1' in str(question_id):
                score_type = 'basic'
            else:
                score_type = 'specialty'

            stats[score_type]['total_answered'] += 1
            if h.get('is_correct'):
                stats[score_type]['correct_count'] += 1

        # 正答率計算
        for score_type in ['basic', 'specialty']:
            total = stats[score_type]['total_answered']
            correct = stats[score_type]['correct_count']
            stats[score_type]['accuracy'] = StatisticsService.calculate_accuracy(correct, total)

        return stats

    @staticmethod
    def get_daily_statistics(history: List[Dict]) -> List[Dict]:
        """
        日別統計を取得

        Args:
            history: 学習履歴リスト

        Returns:
            日別統計リスト（日付、正答率）
        """
        daily_stats = defaultdict(lambda: {'total': 0, 'correct': 0})

        for h in history:
            date = h.get('date', '')[:10]
            if date:
                daily_stats[date]['total'] += 1
                if h.get('is_correct'):
                    daily_stats[date]['correct'] += 1

        daily_accuracy_list = []
        for date in sorted(daily_stats.keys()):
            total = daily_stats[date]['total']
            correct = daily_stats[date]['correct']
            accuracy = StatisticsService.calculate_accuracy(correct, total)
            daily_accuracy_list.append({
                'date': date,
                'accuracy': round(accuracy, 1),
                'total': total,
                'correct': correct
            })

        return daily_accuracy_list

    @staticmethod
    def get_category_statistics(history: List[Dict]) -> Dict[str, Dict]:
        """
        カテゴリ別統計を取得

        Args:
            history: 学習履歴リスト

        Returns:
            カテゴリ別統計の辞書
        """
        category_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'accuracy': 0.0})

        for h in history:
            category = h.get('category', '不明')
            category_stats[category]['total'] += 1
            if h.get('is_correct'):
                category_stats[category]['correct'] += 1

        # 正答率計算
        for category in category_stats:
            total = category_stats[category]['total']
            correct = category_stats[category]['correct']
            category_stats[category]['accuracy'] = StatisticsService.calculate_accuracy(correct, total)

        return dict(category_stats)

    @staticmethod
    def get_department_progress(
        history: List[Dict],
        department_mapping: Dict[str, str]
    ) -> Dict[str, Dict]:
        """
        部門別進捗を取得

        Args:
            history: 学習履歴リスト
            department_mapping: 部門マッピング辞書

        Returns:
            部門別進捗の辞書
        """
        department_progress = {}

        for dept_id, dept_name in department_mapping.items():
            dept_history = [h for h in history if h.get('category') == dept_name]

            if dept_history:
                total_answered = len(dept_history)
                correct_count = sum(1 for h in dept_history if h.get('is_correct'))

                department_progress[dept_id] = {
                    'name': dept_name,
                    'total_answered': total_answered,
                    'correct_count': correct_count,
                    'accuracy': StatisticsService.calculate_accuracy(correct_count, total_answered)
                }

        return department_progress

    @staticmethod
    def get_question_type_progress(
        history: List[Dict],
        available_types: List[str]
    ) -> Dict[str, Dict]:
        """
        問題種別進捗を取得

        Args:
            history: 学習履歴リスト
            available_types: 利用可能な問題種別リスト

        Returns:
            問題種別進捗の辞書
        """
        type_progress = {}

        for type_id in available_types:
            type_history = [h for h in history if h.get('question_type') == type_id]

            if type_history:
                total_answered = len(type_history)
                correct_count = sum(1 for h in type_history if h.get('is_correct'))

                type_progress[type_id] = {
                    'total_answered': total_answered,
                    'correct_count': correct_count,
                    'accuracy': StatisticsService.calculate_accuracy(correct_count, total_answered)
                }

        return type_progress

    @staticmethod
    def calculate_progress_percentage(
        answered: int,
        total_available: int
    ) -> float:
        """
        進捗率を計算

        Args:
            answered: 回答済み問題数
            total_available: 利用可能な総問題数

        Returns:
            進捗率（パーセント）
        """
        return round((answered / total_available) * 100, 1) if total_available > 0 else 0.0

    @staticmethod
    def get_recent_history(
        history: List[Dict],
        limit: int = 30
    ) -> List[Dict]:
        """
        最近の履歴を取得

        Args:
            history: 学習履歴リスト
            limit: 取得する履歴数

        Returns:
            最近の履歴リスト
        """
        return history[-limit:] if history else []

    @staticmethod
    def get_weak_categories(
        history: List[Dict],
        threshold: float = 60.0
    ) -> List[Dict]:
        """
        弱点カテゴリを取得

        Args:
            history: 学習履歴リスト
            threshold: 弱点判定の正答率閾値（デフォルト: 60%）

        Returns:
            弱点カテゴリのリスト（正答率順）
        """
        category_stats = StatisticsService.get_category_statistics(history)

        weak_categories = []
        for category, stats in category_stats.items():
            if stats['total'] >= 3 and stats['accuracy'] < threshold:
                weak_categories.append({
                    'category': category,
                    'accuracy': stats['accuracy'],
                    'total': stats['total'],
                    'correct': stats['correct']
                })

        # 正答率の低い順にソート
        weak_categories.sort(key=lambda x: x['accuracy'])

        return weak_categories

    @staticmethod
    def get_strong_categories(
        history: List[Dict],
        threshold: float = 80.0
    ) -> List[Dict]:
        """
        得意カテゴリを取得

        Args:
            history: 学習履歴リスト
            threshold: 得意判定の正答率閾値（デフォルト: 80%）

        Returns:
            得意カテゴリのリスト（正答率順）
        """
        category_stats = StatisticsService.get_category_statistics(history)

        strong_categories = []
        for category, stats in category_stats.items():
            if stats['total'] >= 3 and stats['accuracy'] >= threshold:
                strong_categories.append({
                    'category': category,
                    'accuracy': stats['accuracy'],
                    'total': stats['total'],
                    'correct': stats['correct']
                })

        # 正答率の高い順にソート
        strong_categories.sort(key=lambda x: x['accuracy'], reverse=True)

        return strong_categories

    @staticmethod
    def get_learning_streak(history: List[Dict]) -> Dict[str, Any]:
        """
        学習連続日数を取得

        Args:
            history: 学習履歴リスト

        Returns:
            連続学習日数情報
        """
        if not history:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_days': 0
            }

        # 日付を抽出
        dates = set()
        for h in history:
            date = h.get('date', '')[:10]
            if date:
                dates.add(date)

        if not dates:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_days': 0
            }

        sorted_dates = sorted(dates)
        total_days = len(sorted_dates)

        # 現在の連続日数を計算
        current_streak = 1
        today = datetime.now().strftime('%Y-%m-%d')

        if sorted_dates[-1] == today or sorted_dates[-1] == datetime.now().strftime('%Y-%m-%d'):
            for i in range(len(sorted_dates) - 2, -1, -1):
                prev_date = datetime.strptime(sorted_dates[i], '%Y-%m-%d')
                curr_date = datetime.strptime(sorted_dates[i + 1], '%Y-%m-%d')
                diff = (curr_date - prev_date).days

                if diff == 1:
                    current_streak += 1
                else:
                    break
        else:
            current_streak = 0

        # 最長連続日数を計算
        longest_streak = 1
        temp_streak = 1

        for i in range(1, len(sorted_dates)):
            prev_date = datetime.strptime(sorted_dates[i - 1], '%Y-%m-%d')
            curr_date = datetime.strptime(sorted_dates[i], '%Y-%m-%d')
            diff = (curr_date - prev_date).days

            if diff == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_days': total_days
        }

    @staticmethod
    def get_time_distribution(history: List[Dict]) -> Dict[str, Any]:
        """
        時間分布を取得

        Args:
            history: 学習履歴リスト

        Returns:
            時間分布情報
        """
        if not history:
            return {
                'total_time': 0,
                'average_time': 0.0,
                'fastest_time': None,
                'slowest_time': None
            }

        times = [h.get('elapsed', 0) for h in history if h.get('elapsed', 0) > 0]

        if not times:
            return {
                'total_time': 0,
                'average_time': 0.0,
                'fastest_time': None,
                'slowest_time': None
            }

        return {
            'total_time': sum(times),
            'average_time': round(sum(times) / len(times), 1),
            'fastest_time': min(times),
            'slowest_time': max(times)
        }
