#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enterprise Blueprint for RCCM Quiz Application
Phase 15 Refactoring - Enterprise API Routes

このBlueprintは/api/enterprise/*配下の企業環境向けAPIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/api/enterprise')


# =============================================================================
# Enterprise User Management API
# =============================================================================

@enterprise_bp.route('/users', methods=['GET'])
def api_enterprise_users():
    """
    全ユーザー一覧API（企業環境用、JSON API）

    🎯 PHASE 15 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import enterprise_user_manager

        users = enterprise_user_manager.get_all_users()

        return jsonify({
            'success': True,
            'users': users,
            'total_users': len(users),
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"企業ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@enterprise_bp.route('/user/<user_name>/report', methods=['GET'])
def api_enterprise_user_report(user_name):
    """
    ユーザー詳細進捗レポートAPI（企業環境用、JSON API）

    🎯 PHASE 15 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import enterprise_user_manager

        report = enterprise_user_manager.get_user_progress_report(user_name)

        if 'error' in report:
            return jsonify({'success': False, 'error': report['error']}), 404

        return jsonify({
            'success': True,
            'report': report
        })

    except Exception as e:
        logger.error(f"企業ユーザーレポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Enterprise Data Management API
# =============================================================================

@enterprise_bp.route('/data/integrity', methods=['GET'])
def api_enterprise_data_integrity():
    """
    データ整合性チェックAPI（企業環境用、JSON API）

    🎯 PHASE 15 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import enterprise_data_manager

        integrity_report = enterprise_data_manager.get_file_integrity_check()

        return jsonify({
            'success': True,
            'integrity_report': integrity_report
        })

    except Exception as e:
        logger.error(f"データ整合性チェックAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Enterprise Cache Management API
# =============================================================================

@enterprise_bp.route('/cache/stats', methods=['GET'])
def api_enterprise_cache_stats():
    """
    キャッシュ統計API（企業環境用、JSON API）

    🎯 PHASE 15 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from utils import cache_manager_instance

        cache_stats = cache_manager_instance.get_stats()

        return jsonify({
            'success': True,
            'cache_stats': cache_stats,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"キャッシュ統計API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@enterprise_bp.route('/cache/clear', methods=['POST'])
def api_enterprise_cache_clear():
    """
    キャッシュクリアAPI（企業環境用、JSON API）

    🎯 PHASE 15 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from utils import cache_manager_instance

        cache_manager_instance.clear_all()

        return jsonify({
            'success': True,
            'message': 'キャッシュをクリアしました',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"キャッシュクリアAPI エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
