#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Blueprint for RCCM Quiz Application
Phase 6 Refactoring - API Routes Modularization

このBlueprintは/api/*配下のAPIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify, session
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
api_bp = Blueprint('api', __name__, url_prefix='/api')


# =============================================================================
# Bookmark API Routes
# =============================================================================

@api_bp.route('/bookmark', methods=['POST'])
def bookmark_question():
    """
    問題のブックマーク機能（JSON API）

    🎯 PHASE 6 REFACTORING: app.pyから移動
    """
    try:
        data = request.get_json()
        question_id = data.get('question_id')

        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'}), 400

        # セッションにブックマークリストがなければ作成
        if 'bookmarks' not in session:
            session['bookmarks'] = []

        # 問題IDがリストになければ追加
        if question_id not in session['bookmarks']:
            session['bookmarks'].append(question_id)
            session.modified = True
            logger.info(f"問題ID {question_id} をブックマークに追加しました")

        return jsonify({'success': True, 'message': '問題をブックマークしました'})

    except Exception as e:
        logger.error(f"ブックマーク機能でエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    """
    ブックマークされた問題IDのリストを返却（JSON API）

    🎯 PHASE 6 REFACTORING: app.pyから移動
    """
    try:
        # セッションからブックマークリストを取得
        bookmarks = session.get('bookmarks', [])
        return jsonify({'bookmark_ids': bookmarks})

    except Exception as e:
        logger.error(f"ブックマークリスト取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/bookmark', methods=['DELETE'])
def remove_bookmark():
    """
    復習リストから問題を除外（JSON API）

    🎯 PHASE 6 REFACTORING: app.pyから移動
    """
    try:
        data = request.get_json()
        question_id = data.get('question_id')

        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'}), 400

        bookmarks = session.get('bookmarks', [])

        if question_id in bookmarks:
            bookmarks.remove(question_id)
            session['bookmarks'] = bookmarks
            session.modified = True
            logger.info(f"問題ID {question_id} を復習リストから削除しました")
            return jsonify({'success': True, 'message': '問題を復習リストから削除しました'})
        else:
            return jsonify({'success': False, 'error': '指定された問題はブックマークされていません'}), 404

    except Exception as e:
        logger.error(f"ブックマーク削除エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Review API Routes
# =============================================================================

@api_bp.route('/review/questions', methods=['POST'])
def get_review_questions():
    """
    復習リストの問題詳細を一括取得（JSON API）

    🎯 PHASE 7 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import load_questions

        data = request.get_json()
        question_ids = data.get('question_ids', [])

        if not question_ids:
            return jsonify({'questions': []})

        questions = load_questions()
        review_questions = []

        for qid in question_ids:
            question = next((q for q in questions if int(q.get('id', 0)) == int(qid)), None)
            if question:
                review_questions.append({
                    'id': question.get('id'),
                    'category': question.get('category'),
                    'question': question.get('question')[:100] + '...' if len(question.get('question', '')) > 100 else question.get('question'),
                    'difficulty': question.get('difficulty', '標準')
                })

        return jsonify({'questions': review_questions})

    except Exception as e:
        logger.error(f"復習問題取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/review/remove', methods=['POST'])
def remove_from_review():
    """
    復習リストから問題を削除（JSON API）

    🎯 PHASE 7 REFACTORING: app.pyから移動
    """
    try:
        data = request.get_json()
        question_id = str(data.get('question_id', ''))

        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'})

        bookmarks = session.get('bookmarks', [])
        if question_id in bookmarks:
            bookmarks.remove(question_id)
            session['bookmarks'] = bookmarks
            session.modified = True
            logger.info(f"復習リストから削除: 問題ID {question_id}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '復習リストに存在しません'})

    except Exception as e:
        logger.error(f"復習問題削除エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/review/bulk_remove', methods=['POST'])
def bulk_remove_from_review():
    """
    復習リストから複数問題を削除（JSON API）

    🎯 PHASE 7 REFACTORING: app.pyから移動
    """
    try:
        data = request.get_json()
        question_ids = data.get('question_ids', [])

        if not question_ids:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'})

        bookmarks = session.get('bookmarks', [])
        removed_count = 0

        for qid in question_ids:
            qid_str = str(qid)
            if qid_str in bookmarks:
                bookmarks.remove(qid_str)
                removed_count += 1

        session['bookmarks'] = bookmarks
        session.modified = True

        logger.info(f"復習リストから一括削除: {removed_count}問")
        return jsonify({'success': True, 'removed_count': removed_count})

    except Exception as e:
        logger.error(f"復習問題一括削除エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})


# =============================================================================
# Gamification API Routes
# =============================================================================

@api_bp.route('/gamification/status', methods=['GET'])
def gamification_status():
    """
    ゲーミフィケーション状態のAPI（JSON API）

    🎯 PHASE 9 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import gamification_manager

        try:
            insights = gamification_manager.get_study_insights(session) if gamification_manager else {}
        except Exception as e:
            logger.error(f"ゲーミフィケーション状態取得エラー: {e}")
            insights = {}

        earned_badges = session.get('earned_badges', [])

        return jsonify({
            'streak': insights.get('study_streak', 0),
            'max_streak': insights.get('max_streak', 0),
            'badges_count': len(earned_badges),
            'total_questions': insights.get('total_questions', 0),
            'overall_accuracy': insights.get('overall_accuracy', 0),
            'recent_accuracy': insights.get('recent_accuracy', 0)
        })

    except Exception as e:
        logger.error(f"ゲーミフィケーション状態取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Difficulty Status API Routes
# =============================================================================

@api_bp.route('/difficulty/status', methods=['GET'])
def api_difficulty_status():
    """
    動的難易度制御状態のAPI（JSON API）

    🎯 PHASE 10 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from datetime import datetime

        department = request.args.get('department')

        # 学習者レベル評価
        from difficulty_controller import difficulty_controller
        learner_assessment = difficulty_controller.assess_learner_level(session, department)

        # 最近のパフォーマンス
        recent_history = session.get('history', [])[-10:]
        if recent_history:
            recent_performance = difficulty_controller._analyze_current_performance(recent_history)
        else:
            recent_performance = {'accuracy': 0, 'avg_time': 0, 'sample_size': 0, 'trend': 'unknown'}

        # 動的セッション設定
        dynamic_config = session.get('dynamic_session_config', {})

        return jsonify({
            'learner_level': learner_assessment['overall_level'],
            'level_name': learner_assessment['level_name'],
            'confidence': learner_assessment['confidence'],
            'recent_performance': recent_performance,
            'dynamic_config': dynamic_config,
            'recommended_difficulty': learner_assessment['recommended_difficulty'],
            'department_factor': learner_assessment.get('department_factor', 1.0),
            'next_adjustment_threshold': learner_assessment.get('next_adjustment_threshold', 20),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"難易度制御状態API エラー: {e}")
        return jsonify({'error': str(e)}), 500
