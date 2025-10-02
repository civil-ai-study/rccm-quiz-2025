#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Certification Blueprint for RCCM Quiz Application
Phase 17 Refactoring - Certification & Organization API Routes

このBlueprintは/api/certifications*と/api/organizations*配下の認定・組織管理APIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
certification_bp = Blueprint('certification', __name__, url_prefix='/api')


# =============================================================================
# Certification API Routes
# =============================================================================

@certification_bp.route('/certifications', methods=['GET', 'POST'])
def api_certifications():
    """
    認定プログラムAPI（JSON API）

    🎯 PHASE 17 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        if request.method == 'GET':
            certifications = api_manager._load_certifications()
            return jsonify({
                'certifications': list(certifications.values()),
                'total_count': len(certifications)
            })

        elif request.method == 'POST':
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401

            validation = api_manager.validate_api_key(api_key, 'manage_certifications')
            if not validation['valid']:
                return jsonify({'error': validation['error']}), 401

            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            requirements = data.get('requirements', {})
            organization = data.get('organization')

            result = api_manager.create_certification_program(name, description, requirements, organization)
            return jsonify(result)

    except Exception as e:
        logger.error(f"認定プログラムAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


@certification_bp.route('/certifications/<cert_id>/progress', methods=['GET'])
def api_certification_progress(cert_id):
    """
    認定進捗API（JSON API）

    🎯 PHASE 17 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400

        progress = api_manager.check_certification_progress(user_id, cert_id)
        return jsonify(progress)

    except Exception as e:
        logger.error(f"認定進捗API エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Organization API Routes
# =============================================================================

@certification_bp.route('/organizations', methods=['GET', 'POST'])
def api_organizations():
    """
    組織管理API（JSON API）

    🎯 PHASE 17 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        if request.method == 'GET':
            organizations = api_manager._load_organizations()
            return jsonify({
                'organizations': list(organizations.values()),
                'total_count': len(organizations)
            })

        elif request.method == 'POST':
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401

            validation = api_manager.validate_api_key(api_key, 'manage_organizations')
            if not validation['valid']:
                return jsonify({'error': validation['error']}), 401

            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            settings = data.get('settings', {})

            result = api_manager.create_organization(name, description, settings)
            return jsonify(result)

    except Exception as e:
        logger.error(f"組織管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@certification_bp.route('/organizations/<org_id>/users', methods=['GET'])
def api_organization_users(org_id):
    """
    組織ユーザー一覧API（JSON API）

    🎯 PHASE 17 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        organizations = api_manager._load_organizations()
        if org_id not in organizations:
            return jsonify({'error': 'Organization not found'}), 404

        org_users = organizations[org_id]['users']
        users_details = []

        for user_id in org_users:
            user_data = api_manager._load_user_data(user_id)
            history = user_data.get('history', [])

            users_details.append({
                'user_id': user_id,
                'total_questions': len(history),
                'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0,
                'last_activity': max([h.get('date', '') for h in history], default='')
            })

        return jsonify({
            'organization_id': org_id,
            'users': users_details,
            'total_users': len(users_details)
        })

    except Exception as e:
        logger.error(f"組織ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500
