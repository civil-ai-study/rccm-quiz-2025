#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Blueprint for RCCM Quiz Application
Phase 8 Refactoring - Data Export & Cache API Routes

このBlueprintは/api/data/*および/api/cache/*配下のAPIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify, session
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
data_bp = Blueprint('data', __name__, url_prefix='/api')


# =============================================================================
# Data Export API Routes
# =============================================================================

@data_bp.route('/data/export', methods=['GET'])
def export_data():
    """
    学習データのエクスポート（JSON API）

    🎯 PHASE 8 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import data_manager

        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'セッションが見つかりません'}), 400

        export_data = data_manager.get_data_export(session_id)
        if export_data:
            return jsonify(export_data)
        else:
            return jsonify({'error': 'エクスポートデータがありません'}), 404

    except Exception as e:
        logger.error(f"データエクスポートエラー: {e}")
        return jsonify({'error': 'エクスポートに失敗しました'}), 500


# =============================================================================
# Cache Management API Routes
# =============================================================================

@data_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    問題データキャッシュのクリア（JSON API）

    🎯 PHASE 8 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import clear_questions_cache

        clear_questions_cache()
        return jsonify({'message': 'キャッシュをクリアしました'})

    except Exception as e:
        logger.error(f"キャッシュクリアエラー: {e}")
        return jsonify({'error': 'キャッシュクリアに失敗しました'}), 500
