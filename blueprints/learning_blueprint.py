#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Learning Optimization Blueprint for RCCM Quiz Application
Phase 13 Refactoring - Learning Optimization API Routes

このBlueprintは/api/learning/*配下の学習最適化APIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')


# =============================================================================
# Real-time Learning Tracking API
# =============================================================================

@learning_bp.route('/realtime_tracking', methods=['POST'])
def api_realtime_learning_tracking():
    """
    リアルタイム学習効率追跡API（JSON API）

    🎯 PHASE 13 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import learning_optimizer

        data = request.get_json()
        session_start_time = data.get('session_start_time')

        if session_start_time:
            session_start = datetime.fromisoformat(session_start_time)
        else:
            session_start = datetime.now()

        current_session_data = {
            'start_time': session_start,
            'question_count': data.get('question_count', 0)
        }

        tracking_result = learning_optimizer.track_real_time_efficiency(session, current_session_data)

        return jsonify({
            'success': True,
            'tracking_data': tracking_result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"リアルタイム学習追跡API エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Biorhythm Calculation API
# =============================================================================

@learning_bp.route('/biorhythm', methods=['POST'])
def api_biorhythm_calculation():
    """
    バイオリズム計算API（JSON API）

    🎯 PHASE 13 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import learning_optimizer

        data = request.get_json()
        birth_date = data.get('birth_date')
        target_date_str = data.get('target_date')

        if not birth_date:
            return jsonify({'success': False, 'error': '生年月日が必要です'}), 400

        # セッションに生年月日を保存
        session['birth_date'] = birth_date
        session.modified = True

        target_date = datetime.now()
        if target_date_str:
            target_date = datetime.fromisoformat(target_date_str)

        biorhythm_scores = learning_optimizer.calculate_biorhythm_score(birth_date, target_date)

        # 今後7日間のバイオリズム予測
        future_biorhythms = {}
        for i in range(7):
            future_date = target_date + timedelta(days=i)
            future_scores = learning_optimizer.calculate_biorhythm_score(birth_date, future_date)
            future_biorhythms[future_date.strftime('%Y-%m-%d')] = future_scores

        return jsonify({
            'success': True,
            'current_biorhythm': biorhythm_scores,
            'future_biorhythms': future_biorhythms,
            'birth_date': birth_date,
            'target_date': target_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        logger.error(f"バイオリズム計算API エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Optimal Schedule API
# =============================================================================

@learning_bp.route('/optimal_schedule', methods=['GET'])
def api_optimal_schedule():
    """
    最適学習スケジュールAPI（JSON API）

    🎯 PHASE 13 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import learning_optimizer

        target_date = request.args.get('date')
        if target_date:
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
        else:
            target_datetime = datetime.now()

        recommendation = learning_optimizer.get_optimal_study_time_recommendation(session, target_datetime)

        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"最適スケジュールAPI エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
