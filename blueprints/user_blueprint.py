#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Management Blueprint for RCCM Quiz Application
Phase 16 Refactoring - User and Reports API Routes

このBlueprintは/api/users/*と/api/reports/*配下のAPIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
user_bp = Blueprint('user', __name__, url_prefix='/api')


# =============================================================================
# User Management API
# =============================================================================

@user_bp.route('/users', methods=['GET'])
def api_users_list():
    """
    ユーザー一覧API（JSON API）

    🎯 PHASE 16 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        validation = api_manager.validate_api_key(api_key, 'read_users')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401

        # 全ユーザーデータ取得（簡略化）
        all_users = api_manager._load_all_user_data()

        users_list = []
        for user_id, user_data in all_users.items():
            history = user_data.get('history', [])
            users_list.append({
                'user_id': user_id,
                'total_questions': len(history),
                'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0,
                'last_activity': max([h.get('date', '') for h in history], default=''),
                'primary_department': api_manager._get_user_primary_departments(user_data)[0] if history else 'unknown'
            })

        return jsonify({
            'users': users_list,
            'total_count': len(users_list),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<user_id>/progress', methods=['GET'])
def api_user_progress(user_id):
    """
    ユーザー進捗API（JSON API）

    🎯 PHASE 16 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        validation = api_manager.validate_api_key(api_key, 'read_progress')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401

        # 進捗レポート生成
        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')

        report = api_manager.generate_progress_report(user_id, None, time_period, report_format)

        return jsonify(report)

    except Exception as e:
        logger.error(f"ユーザー進捗API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<user_id>/certifications', methods=['GET'])
def api_user_certifications(user_id):
    """
    ユーザー認定情報API（JSON API）

    🎯 PHASE 16 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        validation = api_manager.validate_api_key(api_key, 'read_users')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401

        user_data = api_manager._load_user_data(user_id)
        certifications = user_data.get('certifications', {})

        # 各認定の詳細情報を取得
        detailed_certifications = []
        for cert_id, enrollment in certifications.items():
            cert_progress = api_manager.check_certification_progress(user_id, cert_id)
            detailed_certifications.append(cert_progress)

        return jsonify({
            'user_id': user_id,
            'certifications': detailed_certifications,
            'total_certifications': len(detailed_certifications),
            'completed_certifications': len([c for c in detailed_certifications if c.get('enrollment_status') == 'completed'])
        })

    except Exception as e:
        logger.error(f"ユーザー認定情報API エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Reports API
# =============================================================================

@user_bp.route('/reports/progress', methods=['GET'])
def api_progress_reports():
    """
    進捗レポートAPI（JSON API）

    🎯 PHASE 16 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        validation = api_manager.validate_api_key(api_key, 'generate_reports')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401

        user_id = request.args.get('user_id')
        organization = request.args.get('organization')
        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')

        report = api_manager.generate_progress_report(user_id, organization, time_period, report_format)

        return jsonify(report)

    except Exception as e:
        logger.error(f"進捗レポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/reports/organization/<org_id>', methods=['GET'])
def api_organization_report(org_id):
    """
    組織レポートAPI（JSON API）

    🎯 PHASE 16 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import api_manager

        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        validation = api_manager.validate_api_key(api_key, 'generate_reports')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401

        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')

        report = api_manager._generate_organization_report(org_id, time_period, report_format)

        return jsonify(report)

    except Exception as e:
        logger.error(f"組織レポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500
