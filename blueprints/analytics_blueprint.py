#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analytics Blueprint for RCCM Quiz Application
Phase 19 Refactoring - AI Analysis & Reports Export API Routes

このBlueprintは/api/ai_analysisと/api/reports/export配下の分析・レポートAPIエンドポイントを統合します。
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blueprint作成
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')


# =============================================================================
# AI Analysis API Routes
# =============================================================================

@analytics_bp.route('/ai_analysis', methods=['GET'])
def api_ai_analysis():
    """
    AI分析結果のAPI（部門別対応版、JSON API）

    🎯 PHASE 19 REFACTORING: app.pyから移動
    """
    try:
        # 循環インポート回避のためローカルインポート
        from app import ai_analyzer, adaptive_engine

        department_filter = request.args.get('department')

        try:
            analysis_result = ai_analyzer.analyze_weak_areas(session, department_filter) if ai_analyzer else {}
        except Exception as e:
            logger.error(f"AI分析エラー: {e}")
            analysis_result = {}

        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)

        return jsonify({
            'analysis': analysis_result,
            'recommended_mode': recommended_mode,
            'department_filter': department_filter,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"AI分析API エラー: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Reports Export API Routes
# =============================================================================

@analytics_bp.route('/reports/export/<format>', methods=['GET'])
def api_export_analytics(format):
    """
    学習分析エクスポートAPI（JSON API）

    🎯 PHASE 19 REFACTORING: app.pyから移動
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

        include_personal = request.args.get('include_personal_data', 'false').lower() == 'true'

        result = api_manager.export_learning_analytics(format, include_personal)

        return jsonify(result)

    except Exception as e:
        logger.error(f"学習分析エクスポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500
