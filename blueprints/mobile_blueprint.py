#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobile Blueprint for RCCM Quiz Application
Phase 11 Refactoring - Mobile API Routes

このBlueprintは/api/mobile/*配下のモバイル最適化APIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify, session
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
mobile_bp = Blueprint('mobile', __name__, url_prefix='/api/mobile')


# =============================================================================
# PWA Manifest API Routes
# =============================================================================

@mobile_bp.route('/manifest', methods=['GET'])
def mobile_manifest():
    """
    PWAマニフェストの動的生成（JSON API）

    🎯 PHASE 11 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        manifest = mobile_manager.get_pwa_manifest()
        return jsonify(manifest)

    except Exception as e:
        logger.error(f"マニフェスト生成エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Offline Data API Routes
# =============================================================================

@mobile_bp.route('/offline/save', methods=['POST'])
def save_offline_data():
    """
    オフラインデータの保存（JSON API）

    🎯 PHASE 11 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        data = request.get_json()
        session_id = session.get('session_id')

        if not session_id:
            return jsonify({'success': False, 'error': 'セッションIDが見つかりません'}), 400

        success = mobile_manager.save_offline_session(session_id, data)

        if success:
            return jsonify({'success': True, 'message': 'オフラインデータを保存しました'})
        else:
            return jsonify({'success': False, 'error': 'データ保存に失敗しました'}), 500

    except Exception as e:
        logger.error(f"オフラインデータ保存エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mobile_bp.route('/offline/sync', methods=['POST'])
def sync_offline_data():
    """
    オフラインデータの同期（JSON API）

    🎯 PHASE 11 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        sync_result = mobile_manager.sync_offline_data(session)
        session.modified = True

        mobile_manager.update_last_sync_time()

        return jsonify({
            'success': sync_result['success'],
            'synced_sessions': sync_result['synced_sessions'],
            'failed_sessions': sync_result['failed_sessions'],
            'errors': sync_result['errors']
        })

    except Exception as e:
        logger.error(f"オフライン同期エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Mobile Optimized Question API Routes
# =============================================================================

@mobile_bp.route('/question/<int:question_id>', methods=['GET'])
def mobile_optimized_question(question_id):
    """
    モバイル最適化問題データ（JSON API）

    🎯 PHASE 11 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import load_questions, mobile_manager

        questions = load_questions()
        question = next((q for q in questions if int(q.get('id', 0)) == question_id), None)

        if not question:
            return jsonify({'error': '問題が見つかりません'}), 404

        mobile_question = mobile_manager.get_mobile_optimized_question(question)
        return jsonify(mobile_question)

    except Exception as e:
        logger.error(f"モバイル問題取得エラー: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/cache/questions', methods=['GET'])
def mobile_cache_questions():
    """
    モバイル用問題キャッシュデータ（JSON API）

    🎯 PHASE 11 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import load_questions, mobile_manager

        questions = load_questions()
        cache_data = mobile_manager.generate_mobile_cache_data(questions)
        return jsonify(cache_data)

    except Exception as e:
        logger.error(f"モバイルキャッシュ生成エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Mobile Settings API Routes
# =============================================================================

@mobile_bp.route('/voice/settings', methods=['GET', 'POST'])
def voice_settings():
    """
    音声設定の取得・更新（JSON API）

    🎯 PHASE 12 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        if request.method == 'GET':
            settings = mobile_manager.get_voice_settings()
            return jsonify(settings)
        else:
            data = request.get_json()
            success = mobile_manager.update_voice_settings(data)

            if success:
                return jsonify({'success': True, 'message': '音声設定を更新しました'})
            else:
                return jsonify({'success': False, 'error': '設定更新に失敗しました'}), 500

    except Exception as e:
        logger.error(f"音声設定エラー: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/touch/settings', methods=['GET', 'POST'])
def touch_settings():
    """
    タッチジェスチャー設定の取得・更新（JSON API）

    🎯 PHASE 12 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        if request.method == 'GET':
            settings = mobile_manager.get_touch_settings()
            return jsonify(settings)
        else:
            data = request.get_json()
            success = mobile_manager.update_touch_settings(data)

            if success:
                return jsonify({'success': True, 'message': 'タッチ設定を更新しました'})
            else:
                return jsonify({'success': False, 'error': '設定更新に失敗しました'}), 500

    except Exception as e:
        logger.error(f"タッチ設定エラー: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/performance', methods=['GET'])
def mobile_performance_metrics():
    """
    モバイルパフォーマンス指標（JSON API）

    🎯 PHASE 12 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import mobile_manager

        metrics = mobile_manager.get_performance_metrics()
        return jsonify(metrics)

    except Exception as e:
        logger.error(f"パフォーマンス指標エラー: {e}")
        return jsonify({'error': str(e)}), 500
