#!/usr/bin/env python3
"""
🚨 EMERGENCY FIX: Standard WSGI entrypoint for Render.com
This file resolves the "ModuleNotFoundError: No module named 'wsgi'" deployment error.
"""

import os
import sys
import logging

# Configure basic logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Ensure both current directory and rccm-quiz-app subdirectory are in Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(current_dir, 'rccm-quiz-app')
    
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Set production environment
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('RENDER', 'true')
    
    # Auto-generate SECRET_KEY if not provided by Render.com
    if not os.environ.get('SECRET_KEY'):
        import secrets
        os.environ['SECRET_KEY'] = secrets.token_hex(32)
        logger.info("🔐 Auto-generated SECRET_KEY for production")
    
    # Import Flask application
    from app import app
    
    # Verify app loaded successfully
    logger.info(f"✅ Flask app '{app.name}' loaded successfully")
    logger.info(f"🎯 Routes registered: {len(list(app.url_map.iter_rules()))}")
    
    # This is what Gunicorn will import
    application = app
    
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to load Flask app: {e}")
    logger.error(f"📁 Current directory: {os.getcwd()}")
    logger.error(f"🐍 Python path: {sys.path}")
    raise

# For local development testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Starting development server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)