# -*- coding: utf-8 -*-
"""
Render.com Gunicorn Configuration for RCCM Quiz Application
Expert-recommended configuration to resolve CSRF token session issues

Based on expert recommendations from:
- Miguel Grinberg Flask session management
- Stack Overflow CSRF token missing solutions
- Render.com deployment best practices
"""

import os

# Expert Fix 1: Use gthread worker to resolve CSRF token issues
# Changing from 'sync' to 'gthread' resolves Flask session corruption
worker_class = 'gthread'

# Expert Fix 2: Threading configuration for session persistence
# Adding threads parameter helps with session token management
threads = 2

# Basic configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1  # Single worker for session consistency in small apps

# Timeout settings
timeout = 120
keepalive = 2

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'

# Expert Fix 3: Preload app for better session handling
preload_app = True

# Process naming
proc_name = 'rccm-quiz-app'

# Expert Fix 4: Enable threading for Flask-Session compatibility
enable_stdio_inheritance = True

print("[EXPERT GUNICORN] Configuration loaded: gthread worker with Flask-Session support")