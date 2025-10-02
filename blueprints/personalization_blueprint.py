#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Personalization Blueprint for RCCM Quiz Application
Phase 18 Refactoring - Advanced Personalization API Routes

このBlueprintは/api/personalization配下の高度な個人化APIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
personalization_bp = Blueprint('personalization', __name__, url_prefix='/api/personalization')


# =============================================================================
# Personalization API Routes
# =============================================================================

@personalization_bp.route('/profile/<user_id>')
def api_personalization_profile(user_id):
    """
    個人化プロファイルAPI（JSON API）

    🎯 PHASE 18 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import advanced_personalization

        profile = advanced_personalization.analyze_user_profile(user_id)

        return jsonify({
            'user_id': user_id,
            'profile': profile,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"個人化プロファイルAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


@personalization_bp.route('/recommendations/<user_id>')
def api_personalization_recommendations(user_id):
    """
    ML推薦API（JSON API）

    🎯 PHASE 18 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import advanced_personalization

        context = request.args.to_dict()
        recommendations = advanced_personalization.get_ml_recommendations(user_id, context)

        return jsonify({
            'user_id': user_id,
            'recommendations': recommendations,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"ML推薦API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@personalization_bp.route('/ui/<user_id>')
def api_personalization_ui(user_id):
    """
    UI個人化API（JSON API）

    🎯 PHASE 18 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import advanced_personalization

        ui_customizations = advanced_personalization.customize_ui(user_id)

        return jsonify({
            'user_id': user_id,
            'ui_customizations': ui_customizations,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"UI個人化API エラー: {e}")
        return jsonify({'error': str(e)}), 500
