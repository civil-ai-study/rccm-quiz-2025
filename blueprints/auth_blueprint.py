#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Authentication Blueprint for RCCM Quiz Application
Phase 14 Refactoring - Authentication API Routes

このBlueprintは/api/auth/*配下の認証・APIキー管理エンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# =============================================================================
# API Key Generation
# =============================================================================

@auth_bp.route('/generate_key', methods=['POST'])
def generate_api_key():
    """
    APIキー生成（JSON API）

    🎯 PHASE 14 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        data = request.get_json()
        organization = data.get('organization')
        permissions = data.get('permissions', [])
        expires_in_days = data.get('expires_in_days', 365)

        if not organization:
            return jsonify({'success': False, 'error': '組織名が必要です'}), 400

        result = api_manager.generate_api_key(organization, permissions, expires_in_days)

        return jsonify(result)

    except Exception as e:
        logger.error(f"APIキー生成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# API Key Validation
# =============================================================================

@auth_bp.route('/validate_key', methods=['POST'])
def validate_api_key():
    """
    APIキー検証（JSON API）

    🎯 PHASE 14 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        data = request.get_json()
        api_key = data.get('api_key')
        required_permission = data.get('required_permission')

        if not api_key:
            return jsonify({'valid': False, 'error': 'APIキーが必要です'}), 400

        result = api_manager.validate_api_key(api_key, required_permission)

        return jsonify(result)

    except Exception as e:
        logger.error(f"APIキー検証エラー: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 500


# =============================================================================
# API Key Revocation
# =============================================================================

@auth_bp.route('/revoke_key', methods=['DELETE'])
def revoke_api_key():
    """
    APIキー無効化（JSON API）

    🎯 PHASE 14 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        data = request.get_json()
        api_key = data.get('api_key')

        if not api_key:
            return jsonify({'success': False, 'error': 'APIキーが必要です'}), 400

        result = api_manager.revoke_api_key(api_key)

        return jsonify(result)

    except Exception as e:
        logger.error(f"APIキー無効化エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
