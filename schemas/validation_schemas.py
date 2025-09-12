#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC STAGE 6: Flask Parameter Validation Schemas
PHASE 1 タスク B2: 2024年標準 Marshmallow validation実装

Purpose: Provide robust parameter validation for exam route
Created: 2025-08-31 (PHASE 1 Task B2 Implementation)
"""

from marshmallow import Schema, fields, validate, ValidationError, pre_load, post_load
from flask_marshmallow import Marshmallow
import logging

logger = logging.getLogger(__name__)

class ExamParameterSchema(Schema):
    """
    RCCM Quiz Application - Exam Route Parameter Validation Schema
    
    Validates all incoming parameters for the /exam route with:
    - Department validation (13 valid departments)
    - Question type validation (basic/specialist)
    - Category parameter handling
    - Count parameter validation (10 questions fixed)
    
    2024 Best Practice: Marshmallow schema-based validation
    """
    
    # Core Parameters
    department = fields.String(
        required=True,
        validate=validate.OneOf([
            '基礎科目', '道路', 'トンネル', '河川、砂防及び海岸・海洋', '都市計画及び地方計画', '造園', 
            '建設環境', '鋼構造及びコンクリート', '土質及び基礎', '施工計画、施工設備及び積算', '上水道及び工業用水道', '森林土木', '農業土木'
        ]),
        error_messages={
            'required': 'Department parameter is required.',
            'validator_failed': 'Invalid department. Must be one of the 13 valid RCCM departments in Japanese.'
        }
    )
    
    question_type = fields.String(
        required=False,
        validate=validate.OneOf(['basic', 'specialist']),
        load_default='specialist',  # Default to specialist (Marshmallow 3.x syntax)
        error_messages={
            'validator_failed': 'Invalid question_type. Must be "basic" or "specialist".'
        }
    )
    
    # Alternative parameter name for backward compatibility
    type = fields.String(
        required=False,
        validate=validate.OneOf(['basic', 'specialist']),
        error_messages={
            'validator_failed': 'Invalid type. Must be "basic" or "specialist".'
        }
    )
    
    category = fields.String(
        required=False,
        load_default='all',  # Marshmallow 3.x syntax
        validate=validate.Length(min=1, max=50),
        error_messages={
            'validator_failed': 'Category must be between 1 and 50 characters.'
        }
    )
    
    count = fields.Integer(
        required=False,
        validate=validate.Range(min=1, max=50),
        load_default=10,  # CRITICAL: 10問固定（ユーザー要求）
        error_messages={
            'validator_failed': 'Count must be between 1 and 50.'
        }
    )
    
    # Session parameters
    selected_year = fields.String(
        required=False,
        validate=validate.Length(min=4, max=4),
        error_messages={
            'validator_failed': 'Year must be 4 digits.'
        }
    )
    
    @pre_load
    def normalize_parameters(self, data, **kwargs):
        """
        Pre-processing: Parameter normalization and backward compatibility
        
        Handles:
        - question_type → type parameter mapping
        - category='all' → count=10 implicit conversion
        - URL decoding and sanitization
        """
        logger.info(f"Pre-load validation: Raw data: {data}")
        
        # Handle question_type → type parameter precedence
        if 'question_type' in data and data['question_type']:
            # question_type takes precedence over type
            if 'type' in data:
                logger.info(f"Parameter precedence: question_type={data['question_type']} overrides type={data.get('type')}")
            data['type'] = data['question_type']
        elif 'type' in data and data['type']:
            # Use type if question_type not present
            data['question_type'] = data['type']
        else:
            # Default to specialist if neither present
            data['question_type'] = 'specialist'
            data['type'] = 'specialist'
            logger.info("Parameter default: question_type=specialist (no parameter provided)")
        
        # Handle category='all' → count=10 conversion
        if data.get('category') == 'all' and 'count' not in data:
            data['count'] = 10
            logger.info("Parameter conversion: category='all' → count=10")
        
        # Clean up None values
        cleaned_data = {k: v for k, v in data.items() if v is not None}
        
        logger.info(f"Pre-load normalized: {cleaned_data}")
        return cleaned_data
    
    @post_load
    def finalize_parameters(self, data, **kwargs):
        """
        Post-processing: Final parameter validation and assignment
        
        Ensures:
        - All required parameters are properly set
        - Business logic constraints are met
        - Consistent parameter structure
        """
        logger.info(f"Post-load validation: Processed data: {data}")
        
        # Ensure question_type and type are synchronized
        if 'question_type' in data and 'type' not in data:
            data['type'] = data['question_type']
        elif 'type' in data and 'question_type' not in data:
            data['question_type'] = data['type']
        
        # CRITICAL: Enforce 10問固定（CLAUDE.md requirement）
        if data.get('count') != 10:
            logger.warning(f"Count override: {data.get('count')} → 10 (CLAUDE.md requirement)")
            data['count'] = 10
        
        logger.info(f"Post-load finalized: {data}")
        return data

class DepartmentParameterSchema(Schema):
    """
    Department selection parameter validation
    Used for /departments/<department_id>/types routes
    """
    
    department_id = fields.String(
        required=True,
        validate=validate.OneOf([
            '基礎科目', '道路', 'トンネル', '河川、砂防及び海岸・海洋', '都市計画及び地方計画', '造園', 
            '建設環境', '鋼構造及びコンクリート', '土質及び基礎', '施工計画、施工設備及び積算', '上水道及び工業用水道', '森林土木', '農業土木'
        ]),
        error_messages={
            'required': 'Department ID is required.',
            'validator_failed': 'Invalid department ID. Must be one of the 13 valid RCCM departments in Japanese.'
        }
    )

def validate_exam_parameters(request_args, request_form=None):
    """
    Unified parameter validation function for exam route
    
    Args:
        request_args: Flask request.args (GET parameters)
        request_form: Flask request.form (POST parameters, optional)
    
    Returns:
        dict: Validated and normalized parameters
        
    Raises:
        ValidationError: If validation fails
    """
    schema = ExamParameterSchema()
    
    # Combine GET and POST parameters (POST takes precedence)
    combined_data = dict(request_args)
    if request_form:
        combined_data.update(dict(request_form))
    
    try:
        validated_data = schema.load(combined_data)
        logger.info(f"Parameter validation successful: {validated_data}")
        return validated_data
    
    except ValidationError as e:
        logger.error(f"Parameter validation failed: {e.messages}")
        raise ValidationError(f"Parameter validation error: {e.messages}")

def validate_department_parameter(department_id):
    """
    Validate department ID for department routes
    
    Args:
        department_id: Department identifier string
        
    Returns:
        dict: Validated department parameter
        
    Raises:
        ValidationError: If validation fails
    """
    schema = DepartmentParameterSchema()
    
    try:
        validated_data = schema.load({'department_id': department_id})
        logger.info(f"Department validation successful: {validated_data}")
        return validated_data
    
    except ValidationError as e:
        logger.error(f"Department validation failed: {e.messages}")
        raise ValidationError(f"Department validation error: {e.messages}")